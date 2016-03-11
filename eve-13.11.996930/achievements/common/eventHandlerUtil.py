#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\eventHandlerUtil.py
import evetypes

def ListContainsTypeInGivenCategories(typeIDs, categoryIDs):

    def IsCategoryInList(typeID):
        return evetypes.GetCategoryID(typeID) in categoryIDs

    return ContainsTypeInGivenCollections(typeIDs, IsCategoryInList)


def ListContainsTypeInGivenGroups(typeIDs, groupIDs):

    def IsGroupInList(typeID):
        return evetypes.GetGroupID(typeID) in groupIDs

    return ContainsTypeInGivenCollections(typeIDs, IsGroupInList)


def ContainsTypeInGivenCollections(typeIDs, checkFunc):
    for typeID in typeIDs:
        if not evetypes.Exists(typeID):
            continue
        if checkFunc(typeID):
            return True

    return False
