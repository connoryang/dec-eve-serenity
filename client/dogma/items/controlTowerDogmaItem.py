#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\controlTowerDogmaItem.py
from locationDogmaItem import LocationDogmaItem
import util
import inventorycommon.const as invconst

class ControlTowerDogmaItem(LocationDogmaItem):

    def OnItemLoaded(self):
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, 0)
        super(ControlTowerDogmaItem, self).OnItemLoaded()

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.itemID == self.itemID:
            return True
        if dogmaItem.categoryID == invconst.categoryStarbase and dogmaItem.groupID != invconst.groupControlTower:
            return True
        return False

    def GetEnvironmentInfo(self):
        return util.KeyVal(itemID=self.itemID, shipID=self.itemID, charID=None, otherID=None, targetID=None, effectID=None)

    def GetShip(self):
        return self.itemID
