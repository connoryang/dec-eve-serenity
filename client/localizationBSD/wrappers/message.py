#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\message.py
from . import AuthoringValidationError
from .. import const as localizationBSDConst
from ..util import GetNumericLanguageIDFromLanguageID
import bsdWrappers
import bsd
import dbutil
import re
from localization.const import LOCALE_SHORT_ENGLISH
import utillib as util
import messageText as locMessageText
import wordMetaData as locWordMetaData
import wordType as locWordType

class Message(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(localizationBSDConst.MESSAGES_TABLE)
    _messageTextTable = None
    _propertyTable = None
    _bsdSvc = None
    _APPEND_NEW = '(new)'

    def GetLabelPath(self, projectID = None):
        from messageGroup import MessageGroup
        labelPath = '' if self.label is None else self.label
        if self.groupID is not None:
            folderPath = MessageGroup.Get(self.groupID).GetFolderPath(projectID=projectID)
            if folderPath and labelPath:
                labelPath = '/'.join((folderPath, labelPath))
            elif folderPath:
                labelPath = folderPath
        return labelPath

    def GetOpenedBy(self):
        openedBy = [self._GetOpenedBy(self)]
        for messageText in locMessageText.MessageText.GetWithFilter(messageID=self.messageID):
            openedBy += [self._GetOpenedBy(messageText)]

        for metadata in locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID):
            openedBy += [self._GetOpenedBy(metadata)]

        openedBy = '\n'.join([ text for text in openedBy if text ])
        return openedBy

    def _GetOpenedBy(self, bsdWrapper):
        openedBy = ''
        openedByUserIDs = bsdWrapper.GetOpenedByUserIDs()
        bsdState = bsdWrapper.GetState()
        if bsdState & dbutil.BSDSTATE_OPENFORADD != 0:
            openedBy += bsdWrapper.__class__.__name__ + ' added by '
        elif bsdState & dbutil.BSDSTATE_OPENFORDELETE != 0:
            openedBy += bsdWrapper.__class__.__name__ + ' marked for delete by '
        elif bsdState & dbutil.BSDSTATE_OPENFOREDIT != 0:
            openedBy += bsdWrapper.__class__.__name__ + ' opened for edit by '
        elif openedByUserIDs:
            openedBy += bsdWrapper.__class__.__name__ + ' opened in unknown state by '
        if not openedBy:
            return openedBy
        openedBy += ', '.join((bsdWrapper.cache.Row(const.cacheStaticUsers, userID).userName for userID in openedByUserIDs))
        return openedBy

    def Copy(self, groupID, newLabel = None):
        Message._ErrorIfInTransaction('Message Copy will not run within Transaction.')
        copyLabel = newLabel or self.label
        if not Message.CheckIfLabelUnique(copyLabel, groupID):
            raise AuthoringValidationError('Label (%s) is not unique.' % copyLabel)
        messageCopy = Message.Create(copyLabel, groupID, text=self.GetTextEntry(LOCALE_SHORT_ENGLISH).text, context=self.context)
        englishText = messageCopy.GetTextEntry(LOCALE_SHORT_ENGLISH)
        originalEnglishText = self.GetTextEntry(LOCALE_SHORT_ENGLISH)
        originalTexts = self.messageTextTable.GetRows(messageID=self.messageID, _getDeleted=False)
        for aText in originalTexts:
            if aText.numericLanguageID != localizationBSDConst.LOCALE_ID_ENGLISH:
                newSourceDataID = englishText.dataID if originalEnglishText.dataID == aText.sourceDataID else None
                self.messageTextTable.AddRow(messageCopy.messageID, aText.numericLanguageID, sourceDataID=newSourceDataID, text=aText.text, statusID=aText.statusID)

        locWordMetaData.WordMetaData._CopyAllMetaDataToNewMessage(sourceMessageID=self.messageID, destMessageID=messageCopy.messageID, destinationWordTypeID=messageCopy.wordTypeID)
        return messageCopy

    def ResetWordType(self):
        if self.wordTypeID is not None:
            with bsd.BsdTransaction():
                self._DeleteMetaData()
                bsdWrappers.BaseWrapper.__setattr__(self, 'wordTypeID', None)

    def GetAllMetaDataEntries(self, languageID):
        metaDataForLanguage = []
        dbLanguageID = GetNumericLanguageIDFromLanguageID(languageID)
        propertyTable = self.__class__._propertyTable
        allMetaData = locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID)
        for metaEntry in allMetaData:
            propertyRow = propertyTable.GetRowByKey(metaEntry.wordPropertyID)
            if propertyRow and propertyRow.numericLanguageID == dbLanguageID:
                metaDataForLanguage.append(metaEntry)

        return metaDataForLanguage

    def GetMetaDataEntry(self, wordPropertyID):
        metaDataRows = locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID, wordPropertyID=wordPropertyID)
        if metaDataRows and len(metaDataRows):
            return metaDataRows[0]
        else:
            return None

    def GetMetaDataEntryByName(self, propertyName, languageID):
        propertyRows = self.__class__._propertyTable.GetRows(wordTypeID=self.wordTypeID, propertyName=propertyName, numericLanguageID=GetNumericLanguageIDFromLanguageID(languageID), _getDeleted=False)
        if propertyRows and len(propertyRows) != 1:
            return None
        else:
            metaDataRows = locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID, wordPropertyID=propertyRows[0].wordPropertyID)
            if metaDataRows and len(metaDataRows):
                return metaDataRows[0]
            return None

    def AddMetaDataEntry(self, wordPropertyID, metaDataValue, transactionBundle = None):
        if self.wordTypeID == None:
            raise AuthoringValidationError('Before adding metadata, the wordType needs to be set on this messageID (%s).' % str(self.messageID))
        with bsd.BsdTransaction():
            locWordMetaData.WordMetaData.TransactionAwareCreate(wordPropertyID, self.messageID, metaDataValue, transactionBundle=transactionBundle)

    def AddMetaDataEntryByName(self, propertyName, languageID, metaDataValue, transactionBundle = None):
        if self.wordTypeID == None:
            raise AuthoringValidationError('Before adding metadata, the wordType needs to be set on this messageID (%s).' % str(self.messageID))
        typeRow = locWordType.WordType.Get(self.wordTypeID)
        if typeRow == None:
            raise AuthoringValidationError('WordTypeID (%s), of this message, does not exist.' % self.wordTypeID)
        typeName = typeRow.typeName
        with bsd.BsdTransaction():
            locWordMetaData.WordMetaData.TransactionAwareCreateFromPropertyName(typeName, propertyName, languageID, self.messageID, metaDataValue, transactionBundle)

    def GetTextEntry(self, languageID):
        return locMessageText.MessageText.Get(self.messageID, languageID)

    def AddTextEntry(self, languageID, text):
        textRow = locMessageText.MessageText.Get(self.messageID, languageID)
        if textRow == None:
            locMessageText.MessageText.Create(self.messageID, languageID, text=text)
        else:
            raise AuthoringValidationError('Can not add duplicate text entry. messageID,languageID : (%s, %s)' % (str(self.messageID), languageID))

    def GetState(self):
        bsdState = super(Message, self).GetState()
        for messageText in locMessageText.MessageText.GetWithFilter(messageID=self.messageID):
            bsdState |= messageText.GetState()

        for metadata in locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID):
            bsdState |= metadata.GetState()

        return bsdState

    def GetWordCount(self, languageID = 'en-us', includeMetadata = True):
        textEntry = self.GetTextEntry(languageID)
        if not textEntry:
            return 0
        count = len([ part for part in re.findall('\\w*', textEntry.text or '') if part ])
        if includeMetadata:
            metadataEntries = self.GetAllMetaDataEntries(languageID)
            for metadata in metadataEntries:
                if metadata.metaDataValue:
                    count += len([ part for part in re.findall('\\w*', metadata.metaDataValue or '') if part ])

        return count

    def __init__(self, row):
        bsdWrappers.BaseWrapper.__init__(self, row)
        self.__class__.CheckAndSetCache()
        self.messageTextTable = self.__class__._messageTextTable

    def __setattr__(self, key, value):
        if key == localizationBSDConst.COLUMN_LABEL:
            if not Message.CheckIfLabelUnique(value, self.groupID):
                raise AuthoringValidationError('Label can not be set to non-unique name (%s).' % str(value))
        if key == localizationBSDConst.COLUMN_TYPE_ID:
            if self.wordTypeID is not None:
                raise AuthoringValidationError('Not allowed to edit wordTypeID on the message that may contain metadata. Use ResetWordType().')
            elif locWordType.WordType.Get(value) is None:
                raise AuthoringValidationError('WordTypeID (%s) does not exist.' % str(value))
        bsdWrappers.BaseWrapper.__setattr__(self, key, value)

    def _DeleteChildren(self):
        with bsd.BsdTransaction('Deleting message: %s' % self.label):
            self._DeleteText()
            self._DeleteMetaData()
        return True

    def _DeleteText(self):
        for messageText in locMessageText.MessageText.GetMessageTextsByMessageID(self.messageID):
            if not messageText.Delete():
                raise AuthoringValidationError('Message (%s) wrapper was unable to delete text entry.' % self.messageID)

    def _DeleteMetaData(self):
        for metaData in locWordMetaData.WordMetaData.GetWithFilter(messageID=self.messageID):
            if not metaData.Delete():
                raise AuthoringValidationError('Message (%s) wrapper was unable to metadata entry.' % self.messageID)

    @classmethod
    def Get(cls, messageID):
        return bsdWrappers._TryGetObjByKey(cls, messageID, _getDeleted=False)

    @classmethod
    def CheckAndSetCache(cls):
        if cls._messageTextTable is None or cls._propertyTable is None:
            bsdTableSvc = sm.GetService('bsdTable')
            cls._messageTextTable = bsdTableSvc.GetTable(localizationBSDConst.MESSAGE_TEXTS_TABLE)
            cls._propertyTable = bsdTableSvc.GetTable(localizationBSDConst.WORD_PROPERTIES_TABLE)
            cls._bsdSvc = sm.GetService('BSD')

    @classmethod
    def Create(cls, label, groupID = None, text = '', context = None):
        cls._ErrorIfInTransaction('Message Create will not run within Transaction. Use TransactionAwareCreate.')
        with bsd.BsdTransaction('Creating new message: %s' % label) as bsdTransaction:
            cls._TransactionAwareCreate(label, groupID, LOCALE_SHORT_ENGLISH, text, context, wordTypeID=None, transactionBundle=None)
        resultList = bsdTransaction.GetTransactionResult()
        return cls.Get(resultList[0][1].messageID)

    @classmethod
    def TransactionAwareCreate(cls, label, groupID = None, text = '', context = None, transactionBundle = None):
        cls._ErrorIfNotInTransaction('Message TransactionAwareCreate will not run within Transaction. Use Create.')
        with bsd.BsdTransaction('Creating new message: %s' % label):
            actionIDsResult = cls._TransactionAwareCreate(label, groupID, LOCALE_SHORT_ENGLISH, text, context, wordTypeID=None, transactionBundle=transactionBundle)
        return actionIDsResult

    @classmethod
    def _GetGroupRecord(cls, groupID, transactionBundle = None):
        from messageGroup import MessageGroup
        if transactionBundle and type(groupID) != int:
            currentGroup = transactionBundle.get(localizationBSDConst.BUNDLE_GROUP, {}).get(groupID, None)
        else:
            currentGroup = MessageGroup.Get(groupID)
        return currentGroup

    @classmethod
    def _GetWordTypeID(cls, groupID, transactionBundle = None):
        wordTypeID = None
        if groupID is not None:
            parentGroup = cls._GetGroupRecord(groupID, transactionBundle=transactionBundle)
            if parentGroup:
                wordTypeID = parentGroup.wordTypeID
        return wordTypeID

    @classmethod
    def _ValidateCreationOfMessage(cls, label, groupID, wordTypeID, transactionBundle = None):
        if not cls.CheckIfLabelUnique(label, groupID, transactionBundle=transactionBundle):
            raise AuthoringValidationError('Label (%s) in groupID (%s) is not unique.' % (label, str(groupID)))
        if groupID != None:
            parentGroup = cls._GetGroupRecord(groupID, transactionBundle=transactionBundle)
            if parentGroup:
                if wordTypeID != parentGroup.wordTypeID:
                    raise AuthoringValidationError('Group type doesnt match message type (%s,%s).' % (wordTypeID, parentGroup.wordTypeID))
            else:
                raise AuthoringValidationError("Parent group (%s) wasn't found." % str(groupID))
        if wordTypeID != None:
            typeRow = locWordType.WordType.Get(wordTypeID)
            if typeRow == None:
                raise AuthoringValidationError("Type (%s) wasn't found." % wordTypeID)
        return True

    @classmethod
    def _TransactionAwareCreate(cls, label, groupID, languageID, text, context, wordTypeID = None, transactionBundle = None):
        inheritedWordTypeID = Message._GetWordTypeID(groupID)
        if wordTypeID is None:
            wordTypeID = inheritedWordTypeID
        Message._ValidateCreationOfMessage(label, groupID, wordTypeID, transactionBundle=transactionBundle)
        dbLocaleID = GetNumericLanguageIDFromLanguageID(languageID)
        if dbLocaleID is None:
            raise AuthoringValidationError('Didnt find language (%s).' % languageID)
        reservedActionID = bsdWrappers.BaseWrapper._Create(cls, label=label, groupID=groupID, context=context, wordTypeID=wordTypeID)
        if transactionBundle:
            tupleActionID = (reservedActionID, 'messageID')
            transactionBundle[localizationBSDConst.BUNDLE_MESSAGE][tupleActionID] = util.KeyVal({'label': label,
             'groupID': groupID,
             'context': context,
             'wordTypeID': wordTypeID})
        messageTextTable = bsdWrappers.GetTable(locMessageText.MessageText.__primaryTable__)
        messageTextTable.AddRow((reservedActionID, 'messageID'), dbLocaleID, text=text)
        if type(reservedActionID) == int:
            return {'reservedMessageID': reservedActionID}
        raise AuthoringValidationError('Unexpected error. Possibly incorrect use of transactions. Expected actionID but instead got : %s ' % str(reservedActionID))

    @classmethod
    def _ErrorIfInTransaction(cls, errorMessage):
        cls.CheckAndSetCache()
        if cls._bsdSvc.TransactionOngoing():
            raise AuthoringValidationError(errorMessage)

    @classmethod
    def _ErrorIfNotInTransaction(cls, errorMessage):
        cls.CheckAndSetCache()
        if not cls._bsdSvc.TransactionOngoing():
            raise AuthoringValidationError(errorMessage)

    @staticmethod
    def CheckIfLabelUnique(originalLabel, groupID, transactionBundle = None, _appendWord = None):
        isUnique, label = Message._CheckLabelUniqueness(originalLabel, groupID, transactionBundle=transactionBundle, returnUnique=False, _appendWord=_appendWord)
        return isUnique

    @staticmethod
    def GetUniqueLabel(originalLabel, groupID, transactionBundle = None, _appendWord = None):
        isUnique, label = Message._CheckLabelUniqueness(originalLabel, groupID, transactionBundle=transactionBundle, returnUnique=True, _appendWord=_appendWord)
        return label

    @staticmethod
    def GetMessageByID(messageID):
        primaryTable = bsdWrappers.GetTable(Message.__primaryTable__)
        return primaryTable.GetRowByKey(_wrapperClass=Message, keyId1=messageID, _getDeleted=False)

    @staticmethod
    def GetMessagesByGroupID(groupID, projectID = None):
        return Message.GetWithFilter(groupID=groupID)

    @staticmethod
    def _CheckLabelUniqueness(originalLabel, groupID, transactionBundle = None, returnUnique = False, _appendWord = None):
        isOriginalLabelUnique = True
        if originalLabel is None:
            return (isOriginalLabelUnique, None)
        primaryTable = bsdWrappers.GetTable(Message.__primaryTable__)
        newLabel = originalLabel
        while True:
            labels = primaryTable.GetRows(label=newLabel, groupID=groupID, _getDeleted=True)
            atLeastOneMatch = False
            if transactionBundle:
                for key, aLabel in transactionBundle[localizationBSDConst.BUNDLE_MESSAGE].iteritems():
                    if aLabel.label == newLabel and aLabel.groupID == groupID:
                        atLeastOneMatch = True
                        break

            if labels and len(labels) or atLeastOneMatch:
                isOriginalLabelUnique = False
                if returnUnique:
                    newLabel = newLabel + (Message._APPEND_NEW if not _appendWord else _appendWord)
                else:
                    break
            else:
                break

        if returnUnique:
            return (isOriginalLabelUnique, newLabel)
        else:
            return (isOriginalLabelUnique, None)
