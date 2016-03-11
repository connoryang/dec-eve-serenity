#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\wordMetaData.py
from . import AuthoringValidationError
from .. import const as localizationBSDConst
from ..util import GetNumericLanguageIDFromLanguageID
import bsdWrappers
import bsd
import utillib as util

class WordMetaData(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(localizationBSDConst.WORD_METADATA_TABLE)
    _typesTable = None
    _propertyTable = None
    _metaDataTable = None
    _bsdSvc = None

    def Copy(self, keyID = None, keyID2 = None, keyID3 = None, **kw):
        raise NotImplementedError

    def __setattr__(self, key, value):
        if key == localizationBSDConst.COLUMN_MESSAGEID or key == localizationBSDConst.COLUMN_PROPERTY_ID:
            raise AuthoringValidationError('Not allowed to edit messageID or wordPropertyID on the metadata.')
        bsdWrappers.BaseWrapper.__setattr__(self, key, value)

    def __init__(self, row):
        bsdWrappers.BaseWrapper.__init__(self, row)
        self.__class__.CheckAndSetCache()

    @classmethod
    def _GetMessageRecord(cls, messageID, transactionBundle = None):
        from message import Message
        currentMessage = None
        if transactionBundle and type(messageID) != int:
            currentMessage = transactionBundle[localizationBSDConst.BUNDLE_MESSAGE].get(messageID, None)
        else:
            currentMessage = Message.Get(messageID)
        return currentMessage

    @classmethod
    def _ValidateCreationOfMetaData(cls, wordPropertyID, messageID, metaDataValue, transactionBundle = None):
        cls.CheckAndSetCache()
        propertyRow = cls._propertyTable.GetRowByKey(keyId1=wordPropertyID, _getDeleted=False)
        if propertyRow:
            wordTypeID = propertyRow.wordTypeID
        else:
            raise AuthoringValidationError('Couldnt find typeID of the propertyID (%s).' % wordPropertyID)
        currentMessage = cls._GetMessageRecord(messageID, transactionBundle)
        if currentMessage is None:
            raise AuthoringValidationError('Couldnt find message parent of this metadata. MessageID (%s).' % str(messageID))
        if wordTypeID != currentMessage.wordTypeID:
            raise AuthoringValidationError("Couldnt verify that property's typeID (%s) matches message's typeID (%s)." % (wordTypeID, currentMessage.wordTypeID))
        duplicateMetaData = cls._metaDataTable.GetRows(wordPropertyID=wordPropertyID, messageID=messageID)
        if duplicateMetaData and len(duplicateMetaData):
            raise AuthoringValidationError('Can not add duplicate metadata. wordPropertyID,messageID : (%s, %s)' % (wordPropertyID, str(messageID)))
        if cls._bsdSvc.TransactionOngoing() and transactionBundle:
            for aMetaData in transactionBundle[localizationBSDConst.BUNDLE_METADATA]:
                if aMetaData.wordPropertyID == wordPropertyID and aMetaData.messageID == messageID:
                    raise AuthoringValidationError('Can not add duplicate metadata. wordPropertyID,messageID : (%s, %s)' % (wordPropertyID, str(messageID)))

        return True

    @classmethod
    def _TransactionAwareCreate(cls, wordPropertyID, messageID, metaDataValue, transactionBundle = None):
        cls._ValidateCreationOfMetaData(wordPropertyID, messageID, metaDataValue, transactionBundle)
        if transactionBundle:
            transactionBundle[localizationBSDConst.BUNDLE_METADATA].append(util.KeyVal({'wordPropertyID': wordPropertyID,
             'messageID': messageID,
             'metaDataValue': metaDataValue}))
        result = bsdWrappers.BaseWrapper._Create(cls, wordPropertyID=wordPropertyID, messageID=messageID, metaDataValue=metaDataValue)
        if type(result) == int:
            return {'reservedWordMetaDataID': result}
        else:
            return result

    @classmethod
    def TransactionAwareCreate(cls, wordPropertyID, messageID, metaDataValue, transactionBundle = None):
        return cls._TransactionAwareCreate(wordPropertyID, messageID, metaDataValue, transactionBundle)

    @classmethod
    def Create(cls, wordPropertyID, messageID, metaDataValue):
        return cls._TransactionAwareCreate(wordPropertyID, messageID, metaDataValue, transactionBundle=None)

    @classmethod
    def _TransactionAwareCreateFromPropertyName(cls, typeName, propertyName, languageID, messageID, metaDataValue, transactionBundle = None):
        cls.CheckAndSetCache()
        typeAndProperty = cls._GetWordTypeAndPropertyID(cls._typesTable, cls._propertyTable, typeName, propertyName, languageID)
        if typeAndProperty is None:
            raise AuthoringValidationError('Didnt find matching type and property for typeName,propertyName : (%s,%s).' % (typeName, propertyName))
        wordTypeID, wordPropertyID = typeAndProperty
        return cls._TransactionAwareCreate(wordPropertyID, messageID, metaDataValue, transactionBundle)

    @classmethod
    def CreateFromPropertyName(cls, typeName, propertyName, languageID, messageID, metaDataValue):
        return cls._TransactionAwareCreateFromPropertyName(typeName, propertyName, languageID, messageID, metaDataValue, transactionBundle=None)

    @classmethod
    def TransactionAwareCreateFromPropertyName(cls, typeName, propertyName, languageID, messageID, metaDataValue, transactionBundle = None):
        return cls._TransactionAwareCreateFromPropertyName(typeName, propertyName, languageID, messageID, metaDataValue, transactionBundle)

    @classmethod
    def CheckAndSetCache(cls):
        if cls._typesTable is None or cls._propertyTable is None or cls._metaDataTable is None:
            bsdTableSvc = sm.GetService('bsdTable')
            cls._typesTable = bsdTableSvc.GetTable(localizationBSDConst.WORD_TYPES_TABLE)
            cls._propertyTable = bsdTableSvc.GetTable(localizationBSDConst.WORD_PROPERTIES_TABLE)
            cls._metaDataTable = bsdTableSvc.GetTable(localizationBSDConst.WORD_METADATA_TABLE)
            cls._bsdSvc = sm.GetService('BSD')

    @classmethod
    def _CopyAllMetaDataToNewMessage(cls, sourceMessageID, destMessageID, destinationWordTypeID, transactionBundle = None):
        cls.CheckAndSetCache()
        sourceMetaRows = cls._metaDataTable.GetRows(messageID=sourceMessageID, _getDeleted=False)
        with bsd.BsdTransaction():
            for aMetaRow in sourceMetaRows:
                propertyRow = cls._propertyTable.GetRowByKey(aMetaRow.wordPropertyID)
                if propertyRow.wordTypeID != destinationWordTypeID:
                    raise AuthoringValidationError('Source metadata property typeID doesnt match destination typeID. (%s, %s).' % (propertyRow.wordTypeID, destinationWordTypeID))
                cls._TransactionAwareCreate(wordPropertyID=aMetaRow.wordPropertyID, messageID=destMessageID, metaDataValue=aMetaRow.metaDataValue, transactionBundle=transactionBundle)

        return True

    @staticmethod
    def _GetWordTypeAndPropertyID(typesTable, propertiesTable, typeName, propertyName, languageID):
        wordTypeID = None
        wordPropertyID = None
        typeRows = typesTable.GetRows(typeName=typeName, _getDeleted=False)
        if typeRows and len(typeRows):
            wordTypeID = typeRows[0].wordTypeID
        else:
            return
        dbLanguageID = GetNumericLanguageIDFromLanguageID(languageID)
        propertyRows = propertiesTable.GetRows(propertyName=propertyName, wordTypeID=wordTypeID, numericLanguageID=dbLanguageID, _getDeleted=False)
        if propertyRows and len(propertyRows):
            wordPropertyID = propertyRows[0].wordPropertyID
        else:
            return
        return (wordTypeID, wordPropertyID)
