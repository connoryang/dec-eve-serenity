#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\project.py
from . import AuthoringValidationError
from .. import const as localizationBSDConst
import bsdWrappers
import bsd

class Project(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(localizationBSDConst.LOC_PROJECT_TABLE)
    _projectsToGroups = None

    def Copy(self, keyID = None, keyID2 = None, keyID3 = None, **kw):
        raise NotImplementedError

    @classmethod
    def GetByName(cls, projectName):
        projectRows = Project.GetWithFilter(projectName=projectName)
        if projectRows and len(projectRows) > 1:
            raise AuthoringValidationError("Multiple projects (%s) were found. Duplicate project names aren't allowed to exist." % projectName)
        if projectRows:
            return projectRows[0]
        else:
            return None

    def AddLanguageToProject(self, languageID):
        languageProjectRow, languageRow = self._GetLanguageSetting(languageID)
        if not languageProjectRow:
            projectsToLanguages = sm.GetService('bsdTable').GetTable(localizationBSDConst.PROJECT_LANGUAGE_TABLE)
            projectsToLanguages.AddRow(languageRow.numericLanguageID, self.projectID)

    def RemoveLanguageFromProject(self, languageID):
        languageProjectRow, languageRow = self._GetLanguageSetting(languageID)
        if languageProjectRow:
            languageProjectRow.Delete()

    def GetAllLanguages(self):
        projectsToLanguages = sm.GetService('bsdTable').GetTable(localizationBSDConst.PROJECT_LANGUAGE_TABLE)
        languagesTable = sm.GetService('bsdTable').GetTable(localizationBSDConst.LANGUAGE_SETTINGS_TABLE)
        listOfLanguages = []
        for aTag in projectsToLanguages.GetRows(projectID=self.projectID, _getDeleted=False):
            listOfLanguages.append(languagesTable.GetRowByKey(aTag.numericLanguageID, _getDeleted=False).languageID)

        return listOfLanguages

    def AddGroupToProject(self, groupID):
        existingRows = Project._projectsToGroups.GetRows(groupID=groupID, projectID=self.projectID)
        if existingRows and len(existingRows):
            return
        Project._projectsToGroups.AddRow(groupID=groupID, projectID=self.projectID)

    def RemoveGroupFromProject(self, groupID):
        from messageGroup import MessageGroup
        existingRows = Project._projectsToGroups.GetRows(groupID=groupID, projectID=self.projectID)
        if existingRows:
            for tag in existingRows:
                tag.Delete()

            currentGroup = MessageGroup.Get(groupID)
            if currentGroup:
                for aSubgroup in MessageGroup.GetWithFilter(parentID=currentGroup.groupID):
                    self.RemoveGroupFromProject(aSubgroup.groupID)

    def GetAllGroupIDs(self):
        allTags = Project._projectsToGroups.GetRows(projectID=self.projectID, _getDeleted=False)
        if allTags and len(allTags):
            return [ aTag.groupID for aTag in allTags ]
        else:
            return []

    def GetMessageGroupsByParentID(self, groupID):
        from messageGroup import MessageGroup
        groupList = []
        for subGroup in MessageGroup.GetWithFilter(parentID=groupID):
            if Project._projectsToGroups.GetRows(groupID=subGroup.groupID, projectID=self.projectID, _getDeleted=False):
                groupList.append(subGroup)

        return groupList

    def GetVisibleGroupsByParentID(self, groupID):
        from messageGroup import MessageGroup
        groupList = []
        for subGroup in MessageGroup.GetWithFilter(parentID=groupID):
            if self._IsVisibleGroup(subGroup):
                groupList.append(subGroup)

        return groupList

    def GetAllMessages(self):
        from message import Message
        allGroupTags = Project._projectsToGroups.GetRows(projectID=self.projectID, _getDeleted=False)
        if allGroupTags:
            allMessages = []
            for aGroupTag in allGroupTags:
                allMessages += Message.GetWithFilter(groupID=aGroupTag.groupID)

            return allMessages
        else:
            return []

    def __init__(self, row):
        bsdWrappers.BaseWrapper.__init__(self, row)
        self.__class__._CheckAndSetCache()

    def _GetLanguageSetting(self, languageID):
        languagesTable = sm.GetService('bsdTable').GetTable(localizationBSDConst.LANGUAGE_SETTINGS_TABLE)
        languageRows = languagesTable.GetRows(languageID=languageID, _getDeleted=False)
        if len(languageRows) == 0:
            raise AuthoringValidationError('Can not perform operation since didnt find the unique language setting entry. Instead found (%s) rows. ProjectID = (%s), LanguageID = (%s)' % (len(languageRows), self.projectID, languageID))
        languageRow = languageRows[0]
        projectsToLanguages = sm.GetService('bsdTable').GetTable(localizationBSDConst.PROJECT_LANGUAGE_TABLE)
        languageProjectRow = projectsToLanguages.GetRowByKey(languageRow.numericLanguageID, self.projectID, _getDeleted=False)
        return (languageProjectRow, languageRow)

    @classmethod
    def _CheckAndSetCache(cls):
        if cls._projectsToGroups is None:
            bsdTableSvc = sm.GetService('bsdTable')
            cls._projectsToGroups = bsdTableSvc.GetTable(localizationBSDConst.PROJECT_GROUP_TABLE)

    def Delete(self):
        self._DeleteTags()
        return bsdWrappers.BaseWrapper.Delete(self)

    def _DeleteTags(self):
        batchSize = 1000
        rowIndex = 0
        projectToGroupsRows = Project._projectsToGroups.GetRows(projectID=self.projectID, _getDeleted=False)
        while rowIndex < len(projectToGroupsRows):
            with bsd.BsdTransaction():
                for aTag in projectToGroupsRows[rowIndex:rowIndex + batchSize]:
                    rowIndex += 1
                    aTag.Delete()

        projectsToLanguages = sm.GetService('bsdTable').GetTable(localizationBSDConst.PROJECT_LANGUAGE_TABLE)
        for aTag in projectsToLanguages.GetRows(projectID=self.projectID, _getDeleted=False):
            aTag.Delete()

    def _IsVisibleGroup(self, groupWrapper):
        from messageGroup import MessageGroup
        if Project._projectsToGroups.GetRows(groupID=groupWrapper.groupID, projectID=self.projectID, _getDeleted=False):
            return True
        for subGroup in MessageGroup.GetWithFilter(parentID=groupWrapper.groupID):
            if self._IsVisibleGroup(subGroup):
                return True

        return False

    @classmethod
    def Create(cls, projectName, projectDescription = None, workingDirectory = None, exportLocation = None, exportFileName = None, exportTypeName = None):
        if not projectName:
            raise AuthoringValidationError('Project name (%s) must be valid string.' % projectName)
        duplicateProjects = cls.GetWithFilter(projectName=projectName, _getDeleted=True)
        if duplicateProjects and len(duplicateProjects):
            raise AuthoringValidationError('Can not insert duplicate project (%s).' % projectName)
        return bsdWrappers.BaseWrapper._Create(cls, projectName=projectName, projectDescription=projectDescription, workingDirectory=workingDirectory, exportLocation=exportLocation, exportFileName=exportFileName, exportTypeName=exportTypeName)

    @classmethod
    def GetProjectsForGroup(cls, groupID):
        cls._CheckAndSetCache()
        projectTags = cls._projectsToGroups.GetRows(groupID=groupID, _getDeleted=False)
        if projectTags and len(projectTags):
            return [ Project.Get(aTag.projectID) for aTag in projectTags ]
        else:
            return []
