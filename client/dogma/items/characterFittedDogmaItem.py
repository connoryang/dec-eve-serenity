#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\characterFittedDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
import util
import weakref
from ccpProfile import TimedFunction

class CharacterFittedDogmaItem(FittableDogmaItem):

    def GetShipID(self):
        if self.location is None:
            self.dogmaLocation.LogWarn('CharacterFittedDogmaItem::GetShipID - item not fitted to location', self.itemID)
            return
        return self.location.GetShipID()

    @TimedFunction('CharacterFittedDogmaItem::SetLocation')
    def SetLocation(self, locationID, locationDogmaItem, flagID):
        self.flagID = flagID
        if locationDogmaItem is None:
            self.dogmaLocation.LogError('CharacterFittedDogmaItem::SetLocation, locationDogmaItem is None')
            return
        oldData = self.GetLocationInfo()
        self.location = weakref.proxy(locationDogmaItem)
        locationDogmaItem.RegisterFittedItem(self, flagID)
        return oldData

    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterFittedItem(self)

    def GetEnvironmentInfo(self):
        charID = self.GetPilot()
        shipID = self.dogmaLocation.shipsByPilotID.get(charID, None)
        return util.KeyVal(itemID=self.itemID, shipID=shipID, charID=charID, otherID=None, targetID=None, effectID=None)

    def GetPilot(self):
        return self.locationID


class GhostCharacterFittedDogmaItem(CharacterFittedDogmaItem):
    __guid__ = 'GhostCharacterFittedDogmaItem'

    def GetShipID(self):
        return self.dogmaLocation.shipID
