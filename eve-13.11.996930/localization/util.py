#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localization\util.py
import pytelemetry.zoning as telemetry
from carbon.common.script.util.commonutils import StripTags
import internalUtil
from . import const as locconst

def ConvertLanguageIDFromMLS(mlsLanguageID):
    if mlsLanguageID.lower() == 'en':
        return 'en-us'
    else:
        return mlsLanguageID.lower()


def ConvertLanguageIDToMLS(languageID):
    if languageID.lower() == 'en-us':
        return 'EN'
    else:
        return languageID.upper()


def GetLanguageID():
    return internalUtil.GetLanguageID()


def GetDefaultServerLanguageID():
    if boot.region == 'optic':
        return locconst.LOCALE_SHORT_CHINESE
    else:
        return locconst.LOCALE_SHORT_ENGLISH


def StandardizedLanguageIDOrDefault(fromLanguageID = None):
    if not fromLanguageID:
        return internalUtil.GetLanguageID()
    else:
        fromLanguageID = fromLanguageID.lower()
        if fromLanguageID == 'en':
            return 'en-us'
        return fromLanguageID


def GetSortFunc(languageID):
    languageID = StandardizedLanguageIDOrDefault(languageID)
    import eveLocalization
    collator = eveLocalization.Collator()
    collator.locale = str(languageID)

    def SortFunc(left, right):
        res = collator.Compare(unicode(left.lower()), unicode(right.lower()))
        if res == 0:
            return collator.Compare(unicode(right), unicode(left))
        return res

    return SortFunc


@telemetry.ZONE_FUNCTION
def Sort(iterable, cmp = None, key = lambda x: x, reverse = False, languageID = None):
    import localization
    if cmp:
        raise ValueError("Passing a compare function into Sort defeats the purpose of using a language-aware sort.  You probably want to use the 'key' parameter instead.")
    cmpFunc = GetSortFunc(languageID)
    if all([ isinstance(key(each), (int, type(None))) for each in iterable ]):

        def getPronunciation(messageID):
            if not messageID:
                return ''
            ret = ''
            try:
                ret = localization.GetMetaData(messageID, 'pronounciation', languageID=languageID)
            except KeyError:
                ret = localization.GetByMessageID(messageID, languageID)

            return ret

        return sorted(iterable, cmp=cmpFunc, key=lambda x: StripTags(getPronunciation(key(x))), reverse=reverse)
    return sorted(iterable, cmp=cmpFunc, key=lambda x: StripTags(key(x)), reverse=reverse)


def IsSearchTextIdeographic(languageID, textString):
    languageID = StandardizedLanguageIDOrDefault(languageID)
    if languageID in (locconst.LOCALE_SHORT_JAPANESE, locconst.LOCALE_SHORT_CHINESE):
        try:
            textString.encode('ascii')
        except UnicodeEncodeError:
            return True

    return False
