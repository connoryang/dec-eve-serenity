#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\messageGroup.py
from . import AuthoringValidationError
from ..const import MESSAGE_GROUPS_TABLE
import bsdWrappers
import bsd
import wordType as locWordType
import message as locMessage
import project as locProject

class MessageGroup(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(MESSAGE_GROUPS_TABLE)

    def __setattr__(self, key, value):
        if key == 'wordTypeID':
            if self.wordTypeID:
                wordType = locWordType.WordType.Get(self.wordTypeID)
                wordTypeName = wordType.typeName if wordType else 'None'
                raise AuthoringValidationError("Cannot change wordTypeID: Group '%s' (groupID %s) may contain metadata for wordType '%s'; call ResetWordType first to delete all metadata in this group and try again." % (self.groupName, self.groupID, wordTypeName))
            if locWordType.WordType.Get(value) == None:
                raise AuthoringValidationError('WordTypeID (%s) does not exist.' % value)
            with bsd.BsdTransaction():
                for message in locMessage.Message.GetMessagesByGroupID(self.groupID):
                    message.wordTypeID = value

                bsdWrappers.BaseWrapper.__setattr__(self, key, value)
            return
        if key == 'parentID' and value is not None:
            if not MessageGroup.Get(value):
                raise AuthoringValidationError("Cannot set parentID: '%s' is not a valid groupID." % value)
            if self._IsSubGroup(value):
                subGroup = MessageGroup.Get(value)
                raise AuthoringValidationError("You cannot assign group '%s' as a child of group '%s' because it would create a circular reference." % (self.groupName, subGroup.groupName))
        bsdWrappers.BaseWrapper.__setattr__(self, key, value)

    @classmethod
    def Create(cls, parentID = None, groupName = 'New Folder', isReadOnly = None, wordTypeID = None):
        if not groupName:
            raise AuthoringValidationError('You must specify a group name.')
        messageGroupTable = bsdWrappers.GetTable(MessageGroup.__primaryTable__)
        if groupName:
            groupName = MessageGroup.GenerateUniqueName(parentID, groupName)
        if parentID is not None and MessageGroup.Get(parentID) is None:
            raise AuthoringValidationError('Parent(%s) was not found. Can not create this group. groupName : %s ' % (parentID, groupName))
        newGroup = bsdWrappers.BaseWrapper._Create(cls, parentID=parentID, groupName=groupName, isReadOnly=isReadOnly, wordTypeID=wordTypeID)
        if parentID is not None:
            projectList = locProject.Project.GetProjectsForGroup(parentID)
            for aProject in projectList:
                aProject.AddGroupToProject(newGroup.groupID)

            if MessageGroup.Get(parentID).important:
                newGroup.important = MessageGroup.Get(parentID).important
        return newGroup

    @classmethod
    def Get(cls, groupID):
        return bsdWrappers._TryGetObjByKey(MessageGroup, keyID1=groupID, keyID2=None, keyID3=None, _getDeleted=False)

    def Copy(self, destGroupID):
        if destGroupID:
            destGroup = MessageGroup.Get(destGroupID)
            if not destGroup:
                raise AuthoringValidationError('Invalid groupID %s' % destGroupID)
            if destGroup.groupID == self.groupID:
                raise AuthoringValidationError('You cannot copy a group into itself.')
            if self._IsSubGroup(destGroup.groupID):
                raise AuthoringValidationError("You cannot copy group '%s' into group '%s' because it is a subgroup of '%s'." % (self.groupName, destGroup.groupName, self.groupName))
        newGroupName = MessageGroup.GenerateUniqueCopyName(self.groupID, destGroupID)
        self._Copy(destGroupID, newGroupName)

    def GetFolderPath(self, projectID = None):
        pathList = [self.groupName]
        groupDepth = 0
        currentNode = self
        while currentNode.parentID is not None and groupDepth < 100:
            currentNode = MessageGroup.Get(currentNode.parentID)
            if currentNode is not None:
                pathList = [currentNode.groupName] + pathList
            groupDepth += 1

        pathString = '/'.join(pathList)
        if projectID is not None:
            pathString = MessageGroup.TurnIntoRelativePath(pathString, locProject.Project.Get(projectID).workingDirectory)
        return pathString

    @staticmethod
    def TurnIntoRelativePath(absolutePath, workingDirectoryPath):
        if workingDirectoryPath:
            workingDirectoryPath = workingDirectoryPath.strip('/')
        if absolutePath:
            absolutePath = absolutePath.strip('/')
        if workingDirectoryPath and absolutePath:
            rootPathPrefix = '/'
            workingPathWithSlash = workingDirectoryPath + '/'
            absolutePath += '/'
            if absolutePath.startswith(workingPathWithSlash):
                newPath = absolutePath.replace(workingPathWithSlash, '', 1)
            else:
                newPath = rootPathPrefix + absolutePath
            return newPath.rstrip('/')
        else:
            return absolutePath

    def MarkImportant(self, impValue):
        self.important = impValue
        childGroups = MessageGroup.GetMessageGroupsByParentID(self.groupID)
        for childGroup in childGroups:
            childGroup.MarkImportant(impValue)

    def RemoveFromProject(self, projectName):
        projectRow = locProject.Project.GetByName(projectName)
        if not projectRow:
            raise AuthoringValidationError('No project (%s) was found. Can not tag with this project name.' % projectName)
        projectRow.RemoveGroupFromProject(self.groupID)

    def AddToProject(self, projectID):
        projectRow = locProject.Project.Get(projectID)
        if not projectRow:
            raise AuthoringValidationError('No project (%s) was found. Can not tag with this project id.' % projectID)
        projectRow.AddGroupToProject(self.groupID)

    def AddToProjectByName(self, projectName):
        projectRow = locProject.Project.GetByName(projectName)
        if not projectRow:
            raise AuthoringValidationError('No project (%s) was found. Can not tag with this project name.' % projectName)
        projectRow.AddGroupToProject(self.groupID)

    def GetWordCount(self, languageID = 'en-us', recursive = False, includeMetadata = True, projectID = None):
        wordCount = sum([ message.GetWordCount(languageID=languageID, includeMetadata=includeMetadata) for message in locMessage.Message.GetMessagesByGroupID(self.groupID) ])
        if recursive:
            childGroups = MessageGroup.GetMessageGroupsByParentID(self.groupID, projectID=projectID)
            for childGroup in childGroups:
                wordCount += childGroup.GetWordCount(languageID=languageID, recursive=recursive, projectID=projectID)

        return wordCount

    def _Copy(self, destGroupID, groupName):
        if sm.GetService('BSD').TransactionOngoing():
            raise AuthoringValidationError('You cannot copy groups from within a transaction.')
        groupID = MessageGroup.Create(parentID=destGroupID, groupName=groupName, isReadOnly=self.isReadOnly, wordTypeID=self.wordTypeID).groupID
        with bsd.BsdTransaction("Copying messages from group '%s' (groupID %s) to %s (groupID %s)" % (self.groupName,
         self.groupID,
         groupName,
         groupID)):
            for message in locMessage.Message.GetMessagesByGroupID(self.groupID):
                message.TransactionAwareCopy(groupID)

        childGroups = MessageGroup.GetMessageGroupsByParentID(self.groupID)
        for group in childGroups:
            group._Copy(groupID, group.groupName)

    def _DeleteChildren(self):
        with bsd.BsdTransaction():
            childGroups = MessageGroup.GetMessageGroupsByParentID(self.groupID)
            for group in childGroups:
                if not group.Delete():
                    return False

            messages = locMessage.Message.GetMessagesByGroupID(self.groupID)
            for message in messages:
                if not message.Delete():
                    return False

            for aProject in locProject.Project.GetProjectsForGroup(self.groupID):
                aProject.RemoveGroupFromProject(self.groupID)

        return True

    def ResetWordType(self):
        with bsd.BsdTransaction():
            for message in locMessage.Message.GetMessagesByGroupID(self.groupID):
                message.ResetWordType()

            bsdWrappers.BaseWrapper.__setattr__(self, 'wordTypeID', None)

    def _IsSubGroup(self, groupID):
        testGroup = MessageGroup.Get(groupID)
        while testGroup.parentID != None:
            if testGroup.parentID == self.groupID:
                return True
            testGroup = MessageGroup.Get(testGroup.parentID)

        return False

    @staticmethod
    def GetMessageGroupsByParentID(parentID, projectID = None):
        if projectID:
            currentProject = locProject.Project.Get(projectID)
            return currentProject.GetMessageGroupsByParentID(parentID)
        else:
            return MessageGroup.GetWithFilter(parentID=parentID)

    @staticmethod
    def GetVisibleGroupsByParentID(parentID, projectID = None):
        if projectID:
            currentProject = locProject.Project.Get(projectID)
            return currentProject.GetVisibleGroupsByParentID(parentID)
        else:
            return MessageGroup.GetMessageGroupsByParentID(parentID)

    @staticmethod
    def GenerateUniqueName(destGroupID, groupName):
        groupNames = [ group.groupName for group in MessageGroup.GetMessageGroupsByParentID(destGroupID) ]
        numDuplicates = 2
        newLabel = groupName
        while True:
            if newLabel not in groupNames:
                return newLabel
            newLabel = ''.join((groupName,
             ' (',
             str(numDuplicates),
             ')'))
            numDuplicates += 1

    @staticmethod
    def GenerateUniqueCopyName(sourceGroupID, destGroupID):
        sourceGroup = MessageGroup.Get(sourceGroupID)
        if not sourceGroup:
            raise AuthoringValidationError('%s is not a valid groupID' % sourceGroupID)
        if sourceGroup.parentID == destGroupID:
            return MessageGroup.GenerateUniqueName(destGroupID, sourceGroup.groupName + ' - Copy')
        return MessageGroup.GenerateUniqueName(destGroupID, sourceGroup.groupName)
