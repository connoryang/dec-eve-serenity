#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\propertyHandlers\numericPropertyHandler.py
import eveLocalization
import carbon.common.script.util.format as fmtutils
import eve.common.script.util.eveFormat as evefmtutils
from basePropertyHandler import BasePropertyHandler
from .. import const as locconst

class NumericPropertyHandler(BasePropertyHandler):
    PROPERTIES = {locconst.CODE_UNIVERSAL: ['quantity',
                               'isk',
                               'aur',
                               'distance']}

    def _GetQuantity(self, value, languageID, *args, **kwargs):
        return value

    def _GetIsk(self, value, languageID, *args, **kwargs):
        return evefmtutils.FmtISK(value)

    def _GetAur(self, value, languageID, *args, **kwargs):
        return evefmtutils.FmtAUR(value)

    def _GetDistance(self, value, languageID, *args, **kwargs):
        return fmtutils.FmtDist(value, maxdemicals=kwargs.get('decimalPlaces', 3))


eveLocalization.RegisterPropertyHandler(eveLocalization.VARIABLE_TYPE.NUMERIC, NumericPropertyHandler())
