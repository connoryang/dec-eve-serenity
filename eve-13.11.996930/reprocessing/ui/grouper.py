#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\grouper.py
import evetypes

class Grouper(object):

    def __init__(self, groupingFunc, getGroupName):
        self.groupingFunc = groupingFunc
        self.getGroupName = getGroupName

    def GetGroupIDs(self, items):
        return {self.GetGroupID(i) for i in items}

    def GetGroupID(self, item):
        return self.groupingFunc(item.typeID)

    def GetGroupName(self, groupID):
        return self.getGroupName(groupID)


def GetCategoryGrouper():
    return Grouper(lambda typeID: evetypes.GetCategoryID(typeID), lambda categoryID: evetypes.GetCategoryNameByCategory(categoryID))


def GetGroupGrouper():
    return Grouper(lambda typeID: evetypes.GetGroupID(typeID), lambda groupID: evetypes.GetGroupNameByGroup(groupID))
