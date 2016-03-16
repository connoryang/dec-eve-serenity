#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\characterDogmaItem.py
from shipFittableDogmaItem import ShipFittableDogmaItem
from utillib import strx, KeyVal, IsDustCharacter
import weakref
import sys
import log
import dogma.const as dgmconst
import inventorycommon.const as invconst
from eve.common.script.sys.idCheckers import IsStation
from ccpProfile import TimedFunction

class CharacterDogmaItem(ShipFittableDogmaItem):

    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(CharacterDogmaItem, self).__init__(dogmaLocation, item, eveCfg, clientIDFunc)
        self.fittedItems = {}
        self._activeShipID = None

    @property
    def activeShipID(self):
        return self._activeShipID

    @activeShipID.setter
    def activeShipID(self, activeShipID):
        if activeShipID is None and self._activeShipID is not None:
            log.LogTraceback('Active shipID is being set to None post initialization!')
            return
        self._activeShipID = activeShipID

    def GetOwnedItemsToModify(self):
        modItems = []
        for dogmaItem in self.ownedItems:
            if dogmaItem.IsOwnerModifiable():
                modItems.append(dogmaItem)

        return modItems

    @TimedFunction('CharacterDogmaItem::Load')
    def Load(self, item, instanceRow):
        super(CharacterDogmaItem, self).Load(item, instanceRow)
        self.ownerID = self.itemID
        attrs = self.attributes
        char = self.dogmaLocation.GetCharacter(item.itemID, flush=True)
        if IsDustCharacter(item.itemID):
            attrs[dgmconst.attributeIntelligence].SetBaseValue(20)
            attrs[dgmconst.attributeCharisma].SetBaseValue(20)
            attrs[dgmconst.attributePerception].SetBaseValue(20)
            attrs[dgmconst.attributeMemory].SetBaseValue(20)
            attrs[dgmconst.attributeWillpower].SetBaseValue(20)
            return
        attrs[dgmconst.attributeIntelligence].SetBaseValue(char.intelligence)
        attrs[dgmconst.attributeCharisma].SetBaseValue(char.charisma)
        attrs[dgmconst.attributePerception].SetBaseValue(char.perception)
        attrs[dgmconst.attributeMemory].SetBaseValue(char.memory)
        attrs[dgmconst.attributeWillpower].SetBaseValue(char.willpower)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if flagID != invconst.flagPilot:
            raise RuntimeError('CharacterDogmaItem::SetLocation - flag not pilot (%s, %s)' % (locationID, flagID))
        oldData = self.GetLocationInfo()
        oldShipID = self.activeShipID
        self.activeShipID = locationID
        self.flagID = flagID
        self.HandleLocationChange(oldShipID)
        return oldData

    def UnsetLocation(self, locationDogmaItem):
        locationDogmaItem.UnregisterPilot(self)

    def RegisterFittedItem(self, dogmaItem, flagID):
        self.dogmaLocation.moduleListsByShipGroup[self.itemID][dogmaItem.groupID].add(dogmaItem.itemID)
        self.fittedItems[dogmaItem.itemID] = weakref.proxy(dogmaItem)

    def UnregisterFittedItem(self, dogmaItem):
        groupID = dogmaItem.groupID
        itemID = dogmaItem.itemID
        try:
            self.dogmaLocation.moduleListsByShipGroup[self.itemID][groupID].remove(itemID)
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but group wasn't there", strx(dogmaItem))
            sys.exc_clear()
        except IndexError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from mlsg but it wasn't there", strx(dogmaItem))
            sys.exc_clear()

        try:
            del self.fittedItems[dogmaItem.itemID]
        except KeyError:
            self.dogmaLocation.LogError("UnregisterFittedItem::Tried to remove item from fittedItems but it wasn't there", strx(dogmaItem.itemID))

    def Unload(self):
        super(CharacterDogmaItem, self).Unload()
        itemID = self.itemID
        shipID = self.dogmaLocation.shipsByPilotID.get(self.itemID, None)
        if shipID is None:
            self.dogmaLocation.LogError('Character %s unloading without having been put into a ship. State is not consistent!' % self.itemID)
        for itemKey in self.fittedItems.keys():
            self.dogmaLocation.UnloadItem(itemKey)

        if itemID in self.dogmaLocation.shipsByPilotID:
            del self.dogmaLocation.shipsByPilotID[itemID]
        if shipID in self.dogmaLocation.pilotsByShipID:
            del self.dogmaLocation.pilotsByShipID[shipID]
        if self.itemID in self.dogmaLocation.moduleListsByShipGroup:
            del self.dogmaLocation.moduleListsByShipGroup[self.itemID]
        if self.itemID in self.dogmaLocation.scarecrows:
            while self.dogmaLocation.scarecrows[self.itemID].queue > 0:
                self.dogmaLocation.scarecrows[self.itemID].send(True)

    def OnItemLoaded(self):
        self.dogmaLocation.InitBrain(self.itemID, (-1, [], []))
        initShipID = self.dogmaLocation.GetActiveShipID(self.itemID)
        if initShipID:
            self.dogmaLocation.OnCharacterEmbarkation(self.itemID, initShipID)

    def CanFitItem(self, dogmaItem, flagID):
        if flagID == invconst.flagBooster:
            return True
        return False

    def ValidFittingFlag(self, flagID):
        if flagID == invconst.flagBooster:
            return True
        return False

    def GetFittedItems(self):
        return self.fittedItems

    def GetEnvironmentInfo(self):
        return KeyVal(itemID=self.itemID, shipID=self.GetShipID(), charID=self.itemID, otherID=None, targetID=None, effectID=None)

    def GetPersistables(self):
        ret = super(CharacterDogmaItem, self).GetPersistables()
        ret.update(self.fittedItems.keys())
        return ret

    def _FlushEffects(self):
        with self.dogmaLocation.ignoredOwnerEvents.Event(self.itemID):
            stackTraceCount = 0
            for fittedItem in self.fittedItems.itervalues():
                stackTraceCount += fittedItem.FlushEffects()

            stackTraceCount += super(CharacterDogmaItem, self)._FlushEffects()
        return stackTraceCount

    def GetPilot(self):
        return self.itemID

    def GetShipID(self):
        locationID = self.invItem.locationID
        if locationID > invconst.minPlayerItem:
            return self.dogmaLocation.shipsByPilotID[self.itemID]

    def HandleLocationChange(self, oldShipID):
        newShipID = self.activeShipID
        shipByPilotID = self.dogmaLocation.shipsByPilotID.get(self.itemID, None)
        if self.dogmaLocation.locationGroup == invconst.groupStation:
            oldShipID = shipByPilotID
        if newShipID == oldShipID:
            self.dogmaLocation.LogInfo('%s: HandleLocationChange does not need to do anything for character %s who is already in location %s' % (self.dogmaLocation.locationID, self.itemID, oldShipID))
            return
        if shipByPilotID and oldShipID != shipByPilotID and oldShipID is not None:
            log.LogTraceback('%s: HandleLocationChange expected to find character %s in ship %s but found him in ship %s' % (self.dogmaLocation.locationID,
             self.itemID,
             oldShipID,
             shipByPilotID))
        self.dogmaLocation.LogInfo('%s: HandleLocationChange is changing location for character %s from %s to %s' % (self.dogmaLocation.locationID,
         self.itemID,
         oldShipID,
         newShipID))
        oldShipItem = self.dogmaLocation.dogmaItems.get(oldShipID, None)
        try:
            if oldShipItem:
                oldShipItem.HandlePilotChange(None)
                self._UnregisterAsOwnerForShipItems(oldShipItem)
            if oldShipID in self.dogmaLocation.pilotsByShipID:
                del self.dogmaLocation.pilotsByShipID[oldShipID]
            self.dogmaLocation.shipsByPilotID[self.itemID] = newShipID
            self.dogmaLocation.pilotsByShipID[newShipID] = self.itemID
            super(CharacterDogmaItem, self).HandleLocationChange(newShipID)
            newShipItem = self.dogmaLocation.dogmaItems.get(newShipID, None)
            if newShipItem:
                newShipItem.RegisterPilot(self)
                newShipItem.HandlePilotChange(self.itemID)
                newShipItem.ownerID = self.itemID
                self._RegisterAsOwnerForShipItems(newShipItem)
        except Exception as e:
            self.dogmaLocation.shipsByPilotID[self.itemID] = oldShipID
            self.dogmaLocation.pilotsByShipID[oldShipID] = self.itemID
            if newShipID in self.dogmaLocation.pilotsByShipID:
                del self.dogmaLocation.pilotsByShipID[newShipID]
            raise e

    def _UnregisterAsOwnerForShipItems(self, oldShipItem):
        for item in oldShipItem.subItems:
            item.owner = None
            try:
                self.ownedItems.remove(item)
            except KeyError:
                self.dogmaLocation.LogError("item should have been registered as owned but wasn't", self.itemID, item.itemID, oldShipItem.itemID)

    def _RegisterAsOwnerForShipItems(self, newShipItem):
        for item in newShipItem.subItems:
            item.owner = weakref.proxy(self)
            self.ownedItems.add(item)


class GhostCharacterDogmaItem(CharacterDogmaItem):
    __guid__ = 'GhostCharacterDogmaItem'
