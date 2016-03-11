#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\baseDogmaItem.py
from slimDogmaItem import SlimDogmaItem
from dogma import dogmaLogging as log
import sys
import inventorycommon.const as invconst
import dogma.const as dgmconst
from ccpProfile import TimedFunction
from utillib import KeyVal
from slimDogmaItem import RESISTANCEMATRIX

class BaseDogmaItem(SlimDogmaItem):

    @TimedFunction('BaseDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(BaseDogmaItem, self).__init__(dogmaLocation, item, clientIDFunc)
        self.flagID = None
        self.isDirty = False
        self.fittingFlags = set()
        self.cfg = eveCfg

    @TimedFunction('BaseDogmaItem::Load')
    def Load(self, item, instanceRow):
        categoryID = item.categoryID
        typeID = item.typeID
        groupID = item.groupID
        ownerID = item.ownerID
        flag = item.flagID
        if ownerID:
            ownerOb = self.cfg.eveowners.Get(ownerID)
            if ownerOb.typeID == invconst.typeCorporation or ownerOb.IsNPC() or ownerOb.IsSystem():
                ownerID = None
        self.flagID = None
        attrs = self.attributes
        for attrID, value in self.dogmaLocation.GetAttributesForType(typeID).iteritems():
            attrs[attrID].SetBaseValue(value)

        attributesByIdx = self.dogmaLocation.GetAttributesByIndex()
        for attributeIdx, attributeID in attributesByIdx.iteritems():
            value = instanceRow[attributeIdx]
            if value != 0:
                if type(value) is bool:
                    value = int(value)
                attrs[attributeID].SetBaseValue(value)

    def PostLoadAction(self):
        pass

    def GetLocationInfo(self):
        return (self.invItem.ownerID, self.invItem.locationID, self.flagID)

    def GetItemInfo(self):
        ownerID, locationID, flagID = self.GetLocationInfo()
        return (self.invItem.typeID,
         self.invItem.groupID,
         self.invItem.categoryID,
         ownerID,
         locationID,
         flagID)

    def GetPilot(self):
        return self.invItem.ownerID

    def GetShip(self):
        pilotID = self.GetPilot()
        return self.dogmaLocation.shipsByPilotID.get(pilotID, None)

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        self.flagID = flagID

    def UnsetLocation(self, locationDogmaItem):
        pass

    def MarkDirty(self):
        self.isDirty = True

    def UnmarkDirty(self):
        self.isDirty = False

    def RegisterEffect(self, effectID, effectStart, duration, environment, repeat):
        self.activeEffects[effectID] = [effectStart,
         duration,
         environment,
         repeat]

    def UnregisterEffect(self, effectID, environment):
        del self.activeEffects[effectID]
        if self.itemID in self.dogmaLocation.activeDungeonEffectsByItem:
            if effectID in self.dogmaLocation.activeDungeonEffectsByItem[self.itemID]:
                try:
                    self.dogmaLocation.activeDungeonEffectsByItem[self.itemID][effectID].remove(environment.itemID)
                except ValueError:
                    pass

                if len(self.dogmaLocation.activeDungeonEffectsByItem[self.itemID][effectID]) == 0:
                    del self.dogmaLocation.activeDungeonEffectsByItem[self.itemID][effectID]
            if len(self.dogmaLocation.activeDungeonEffectsByItem[self.itemID]) == 0:
                del self.dogmaLocation.activeDungeonEffectsByItem[self.itemID]

    def IsEffectRegistered(self, effectID, environment):
        return effectID in self.activeEffects

    def Unload(self):
        super(BaseDogmaItem, self).Unload()
        self.dogmaLocation.LogInfo('BaseDogmaItem calling FlushEffects')
        stackTraceCount = self.FlushEffects()
        if stackTraceCount:
            log.LogTraceback('FlushEffectsFromItem %s stack traced %s times, this is to provide higher context' % (self.itemID, stackTraceCount))

    def OnItemLoaded(self):
        pass

    def GetEnvironmentInfo(self):
        return KeyVal(itemID=self.itemID, shipID=self.itemID, charID=None, otherID=None, targetID=None, effectID=None)

    def GetPersistables(self):
        return set([self.itemID])

    def IsOnline(self):
        return False

    def IsActive(self):
        return False

    def FlushEffects(self):
        flushAddedToUnloading = False
        unloadingItems = self.dogmaLocation.unloadingItems
        itemID = self.itemID
        if itemID not in unloadingItems:
            unloadingItems.add(itemID)
            flushAddedToUnloading = True
        try:
            stackTraceCount = self._FlushEffects()
        finally:
            if flushAddedToUnloading and itemID in unloadingItems:
                unloadingItems.remove(itemID)

        return stackTraceCount

    def _FlushEffects(self):
        stackTraceCount = 0
        itemID = self.itemID
        dogmaLM = self.dogmaLocation
        for effectID in self.activeEffects.keys():
            if isinstance(effectID, tuple):
                effectID, shipID = effectID
            effect = dogmaLM.dogmaStaticMgr.effects[effectID]
            try:
                if effect.effectCategory == dgmconst.dgmEffDungeon:
                    dogmaLM.StopDungeonEffect(itemID, effectID)
                elif effect.effectCategory == dgmconst.dgmEffSystem:
                    dogmaLM.StopMultiEffect(itemID, effectID)
                else:
                    dogmaLM.StopEffect(effectID, itemID, forced=True)
            except Exception:
                stackTraceCount += 1
                log.LogException()
                sys.exc_clear()

        return stackTraceCount

    def CanFitItem(self, dogmaItem, flagID):
        return False

    def GetResistanceMatrix(self):
        try:
            return self.resistanceMatrix
        except AttributeError:
            self.resistanceMatrix = RESISTANCEMATRIX.copy()
            for attributeID, resAttribs in self.dogmaLocation.dogmaStaticMgr.resistanceAttributesByLayer.iteritems():
                self.resistanceMatrix[attributeID] = [ self.GetValue(resAttributeID) for resAttributeID in resAttribs ]

            return self.resistanceMatrix
