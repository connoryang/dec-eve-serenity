#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\chargeDogmaItem.py
from shipFittableDogmaItem import ShipFittableDogmaItem
import util
import inventorycommon.const as invconst

class ChargeDogmaItem(ShipFittableDogmaItem):

    def GetEnvironmentInfo(self):
        otherID = None
        if self.location is not None:
            otherID = self.dogmaLocation.GetSlotOther(self.location.itemID, self.flagID)
            if otherID is None and self.dogmaLocation.IsItemSubLocation(self.itemID):
                otherID = self.location.itemID
        return util.KeyVal(itemID=self.itemID, shipID=self.GetShipID(), charID=self.GetPilot(), otherID=otherID, targetID=None, effectID=None)

    def IsValidFittingCategory(self, categoryID):
        return categoryID in (invconst.categoryShip, invconst.categoryStarbase)

    def IsOwnerModifiable(self):
        pilotID = self.location.GetPilot()
        if not pilotID:
            return False
        shipID = self.locationID
        if not shipID:
            return False
        if self.dogmaLocation.IsItemSubLocation(self.itemID):
            if shipID == self.dogmaLocation.shipsByPilotID.get(pilotID, None):
                return True
        return False
