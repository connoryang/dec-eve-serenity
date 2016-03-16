#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\droneDogmaItem.py
import weakref
from inventorycommon import const as invconst
from baseDogmaItem import BaseDogmaItem
from utillib import KeyVal
from eve.common.script.sys.idCheckers import IsSolarSystem
from ccpProfile import TimedFunction

class DroneDogmaItem(BaseDogmaItem):

    def GetShipItem(self):
        shipID = self.dogmaLocation.shipsByPilotID.get(self.ownerID, None)
        if not shipID:
            return
        else:
            return self.dogmaLocation.dogmaItems.get(shipID, None)

    def GetEnvironmentInfo(self):
        return KeyVal(itemID=self.itemID, shipID=self.itemID, charID=self.invItem.ownerID, otherID=None, targetID=None, effectID=None)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        oldOwnerID, oldLocationID, oldFlagID = self.GetLocationInfo()
        self.flagID = flagID
        locationDogmaItem.RegisterDrone(self)
        self.HandleLocationChange(oldLocationID)

    def UnsetLocation(self, locationDogmaItem):
        self.flagID = None
        locationDogmaItem.UnregisterDrone(self.itemID)

    @TimedFunction('DroneDogmaItem::HandleLocationChange')
    def HandleLocationChange(self, oldLocationID):
        self.dogmaLocation.LogInfo('Handle location change from %s to %s, flagID is %s' % (oldLocationID, self.locationID, self.flagID))
        if oldLocationID == self.locationID and self.flagID != invconst.flagDroneBay:
            return
        shipItem = self.GetShipItem()
        if shipItem:
            if self.locationID == self.dogmaLocation.locationID:
                shipItem.subItems.remove(self)
            elif self.locationID == shipItem.itemID:
                shipItem.subItems.add(self)
        self.dogmaLocation.broker.LogInfo('DroneDogmaItem %s handling locationChange from %s to new location %s' % (self.itemID, oldLocationID, self.locationID))
        self.__RemoveAndRestoreDroneOwnerModifiers(oldLocationID)
        super(BaseDogmaItem, self).HandleLocationChange(oldLocationID)

    @TimedFunction('DroneDogmaItem::__RemoveAndRestoreDroneOwnerModifiers')
    def __RemoveAndRestoreDroneOwnerModifiers(self, oldLocationID):
        if self.IsOwnerModifiable(oldLocationID) and not self.IsOwnerModifiable():
            self.RemoveDroneOwnerModifiers()
        elif self.IsOwnerModifiable():
            self.__AddDroneOwnerModifiers()

    def RemoveDroneOwnerModifiers(self, ownerID = None):
        if not ownerID:
            ownerID = self.ownerID
        owner = self.dogmaLocation.dogmaItems.get(ownerID, None)
        if not owner:
            self.dogmaLocation.broker.LogWarn('__RemoveDroneOwnerModifiers::DroneDogmaItem %s could not find its owner?')
            return
        for skillID in self.reqSkills:
            ownerMods = owner.ownerReqSkillMods.get(skillID, {})
            self.dogmaLocation.broker.LogInfo('__RemoveDroneOwnerModifiers is removing modifiers %s from DroneDogmaItem %s owned by %s' % (ownerMods, self.itemID, ownerID))
            for attribID, modSet in ownerMods.iteritems():
                if attribID in self.attributes:
                    toAttrib = self.attributes[attribID]
                    for operation, fromAttrib in modSet:
                        fromAttrib.RemoveOutgoingModifier(operation, toAttrib)
                        toAttrib.RemoveIncomingModifier(operation, fromAttrib)

    def __AddDroneOwnerModifiers(self, ownerID = None):
        if not ownerID:
            ownerID = self.ownerID
        owner = self.dogmaLocation.dogmaItems.get(ownerID, None)
        if not owner:
            self.dogmaLocation.broker.LogWarn('__AddDroneOwnerModifiers::DroneDogmaItem %s could not find its owner?')
            return
        for skillID in self.reqSkills:
            ownerMods = owner.ownerReqSkillMods.get(skillID, {})
            self.dogmaLocation.broker.LogInfo('__AddDroneOwnerModifiers is adding modifiers %s from DroneDogmaItem %s owned by %s' % (ownerMods, self.itemID, ownerID))
            for attribID, modSet in ownerMods.iteritems():
                if attribID in self.attributes:
                    toAttrib = self.attributes[attribID]
                    self._ApplyModsToAttrib(modSet, toAttrib, callOnAttributeChanged=True, debugContext='__AddDroneOwnerModifiers')

    def IsOwnerModifiable(self, locationID = None):
        if not locationID:
            locationID = self.locationID
        pilotID = self.ownerID
        if not pilotID:
            return False
        pilotShip = self.GetShipItem()
        if not pilotShip:
            return False
        if not IsSolarSystem(locationID) and not boot.role == 'client':
            return False
        if self.itemID not in pilotShip.GetDrones():
            return False
        return True

    def ReconnectWithOwner(self, ownerID, shipID):
        self.RemoveDroneOwnerModifiers(ownerID)
        self.dogmaLocation.AddDroneToLocation(shipID, self.itemID)
        self.__AddDroneOwnerModifiers()
