#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\shipDogmaItem.py
import weakref
from collections import defaultdict
from itertools import izip
from utillib import KeyVal
from locationDogmaItem import LocationDogmaItem
import inventorycommon.const as invconst
from inventorycommon.util import IsShipFittingFlag
import dogma.const as dgmconst
import blue
from dogma.attributes import CalculateHeat
from ccpProfile import TimedFunction

class ShipDogmaItem(LocationDogmaItem):

    @TimedFunction('ShipDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(ShipDogmaItem, self).__init__(dogmaLocation, item, eveCfg, clientIDFunc)
        self.flagID = item.flagID
        self.drones = {}
        self.overloadedModules = set()
        self.damageByLayerByType = defaultdict(lambda : defaultdict(float))

    def AddOverloadedModule(self, module):
        self.overloadedModules.add(module)

    def RemoveOverloadedModule(self, module):
        self.overloadedModules.remove(module)

    @TimedFunction('ShipDogmaItem::Load')
    def Load(self, item, instanceRow):
        super(ShipDogmaItem, self).Load(item, instanceRow)
        self.isDirty = True
        self.flagID = item.flagID

    def Unload(self):
        super(ShipDogmaItem, self).Unload()
        for droneID in self.GetDronesInBay():
            self.dogmaLocation.UnloadItem(droneID)

        for droneID, drone in self.GetDronesInSpace().iteritems():
            for attrib in drone.attributes.itervalues():
                attrib.RemoveAllModifiers()
                attrib.MarkDirty()

            self.UnregisterDrone(droneID)

        self.drones = {}

    def PostLoadAction(self):
        self.dogmaLocation.CheckShipOnlineModules(self.itemID)

    def OnItemLoaded(self):
        self.dogmaLocation.LoadPilot(self.itemID)
        self.dogmaLocation.FitItemToLocation(self.itemID, self.itemID, self.flagID)
        super(ShipDogmaItem, self).OnItemLoaded()

    def CanFitItem(self, dogmaItem, flagID):
        if self.ValidFittingFlag(flagID):
            return True
        if dogmaItem.itemID == self.itemID:
            return True
        if flagID == invconst.flagPilot:
            return True
        return False

    def ValidFittingFlag(self, flagID):
        return IsShipFittingFlag(flagID) or flagID == invconst.flagDroneBay

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if locationID != self.itemID:
            raise RuntimeError('ShipDogmaItem.SetLocation::locationID is not ship (%s, %s)' % (locationID, self.itemID))
        self.fittedItems[locationID] = weakref.proxy(self)
        self.flagID = flagID

    def SetDrones(self, drones):
        self.drones = drones

    def GetEnvironmentInfo(self):
        return KeyVal(itemID=self.itemID, shipID=self.itemID, charID=self.GetPilot(), otherID=None, targetID=None, effectID=None)

    def GetPersistables(self):
        ret = super(ShipDogmaItem, self).GetPersistables()
        ret.update(self.drones)
        return ret

    def RegisterDrone(self, drone):
        self.drones[drone.itemID] = drone

    def RegisterPilot(self, pilotDogmaItem):
        pilotID = pilotDogmaItem.itemID
        self.fittedItems[pilotID] = weakref.proxy(pilotDogmaItem)

    def UnregisterPilot(self, pilotDogmaItem):
        try:
            del self.fittedItems[pilotDogmaItem.itemID]
        except KeyError:
            self.dogmaLocation.LogError("ShipDogmaItem::Unregistering a pilot that isn't fitted", pilotDogmaItem.itemID)

    def UnregisterDrone(self, droneID):
        if droneID in self.drones:
            del self.drones[droneID]

    def _FlushEffects(self):
        ownerID = self.dogmaLocation.pilotsByShipID.get(self.itemID, None)
        with self.dogmaLocation.ignoredOwnerEvents.Event(ownerID):
            stackTraceCount = super(ShipDogmaItem, self)._FlushEffects()
        return stackTraceCount

    def GetPilot(self):
        return self.dogmaLocation.pilotsByShipID.get(self.itemID, None)

    def RegisterDamage(self, damageByLayer):
        damageAttribs = self.dogmaLocation.dogmaStaticMgr.damageAttributes
        for attributeID, damages in damageByLayer:
            for damageAttributeID, damage in izip(damageAttribs, damages):
                self.damageByLayerByType[attributeID][damageAttributeID] += damage

    def GetHeatStates(self):
        heatStates = {}
        for heatID in (dgmconst.attributeHeatHi, dgmconst.attributeHeatMed, dgmconst.attributeHeatLow):
            heatStates[heatID] = self.attributes[heatID].GetHeatMessage()

        return heatStates

    def GetHeatValues(self):
        heatVals = {}
        for heatID, heatState in self.GetHeatStates().iteritems():
            currentHeat, maxHeat, incomingHeat, hgm, heatDissipationRate, lastCalc = heatState
            if maxHeat == 0 or currentHeat == 0 and incomingHeat == 0:
                heatVals[heatID] = 0.0
                continue
            currentTime = blue.os.GetSimTime()
            timeDiff = (currentTime - lastCalc) / float(const.dgmTauConstant)
            currentHeat = CalculateHeat(currentHeat, timeDiff, incomingHeat, heatDissipationRate, hgm, maxHeat)
            heatVals[heatID] = currentHeat / maxHeat

        return heatVals

    def GetDrones(self):
        return self.drones.copy()

    def GetDronesInBay(self):
        drones = {}
        for droneID, drone in self.drones.iteritems():
            if drone.locationID == self.itemID:
                drones[droneID] = drone

        return drones

    def GetDronesInSpace(self):
        drones = {}
        for droneID, drone in self.drones.iteritems():
            if drone.locationID == self.locationID:
                drones[droneID] = drone

        return drones


class GhostShipDogmaItem(ShipDogmaItem):
    __guid__ = 'GhostShipDogmaItem'
