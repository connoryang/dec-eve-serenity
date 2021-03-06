#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localizationBSD\wrappers\wordProperty.py
from . import AuthoringValidationError
from ..const import WORD_PROPERTIES_TABLE
from ..util import GetNumericLanguageIDFromLanguageID
import bsdWrappers
from wordMetaData import WordMetaData

class WordProperty(bsdWrappers.BaseWrapper):
    __primaryTable__ = bsdWrappers.RegisterTable(WORD_PROPERTIES_TABLE)

    @classmethod
    def Create(cls, propertyName, wordTypeID, languageID, propertyDescription = None):
        if not propertyName:
            raise AuthoringValidationError('PropertyName (%s) must be a valid string.' % propertyName)
        dbLanguageID = GetNumericLanguageIDFromLanguageID(languageID)
        if dbLanguageID == None:
            raise AuthoringValidationError('Didnt find language (%s).' % languageID)
        from wordType import WordType
        if WordType.Get(wordTypeID) == None:
            raise AuthoringValidationError('Didnt find type (%s).' % wordTypeID)
        duplicateProps = cls.GetWithFilter(propertyName=propertyName, wordTypeID=wordTypeID, numericLanguageID=dbLanguageID, _getDeleted=True)
        if duplicateProps and len(duplicateProps):
            raise AuthoringValidationError('Can not insert duplicate properties. propertyName,wordTypeID,languageID : (%s,%s,%s) ' % (propertyName, wordTypeID, languageID))
        return bsdWrappers.BaseWrapper._Create(cls, propertyName=propertyName, wordTypeID=wordTypeID, numericLanguageID=dbLanguageID, propertyDescription=propertyDescription)

    def Copy(self, keyID = None, keyID2 = None, keyID3 = None, **kw):
        raise NotImplementedError

    def _DeleteChildren(self):
        wordMeta = WordMetaData.GetWithFilter(wordPropertyID=self.wordPropertyID)
        if wordMeta and len(wordMeta):
            raise AuthoringValidationError('Property (%s) can not be deleted, because it still has (%s) metadata entry(s).' % (self.wordPropertyID, str(len(wordMeta))))
        return True
