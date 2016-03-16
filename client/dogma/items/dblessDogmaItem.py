#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\dblessDogmaItem.py
from chargeDogmaItem import ChargeDogmaItem
from ccpProfile import TimedFunction

class DBLessDogmaItem(ChargeDogmaItem):

    @TimedFunction('DBLessDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(DBLessDogmaItem, self).__init__(dogmaLocation, item, eveCfg, clientIDFunc)
        self.fittedItems = {}
        self.subLocations = {}

    def Load(self):
        pass

    def Unload(self):
        super(DBLessDogmaItem, self).Unload()
        self.dogmaLocation.RemoveSubLocationFromLocation(self.itemID)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        super(DBLessDogmaItem, self).SetLocation(locationID, locationDogmaItem, flagID)
        locationDogmaItem.SetSubLocation(self.itemID)
        locationDogmaItem.MarkDirty()

    def UnsetLocation(self, locationDogmaItem):
        super(DBLessDogmaItem, self).UnsetLocation(locationDogmaItem)
        locationDogmaItem.RemoveSubLocation(self.itemID)
