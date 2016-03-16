#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingDogmaLocation.py
import weakref
from dogma.effects.environment import Environment
from eve.client.script.ui.shared.fitting.fittingUtil import GetSensorStrengthAttribute
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import GhostFittingDataObject, GhostFittingDogmaItem
from eve.common.script.dogma.baseDogmaLocation import BaseDogmaLocation
from dogma.items.characterFittedDogmaItem import GhostCharacterFittedDogmaItem
from dogma.items.dblessDogmaItem import DBLessDogmaItem
from dogma.items.droneDogmaItem import DroneDogmaItem
from dogma.items.moduleDogmaItem import GhostModuleDogmaItem
from dogma.items.shipDogmaItem import GhostShipDogmaItem
from shipfitting.fittingDogmaLocationUtil import GetFittingItemDragData, GetOptimalDroneDamage, GetTurretAndMissileDps, CapacitorSimulator
import uthread
import log
import blue
from utillib import KeyVal

class FittingDogmaLocation(BaseDogmaLocation):

    def __init__(self, broker):
        BaseDogmaLocation.__init__(self, broker)
        self.godma = sm.GetService('godma')
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.effectCompiler = sm.GetService('ghostFittingEffectCompiler')
        self.instanceFlagQuantityCache = {}
        self.shipID = None
        self.LoadItem(session.charid)

    def LoadMyShip(self, typeID):
        s = GhostFittingDataObject(None, 0, typeID)
        itemKey = s.GetItemKey()
        self.LoadItem(itemKey, item=s)
        self.pilotsByShipID[itemKey] = session.charid
        shipDogmaItem = self.GetDogmaItem(itemKey)
        charDogmaItem = self.GetDogmaItem(session.charid)
        shipDogmaItem.RegisterPilot(charDogmaItem)
        oldShipID = self.shipID
        self.shipID = itemKey
        charDogmaItem.SetLocation(self.shipID, shipDogmaItem, const.flagPilot)
        self.MakeShipActive(self.shipID, oldShipID)
        return shipDogmaItem

    def FitItemToLocation(self, locationID, itemID, flagID):
        if locationID not in (self.shipID, session.charid):
            return
        self.LogInfo('FitItemtoLocation', locationID, itemID, flagID)
        wasItemLoaded = itemID in self.dogmaItems
        log.LogNotice('FitItemToLocation, locationID=%s' % locationID)
        if locationID not in self.dogmaItems:
            self.LoadItem(locationID)
            if not wasItemLoaded:
                self.LogInfo('Neither location not item loaded, returning early', locationID, itemID)
                return
        if itemID not in self.dogmaItems:
            self.LoadItem(itemID)
            return
        locationDogmaItem = self.SafeGetDogmaItem(locationID)
        if locationDogmaItem is None:
            self.LogInfo('FitItemToLocation::Fitted to None item', itemID, locationID, flagID)
            return
        dogmaItem = self.GetDogmaItem(itemID)
        log.LogNotice('FitItemToLocation, dogmaItem=%s' % dogmaItem)
        dogmaItem.SetLocation(locationID, locationDogmaItem, flagID)
        startedEffects = self.StartPassiveEffects(itemID, dogmaItem.typeID)
        sm.ScatterEvent('OnFittingUpdateStatsNeeded')

    def UnfitItemFromShip(self, itemID):
        self.UnfitItemFromLocation(self.shipID, itemID)
        self.UnloadItem(itemID)

    def GetQuantityFromCache(self, locationID, flagID):
        return 1

    def GetInstance(self, item):
        instanceRow = [item.itemID]
        for attributeID in self.GetAttributesByIndex().itervalues():
            v = getattr(item, self.dogmaStaticMgr.attributes[attributeID].attributeName, 0)
            instanceRow.append(v)

        return instanceRow

    def OnlineModule(self, itemKey):
        self.ChangeModuleStatus(itemKey, const.effectOnline)

    def ActivateModule(self, itemKey, moduleTypeID):
        defaultEffect, overloadEffect = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        defaultEffectID = defaultEffect.effectID
        self.ChangeModuleStatus(itemKey, defaultEffectID)

    def OverheatModule(self, itemKey, moduleTypeID):
        defaultEffect, overloadEffect = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if overloadEffect:
            self.ChangeModuleStatus(itemKey, overloadEffect.effectID)

    def OfflineSimulatedModule(self, itemKey, moduleTypeID):
        self.OfflineModule(itemKey)
        defaultEffect, overloadEffect = sm.GetService('ghostFittingSvc').GetDefaultAndOverheatEffect(moduleTypeID)
        if defaultEffect:
            self.StopEffect(defaultEffect.effectID, itemKey)
        if overloadEffect:
            self.StopEffect(overloadEffect.effectID, itemKey)

    def GetItem(self, itemID):
        if itemID != session.charid:
            return self.dogmaItems.get(itemID)
        if isinstance(itemID, GhostFittingDataObject):
            item = GhostFittingDogmaItem(weakref.proxy(self), ghostFittingItem=itemID, ownerID=session.charid)
        else:
            item = self.godma.GetItem(itemID)
        return item

    def GetCharacter(self, itemID, flush = False):
        return self.GetItem(itemID)

    def ShouldStartChanceBasedEffect(self, *args, **kwargs):
        return False

    def StartSystemEffect(self):
        pass

    def ChangeModuleStatus(self, itemKey, effectID = None):
        dogmaItem = self.GetDogmaItem(itemKey)
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = Environment(itemID=envInfo.itemID, charID=envInfo.charID, shipID=self.shipID, targetID=envInfo.targetID, otherID=envInfo.otherID, effectID=effectID, dogmaLM=weakref.proxy(self), expressionID=None)
        self.StartEffect(effectID, itemKey, env, checksOnly=None)

    def CheckSkillRequirementsForType(self, typeID, *args):
        missingSkills = self._GetMissingSkills(typeID)
        return missingSkills

    def _GetMissingSkills(self, typeID):
        missingSkills = {}
        for requiredSkillTypeID, requiredSkillLevel in self.dogmaStaticMgr.GetRequiredSkills(typeID).iteritems():
            requiredSkill = self.dogmaItems.get('0_%s' % requiredSkillTypeID, None)
            if requiredSkill is None or self.GetAttributeValue(requiredSkill.itemID, const.attributeSkillLevel) < requiredSkillLevel:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel

        return missingSkills

    def SetQuantity(self, itemKey, quantity):
        shipID, flagID, typeID = itemKey
        if self.IsItemLoaded(shipID):
            return self.SetAttributeValue(itemKey, const.attributeQuantity, quantity)

    def GetTurretAndMissileDps(self, shipID):
        turretDps, missileDps = GetTurretAndMissileDps(shipID, self, self.dogmaStaticMgr.TypeHasEffect)
        return (turretDps, missileDps)

    def GetOptimalDroneDamage(self, shipID, activeDrones):
        return GetOptimalDroneDamage(shipID, self, activeDrones)

    def IsModuleIncludedInCalculation(self, module):
        dogmaItem = self.GetDogmaItem(module.itemID)
        return dogmaItem.IsActive()

    def LoadItemsInLocation(self, itemID):
        if itemID == session.charid:
            char = self.godma.GetItem(itemID)
            self.LoadSkills(char)
            self.LoadImplants(char)
            self.LoadBoosters(char)

    def GetDragData(self, itemID):
        return GetFittingItemDragData(itemID, self)

    def GetClassForItem(self, item):
        if item.categoryID == const.categoryShip:
            return GhostShipDogmaItem
        if item.categoryID in (const.categoryModule, const.categorySubSystem):
            return GhostModuleDogmaItem
        return BaseDogmaLocation.GetClassForItem(self, item)

    def LoadSkills(self, charItem):
        for item in charItem.skills.itervalues():
            g = GhostFittingDataObject(session.charid, 0, item.typeID)
            g.skillPoints = item.skillPoints
            self.LoadItem(g.GetItemKey(), item=g)

    def UnloadSkills(self):
        charItem = self.godma.GetItem(session.charid)
        for item in charItem.skills.itervalues():
            self.UnloadItem(item.itemID)

    def LoadImplants(self, charItem):
        for item in charItem.implants:
            g = GhostFittingDataObject(session.charid, 0, item.typeID)
            self.LoadItem(g.GetItemKey(), item=g)

    def LoadBoosters(self, charItem):
        for item in charItem.boosters:
            g = GhostFittingDataObject(session.charid, 0, item.typeID)
            self.LoadItem(g.GetItemKey(), item=g)

    def GetShipItem(self):
        return self.SafeGetDogmaItem(self.shipID)

    def GetFittedItemsToShip(self):
        shipItem = self.GetShipItem()
        if shipItem:
            return shipItem.GetFittedItems()
        else:
            return {}

    def GetModuleFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=False)

    def GetChargeFromShipFlag(self, flagID):
        return self.GetItemFromShipFlag(flagID, getCharge=True)

    def GetItemFromShipFlag(self, flagID, getCharge):
        fittedItems = self.GetFittedItemsToShip()
        for eachItem in fittedItems.itervalues():
            if eachItem.flagID != flagID:
                continue
            if getCharge and self.IsCharge(eachItem) or not getCharge and not self.IsCharge(eachItem):
                return eachItem

    def IsCharge(self, fittedItem):
        if isinstance(fittedItem.itemID, tuple):
            return True
        if fittedItem.categoryID == const.categoryCharge:
            return True
        return False

    def GetChargeNonDB(self, shipID, flagID):
        for itemID, fittedItem in self.GetFittedItemsToShip().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem

    def GetSensorStrengthAttribute(self, shipID):
        return GetSensorStrengthAttribute(self, shipID)

    def MakeShipActive(self, shipID, oldShipID):
        uthread.pool('MakeShipActive', self._MakeShipActive, shipID, oldShipID)

    def _MakeShipActive(self, shipID, oldShipID):
        self.LoadItem(session.charid)
        uthread.Lock(self, 'makeShipActive')
        try:
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.SleepSim(250)

            if shipID is None:
                log.LogTraceback('Unexpectedly got shipID = None')
                return
            shipDogmaItem = self.GetDogmaItem(shipID)
            self.StartPassiveEffects(shipID, shipDogmaItem.typeID)
            charItem = self.GetDogmaItem(session.charid)
            charItems = charItem.GetFittedItems()
            self.scatterAttributeChanges = False
            try:
                if oldShipID is not None:
                    self.UnfitItemFromLocation(oldShipID, session.charid)
                for skill in charItems.itervalues():
                    for effectID in skill.activeEffects.keys():
                        self.StopEffect(effectID, skill.itemID)

                if shipID is not None:
                    for skill in charItems.itervalues():
                        self.StartPassiveEffects(skill.itemID, skill.typeID)

                    if shipID != oldShipID:
                        self.UnloadItem(oldShipID)
            finally:
                self.scatterAttributeChanges = True

        finally:
            uthread.UnLock(self, 'makeShipActive')

    def GetCapacity(self, shipID, attributeID, flagID):
        capacity = self.GetAttributeValue(shipID, attributeID)
        used = 0
        shipDogmaItem = self.GetDogmaItem(shipID)
        for droneID in shipDogmaItem.drones:
            used += self.GetAttributeValue(droneID, const.attributeVolume)

        return KeyVal(capacity=capacity, used=used)

    def CapacitorSimulator(self, shipID):
        return CapacitorSimulator(self, shipID)

    def RemoveFittedModules(self):
        try:
            for itemKey, item in self.dogmaItems.items():
                if isinstance(item, (GhostModuleDogmaItem, DBLessDogmaItem, DroneDogmaItem)):
                    self.UnfitItemFromLocation(self.shipID, itemKey)
                    self.UnloadItem(itemKey)

            self.moduleListsByShipGroup.pop(self.shipID, None)
        finally:
            self.scatterAttributeChanges = True

    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        value = BaseDogmaLocation.OnAttributeChanged(self, attributeID, itemKey, value=value, oldValue=oldValue)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.shipID, itemKey, attributeID, value)

    def GetQuantity(self, itemID):
        return 1

    def GetAccurateAttributeValue(self, itemID, attributeID, *args):
        return self.GetAttributeValue(itemID, attributeID)

    def DecreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2):
        pass

    def IncreaseItemAttribute(self, itemKey, attributeID, itemKey2, attributeID2):
        value = self.GetAttributeValue(itemKey2, attributeID2)
        new, old = self.IncreaseItemAttributeEx(itemKey, attributeID, value, alsoReturnOldValue=True)
        if attributeID in (const.attributeShieldCharge, const.attributeCapacitorCharge) and new > old:
            actingItem = self.dogmaItems.get(itemKey2)
            if actingItem is None:
                self.broker.LogWarn('No actingItem in IncreaseItemAttribute', itemKey, attributeID, itemKey2, attributeID2)
        return new

    def IncreaseItemAttributeEx(self, itemKey, attributeID, value, silently = 0, alsoReturnOldValue = False):
        dogmaItem = self.GetDogmaItem(itemKey)
        if not dogmaItem.CanAttributeBeModified():
            if alsoReturnOldValue:
                return (0, 0)
            return 0
        if attributeID not in dogmaItem.attributes:
            itemTypeID = dogmaItem.typeID
            dogmaItem.attributes[attributeID] = self.dogmaStaticMgr.GetTypeAttribute2(itemTypeID, attributeID)
        v = dogmaItem.attributes[attributeID]
        ma = self.dogmaStaticMgr.attributes[attributeID].maxAttributeID
        ret = v + value
        if ma:
            ret = min(self.GetAttributeValue(itemKey, ma), ret)
        dogmaItem.attributes[attributeID] = ret
        if alsoReturnOldValue:
            return (ret, v)
        return ret

    def IsInWeaponBank(self, *args):
        return False

    def WaitForShip(self, *args):
        pass
