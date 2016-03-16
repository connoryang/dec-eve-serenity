#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\baseDogmaLocation.py
from dogma.eventCounters import EventCount, BrainUpdate
import log
from dogma.dogmaLogging import *
import blue
import sys
from dogma.items.notWantedDogmaItem import NotWantedDogmaItem
import evetypes
import stackless
from carbon.common.script.sys.sessions import FindSessionClient
from eve.common.script.dogma.effect import ApplyBrainEffect, RemoveBrainEffect
from dogma.items.dblessDogmaItem import DBLessDogmaItem
from dogma.items.shipDogmaItem import ShipDogmaItem
from dogma.items.probeDogmaItem import ProbeDogmaItem
from dogma.items.chargeDogmaItem import ChargeDogmaItem
from dogma.items.moduleDogmaItem import ModuleDogmaItem
from dogma.items.characterFittedDogmaItem import CharacterFittedDogmaItem
from dogma.items.controlTowerDogmaItem import ControlTowerDogmaItem
from dogma.items.starbaseDogmaItem import StarbaseDogmaItem
from dogma.items.droneDogmaItem import DroneDogmaItem
from dogma.items.baseDogmaItem import BaseDogmaItem
from dogma.items.characterDogmaItem import CharacterDogmaItem
from dogma.exceptions import EmbarkOnlineError, EffectFailedButShouldBeStopped
from dogma.attributes.attribute import BrainLiteralAttribute
from dogma.attributes.attribute import StackingNurfedAttribute
from inventorycommon.util import IsShipFittingFlag
import weakref
import uthread
import bluepy
import telemetry
import util
import evetypes
from utillib import keydefaultdict
from collections import defaultdict
from dogma.effects.environment import Environment
from ccpProfile import TimedFunction
from dogma import const as dogmaConst

def OpName(opIdx):
    try:
        return opDecoder[opIdx]
    except KeyError:
        return opIdx


opDecoder = {None: '..',
 const.dgmAssPreAssignment: '=.',
 const.dgmAssPreMul: '*.',
 const.dgmAssPreDiv: '/.',
 const.dgmAssModAdd: ' +',
 const.dgmAssModSub: ' -',
 const.dgmAssPostMul: '.*',
 const.dgmAssPostDiv: './',
 const.dgmAssPostPercent: '.%',
 const.dgmAssPostAssignment: '.=',
 9: '.!'}

class MessageMgr(object):

    def __init__(self):
        self.attributes = set()

    def AddAttribute(self, attr):
        self.attributes.add(attr)

    def GetMessages(self):
        messages = []
        for each in self.attributes:
            msg = each.ConstructMessage()
            if msg is not None:
                messages.append(msg)

        return messages

    def Clear(self):
        self.attributes.clear()


