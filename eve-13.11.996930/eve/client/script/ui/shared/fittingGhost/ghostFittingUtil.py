#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingUtil.py
from dogma.items.shipFittableDogmaItem import ShipFittableDogmaItem
import evetypes
import util
OFFLINE = 0
ONLINE = 1
ACTIVE = 2
OVERHEATED = 3

class GhostFittingDataObject(object):

    def __init__(self, locationID, flagID, typeID, ownerID = None, number = None):
        self.locationID = locationID
        self.flagID = flagID
        self.typeID = typeID
        self.number = number
        self.itemID = self.GetItemKey()
        self.categoryID = evetypes.GetCategoryID(typeID)
        self.groupID = evetypes.GetGroupID(typeID)
        self.ownerID = session.charid

    def GetItemKey(self):
        if self.number is None:
            return '%s_%s' % (self.flagID, self.typeID)
        else:
            return '%s_%s_%s' % (self.flagID, self.typeID, self.number)

    def SetNumber(self, number):
        self.number = number
        self.itemID = self.GetItemKey()


class FakeGhostFittingDogmaItem(object):
    pass


class GhostFittingDogmaItem(ShipFittableDogmaItem):
    __guid__ = 'GhostFittingDogmaItem'

    def __init__(self, dogmaLocation, ghostFittingItem, ownerID):
        item = FakeGhostFittingDogmaItem()
        item.itemID = ghostFittingItem.GetItemKey()
        item.typeID = ghostFittingItem.typeID
        item.groupID = evetypes.GetGroupID(item.typeID)
        item.categoryID = evetypes.GetCategoryID(item.typeID)
        super(GhostFittingDogmaItem, self).__init__(dogmaLocation, item)
        self.ownerID = ownerID
        self.fittedItems = {}
        self.subLocations = {}

    def Load(self):
        self.attributes = {}

    def Unload(self):
        super(GhostFittingDogmaItem, self).Unload()
        self.dogmaLocation.RemoveSubLocationFromLocation(self.itemID)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        super(GhostFittingDogmaItem, self).SetLocation(locationID, locationDogmaItem, flagID)

    def UnsetLocation(self, locationDogmaItem):
        super(GhostFittingDogmaItem, self).UnsetLocation(locationDogmaItem)
        locationDogmaItem.RemoveSubLocation(self.itemID)

    def GetEnvironmentInfo(self):
        otherID = None
        if self.location is not None:
            otherID = self.dogmaLocation.GetSlotOther(self.location.itemID, self.flagID)
        return util.KeyVal(itemID=self.itemID, shipID=self.GetShipID(), charID=self.GetPilot(), otherID=otherID, targetID=None, effectID=None)
