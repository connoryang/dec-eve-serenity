#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\textImporting\__init__.py
import evetypes

def GetValidNamesAndTypesDict(validCategoryIDs):
    return {evetypes.GetName(typeID).lower():typeID for typeID in evetypes.GetTypeIDsByCategories(validCategoryIDs)}


def GetLines(text, wordsToRemove = None):
    textWithBr = text.replace('\n', '<br>').replace('\r\n', '<br>')
    if wordsToRemove:
        for word in wordsToRemove:
            textWithBr = textWithBr.replace(word, '')

    lines = SplitAndStrip(textWithBr, '<br>')
    return lines


def SplitAndStrip(text, splitOn):
    parts = text.split(splitOn)
    parts = [ x.strip() for x in parts if x.strip() ]
    return parts
