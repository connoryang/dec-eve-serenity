#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\characterListPropertyHandler.py
from .. import const as locconst
from basePropertyHandler import BasePropertyHandler
import log

class CharacterListPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('quantity', 'genders')}
    GENDER_NORMALIZATION_MAPPING = {1: locconst.GENDER_MALE,
     0: locconst.GENDER_FEMALE}

    def _GetQuantity(self, wrappedCharacters, languageID, *args, **kwargs):
        return len(wrappedCharacters)

    def _GetGenders(self, wrappedCharacters, languageID, *args, **kwargs):
        totalCharacters = len(wrappedCharacters)
        numberOfMales = 0
        numberOfFemales = 0
        for wrappedCharacter in wrappedCharacters:
            try:
                eveGender = cfg.eveowners.Get(wrappedCharacter).gender
            except KeyError:
                log.LogException()
                eveGender = 0

            characterGender = self.GENDER_NORMALIZATION_MAPPING[eveGender]
            if characterGender == locconst.GENDER_FEMALE:
                numberOfFemales += 1
            else:
                numberOfMales += 1
                break

        resultType = locconst.GENDERS_UNDEFINED
        if totalCharacters == 1:
            resultType = locconst.GENDERS_EXACTLY_ONE_FEMALE if numberOfFemales == 1 else locconst.GENDERS_EXACTLY_ONE_MALE
        elif totalCharacters > 1:
            resultType = locconst.GENDERS_AT_LEAST_ONE_MALE if numberOfMales >= 1 else locconst.GENDERS_ALL_FEMALE
        return resultType