class BaseDogmaLocation(object):

    def __init__(self, broker):
        self.broker = broker
        self.onlineEffects = {const.effectOnline: True,
         const.effectOnlineForStructures: True}
        self.shipsByPilotID = {}
        self.pilotsByShipID = {}
        self.dogmaItems = {}
        self.locationID = None
        self.locationName = None
        self.locationGroup = const.groupSystem
        self.moduleListsByShipGroup = defaultdict(lambda : defaultdict(set))
        self.attributeChangeCallbacksByAttributeID = {}
        self.loadingItems = {}
        self.failedLoadingItems = {}
        self.crits = {}
        self.activatingEffects = {}
        self.deactivatingEffects = set()
        self.activatingEffectsByLocation = {}
        self.activatingEffectsByTarget = {}
        self.activeEffectsByShip = {}
        self.activeDungeonEffectsByItem = defaultdict(lambda : defaultdict(list))
        self.instanceFlagQuantityCache = {}
        self.unloadingItems = set()
        self.extraTracebacks = True
        self.checkShipOnlineModulesPending = set()
        self.ignoredOwnerEvents = EventCount()
        self.ignoreOwnerEvents = {}
        self.itemsMissingLocation = defaultdict(set)
        self.itemsMissingOwner = defaultdict(set)
        self.modifiersAwaitingTarget = defaultdict(set)
        self.slaveModulesByMasterModule = {}
        self.onlineByShip = {}
        self.embarkingShips = {}
        self.instanceRowDescriptor = blue.DBRowDescriptor((('instanceID', const.DBTYPE_I8),
         ('online', const.DBTYPE_BOOL),
         ('damage', const.DBTYPE_R5),
         ('charge', const.DBTYPE_R5),
         ('skillPoints', const.DBTYPE_I4),
         ('armorDamage', const.DBTYPE_R5),
         ('shieldCharge', const.DBTYPE_R5),
         ('incapacitated', const.DBTYPE_BOOL)))
        l = [0] + [0] * (len(self.instanceRowDescriptor) - 1)
        self.fakeInstanceRow = blue.DBRow(self.instanceRowDescriptor, l)
        self.RegisterCallback(const.attributeCpuLoad, self.OnCpuAttributeChanged)
        self.RegisterCallback(const.attributePowerLoad, self.OnPowerAttributeChanged)
        self.msgMgr = MessageMgr()
        self.brainLiterals = keydefaultdict(BrainLiteralAttribute)
        self.scarecrows = {}
        self.brainUpdate = BrainUpdate(self.CheckShipOnlineModules)

    def LoadItem(self, itemKey, instanceRow = None, wait = False, item = None, newInstance = False, timerName = None):
        invItem = item
        del item
        if itemKey == self.locationID:
            return itemKey
        if itemKey in self.dogmaItems:
            return itemKey
        self.PreLoadItemActions(itemKey)
        if itemKey in self.dogmaItems:
            return itemKey
        self.EnterCriticalSection('LoadItem', itemKey)
        try:
            if itemKey in self.dogmaItems:
                return itemKey
            self.loadingItems[itemKey] = stackless.channel()
            try:
                dogmaItem = self._LoadItem(itemKey, instanceRow=instanceRow, invItem=invItem, newInstance=newInstance)
            finally:
                while self.loadingItems[itemKey].queue:
                    self.loadingItems[itemKey].send(None)

                del self.loadingItems[itemKey]

            if dogmaItem is not None:
                if itemKey in self.modifiersAwaitingTarget:
                    LogNotice('LoadItem: Calling (and clearing) pending modifiers via itemKey {} for dogmaItem {}\n  modifiers = {}'.format(itemKey, dogmaItem, self.modifiersAwaitingTarget[itemKey]))
                    for callTuple in self.modifiersAwaitingTarget[itemKey]:
                        callTuple[0](*callTuple[1:])

                    del self.modifiersAwaitingTarget[itemKey]
                dogmaItem.PostLoadAction()
        except Exception as e:
            log.LogException('Failed to load a dogma item %s' % str(itemKey))
            try:
                if not len(e.args) or not e.args[0].startswith('GetItem: Item not here'):
                    self.failedLoadingItems[itemKey] = 'Exception: ' + strx(e)
            except Exception:
                pass

            raise e
        finally:
            self.LeaveCriticalSection('LoadItem', itemKey)

        return itemKey

    def _LoadItem_LogOnEntry(self, itemKey, invItem):
        givenInvItemDescription = self.DescribeInvItem(invItem)
        foundDogmaItem = self.dogmaItems.get(itemKey, None)
        foundInvItemDescription = self.DescribeInvItem(foundDogmaItem.invItem) if foundDogmaItem else None
        totalItems = len(self.dogmaItems)
        LogNotice('LoadItem requested for itemKey: {itemKey}, with given invItem {givenInvItemDescription}, having existing dogmaItems entry {foundDogmaItem} with invItem {foundInvItemDescription} (totalItems = {totalItems}) '.format(**locals()))

    def _LoadItem_LogOnExit(self, itemKey):
        dogmaItem = self.dogmaItems.get(itemKey, None)
        invItemDescription = self.DescribeInvItem(dogmaItem.invItem) if dogmaItem else None
        LogNotice('LoadItem completed for itemKey: {itemKey}, having dogmaItems entry {dogmaItem} and invItem {invItemDescription}'.format(**locals()))

    def PreLoadItemActions(self, itemKey):
        pass

    def PostLoadItemActions(self, itemKey):
        pass

    def GetQuantityFromCache(self, locationID, flagID):
        return self.instanceFlagQuantityCache[locationID][flagID].quantity

    @TimedFunction('BaseDogmaLocation::_LoadItem')
    def _LoadItem(self, itemKey, instanceRow = None, invItem = None, newInstance = False):
        self.LogInfo('BaseDogmaLocation::_LoadItem', itemKey)
        if isinstance(itemKey, tuple):
            virtualInvItem = util.KeyVal()
            virtualInvItem.itemID = itemKey
            virtualInvItem.locationID, virtualInvItem.flagID, virtualInvItem.typeID = itemKey
            virtualInvItem.groupID = evetypes.GetGroupID(virtualInvItem.typeID)
            virtualInvItem.categoryID = evetypes.GetCategoryID(virtualInvItem.typeID)
            virtualInvItem.ownerID = self.dogmaItems[virtualInvItem.locationID].ownerID
            dogmaItem = DBLessDogmaItem(weakref.proxy(self), virtualInvItem, cfg, FindSessionClient)
            dogmaItem.Load()
            self.FitItemToLocation(virtualInvItem.locationID, itemKey, virtualInvItem.flagID)
            locationID, flagID, typeID = itemKey
            try:
                quantity = self.GetQuantityFromCache(locationID, flagID)
                dogmaItem.attributes[const.attributeQuantity].SetBaseValue(quantity)
            except KeyError:
                sys.exc_clear()

            return dogmaItem
        if invItem is None:
            invItem = self.GetItem(itemKey)
        if invItem is None:
            raise RuntimeError('Dogma was unable to get invItem to load dogmaItem!')
        if not self.IsItemWanted(invItem.typeID) or newInstance:
            instanceRow = self.IntroduceNewItem(invItem)
        else:
            instanceRow = self.GetInstance(invItem)
        self.LogInfo('BaseDogmaLocation::Actually Loading invItem', itemKey)
        dogmaItem = self.GetClassForItem(invItem)(weakref.proxy(self), invItem, cfg, FindSessionClient)
        dogmaItem.Load(invItem, instanceRow)
        if invItem.flagID != const.flagPilot:
            self.FitItemToLocation(invItem.locationID, itemKey, invItem.flagID)
        dogmaItem.OnItemLoaded()
        self.HandleDogmaLocationEffectsOnItem(dogmaItem)
        return dogmaItem

    def GetDogmaItem(self, itemID):
        return self.dogmaItems[itemID]

    def SafeGetDogmaItem(self, itemID):
        return self.dogmaItems.get(itemID, None)

    def CheckApplyBrainEffects(self, shipID):
        pass

    def SetBrainData(self, charID, brain):
        pass

    def GetBrainData(self, charID):
        pass

    def InitBrain(self, charID, brain):
        pass

    @telemetry.ZONE_METHOD
    def GetModuleListByShipGroup(self, locationID, groupID):
        return self.moduleListsByShipGroup.get(locationID, {}).get(groupID, [])

    def HandleDogmaLocationEffectsOnItem(self, dogmaItem):
        pass

    def ApplyBrainEffects(self, shipID, charID, timerName = 'unknown'):
        self.broker.LogInfo('%s ApplyBrainEffects %s %s. Called from %s' % (self.locationName,
         shipID,
         charID,
         timerName))
        if shipID is None:
            self.broker.LogError('ApplyBrainEffects - shipID is None')
        if charID is None:
            self.broker.LogError('ApplyBrainEffects - charID is None!')
            return
        startTime = blue.os.GetWallclockTimeNow()
        currentShipID = self.shipsByPilotID.get(charID, None)
        if shipID != currentShipID:
            log.LogTraceback("ApplyBrainEffects called for shipID %s but Dogma's shipsByPilots thinks I'm in ship %s" % (shipID, currentShipID))
            self.shipsByPilotID[charID] = shipID
        currentPilotID = self.pilotsByShipID.get(shipID, None)
        if charID != currentPilotID:
            log.LogTraceback("ApplyBrainEffects called for pilot %s in shipID %s but Dogma's pilotsByShips says it is piloted by %s" % (charID, shipID, currentPilotID))
            self.pilotsByShipID[shipID] = charID
        if not self.CheckApplyBrainEffects(shipID):
            endTime = blue.os.GetWallclockTimeNow()
            self.broker.LogInfo('%s - ApplyBrainEffects took %s ms' % (self.locationID, blue.os.TimeDiffInMs(startTime, endTime)))
            return
        log.LogInfo('%s - ApplyBrainEffects to shipID %s' % (self.locationID, shipID))
        shipDogmaItem = self.dogmaItems.get(shipID, None)
        if not shipDogmaItem:
            self.LogError('ApplyBrainEffects:ShipDogmaItem not found!')
            return
        shipTypeID = shipDogmaItem.typeID
        validAttribs = {x.attributeID for x in cfg.dgmtypeattribs[shipTypeID]}
        validAttribs.add(const.attributeCapacity)
        _, charEffects, shipEffects = self.GetBrainData(charID)
        self.broker.LogInfo('%s - Applying %s ship effects to %s' % (self.locationID, len(shipEffects), shipID))
        for effect in shipEffects:
            if effect.modifierType == 'M' and effect.toAttribID not in validAttribs:
                continue
            literal = self.brainLiterals[effect.GetLiteralKey()]
            effType = effect.modifierType
            ApplyBrainEffect[effType](self, shipID, literal, *effect.GetApplicationArgs())

        self.broker.LogInfo('%s - Applying %s character effects to %s' % (self.locationID, len(charEffects), charID))
        for effect in charEffects:
            literal = self.brainLiterals[effect.GetLiteralKey()]
            effType = effect.modifierType
            ApplyBrainEffect[effType](self, charID, literal, *effect.GetApplicationArgs())

        endTime = blue.os.GetWallclockTimeNow()
        self.broker.LogInfo('%s - ApplyBrainEffects took %s ms' % (self.locationID, blue.os.TimeDiffInMs(startTime, endTime)))

    def RemoveBrainEffects(self, shipID, charID, timerName = None):
        self.broker.LogInfo('%s RemoveBrainEffects %s %s. Called from %s' % (self.locationName,
         shipID,
         charID,
         timerName))
        startTime = blue.os.GetWallclockTimeNow()
        currentShipID = self.shipsByPilotID.get(charID, None)
        if shipID != currentShipID:
            log.LogTraceback("RemoveBrainEffects called for shipID %s but Dogma's shipsByPilots thinks I'm in ship %s" % (shipID, currentShipID))
        currentPilotID = self.pilotsByShipID.get(shipID, None)
        if charID != currentPilotID:
            log.LogTraceback("RemoveBrainEffects called for pilot %s in shipID %s but Dogma's pilotsByShips says it is piloted by %s" % (charID, shipID, currentPilotID))
        _, charEffects, shipEffects = self.GetBrainData(charID)
        if shipID is not None:
            shipDogmaItem = self.dogmaItems.get(shipID, None)
            if not shipDogmaItem:
                self.LogError('RemoveBrainEffects:ShipDogmaItem not found!')
                return
            shipTypeID = shipDogmaItem.typeID
            validAttribs = {x.attributeID for x in cfg.dgmtypeattribs[shipTypeID]}
            validAttribs.add(const.attributeCapacity)
            self.broker.LogInfo('Removing %s ship effects from %s' % (len(shipEffects), shipID))
            for effect in shipEffects:
                if effect.modifierType == 'M' and effect.toAttribID not in validAttribs:
                    continue
                literal = self.brainLiterals[effect.GetLiteralKey()]
                effType = effect.modifierType
                RemoveBrainEffect[effType](self, shipID, literal, *effect.GetApplicationArgs())

        self.broker.LogInfo('Removing %s character effects from %s' % (len(charEffects), charID))
        for effect in charEffects:
            literal = self.brainLiterals[effect.GetLiteralKey()]
            effType = effect.modifierType
            RemoveBrainEffect[effType](self, charID, literal, *effect.GetApplicationArgs())

        endTime = blue.os.GetWallclockTimeNow()
        self.broker.LogInfo('%s RemoveBrainEffects took %s ms' % (self.locationID, blue.os.TimeDiffInMs(startTime, endTime)))

    def OnCharacterEmbarkation(self, charID, shipID, switching = False, raiseOnOnlineFailure = False):
        self.LogInfo('OnCharacterEmbarkation charID', charID, 'shipID', shipID)
        with util.ExceptionEater('OnCharacterEmbarkation %s %s' % (charID, shipID)):
            shipItem = self.GetItem(shipID)
            if shipItem.ownerID != charID:
                log.LogTraceback('Ship inventory item owned by ID %s not character. Dogma pilot is %s' % (shipItem.ownerID, self.pilotsByShipID.get(shipID, None)))
        self.embarkingShips[shipID] = charID
        try:
            self._OnCharacterEmbarkation(charID, shipID, switching, raiseOnOnlineFailure)
        finally:
            if shipID in self.embarkingShips:
                del self.embarkingShips[shipID]

    def _OnCharacterEmbarkation(self, charID, shipID, switching, raiseOnOnlineFailure):
        if self.shipsByPilotID.get(charID, None) == shipID:
            self.LogError('OnCharacterEmbarkation - character already embarked? Are we doing things out of order?', charID, shipID, switching)
            return
        if charID in self.shipsByPilotID:
            skipCheck = False
            oldShipID = self.shipsByPilotID.get(charID, None)
        else:
            skipCheck = True
            oldShipID = None
        if oldShipID == shipID:
            self.LogError("OnCharacterEmbarkation - character seem to have been already fitted to this ship so I'm returning", charID, shipID, switching)
            return
        if not self.IsItemLoaded(charID):
            self.LoadItem(charID)
        if not self.IsItemLoaded(shipID):
            self.LoadItem(shipID)
        shipDogmaItem = self.dogmaItems[shipID]
        charDogmaItem = self.dogmaItems[charID]
        charDogmaItem.SetLocation(shipID, shipDogmaItem, const.flagPilot)
        shipFittedItems = shipDogmaItem.GetFittedItems()
        if self.extraTracebacks:
            self.LogInfo('Embark, sorting modules and ship', shipID, shipFittedItems.keys())
        for itemKey in shipFittedItems:
            self.InstallPilotForItem(itemKey, shipID, charID)

        for droneID in shipDogmaItem.GetDronesInBay():
            if droneID not in self.dogmaItems:
                self.LogError("drone in ship's drone dict but not actually loadedd", droneID, charID, shipID)
                continue
            self.InstallPilotForItem(droneID, shipID, charID)

        if self.extraTracebacks:
            self.LogInfo('Embark, sorted modules and ship', shipID, shipFittedItems.keys())
        self.broker.LogInfo('OnCharacterEmbarkation - char adoption', charID)
        self.LogInfo('OnCharacterEmbarkation - char', charID, 'reonlining modules on ship', shipID)
        self.ApplyBrainEffects(shipID, charID, 'baseDogmaLocation._OnCharacterEmbarkation')
        if shipID in self.onlineByShip:
            d = self.onlineByShip[shipID]
            del self.onlineByShip[shipID]
            self.LogInfo('OnCharacterEmbarkation - ship', shipID, 'had online cache hit', d)
            flags = d.keys()
            flags.sort()
            brokenByID = {}
            for i in range(len(flags) - 1, -1, -1):
                moduleID = d[flags[i]]
                try:
                    self.StopEffect(const.effectOnline, moduleID, 0)
                except UserError as e:
                    brokenByID[moduleID] = True
                    item = self.inventory2.GetItem(moduleID)
                    self.broker.LogError('Char', charID, 'piloting', shipID, 'module', moduleID, evetypes.GetName(item.typeID), 'not offline, reason', e)
                    log.LogException(channel='svc.dogmaIM')
                    sys.exc_clear()

            for flag in flags:
                moduleID = d[flag]
                if moduleID not in brokenByID:
                    try:
                        self.StartModuleOnlineEffect(moduleID, charID, shipID, raiseUserError=raiseOnOnlineFailure)
                    except UserError as e:
                        if raiseOnOnlineFailure:
                            log.LogException('Failed to online modules on undock', severity=log.LGWARN, channel='svc.dogmaIM')
                            raise EmbarkOnlineError('FailedToOnlineModulesOnUndock')
                        if e.msg != 'OnlineHasSkillPrerequisites':
                            item = self.inventory2.GetItem(moduleID)
                            self.broker.LogWarn('OnCharacterEmbarkation - char', charID, 'piloting', shipID, 'module', moduleID, evetypes.GetName(item.typeID), 'not onlined again, reason', e)
                            log.LogException(channel='svc.dogmaIM')
                        sys.exc_clear()

            self.LogInfo('OnCharacterEmbarkation - char', charID, 'reonlined modules on ship', shipID, 'candidates', d)

    def InstallPilotForItem(self, itemKey, shipID, pilotID):
        dogmaItem = self.dogmaItems[itemKey]
        itemTypeID = dogmaItem.typeID
        itemGroupID = evetypes.GetGroupID(itemTypeID)
        fittableNonSingleton = evetypes.GetIsGroupFittableNonSingletonByGroup(itemGroupID)
        targetID = shipID
        otherID = None
        aeff = dogmaItem.activeEffects
        for effectID in self.dogmaStaticMgr.passiveFilteredEffectsByType.get(itemTypeID, []):
            if effectID not in aeff:
                if otherID is None and fittableNonSingleton:
                    otherID = self.GetSlotOther(shipID, dogmaItem.flagID)
                if otherID is None and self.effectCompiler.IsEffectDomainOther(effectID):
                    continue
                self.LogInfo('InstallPilotForItem.effect', itemKey, effectID, cfg.dgmeffects.Get(effectID).effectName)
                try:
                    env = Environment(itemKey, pilotID, shipID, targetID, otherID, effectID, weakref.proxy(self), None)
                    self.StartEffect(effectID, itemKey, env)
                except UserError as e:
                    sys.exc_clear()
                    ek, ea = e.msg, e.dict
                    if ek == 'ShipExploding':
                        self.LogInfo('InstallPilotForItem - ship', shipID, 'exploding, so module', itemKey, 'fit failed,  mid effect start loop', effectID)
                        return

            elif self.effectCompiler.IsEffectCharacterModifier(effectID):
                log.LogTraceback('(install) Item %s already has effect %s active' % (itemKey, effectID), channel='svc.dogmaIM')

    @TimedFunction('BaseDogmaLocation::FitItemToLocation')
    def FitItemToLocation(self, locationID, itemID, flagID):
        self.LogInfo('FitItemToLocation', locationID, itemID, flagID)
        if locationID == self.locationID:
            self.LogInfo('Attempting to fit item to self.locationID. Ignored!')
            return
        if locationID not in self.dogmaItems:
            wasItemLoaded = itemID in self.dogmaItems
            if locationID != self.locationID:
                self.LoadItem(locationID)
            if not wasItemLoaded:
                self.LogInfo('Neither location not item was loaded. Loaded location and returned.', locationID, itemID)
                return
        if itemID not in self.dogmaItems:
            self.LoadItem(itemID)
            return
        locationDogmaItem = self.dogmaItems.get(locationID, None)
        if locationDogmaItem is None:
            self.LogInfo('FitItemToLocation::Fitted to None item', itemID, locationID, flagID)
            return
        dogmaItem = self.dogmaItems[itemID]
        if not locationDogmaItem.CanFitItem(dogmaItem, flagID):
            if locationDogmaItem.categoryID == const.categoryShip:
                log.LogTraceback("Somebody asked us to fit an item to a ship that can't be fitted")
            return
        oldOwnerID, oldLocationID, oldFlagID = oldInfo = dogmaItem.GetLocationInfo()
        dogmaItem.SetLocation(locationID, locationDogmaItem, flagID)
        LogNotice('FitItemToLocation: Calling StartPassiveEffects for itemID =', itemID)
        startedEffects = self.StartPassiveEffects(itemID, dogmaItem.typeID)
        if startedEffects is not None:
            self.UnsetItemLocation(itemID, locationID)
            for effectID in startedEffects:
                try:
                    self.StopEffect(effectID, itemID, 1)
                except UserError as e:
                    log.LogException('Failed to start effect %s' % effectID, channel='svc.dogmaIM')
                    sys.exc_clear()

            if util.IsFlagSubSystem(dogmaItem.flagID):
                raise RuntimeError('Failed to start passive effects on a subsystem')
            raise UserError('ModuleFitFailed', {'moduleName': (const.UE_GROUPID, dogmaItem.groupID),
             'reason': ''})
        locationCategoryID = locationDogmaItem.categoryID
        if locationCategoryID == const.categoryShip and dogmaItem.attributes.get(const.attributeIsOnline, False) and self.dogmaStaticMgr.TypeHasEffect(dogmaItem.typeID, const.effectOnline):
            pilotID = dogmaItem.GetPilot()
            LogNotice('FitItemToLocation: Calling StartModuleOnlineEffect for itemID =', itemID)
            self.StartModuleOnlineEffect(dogmaItem.itemID, pilotID, dogmaItem.locationID)
        return oldInfo

    @telemetry.ZONE_METHOD
    def _StartModuleOnlineEffect(self, itemID, pilotID, locationID, context = None, raiseUserError = False):
        environment = Environment(itemID, pilotID, locationID, None, None, const.effectOnline, weakref.proxy(self), None)
        if context is not None:
            for k, v in context.iteritems():
                setattr(environment, k, v)

        try:
            self.StartEffect(const.effectOnline, itemID, environment, 1, byUser=True)
        except UserError as e:
            if e.msg.startswith('EffectAlreadyActive'):
                self.LogInfo('Tried to online', itemID, 'in', locationID, 'but failed because of', e)
            else:
                self.SetAttributeValue(itemID, const.attributeIsOnline, 0)
            if raiseUserError:
                raise
            sys.exc_clear()

    def StartModuleOnlineEffect(self, itemID, pilotID, locationID, context = None, raiseUserError = False):
        item = self.GetItem(itemID)
        if item.locationID != locationID or not IsShipFittingFlag(item.flagID):
            self.LogInfo('StartModuleOnlineEffect::Unexpected location', itemID, item.locationID, locationID)
            return
        if not self.dogmaStaticMgr.TypeHasEffect(item.typeID, const.effectOnline):
            log.LogTraceback('type: %s does not have online effect' % item.typeID)
            return
        if pilotID is not None:
            self._StartModuleOnlineEffect(itemID, pilotID, locationID, context=context, raiseUserError=raiseUserError)
            return
        if locationID not in self.onlineByShip:
            self.onlineByShip[locationID] = {}
        dogmaItem = self.dogmaItems[itemID]
        flagID = dogmaItem.flagID
        dogmaItem.attributes[const.attributeIsOnline].SetBaseValue(1)
        self.onlineByShip[locationID][flagID] = itemID

    def UnfitItemFromLocation(self, locationID, itemID, flushEffects = False):
        self.UnsetItemLocation(itemID, locationID)
        dogmaItem = self.dogmaItems[itemID]
        itemTypeID, itemGroupID = dogmaItem.typeID, dogmaItem.groupID
        for effectID, effect in dogmaItem.activeEffects.items():
            if type(effectID) is tuple:
                effectID = effectID[0]
            if not flushEffects and effect[const.ACT_IDX_DURATION] != -1:
                raise UserError('ModuleEffectActive', {'module': itemTypeID})
            if self.dogmaStaticMgr.effects[effectID].effectCategory != const.dgmEffPassive:
                self.StopEffect(effectID, itemID, forced=flushEffects)

        effectsCompleted = set()
        if self.dogmaStaticMgr.effectsByType.has_key(itemTypeID):
            for effectID in self.dogmaStaticMgr.TypeGetOrderedEffectIDs(itemTypeID):
                if effectID not in dogmaItem.activeEffects:
                    continue
                effect = self.dogmaStaticMgr.effects[effectID]
                if effect.effectCategory in [const.dgmEffPassive, const.dgmEffSystem]:
                    try:
                        self.StopEffect(effectID, itemID)
                        effectsCompleted.add(effect)
                    except UserError as e:
                        for effect in effectsCompleted:
                            try:
                                info = dogmaItem.GetEnvironmentInfo()
                                env = Environment(info.itemID, info.charID, info.shipID, None, info.otherID, effectID, weakref.proxy(self), None)
                                self.StartEffect(effect.effectID, itemID, env)
                            except UserError as e:
                                log.LogException(channel='svc.dogmaIM')
                                sys.exc_clear()

                        sys.exc_clear()

    def UnsetItemLocation(self, itemKey, locationID):
        locationDogmaItem = self.dogmaItems.get(locationID, None)
        dogmaItem = self.dogmaItems[itemKey]
        if locationDogmaItem is None:
            self.LogError("UnsetItemLocation::called for location that wasn't loaded", itemKey, locationID)
            return
        dogmaItem.UnsetLocation(locationDogmaItem)

    @bluepy.TimedFunction('DogmaLocation::StartEffect')
    def StartEffect(self, effectID, itemKey, environment, repeat = 0, byUser = 0, checksOnly = None):
        dogmaItem = None
        try:
            dogmaItem = self.dogmaItems[itemKey]
        except KeyError:
            self.LogError('StartEffect::Item neither loaded nor being loaded', effectID, itemKey)
            self.LoadItem(itemKey)
            dogmaItem = self.dogmaItems[itemKey]

        activateKey = (itemKey, effectID)
        if effectID not in self.dogmaStaticMgr.effectsByType.get(dogmaItem.typeID, []):
            if effectID == const.effectOnline:
                self.LogInfo("StartEffect::Online Effect being started on a type that doesn't have it", itemKey, dogmaItem.typeID, effectID)
            else:
                self.LogError("StartEffect::Effect being started on type that doesn't have it (unexpected)", itemKey, dogmaItem.typeID, effectID)
            return
        if dogmaItem.IsEffectRegistered(effectID, environment):
            raise UserError('EffectAlreadyActive2', {'modulename': (const.UE_TYPEID, dogmaItem.typeID)})
        if activateKey in self.activatingEffects:
            self.broker.LogWarn('Effect already activating o_O', activateKey, blue.os.TimeDiffInMs(self.activatingEffects[activateKey][0], blue.os.GetSimTime()) / 1000.0)
            raise UserError('EffectAlreadyActive2', {'modulename': (const.UE_TYPEID, dogmaItem.typeID)})
        self.activatingEffects[activateKey] = [blue.os.GetSimTime(), None, environment]
        itemLocationID = dogmaItem.locationID
        if itemLocationID not in self.activatingEffectsByLocation:
            self.activatingEffectsByLocation[itemLocationID] = set([activateKey])
        else:
            self.activatingEffectsByLocation[itemLocationID].add(activateKey)
        targetID = environment.targetID
        if targetID:
            if targetID not in self.activatingEffectsByTarget:
                self.activatingEffectsByTarget[targetID] = set([activateKey])
            else:
                self.activatingEffectsByTarget[targetID].add(activateKey)
        try:
            effect = self.dogmaStaticMgr.effects[effectID]
            self.StartEffect_PreChecks(effect, dogmaItem, environment, byUser)
            duration = self.GetEffectDuration(effect, environment)
            try:
                effectStart = self._StartEffect(effect, dogmaItem, environment, duration, repeat, byUser, checksOnly)
            except EffectFailedButShouldBeStopped:
                effectStart = blue.os.GetSimTime()
                repeat = 0
                sys.exc_clear()

            self.RegisterEffect(effect, dogmaItem, environment, effectStart, duration, repeat)
        finally:
            del self.activatingEffects[activateKey]
            self.activatingEffectsByLocation[itemLocationID].remove(activateKey)
            if not len(self.activatingEffectsByLocation[itemLocationID]):
                del self.activatingEffectsByLocation[itemLocationID]
            if targetID:
                self.activatingEffectsByTarget[targetID].remove(activateKey)
                if not len(self.activatingEffectsByTarget[targetID]):
                    del self.activatingEffectsByTarget[targetID]

    def _StartEffect(self, effect, dogmaItem, environment, duration, repeat, byUser, checksOnly):
        effectID = effect.effectID
        self.effectCompiler.PreStartEffectChecks(effectID, environment)
        self.ConsumeResources(environment)
        itemKey = dogmaItem.itemID
        effectStart = blue.os.GetSimTime()
        environment.OnStart(effect, effectStart)
        if environment.startTime is None:
            environment.startTime = effectStart
        if checksOnly is None:
            targetID = environment.targetID
            flag = self.CheckApplyModifiers(environment.shipID, itemKey, effect, targetID, environment)
            if flag is not None:
                checksOnly = not flag
        if effect.preExpression:
            if checksOnly:
                self.effectCompiler.StartEffectChecks(effectID, environment)
            else:
                self.effectCompiler.StartEffect(effectID, environment)
            if effectID == const.effectOnline:
                try:
                    for onlineEffectID in self.dogmaStaticMgr.effectsByType[dogmaItem.typeID]:
                        if self.dogmaStaticMgr.effects[onlineEffectID].effectCategory != const.dgmEffOnline:
                            continue
                        try:
                            self.StartEffect(onlineEffectID, itemKey, environment, repeat, 0)
                        except UserError:
                            self.LogError('Failed to start online effect', onlineEffectID, effectID, itemKey)
                            sys.exc_clear()

                except KeyError:
                    self.LogWarn('Onlining item with no online effects', itemKey)

        return effectStart

    def ConsumeResources(self, environment):
        pass

    def GetEffectDuration(self, effect, environment):
        if effect.durationAttributeID:
            duration = self.GetAttributeValue(environment.itemID, effect.durationAttributeID)
            if duration < 0:
                self.FullyLogAttribute(environment.itemID, effect.durationAttributeID, '[EffectCantHaveNegativeDuration %s]' % effect.effectName, force=True)
                raise UserError('EffectCantHaveNegativeDuration', {'modulename': (const.UE_TYPEID, environment.itemTypeID),
                 'duration': duration})
            elif duration < 20:
                self.broker.LogInfo('Effect', effect.effectName, 'has very conspicuous short duration', duration)
        else:
            duration = -1
        return duration

    def RegisterEffect(self, effect, dogmaItem, environment, effectStart, duration, repeat):
        effectID = effect.effectID
        dogmaItem.RegisterEffect(effectID, environment.currentStartTime, duration, environment, repeat)
        if environment.shipID not in self.activeEffectsByShip:
            self.activeEffectsByShip[environment.shipID] = {effectID: dogmaItem.itemID}
        else:
            self.activeEffectsByShip[environment.shipID][effectID] = dogmaItem.itemID

    def StartEffect_PreChecks(self, effect, dogmaItem, environment, byUser):
        if byUser and effect.effectCategory in [const.dgmEffOnline, const.dgmEffOverload]:
            raise RuntimeError('TheseEffectsShouldNeverBeUserStarted', effect.effectID)
        if effect.effectID == const.effectOnline:
            moduleHp = self.GetAttributeValue(dogmaItem.itemID, const.attributeHp)
            moduleDamage = self.GetAttributeValue(dogmaItem.itemID, const.attributeDamage)
            if moduleHp <= moduleDamage:
                raise UserError('ModuleTooDamagedToBeOnlined')

    def CheckApplyModifiers(self, *args):
        pass

    @bluepy.TimedFunction('DogmaLocation::StopEffect')
    @telemetry.ZONE_METHOD
    def StopEffect(self, effectID, itemKey, byUser = False, activationInfo = None, forced = False, forceStopRepeating = False, possiblyStopRepeat = True):
        try:
            dogmaItem = self.dogmaItems[itemKey]
        except KeyError:
            self.LogInfo("StopEffect called on an item that isn't loaded", itemKey, effectID)
            return

        deactivateKey = (itemKey, effectID)
        if deactivateKey in self.deactivatingEffects:
            self.LogWarn('Multiple concurrent StopEffect calls for', deactivateKey)
            return
        self.deactivatingEffects.add(deactivateKey)
        try:
            if activationInfo is None:
                try:
                    activationInfo = dogmaItem.activeEffects[effectID]
                except KeyError:
                    if (itemKey, effectID) in self.activatingEffects:
                        raise UserError('EffectStillActivating', {'moduleName': (const.UE_TYPEID, dogmaItem.typeID)})
                    self.LogInfo("Stopping effect that isn't active", itemKey, effectID)
                    return 0

            if not self.PreStopEffectChecks(effectID, dogmaItem, activationInfo, forced, byUser, possiblyStopRepeat):
                return
            error = self._StopEffect(effectID, dogmaItem, activationInfo, byUser, forced, forceStopRepeating, possiblyStopRepeat)
            self.PostStopEffectAction(effectID, dogmaItem, activationInfo, forced, byUser, error)
        finally:
            self.deactivatingEffects.remove(deactivateKey)

    @telemetry.ZONE_METHOD
    def _StopEffect(self, effectID, dogmaItem, activationInfo, byUser, forced, forceStopRepeating, possiblyStopRepeat):
        if effectID in self.onlineEffects:
            effects = dogmaItem.activeEffects
            itemKey = dogmaItem.itemID
            for otherEffectID, activationInfo2 in effects.items():
                if otherEffectID != effectID and effects.has_key(otherEffectID):
                    otherDuration = effects[otherEffectID][const.ACT_IDX_DURATION]
                    if otherDuration == -1 and self.dogmaStaticMgr.effects[otherEffectID].effectCategory != const.dgmEffPassive:
                        self.StopEffect(otherEffectID, itemKey, False, activationInfo2)

        environment = activationInfo[const.ACT_IDX_ENV]
        self.effectCompiler.StopEffect(effectID, environment, forced)

    def PreStopEffectChecks(self, effectID, dogmaItem, activationInfo, forced, byUser, possiblyStopRepeat, *args):
        return True

    @telemetry.ZONE_METHOD
    def PostStopEffectAction(self, effectID, dogmaItem, activationInfo, forced, byUser, error):
        environment = activationInfo[const.ACT_IDX_ENV]
        if dogmaItem.IsEffectRegistered(effectID, environment):
            effect = self.dogmaStaticMgr.effects[effectID]
            self.UnregisterEffect(effect, dogmaItem, environment)

    def UnregisterEffect(self, effect, dogmaItem, environment):
        effectID = effect.effectID
        dogmaItem.UnregisterEffect(effectID, environment)
        shipID = environment.shipID
        try:
            del self.activeEffectsByShip[shipID][effectID]
            if len(self.activeEffectsByShip[shipID]) == 0:
                del self.activeEffectsByShip[shipID]
            if shipID in self.activeDungeonEffectsByItem:
                beaconID = environment.itemID
                if effectID in self.activeDungeonEffectsByItem[shipID]:
                    try:
                        self.activeDungeonEffectsByItem[shipID][effectID].remove(beaconID)
                    except ValueError:
                        pass

                    if len(self.activeDungeonEffectsByItem[shipID][effectID]) == 0:
                        del self.activeDungeonEffectsByItem[shipID][effectID]
                if len(self.activeDungeonEffectsByItem[shipID]) == 0:
                    del self.activeDungeonEffectsByItem[shipID]
        except KeyError:
            sys.exc_clear()

    @telemetry.ZONE_METHOD
    def StartPassiveEffects(self, itemID, typeID):
        effectIDList = self.dogmaStaticMgr.passiveFilteredEffectsByType.get(typeID, [])
        if not effectIDList:
            self.LogInfo('No effects to start for item %s of type %s' % (itemID, evetypes.GetName(typeID)))
            return
        dogmaItem = self.dogmaItems[itemID]
        brokerEffects = self.dogmaStaticMgr.effects
        pilotID = dogmaItem.GetPilot()
        shipID = dogmaItem.GetShip()
        sharedEnv = None
        effectsCompleted = set()
        effectID = None
        try:
            for effectID in effectIDList:
                if pilotID is None and self.effectCompiler.IsEffectCharacterModifier(effectID):
                    continue
                if shipID is None and self.effectCompiler.IsEffectShipModifier(effectID):
                    continue
                if effectID in dogmaItem.activeEffects:
                    env = self.GetActiveEffectEnvironment(itemID, effectID)
                    self.LogError('Item', itemID, '(', evetypes.GetName(self.dogmaItems[itemID].typeID), ')', 'already has effect', effectID, '(', cfg.dgmeffects.Get(effectID).effectName, ')', 'Started at: ', util.FmtDate(env.startTime), '(Now is ', util.FmtDate(blue.os.GetSimTime()), ')')
                    continue
                chanceAttributeID = brokerEffects[effectID].fittingUsageChanceAttributeID
                if chanceAttributeID and self.dogmaStaticMgr.TypeHasAttribute(typeID, chanceAttributeID):
                    if not self.ShouldStartChanceBasedEffect(effectID, itemID, chanceAttributeID):
                        continue
                if self.dogmaStaticMgr.effects[effectID].effectCategory == const.dgmEffSystem:
                    self.StartSystemEffect(itemID, effectID)
                    continue
                pythonEffect = self.effectCompiler.IsEffectPythonOverridden(effectID)
                if sharedEnv and not pythonEffect:
                    env = sharedEnv
                else:
                    with bluepy.Timer('LocationManager::Environment'):
                        info = dogmaItem.GetEnvironmentInfo()
                        env = Environment(itemID=info.itemID, charID=info.charID, shipID=info.shipID, targetID=None, otherID=info.otherID, effectID=effectID, dogmaLM=weakref.proxy(self), expressionID=None)
                    if sharedEnv is None and not pythonEffect:
                        sharedEnv = env
                if env.otherID is None and self.effectCompiler.IsEffectDomainOther(effectID):
                    continue
                try:
                    self.StartEffect(effectID, itemID, env)
                except UserError as e:
                    if not e.msg.startswith('EffectAlreadyActive'):
                        raise
                    sys.exc_clear()

                effectsCompleted.add(effectID)

        except Exception:
            log.LogException('Failed to start passive effect %s on %s class %s' % (effectID, itemID, dogmaItem.__class__))
            return effectsCompleted

    def ShouldStartChanceBasedEffect(self, effectID, itemID, chanceAttributeID):
        return False

    def GetActiveEffectEnvironment(self, itemKey, effectID):
        dogmaItem = self.dogmaItems[itemKey]
        if effectID not in dogmaItem.activeEffects:
            return None
        return dogmaItem.activeEffects[effectID][const.ACT_IDX_ENV]

    def GetEffect(self, effectID):
        return self.dogmaStaticMgr.effects[effectID]

    def GetSubLocation(self, locationID, flag):
        if not self.IsItemLoaded(locationID):
            raise RuntimeError('GetSubLocation called for unloaded location', locationID, flag)
        try:
            return self.dogmaItems[locationID].subLocations[flag]
        except (KeyError, AttributeError):
            return None

    def IsItemSubLocation(self, itemKey):
        return type(itemKey) is tuple

    def SetWeaponBanks(self, shipID, data):
        self.slaveModulesByMasterModule[shipID] = defaultdict(set)
        if data is None:
            return
        for masterID, slaveIDs in data.iteritems():
            for slaveID in slaveIDs:
                self.slaveModulesByMasterModule[shipID][masterID].add(slaveID)

    def GetMasterModuleID(self, shipID, slaveID):
        for masterID, slaves in self.slaveModulesByMasterModule.get(shipID, {}).iteritems():
            if slaveID in slaves:
                return masterID

    def GetSlaveModules(self, moduleID, shipID):
        if shipID in self.slaveModulesByMasterModule and moduleID in self.slaveModulesByMasterModule[shipID]:
            return self.slaveModulesByMasterModule[shipID][moduleID].copy()

    def IsModuleMaster(self, moduleID, shipID):
        return moduleID in self.slaveModulesByMasterModule.get(shipID, {})

    def IsModuleSlave(self, moduleID, shipID):
        return self.GetMasterModuleID(shipID, moduleID) is not None

    def GetAttributesForType(self, typeID):
        ret = {}
        for attribute in cfg.dgmtypeattribs.get(typeID, []):
            ret[attribute.attributeID] = attribute.value

        return ret

    @WrappedMethod
    def UnloadItem(self, itemKey, item = None):
        if itemKey in self.unloadingItems:
            self.LogInfo('Item already being unloaded', itemKey)
            return
        self.unloadingItems.add(itemKey)
        try:
            self._UnloadItem(itemKey, item)
        finally:
            self.unloadingItems.remove(itemKey)

    def _UnloadItem_LogOnEntry(self, itemKey, item):
        givenInvItemDescription = self.DescribeInvItem(item)
        foundDogmaItem = self.dogmaItems.get(itemKey, None)
        foundInvItemDescription = self.DescribeInvItem(foundDogmaItem.invItem) if foundDogmaItem else None
        totalItems = len(self.dogmaItems)
        LogNotice('UnloadItem requested for itemKey: {itemKey}, with given invItem {givenInvItemDescription}, having found dogmaItems entry {foundDogmaItem} with invItem {foundInvItemDescription} (totalItems = {totalItems}) '.format(**locals()))

    def _UnloadItem(self, itemKey, item):
        dogmaItem = self.dogmaItems.get(itemKey, None)
        if dogmaItem is not None:
            dogmaItem.Unload()
            self.RemoveItem(itemKey)
            self.LogInfo('_UnloadItem::Deleting dogmaItem', itemKey)
            del self.dogmaItems[itemKey]

    def RemoveSubLocationFromLocation(self, itemKey):
        locationID = itemKey[0]
        self.dogmaItems[locationID].RemoveSubLocation(itemKey)

    def GetClassForItem(self, item):
        if item.categoryID == const.categoryShip:
            return ShipDogmaItem
        elif item.groupID == const.groupCharacter:
            return CharacterDogmaItem
        elif item.groupID in (const.groupSurveyProbe,
         const.groupWarpDisruptionProbe,
         const.groupScannerProbe,
         const.groupBomb,
         const.groupBombECM,
         const.groupBombEnergy):
            return ProbeDogmaItem
        elif item.categoryID == const.categoryCharge:
            return ChargeDogmaItem
        elif item.categoryID in (const.categoryModule, const.categorySubSystem):
            return ModuleDogmaItem
        elif item.groupID == const.groupControlTower:
            return ControlTowerDogmaItem
        elif item.categoryID == const.categoryStarbase:
            return StarbaseDogmaItem
        elif item.categoryID == const.categoryDrone:
            return DroneDogmaItem
        else:
            return BaseDogmaItem

    def GetInstance(self, item):
        return self.fakeInstanceRow

    def IntroduceNewItem(self, item):
        return self.fakeInstanceRow

    def IsItemWanted(self, typeID, groupID = None):
        return True

    def RemoveDroneFromLocation(self, shipID, droneID):
        dogmaItem = self.dogmaItems[shipID]
        dogmaItem.UnregisterDrone(droneID)

    def AddDroneToLocation(self, shipID, droneID):
        shipItem = self.dogmaItems[shipID]
        droneItem = self.dogmaItems[droneID]
        shipItem.RegisterDrone(droneItem)

    def IsDroneFitted(self, shipID, droneID):
        try:
            shipItem = self.dogmaItems[shipID]
            return droneID in shipItem.GetDronesInBay()
        except KeyError:
            return False

    def RegisterCallback(self, attributeID, cb):
        if isinstance(attributeID, str):
            attributeID = self.dogmaStaticMgr.attributesByName[attributeID].attributeID
        if attributeID in self.attributeChangeCallbacksByAttributeID:
            log.LogException('RegisterCallback::Overwriting a callback %s %s' % (attributeID, self.attributeChangeCallbacksByAttributeID[attributeID].func_name))
        self.attributeChangeCallbacksByAttributeID[attributeID] = cb

    def UnregisterCallback(self, attributeID):
        if isinstance(attributeID, str):
            attributeID = self.dogmaStaticMgr.attributesByName[attributeID].attributeID
        if attributeID in self.attributeChangeCallbacksByAttributeID:
            del self.attributeChangeCallbacksByAttributeID[attributeID]

    def OnCpuAttributeChanged(self, attributeID, itemID, newValue, oldValue = None):
        self.OnFittingChanged(itemID, const.attributeCpuLoad, const.attributeCpuOutput)

    def OnPowerAttributeChanged(self, attributeID, itemID, newValue, oldValue = None):
        self.OnFittingChanged(itemID, const.attributePowerLoad, const.attributePowerOutput)

    def OnFittingChanged(self, itemID, loadAttributeID, outputAttributeID):
        if isinstance(itemID, tuple):
            return
        if itemID not in self.pilotsByShipID:
            return
        if getattr(self.dogmaItems[itemID], 'isBeingDisembarked', False):
            return
        load = self.GetAttributeValue(itemID, loadAttributeID)
        output = self.GetAttributeValue(itemID, outputAttributeID)
        if output - load < 1e-07:
            self.CheckShipOnlineModules(itemID)

    def CheckShipOnlineModules(self, shipID):
        if self.brainUpdate.IsEventHappening(shipID):
            return
        try:
            self.checkShipOnlineModulesPending.remove(shipID)
        except KeyError:
            pass

        if self.IsItemLoading(shipID):
            return
        if self.broker is None:
            return
        if not self.IsShipLoaded(shipID):
            return
        if shipID in self.unloadingItems:
            return
        dogmaItem = self.dogmaItems[shipID]
        if dogmaItem.categoryID != const.categoryShip:
            return
        powerLoad = self.GetAttributeValue(shipID, const.attributePowerLoad)
        powerOutput = self.GetAttributeValue(shipID, const.attributePowerOutput)
        cpuLoad = self.GetAttributeValue(shipID, const.attributeCpuLoad)
        cpuOutput = self.GetAttributeValue(shipID, const.attributeCpuOutput)
        powerUsage = powerLoad / max(powerOutput, 1e-07)
        cpuUsage = cpuLoad / max(cpuOutput, 1e-07)
        if powerUsage > 1.0 and (cpuUsage <= 1.0 or cpuUsage > 1.0 and powerUsage > cpuUsage):
            candidates = []
            if self.IsShipLoaded(shipID):
                for moduleID, moduleDogmaItem in dogmaItem.GetFittedItems().iteritems():
                    if (moduleID, const.effectOnline) in self.deactivatingEffects:
                        continue
                    if not moduleDogmaItem.IsOnline():
                        continue
                    used = self.GetAttributeValue(moduleID, const.attributePower)
                    if used:
                        candidates.append((used, moduleID))

            self.broker.LogInfo('CheckShipOnlineModules', shipID, 'powerUsage', powerUsage, 'cpuUsage', cpuUsage)
            if len(candidates):
                mc = max(candidates)
                itemKey = mc[1]
                if (itemKey, const.effectOnline) in self.deactivatingEffects:
                    self.broker.LogInfo('Low on power, already taking module offline so skipping', mc)
                else:
                    self.broker.LogInfo('Low on power, taking module offline', mc)
                    self.OfflineModule(itemKey)
            else:
                self.broker.LogError('The ship', shipID, "has something modifying it's powerLoad that isn't an online effect")
        elif cpuUsage > 1.0:
            candidates = []
            if self.IsShipLoaded(shipID):
                for moduleID, moduleDogmaItem in dogmaItem.GetFittedItems().iteritems():
                    if (moduleID, const.effectOnline) in self.deactivatingEffects:
                        continue
                    if not moduleDogmaItem.IsOnline():
                        continue
                    used = self.GetAttributeValue(moduleID, const.attributeCpu)
                    if used > 0:
                        candidates.append((used, moduleID))

            self.broker.LogInfo('CheckShipOnlineModules', shipID, 'powerUsage', powerUsage, 'cpuUsage', cpuUsage)
            if len(candidates):
                mc = max(candidates)
                itemKey = mc[1]
                if (itemKey, const.effectOnline) in self.deactivatingEffects:
                    self.broker.LogInfo('Low on cpu, already taking module offline so skipping', mc)
                else:
                    self.broker.LogInfo('Low on cpu, taking module offline', mc)
                    self.OfflineModule(itemKey)
            else:
                self.broker.LogError('The ship', shipID, "has something modifying it's cpuLoad that isn't an online effect")

    def OfflineModule(self, moduleID):
        self.StopEffect(const.effectOnline, moduleID)

    def FitItemToSelf(self, item):
        self.OnItemAddedToLocation(item.itemID, item, shipid=item.itemID)

    def GetCharacter(self, itemID, flush = False):
        pass

    def LoadSublocations(self, itemID):
        for flagID, sublocation in self.instanceFlagQuantityCache.get(itemID, {}).iteritems():
            self.LoadItem((sublocation[0], sublocation[1], sublocation[2]))

    def GetAttributesByIndex(self):
        return const.dgmAttributesByIdx

    def LoadItemsInLocation(self, itemID):
        pass

    def UnloadItemsInLocation(self, locationID):
        pass

    def GetItem(self, itemID):
        pass

    def OnSublocationAddedToLocation(self, itemKey, shipid = None, pilotID = None, fitting = False, locationName = None, timerName = 'AddUnknown2'):
        pass

    def OnItemAddedToLocation(self, locationid, item, shipid = None, pilotID = None, fitting = False, locationName = None, timerName = 'AddUnknown1', byUser = False):
        pass

    def GetAttributeValue(self, itemKey, attributeID):
        return self.dogmaItems[itemKey].attributes[attributeID].GetValue()

    def GetAttributeDictForItem(self, itemKey):
        try:
            item = self.dogmaItems[itemKey]
        except KeyError:
            return {}

        return {attribID:item.attributes[attribID].GetValue() for attribID in item.attributes}

    def SetAttributeValue(self, itemKey, attributeID, value, dirty = True, keepLists = True):
        value, v, dirty = self._SetAttributeValue(itemKey, attributeID, value, dirty, keepLists)
        return value

    def _SetAttributeValue(self, itemKey, attributeID, value, dirty, keepLists):
        if itemKey not in self.dogmaItems:
            self.broker.LogInfo('Item', itemKey, 'not loaded')
            return (0, 0, False)
        dogmaAttribute = self.dogmaItems[itemKey].attributes[attributeID]
        oldValue = dogmaAttribute.GetValue()
        if oldValue == value:
            dirty = False
        if value is None:
            log.LogTraceback('Tried to set attributesByItemAttribute[%s][%s] to None' % (itemKey, attributeID), channel='svc.dogmaIM')
            return (0, 0, False)
        dogmaAttribute.SetBaseValue(value)
        if itemKey in self.dogmaItems:
            self.OnAttributeChanged(attributeID, itemKey, value, oldValue)
        return (value, oldValue, dirty)

    def OnDamageAttributeChange(attributeID, itemKey, value, v):
        pass

    @telemetry.ZONE_METHOD
    def OnAttributeChanged(self, attributeID, itemKey, value = None, oldValue = None):
        attrObj = self.dogmaItems[itemKey].attributes[attributeID]
        if value is None:
            value = attrObj.GetValue()
        for _opIdx, dependantAttrObj in attrObj.GetOutgoingModifiers():
            try:
                if dependantAttrObj.item is None:
                    continue
                affectedItemID = dependantAttrObj.item.itemID
                affectedAttributeID = dependantAttrObj.attribID
                if affectedItemID not in self.unloadingItems and affectedItemID in self.dogmaItems:
                    self.OnAttributeChanged(affectedAttributeID, affectedItemID)
            except ReferenceError:
                self.LogError("BaseDogmaLocation::OnAttributeChanged: 'Orphan' Attribute detected as dependantAttrObj:", dependantAttrObj, '..via attrObj:', attrObj)
                dependantAttrObj.CheckIntegrity()
                LogTraceback()

        return value

    def GetDamageStateEx(self, itemID, ownerID = None):
        if itemID in self.failedLoadingItems:
            return None
        if itemID not in self.dogmaItems:
            return None
        dogmaItem = self.dogmaItems[itemID]
        if isinstance(dogmaItem, NotWantedDogmaItem):
            return None
        if ownerID and dogmaItem.ownerID != ownerID:
            return None
        ret = []
        v = dogmaItem.attributes[const.attributeShieldCharge].GetFullChargedInfo()
        if v[1] > 0:
            ret.append((v[0] / v[1], v[2], blue.os.GetSimTime()))
        else:
            ret.append(v[0])
        hpAttribute = const.attributeArmorHP
        damageAttribute = const.attributeArmorDamage
        maxDamage = dogmaItem.attributes[hpAttribute].GetValue()
        if maxDamage == 0:
            ret.append(0.0)
        else:
            ret.append(1.0 - dogmaItem.attributes[damageAttribute].GetValue() / maxDamage)
        maxDamage = dogmaItem.attributes[const.attributeHp].GetValue()
        if maxDamage == 0:
            ret.append(0.0)
        else:
            ret.append(1.0 - dogmaItem.attributes[const.attributeDamage].GetValue() / maxDamage)
        return ret

    def IsItemLoaded(self, itemID):
        return itemID not in self.loadingItems and itemID in self.dogmaItems

    def IsItemLoading(self, itemID):
        return itemID in self.loadingItems

    def IsItemUnloading(self, itemKey):
        return itemKey in self.unloadingItems

    def IsShipLoaded(self, shipID):
        dogmaItem = self.dogmaItems.get(shipID, None)
        if dogmaItem is None:
            return False
        else:
            return dogmaItem.categoryID == const.categoryShip

    def DescribeInvItem(self, invItem):
        if invItem is None:
            return 'None'
        try:
            invItemCategoryName = evetypes.GetCategoryNameByCategory(invItem.categoryID)
            invItemGroupName = evetypes.GetGroupNameByGroup(invItem.groupID)
            invItemTypeName = evetypes.GetName(invItem.typeID)
            invItemID = invItem.itemID
            return "'{invItemCategoryName}/{invItemGroupName}/{invItemTypeName}' {invItemID}".format(**locals())
        except:
            return '[failed to describe invItem: {}]'.format(invItem)

    def DescribeAttrOnItem(self, attribID, itemID):
        attributeName = cfg.dgmattribs[attribID].attributeName
        try:
            dogmaItem = self.dogmaItems[itemID]
            attribute = dogmaItem.attributes[attribID]
            return str(attribute)
        except:
            return "[failed to describe '{attributeName}' on (unloaded?) itemID: {itemID}]".format(**locals())

    def DescribeModifier(self, op, fromItemID, fromAttribID, toItemID, toAttribID):
        src = self.DescribeAttrOnItem(fromAttribID, fromItemID)
        dest = self.DescribeAttrOnItem(toAttribID, toItemID)
        return 'Op: {op}, From: {src}, To: {dest}'.format(**locals())

    def _GenericAddModifier(self, operation, toItem, toAttribID, fromAttrib):
        toAttrib = toItem.attributes[toAttribID]
        oldValue = toAttrib.GetValue()
        fromAttrib.AddModifierTo(operation, toAttrib)
        self.OnAttributeChanged(toAttribID, toItem.itemID, oldValue=oldValue)

    def _GenericRemoveModifier(self, operation, toItem, toAttribID, fromAttrib, weirdSpecialCase = False):
        toAttrib = toItem.attributes[toAttribID]
        oldValue = toAttrib.GetValue()
        fromAttrib.RemoveModifierTo(operation, toAttrib)
        if weirdSpecialCase:
            toItemID = toItem.itemID
            if not self.IsItemUnloading(toItemID) and oldValue is not None:
                self.OnAttributeChanged(toAttribID, toItemID, oldValue=oldValue)
        else:
            self.OnAttributeChanged(toAttribID, toItem.itemID, oldValue=oldValue)

    def _FindOrDefer(self, itemID, deferFunc, *deferArgs):
        try:
            targetItem = self.dogmaItems[itemID]
            return targetItem
        except KeyError:
            LogNotice("_FindOrDefer: Couldn't find `itemID` {} when trying to Add a Modifier; maybe it hasn't loaded yet (or was recently unloaded?); deferring work: ...\n    `deferFunc` = {}\n    `deferArgs` = {}\n    alreadyPending = {}\n".format(itemID, deferFunc, deferArgs, self.modifiersAwaitingTarget[itemID]))
            self.modifiersAwaitingTarget[itemID].add((deferFunc,) + deferArgs)
            return None

    def _FindOrAbandon(self, itemID, deferFunc, *deferArgs):
        try:
            targetItem = self.dogmaItems[itemID]
            return targetItem
        except KeyError:
            try:
                self.modifiersAwaitingTarget[itemID].remove((deferFunc,) + deferArgs)
            except KeyError:
                pass

            return None

    def _Add(self, theDict, index, toAdd, debugStr = '<none>'):
        try:
            innerContainer = theDict[index]
            if toAdd in innerContainer:
                LogTraceback('_Add: item `toAdd` already present in `theDict` at the given `index`')
            innerContainer.add(toAdd)
        except KeyError:
            LogTraceback('_Add: no innerContainer found at the given `index`.')

    def _RemoveAndCleanup(self, theDict, index, toRemove, debugStr = '<none>'):
        try:
            innerContainer = theDict[index]
            try:
                innerContainer.remove(toRemove)
            except KeyError:
                LogTraceback('_RemoveAndCleanup: item `toRemove` not found in `theDict` at the given `index`')

            if not theDict[index]:
                del theDict[index]
        except KeyError:
            LogTraceback('_RemoveAndCleanup: no innerContainer found at the given `index`')

    def _Add_2D(self, theDict, index1, index2, toAdd, debugStr = '<none>'):
        try:
            innerContainer = theDict[index1][index2]
            if toAdd in innerContainer:
                LogWarn('_Add_2D: item `toAdd` already present in `theDict` at the given indices')
            innerContainer.add(toAdd)
        except KeyError:
            LogTraceback('_Add_2D: no innerContainer found at the given indices.')

    def _RemoveAndCleanup_2D(self, theDict, index1, index2, toRemove, debugStr = '<none>'):
        try:
            innerContainer = theDict[index1][index2]
            try:
                innerContainer.remove(toRemove)
            except KeyError:
                LogWarn('_RemoveAndCleanup_2D: item `toRemove` not found in `theDict` at the given indices')

            if not theDict[index1][index2]:
                del theDict[index1][index2]
            if not theDict[index1]:
                del theDict[index1]
        except KeyError:
            LogTraceback('_RemoveAndCleanup_2D: no innerContainer found at the given indices.')

    def LogMod(self, action, op, fromAttrib, *otherArgs):
        pass

    @telemetry.ZONE_METHOD
    def AddModifier(self, operation, toItemID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddModifierWithSource(operation, toItemID, toAttribID, fromAttrib)

    def AddModifierWithSource(self, operation, toItemID, toAttribID, fromAttrib):
        self.LogMod('+Mod:', operation, fromAttrib, self.DescribeAttrOnItem(toAttribID, toItemID))
        if not toItemID or not fromAttrib:
            raise RuntimeError('Item missing from AddModifier')
        toItem = self._FindOrDefer(toItemID, self.AddModifierWithSource, operation, toItemID, toAttribID, fromAttrib)
        if not toItem:
            return
        self._GenericAddModifier(operation, toItem, toAttribID, fromAttrib)

    @telemetry.ZONE_METHOD
    def RemoveModifier(self, operation, toItemID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveModifierWithSource(operation, toItemID, toAttribID, fromAttrib)

    def RemoveModifierWithSource(self, operation, toItemID, toAttribID, fromAttrib):
        self.LogMod('-Mod:', operation, fromAttrib, self.DescribeAttrOnItem(toAttribID, toItemID))
        if not toItemID or not fromAttrib:
            return
        toItem = self._FindOrAbandon(toItemID, self.AddModifierWithSource, operation, toItemID, toAttribID, fromAttrib)
        if not toItem:
            return
        self._GenericRemoveModifier(operation, toItem, toAttribID, fromAttrib, weirdSpecialCase=True)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def AddLocationModifier(self, operation, toLocationID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddLocationModifierWithSource(operation, toLocationID, toAttribID, fromAttrib)

    def AddLocationModifierWithSource(self, operation, toLocationID, toAttribID, fromAttrib):
        self.LogMod('+LocationMod:', operation, fromAttrib, toLocationID)
        if not toLocationID:
            raise RuntimeError('Item missing from AddLocationModifier')
        toLocation = self._FindOrDefer(toLocationID, self.AddLocationModifierWithSource, operation, toLocationID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._Add(toLocation.locationMods, toAttribID, (operation, fromAttrib), debugStr='LocMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: toAttribID in i.attributes, toLocation.subItems):
            self._GenericAddModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def RemoveLocationModifier(self, operation, toLocationID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveLocationModifierWithSource(operation, toLocationID, toAttribID, fromAttrib)

    def RemoveLocationModifierWithSource(self, operation, toLocationID, toAttribID, fromAttrib):
        self.LogMod('-LocationMod:', operation, fromAttrib, toLocationID)
        if not toLocationID:
            return
        toLocation = self._FindOrAbandon(toLocationID, self.AddLocationModifierWithSource, operation, toLocationID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._RemoveAndCleanup(toLocation.locationMods, toAttribID, (operation, fromAttrib), debugStr='LocMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: toAttribID in i.attributes, toLocation.subItems):
            self._GenericRemoveModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def AddLocationGroupModifier(self, operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddLocationGroupModifierWithSource(operation, toLocationID, groupID, toAttribID, fromAttrib)

    def AddLocationGroupModifierWithSource(self, operation, toLocationID, groupID, toAttribID, fromAttrib):
        self.LogMod('+LocationGroupMod:', operation, fromAttrib, toLocationID, groupID)
        if not toLocationID:
            raise RuntimeError('Item missing from AddLocationGroupModifier')
        toLocation = self._FindOrDefer(toLocationID, self.AddLocationGroupModifierWithSource, operation, toLocationID, groupID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._Add_2D(toLocation.locationGroupMods, groupID, toAttribID, (operation, fromAttrib), debugStr='LocGrpMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: i.invItem.groupID == groupID and toAttribID in i.attributes, toLocation.subItems):
            self._GenericAddModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def RemoveLocationGroupModifier(self, operation, toLocationID, groupID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveLocationGroupModifierWithSource(operation, toLocationID, groupID, toAttribID, fromAttrib)

    def RemoveLocationGroupModifierWithSource(self, operation, toLocationID, groupID, toAttribID, fromAttrib):
        self.LogMod('-LocationGroupMod:', operation, fromAttrib, toLocationID, groupID)
        if not toLocationID:
            return
        toLocation = self._FindOrAbandon(toLocationID, self.AddLocationGroupModifierWithSource, operation, toLocationID, groupID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._RemoveAndCleanup_2D(toLocation.locationGroupMods, groupID, toAttribID, (operation, fromAttrib), debugStr='LocGrpMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: i.invItem.groupID == groupID and toAttribID in i.attributes, toLocation.subItems):
            self._GenericRemoveModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def AddLocationRequiredSkillModifier(self, operation, toLocationID, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddLocationRequiredSkillModifierWithSource(operation, toLocationID, skillID, toAttribID, fromAttrib)

    def AddLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib):
        self.LogMod('+LocationRequiredSkillMod:', operation, fromAttrib, toLocationID, skillID)
        if not toLocationID:
            raise RuntimeError('Item missing from AddLocationRequiredSkillModifier')
        toLocation = self._FindOrDefer(toLocationID, self.AddLocationRequiredSkillModifierWithSource, operation, toLocationID, skillID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._Add_2D(toLocation.locationReqSkillMods, skillID, toAttribID, (operation, fromAttrib), debugStr='LocReqSkillMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: skillID in i.reqSkills and toAttribID in i.attributes, toLocation.subItems):
            self._GenericAddModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def RemoveLocationRequiredSkillModifier(self, operation, toLocationID, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveLocationRequiredSkillModifierWithSource(operation, toLocationID, skillID, toAttribID, fromAttrib)

    def RemoveLocationRequiredSkillModifierWithSource(self, operation, toLocationID, skillID, toAttribID, fromAttrib):
        self.LogMod('-LocationRequiredSkillMod:', operation, fromAttrib, toLocationID, skillID)
        if not toLocationID:
            return
        toLocation = self._FindOrAbandon(toLocationID, self.AddLocationRequiredSkillModifierWithSource, operation, toLocationID, skillID, toAttribID, fromAttrib)
        if not toLocation:
            return
        self._RemoveAndCleanup_2D(toLocation.locationReqSkillMods, skillID, toAttribID, (operation, fromAttrib), debugStr='LocReqSkillMod for Location {}'.format(toLocation))
        for toItem in filter(lambda i: skillID in i.reqSkills and toAttribID in i.attributes, toLocation.subItems):
            self._GenericRemoveModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def AddOwnerRequiredSkillModifier(self, operation, ownerID, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddOwnerRequiredSkillModifierWithSource(operation, ownerID, skillID, toAttribID, fromAttrib)

    def AddOwnerRequiredSkillModifierWithSource(self, operation, ownerID, skillID, toAttribID, fromAttrib):
        self.LogMod('+OwnerRequiredSkillMod:', operation, fromAttrib, ownerID, skillID)
        if not ownerID:
            return
        toOwner = self._FindOrDefer(ownerID, self.AddOwnerRequiredSkillModifierWithSource, operation, ownerID, skillID, toAttribID, fromAttrib)
        if not toOwner:
            return
        self._Add_2D(toOwner.ownerReqSkillMods, skillID, toAttribID, (operation, fromAttrib), debugStr='OwnerReqSkillMod for Owner {}'.format(toOwner))
        modItems = filter(lambda i: skillID in i.reqSkills and toAttribID in i.attributes, toOwner.GetOwnedItemsToModify())
        for toItem in modItems:
            self._GenericAddModifier(operation, toItem, toAttribID, fromAttrib)

    @WrappedMethod
    @telemetry.ZONE_METHOD
    def RemoveOwnerRequiredSkillModifier(self, operation, ownerID, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveOwnerRequiredSkillModifierWithSource(operation, ownerID, skillID, toAttribID, fromAttrib)

    def RemoveOwnerRequiredSkillModifierWithSource(self, operation, ownerID, skillID, toAttribID, fromAttrib):
        self.LogMod('-OwnerRequiredSkillMod:', operation, fromAttrib, ownerID, skillID)
        if not ownerID:
            return
        toOwner = self._FindOrAbandon(ownerID, self.AddOwnerRequiredSkillModifierWithSource, operation, ownerID, skillID, toAttribID, fromAttrib)
        if not toOwner:
            return
        self._RemoveAndCleanup_2D(toOwner.ownerReqSkillMods, skillID, toAttribID, (operation, fromAttrib), debugStr='OwnerReqSkillMod for Owner {}'.format(toOwner))
        modItems = filter(lambda i: skillID in i.reqSkills and toAttribID in i.attributes, toOwner.GetOwnedItemsToModify())
        for toItem in modItems:
            self._GenericRemoveModifier(operation, toItem, toAttribID, fromAttrib)

    def AddGangRequiredSkillModifier(self, shipID, op, skillID, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.AddGangRequiredSkillModifierWithSource(shipID, op, skillID, attributeID, affectingAttribute)

    def AddGangRequiredSkillModifierWithSource(self, shipID, op, skillID, attributeID, affectingAttribute):
        pass

    def RemoveGangRequiredSkillModifier(self, shipID, op, skillID, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.RemoveGangRequiredSkillModifierWithSource(shipID, op, skillID, attributeID, affectingAttribute)

    def RemoveGangRequiredSkillModifierWithSource(self, shipID, op, skillID, attributeID, affectingAttribute):
        pass

    def AddGangShipModifier(self, shipID, op, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.AddGangShipModifierWithSource(shipID, op, attributeID, affectingAttribute)

    def AddGangShipModifierWithSource(self, shipID, op, attributeID, affectingAttribute):
        pass

    def RemoveGangShipModifier(self, shipID, op, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.RemoveGangShipModifierWithSource(shipID, op, attributeID, affectingAttribute)

    def RemoveGangShipModifierWithSource(self, shipID, op, attributeID, affectingAttribute):
        pass

    def AddGangGroupModifier(self, shipID, op, groupID, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.AddGangGroupModifierWithSource(shipID, op, groupID, attributeID, affectingAttribute)

    def AddGangGroupModifierWithSource(self, shipID, op, groupID, attributeID, affectingAttribute):
        pass

    def RemoveGangGroupModifier(self, shipID, op, groupID, attributeID, itemID, affectingAttributeID):
        affectingAttribute = self.dogmaItems[itemID].attributes[affectingAttributeID]
        self.RemoveGangGroupModifierWithSource(shipID, op, groupID, attributeID, affectingAttribute)

    def RemoveGangGroupModifierWithSource(self, shipID, op, groupID, attributeID, affectingAttribute):
        pass

    @telemetry.ZONE_METHOD
    def RemoveItem(self, itemID):
        self.dogmaItems[itemID].FlushAllModifiers()

    @telemetry.ZONE_METHOD
    def DescribeModifierGraphForDebugWindow(self, itemID, attributeID):
        try:
            itemAttributes = self.dogmaItems[itemID].attributes
            if attributeID in itemAttributes:
                attribRoot = itemAttributes[attributeID]
            else:
                return 'AttribID {} not found for ItemID {}'.format(attributeID, itemID)
        except:
            return 'ItemID {} not found in dogmaItems'.format(itemID)

        levels = defaultdict(list)

        def DescribeAttributeForDebugWindow(attrib):
            attribStr = attrib.friendlyStr()
            base = attrib.GetBaseValue()
            val = attrib.GetValue()
            attribDescription = '{attribStr}: base={base} val={val}'.format(**locals())
            return attribDescription

        def DescribeModifierForDebugWindow(operatorName, attrib, relationName = 'from'):
            attribDescription = DescribeAttributeForDebugWindow(attrib)
            modifierDescription = '   {operatorName} {relationName} {attribDescription}'.format(**locals())
            return modifierDescription

        def HarvestModifiers(curAttrib, curLevel, isIncoming):
            if isIncoming:
                direction, relationName, levelDelta = ('Incoming', 'from', -1)
                modifiers = curAttrib.GetIncomingModifiers()
            else:
                direction, relationName, levelDelta = 'Outgoing', 'to', +1
                modifiers = curAttrib.GetOutgoingModifiers()
            if not modifiers:
                return
            curAttribDescription = DescribeAttributeForDebugWindow(curAttrib)
            levels[curLevel].append('{} Mods for {}:'.format(direction, curAttribDescription))
            for opIdx, attrib in modifiers:
                opName = OpName(opIdx)
                levels[curLevel].append(DescribeModifierForDebugWindow(opName, attrib, relationName))
                HarvestModifiers(attrib, curLevel + levelDelta, isIncoming)

        rootInfo = 'Root at address {:#x}'.format(id(attribRoot))
        levels[0].append(rootInfo)
        levels[0].append(DescribeModifierForDebugWindow('Root', attribRoot, 'is'))
        HarvestModifiers(attribRoot, curLevel=-1, isIncoming=True)
        HarvestModifiers(attribRoot, curLevel=1, isIncoming=False)
        levels = sorted([ (level, strings) for level, strings in levels.iteritems() ])
        ret = '\n\n'.join([ 'Level %d:\n\n' % (level,) + '\n'.join(strings) for level, strings in levels ])
        return ret

    @telemetry.ZONE_METHOD
    def GetCharacterAttributeModifiers(self, itemID, attributeID):
        if itemID not in self.dogmaItems:
            return []
        modifierList = []
        modifiers = self.dogmaItems[itemID].attributes[attributeID].incomingModifiers
        if modifiers is None:
            return modifierList
        for operator, attribSet in enumerate(modifiers):
            operator -= const.dgmOperatorOffset
            for attrib in attribSet:
                modValue = attrib.GetValue()
                if modValue == 1.0 and operator in (const.dgmAssPostMul,
                 const.dgmAssPreMul,
                 const.dgmAssPostDiv,
                 const.dgmAssPreDiv):
                    continue
                if modValue == 0.0 and operator in (const.dgmAssPostPercent, const.dgmAssModAdd, const.dgmAssModSub):
                    continue
                modifierList.append((attrib.invItem.itemID,
                 attrib.invItem.typeID,
                 operator,
                 modValue))

        return modifierList

    def EnterCriticalSection(self, k, v):
        if (k, v) not in self.crits:
            self.crits[k, v] = uthread.CriticalSection((k, v))
        self.crits[k, v].acquire()

    def LeaveCriticalSection(self, k, v):
        self.crits[k, v].release()
        if (k, v) in self.crits and self.crits[k, v].IsCool():
            del self.crits[k, v]

    def FullyLogAttribute(self, itemID, attributeID, reason, force = 0):
        description = self.FullyDescribeAttribute(itemID, attributeID, reason, force)
        self.LogNotice(description)
        return description

    def FullyDescribeAttribute(self, itemID, attributeID, reason, force = 0):
        if type(attributeID) is str:
            attribute = self.dogmaStaticMgr.attributesByName[attributeID]
            attributeID = attribute.attributeID
        else:
            attribute = self.dogmaStaticMgr.attributes[attributeID]
        rep = ['Full description requested for attribute %s on item %s, reason: %s' % (attribute.attributeName, self.GetLocName(itemID), reason)]
        stackText = 'Stackable, ' if attribute.stackable else 'Not stackable, '
        stackText += 'higher value is better.' if attribute.highIsGood else 'lower value is better.'
        rep.append(stackText)
        val = self.QueryAttributeValue(itemID, attributeID)
        rep.append('Value:%s' % val)
        if self.IsItemSubLocation(itemID):
            locationID = itemID[0]
            typeID = itemID[2]
            groupID = evetypes.GetGroupID(typeID)
            _locationItem = self.broker.i2.GetItemMx(locationID)
            ownerID = _locationItem.ownerID
        elif itemID in self.dogmaItems:
            _dogmaItem = self.dogmaItems[itemID]
            if _dogmaItem.location is not None:
                locationID = _dogmaItem.location.itemID
            else:
                locationID = None
            typeID, groupID, ownerID = _dogmaItem.typeID, _dogmaItem.groupID, _dogmaItem.ownerID
        else:
            item = self.broker.i2.GetItemMx(itemID)
            locationID = item.locationID
            typeID, groupID, ownerID = item.typeID, item.groupID, item.ownerID
        oval = self.dogmaStaticMgr.GetTypeAttribute(typeID, attributeID, 'No idea!')
        rep.append('Original Value:%s' % oval)
        rep.append('Attribute modification graph:')
        rep.append('')
        modifierInfo = self.DescribeModifierGraphForDebugWindow(itemID, attributeID)
        rep.extend(modifierInfo.split('\n'))
        return rep

    def QueryAttributeValue(self, itemID, attributeID):
        try:
            val = self.GetAttributeValue(itemID, attributeID)
        except StandardError:
            val = '[No idea!]'
            sys.exc_clear()

        return val

    def QueryAllAttributesForItem(self, itemID):
        return self.GetAttributeDictForItem(itemID)

    def GetLocName(self, locid):
        dogmaItem = self.dogmaItems.get(locid, None)
        if dogmaItem is None:
            return 'Unknown Item'
        return evetypes.GetName(dogmaItem.typeID)

    def LogInfo(self, *args):
        return self.broker.LogInfo(self.locationID, *args)

    def LogNotice(self, *args):
        return self.broker.LogNotice(self.locationID, *args)

    def LogWarn(self, *args):
        return self.broker.LogWarn(self.locationID, *args)

    def LogError(self, *args):
        return self.broker.LogError(self.locationID, *args)

    def IsIgnoringOwnerEvents(self, ownerID):
        return self.ignoredOwnerEvents.IsEventHappening(ownerID)

    def SlotExists(self, shipID, flagID):
        attributeID = None
        if flagID in const.hiSlotFlags:
            attributeID = const.attributeHiSlots
            slotNumber = flagID - const.flagHiSlot0
        elif flagID in const.medSlotFlags:
            attributeID = const.attributeMedSlots
            slotNumber = flagID - const.flagMedSlot0
        elif flagID in const.loSlotFlags:
            attributeID = const.attributeLowSlots
            slotNumber = flagID - const.flagLoSlot0
        elif flagID in const.rigSlotFlags:
            attributeID = const.attributeRigSlots
            slotNumber = flagID - const.flagRigSlot0
        if attributeID is not None:
            totalSlots = self.GetAttributeValue(shipID, attributeID)
            if slotNumber >= totalSlots:
                return False
        return True

    def GetSublocations(self, shipID):
        ret = set()
        for subLocation in self.GetDogmaItem(shipID).subLocations.itervalues():
            ret.add(self.GetDogmaItem(subLocation))

        return ret

    def GetSlotOther(self, shipID, flagID):
        for item in self.dogmaItems[shipID].GetFittedItems().itervalues():
            if item.flagID == flagID and item.categoryID == const.categoryModule:
                return item.itemID

    @telemetry.ZONE_METHOD
    def CheckSkillRequirements(self, charID, skillID, errorMsgName):
        skillItem = self.dogmaItems[skillID]
        self.CheckSkillRequirementsForType(skillItem.typeID, errorMsgName)

    def CheckSkillRequirementsForType(self, typeID, errorMsgName):
        pass

    def ProcessBrainData(self, charID, brainData):
        brainVersion, grayMatter = brainData
        if grayMatter:
            charEffects, shipEffects = blue.marshal.Load(grayMatter)
            self.broker.LogInfo('Got a brain with', len(charEffects), 'char effects and', len(shipEffects), 'ship effects')
            brain = (brainVersion, charEffects, shipEffects)
            self.SetBrainData(charID, brain)

    def CanFitItemInSpace(self, charID, shipID, itemID):
        return True

    def CheckSlotOnliningAndExistence(self, shipID, moduleID):
        pass
