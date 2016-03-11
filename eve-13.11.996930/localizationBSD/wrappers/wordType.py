#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\wordType.py
from . import AuthoringValidationError
from ..const import WORD_TYPES_TABLE
from ..util import GetNumericLanguageIDFromLanguageID
import bsdWrappers
import wordProperty as locWordProperty

class WordType(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(WORD_TYPES_TABLE)

    def Copy(self, keyID = None, keyID2 = None, keyID3 = None, **kw):
        raise NotImplementedError

    def GetAllProperties(self, languageID):
        dbLanguageID = GetNumericLanguageIDFromLanguageID(languageID)
        if dbLanguageID != None:
            return locWordProperty.WordProperty.GetWithFilter(wordTypeID=self.wordTypeID, numericLanguageID=dbLanguageID)
        else:
            return []

    def GetPropertyEntry(self, wordPropertyID):
        propertyRow = locWordProperty.WordProperty.Get(wordPropertyID)
        if propertyRow is not None and propertyRow.wordTypeID == self.wordTypeID:
            return propertyRow

    def GetPropertyEntryByName(self, propertyName, languageID):
        dbLanguageID = GetNumericLanguageIDFromLanguageID(languageID)
        if dbLanguageID != None:
            propertyRows = locWordProperty.WordProperty.GetWithFilter(propertyName=propertyName, wordTypeID=self.wordTypeID, numericLanguageID=dbLanguageID)
            if propertyRows and len(propertyRows):
                return propertyRows[0]

    def AddPropertyEntry(self, propertyName, languageID, propertyDescription = None):
        locWordProperty.WordProperty.Create(propertyName, self.wordTypeID, languageID, propertyDescription=propertyDescription)

    def _DeleteChildren(self):
        wordProperties = locWordProperty.WordProperty.GetWithFilter(wordTypeID=self.wordTypeID)
        if wordProperties and len(wordProperties):
            raise AuthoringValidationError('Type (%s) can not be deleted, because it still has (%s) property(s).' % (self.wordTypeID, str(len(wordProperties))))
        return True

    @classmethod
    def Create(cls, typeName, typeDescription = None):
        if not typeName:
            raise AuthoringValidationError('Type name (%s) must be valid string.' % typeName)
        duplicateTypes = cls.GetWithFilter(typeName=typeName, _getDeleted=True)
        if duplicateTypes and len(duplicateTypes):
            raise AuthoringValidationError('Can not insert duplicate word type (%s).' % typeName)
        return bsdWrappers.BaseWrapper._Create(cls, typeName=typeName, typeDescription=typeDescription)
