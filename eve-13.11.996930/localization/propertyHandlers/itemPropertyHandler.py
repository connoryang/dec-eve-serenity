#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\itemPropertyHandler.py
import eveLocalization
import evetypes
import localization
from basePropertyHandler import BasePropertyHandler
import log
from .. import const as locconst
from ..logger import LogWarn
import eve.common.script.util.eveFormat as evefmt

class ItemPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ('name', 'rawName', 'quantity', 'quantityName', 'nameWithArticle'),
     locconst.LOCALE_SHORT_ENGLISH: ('nameWithArticle',),
     locconst.LOCALE_SHORT_GERMAN: ('gender',),
     locconst.LOCALE_SHORT_RUSSIAN: ('gender',)}

    def _GetName(self, typeID, languageID, *args, **kwargs):
        try:
            return evetypes.GetName(typeID)
        except KeyError:
            log.LogException()
            return '[no type: %d]' % typeID

    def _GetRawName(self, typeID, languageID, *args, **kwargs):
        try:
            return evetypes.GetName(typeID, languageID)
        except KeyError:
            log.LogException()
            return '[no type: %d]' % typeID

    if boot.role != 'client':
        _GetName = _GetRawName

    def _GetQuantity(self, itemID, languageID, *args, **kwargs):
        return kwargs.get('dereferencedQuantity', 1)

    def _GetQuantityName(self, typeID, languageID, *args, **kwargs):
        quantity = kwargs.get('dereferencedQuantity', 1)
        if typeID == const.typeCredits:
            return evefmt.FmtCurrency(quantity)
        return localization.GetByLabel('UI/Common/QuantityAndItem', quantity=quantity, item=typeID)

    def _GetArticleEN_US(self, typeID, *args, **kwargs):
        try:
            messageID = evetypes.GetNameID(typeID)
        except KeyError:
            return '[no type: %d]' % typeID

        try:
            return localization.GetMetaData(messageID, 'article', languageID=locconst.LOCALE_SHORT_ENGLISH)
        except KeyError:
            return ''

    def _GetNameWithArticle(self, itemID, languageID, *args, **kwargs):
        return self._GetName(itemID, languageID, args, kwargs)

    def _GetNameWithArticleEN_US(self, itemID, *args, **kwargs):
        article = self._GetArticleEN_US(itemID)
        englishName = self._GetName(itemID, locconst.LOCALE_SHORT_ENGLISH)
        if article:
            return self._PrepareLocalizationSafeString(' '.join((article, englishName)))
        else:
            return englishName

    def _GetGenderDE(self, typeID, *args, **kwargs):
        try:
            messageID = evetypes.GetNameID(typeID)
        except KeyError:
            log.LogException()
            return locconst.GENDER_MALE

        try:
            return localization.GetMetaData(messageID, 'gender', languageID=locconst.LOCALE_SHORT_GERMAN)
        except KeyError:
            LogWarn("itemID %s does not have the requested metadata 'gender' in language '%s. Returning masculine gender by default." % (typeID, locconst.LOCALE_SHORT_GERMAN))
            return locconst.GENDER_MALE

    def _GetGenderRU(self, typeID, *args, **kwargs):
        try:
            messageID = evetypes.GetNameID(typeID)
        except KeyError:
            log.LogException()
            return locconst.GENDER_MALE

        try:
            return localization.GetMetaData(messageID, 'gender', languageID=locconst.LOCALE_SHORT_RUSSIAN)
        except KeyError:
            LogWarn("itemID %s does not have the requested metadata 'gender' in language '%s. Returning masculine gender by default." % (typeID, locconst.LOCALE_SHORT_RUSSIAN))
            return locconst.GENDER_MALE

    def Linkify(self, typeID, linkText):
        return '<a href=showinfo:' + str(typeID) + '>' + linkText + '</a>'


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.ITEM, ItemPropertyHandler())
