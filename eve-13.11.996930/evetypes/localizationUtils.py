#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evetypes\localizationUtils.py
_isBuilt = False
try:
    import localization
    _isBuilt = True
except ImportError:
    import localizationcache

def GetLocalizedTypeName(messageID, languageID = None):
    if _isBuilt:
        return localization.GetImportantByMessageID(messageID, languageID=languageID)
    elif messageID is None:
        return
    else:
        return localizationcache.GetMessage(GetTypeLocalizationPath(messageID), messageID, languageID=languageID)


def GetTypeLocalizationPath(messageID):
    return 'EVE/Evetypes/Types/Names/{0:02d}'.format(messageID % 100)


def GetLocalizedTypeDescription(messageID, languageID = None):
    if _isBuilt:
        return localization.GetByMessageID(messageID, languageID)
    elif messageID is None:
        return
    else:
        return localizationcache.GetMessage(GetDescriptionLocalizationPath(messageID), messageID, languageID=languageID)


def GetDescriptionLocalizationPath(messageID):
    return 'EVE/Evetypes/Types/Descriptions/{0:02d}'.format(messageID % 100)


def GetLocalizedGroupName(messageID, languageID = None):
    if _isBuilt:
        return localization.GetImportantByMessageID(messageID, languageID=languageID)
    else:
        return localizationcache.GetMessage('EVE/Evetypes/Groups/Names', messageID, languageID=languageID)


def GetLocalizedCategoryName(messageID, languageID = None):
    if _isBuilt:
        return localization.GetImportantByMessageID(messageID, languageID=languageID)
    else:
        return localizationcache.GetMessage('EVE/Evetypes/Categories/Names', messageID, languageID=languageID)
