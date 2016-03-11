#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingSvc.py
from contextlib import contextmanager
import dogma.const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingUtil import GetPowerType
from eve.client.script.ui.shared.fittingGhost.fittingUtilGhost import GetDefaultAndOverheatEffectForType, CheckChargeForLauncher, GetFlagIdToUse
from eve.client.script.ui.shared.fittingGhost.ghostFittingUtil import GhostFittingDataObject, ONLINE, OVERHEATED, ACTIVE, OFFLINE
from dogma.items.chargeDogmaItem import ChargeDogmaItem
from dogma.items.moduleDogmaItem import ModuleDogmaItem
from shipfitting.fittingDogmaLocationUtil import CheckCanFitType
from shipfitting.fittingStuff import DoesModuleTypeIDFit, IsRightSlotForType
import inventorycommon.const as invConst
import service
import blue
import log
allSlots = invConst.subSystemSlotFlags + invConst.rigSlotFlags + invConst.loSlotFlags + invConst.medSlotFlags + invConst.hiSlotFlags
AVAILABLEFLAGS = {dogmaConst.effectLoPower: (invConst.flagLoSlot0, 8),
 dogmaConst.effectMedPower: (invConst.flagMedSlot0, 8),
 dogmaConst.effectHiPower: (invConst.flagHiSlot0, 8),
 dogmaConst.effectRigSlot: (invConst.flagRigSlot0, 3)}

