#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\marketutil\quickbarUtil.py
from collections import defaultdict

def GetTypesUnderFolder(parentID, quickbar):
    foldersByParentID, typesByParentID = GetFolderAndTypeDicts(quickbar)
    typesUnderFolder = defaultdict(int)
    typesInParentFolder = typesByParentID.get(parentID, {})
    AddTypesAndQtyInFolder(typesInParentFolder, typesUnderFolder)
    currentIteration = foldersByParentID.get(parentID)
    while currentIteration:
        nextIteration = set()
        for eachID in currentIteration:
            subFolders = foldersByParentID.get(eachID, set())
            nextIteration.update(subFolders)
            inFolder = typesByParentID.get(eachID, {})
            AddTypesAndQtyInFolder(inFolder, typesUnderFolder)

        currentIteration = nextIteration

    return dict(typesUnderFolder)


def AddTypesAndQtyInFolder(inFolder, typesUnderFolder):
    for typeID, extraText in inFolder:
        try:
            qty = int(extraText)
        except ValueError:
            qty = 1

        typesUnderFolder[typeID] += qty


def GetFolderAndTypeDicts(quickbar):
    foldersByParentID = defaultdict(set)
    typesByParentID = defaultdict(list)
    for dataID, data in quickbar.iteritems():
        if data.label is None:
            continue
        if isinstance(data.label, unicode):
            foldersByParentID[data.parent].add(data.id)
        else:
            try:
                extraText = data.extraText
            except:
                extraText = ''

            typesByParentID[data.parent].append((data.label, extraText))

    return (foldersByParentID, typesByParentID)
