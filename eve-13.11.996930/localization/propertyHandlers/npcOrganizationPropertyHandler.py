#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\npcOrganizationPropertyHandler.py
import const
import eveLocalization
from basePropertyHandler import BasePropertyHandler
import log
from .. import GetMetaData
from .. import const as locconst
from ..logger import LogWarn

class NpcOrganizationPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('name', 'rawName', 'nameWithArticle'),
     locconst.LOCALE_SHORT_ENGLISH: ('nameWithArticle',),
     locconst.LOCALE_SHORT_RUSSIAN: ('gender',),
     locconst.LOCALE_SHORT_GERMAN: ('gender',),
     locconst.LOCALE_SHORT_FRENCH: ('nameWithArticle', 'genitiveName')}

    def _GetName(self, npcOrganizationID, languageID, *args, **kwargs):
        if const.minFaction <= npcOrganizationID <= const.maxFaction or const.minNPCCorporation <= npcOrganizationID <= const.maxNPCCorporation:
            try:
                return cfg.eveowners.Get(npcOrganizationID).name
            except KeyError:
                log.LogException()
                return '[no npcOrganization: %d]' % npcOrganizationID

    def _GetRawName(self, npcOrganizationID, languageID, *args, **kwargs):
        if const.minFaction <= npcOrganizationID <= const.maxFaction or const.minNPCCorporation <= npcOrganizationID <= const.maxNPCCorporation:
            try:
                return cfg.eveowners.Get(npcOrganizationID).GetRawName(languageID)
            except KeyError:
                log.LogException()
                return '[no npcOrganization: %d]' % npcOrganizationID

    if boot.role != 'client':
        _GetName = _GetRawName

    def _GetArticleEN_US(self, npcOrganizationID, *args, **kwargs):
        try:
            messageID = cfg.eveowners.Get(npcOrganizationID).ownerNameID
        except KeyError:
            log.LogException()
            return '[no npcOrganization: %d]' % npcOrganizationID

        try:
            return GetMetaData(messageID, 'article', languageID=locconst.LOCALE_SHORT_ENGLISH)
        except:
            LogWarn("npcOrganizationID %s does not have the requested metadata 'article' in language '%s. Returning empty string by default." % (itemID, locconst.LOCALE_SHORT_ENGLISH))
            return ''

    def _GetNameWithArticle(self, npcOrganizationID, languageID, *args, **kwargs):
        return self._GetName(npcOrganizationID, languageID, args, kwargs)

    def _GetNameWithArticleEN_US(self, npcOrganizationID, *args, **kwargs):
        englishName = self._GetName(npcOrganizationID, locconst.LOCALE_SHORT_ENGLISH) or 'None'
        if 'The ' in englishName:
            return englishName
        else:
            return self._PrepareLocalizationSafeString(' '.join(('the', englishName)))

    def _GetGenderDE(self, npcOrganizationID, *args, **kwargs):
        return locconst.GENDER_MALE

    def _GetGenderRU(self, npcOrganizationID, *args, **kwargs):
        return locconst.GENDER_MALE

    def _GetNameWithArticleFR(self, npcOrganizationID, *args, **kwargs):
        ret = self._GetName(npcOrganizationID, locconst.LOCALE_SHORT_FRENCH)
        messageID = cfg.eveowners.Get(npcOrganizationID).ownerNameID
        try:
            article = GetMetaData(messageID, 'article', locconst.LOCALE_SHORT_FRENCH)
        except KeyError:
            log.LogException()
            return ret

        if article:
            if article.endswith("'"):
                ret = article + ret
            else:
                ret = ' '.join((article, ret))
        return ret

    def _GetGenitiveNameFR(self, npcOrganizationID, *args, **kwargs):
        ret = self._GetName(npcOrganizationID, locconst.LOCALE_SHORT_FRENCH)
        messageID = cfg.eveowners.Get(npcOrganizationID).ownerNameID
        try:
            article = GetMetaData(messageID, 'genitiveArticle', locconst.LOCALE_SHORT_FRENCH)
        except KeyError:
            log.LogException()
            return ret

        if article:
            if article.endswith("'"):
                ret = article + ret
            else:
                ret = ' '.join((article, ret))
        return ret

    def GetShowInfoData(self, ownerID, *args, **kwargs):
        try:
            item = cfg.eveowners.Get(ownerID)
        except KeyError:
            log.LogException()
            return [0, 0]

        return [item.typeID, ownerID]


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.NPCORGANIZATION, NpcOrganizationPropertyHandler())
