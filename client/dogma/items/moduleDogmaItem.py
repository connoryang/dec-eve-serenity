#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\moduleDogmaItem.py
from shipFittableDogmaItem import ShipFittableDogmaItem
from utillib import KeyVal
import dogma.const as dgmconst

class ModuleDogmaItem(ShipFittableDogmaItem):

    def GetEnvironmentInfo(self):
        otherID = None
        locationDogmaItem = self.location
        if locationDogmaItem is not None:
            otherID = locationDogmaItem.subLocations.get(self.flagID, None)
            if otherID is None:
                other = self.dogmaLocation.GetChargeNonDB(locationDogmaItem.itemID, self.flagID)
                if other is not None:
                    otherID = other.itemID
        return KeyVal(itemID=self.itemID, shipID=self.GetShipID(), charID=self.GetPilot(), otherID=otherID, targetID=None, effectID=None)

    def IsOnline(self):
        return dgmconst.effectOnline in self.activeEffects


class GhostModuleDogmaItem(ModuleDogmaItem):

    def GetPilot(self):
        return session.charid
