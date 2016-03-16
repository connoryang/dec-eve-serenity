#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\formatters\listFormatters.py
import telemetry
from ..uiutil import PrepareLocalizationSafeString

@telemetry.ZONE_FUNCTION
def FormatGenericList(iterable, languageID = None, useConjunction = False):
    import localization
    stringList = [ unicode(each) for each in iterable ]
    delimiter = localization.GetByLabel('UI/Common/Formatting/ListGenericDelimiter', languageID)
    if not useConjunction or len(stringList) < 2:
        listString = delimiter.join(stringList)
    elif len(stringList) == 2:
        listString = localization.GetByLabel('UI/Common/Formatting/SimpleGenericConjunction', languageID, A=stringList[0], B=stringList[1])
    else:
        listPart = delimiter.join(stringList[:-1])
        listString = localization.GetByLabel('UI/Common/Formatting/ListGenericConjunction', languageID, list=listPart, lastItem=stringList[-1])
    return PrepareLocalizationSafeString(listString, messageID='genericlist')
