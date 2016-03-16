#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\formatters\numericFormatters.py
import telemetry
from .. import uiutil
from .. import internalUtil
import eveLocalization

@telemetry.ZONE_FUNCTION
def FormatNumeric(value, useGrouping = False, decimalPlaces = None, leadingZeroes = None):
    result = eveLocalization.FormatNumeric(value, internalUtil.GetLanguageID(), useGrouping=useGrouping, decimalPlaces=decimalPlaces, leadingZeroes=leadingZeroes)
    return uiutil.PrepareLocalizationSafeString(result, messageID='numeric')
