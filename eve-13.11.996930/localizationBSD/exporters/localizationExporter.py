#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\exporters\localizationExporter.py
from ..wrappers.messageGroup import MessageGroup

class LocalizationMessage:

    def __init__(self):
        self.labelPath = None
        self.labelRow = None
        self._textRows = {}

    def GetTextRow(self, languageID):
        if languageID in self._textRows:
            return self._textRows[languageID]

    def GetAllTextDict(self):
        return self._textRows


class LocalizationExporterBase(object):
    EXPORT_DESCRIPTION = 'Undefined'

    @classmethod
    def ExportWithProjectSettings(cls, projectID, **kwargs):
        raise NotImplementedError

    @classmethod
    def GetResourceNamesWithProjectSettings(cls, projectID, **kwargs):
        raise NotImplementedError

    @classmethod
    def _GetLocalizationMessageDataForExport(cls, projectID, getSubmittedOnly, bsdBranchID = None):
        dbzlocalization = sm.GetService('DB2').GetSchema('zlocalization')
        exportResultSet = dbzlocalization.GetTableDataForMessageExport(1 if getSubmittedOnly else 0, projectID, bsdBranchID)
        messageResultSet = exportResultSet[0]
        labelsResultSet = exportResultSet[1]
        languageCodesResultSet = exportResultSet[2]
        projectResultSet = exportResultSet[3]
        maxDataID = exportResultSet[4][0].maxDataID
        workingDirectory = None
        if projectResultSet and len(projectResultSet):
            workingDirectory = projectResultSet[0].workingDirectory
        messagesDict = {}
        for aLabel in labelsResultSet:
            if aLabel.messageID in messagesDict:
                messageObj = messagesDict[aLabel.messageID]
            else:
                messageObj = messagesDict[aLabel.messageID] = LocalizationMessage()
            messageObj.labelRow = aLabel
            messageObj.labelPath = MessageGroup.TurnIntoRelativePath(aLabel.FullPath + '/' + aLabel.label, workingDirectory)

        langsByNumeric = languageCodesResultSet.Index('numericLanguageID')
        for textRow in messageResultSet:
            if textRow.messageID in messagesDict:
                messageObj = messagesDict[textRow.messageID]
            else:
                messageObj = messagesDict[textRow.messageID] = LocalizationMessage()
            languageID = langsByNumeric[textRow.numericLanguageID].languageID
            messageObj._textRows[languageID] = textRow

        folderPathToMessagesIndex = {}
        for aLabelRow in labelsResultSet:
            fullPath = MessageGroup.TurnIntoRelativePath(aLabelRow.FullPath, workingDirectory)
            if fullPath not in folderPathToMessagesIndex:
                folderPathToMessagesIndex[fullPath] = []
            folderPathToMessagesIndex[fullPath].append(messagesDict[aLabelRow.messageID])

        return (folderPathToMessagesIndex,
         messagesDict,
         languageCodesResultSet,
         projectResultSet,
         maxDataID)
