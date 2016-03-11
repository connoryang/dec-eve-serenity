#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\shipFittableDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
import dogma.const as dgmconst
import inventorycommon.const as invconst
from ccpProfile import TimedFunction

class ShipFittableDogmaItem(FittableDogmaItem):

    @TimedFunction('ShipFittableDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(ShipFittableDogmaItem, self).__init__(dogmaLocation, item, eveCfg, clientIDFunc)
        self.lastStopTime = None

    @TimedFunction('ShipFittableDogmaItem::SetLocation')
    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationDogmaItem is None:
            self.dogmaLocation.LogError('SetLocation called with no locationDogmaItem', self.itemID)
            return
        self.flagID = flagID
        oldData = self.GetLocationInfo()
        if self.IsValidFittingCategory(locationDogmaItem.categoryID):
            locationDogmaItem.RegisterFittedItem(self, flagID)
        else:
            self.dogmaLocation.LogError('SetLocation::ShipFittable item fitted to something other than ship')
        return oldData

    @property
    def ownerID(self):
        if self.location is None:
            return
        return self.location.ownerID

    @ownerID.setter
    def ownerID(self, inOwnerID):
        try:
            if self.location is not None:
                if self.location.ownerID != inOwnerID:
                    self.dogmaLocation.LogError('Setting ownerID on a ShipFittableDogmaItem to something that disagrees with its location!', self.location.ownerID, inOwnerID)
        except Exception:
            pass

    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterFittedItem(self)

    def GetShipID(self):
        return self.invItem.locationID

    def SetLastStopTime(self, lastStopTime):
        self.lastStopTime = lastStopTime

    def IsActive(self):
        for effectID in self.activeEffects:
            if effectID == dgmconst.effectOnline:
                continue
            effect = self.dogmaLocation.GetEffect(effectID)
            if effect.effectCategory in (dgmconst.dgmEffActivation, dgmconst.dgmEffTarget):
                return True

        return False

    def IsValidFittingCategory(self, categoryID):
        return categoryID == invconst.categoryShip

    def GetPilot(self):
        if self.location is not None:
            return self.location.GetPilot()

    def SerializeForPropagation(self):
        retVal = super(ShipFittableDogmaItem, self).SerializeForPropagation()
        retVal.lastStopTime = self.lastStopTime
        return retVal

    def UnpackPropagationData(self, propData, charID, shipID):
        super(ShipFittableDogmaItem, self).UnpackPropagationData(propData, charID, shipID)
        self.SetLastStopTime(propData.lastStopTime)