class GhostFittingSvc(service.Service):
    __guid__ = 'svc.ghostFittingSvc'
    __exportedcalls__ = {}
    __startupdependencies__ = []
    __notifyevents__ = []

    def __init__(self):
        service.Service.__init__(self)
        self.effectsByType = {}
        self.activeDrones = set()

    def Run(self, ms = None):
        self.state = service.SERVICE_RUNNING
        self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.fittingDogmaLocation = sm.GetService('clientDogmaIM').GetFittingDogmaLocation()

    def FitDronesToShip(self, shipID, droneTypeID, qty = 1):
        shipDogmaItem = self.fittingDogmaLocation.GetDogmaItem(shipID)
        g = GhostFittingDataObject(shipID, const.flagDroneBay, droneTypeID)
        for i in xrange(qty):
            counter = 0
            while g.GetItemKey() in shipDogmaItem.drones:
                g.SetNumber(counter)
                counter += 1

            itemKey = g.GetItemKey()
            dogmaItem = self.GetLoadedItem(itemKey, item=g)
            dogmaItem.stacksize = 1

        sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def GetLoadedItem(self, itemKey, item = None):
        self.fittingDogmaLocation.LoadItem(itemKey=itemKey, item=item)
        return self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)

    def FitModuleToShipAndChangeState(self, shipID, flagID, moduleTypeID, stacksize = 1, doOnline = True, doActivate = True):
        dogmaItem = self.FitModuleToShip(shipID, flagID, moduleTypeID, stacksize)
        if not dogmaItem:
            return
        itemKey = dogmaItem.itemID
        if doOnline:
            with self.EatCpuPowergridActiveUserErrors():
                self.PerformActionAndSetNewState(ONLINE, itemKey, moduleTypeID)
        if doActivate:
            with self.EatCpuPowergridActiveUserErrors():
                self.PerformActionAndSetNewState(ACTIVE, itemKey, moduleTypeID)
        return dogmaItem

    def FitModuleToShip(self, shipID, flagID, moduleTypeID, stacksize = 1):
        usedFlags = {x.flagID for x in self.fittingDogmaLocation.GetFittedItemsToShip().itervalues()}
        flagID = GetFlagIdToUse(moduleTypeID, flagID, usedFlags)
        canFitModuleInSlot = self.CanFitModuleInSlot(shipID, moduleTypeID, flagID)
        if not canFitModuleInSlot:
            return
        g = GhostFittingDataObject(shipID, flagID, moduleTypeID)
        itemKey = g.GetItemKey()
        dogmaItem = self.GetLoadedItem(itemKey, g)
        return dogmaItem

    def CanFitModuleInSlot(self, shipID, moduleTypeID, flagID):
        errorText = DoesModuleTypeIDFit(self.fittingDogmaLocation, moduleTypeID, flagID)
        if errorText:
            self.LogInfo('Couldn not fit a module to ship, errorText = ' + errorText, shipID, flagID, moduleTypeID)
            return False
        if self.fittingDogmaLocation.GetSlotOther(shipID, flagID):
            self.LogInfo('Couldn not fit a module to ship, something there ', shipID, flagID, moduleTypeID)
            return False
        powerType = GetPowerType(flagID)
        if not IsRightSlotForType(moduleTypeID, powerType):
            self.LogInfo('Couldn not fit a module to ship, not right slot ', shipID, flagID, moduleTypeID)
            return False
        CheckCanFitType(self.fittingDogmaLocation, moduleTypeID, shipID)
        return True

    def UnfitModule(self, itemKey, scatter = True):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            log.LogWarn('cant use ghost fitting to unfit non-simulated ship')
            return
        dogmaItem = self.fittingDogmaLocation.SafeGetDogmaItem(itemKey)
        if dogmaItem:
            with self.EatCpuPowergridActiveUserErrors():
                self.PerformActionAndSetNewState(OFFLINE, dogmaItem.itemID, dogmaItem.typeID)
        self.fittingDogmaLocation.UnfitItemFromShip(itemKey)
        if scatter:
            sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def FitAmmoList(self, ammoInfo):
        for typeID, flagID in ammoInfo:
            self.FitAmmoToLocation(flagID, typeID)

    def FitAmmoToLocation(self, flagID, ammoTypeID):
        shipID = self.fittingDogmaLocation.shipID
        itemKey = (shipID, flagID, ammoTypeID)
        moduleItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
        if not moduleItem:
            return
        doesFit = CheckChargeForLauncher(self.fittingDogmaLocation.dogmaStaticMgr, moduleItem.typeID, ammoTypeID)
        if not doesFit:
            return
        oldAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
        chargeItem = self.GetLoadedItem(itemKey)
        if oldAmmo:
            try:
                self.UnfitModule(oldAmmo.itemID, scatter=False)
            except Exception as e:
                print 'e = ', e

    def GetDefaultAndOverheatEffect(self, typeID):
        if typeID not in self.effectsByType:
            effectsForType = GetDefaultAndOverheatEffectForType(typeID)
            self.effectsByType[typeID] = effectsForType
        return self.effectsByType[typeID]

    def GetShipAttribute(self, shipID, attributeID, simulated = True):
        fittingSvc = sm.GetService('fittingSvc')
        if fittingSvc.IsShipSimulated():
            shipID = self.fittingDogmaLocation.shipID
            value = self.fittingDogmaLocation.GetAttributeValue(shipID, attributeID)
            return value
        else:
            return self.GetActualShipAttribute(shipID, attributeID)

    def GetActualShipAttribute(self, shipID, attributeID):
        self.LogException('In GetActualShipAttribute, should not be here')
        if self.fittingDogmaLocation.shipID == shipID:
            ship = sm.GetService('godma').GetItem(shipID)
            attributeName = self.dogmaLocation.dogmaStaticMgr.attributes[attributeID].attributeName
            return getattr(ship, attributeName)
        else:
            return self.dogmaLocation.GetAttributeValue(shipID, attributeID)

    def GetModuleStatus(self, itemKey, typeID):
        defaultEffect, overloadEffect = self.GetDefaultAndOverheatEffect(typeID)
        currentState = self.GetCurrentState(itemKey, defaultEffect, overloadEffect)
        return currentState

    def ResetModuleStatus(self):
        self.OfflineAllModules()
        self.activeDrones.clear()
        self.fittingDogmaLocation.RemoveFittedModules()

    def PerformActionAndSetNewState(self, newState, itemKey, typeID):
        defaultEffect, overloadEffect = self.GetDefaultAndOverheatEffect(typeID)
        if newState == OVERHEATED and not overloadEffect:
            newState = ACTIVE
        if newState == ACTIVE and not defaultEffect:
            return
        if newState == ONLINE:
            self.fittingDogmaLocation.OnlineModule(itemKey)
        elif newState == ACTIVE:
            self.fittingDogmaLocation.ActivateModule(itemKey, typeID)
        elif newState == OVERHEATED:
            self.fittingDogmaLocation.OverheatModule(itemKey, typeID)
        elif newState == OFFLINE:
            self.fittingDogmaLocation.OfflineSimulatedModule(itemKey, typeID)
        else:
            log.LogWarn('something went wrong!')
            return

    def GetCurrentState(self, itemKey, defaultEffect, overloadEffect):
        dogmaItem = self.fittingDogmaLocation.GetDogmaItem(itemKey)
        if self.IsRigSlot(defaultEffect):
            if defaultEffect.effectID in dogmaItem.activeEffects:
                return ACTIVE
            else:
                return ONLINE
        elif not defaultEffect:
            if dogmaItem.IsOnline():
                return ONLINE
            else:
                return OFFLINE
        else:
            if not dogmaItem.IsOnline():
                return OFFLINE
            if not dogmaItem.IsActive():
                return ONLINE
            if overloadEffect and overloadEffect.effectID in dogmaItem.activeEffects:
                return OVERHEATED
            return ACTIVE

    def IsRigSlot(self, defaultEffect):
        isRigSlot = defaultEffect and defaultEffect.effectID == dogmaConst.effectRigSlot
        return isRigSlot

    def GetNewState(self, currentState, defaultEffect, overloadEffect):
        newState = None
        if currentState == ONLINE:
            if defaultEffect:
                newState = ACTIVE
            else:
                newState = OFFLINE
        elif currentState == ACTIVE:
            if overloadEffect:
                newState = OVERHEATED
            else:
                newState = OFFLINE
        elif currentState == OVERHEATED:
            newState = OFFLINE
        elif currentState == OFFLINE:
            newState = ONLINE
        return newState

    def SwitchBetweenModes(self, itemKey, typeID):
        defaultEffect, overloadEffect = self.GetDefaultAndOverheatEffect(typeID)
        isRigSlot = self.IsRigSlot(defaultEffect)
        if isRigSlot:
            return
        currentState = self.GetCurrentState(itemKey, defaultEffect, overloadEffect)
        newState = self.GetNewState(currentState, defaultEffect, overloadEffect)
        if newState is not None:
            self.PerformActionAndSetNewState(newState, itemKey, typeID)
        else:
            log.LogWarn('newState was None')
        sm.ScatterEvent('OnFittingUpdateStatsNeeded')

    def OnlineAllSlots(self):
        return self.OnlineAllInRack(allSlots)

    def ActivateAllSlots(self):
        return self.ActivateSlotList(allSlots)

    def OnlineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OnlineSlotList(slotList)

    def ActivateAllHighSlots(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.ActivateSlotList(slotList)

    def OverheatAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OverheatSlotList(slotList)

    def OfflineAllInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.OfflineSlotList(slotList)

    def UnfitAllAmmoInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList, unfitModules=False)

    def UnfitAllModulesInRack(self, slotList):
        with self.PerformAndScatterUpdateEvent():
            self.UnfitAllInSlotlist(slotList)

    def UnfitAllInSlotlist(self, slotList, unfitModules = True):
        for flagID in slotList:
            ghostAmmo = self.fittingDogmaLocation.GetChargeFromShipFlag(flagID)
            if ghostAmmo:
                self.UnfitModule(ghostAmmo.itemID)
            if unfitModules:
                ghostModule = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
                if ghostModule:
                    self.PerformActionAndSetNewState(0, ghostModule.itemID, ghostModule.typeID)
                    self.UnfitModule(ghostModule.itemID)

    def OnlineSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.PerformActionOnSlotList(ONLINE, slotList)

    def ActivateSlotList(self, slotList):
        self.OfflineSlotList(slotList)
        self.OnlineSlotList(slotList)
        self.PerformActionOnSlotList(ACTIVE, slotList)

    def OverheatSlotList(self, slotList):
        self.ActivateSlotList(slotList)
        self.PerformActionOnSlotList(OVERHEATED, slotList)

    def OfflineSlotList(self, slotList):
        self.PerformActionOnSlotList(OFFLINE, slotList)

    def OfflineAllModules(self):
        self.OfflineSlotList(invConst.hiSlotFlags)
        self.OfflineSlotList(invConst.medSlotFlags)
        self.OfflineSlotList(invConst.loSlotFlags)

    def PerformActionOnSlotList(self, action, slotList):
        for flagID in slotList:
            ghostItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if ghostItem:
                with self.EatCpuPowergridActiveUserErrors():
                    self.PerformActionAndSetNewState(action, ghostItem.itemID, ghostItem.typeID)

    @contextmanager
    def EatCpuPowergridActiveUserErrors(self):
        try:
            yield
        except UserError as e:
            if e.msg in ('EffectAlreadyActive2', 'NotEnoughCpu', 'NotEnoughPower', 'NoCharges'):
                self.LogInfo('UserError ingored when fitting= ' + e.msg + str(e.args))
            else:
                raise

    @contextmanager
    def PerformAndScatterUpdateEvent(self):
        try:
            yield
        finally:
            sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def SimulateFitting(self, fitting, *args):
        return self.LoadSimulatedFitting(fitting.shipTypeID, fitting.fitData)

    def LoadCurrentShip(self):
        self.ResetModuleStatus()
        clientDL = sm.GetService('clientDogmaIM').GetDogmaLocation()
        ship = clientDL.GetDogmaItem(clientDL.shipID)
        moduleInfoToLoad = []
        chargeInfoToLoad = []
        for module in ship.GetFittedItems().values():
            if isinstance(module, ModuleDogmaItem):
                info = (module.typeID, module.flagID, 1)
                moduleInfoToLoad.append(info)
            elif isinstance(module, ChargeDogmaItem):
                info = (module.typeID, module.flagID)
                chargeInfoToLoad.append(info)
            else:
                continue

        blue.pyos.synchro.Yield()
        self.LoadSimulatedFitting(ship.typeID, moduleInfoToLoad)
        self.FitAmmoList(chargeInfoToLoad)

    def LoadSimulatedFitting(self, shipTypeID, moduleInfo):
        if not sm.GetService('machoNet').GetGlobalConfig().get('enableGhostFitting'):
            log.LogWarn('Trying to load simulated fitting, config not set')
            return
        self.ResetModuleStatus()
        shipDogmaItem = self.LoadShip(shipTypeID)
        shipItemKey = shipDogmaItem.itemID
        sm.GetService('fittingSvc').simulated = True
        sm.ScatterEvent('OnSimulatedShipLoaded', shipItemKey, shipTypeID)
        moduleInfo.sort(key=lambda x: x[1], reverse=True)
        rigsAndModulesInfo = [ m for m in moduleInfo if m[1] in allSlots ]
        for typeID, flagID, stacksize in rigsAndModulesInfo:
            try:
                self.FitModuleToShip(shipItemKey, flagID, typeID, stacksize)
            finally:
                pass

        self.OnlineAllSlots()
        blue.pyos.synchro.Yield()
        self.ActivateAllSlots()
        droneInfo = [ m for m in moduleInfo if m[1] == const.flagDroneBay ]
        for typeID, flagID, stacksize in droneInfo:
            try:
                self.FitDronesToShip(shipItemKey, typeID, stacksize)
            finally:
                pass

        sm.ScatterEvent('OnFittingUpdateStatsNeeded')

    def LoadShip(self, shipTypeID):
        self.ResetModuleStatus()
        if self.fittingDogmaLocation.shipID:
            currentDLShip = self.fittingDogmaLocation.GetDogmaItem(self.fittingDogmaLocation.shipID)
        else:
            currentDLShip = None
        if currentDLShip and currentDLShip.typeID == shipTypeID:
            shipDogmaItem = currentDLShip
        else:
            shipDogmaItem = self.fittingDogmaLocation.LoadMyShip(shipTypeID)
        return shipDogmaItem

    def RegisterDroneAsActive(self, droneID):
        self.activeDrones.add(droneID)

    def UnregisterDroneFromActive(self, droneID):
        if droneID in self.activeDrones:
            self.activeDrones.remove(droneID)

    def IsDroneActive(self, droneID):
        return droneID in self.activeDrones

    def GetActiveDrones(self):
        return self.activeDrones.copy()

    def TryFitAmmoTypeToAll(self, ammoTypeID):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        for flagID in const.hiSlotFlags + const.medSlotFlags + const.loSlotFlags:
            self.FitAmmoToLocation(flagID, ammoTypeID)

        sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def TryFitModuleToOneSlot(self, moduleTypeID):
        fittingSvc = sm.GetService('fittingSvc')
        if not fittingSvc.IsShipSimulated():
            return
        shipID = self.fittingDogmaLocation.shipID
        dogmaItemFitted = None
        for flagID in allSlots:
            oldGhostFittedItem = self.fittingDogmaLocation.GetModuleFromShipFlag(flagID)
            if oldGhostFittedItem and getattr(oldGhostFittedItem, 'isPreviewItem', None):
                self.UnfitModule(oldGhostFittedItem.itemID)
            dogmaItemFitted = self.FitModuleToShipAndChangeState(shipID, flagID, moduleTypeID)
            if dogmaItemFitted:
                break

        sm.ScatterEvent('OnFakeUpdateFittingWindow')
        return dogmaItemFitted
