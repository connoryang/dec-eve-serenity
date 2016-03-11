#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\dogma\clientDogmaLocation.py
from dogma.dogmaLogging import *
from dogma.dogmaWrappers import WrappedMethod
import sys
import weakref
from inventorycommon.util import IsShipFittingFlag
import util
import math
import uix
import log
import moniker
import blue
import uiutil
import uthread
import itertools
import localization
import telemetry
import evetypes
from collections import defaultdict
from eve.common.script.dogma.baseDogmaLocation import BaseDogmaLocation
from eve.common.script.dogma.effect import ApplyBrainEffect, BrainEffect
import carbonui.const as uiconst
from dogma.attributes.format import GetFormatAndValue
from dogma.effects.environment import Environment
GROUPALL_THROTTLE_TIMER = 2 * const.SEC

class DogmaLocation(BaseDogmaLocation):
    __notifyevents__ = ['OnModuleAttributeChanges',
     'OnWeaponBanksChanged',
     'OnWeaponGroupDestroyed',
     'OnServerBrainUpdated',
     'OnHeatAdded',
     'OnHeatRemoved']

    def __init__(self, broker, charBrain = None):
        super(DogmaLocation, self).__init__(broker)
        self.instanceCache = {}
        self.scatterAttributeChanges = True
        self.dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
        self.remoteDogmaLM = None
        self.godma = sm.GetService('godma')
        self.stateMgr = self.godma.GetStateManager()
        self.skillSvc = sm.GetService('skills')
        self.fakeInstanceRow = None
        self.items = {}
        self.nextItemID = 0
        self.effectCompiler = sm.GetService('clientEffectCompiler')
        self.brain = None
        if charBrain:
            self.SetBrainData(session.charid, charBrain)
        self.lastGroupAllRequest = None
        self.lastUngroupAllRequest = None
        self.shipIDBeingDisembarked = None
        self.shipIDBeingEmbarked = None
        self.locationName = 'ClientDogmaLocation'
        sm.RegisterNotify(self)

    def SetBrainData(self, charID, brain):
        brainVersion, charEffects, shipEffects = brain
        self.brain = brain

    def GetBrainData(self, charID):
        return self.brain

    def GetCurrentShipID(self):
        return self.shipsByPilotID.get(session.charid, None)

    def GetActiveShipID(self, characterID):
        return session.shipid

    def CheckApplyBrainEffects(self, shipID):
        return shipID in self.dogmaItems

    def GetMatchingAmmo(self, shipID, itemID):
        dogmaItem = self.dogmaItems[itemID]
        ammoInfoByTypeID = defaultdict(lambda : util.KeyVal(singletons=[], nonSingletons=[]))
        validGroupIDs = self.dogmaStaticMgr.GetValidChargeGroupsForType(dogmaItem.typeID)
        GetTypeAttribute = self.dogmaStaticMgr.GetTypeAttribute
        preferredChargeSize = GetTypeAttribute(dogmaItem.typeID, const.attributeChargeSize)
        for item in self.broker.invCache.GetInventoryFromId(shipID).List(const.flagCargo):
            if validGroupIDs is not None and item.groupID not in validGroupIDs:
                continue
            if preferredChargeSize is not None and GetTypeAttribute(item.typeID, const.attributeChargeSize) != preferredChargeSize:
                continue
            if item.singleton:
                ammoInfoByTypeID[item.typeID].singletons.append(item)
            else:
                ammoInfoByTypeID[item.typeID].nonSingletons.append(item)

        return ammoInfoByTypeID

    def AddToMenuFromAmmoInfo(self, itemID, chargeTypeID, ammoInfo, minimumAmmoNeeded, labels):
        menu = []
        if sum((item.stacksize for item in ammoInfo.singletons)) >= minimumAmmoNeeded:
            text = uiutil.MenuLabel(labels[0], {'typeID': chargeTypeID})
            menu.append((text, self.LoadChargeToModule, (itemID, chargeTypeID, ammoInfo.singletons)))
        noOfNonSingletons = sum((item.stacksize for item in ammoInfo.nonSingletons))
        if noOfNonSingletons >= minimumAmmoNeeded:
            text = uiutil.MenuLabel(labels[1], {'typeID': chargeTypeID,
             'sumqty': noOfNonSingletons})
            menu.append((text, self.LoadChargeToModule, (itemID, chargeTypeID, ammoInfo.nonSingletons)))
        return menu

    def GetAmmoMenu(self, shipID, itemID, existingChargeID, roomForReload):
        usedChargeType = self.godma.GetStateManager().GetAmmoTypeForModule(itemID)
        ammoInfoByTypeID = self.GetMatchingAmmo(shipID, itemID)
        try:
            minimumAmmoNeeded = len(self.GetModulesInBank(shipID, itemID))
        except TypeError:
            minimumAmmoNeeded = 1

        menu = []
        if usedChargeType in ammoInfoByTypeID and roomForReload:
            ammoInfo = ammoInfoByTypeID[usedChargeType]
            menuItems = self.AddToMenuFromAmmoInfo(itemID, usedChargeType, ammoInfo, minimumAmmoNeeded, ('UI/Inflight/ModuleRacks/ReloadUsed', 'UI/Inflight/ModuleRacks/Reload'))
            if menuItems:
                menu.extend(menuItems)
                menu.append((uiutil.MenuLabel('UI/Inflight/ModuleRacks/ReloadAll'), uicore.cmd.CmdReloadAmmo))
        if existingChargeID:
            menu.append((uiutil.MenuLabel('UI/Inflight/ModuleRacks/UnloadToCargo'), self.UnloadChargeToContainer, (shipID,
              existingChargeID,
              (shipID,),
              const.flagCargo)))
        otherChargeMenu = []
        for chargeTypeID in localization.util.Sort(ammoInfoByTypeID.keys(), key=lambda x: evetypes.GetName(x)):
            ammoInfo = ammoInfoByTypeID[chargeTypeID]
            if chargeTypeID == usedChargeType:
                continue
            otherChargeMenu.extend(self.AddToMenuFromAmmoInfo(itemID, chargeTypeID, ammoInfo, minimumAmmoNeeded, ('UI/Inflight/ModuleRacks/AmmoTypeAndStatus', 'UI/Inflight/ModuleRacks/AmmoTypeAndQuantity')))

        menu.extend(otherChargeMenu)
        return menu

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def MakeShipActive(self, shipID, shipState = None):
        uthread.pool('MakeShipActive', self._MakeShipActive, shipID, shipState)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def _MakeShipActive(self, shipID, shipState):
        uthread.Lock(self, 'makeShipActive')
        if shipID is None:
            log.LogTraceback('Unexpectedly got shipID = None')
            return
        if shipID == self.locationID:
            log.LogTraceback('ClientDogmaLocation is attempting to activate itself as a characters shipID!')
            return
        self.shipIDBeingDisembarked = self.GetCurrentShipID()
        self.shipIDBeingEmbarked = shipID
        try:
            if self.GetCurrentShipID() == shipID:
                self.shipIDBeingEmbarked = self.shipIDBeingDisembarked = None
                return
            while not session.IsItSafe():
                self.LogInfo('MakeShipActive - session is mutating. Sleeping for 250ms')
                blue.pyos.synchro.SleepSim(250)

            self.UpdateRemoteDogmaLocation()
            oldShipID = self.GetCurrentShipID()
            if oldShipID and oldShipID in self.dogmaItems:
                self.RemoveBrainEffects(oldShipID, session.charid, 'clientDogmaLocation._MakeShipActive')
            if shipState is not None:
                self.instanceCache, self.instanceFlagQuantityCache, self.wbData, heatStates = shipState
            else:
                try:
                    self.instanceCache, self.instanceFlagQuantityCache, self.wbData, heatStates = self.remoteShipMgr.Board(shipID, session.shipid)
                except Exception:
                    raise

            self.scatterAttributeChanges = False
            try:
                LogNotice('_MakeShipActive: Calling LoadItem on new shipID=', shipID)
                if oldShipID is not None:
                    LogNotice('_MakeShipActive: Unfitting oldShipID=', oldShipID)
                    self.UnfitItemFromLocation(oldShipID, session.charid)
                if shipID is not None:
                    LogNotice('_MakeShipActive: Calling OnCharacterEmbarkation')
                    if not oldShipID:
                        self.LoadItem(session.charid)
                        self.SetWeaponBanks(shipID, self.wbData)
                    else:
                        if oldShipID and oldShipID in self.dogmaItems:
                            LogNotice('_MakeShipActive: Unloading oldShipID=', oldShipID)
                            self.UnloadItem(oldShipID)
                        self.OnCharacterEmbarkation(session.charid, shipID, switching=oldShipID is not None)
                        LogNotice('_MakeShipActive: Calling SetWeaponBanks')
                        self.SetWeaponBanks(shipID, self.wbData)
                        self.LoadItemsInLocation(shipID)
                        sm.ChainEvent('ProcessActiveShipChanged', shipID, oldShipID)
            finally:
                self.scatterAttributeChanges = True

            self.ClearInstanceCache()
        finally:
            self.shipIDBeingDisembarked = None
            self.shipIDBeingEmbarked = None
            uthread.UnLock(self, 'makeShipActive')

        LogNotice('_MakeShipActive: DONE')

    def WaitForShip(self):
        startTime = blue.os.GetWallclockTime()
        while self.IsSwitchingShips() and blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) < 2000:
            blue.pyos.synchro.Sleep(100)

    def IsSwitchingShips(self):
        return self.shipIDBeingDisembarked is not None

    def ClearInstanceCache(self):
        self.instanceCache = {}
        self.instanceFlagQuantityCache = {}
        self.wbData = None

    @telemetry.ZONE_METHOD
    def UpdateRemoteDogmaLocation(self):
        if session.stationid2 is not None:
            self.remoteDogmaLM = moniker.GetStationDogmaLocation()
            self.remoteShipMgr = moniker.GetStationShipAccess()
            self.locationGroup = const.groupStation
            self.locationID = session.stationid2
        else:
            self.remoteDogmaLM = moniker.CharGetDogmaLocation()
            self.remoteShipMgr = moniker.GetShipAccess()
            self.locationGroup = const.groupSolarSystem
            self.locationID = session.solarsystemid

    @telemetry.ZONE_METHOD
    def OnModuleAttributeChanges(self, changes):
        changes.sort(key=lambda change: change[4])
        for change in changes:
            try:
                eventName, ownerID, itemID, attributeID, time, newValue, oldValue, _ = change
                if attributeID == const.attributeQuantity:
                    if isinstance(itemID, tuple) and not self.IsItemLoaded(itemID[0]):
                        self.LogWarn("got an module attribute change and the item wasn't loaded", itemID)
                        continue
                    if newValue == 0:
                        self.SetAttributeValue(itemID, const.attributeQuantity, newValue)
                        self.UnfitItemFromLocation(itemID[0], itemID)
                        self.UnloadItem(itemID)
                    else:
                        if itemID != self.GetSubLocation(itemID[0], itemID[1]):
                            self.FitItemToLocation(itemID[0], itemID, itemID[1])
                        self.dogmaItems[itemID].attributes[attributeID].SetBaseValue(newValue)
                elif attributeID == const.attributeIsOnline:
                    if not self.IsItemLoaded(itemID):
                        continue
                    if newValue == self.GetAttributeValue(itemID, const.attributeIsOnline):
                        continue
                    if newValue == 0:
                        self.StopEffect(const.effectOnline, itemID)
                    else:
                        self.Activate(itemID, const.effectOnline)
                elif self.IsItemLoaded(itemID) and attributeID in self.dogmaStaticMgr.damageStateAttributes:
                    dogmaItem = self.dogmaItems[itemID]
                    dogmaItem.attributes[attributeID].SetBaseValue(newValue)
                    sm.ScatterEvent('OnDamageStateChanged', itemID)
            except Exception as e:
                log.LogException('OnModuleAttributeChanges::Unexpected exception')
                sys.exc_clear()

    @telemetry.ZONE_METHOD
    def FitItemToLocation(self, locationID, itemID, flagID):
        if self._IsLocationIDInvalidForFitting(locationID):
            return
        super(DogmaLocation, self).FitItemToLocation(locationID, itemID, flagID)

    @telemetry.ZONE_METHOD
    def UnfitItemFromLocation(self, locationID, itemID, flushEffects = False):
        super(DogmaLocation, self).UnfitItemFromLocation(locationID, itemID, flushEffects)
        if locationID not in self.checkShipOnlineModulesPending:
            self.checkShipOnlineModulesPending.add(locationID)
            uthread.pool('LocationManager::CheckShipOnlineModules', self.CheckShipOnlineModules, locationID)

    @telemetry.ZONE_METHOD
    def GetChargeNonDB(self, shipID, flagID):
        for itemID, fittedItem in self.dogmaItems[shipID].GetFittedItems().iteritems():
            if isinstance(itemID, tuple):
                continue
            if fittedItem.flagID != flagID:
                continue
            if fittedItem.categoryID == const.categoryCharge:
                return fittedItem

    @telemetry.ZONE_METHOD
    def GetSubSystemInFlag(self, shipID, flagID):
        shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        items = shipInv.List(flagID)
        if len(items) == 0:
            return None
        else:
            return self.dogmaItems[items[0].itemID]

    @telemetry.ZONE_METHOD
    def GetItem(self, itemID):
        session.WaitUntilSafe()
        if itemID == self.GetCurrentShipID() or itemID == self.shipIDBeingEmbarked:
            return self.broker.invCache.GetInventoryFromId(itemID, locationID=session.stationid2).GetItem()
        try:
            return self.items[itemID]
        except KeyError:
            sys.exc_clear()

        return self.godma.GetItem(itemID)

    @telemetry.ZONE_METHOD
    def GetCharacter(self, itemID, flush):
        return self.GetItem(itemID)

    @telemetry.ZONE_METHOD
    def Activate(self, itemID, effectID):
        dogmaItem = self.dogmaItems[itemID]
        envInfo = dogmaItem.GetEnvironmentInfo()
        env = Environment(envInfo.itemID, envInfo.charID, envInfo.shipID, envInfo.targetID, envInfo.otherID, effectID, weakref.proxy(self), None)
        env.dogmaLM = self
        self.StartEffect(effectID, itemID, env)

    @telemetry.ZONE_METHOD
    def PostStopEffectAction(self, effectID, dogmaItem, activationInfo, *args):
        super(DogmaLocation, self).PostStopEffectAction(effectID, dogmaItem, activationInfo, *args)
        if effectID == const.effectOnline:
            shipID = dogmaItem.locationID
            if shipID not in self.checkShipOnlineModulesPending:
                self.checkShipOnlineModulesPending.add(shipID)
                uthread.pool('LocationManager::CheckShipOnlineModules', self.CheckShipOnlineModules, shipID)

    @telemetry.ZONE_METHOD
    def GetInstance(self, item):
        try:
            return self.instanceCache[item.itemID]
        except KeyError:
            sys.exc_clear()

        instanceRow = [item.itemID]
        godmaItem = self.broker.godma.GetItem(item.itemID)
        for attributeID in self.GetAttributesByIndex().itervalues():
            instanceRow.append(getattr(godmaItem, self.dogmaStaticMgr.attributes[attributeID].attributeName, 0))

        return instanceRow

    def GetAccurateAttributeValue(self, itemID, attributeID, *args):
        if session.solarsystemid is None:
            return self.GetAttributeValue(itemID, attributeID)
        else:
            return self.GetGodmaAttributeValue(itemID, attributeID)

    @telemetry.ZONE_METHOD
    def _GetMissingSkills(self, typeID):
        skillSvc = sm.GetService('skills')
        missingSkills = {}
        for requiredSkillTypeID, requiredSkillLevel in self.dogmaStaticMgr.GetRequiredSkills(typeID).iteritems():
            mySkill = skillSvc.GetSkill(requiredSkillTypeID)
            if mySkill is None:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel
            elif mySkill.skillLevel < requiredSkillLevel:
                missingSkills[requiredSkillTypeID] = requiredSkillLevel

        return missingSkills

    @telemetry.ZONE_METHOD
    def CheckSkillRequirementsForType(self, _, typeID, errorMsgName):
        missingSkills = self._GetMissingSkills(typeID)
        if len(missingSkills) > 0:
            nameList = []
            for skillTypeID, requiredSkillLevel in missingSkills.iteritems():
                nameList.append(localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=requiredSkillLevel))

            raise UserError(errorMsgName, {'requiredSkills': localization.formatters.FormatGenericList(nameList),
             'item': typeID,
             'skillCount': len(nameList)})
        return missingSkills

    @telemetry.ZONE_METHOD
    def LoadItemsInLocation(self, itemID):
        if itemID in (session.charid, self.GetCurrentShipID(), self.shipIDBeingEmbarked):
            dogmaItem = self.dogmaItems[itemID]
            self.LogInfo('LoadItemsInLocation %s' % itemID)
            self.UpdateRemoteDogmaLocation()
            itemInv = self.broker.invCache.GetInventoryFromId(itemID, locationID=self.locationID)
            for item in itemInv.List():
                try:
                    if dogmaItem.ValidFittingFlag(item.flagID):
                        self.items[item.itemID] = item
                        self.LoadItem(item.itemID, item=item)
                except Exception:
                    if item.itemID in self.items:
                        del self.items[item.itemID]
                    log.LogException('LoadItemsInLocation %s, %s' % (itemID, evetypes.GetName(item.typeID)))
                    sys.exc_clear()

    def UnloadItem(self, itemKey, item = None):
        super(DogmaLocation, self).UnloadItem(itemKey, item)
        if itemKey in self.items:
            del self.items[itemKey]

    def UnloadItemsInLocation(self, locationID):
        if locationID in (session.charid, self.GetCurrentShipID(), self.shipIDBeingEmbarked):
            self.LogInfo('UnloadItemsInLocation %s' % locationID)
            self.UpdateRemoteDogmaLocation()
            itemInv = self.broker.invCache.GetInventoryFromId(locationID, locationID=self.locationID)
            for item in itemInv.List():
                try:
                    self.UnfitItem(item.itemID)
                    self.UnloadItem(item.itemID, item)
                    if item.itemID in self.items:
                        del self.items[item.itemID]
                except:
                    if item.itemID not in self.items:
                        self.items[item.itemID] = item
                    log.LogException('UnloadItemsInLocation %s, %s' % (locationID, evetypes.GetName(item.typeID)))
                    sys.exc_clear()

    @telemetry.ZONE_METHOD
    def LoadPilot(self, shipID):
        pilotItem = self.GetItem(session.charid)
        if pilotItem:
            self.LoadItem(pilotItem.itemID, item=pilotItem)

    def GetSensorStrengthAttribute(self, shipID):
        maxAttributeID = None
        maxValue = None
        for attributeID in (const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrength,
         const.attributeScanMagnetometricStrength,
         const.attributeScanRadarStrength):
            val = self.GetAttributeValue(shipID, attributeID)
            if val > maxValue:
                maxValue, maxAttributeID = val, attributeID

        return (maxAttributeID, maxValue)

    def UnfitItem(self, itemID):
        if itemID == session.charid:
            self.UnboardShip(session.charid)
        else:
            locationID = self.dogmaItems[itemID].locationID
            self.UnfitItemFromLocation(locationID, itemID)
            self.UnloadItem(itemID)
        if itemID in self.items:
            del self.items[itemID]
        if itemID in self.instanceCache:
            del self.instanceCache[itemID]

    def UnboardShip(self, charID):
        char = self.dogmaItems[charID]
        charItems = char.GetFittedItems()
        for implant in charItems.itervalues():
            for effectID in implant.activeEffects.keys():
                self.StopEffect(effectID, implant.itemID)

        oldShipID = self.GetCurrentShipID()
        self.UnfitItemFromLocation(self.GetCurrentShipID(), charID)

    def FitItem(self, item):
        if self._IsLocationIDInvalidForFitting(item.locationID):
            return
        self.items[item.itemID] = item
        self.FitItemToLocation(item.locationID, item.itemID, item.flagID)

    def OnItemChange(self, item, change):
        wasFitted = item.itemID in self.dogmaItems
        isFitted = self.IsFitted(item)
        if wasFitted and not isFitted:
            if isinstance(item.itemID, tuple):
                pass
            elif item.categoryID == const.categoryDrone:
                self.UnfitItemFromLocation(self.GetCurrentShipID(), item.itemID)
                self.UnloadItem(item.itemID)
            else:
                self.UnfitItem(item.itemID)
        if not wasFitted and isFitted:
            try:
                self.FitItem(item)
            except Exception:
                log.LogException('OnItemChange unexpectedly failed fitting item %s: (%s)' % (item.itemID, change))
                raise

        if wasFitted and isFitted and const.ixFlag in change:
            self.dogmaItems[item.itemID].flagID = item.flagID
        if isFitted and const.ixStackSize in change:
            self.SetAttributeValue(item.itemID, const.attributeQuantity, item.stacksize)
        try:
            dogmaItem = self.dogmaItems[item.itemID]
        except KeyError:
            pass
        else:
            oldLocationID = item.locationID
            oldOwnerID = item.ownerID
            dogmaItem.invItem = item
            if const.ixOwnerID in change:
                dogmaItem.HandleOwnerChange(oldOwnerID)
            if const.ixLocationID in change:
                dogmaItem.HandleLocationChange(oldLocationID)
            self._OnlineModuleIfApplicable(item)

        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaItemChange', item, change)
        self.items[item.itemID] = item

    def _OnlineModuleIfApplicable(self, item):
        if self.dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectOnline):
            try:
                self.OnlineModule(item.itemID)
            except UserError as e:
                if e.msg != 'EffectAlreadyActive2':
                    uthread.pool('FitItem::RaiseUserError', eve.Message, *e.args)
            except Exception:
                log.LogException('Raised during OnlineModule')

    def IsFitted(self, item):
        if self._IsLocationIDInvalidForFitting(item.locationID):
            return False
        if not IsShipFittingFlag(item.flagID) and item.flagID != const.flagDroneBay:
            return False
        if item[const.ixStackSize] <= 0:
            return False
        return True

    def _IsLocationIDInvalidForFitting(self, locationID):
        isLocationIDValidForFitting = locationID not in (self.GetCurrentShipID(), session.charid, self.shipIDBeingEmbarked)
        return isLocationIDValidForFitting

    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        value = super(DogmaLocation, self).OnAttributeChanged(attributeID, itemKey, value=value, oldValue=oldValue)
        if self.scatterAttributeChanges:
            sm.ScatterEvent('OnDogmaAttributeChanged', self.GetCurrentShipID(), itemKey, attributeID, value)

    def GetShip(self):
        return self.dogmaItems[self.GetCurrentShipID()]

    def TryFit(self, item, flagID):
        shipID = util.GetActiveShip()
        shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
        shipInv.Add(item.itemID, item.locationID, qty=1, flag=flagID)

    def GetQuantity(self, itemID):
        if isinstance(itemID, tuple):
            return self.GetAttributeValue(itemID, const.attributeQuantity)
        return self.GetItem(itemID).stacksize

    def GetCapacity(self, shipID, attributeID, flagID):
        ret = self.broker.invCache.GetInventoryFromId(self.GetCurrentShipID(), locationID=session.stationid2).GetCapacity(flagID)
        if const.flagLoSlot0 <= flagID <= const.flagHiSlot7:
            shipDogmaItem = self.dogmaItems[shipID]
            subLocation = shipDogmaItem.subLocations.get(flagID, None)
            if subLocation is None:
                used = ret.used
            else:
                used = self.GetAttributeValue(subLocation, const.attributeQuantity) * evetypes.GetVolume(subLocation[2])
            moduleID = self.GetSlotOther(shipID, flagID)
            if moduleID is None:
                capacity = 0
            else:
                capacity = self.GetAttributeValue(moduleID, const.attributeCapacity)
            return util.KeyVal(capacity=capacity, used=used)
        return ret

    def CapacitorSimulator(self, shipID):
        dogmaItem = self.dogmaItems[shipID]
        capacitorCapacity = self.GetAttributeValue(shipID, const.attributeCapacitorCapacity)
        rechargeTime = self.GetAttributeValue(shipID, const.attributeRechargeRate)
        modules = []
        totalCapNeed = 0
        for moduleID, module in dogmaItem.GetFittedItems().iteritems():
            if not module.IsOnline():
                continue
            try:
                defaultEffectID = self.dogmaStaticMgr.GetDefaultEffect(module.typeID)
            except KeyError:
                defaultEffectID = None
                sys.exc_clear()

            if defaultEffectID is None:
                continue
            defaultEffect = self.dogmaStaticMgr.effects[defaultEffectID]
            durationAttributeID = defaultEffect.durationAttributeID
            dischargeAttributeID = defaultEffect.dischargeAttributeID
            if durationAttributeID is None or dischargeAttributeID is None:
                continue
            duration = self.GetAttributeValue(moduleID, durationAttributeID)
            capNeed = self.GetAttributeValue(moduleID, dischargeAttributeID)
            modules.append([capNeed, long(duration * const.dgmTauConstant), 0])
            totalCapNeed += capNeed / duration

        rechargeRateAverage = capacitorCapacity / rechargeTime
        peakRechargeRate = 2.5 * rechargeRateAverage
        tau = rechargeTime / 5
        TTL = None
        if totalCapNeed > peakRechargeRate:
            TTL = self.RunSimulation(capacitorCapacity, rechargeTime, modules)
            loadBalance = 0
        else:
            c = 2 * capacitorCapacity / tau
            k = totalCapNeed / c
            exponent = (1 - math.sqrt(1 - 4 * k)) / 2
            if exponent == 0:
                loadBalance = 1
            else:
                t = -math.log(exponent) * tau
                loadBalance = (1 - math.exp(-t / tau)) ** 2
        return (peakRechargeRate,
         totalCapNeed,
         loadBalance,
         TTL)

    def RunSimulation(self, capacitorCapacity, rechargeRate, modules):
        capacitor = capacitorCapacity
        tauThingy = float(const.dgmTauConstant) * (rechargeRate / 5.0)
        currentTime = nextTime = 0L
        while capacitor > 0.0 and nextTime < const.DAY:
            capacitor = (1.0 + (math.sqrt(capacitor / capacitorCapacity) - 1.0) * math.exp((currentTime - nextTime) / tauThingy)) ** 2 * capacitorCapacity
            currentTime = nextTime
            nextTime = const.DAY
            for data in modules:
                if data[2] == currentTime:
                    data[2] += data[1]
                    capacitor -= data[0]
                nextTime = min(nextTime, data[2])

        if capacitor > 0.0:
            return const.DAY
        return currentTime

    def OnlineModule(self, moduleID):
        self.Activate(moduleID, const.effectOnline)
        dogmaItem = self.dogmaItems[moduleID]
        try:
            if dogmaItem.ownerID != session.charid:
                log.LogTraceback('OnlineModule character %s is attempting to online a module that he does not own!' % session.charid)
            self.remoteDogmaLM.SetModuleOnline(dogmaItem.locationID, moduleID)
        except UserError as e:
            if e.msg != 'EffectAlreadyActive2':
                self.StopEffect(const.effectOnline, moduleID)
                raise
        except Exception:
            self.StopEffect(const.effectOnline, moduleID)
            raise

    def OfflineModule(self, moduleID):
        dogmaItem = self.dogmaItems[moduleID]
        if dogmaItem.locationID not in (self.shipIDBeingDisembarked, self.shipIDBeingEmbarked):
            try:
                self.StopEffect(const.effectOnline, moduleID)
                self.remoteDogmaLM.TakeModuleOffline(dogmaItem.locationID, moduleID)
            except Exception:
                self.Activate(moduleID, const.effectOnline)
                raise

    def GetDragData(self, itemID):
        if itemID in self.items:
            return [uix.GetItemData(self.items[itemID], 'icons')]
        dogmaItem = self.dogmaItems[itemID]
        data = uiutil.Bunch()
        data.__guid__ = 'listentry.InvItem'
        data.item = util.KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=self.GetAttributeValue(itemID, const.attributeQuantity))
        data.rec = data.item
        data.itemID = itemID
        data.viewMode = 'icons'
        return [data]

    def GetDisplayAttributes(self, itemID, attributes):
        ret = {}
        dogmaItem = self.dogmaItems[itemID]
        for attributeID in itertools.chain(dogmaItem.attributes, attributes):
            if attributeID == const.attributeVolume:
                continue
            ret[attributeID] = self.GetAttributeValue(itemID, attributeID)

        return ret

    def LinkWeapons(self, shipID, toID, fromID, merge = True):
        if toID == fromID:
            return
        toItem = self.dogmaItems[toID]
        fromItem = self.dogmaItems[fromID]
        for item in (toItem, fromItem):
            if not item.IsOnline():
                raise UserError('CantLinkModuleNotOnline')

        if toItem.typeID != fromItem.typeID:
            self.LogInfo('LinkWeapons::Modules not of same type', toItem, fromItem)
            return
        if toItem.groupID not in const.dgmGroupableGroupIDs:
            self.LogInfo('group not groupable', toItem, fromItem)
            return
        if shipID is None or shipID != fromItem.locationID:
            log.LogTraceback('LinkWeapons::Modules not located in the same place')
        masterID = self.GetMasterModuleID(shipID, toID)
        if not masterID:
            masterID = toID
        slaveID = self.IsInWeaponBank(shipID, fromID)
        if slaveID:
            if merge:
                info = self.remoteDogmaLM.MergeModuleGroups(shipID, masterID, slaveID)
            else:
                info = self.remoteDogmaLM.PeelAndLink(shipID, masterID, slaveID)
        else:
            info = self.remoteDogmaLM.LinkWeapons(shipID, masterID, fromID)
        self.OnWeaponBanksChanged(shipID, info)

    def UngroupModule(self, shipID, moduleID):
        slaveID = self.remoteDogmaLM.UnlinkModule(shipID, moduleID)
        self.slaveModulesByMasterModule[shipID][moduleID].remove(slaveID)
        if not self.slaveModulesByMasterModule[shipID][moduleID]:
            del self.slaveModulesByMasterModule[shipID][moduleID]
        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')
        return slaveID

    def UnlinkAllWeapons(self, shipID):
        info = self.remoteDogmaLM.UnlinkAllModules(shipID)
        self.OnWeaponBanksChanged(shipID, info)
        self.lastUngroupAllRequest = blue.os.GetSimTime()

    def LinkAllWeapons(self, shipID):
        info = self.remoteDogmaLM.LinkAllWeapons(shipID)
        self.OnWeaponBanksChanged(shipID, info)
        self.lastGroupAllRequest = blue.os.GetSimTime()

    def GetGroupAllOpacity(self, attributeName):
        lastRequest = getattr(self, attributeName)
        if lastRequest is None:
            return 1.0
        timeDiff = blue.os.GetSimTime() - lastRequest
        waitTime = min(GROUPALL_THROTTLE_TIMER, GROUPALL_THROTTLE_TIMER - timeDiff)
        opacity = max(0, 1 - float(waitTime) / GROUPALL_THROTTLE_TIMER)
        return opacity

    def IsInWeaponBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        if itemID in slaveModulesByMasterModule:
            return itemID
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is not None:
            return masterID
        return False

    def GetGroupableTypes(self, shipID):
        groupableTypes = defaultdict(lambda : 0)
        try:
            dogmaItem = self.dogmaItems[shipID]
        except KeyError:
            self.LogInfo('GetGroupableTypes - called before I was ready', shipID)
        else:
            for fittedItem in dogmaItem.GetFittedItems().itervalues():
                if not const.flagHiSlot0 <= fittedItem.flagID <= const.flagHiSlot7:
                    continue
                if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                    continue
                if not fittedItem.IsOnline():
                    continue
                groupableTypes[fittedItem.typeID] += 1

        return groupableTypes

    def CanGroupAll(self, shipID):
        groupableTypes = self.GetGroupableTypes(shipID)
        groups = {}
        dogmaItem = self.dogmaItems[shipID]
        for fittedItem in dogmaItem.GetFittedItems().itervalues():
            if fittedItem.groupID not in const.dgmGroupableGroupIDs:
                continue
            if not fittedItem.IsOnline():
                continue
            if not self.IsInWeaponBank(shipID, fittedItem.itemID) and groupableTypes[fittedItem.typeID] > 1:
                return True
            masterID = self.GetMasterModuleID(shipID, fittedItem.itemID)
            if masterID is None:
                masterID = fittedItem.itemID
            if fittedItem.typeID not in groups:
                groups[fittedItem.typeID] = masterID
            elif groups[fittedItem.typeID] != masterID:
                return True

        return False

    def DestroyWeaponBank(self, shipID, itemID):
        self.remoteDogmaLM.DestroyWeaponBank(shipID, itemID)
        self.OnWeaponGroupDestroyed(shipID, itemID)

    def SetWeaponBanks(self, shipID, data):
        super(DogmaLocation, self).SetWeaponBanks(shipID, data)
        self.SetGroupNumbers(shipID)

    def OnWeaponBanksChanged(self, shipID, info):
        self.SetWeaponBanks(shipID, info)
        sm.ScatterEvent('OnRefreshModuleBanks')

    def OnWeaponGroupDestroyed(self, shipID, itemID):
        del self.slaveModulesByMasterModule[shipID][itemID]
        self.SetGroupNumbers(shipID)
        sm.ScatterEvent('OnRefreshModuleBanks')

    def SetGroupNumbers(self, shipID):
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupsDict = allGroupsDict.get(shipID, {})
        for masterID in groupsDict.keys():
            if masterID not in self.slaveModulesByMasterModule[shipID]:
                del groupsDict[masterID]

        for masterID in self.slaveModulesByMasterModule[shipID]:
            if masterID in groupsDict:
                continue
            for i in xrange(1, 9):
                if i not in groupsDict.values():
                    groupsDict[masterID] = i
                    break

        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)

    def GetModulesInBank(self, shipID, itemID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is None and itemID in slaveModulesByMasterModule:
            masterID = itemID
        elif masterID is None:
            return
        moduleIDs = self.GetSlaveModules(masterID, shipID)
        moduleIDs.add(masterID)
        return list(moduleIDs)

    def GetAllSlaveModulesByMasterModule(self, shipID):
        slaveModulesByMasterModule = self.slaveModulesByMasterModule.get(shipID, {})
        return slaveModulesByMasterModule

    def GetMasterModuleForFlag(self, shipID, flagID):
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            raise RuntimeError('GetMasterModuleForFlag, no module in the flag')
        masterID = self.GetMasterModuleID(shipID, moduleID)
        if masterID is not None:
            return masterID
        return moduleID

    def _UnloadDBLessChargesToContainer(self, shipID, itemIDs, containerArgs, flag, quantity):
        if len(itemIDs) > 1:
            ship = self.broker.invCache.GetInventoryFromId(shipID)
            ship.RemoveChargesToLocationFromBank(itemIDs, containerArgs[0])
        else:
            inv = self.broker.invCache.GetInventoryFromId(locationID=session.stationid2, *containerArgs)
            inv.Add(itemIDs[0], shipID, flag=flag, qty=quantity)

    def _UnloadRealItemChargesToContainer(self, shipID, itemIDs, containerArgs, flag, quantity):
        if containerArgs[0] == const.containerHangar:
            inv = self.broker.invCache.GetInventory(const.containerHangar)
        else:
            inv = self.broker.invCache.GetInventoryFromId(locationID=session.stationid2, *containerArgs)
        inv.MultiAdd(itemIDs, shipID, flag=flag, fromManyFlags=True, qty=quantity)

    def UnloadChargeToContainer(self, shipID, itemID, containerArgs, flag, quantity = None):
        if isinstance(itemID, tuple):
            func = self._UnloadDBLessChargesToContainer
            itemIDs = self.GetSubLocationsInBank(shipID, itemID)
        else:
            func = self._UnloadRealItemChargesToContainer
            itemIDs = self.GetCrystalsInBank(shipID, itemID)
        if len(itemIDs) == 0:
            itemIDs = [itemID]
        try:
            func(shipID, itemIDs, containerArgs, flag, quantity)
        except UserError as e:
            if e.msg == 'NotEnoughCargoSpace' and len(itemIDs) > 1:
                eve.Message('NotEnoughCargoSpaceToUnloadBank')
                return
            raise

    def GetSubLocationsInBank(self, shipID, itemID):
        ret = []
        try:
            flagID = self.dogmaItems[itemID].flagID
        except KeyError:
            return []

        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        shipDogmaItem = self.dogmaItems[shipID]
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            chargeID = shipDogmaItem.subLocations.get(moduleDogmaItem.flagID, None)
            if chargeID is not None:
                ret.append(chargeID)

        return ret

    def GetCrystalsInBank(self, shipID, itemID):
        flagID = self.dogmaItems[itemID].flagID
        moduleID = self.GetSlotOther(shipID, flagID)
        if moduleID is None:
            return []
        moduleIDs = self.GetModulesInBank(shipID, moduleID)
        if not moduleIDs:
            return []
        crystals = []
        for moduleID in moduleIDs:
            moduleDogmaItem = self.dogmaItems[moduleID]
            crystal = self.GetChargeNonDB(shipID, moduleDogmaItem.flagID)
            if crystal is not None:
                crystals.append(crystal.itemID)

        return crystals

    def LoadChargeToModule(self, itemID, chargeTypeID, chargeItems = None, qty = None, preferSingletons = False):
        shipID = self.dogmaItems[itemID].locationID
        masterID = self.GetMasterModuleID(shipID, itemID)
        if masterID is None:
            masterID = itemID
        if chargeItems is None:
            shipInv = self.broker.invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
            chargeItems = []
            for item in shipInv.List(const.flagCargo):
                if item.typeID == chargeTypeID:
                    chargeItems.append(item)

        if not chargeItems:
            raise UserError('CannotLoadNotEnoughCharges')
        chargeLocationID = chargeItems[0].locationID
        for item in chargeItems:
            if IsShipFittingFlag(item.flagID):
                raise UserError('CantMoveChargesBetweenModules')

        if preferSingletons:
            for item in chargeItems[:]:
                if not item.singleton:
                    chargeItems.remove(item)

        if qty is not None:
            totalQty = 0
            i = 0
            for item in chargeItems:
                if totalQty >= qty:
                    break
                i += 1
                totalQty += item.stacksize

            chargeItems = chargeItems[:i]
        itemIDs = []
        for item in chargeItems:
            itemIDs.append(item.itemID)

        self.remoteDogmaLM.LoadAmmoToBank(shipID, masterID, chargeTypeID, itemIDs, chargeLocationID)

    def LoadAmmoToModules(self, shipID, moduleIDs, chargeTypeID, itemID, ammoLocationID):
        self.CheckSkillRequirementsForType(None, chargeTypeID, 'FittingHasSkillPrerequisites')
        self.remoteDogmaLM.LoadAmmoToModules(shipID, moduleIDs, chargeTypeID, itemID, ammoLocationID)

    def DropLoadChargeToModule(self, itemID, chargeTypeID, chargeItems, qty = None, preferSingletons = False):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            maxQty = 0
            for item in chargeItems:
                if item.typeID != chargeTypeID:
                    continue
                maxQty += item.stacksize

            if maxQty == 0:
                errmsg = localization.GetByLabel('UI/Common/NoMoreUnits')
            else:
                errmsg = localization.GetByLabel('UI/Common/NoRoomForMore')
            qty = None
            ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
            if ret is not None:
                qty = ret['qty']
                if qty <= 0:
                    return
        self.LoadChargeToModule(itemID, chargeTypeID, chargeItems=chargeItems, qty=qty, preferSingletons=preferSingletons)

    def UnloadModuleToContainer(self, shipID, itemID, containerArgs, flag = None):
        if self.IsInWeaponBank(shipID, itemID):
            ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/Common/Confirm'),
             'question': localization.GetByLabel('UI/Fitting/ClearGroupModule')}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
        item = self.GetItem(itemID)
        containerInv = self.broker.invCache.GetInventoryFromId(*containerArgs)
        if item is not None:
            subLocation = self.GetSubLocation(item.locationID, item.flagID)
            if subLocation is not None:
                containerInv.Add(subLocation, subLocation[0], qty=None, flag=flag)
            crystal = self.GetChargeNonDB(shipID, item.flagID)
            if crystal is not None:
                containerInv.Add(crystal.itemID, item.locationID, qty=None, flag=flag)
        if getattr(containerInv, 'typeID', None) is not None and evetypes.GetGroupID(containerInv.typeID) == const.groupAuditLogSecureContainer:
            flag = settings.user.ui.Get('defaultContainerLock_%s' % containerInv.itemID, None)
        if containerArgs[0] == shipID:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        elif flag is not None:
            containerInv.Add(itemID, item.locationID, qty=None, flag=flag)
        else:
            containerInv.Add(itemID, item.locationID)

    def CheckCanFit(self, locationID, itemID, flagID, fromLocationID):
        item = self.broker.invCache.FetchItem(itemID, fromLocationID)
        if item is None:
            self.LogInfo('ClientDogmaLocation::CheckCanFit - unable to fetch item', locationID, itemID, flagID, fromLocationID)
            return
        maxGroupFitted = self.dogmaStaticMgr.GetTypeAttribute(item.typeID, const.attributeMaxGroupFitted)
        if maxGroupFitted is not None:
            modulesByGroup = self.GetModuleListByShipGroup(locationID, item.groupID)
            if len(modulesByGroup) >= maxGroupFitted:
                shipItem = self.dogmaItems[locationID]
                raise UserError('CantFitTooManyByGroup', {'ship': shipItem.typeID,
                 'module': item.typeID,
                 'groupName': evetypes.GetGroupNameByGroup(item.groupID),
                 'noOfModules': int(maxGroupFitted),
                 'noOfModulesFitted': len(modulesByGroup)})

    def GetOnlineModules(self, shipID):
        return {module.flagID:moduleID for moduleID, module in self.dogmaItems[shipID].GetFittedItems().iteritems() if module.IsOnline()}

    def ShouldStartChanceBasedEffect(self, effectID, itemID, chanceAttributeID):
        dogmaItem = self.dogmaItems[itemID]
        if dogmaItem.groupID == const.groupBooster:
            godmaItem = self.godma.GetItem(itemID)
            if godmaItem is None:
                return False
            effectName = cfg.dgmeffects.Get(effectID).effectName
            godmaEffect = godmaItem.effects.get(effectName, None)
            if godmaEffect is None:
                return False
            if godmaEffect.isActive:
                return True
        return False

    def GetDogmaItemWithWait(self, itemID):
        startTime = blue.os.GetWallclockTime()
        while blue.os.TimeDiffInMs(startTime, blue.os.GetWallclockTime()) < 2000:
            if itemID in self.dogmaItems:
                return self.dogmaItems[itemID]
            self.LogInfo('GetDogmaItemWithWait::Item not ready, sleeping for 100ms')
            blue.pyos.synchro.Sleep(100)

        self.LogError('Failed to get dogmaItem in time', itemID)

    def GetModifierString(self, itemID, attributeID):
        dogmaItem = self.dogmaItems[itemID]
        modifiers = self.GetModifiersOnAttribute(itemID, attributeID, dogmaItem.locationID, dogmaItem.groupID, dogmaItem.ownerID, dogmaItem.typeID)
        baseValue = self.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.typeID, attributeID)
        ret = 'Base Value: %s\n' % GetFormatAndValue(cfg.dgmattribs.Get(attributeID), baseValue)
        if modifiers:
            ret += 'modified by\n'
            for op, modifyingItemID, modifyingAttributeID in modifiers:
                value = self.GetAttributeValue(modifyingItemID, modifyingAttributeID)
                if op in (const.dgmAssPostMul,
                 const.dgmAssPreMul,
                 const.dgmAssPostDiv,
                 const.dgmAssPreDiv) and value == 1.0:
                    continue
                elif op in (const.dgmAssPostPercent, const.dgmAssModAdd, const.dgmAssModAdd) and value == 0.0:
                    continue
                modifyingItem = self.dogmaItems[modifyingItemID]
                modifyingAttribute = cfg.dgmattribs.Get(modifyingAttributeID)
                value = GetFormatAndValue(modifyingAttribute, value)
                ret += '  %s: %s\n' % (evetypes.GetName(modifyingItem.typeID), value)

        return ret

    def GetDamageFromItem(self, itemID):
        accDamage = 0
        for attributeID in (const.attributeEmDamage,
         const.attributeExplosiveDamage,
         const.attributeKineticDamage,
         const.attributeThermalDamage):
            accDamage += self.GetAttributeValue(itemID, attributeID)

        return accDamage

    def GatherDroneInfo(self, shipDogmaItem):
        dronesByTypeID = {}
        for droneID in shipDogmaItem.GetDronesInBay():
            damage = self.GetDamageFromItem(droneID)
            if damage == 0:
                continue
            damageMultiplier = self.GetAttributeValue(droneID, const.attributeDamageMultiplier)
            if damageMultiplier == 0:
                continue
            duration = self.GetAttributeValue(droneID, const.attributeRateOfFire)
            droneDps = damage * damageMultiplier / duration
            droneBandwidth = self.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)
            droneDogmaItem = self.dogmaItems[droneID]
            droneItem = self.GetItem(droneID)
            if droneDogmaItem.typeID not in dronesByTypeID:
                dronesByTypeID[droneItem.typeID] = [droneBandwidth, droneDps, droneItem.stacksize]
            else:
                dronesByTypeID[droneItem.typeID][-1] += droneItem.stacksize

        drones = defaultdict(list)
        for typeID, (bw, dps, qty) in dronesByTypeID.iteritems():
            bw = int(bw)
            drones[bw].append((typeID,
             bw,
             qty,
             dps))

        for l in drones.itervalues():
            l.sort(key=lambda vals: vals[-1], reverse=True)

        return drones

    def SimpleGetDroneDamageOutput(self, drones, bwLeft, dronesLeft):
        dronesUsed = {}
        totalDps = 0
        for bw in sorted(drones.keys(), reverse=True):
            if bw > bwLeft:
                continue
            for typeID, bwNeeded, qty, dps in drones[bw]:
                noOfDrones = min(int(bwLeft) / int(bwNeeded), qty, dronesLeft)
                if noOfDrones == 0:
                    break
                dronesUsed[typeID] = noOfDrones
                totalDps += dps * noOfDrones
                dronesLeft -= noOfDrones
                bwLeft -= noOfDrones * bwNeeded

        return (totalDps, dronesUsed)

    def GetOptimalDroneDamage(self, shipID, *args):
        shipDogmaItem = self.dogmaItems[shipID]
        drones = self.GatherDroneInfo(shipDogmaItem)
        self.LogInfo('Gathered drone info and found', len(drones), 'types of drones')
        bandwidth = self.GetAttributeValue(shipID, const.attributeDroneBandwidth)
        if session.solarsystemid:
            maxDrones = self.godma.GetItem(session.charid).maxActiveDrones
        else:
            maxDrones = self.GetAttributeValue(shipDogmaItem.ownerID, const.attributeMaxActiveDrones)
        self.startedKnapsack = blue.os.GetWallclockTime()
        dps, drones = self.SimpleGetDroneDamageOutput(drones, bandwidth, maxDrones)
        return (dps * 1000, drones)

    def GetTurretAndMissileDps(self, shipID):
        shipDogmaItem = self.dogmaItems[shipID]
        chargesByFlag = {}
        turretsByFlag = {}
        launchersByFlag = {}
        IsTurret = lambda typeID: self.dogmaStaticMgr.TypeHasEffect(typeID, const.effectTurretFitted)
        IsLauncher = lambda typeID: self.dogmaStaticMgr.TypeHasEffect(typeID, const.effectLauncherFitted)
        godmaShipItem = self.godma.GetItem(shipID)
        if godmaShipItem is not None:
            GAV = self.GetGodmaAttributeValue
        else:
            GAV = self.GetAttributeValue
        for module in shipDogmaItem.GetFittedItems().itervalues():
            if IsTurret(module.typeID):
                if not module.IsOnline():
                    continue
                turretsByFlag[module.flagID] = module.itemID
            elif IsLauncher(module.typeID):
                if not module.IsOnline():
                    continue
                launchersByFlag[module.flagID] = module.itemID
            elif module.categoryID == const.categoryCharge:
                chargesByFlag[module.flagID] = module.itemID

        turretDps = 0
        for flagID, itemID in turretsByFlag.iteritems():
            chargeKey = chargesByFlag.get(flagID)
            thisTurretDps = self.GetTurretDps(chargeKey, itemID, GAV)
            turretDps += thisTurretDps

        missileDps = 0
        for flagID, itemID in launchersByFlag.iteritems():
            chargeKey = chargesByFlag.get(flagID)
            if chargeKey is None:
                continue
            thisLauncherDps = self.GetLauncherDps(chargeKey, itemID, shipDogmaItem.ownerID, GAV)
            missileDps += thisLauncherDps

        return (turretDps, missileDps)

    def GetTurretDps(self, chargeKey, itemID, GAV, *args):
        turretDps = 0.0
        if chargeKey is not None:
            damage = self.GetDamageFromItem(chargeKey)
        else:
            damage = self.GetDamageFromItem(itemID)
        if abs(damage) > 0:
            damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
            duration = GAV(itemID, const.attributeRateOfFire)
            if abs(duration) > 0:
                turretDps = damage * damageMultiplier / duration
        return turretDps * 1000

    def GetLauncherDps(self, chargeKey, itemID, ownerID, GAV, damageMultiplier = None):
        missileDps = 0.0
        damage = self.GetDamageFromItem(chargeKey)
        duration = GAV(itemID, const.attributeRateOfFire)
        if damageMultiplier is None:
            damageMultiplier = GAV(ownerID, const.attributeMissileDamageMultiplier)
        missileDps = damage * damageMultiplier / duration
        return missileDps * 1000

    def GetGodmaAttributeValue(self, itemID, attributeID):
        attributeName = self.dogmaStaticMgr.attributes[attributeID].attributeName
        return self.godma.GetStateManager().GetAttribute(itemID, attributeName)

    def GetModulesLackingSkills(self):
        ret = []
        for moduleID, module in self.dogmaItems[self.GetCurrentShipID()].GetFittedItems().iteritems():
            if module.categoryID == const.categoryModule and IsShipFittingFlag(module.flagID) and not const.flagRigSlot0 <= module.flagID <= const.flagRigSlot7:
                if self._GetMissingSkills(module.typeID):
                    ret.append(moduleID)

        return ret

    def OnServerBrainUpdated(self, brainData):
        self.LogInfo('OnServerBrainUpdated received for character %s' % session.charid)
        shipID = util.GetActiveShip()
        if shipID is None:
            self.LogInfo('OnServerBrainUpdated:ClientDomgaLocation has not embarked character to anything. Nothing to do.')
            self.ProcessBrainData(session.charid, brainData)
            return
        with self.brainUpdate.Event(shipID):
            self.RemoveBrainEffects(shipID, session.charid, 'clientDogmaLocation.OnServerBrainUpdated')
            self.ProcessBrainData(session.charid, brainData)
            self.ApplyBrainEffects(shipID, session.charid, 'clientDogmaLocation.OnServerBrainUpdated')

    def GetModifiedTypeAttribute(self, typeID, attributeID):
        return self.dogmaStaticMgr.GetTypeAttribute(typeID, attributeID)

    def GetCurrentShipHeatStates(self):
        shipID = self.GetCurrentShipID()
        shipHeatStates = {}
        if shipID:
            shipHeatStates = self.dogmaItems[shipID].GetHeatValues()
        return shipHeatStates

    def OnHeatAdded(self, heatID, moduleID):
        shipItem = self.dogmaItems[self.GetCurrentShipID()]
        moduleItem = self.dogmaItems[moduleID]
        sourceAttribute = moduleItem.attributes[const.attributeHeatAbsorbtionRateModifier]
        heatAttribute = shipItem.attributes[heatID]
        sourceAttribute.AddOutgoingModifier(const.dgmAssModAdd, heatAttribute.incomingHeat)
        heatAttribute.AddIncomingModifier(const.dgmAssModAdd, sourceAttribute)

    def OnHeatRemoved(self, heatID, moduleID):
        shipItem = self.dogmaItems[self.GetCurrentShipID()]
        moduleItem = self.dogmaItems[moduleID]
        sourceAttribute = moduleItem.attributes[const.attributeHeatAbsorbtionRateModifier]
        heatAttribute = shipItem.attributes[heatID]
        sourceAttribute.RemoveOutgoingModifier(const.dgmAssModAdd, heatAttribute.incomingHeat)
        heatAttribute.RemoveIncomingModifier(const.dgmAssModAdd, sourceAttribute)
