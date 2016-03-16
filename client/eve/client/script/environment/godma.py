#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\godma.py
from carbon.common.script.sys.row import Row
from eve.common.script.sys.rowset import FilterRowset, IndexRowset, IndexedRowLists, IndexedRows
from eve.client.script.util import godmarowset
from gametime import GetDurationInClient
import cPickle
import math
from inventorycommon.util import GetItemVolume, IsShipFittingFlag
import carbonui.const as uiconst
import service
import blue
import util
import dbutil
import uthread
import moniker
import random
import sys
from timerstuff import ClockThis
import inventoryFlagsCommon
import log
import numbers
import telemetry
import evetypes
MODULE_NOT_OVERLOADED = 0
MODULE_OVERLOADED = 1
MODULE_PENDING_OVERLOADING = 2
MODULE_PENDING_STOPOVERLOADING = 3

def remDups(x, y):
    if x[-1] != y:
        x.append(y)
    return x


class Godma(service.Service):
    __guid__ = 'svc.godma'
    __exportedcalls__ = {'GetItem': {'role': service.ROLE_ANY,
                 'fastcall': 1},
     'GetType': {'role': service.ROLE_ANY,
                 'fastcall': 1},
     'GetStateManager': [service.ROLE_ANY],
     'LogAttributeViaGodma': [service.ROLE_ANY],
     'GetDogmaLM': [service.ROLE_ANY]}
    __notifyevents__ = ['OnModuleAttributeChange',
     'OnModuleAttributeChanges',
     'OnGodmaShipEffect',
     'OnEffectMessage',
     'OnDamageMessage',
     'OnDamageMessages',
     'OnJamStart',
     'OnJamEnd',
     'OnMultiEvent',
     'ProcessGodmaPrimeLocation',
     'OnGodmaPrimeItem',
     'OnLocationAttributeChange',
     'OnGodmaEffectInfo',
     'OnGodmaFlushLocation',
     'OnGodmaFlushLocationProfile',
     'OnJumpCloneTransitionCompleted',
     'OnSystemEffectStarted',
     'OnChargeBeingLoadedToModule']
    __dependencies__ = ['invCache']
    __startupdependencies__ = ['settings']

    def Run(self, ms):
        self.stateManager = None
        if ms:
            ms.Seek(0)
            dump = ms.Read()
            if len(dump):
                number = cPickle.loads(str(dump))
                if number == 1:
                    self.GetStateManager().ProcessSessionChange(0, eve.session, {})
        sm.FavourMe(self.OnModuleAttributeChange)
        sm.FavourMe(self.OnModuleAttributeChanges)
        self.__itemrd = None
        self.__sublocrd = None
        self.__subloc_internalrd = None
        self.activeJams = set()
        self.michelle = None

    @property
    def itemrd(self):
        if self.__itemrd is None:
            self.__itemrd = sm.GetService('invCache').GetItemHeader()
        return self.__itemrd

    @property
    def sublocrd(self):
        if not self.__sublocrd:
            columns = []
            for key, dbtype, size in list(self.itemrd):
                if dbtype == 0 and size == 0:
                    continue
                if key == 'itemID':
                    columns.append(('itemID', const.DBTYPE_STR))
                else:
                    columns.append((key, dbtype))

            self.__sublocrd = blue.DBRowDescriptor(tuple(columns))
            self.__sublocrd.virtual = self.itemrd.virtual
        return self.__sublocrd

    @property
    def subloc_internalrd(self):
        if not self.__subloc_internalrd:
            columns = []
            for key, dbtype, size in list(self.itemrd):
                if dbtype == 0 and size == 0:
                    continue
                if key in ('quantity', 'customInfo'):
                    continue
                if key == 'itemID':
                    columns.append(('itemID', const.DBTYPE_STR))
                else:
                    columns.append((key, dbtype))

            self.__subloc_internalrd = blue.DBRowDescriptor(tuple(columns))
        return self.__subloc_internalrd

    def GetType(self, typeID):
        return self.GetStateManager().GetType(typeID)

    def TypeHasEffect(self, typeID, effectID):
        return self.GetStateManager().TypeHasEffect(typeID, effectID)

    def LogAttributeViaGodma(self, itemID, attributeID, reason = None):
        mask = service.ROLE_CONTENT | service.ROLE_QA | service.ROLE_PROGRAMMER | service.ROLE_GMH
        if eve.session.role & mask == 0:
            return
        return self.GetStateManager().LogAttributeViaStateManager(itemID, attributeID, reason)

    def Stop(self, ms):
        if ms is not None:
            ms.Write(cPickle.dumps(1))

    def OnJamStart(self, sourceBallID, moduleID, targetBallID, jammingType, startTime, duration):
        jamTuple = (sourceBallID,
         moduleID,
         targetBallID,
         jammingType)
        self.activeJams.add(jamTuple)
        uthread.new(self.StopJam, GetDurationInClient(startTime, duration), jamTuple)

    def StopJam(self, duration, jamTuple):
        blue.pyos.synchro.SleepSim(duration)
        if jamTuple in self.activeJams:
            self.activeJams.remove(jamTuple)
            sm.ScatterEvent('OnJamEnd', *jamTuple)

    def OnJamEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        try:
            self.activeJams.remove((sourceBallID,
             moduleID,
             targetBallID,
             jammingType))
        except KeyError:
            pass

    def OnMultiEvent(self, events):
        dmg = []
        attr = []
        target = []
        gsf = []
        gfl = []
        dastatedict = {'OnDamageMessage': dmg,
         'OnModuleAttributeChange': attr,
         'OnTarget': target,
         'OnGodmaShipEffect': gsf,
         'OnGodmaFlushLocation': gfl,
         'OnGodmaFlushLocationProfile': gfl,
         'OnJamStart': gfl,
         'OnJamStop': gfl}
        other = []
        for ev in events:
            dastatedict.get(ev[0], other).append(ev)

        laters = []
        for ev in other:
            if ev[0].startswith('Process'):
                laters.append(ev)
            else:
                sm.ScatterEvent(*ev)

        if len(gsf):
            self.BroadcastFilteredGSF(gsf)
        if dmg:
            sm.ScatterEvent(*('OnDamageMessages', dmg))
        if target:
            target = reduce(remDups, target, [target[0]])
            sm.ScatterEvent(*('OnTargets', target))
        if attr:
            self.BroadcastFilteredMAC(attr)
        for ev in gfl:
            sm.ScatterEvent(*ev)

        for ev in laters:
            sm.ChainEvent(*ev)

    def BroadcastFilteredGSF(self, gsf):
        gsf.sort(lambda x, y: cmp(x[3], y[3]))
        eventsByID = {}
        for line in gsf:
            k = (line[1], line[2])
            if not eventsByID.has_key(k):
                eventsByID[k] = []
            eventsByID[k].append(line)

        skipCount = 0
        sendCount = 0
        for k, lines in eventsByID.iteritems():
            skipCount += len(lines) - 1
            sm.ScatterEvent(*lines[-1])
            sendCount += 1

        self.LogInfo('BroadcastFilteredGSF', 'OnGodmaShipEffect - skips', skipCount, 'sends', sendCount)

    def BroadcastFilteredMAC(self, mac):
        mac.sort(lambda x, y: cmp(x[4], y[4]))
        eventsByID = {}
        for line in mac:
            k = (line[1], line[2], line[3])
            if not eventsByID.has_key(k):
                eventsByID[k] = []
            eventsByID[k].append(line)

        skipCount = 0
        result = []
        for k, lines in eventsByID.iteritems():
            skipCount += len(lines) - 1
            result.append(lines[-1])

        sm.ScatterEvent(*('OnModuleAttributeChanges', result))
        self.LogInfo('BroadcastFilteredMAC', 'OnModuleAttributeChanges - skips', skipCount, 'sends', len(result))

    def GetStateManager(self):
        if self.stateManager == None:
            self.stateManager = StateManager(self)
        return self.stateManager

    def ReleaseStateManager(self):
        if self.stateManager:
            self.stateManager.Release()
        self.stateManager = None

    def GetDogmaLM(self):
        return self.GetStateManager().GetDogmaLM()

    def GetItem(self, itemID):
        return self.GetStateManager().GetItem(itemID)

    def OnModuleAttributeChange(self, *args):
        self.GetStateManager().OnModuleAttributeChange(*args)

    def OnModuleAttributeChanges(self, changes):
        self.GetStateManager().OnModuleAttributeChanges(changes)

    def OnGodmaShipEffect(self, *args, **kwargs):
        self.GetStateManager().OnGodmaShipEffect(*args, **kwargs)

    def ProcessGodmaPrimeLocation(self, locationID, data):
        self.GetStateManager().ProcessGodmaPrimeLocation(locationID, data)

    def OnLocationAttributeChange(self, ownerID, locationID, itemKey, attributeID, t, value, oldValue):
        self.GetStateManager().OnLocationAttributeChange(ownerID, locationID, itemKey, attributeID, t, value, oldValue)

    def OnGodmaEffectInfo(self, *args, **kwargs):
        self.GetStateManager().OnGodmaEffectInfo(*args, **kwargs)

    def OnGodmaPrimeItem(self, locationID, row):
        stateMgr = self.GetStateManager()
        stateMgr.OnGodmaPrimeItem(locationID, row)
        if stateMgr.IsSubLocation(row.itemID):
            rd = self.sublocrd
            locationID, flag, typeID = row.itemID
            quantity = row.attributes[const.attributeQuantity]
            self.LogInfo('Godma:UpdateItem - QUANTITY', quantity)
            ownerID = None
            change = {const.ixLocationID: None,
             const.ixFlag: None}
        else:
            rd = self.itemrd
            flag = row.invItem.flagID
            typeID = row.invItem.typeID
            quantity = row.invItem.quantity
            ownerID = row.invItem.ownerID
            change = {}
        stackSize = max(1, quantity)
        item = blue.DBRow(rd, [row.itemID,
         typeID,
         ownerID,
         locationID,
         flag,
         quantity,
         evetypes.GetGroupID(typeID),
         evetypes.GetCategoryID(typeID),
         stackSize])
        sm.ScatterEvent('OnItemChange', item, change)

    def OnGodmaFlushLocation(self, locationID):
        self.GetStateManager().OnGodmaFlushLocation(locationID)

    def OnGodmaFlushLocationProfile(self, locationID, profileID):
        self.GetStateManager().OnGodmaFlushLocationProfile(locationID, profileID)

    @telemetry.ZONE_METHOD
    def DamageMessageGrouped(self, turretSets, hitQuality):
        if hitQuality <= 0:
            for t in turretSets:
                t.SetShotMissed(True)

        elif hitQuality >= 3:
            for t in turretSets:
                t.SetShotMissed(False)

        else:
            missPct = [0.5, 0.25][hitQuality - 1]
            for t in turretSets:
                t.SetShotMissed(random.random() < missPct)

    @telemetry.ZONE_METHOD
    def DamageMessageTurretPropogation(self, shipID, ship, hitQuality, args, banked):
        weaponID = args.get('weapon', 0)
        canGetBanks = banked and shipID == session.shipid
        if getattr(ship, 'modules', None):
            minQueue = None
            minTime = None
            minTimeID = None
            minTimeTurrets = []
            shotTimeVariance = 0.0
            for modID, module in ship.modules.iteritems():
                if hasattr(module, 'GetTurretSets'):
                    turretSets = module.GetTurretSets()
                    shooting = module.isShooting
                    targetMatch = shooting
                    shotTimeVariance = max(shotTimeVariance, turretSets[0].GetShotTimeVariance())
                    if shooting and args.has_key('target'):
                        targetMatch = module.targetID == args['target']
                    typeMatch = shooting
                    if shooting and weaponID is not 0:
                        typeMatch = module.turretTypeID == weaponID
                    if shooting and targetMatch and typeMatch:
                        queueSize = turretSets[0].MissQueueSize()
                        shotTime = turretSets[0].GetLastShotTime()
                        turretID = modID
                        if canGetBanks:
                            turretID = self.GetStateManager().dogmaLocation.IsInWeaponBank(shipID, modID) or modID
                            if turretID == minTimeID:
                                minTimeTurrets.append(module)
                            elif minQueue is None or queueSize < minQueue:
                                minQueue = queueSize
                                minTime = shotTime
                                minTimeID = turretID
                                minTimeTurrets = [module]
                            elif queueSize == minQueue and (minTime is None or shotTime < minTime):
                                minTime = shotTime
                                minTimeID = turretID
                                minTimeTurrets = [module]
                        elif banked:
                            if minTime is None or shotTime < minTime + shotTimeVariance:
                                if minTime is None:
                                    minTime = shotTime
                                else:
                                    minTime = min(shotTime, minTime)
                                minTimeID = turretID
                                minTimeTurrets.append(module)
                        elif minQueue is None or queueSize < minQueue:
                            minQueue = queueSize
                            minTime = shotTime
                            minTimeTurrets = [module]
                        elif queueSize == minQueue and (minTime is None or shotTime < minTime):
                            minTime = shotTime
                            minTimeTurrets = [module]

            allTurretSets = []
            for turret in minTimeTurrets:
                for turretSet in turret.GetTurretSets():
                    if canGetBanks or minTime + shotTimeVariance >= turretSet.GetLastShotTime():
                        allTurretSets.append(turretSet)

            self.DamageMessageGrouped(allTurretSets, hitQuality)

    @telemetry.ZONE_METHOD
    def OnDamageMessage(self, damageMessagesArgs):
        if self.michelle is None:
            self.michelle = sm.GetService('michelle')
        try:
            hitQuality = damageMessagesArgs.get('hitQuality', 5)
            banked = damageMessagesArgs.get('isBanked', False)
            if 'observed' in damageMessagesArgs:
                sourceID = damageMessagesArgs['source']
                ship = self.michelle.GetBall(sourceID)
                if sourceID and ship:
                    self.DamageMessageTurretPropogation(sourceID, ship, hitQuality, damageMessagesArgs, banked)
            elif 'target' in damageMessagesArgs:
                ship = self.michelle.GetBall(session.shipid)
                if ship and hasattr(ship, 'turrets'):
                    self.DamageMessageTurretPropogation(session.shipid, ship, hitQuality, damageMessagesArgs, banked)
            elif 'owner' in damageMessagesArgs:
                ownerData, ownerID = damageMessagesArgs['owner']
                if ownerData == const.UE_OWNERID:
                    targetSvc = sm.GetService('target')
                    ship = None
                    shipID = targetSvc.ownerToShipIDCache.get(ownerID, None)
                    if shipID is not None:
                        ship = self.michelle.GetBall(shipID)
                    if shipID and ship:
                        self.DamageMessageTurretPropogation(shipID, ship, hitQuality, damageMessagesArgs, banked)
            elif 'source' in damageMessagesArgs:
                shipID = damageMessagesArgs['source']
                ship = self.michelle.GetBall(shipID)
                if hasattr(ship, 'turrets'):
                    self.DamageMessageTurretPropogation(shipID, ship, hitQuality, damageMessagesArgs, banked)
                elif hasattr(ship, 'model') and hasattr(ship.model, 'turretSets'):
                    self.DamageMessageGrouped(ship.model.turretSets, hitQuality)
        except:
            log.LogException('Error setting hit/miss state on a turret')

        if not settings.user.ui.Get('damageMessages', 1):
            return
        if 'damage' in damageMessagesArgs and damageMessagesArgs['damage'] == 0.0 and not settings.user.ui.Get('damageMessagesNoDamage', 1):
            return
        if 'owner' in damageMessagesArgs or 'source' in damageMessagesArgs:
            sm.ScatterEvent('OnShipDamage', damageMessagesArgs.get('damageTypes', {}))
            if not settings.user.ui.Get('damageMessagesEnemy', 1):
                return
        elif not settings.user.ui.Get('damageMessagesMine', 1):
            return
        sm.GetService('logger').AddCombatMessageFromDict(damageMessagesArgs)

    @telemetry.ZONE_METHOD
    def OnDamageMessages(self, dmgmsgs):
        if not settings.user.ui.Get('damageMessages', 1):
            return
        for msg in dmgmsgs:
            self.OnDamageMessage(*msg[1:])

    def OnEffectMessage(self, msgkey, args):
        msg = cfg.GetMessage(msgkey, args)
        sm.GetService('gameui').Say(msg.text)

    def ProcessSessionChange(self, isRemote, session, change):
        self.GetStateManager().ProcessSessionChange(isRemote, session, change)

    def OnItemChange(self, *args):
        try:
            self.GetStateManager().OnItemChange(*args)
        finally:
            sm.GetService('clientDogmaIM').GodmaItemChanged(*args)

    def OnChargeBeingLoadedToModule(self, itemIDs, chargeTypeID, time):
        if self.stateManager:
            self.stateManager.OnChargeBeingLoadedToModule(itemIDs, chargeTypeID, time)

    def OverloadRack(self, moduleID):
        if moduleID is None:
            return
        if self.stateManager:
            self.stateManager.OverloadRack(moduleID)

    def StopOverloadRack(self, moduleID):
        if self.stateManager:
            self.stateManager.StopOverloadRack(moduleID)

    def OnJumpCloneTransitionCompleted(self):
        if self.stateManager:
            self.stateManager.OnJumpCloneTransitionCompleted()

    def GetTypeAttribute(self, typeID, attributeID, defaultValue = None):
        if cfg.dgmtypeattribs.has_key(typeID):
            for r in cfg.dgmtypeattribs[typeID]:
                if r.attributeID == attributeID:
                    return r.value

        return defaultValue

    def GetTypeAttribute2(self, typeID, attributeID):
        val = self.GetTypeAttribute(typeID, attributeID)
        if val is None and attributeID in cfg.dgmattribs:
            val = cfg.dgmattribs.Get(attributeID).defaultValue
        return val

    def CheckSkillRequirementsForType(self, typeID):
        skillSvc = sm.StartService('skills')
        requiredSkills = skillSvc.GetRequiredSkills(typeID)
        for skillTypeID, level in requiredSkills.iteritems():
            skillInfo = skillSvc.GetSkill(skillTypeID)
            if skillInfo and skillInfo.skillLevel >= level:
                continue
            return False

        return True

    def GetFlagsCompatibleWithChargeType(self, chargeTypeID):
        chargeGroupID = self.GetType(chargeTypeID).groupID
        chargeChargeSize = self.GetTypeAttribute(chargeTypeID, const.attributeChargeSize)
        if not hasattr(self, 'chargeGroupAttrs'):
            self.chargeGroupAttrs = []
            import re
            cgre = re.compile('chargeGroup\\d{1,2}')
            for a in cfg.dgmattribs:
                if cgre.match(a.attributeName) is not None:
                    self.chargeGroupAttrs.append(a.attributeName)

        shipItem = self.GetStateManager().GetItem(session.shipid)
        flags = []
        for module in shipItem.modules:
            groupCompatible = False
            for cgaID in self.chargeGroupAttrs:
                if cgaID in self.stateManager.attributesByItemAttribute.get(module.itemID, {}):
                    if self.stateManager.GetAttribute(module.itemID, cgaID) == chargeGroupID:
                        groupCompatible = True
                        continue

            if groupCompatible is False:
                continue
            if 'chargeSize' in self.stateManager.attributesByItemAttribute.get(module.itemID, {}):
                if self.stateManager.GetAttribute(module.itemID, 'chargeSize') == chargeChargeSize:
                    flags.append(module.flagID)
            else:
                flags.append(module.flagID)

        return flags

    def OnSkillPointsRemovedDueToShipLoss(self, skillTypeID, skillPoints, shipTypeID):
        entry = util.KeyVal(skillTypeID=skillTypeID, skillPoints=skillPoints, shipTypeID=shipTypeID)
        settings.char.generic.Set('skillLossNotification', entry)

    def OnSystemEffectStarted(self, typeIDs):
        body = ''
        for typeID in typeIDs:
            if len(body) > 0:
                body += '<br><br>'
            body += evetypes.GetDescription(typeID)

        eve.Message('CustomNotify', {'notify': body})

    def DoSimClockRebase(self, times):
        self.stateManager.DoSimClockRebase(times)

    def GetPowerEffectForType(self, typeID):
        powerEffects = [const.effectHiPower,
         const.effectMedPower,
         const.effectLoPower,
         const.effectRigSlot,
         const.effectSubSystem]
        if typeID not in cfg.dgmtypeeffects:
            return None
        for effect in cfg.dgmtypeeffects[typeID]:
            if effect.effectID in powerEffects:
                return effect.effectID

    def ShipOnlineModules(self):
        self.GetDogmaLM().ShipOnlineModules()


class TypeWrapper(object):

    def __init__(self, statemanager, typeID):
        self.statemanager = statemanager
        self.typeID = typeID
        self.categoryID = evetypes.GetCategoryID(typeID)

    def __getattr__(self, attributeName):
        if attributeName == 'hasCorporateHangars':
            try:
                result = self.__InnerGetattr('hasFleetHangars')
            except AttributeError:
                result = self.__InnerGetattr('hasCorporateHangars')

        else:
            result = self.__InnerGetattr(attributeName)
        setattr(self, attributeName, result)
        return result

    def __InnerGetattr(self, attributeName):
        if attributeName == 'itemID':
            return
        typeID = self.typeID
        if attributeName == 'displayAttributes':
            rowDescriptor = blue.DBRowDescriptor((('displayName', const.DBTYPE_STR),
             ('value', const.DBTYPE_R5),
             ('unitID', const.DBTYPE_UI1),
             ('iconID', const.DBTYPE_I4),
             ('attributeID', const.DBTYPE_I2)))
            rowset = dbutil.CRowset(rowDescriptor, [])
            for each in cfg.dgmtypeattribs.get(typeID, []):
                attrib = self.statemanager.attributesByID[each.attributeID]
                name = attrib.displayName or attrib.attributeName
                if attrib.attributeCategory == 9:
                    val = evetypes.GetAttributeForType(typeID, attrib.attributeName)
                elif each.value is not None:
                    val = each.value
                else:
                    val = attrib.defaultValue
                rowset.InsertNew([name,
                 val,
                 attrib.unitID,
                 attrib.iconID,
                 each.attributeID])

            return rowset
        if attributeName == 'effects':
            self.statemanager.CacheTypeEffects(typeID)
            return self.statemanager.effectsByType[typeID]
        if self.statemanager.attributesByName.has_key(attributeName):
            value = None
            attribute = self.statemanager.attributesByName[attributeName]
            if attribute.attributeCategory == 9:
                value = evetypes.GetAttributeForType(typeID, attributeName)
            attributeID = attribute.attributeID
            for each in cfg.dgmtypeattribs.get(typeID, []):
                if each.attributeID == attributeID:
                    value = each.value
                    break

            if value is None:
                value = self.statemanager.attributesByName[attributeName].defaultValue
            if cfg.dgmattribs.Get(attributeID).attributeCategory in (0, 1, 3, 4, 10, 11, 12):
                return int(value)
            return value
        if attributeName == 'name':
            return evetypes.GetName(typeID)
        return evetypes.GetAttributeForType(typeID, attributeName)

    def AttributeExists(self, attributeName):
        attributeID = self.statemanager.attributesByName[attributeName].attributeID
        for each in cfg.dgmtypeattribs.get(self.typeID, []):
            if each.attributeID == attributeID:
                return 1

        return 0

    def __str__(self):
        return self.typeName

    def __repr__(self):
        return '<godma-type typeID="%d">' % self.typeID


class ItemWrapper():
    __guid__ = 'godma.ItemWrapper'

    def __init__(self, statemanager, header, dbrow):
        self.statemanager = statemanager
        self.dbrow = dbrow
        self.header = header
        self.defaultEffectName = None

    def __str__(self):
        try:
            tname = self.name
        except:
            sys.exc_clear()
            tname = '<Unknown type name>'

        try:
            name = self.name
            if tname != name:
                name = tname + ':' + name
        except:
            sys.exc_clear()
            name = ''

        name += ' (row data: %s)' % str(self.dbrow)
        return name

    def __getattr__(self, attribute):
        d = self.__dict__
        if attribute == 'defaultEffect':
            if d['defaultEffectName'] is None:
                for effect in d['statemanager'].effectsByItemEffect.get(self.itemID, {}).itervalues():
                    if effect.isDefault:
                        d['defaultEffectName'] = effect.effectName
                        break

            effectName = d['defaultEffectName']
            return d['statemanager'].effectsByItemEffect[self.itemID].get(effectName, None)
        if attribute == 'line':
            return list(d['dbrow'])
        if attribute in d['dbrow'].__columns__:
            return d['dbrow'][attribute]
        if d['dbrow'].__class__.__dict__.has_key(attribute):
            return getattr(d['dbrow'], attribute)
        if self.__class__.__dict__.has_key(attribute):
            return self.__class__.__dict__[attribute]
        if attribute.startswith('__') and attribute.endswith('__'):
            raise AttributeError('ItemWrapper has no %s' % attribute)
        else:
            if attribute == 'inventory':
                return d['statemanager'].invByID.get(self.itemID, None)
            return d['statemanager'].GetAttribute(self.itemID, attribute)

    def __nonzero__(self):
        return True

    def GetChargeEffect(self, typeID):
        eff = self.statemanager.GetDefaultEffect(typeID)
        if eff is None:
            return
        eff = eff.__class__(self.statemanager, eff.header, eff.dbrow)
        idx = eff.header.Index('itemID')
        eff[idx] = self.itemID
        return eff

    def IsFitted(self):
        return IsShipFittingFlag(self.flagID)

    def GetSlotOccupants(self, flag):
        return [ item for item in self.statemanager.invitems.itervalues() if item.locationID == self.itemID and item.flagID == flag ]

    def GetCapacity(self, flag = None):
        used = None
        capacity = 0
        contents = []
        if self.categoryID == const.categoryShip:
            if IsShipFittingFlag(flag):
                occupants = self.GetSlotOccupants(flag)
                modules = filter(lambda x: x.categoryID == const.categoryModule, occupants)
                if len(modules):
                    capacity = self.statemanager.GetItem(modules[0].itemID).capacity
                else:
                    capacity = 0
                sublocation = self.statemanager.GetSubLocation(self.itemID, flag)
                if sublocation is not None:
                    contents = [sublocation]
                else:
                    occupants = self.GetSlotOccupants(flag)
                    contents = filter(lambda x: x.categoryID == const.categoryCharge, occupants)
            elif flag == const.flagDroneBay:
                contents = self.statemanager.invByID[self.itemID].ListDroneBay()
                capacity = self.droneCapacity
            elif flag is None or flag == const.flagCargo:
                contents = self.statemanager.invByID[self.itemID].ListCargo()
                capacity = self.capacity
            elif flag == const.flagShipHangar:
                if self.statemanager.invByID.has_key(self.itemID):
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = inv.List(flag)
                capacity = self.shipMaintenanceBayCapacity
            elif flag in (const.flagHangar,
             const.flagCorpSAG2,
             const.flagCorpSAG3,
             const.flagCorpSAG4,
             const.flagCorpSAG5,
             const.flagCorpSAG6,
             const.flagCorpSAG7):
                if self.statemanager.invByID.has_key(self.itemID):
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = [ item for item in inv.List() if item.flagID in (const.flagHangar,
                 const.flagCorpSAG2,
                 const.flagCorpSAG3,
                 const.flagCorpSAG4,
                 const.flagCorpSAG5,
                 const.flagCorpSAG6,
                 const.flagCorpSAG7) ]
                capacity = self.corporateHangarCapacity
            elif flag in inventoryFlagsCommon.inventoryFlagData:
                capacity = self.statemanager.GetAttributeValueByID(self.itemID, inventoryFlagsCommon.inventoryFlagData[flag]['attribute'])
                if self.statemanager.invByID.has_key(self.itemID):
                    inv = self.statemanager.invByID[self.itemID]
                elif self.statemanager.godma.invCache.IsInventoryPrimedAndListed(self.itemID):
                    inv = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                contents = [ item for item in inv.List() if item.flagID == flag ]
            else:
                raise RuntimeError('BadSlotForCapacity', flag)
        elif self.categoryID == const.categoryStarbase:
            capacity = self.capacity
            if self.groupID in (const.groupMobileMissileSentry, const.groupMobileProjectileSentry, const.groupMobileHybridSentry):
                contents = self.sublocations
            else:
                contents = sm.GetService('invCache').GetInventoryFromId(self.itemID).List(flag)
        if used is None:
            used = 0
            for item in contents:
                if flag and item.flagID != flag:
                    continue
                vol = GetItemVolume(item)
                if vol > 0:
                    used = used + vol

        return Row(['capacity', 'used'], [capacity, used])


class EffectWrapper():
    __guid__ = 'godma.EffectWrapper'

    def __init__(self, statemanager, header, dbrow):
        d = self.__dict__
        d['statemanager'] = statemanager
        d['dbrow'] = dbrow
        d['header'] = header
        d['defaultEffectName'] = None

    def __getattr__(self, attribute):
        d = self.__dict__
        if attribute in d:
            return d[attribute]
        try:
            return d['dbrow'][attribute]
        except:
            sys.exc_clear()
            ret = d['statemanager'].GetEffectAttributeEx(self, d['dbrow'].itemID, attribute)
            if ret is None:
                raise AttributeError, attribute
            return ret

    def __setattr__(self, attr, value):
        d = self.__dict__
        if attr in d['header'].Keys():
            d['dbrow'][attr] = value
        else:
            d[attr] = value

    def __setitem__(self, idx, value):
        self.dbrow[idx] = value

    def Activate(self, target = None, repeat = 0):
        if self.isActive and self.duration <= 0:
            self.statemanager.godma.LogError('Module effect already active', self.effectName, self.itemID)
            return
        elif not eve.session.IsItSafe():
            return
        elif self.effectCategory == const.dgmEffOverload:
            return self.statemanager.Overload(self.itemID, self.effectID)
        else:
            return self.statemanager.Activate(self.itemID, self.effectName, target, repeat)

    def Deactivate(self):
        if not self.isActive:
            self.statemanager.godma.LogError('Module effect not active', self.effectName, self.itemID)
            return
        elif self.effectCategory == const.dgmEffOverload:
            return self.statemanager.StopOverload(self.itemID, self.effectID)
        else:
            return self.statemanager.Deactivate(self.itemID, self.effectName)

    def Toggle(self):
        if self.isActive:
            return self.Deactivate()
        else:
            return self.Activate()


ENV_IDX_SELF = 0
ENV_IDX_CHAR = 1
ENV_IDX_SHIP = 2
ENV_IDX_TARGET = 3
ENV_IDX_OTHER = 4
ENV_IDX_AREA = 5
ENV_IDX_EFFECT = 6
ENV_IDX_LINE = 7

class StateManager():
    __guid__ = 'godma.StateManager'
    __effectheader__ = blue.DBRowDescriptor((('itemID', const.DBTYPE_STR),
     ('effectID', const.DBTYPE_I4),
     ('effectName', const.DBTYPE_STR),
     ('effectCategory', const.DBTYPE_I2),
     ('isDefault', const.DBTYPE_BOOL),
     ('isActive', const.DBTYPE_BOOL),
     ('isOffensive', const.DBTYPE_BOOL),
     ('isAssistance', const.DBTYPE_BOOL),
     ('description', const.DBTYPE_STR),
     ('trackingSpeedAttributeID', const.DBTYPE_I2),
     ('rangeAttributeID', const.DBTYPE_I2),
     ('falloffAttributeID', const.DBTYPE_I4),
     ('dischargeAttributeID', const.DBTYPE_I2),
     ('durationAttributeID', const.DBTYPE_I2),
     ('iconID', const.DBTYPE_I4),
     ('targetID', const.DBTYPE_I8),
     ('startTime', const.DBTYPE_FILETIME),
     ('duration', const.DBTYPE_I4),
     ('repeat', const.DBTYPE_I4),
     ('isDeactivating', const.DBTYPE_BOOL)))

    def __init__(self, godma):
        self.godma = godma
        self.activatedLocation = {}
        self.invitems = godmarowset.GodmaIndexedRowset(godma.itemrd, 'itemID', rowClass=self.GetItemWrapper)
        self.sublocationsByKey = godmarowset.GodmaIndexedRowset(self.godma.subloc_internalrd, 'itemID', rowClass=self.GetSubLocationWrapper)
        self.sublocationsByLocationFlag = godmarowset.GodmaRowset(self.godma.subloc_internalrd, [], rowClass=self.GetSubLocationWrapper).Filter('locationID', 'flagID')
        self.itemsByLocationID = {}
        self.inited = False
        self.priming = False
        self.primingChannel = None
        self.attributesByName = None
        self.attributesByID = None
        self.effectsByType = {}
        self.defaultEffectsByType = {}
        self.chargedAttributeTauCaps = {}
        self.droneSettingAttributes = {}
        self.lastAttributeChange = {}
        self.attributesByItemAttribute = {}
        self.effectsByItemEffect = {}
        self.chargedAttributesByItemAttribute = {}
        self.modulesBeingRepaired = {}
        self.slaveModulesByMasterModule = {}
        self.activatingEffects = set()
        self.chargeTypeByModule = {}
        self.modulesBeingReloaded = {}
        self.lastStopTimesByItemID = {}
        self.invByID = {}
        self.dogmaLM = None
        self.pending = {}
        self.pendingOverloading = set()
        self.pendingStopOverloading = set()
        self.itemKeyChannels = {}
        self.requiredEffects = {const.effectOnline: True,
         const.effectHiPower: True,
         const.effectMedPower: True,
         const.effectLoPower: True,
         const.effectRigSlot: True}
        self.electronicAttributes = {const.attributeScanGravimetricStrengthBonus: const.attributeScanGravimetricStrength,
         const.attributeScanLadarStrengthBonus: const.attributeScanLadarStrength,
         const.attributeScanMagnetometricStrengthBonus: const.attributeScanMagnetometricStrength,
         const.attributeScanRadarStrengthBonus: const.attributeScanRadarStrength}
        self.propulsionAttributes = {const.attributePropulsionFusionStrengthBonus: const.attributePropulsionFusionStrength,
         const.attributePropulsionIonStrengthBonus: const.attributePropulsionIonStrength,
         const.attributePropulsionMagpulseStrengthBonus: const.attributePropulsionMagpulseStrength,
         const.attributePropulsionPlasmaStrengthBonus: const.attributePropulsionPlasmaStrength}
        self.dogmaLocation = None

    def Release(self):
        self.dogmaLM = None
        self.invitems = None
        self.sublocationsByLocationFlag = None
        self.sublocationsByKey = None
        self.itemsByLocationID = None
        self.godma = None
        self.effectsByItemEffect = None
        self.defaultEffectsByType = None
        self.attributesByItemAttribute = None

    def IsLocationLoaded(self, locationID):
        return locationID in self.itemsByLocationID

    def IsItemLoaded(self, itemKey):
        return itemKey in self.invitems or itemKey in self.sublocationsByKey

    def GetDogmaLM(self):
        if not self.dogmaLM:
            self.dogmaLM = moniker.CharGetDogmaLocation()
        return self.dogmaLM

    def LogAttributeViaStateManager(self, itemID, attributeID, reason = None):
        if reason is None:
            reason = ''
        else:
            reason += '  '
        val = None
        try:
            val = self.GetAttribute(itemID, self.attributesByID[attributeID].attributeName)
        except:
            sys.exc_clear()
            val = 'screwed'

        logStuff = self.GetDogmaLM().FullyDescribeAttribute(itemID, attributeID, reason + 'Value on client was %s.' % val)
        for line in logStuff:
            self.godma.LogError(line)

    def ProcessSessionChange(self, isRemote, session, change):
        if session.charid:
            if 'stationid2' in change or 'solarsystemid' in change or 'shipid' in change or 'charid' in change:
                self.priming = True
                self.PurgeInventories([session.charid, session.shipid], skipCapacityEvent=True)
                self.dogmaLM = None
                self.godma.LogInfo('ProcessSessionChange: Prime (pre)')
                self.lastAttributeChange = {}
                if session.shipid is None:
                    self.Prime()
                else:
                    oldAttribs = {}
                    try:
                        del self.invByID[session.shipid]
                        oldAttribs = self.attributesByItemAttribute[session.shipid].copy()
                    except KeyError:
                        pass

                    self.Prime(session.shipid)
                    if session.shipid in self.attributesByItemAttribute and self.attributesByItemAttribute[session.shipid]:
                        newAttribs = self.attributesByItemAttribute[session.shipid]
                        attribChanges = []
                        shipItem = self.invitems[session.shipid]
                        for introducedAttribute in set(newAttribs).difference(set(oldAttribs)):
                            attribChanges.append((introducedAttribute, shipItem, newAttribs[introducedAttribute]))

                        for commonAttribute in set(newAttribs).intersection(set(oldAttribs)):
                            if oldAttribs[commonAttribute] != newAttribs[commonAttribute]:
                                attribChanges.append((commonAttribute, shipItem, newAttribs[commonAttribute]))

                        if attribChanges:
                            sm.ScatterEvent('OnAttributes', attribChanges)
                    self.ClearPendingOverloadingFlags()
                self.godma.LogInfo('ProcessSessionChange: Prime (post)')
                self.priming = False
            if session.stationid or session.solarsystemid:
                dogmaLM = self.GetDogmaLM()
                dogmaLM.Bind()
            for moduleID in self.modulesBeingRepaired.keys():
                self.StopRepairModule(moduleID)

            if 'shipid' in change:
                self.chargeTypeByModule = {}
        else:
            self.dogmaLM = None

    def OnItemChange(self, item, change):
        if self.IsSubLocation(item.itemID):
            return
        if item.itemID in self.chargeTypeByModule and const.ixFlag in change:
            del self.chargeTypeByModule[item.itemID]
        self.godma.LogInfo('OnItemChange', item, change)
        if const.ixLocationID in change or const.ixStackSize in change and item.stacksize == 0:
            flag = item.flagID
            oFlagOk = IsShipFittingFlag(flag) or flag == const.flagPilot
            if change.has_key(const.ixFlag):
                cFlag = change[const.ixFlag]
                cFlagOk = IsShipFittingFlag(cFlag) or cFlag == const.flagPilot
                if not (oFlagOk or cFlagOk):
                    return
            elif not oFlagOk:
                return
            if self.invByID.has_key(item.locationID) and not (change.has_key(const.ixStackSize) and item.stacksize == 0):
                self.UpdateItem(item)
                if self.invitems.has_key(item.itemID):
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
            elif self.invitems.has_key(item.itemID):
                oldLocationID = change.get(const.ixLocationID, item.locationID)
                if not self.invByID.has_key(item.itemID):
                    self.invitems[item.itemID].locationID = item.locationID
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
                    del self.invitems[item.itemID]
                else:
                    self.invitems[item.itemID].locationID = item.locationID
                    self.invitems[item.itemID].flagID = item.flagID
                    sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)
                if oldLocationID != item.locationID:
                    if oldLocationID in self.itemsByLocationID:
                        self.itemsByLocationID[oldLocationID].discard(item.itemID)
                    if item.locationID in self.itemsByLocationID:
                        self.itemsByLocationID[item.locationID].add(item.itemID)
        elif self.invByID.has_key(item.locationID):
            if self.invitems.has_key(item.itemID):
                if item.ownerID != session.charid and const.ixOwnerID in change or const.ixFlag in change and not (IsShipFittingFlag(item.flagID) or item.flagID in (const.flagSkill, const.flagSkillInTraining, const.flagBooster)):
                    sm.ScatterEvent('OnGodmaItemChange', item, change)
                    del self.invitems[item.itemID]
                    if item.locationID in self.itemsByLocationID:
                        self.itemsByLocationID[item.locationID].remove(item.itemID)
                    return
            if item.flagID in util.Flatten((inventoryFlagsCommon.inventoryFlagData,
             const.flagCorpSAGs,
             const.flagDroneBay,
             const.flagCargo,
             const.flagHangar)):
                return
            if item.groupID == const.groupCapsule and item.ownerID == session.charid:
                if item.locationID == session.locationid and item.flagID == const.flagNone or item.locationID == session.shipid and item.flagID == const.flagCapsule:
                    return
            if len(change) == 1 and change.has_key(const.ixStackSize) and not (item.singleton and change[const.ixStackSize] > 0):
                self.UpdateItem(item, dontGetInfo=1)
            else:
                self.UpdateItem(item)
            if self.invitems.has_key(item.itemID):
                sm.ScatterEvent('OnGodmaItemChange', self.invitems[item.itemID], change)

    def ProcessGodmaPrimeLocation(self, locationID, data):
        self.godma.LogInfo('ProcessGodmaPrimeLocation', locationID, 'rows:', len(data))
        self.itemsByLocationID[locationID] = set()
        if data.has_key(locationID):
            row = data[locationID]
            self.UpdateItem(row.invItem, row)
        for itemKey in data.iterkeys():
            if itemKey == locationID:
                continue
            row = data[itemKey]
            self.UpdateItem(row.invItem, row)

        sm.ChainEvent('ProcessGodmaLocationPrimed', locationID)

    def ProcessLocationInfo(self, cData):
        for locationID, datas in cData.iteritems():
            for data in datas:
                self.ProcessGodmaPrimeLocation(locationID, data)

    def OnGodmaPrimeItem(self, locationID, row):
        if locationID not in self.itemsByLocationID:
            log.LogError('OnGodmaPrimeItem received row %s for locationID %s, location primed!' % (row, locationID))
            self.itemsByLocationID[locationID] = set()
        self.UpdateItem(row.invItem, row)

    def OnGodmaFlushLocation(self, locationID):
        self.godma.LogInfo('OnGodmaFlushLocation', locationID)
        self.PurgeEntries(locationID)

    def OnGodmaFlushLocationProfile(self, locationID, profileID):
        self.godma.LogInfo('OnGodmaFlushLocationProfile', locationID, profileID)
        if profileID[0] == 'effect' and profileID[1] != locationID:
            self.PurgeEntry(profileID[1], locationID)

    def OnModuleAttributeChange(self, ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr = True):
        if self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnModuleAttributeChange - Discarded due to response from receive', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
                return
            self.godma.LogWarn('OnModuleAttributeChange - Stalled, but now in action', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
        self.OnModuleAttributeChange_(ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr, useTasket=True)

    def OnModuleAttributeChange_(self, ownerID, itemKey, attributeID, time, newValue, oldValue, wallclockTime, scatterAttr = True, useTasket = False):
        attributeName = cfg.dgmattribs.Get(attributeID).attributeName
        if not self._IsAttributeChangeRelevant(itemKey, attributeID, wallclockTime):
            self.godma.LogInfo('Ignoring attribute change to attribute', attributeID, 'on', itemKey, 'as it is too old', (oldValue, newValue))
            return
        if wallclockTime:
            self.lastAttributeChange[itemKey, attributeID] = wallclockTime
        if not (itemKey == eve.session.charid or ownerID == eve.session.charid):
            if eve.session.charid is None:
                return
            log.LogTraceback('Got moduleattributechange for object I do not own!!!!!!!! Yayz0r - ownerID = %s, itemKey = %s, attributeID = %s, session.charid = %s' % (ownerID,
             itemKey,
             attributeID,
             eve.session.charid), channel='svc.godma')
            self.godma.LogError('OnModuleAttributeChange', ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
            return
        if useTasket:
            uthread.pool('godma::ApplyAttributeChange::OnModuleAttributeChange', self.ApplyAttributeChange, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
        else:
            self.ApplyAttributeChange(ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)

    def OnLocationAttributeChange(self, ownerID, locationID, itemKey, attributeID, time, newValue, oldValue):
        if locationID not in self.itemsByLocationID:
            log.LogInfo('Got attribute change event for unknown location: %s ' % [ownerID,
             locationID,
             itemKey,
             attributeID,
             time,
             newValue,
             oldValue])
            return
        ClockThis('godma::ApplyAttributeChange::OnLocationAttributeChange', self.ApplyAttributeChange, ownerID, itemKey, attributeID, time, newValue, oldValue)

    def OnModuleAttributeChanges(self, changes):
        if self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnModuleAttributeChanges - Discarded due to response from receive', changes)
                return
            self.godma.LogWarn('OnModuleAttributeChanges - Stalled, but now in action', changes)
        qtyChanges = []
        itemKeyIdx, attributeIdx, newValueIdx = (2, 3, 5)
        for each in changes:
            if type(each[itemKeyIdx]) is tuple and each[attributeIdx] == const.attributeQuantity and each[newValueIdx] == 0.0:
                qtyChanges.append(each[itemKeyIdx])

        for each in changes:
            if each[itemKeyIdx] in qtyChanges and each[attributeIdx] != const.attributeQuantity:
                continue
            with util.ExceptionEater('Actioning on an attribute change in Godma'):
                self.OnModuleAttributeChange_(*(each[1:] + (0,)))

        ch = []
        for change in changes:
            entry = None
            itemKey = change[2]
            if self.invitems.has_key(itemKey):
                entry = self.invitems[itemKey]
            elif self.sublocationsByKey.has_key(itemKey):
                entry = self.sublocationsByKey[itemKey]
            if entry:
                ch.append((cfg.dgmattribs.Get(change[3]).attributeName, entry, change[5]))

        sm.ScatterEvent('OnAttributes', ch)

    def GetActiveModulesOnTargetID(self, targetID):
        ret = []
        for module in self.GetItem(session.shipid).modules:
            try:
                effect = module.defaultEffect
                if effect is None:
                    continue
                if effect.isActive and effect.targetID == targetID:
                    ret.append(module)
            except KeyError:
                continue

        return ret

    def OnGodmaShipEffect(self, itemID, effectID, t, start, active, environment, startTime, duration, repeat, error, actualStopTime = None, stall = True):
        if stall and self.primingChannel is not None:
            if not self.primingChannel.receive():
                self.godma.LogError('OnGodmaShipEffect - Discarded due to response from receive', itemID, effectID, t, start, active, environment, startTime, duration, repeat, error)
                return
            self.godma.LogWarn('OnGodmaShipEffect - Stalled, but now in action', itemID, effectID, t, start, active, environment, startTime, duration, repeat, error)
        effect = cfg.dgmeffects.Get(effectID)
        effectName = effect.effectName
        if self.effectsByItemEffect.has_key(itemID) and self.effectsByItemEffect[itemID].has_key(effectName):
            self.godma.LogInfo('OnGodmaShipEffect.effectsByItemEffect', itemID, effectName, active, duration, repeat)
            self.effectsByItemEffect[itemID][effectName].isDeactivating = False
            self.effectsByItemEffect[itemID][effectName].isActive = active
            self.effectsByItemEffect[itemID][effectName].startTime = startTime
            self.effectsByItemEffect[itemID][effectName].duration = duration
            self.effectsByItemEffect[itemID][effectName].repeat = repeat
            self.effectsByItemEffect[itemID][effectName].targetID = environment[ENV_IDX_TARGET]
            if environment[ENV_IDX_SHIP] == session.shipid or environment[ENV_IDX_SELF] and sm.GetService('pwn').GetCurrentControl(environment[ENV_IDX_SELF]):
                effectState = util.KeyVal(itemID=itemID, effectName=effectName, time=t, start=start, active=active, environment=environment, duration=duration, repeat=repeat, error=error)
                uthread.new(self.ActualStopEffect, itemID, effectID, actualStopTime, effectState)
        if effect.effectCategory == const.dgmEffOverload:
            if start and itemID in self.pendingOverloading:
                self.StopPendingOverloadModule(itemID)
            elif not start and itemID in self.pendingStopOverloading:
                self.StopPendingStopOverloadModule(itemID)

    def ActualStopEffect(self, itemID, effectID, stopTime, effectState):
        if not effectState.start and stopTime is not None:
            timeDiffInMs = (stopTime - blue.os.GetSimTime()) / const.MSEC
            if timeDiffInMs > 0:
                self.godma.LogInfo('ActualStopEffect::Sleeping for', timeDiffInMs)
                blue.pyos.synchro.SleepSim(timeDiffInMs)
        self.RecordLastStopTime(itemID, effectState, effectID)
        self.ClearPendingOverloadingFlags()
        sm.ChainEvent('ProcessShipEffect', self, effectState)

    def RecordLastStopTime(self, itemID, effectState, effectID):
        if effectState.start or effectID in (const.effectOnline, const.effectOverloadRofBonus):
            return
        delayTime = self.dogmaLocation.GetAccurateAttributeValue(itemID, const.attributeModuleReactivationDelay)
        if not delayTime:
            return
        self.RemoveOldCooldownTimers()
        time = blue.os.GetSimTime()
        self.lastStopTimesByItemID[itemID] = (time, delayTime)

    def OnGodmaEffectInfo(self, itemID, itemTypeID, effectInfo, snapshotTime):
        info = util.KeyVal(activeEffects=effectInfo, time=snapshotTime)
        self.RefreshItemEffects(itemID, itemTypeID, info=info, doUpdate=True)

    def InitializeData(self):
        if not self.inited:
            self.attributesByName = IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeName',))
            self.attributesByID = IndexedRows(cfg.dgmattribs.data.itervalues(), ('attributeID',))
            chargedAttributes = IndexedRowLists(cfg.dgmattribs.data.itervalues(), ('chargeRechargeTimeID',))
            chargedAttributeTauCaps = {}
            chargedAttributeTauCapsByMax = {}
            chargedAttributesByTau = {}
            for tauID in chargedAttributes.iterkeys():
                if tauID:
                    tauName = self.attributesByID[tauID].attributeName
                    for attribute in chargedAttributes[tauID]:
                        if attribute.attributeCategory != 8:
                            attName = attribute.attributeName
                            capName = self.attributesByID[attribute.maxAttributeID].attributeName
                            chargedAttributeTauCaps[attName] = (tauName, capName)
                            if not chargedAttributeTauCapsByMax.has_key(capName):
                                chargedAttributeTauCapsByMax[capName] = []
                            chargedAttributeTauCapsByMax[capName].append(attName)
                            if not chargedAttributesByTau.has_key(tauName):
                                chargedAttributesByTau[tauName] = []
                            chargedAttributesByTau[tauName].append(attName)

            self.chargedAttributeTauCaps = chargedAttributeTauCaps
            self.chargedAttributeTauCapsByMax = chargedAttributeTauCapsByMax
            self.chargedAttributesByTau = chargedAttributesByTau
            self.typeWrappers = {}
            shipID = session.shipid
            self.inited = True

    def IsSubLocation(self, itemKey):
        return type(itemKey) is tuple

    def UpdateItem(self, item, infoz = None, dontGetInfo = 0):
        self.godma.LogInfo('UpdateItem:', item, infoz, dontGetInfo)
        isSubLocation = item is not None and self.IsSubLocation(item.itemID) or infoz is not None and self.IsSubLocation(infoz.itemID)
        if isSubLocation:
            itemKey = infoz.itemID
            itemLocationID, itemFlag, itemTypeID = itemKey
            itemGroupID = evetypes.GetGroupID(itemTypeID)
            itemCategoryID = evetypes.GetCategoryID(itemTypeID)
        else:
            itemKey = item.itemID
            itemLocationID = item.locationID
            itemTypeID, itemGroupID, itemCategoryID, itemFlag = (item.typeID,
             item.groupID,
             item.categoryID,
             item.flagID)
        if itemCategoryID not in (const.categoryEntity,
         const.categoryStarbase,
         const.categorySovereigntyStructure,
         const.categoryShip,
         const.categoryModule,
         const.categoryCharge,
         const.categoryDrone,
         const.categorySubSystem,
         const.categoryFighter) and itemGroupID != const.groupCharacter:
            self.godma.LogError('Godma location received unexpected and unwanted item', item)
            return
        if itemFlag in (const.flagCargo, const.flagDroneBay) or itemFlag in const.fighterTubeFlags:
            return
        doUpdate = False
        ret = None
        if isSubLocation:
            if itemLocationID not in self.invitems:
                self.godma.LogWarn('Godma:UpdateItem - could not find location object', itemLocationID, ', skipping update of', itemKey)
                return
            locationItem = self.invitems[itemLocationID]
            defaultQty = self.attributesByName['quantity'].defaultValue
            l = blue.DBRow(self.godma.subloc_internalrd, [itemKey,
             itemTypeID,
             locationItem.ownerID,
             itemLocationID,
             itemFlag,
             itemGroupID,
             itemCategoryID])
            if not self.sublocationsByKey.has_key(itemFlag):
                self.godma.LogInfo('Godma:UpdateItem - Inserting sublocation', itemKey)
                if not infoz.attributes.has_key(const.attributeQuantity):
                    log.LogTraceback('Godma:UpdateItem - QUANTITY MISSING', channel='svc.godma')
                    self.godma.LogError('Godma:UpdateItem - QUANTITY MISSING')
                else:
                    quantity = infoz.attributes[const.attributeQuantity]
                    item = blue.DBRow(self.godma.sublocrd, [itemKey,
                     itemTypeID,
                     locationItem.ownerID,
                     itemLocationID,
                     itemFlag,
                     quantity,
                     itemGroupID,
                     itemCategoryID,
                     None])
                    if self.godma.invCache.IsInventoryPrimedAndListed(itemLocationID):
                        self.godma.LogInfo('Godma:UpdateItem - QUANTITY', infoz.attributes[const.attributeQuantity])
                        sm.ScatterEvent('OnItemChange', item, {const.ixLocationID: None,
                         const.ixFlag: None})
            self.sublocationsByKey[itemKey] = l
            if not self.sublocationsByLocationFlag.has_key(itemLocationID):
                self.sublocationsByLocationFlag[itemLocationID] = godmarowset.GodmaIndexedRowset(self.godma.subloc_internalrd, 'flagID', rowClass=self.GetSubLocationWrapper)
            elif self.sublocationsByLocationFlag[itemLocationID].has_key(itemFlag):
                doUpdate = True
            ret = self.sublocationsByLocationFlag[itemLocationID][itemFlag] = l
        else:
            if not self.invitems.has_key(itemKey):
                self.godma.LogInfo('Godma:UpdateItem - Inserting item', itemKey)
            else:
                doUpdate = True
            ret = self.invitems[itemKey] = item
            if itemCategoryID in (const.categoryShip, const.categoryStarbase) or itemGroupID == const.groupCharacter:
                self.itemsByLocationID[itemKey] = set()
            if not (util.IsSolarSystem(itemLocationID) or util.IsStation(itemLocationID) or util.IsWorldSpace(itemLocationID)):
                self.itemsByLocationID[itemLocationID].add(itemKey)
        if IsShipFittingFlag(itemFlag) and not isSubLocation and itemCategoryID not in (const.categoryModule, const.categoryCharge, const.categorySubSystem):
            self.godma.LogError('Godma:UpdateItem.skip2', itemKey)
            return
        if (isSubLocation or not item.singleton) and (itemCategoryID != const.categoryCharge or itemGroupID == const.groupMine):
            if itemFlag != const.flagCapsule:
                self.godma.LogError('Godma:UpdateItem.skip3', itemKey)
            return
        if dontGetInfo:
            self.godma.LogError('Godma:UpdateItem.skip4', itemKey)
            return
        if infoz is None:
            infoz = self.GetDogmaLM().ItemGetInfo(itemKey)
        if infoz is None:
            return
        self.RefreshItemAttributes(itemKey, infoz, doUpdate)
        self.RefreshItemEffects(itemKey, itemTypeID, infoz, doUpdate)
        if isSubLocation:
            regKey = (itemLocationID, itemFlag, None)
        else:
            regKey = itemKey
        if regKey in self.itemKeyChannels:
            while self.itemKeyChannels[regKey].queue:
                self.godma.LogInfo('GetWithWait-END', regKey)
                self.itemKeyChannels[regKey].send(ret)

            del self.itemKeyChannels[regKey]

    def RefreshItemEffects(self, itemID, itemTypeID, info = None, doUpdate = False):
        if info is None:
            info = self.GetDogmaLM().ItemGetInfo(itemID)
            if info is None:
                return
        effLines = []
        eventLines = []
        activeDict = info.activeEffects
        rl = cfg.dgmtypeeffects.get(itemTypeID, None)
        if rl is not None:
            for row in rl:
                effectID = row.effectID
                eff = cfg.dgmeffects.Get(effectID)
                if row.isDefault and effectID != const.effectSkillEffect or self.requiredEffects.has_key(effectID) or eff.effectCategory in (const.dgmEffActivation,
                 const.dgmEffTarget,
                 const.dgmEffArea,
                 const.dgmEffOverload) or eff.fittingUsageChanceAttributeID is not None:
                    line = blue.DBRow(self.__effectheader__, [itemID,
                     eff.effectID,
                     eff.effectName,
                     eff.effectCategory,
                     row.isDefault,
                     activeDict.has_key(effectID),
                     eff.isOffensive,
                     eff.isAssistance,
                     eff.description,
                     eff.trackingSpeedAttributeID,
                     eff.rangeAttributeID,
                     eff.falloffAttributeID,
                     eff.dischargeAttributeID,
                     eff.durationAttributeID,
                     eff.iconID,
                     None,
                     None,
                     None,
                     None,
                     False])
                    effLines.append(line)
                    self.godma.LogInfo('RefreshItemEffects.effectsByItemEffect', itemID, effectID, effLines[-1])
                    if activeDict.has_key(effectID) and eff.effectCategory in (const.dgmEffActivation,
                     const.dgmEffTarget,
                     const.dgmEffArea,
                     const.dgmEffOverload) and not self.requiredEffects.has_key(effectID):
                        d = activeDict[effectID]
                        env = d[:ENV_IDX_LINE]
                        startTime, duration, repeat = d[7], d[8], d[9]
                        eventLines.append((itemID,
                         effectID,
                         info.time,
                         True,
                         True,
                         env,
                         startTime,
                         duration,
                         repeat,
                         None))

        if doUpdate and self.effectsByItemEffect.has_key(itemID):
            ind = self.effectsByItemEffect[itemID].header.Index('effectName')
            for i in effLines:
                self.effectsByItemEffect[itemID][i[ind]] = i

        else:
            self.effectsByItemEffect[itemID] = godmarowset.GodmaRowset(self.__effectheader__, effLines, rowClass=self.GetEffectWrapper).Index('effectName')
        kwArgs = {'stall': False}
        for line in eventLines:
            apply(self.OnGodmaShipEffect, line, kwArgs)

    def RefreshItemAttributes(self, itemID, info = None, doUpdate = False):
        if info is None:
            info = self.GetDogmaLM().ItemGetInfo(itemID)
            if info is None:
                return
        if doUpdate:
            atts = self.attributesByItemAttribute.get(itemID, {})
        else:
            atts = {}
        time = info.time
        wallclockTime = info.wallclockTime
        for attributeID, val in info.attributes.iteritems():
            if not self._IsAttributeChangeRelevant(itemID, attributeID, wallclockTime):
                continue
            self.godma.LogInfo('UpdateAttributeIDs', itemID, attributeID, cfg.dgmattribs.Get(attributeID).attributeName, val)
            atts[self.attributesByID[attributeID].attributeName] = val

        return self.UpdateAttribute(itemID, atts, time)

    def _IsAttributeChangeRelevant(self, itemID, attributeID, wallclockTime):
        if not wallclockTime:
            return True
        if (itemID, attributeID) not in self.lastAttributeChange:
            return True
        if self.lastAttributeChange[itemID, attributeID] <= wallclockTime:
            return True
        return False

    def UpdateAttribute(self, itemID, attributes, time):
        self.attributesByItemAttribute[itemID] = attributes
        if time is None:
            time = blue.os.GetSimTime()
        for k in attributes.iterkeys():
            if self.chargedAttributeTauCaps.has_key(k):
                if not self.chargedAttributesByItemAttribute.has_key(itemID):
                    self.chargedAttributesByItemAttribute[itemID] = {}
                if self.attributesByItemAttribute[itemID].get(self.chargedAttributeTauCaps[k][0]) and self.attributesByItemAttribute[itemID].get(self.chargedAttributeTauCaps[k][1]):
                    self.CreateChargedAttribute(itemID, k, attributes[k], time, self.chargedAttributeTauCaps[k])

    def CreateChargedAttribute(self, itemID, attribute, value, time, taucap):
        tau, cap = taucap
        tauValue = self.GetAttribute(itemID, tau) / 5.0
        capValue = self.GetAttribute(itemID, cap)
        self.chargedAttributesByItemAttribute[itemID][attribute] = [value,
         time,
         tauValue,
         capValue]
        self.godma.LogInfo('CreateChargedAttribute', itemID, attribute, time, self.chargedAttributesByItemAttribute[itemID][attribute])

    def NameToGroup(self, name):
        k = 'group' + name[0].capitalize() + name[1:]
        if util.ConstValueExists(k):
            return util.LookupConstValue(k, None)

    def NameToType(self, name):
        k = 'type' + name[0].capitalize() + name[1:]
        if util.ConstValueExists(k):
            return util.LookupConstValue(k, None)

    def LocateItem(self, id, name):
        typeID = self.NameToType(name)
        if typeID is not None:
            loc = FilterRowset(self.invitems.header, self.invitems.items.values(), 'locationID', self.GetItemWrapper)
            for item in loc[id]:
                if item.flagID in [const.flagSkill, const.flagSkillInTraining] and item.typeID == typeID:
                    return item

    def GetDisplayAttributes(self, id):
        rowDescriptor = blue.DBRowDescriptor((('displayName', const.DBTYPE_STR),
         ('value', const.DBTYPE_R5),
         ('unitID', const.DBTYPE_UI1),
         ('iconID', const.DBTYPE_I4),
         ('attributeID', const.DBTYPE_I2)))
        rowset = dbutil.CRowset(rowDescriptor, [])
        for k, v in self.GetAttributes(id).iteritems():
            attribute = self.attributesByName[k]
            realK = attribute.displayName
            if not len(realK):
                realK = k
            if attribute.published:
                rowset.InsertNew([realK,
                 v,
                 attribute.unitID,
                 attribute.iconID,
                 attribute.attributeID])

        return rowset

    def GetItemWrapper(self, header, dbrow):
        return ItemWrapper(self, header, dbrow)

    def GetSubLocationWrapper(self, header, dbrow):
        return ItemWrapper(self, header, dbrow)

    def GetItem(self, itemID, waitForPrime = False):
        if type(itemID) is tuple:
            return self.GetSubLocation(itemID[0], itemID[1], waitForPrime)
        while self.priming:
            blue.pyos.synchro.SleepWallclock(1000)

        if self.invitems.has_key(itemID):
            return self.invitems[itemID]
        if waitForPrime:
            self.godma.LogInfo('GetItem.GetWithWait', itemID)
            return self.GetWithWait(itemID)

    def GetSubLocation(self, locationID, flag, waitForPrime = False):
        while self.priming:
            blue.pyos.synchro.SleepWallclock(1000)

        if self.sublocationsByLocationFlag.has_key(locationID) and self.sublocationsByLocationFlag[locationID].has_key(flag):
            return self.sublocationsByLocationFlag[locationID][flag]
        if waitForPrime:
            self.godma.LogInfo('GetSubLocation.GetWithWait', locationID, flag)
            return self.GetWithWait((locationID, flag, None))

    def GetWithWait(self, itemKey):
        if self.itemKeyChannels.has_key(itemKey):
            channel = self.itemKeyChannels[itemKey]
        else:
            channel = uthread.Channel(('godma::GetItem', itemKey))
            self.itemKeyChannels[itemKey] = channel
        ret = channel.receive()
        self.godma.LogInfo('GetWithWait', itemKey, 'DONE', ret)
        return ret

    def GetAttributes(self, id):
        if self.attributesByItemAttribute.has_key(id):
            return self.attributesByItemAttribute[id]
        return {}

    def GetAttribute(self, itemKey, attrKey):
        if self.IsSubLocation(itemKey):
            if attrKey == 'singleton':
                return 0
            if attrKey == 'stacksize':
                attrKey = 'quantity'
        if self.chargedAttributesByItemAttribute.has_key(itemKey) and self.chargedAttributesByItemAttribute[itemKey].has_key(attrKey):
            chargedAttribute = self.chargedAttributesByItemAttribute[itemKey][attrKey]
            try:
                return self.GetChargeValue(*chargedAttribute)
            except ZeroDivisionError:
                typeID = self.invitems[itemKey].typeID if not isinstance(itemKey, tuple) else itemKey[2]
                log.LogException('GetChargeValue got a ZeroDivisionError for item %s of type %s' % (itemKey, evetypes.GetName(typeID)))
                raise

        shipID = session.shipid
        if self.attributesByItemAttribute.has_key(itemKey):
            if self.attributesByItemAttribute[itemKey].has_key(attrKey):
                return self.attributesByItemAttribute[itemKey][attrKey]
        if self.sublocationsByKey.has_key(itemKey):
            typeID = itemKey[2]
            locationID = itemKey[0]
        else:
            typeID = self.invitems[itemKey].typeID
            locationID = self.invitems[itemKey].locationID
        categoryID = evetypes.GetCategoryID(typeID)
        if categoryID == const.categorySkill:
            raise RuntimeError('StateManager::GetAttribute called for skill item! Skill items should not exist!')
        if self.attributesByName.has_key(attrKey):
            return self.attributesByName[attrKey].defaultValue
        if attrKey == 'invItem':
            if self.sublocationsByKey.has_key(itemKey):
                rd = self.godma.sublocrd
                item = self.GetSubLocation(locationID, itemKey[1])
            else:
                rd = self.godma.itemrd
                item = self.Item(itemKey)
            return blue.DBRow(rd, [itemKey,
             typeID,
             item.ownerID,
             locationID,
             item.flagID,
             item.quantity,
             evetypes.GetGroupID(typeID),
             categoryID,
             None])
        if attrKey == 'displayAttributes':
            return self.GetDisplayAttributes(itemKey)
        if attrKey == 'attributes':
            return self.GetAttributes(itemKey)
        if attrKey == 'typeID':
            return typeID
        if attrKey == 'type':
            log.LogTraceback("Someone is asking for 'type' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'description':
            return evetypes.GetDescription(typeID)
        if attrKey == 'group':
            log.LogTraceback("Someone is asking for 'group' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'category':
            log.LogTraceback("Someone is asking for 'category' as an attribute in godma.py::GetAttribute. We don't support that anymore")
        if attrKey == 'parent':
            return self.invitems[locationID]
        if attrKey == 'name':
            return evetypes.GetName(typeID)
        if attrKey == 'graphicID':
            return evetypes.GetGraphicID(typeID)
        if attrKey == 'iconID':
            return evetypes.GetIconID(typeID)
        if attrKey == 'effects':
            return self.effectsByItemEffect.get(itemKey, {})
        if attrKey == 'skills':
            raise RuntimeError("Godma::GetAttribute called for 'skills'")
        else:
            if attrKey == 'implants':
                return [ implant for implant in sm.StartService('skills').GetImplants().itervalues() ]
            if attrKey == 'boosters':
                boosters = [ booster for booster in sm.StartService('skills').GetBoosters().itervalues() ]
                for booster in boosters:
                    setattr(booster, 'typeID', booster.boosterTypeID)

                return boosters
            if attrKey == 'modules':
                li = []
                if itemKey in self.itemsByLocationID:
                    for itemKey2 in self.itemsByLocationID[itemKey]:
                        if self.invitems.has_key(itemKey2):
                            module = self.invitems[itemKey2]
                            if IsShipFittingFlag(module.flagID):
                                li.append(self.invitems[itemKey2].dbrow)

                return godmarowset.GodmaRowset(self.invitems.header, li, self.GetItemWrapper)
            if attrKey == 'sublocations':
                li = []
                if itemKey in self.sublocationsByLocationFlag:
                    li = [ i.dbrow for i in self.sublocationsByLocationFlag[itemKey].values() if IsShipFittingFlag(i[0][1]) ]
                return godmarowset.GodmaRowset(self.sublocationsByLocationFlag.header, li, self.GetItemWrapper)
        if not self.invitems.has_key(itemKey):
            raise RuntimeError('Item (or its parent) has not been primed', itemKey)
        loc = self.LocateItem(itemKey, attrKey)
        if loc is not None:
            return loc
        eff = self.GetEffect(itemKey, attrKey)
        if eff:
            return eff
        raise AttributeError, attrKey

    def GetEffectAttributeEx(self, eff, itemID, attribute):
        if attribute == 'item' or attribute == 'module':
            return self.GetItem(itemID)
        if attribute == 'trackingSpeed':
            trackingSpeedAttributeName = self.attributesByID[eff.trackingSpeedAttributeID].attributeName
            return self.GetAttribute(itemID, trackingSpeedAttributeName)
        if attribute == 'falloff':
            falloffAttributeName = self.attributesByID[eff.falloffAttributeID].attributeName
            return self.GetAttribute(itemID, falloffAttributeName)
        if attribute == 'range':
            rangeAttributeName = self.attributesByID[eff.rangeAttributeID].attributeName
            return self.GetAttribute(itemID, rangeAttributeName)

    def GetEffectWrapper(self, header, line):
        return EffectWrapper(self, header, line)

    def GetEffect(self, id, effect):
        if not self.effectsByItemEffect.has_key(id):
            return None
        if not self.effectsByItemEffect[id].has_key(effect):
            return None
        return self.effectsByItemEffect[id][effect]

    def GetDefaultEffect(self, typeID):
        if not self.defaultEffectsByType.has_key(typeID):
            possibleEffects = cfg.dgmtypeeffects.get(typeID, [])
            eff = None
            for effect in possibleEffects:
                if effect.isDefault:
                    eff = cfg.dgmeffects.Get(effect.effectID)

            if eff is None:
                return
            line = [None,
             eff.effectID,
             eff.effectName,
             eff.effectCategory,
             1,
             0,
             eff.isOffensive,
             eff.isAssistance,
             eff.description,
             eff.trackingSpeedAttributeID,
             eff.rangeAttributeID,
             eff.falloffAttributeID,
             eff.dischargeAttributeID,
             eff.durationAttributeID,
             eff.iconID,
             None,
             None,
             None,
             None,
             0]
            self.defaultEffectsByType[typeID] = EffectWrapper(self, self.__effectheader__, blue.DBRow(self.__effectheader__, line))
        return self.defaultEffectsByType[typeID]

    def TypeHasEffect(self, typeID, effectID):
        self.CacheTypeEffects(typeID)
        return self.effectsByType[typeID].has_key(effectID)

    def CacheTypeEffects(self, typeID):
        if not self.effectsByType.has_key(typeID):
            lines = []
            if cfg.dgmtypeeffects.has_key(typeID):
                lines = [ cfg.dgmeffects.Get(typeEffect.effectID) for typeEffect in cfg.dgmtypeeffects[typeID] ]
            self.effectsByType[typeID] = IndexRowset(cfg.dgmeffects.header, lines, 'effectID')

    def GetShipType(self, shipTypeID):
        return self.GetType(shipTypeID)

    def GetType(self, genericTypeID):
        self.InitializeData()
        if self.typeWrappers.has_key(genericTypeID):
            return self.typeWrappers[genericTypeID]
        result = TypeWrapper(self, genericTypeID)
        self.typeWrappers[genericTypeID] = result
        return result

    def GetChargeValue(self, oldVal, oldTime, tau, Ec, newTime = None):
        if Ec == 0:
            return 0
        if newTime is None:
            newTime = blue.os.GetSimTime()
        sq = math.sqrt(max(oldVal / Ec, 0))
        timePassed = min(oldTime - newTime, 0) / float(const.dgmTauConstant)
        exp = math.exp(timePassed / tau)
        ret = (1.0 + (sq - 1.0) * exp) ** 2 * Ec
        return ret

    def Activate(self, itemID, effectName, target, repeat):
        ret = None
        activateKey = (itemID, effectName)
        if activateKey in self.activatingEffects:
            self.godma.LogWarn('Trying to activate effect twice', effectName, itemID)
            return
        self.activatingEffects.add(activateKey)
        try:
            if target is not None and not isinstance(target, numbers.Integral):
                raise RuntimeError('InvalidTargetType', type(target))
            sm.GetService('invCache').TryLockItem(itemID, 'lockItemGodmaActivate', {}, 1)
            try:
                ret = self.GetDogmaLM().Activate(itemID, effectName, target, repeat)
                if effectName != 'online':
                    self.activatedLocation[itemID, effectName] = eve.session.locationid
                return ret
            finally:
                sm.GetService('invCache').UnlockItem(itemID)

        finally:
            self.activatingEffects.remove(activateKey)

    def Overload(self, itemID, effectID):
        self.GetDogmaLM().Overload(itemID, effectID)
        self.pendingOverloading.add(itemID)
        self.StopPendingStopOverloadModule(itemID)
        return itemID

    def OverloadRack(self, itemID):
        moduleIDs = self.GetDogmaLM().OverloadRack(itemID)
        for moduleID in moduleIDs:
            if not self.IsModuleOverloaded(moduleID):
                self.pendingOverloading.add(moduleID)

        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)
        return moduleIDs

    def Deactivate(self, itemID, effectName):
        sm.GetService('invCache').TryLockItem(itemID, 'lockItemGodmaDeactivate', {}, 1)
        try:
            if self.activatedLocation.has_key((itemID, effectName)) and self.activatedLocation[itemID, effectName] != eve.session.locationid:
                return
            if self.effectsByItemEffect.has_key(itemID) and self.effectsByItemEffect[itemID].has_key(effectName):
                self.effectsByItemEffect[itemID][effectName].isDeactivating = True
            return self.GetDogmaLM().Deactivate(itemID, effectName)
        finally:
            sm.GetService('invCache').UnlockItem(itemID)

    def StopOverload(self, itemID, effectID):
        self.GetDogmaLM().StopOverload(itemID, effectID)
        self.pendingStopOverloading.add(itemID)
        self.StopPendingOverloadModule(itemID)
        return itemID

    def StopOverloadRack(self, itemID):
        moduleIDs = self.GetDogmaLM().StopOverloadRack(itemID)
        self.pendingStopOverloading.update(moduleIDs)
        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)

    def StopPendingOverloadModule(self, itemID):
        try:
            self.pendingOverloading.remove(itemID)
        except KeyError:
            pass

        sm.ChainEvent('ProcessPendingOverloadUpdate', [itemID])

    def StopPendingStopOverloadModule(self, itemID):
        try:
            self.pendingStopOverloading.remove(itemID)
        except KeyError:
            pass

        sm.ChainEvent('ProcessPendingOverloadUpdate', [itemID])

    def IsModuleOverloaded(self, itemID):
        for effect in self.GetItem(itemID).effects.itervalues():
            if effect.effectCategory == const.dgmEffOverload and effect.isActive:
                return True

        return False

    def GetOverloadState(self, itemID):
        item = self.GetItem(itemID)
        for effectName, effect in item.effects.iteritems():
            if effect.effectCategory == const.dgmEffOverload and effect.isActive:
                if itemID in self.pendingStopOverloading:
                    return MODULE_PENDING_STOPOVERLOADING
                return MODULE_OVERLOADED
                break
        else:
            if itemID in self.pendingOverloading:
                return MODULE_PENDING_OVERLOADING
            return MODULE_NOT_OVERLOADED

    def ClearPendingOverloadingFlags(self):
        moduleIDs = self.pendingOverloading.copy()
        moduleIDs.update(self.pendingStopOverloading.copy())
        self.pendingOverloading.clear()
        self.pendingStopOverloading.clear()
        sm.ChainEvent('ProcessPendingOverloadUpdate', moduleIDs)

    def GetMaxDamagedModuleInGroup(self, shipID, itemID):
        moduleIDs = self.dogmaLocation.GetModulesInBank(shipID, itemID)
        if moduleIDs is None:
            item = self.GetItem(itemID)
            damage = item.damage if item else 0
            return (itemID, damage)
        maxDamage = 0
        for moduleID in moduleIDs:
            item = self.GetItem(moduleID)
            if not item:
                continue
            if item.damage > maxDamage:
                maxDamage = item.damage

        masterID = self.dogmaLocation.GetMasterModuleID(shipID, itemID)
        masterID = masterID if masterID is not None else itemID
        return (masterID, maxDamage)

    def RepairModule(self, itemID):
        timeStamp = blue.os.GetSimTime()
        res = self.GetDogmaLM().InitiateModuleRepair(itemID)
        if res == False:
            return False
        self.modulesBeingRepaired[itemID] = timeStamp
        uthread.pool('godma::RepairModule::RepairModule_thread', self.RepairModule_thread, itemID, timeStamp)
        return True

    def RepairModule_thread(self, itemID, timeStamp):
        dmg = self.GetAttribute(itemID, 'damage')
        owner = session.charid
        rateOfRepair = self.GetAttribute(owner, 'moduleRepairRate')
        timeToSleep = dmg / rateOfRepair
        timeToSleepMs = int(timeToSleep * 60 * 1000)
        blue.pyos.synchro.SleepSim(timeToSleepMs + 1000)
        if itemID in self.modulesBeingRepaired and self.modulesBeingRepaired[itemID] == timeStamp:
            self.StopRepairModule(itemID)

    def StopRepairModule(self, itemID):
        if self.modulesBeingRepaired.has_key(itemID):
            try:
                self.GetDogmaLM().StopModuleRepair(itemID)
            finally:
                sm.ScatterEvent('OnModuleRepaired', itemID)
                del self.modulesBeingRepaired[itemID]

    def GetRepairTimeStamp(self, itemID):
        return self.modulesBeingRepaired.get(itemID, None)

    def OnChargeBeingLoadedToModule(self, moduleIDs, chargeTypeID, durationTime):
        for eachModuleID in moduleIDs:
            self.modulesBeingReloaded[eachModuleID] = (blue.os.GetSimTime(), durationTime)

    def RemoveModulesBeingReloaded(self, moduleID):
        if moduleID in self.modulesBeingReloaded:
            del self.modulesBeingReloaded[moduleID]

    def GetReloadTimes(self, moduleID):
        return self.modulesBeingReloaded.get(moduleID, None)

    def GetCooldownTimes(self, moduleID):
        return self.lastStopTimesByItemID.get(moduleID, None)

    def RemoveOldCooldownTimers(self):
        now = blue.os.GetSimTime()
        for moduleID, times in self.lastStopTimesByItemID.items():
            time, delayTime = times
            if time + delayTime + 5 * const.SEC < now:
                del self.lastStopTimesByItemID[moduleID]

    def SendDroneSettings(self):
        droneSettingChanges = {const.attributeDroneIsAggressive: settings.char.ui.Get('droneAggression', cfg.dgmattribs.Get(const.attributeDroneIsAggressive).defaultValue),
         const.attributeFighterAttackAndFollow: settings.char.ui.Get('fighterAttackAndFollow', cfg.dgmattribs.Get(const.attributeFighterAttackAndFollow).defaultValue),
         const.attributeDroneFocusFire: settings.char.ui.Get('droneFocusFire', cfg.dgmattribs.Get(const.attributeDroneFocusFire).defaultValue)}
        self.GetDogmaLM().ChangeDroneSettings(droneSettingChanges)

    def ChangeDroneSettings(self, droneSettingChanges):
        validDroneSettingAttribs = [const.attributeDroneIsAggressive, const.attributeFighterAttackAndFollow, const.attributeDroneFocusFire]
        for key in droneSettingChanges:
            if key in validDroneSettingAttribs:
                self.droneSettingAttributes[key] = droneSettingChanges[key]
                continue
            else:
                return

        self.GetDogmaLM().ChangeDroneSettings(droneSettingChanges)

    def GetDroneSettingAttributes(self):
        return self.droneSettingAttributes

    def RefreshTargets(self):
        for objectID in self.GetDogmaLM().GetTargets():
            sm.ScatterEvent('OnTarget', 'add', objectID)

        for objectID in self.GetDogmaLM().GetTargeters():
            sm.ScatterEvent('OnTarget', 'otheradd', objectID)

    def Prime(self, shipID = None):
        self.godma.LogInfo('Prime')
        self.priming = True
        self.primingChannel = uthread.Channel(('godma::Prime', session.shipid))
        charFittedItems = []
        charBrain = ()
        self.InitializeData()
        dogmaLM = self.GetDogmaLM()
        self.godma.LogInfo('Godma Prime, shipID:', shipID)
        getShipInfo = False
        if shipID is not None and not self.invByID.has_key(shipID):
            getShipInfo = True
        getCharInfo = False
        if not self.invByID.has_key(session.charid):
            getCharInfo = True
        invCache = sm.GetService('invCache')
        charInv = invCache.GetInventoryFromId(session.charid, 1)
        if shipID is not None:
            shipInv = invCache.GetInventoryFromId(shipID, 1)
        else:
            shipInv = None
        if getCharInfo or getShipInfo:
            allInfo = dogmaLM.GetAllInfo(getCharInfo, getShipInfo)
        else:
            allInfo = None
        if allInfo is None:
            self.godma.LogInfo('Prime no dogma call needed')
        else:
            if allInfo.locationInfo is not None:
                self.ProcessLocationInfo(allInfo.locationInfo)
            self.godma.LogNotice('Prime reply received: (shipID, shipInfo, shipRow, charRow, charInfo, charInv, shipInv)', shipID, allInfo.Get('shipInfo', None) is not None, shipID in allInfo.Get('shipInfo', {}), session.charid in allInfo.Get('shipInfo', {}), allInfo.Get('charInfo', None) is not None, charInv is not None, shipInv is not None)
        charID = session.charid
        if shipID is not None:
            if not self.invByID.has_key(shipID):
                skips = set()
                if allInfo is not None:
                    if shipID in allInfo.shipInfo:
                        skips.add(shipID)
                        row = allInfo.shipInfo[shipID]
                        self.UpdateItem(row.invItem, row)
                    if charID in allInfo.shipInfo:
                        skips.add(charID)
                        row = allInfo.shipInfo[charID]
                        self.UpdateItem(row.invItem, row)
                    for itemID in allInfo.shipInfo.iterkeys():
                        if itemID in skips:
                            continue
                        row = allInfo.shipInfo[itemID]
                        self.UpdateItem(row.invItem, row)

            else:
                self.invitems[shipID].locationID = session.solarsystemid or session.stationid
            self.invByID[shipID] = shipInv
        if not self.invByID.has_key(charID):
            skips = set()
            if allInfo is not None:
                charFittedItems, charBrain = allInfo.charInfo
                if charID in charFittedItems:
                    skips.add(charID)
                    row = charFittedItems[charID]
                    self.UpdateItem(row.invItem, row)
                for itemID in charFittedItems.iterkeys():
                    if itemID in skips:
                        continue
                    row = charFittedItems[itemID]
                    self.UpdateItem(row.invItem, row)

        else:
            self.invitems[charID].locationID = shipID or session.stationid
        if allInfo is not None and allInfo.shipModifiedCharAttribs is not None:
            self.RefreshItemAttributes(session.charid, info=allInfo.shipModifiedCharAttribs, doUpdate=True)
        self.invByID[charID] = charInv
        self.priming = False
        while self.primingChannel.queue:
            self.godma.LogInfo('Prime - Channel send', shipID)
            self.primingChannel.send(True)

        self.primingChannel = None
        char = self.GetItem(charID)
        for att in ['memory',
         'perception',
         'willpower',
         'charisma',
         'intelligence']:
            sm.ScatterEvent('OnAttribute', att, char, getattr(char, att))

        if shipID is not None:
            sm.ScatterEvent('OnCapacityChange', shipID)
        if session.charid:
            self.dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation(charBrain=charBrain)
            if allInfo is not None:
                self.dogmaLocation.MakeShipActive(allInfo.activeShipID, allInfo.shipState)

    def PurgeInventories(self, keepList, skipCapacityEvent = False):
        self.godma.LogInfo('PurgeInventories: 1, Inventories.')
        for itemID in self.invByID.keys():
            if itemID not in keepList:
                self.PurgeEntries(itemID, skipCapacityEvent)
            else:
                for itemID2 in self.invitems.iterkeys():
                    if self.invitems[itemID2].locationID == itemID and not self.invByID.has_key(itemID2):
                        if self.effectsByItemEffect.has_key(itemID2):
                            for effect in self.effectsByItemEffect[itemID2].itervalues():
                                if effect.isActive and effect.effectCategory in (const.dgmEffActivation, const.dgmEffTarget) and effect.effectName != 'online':
                                    effect.isActive = 0
                                    effect.isDeactivating = False

        self.godma.LogInfo('PurgeInventories: 2, Locations.')
        for locationID in self.itemsByLocationID.keys():
            if locationID not in keepList:
                self.PurgeEntries(locationID, skipCapacityEvent)

    def PurgeEntries(self, locationID, skipCapacityEvent = False):
        self.godma.LogInfo('PurgeEntries', locationID, 'with pending', self.pending)
        if locationID in self.pending:
            self.godma.LogError('PurgeEntries: failed,', locationID, 'is marked as pending.')
            return
        if not (self.invByID.has_key(locationID) or locationID in self.itemsByLocationID):
            self.godma.LogError('PurgeEntries: failed,', locationID, 'is not primed.')
            return
        self.godma.LogInfo('PurgeEntries: Proceeding with', locationID)
        for itemID in self.invitems.keys():
            if self.invitems[itemID].locationID == locationID and not self.invByID.has_key(itemID):
                self.PurgeEntry(itemID)
                del self.invitems[itemID]

        for itemKey in self.sublocationsByKey.keys():
            if itemKey[0] == locationID:
                self.PurgeEntry(itemKey)
                try:
                    del self.sublocationsByKey[itemKey]
                    del self.sublocationsByLocationFlag[locationID][itemKey[1]]
                except KeyError:
                    self.godma.LogError("Failed to delete key because it wasn't there", locationID, self.sublocationsByKey, self.sublocationsByLocationFlag, itemKey)

        self.PurgeEntry(locationID)
        if self.invitems.has_key(locationID):
            del self.invitems[locationID]
        if self.invByID.has_key(locationID):
            del self.invByID[locationID]
        if locationID in self.itemsByLocationID:
            del self.itemsByLocationID[locationID]
        if not skipCapacityEvent:
            sm.ScatterEvent('OnCapacityChange', locationID)
        self.godma.LogInfo('PurgeEntries: Done with', locationID)

    def PurgeEntry(self, itemKey, locationID = None):
        if locationID is not None:
            self.godma.LogInfo('PurgeEntry', itemKey, locationID)
            if self.IsSubLocation(itemKey):
                if itemKey[0] == locationID:
                    del self.sublocationsByKey[itemKey]
                    del self.sublocationsByLocationFlag[locationID][itemKey[1]]
            elif self.invitems.has_key(itemKey):
                del self.invitems[itemKey]
                if itemKey in self.itemsByLocationID[locationID]:
                    self.itemsByLocationID[locationID].remove(itemKey)
        if self.effectsByItemEffect.has_key(itemKey):
            del self.effectsByItemEffect[itemKey]
        if self.attributesByItemAttribute.has_key(itemKey):
            del self.attributesByItemAttribute[itemKey]
        if self.chargedAttributesByItemAttribute.has_key(itemKey):
            del self.chargedAttributesByItemAttribute[itemKey]

    def ApplyAttributeChange(self, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr = True):
        item = None
        if self.invitems.has_key(itemKey):
            item = self.invitems[itemKey]
        elif self.sublocationsByKey.has_key(itemKey):
            item = self.sublocationsByKey[itemKey]
        if item is None or not self.attributesByItemAttribute.has_key(itemKey):
            if itemKey not in self.attributesByItemAttribute:
                self.godma.LogInfo('ApplyAttributeChange - item not found', item, ownerID, itemKey, attributeID, time, newValue, oldValue, scatterAttr)
            return
        attributeName = cfg.dgmattribs.Get(attributeID).attributeName
        att = getattr(item, attributeName, 'not there')
        argumentOldValue = oldValue
        oldValue = self.GetAttribute(itemKey, attributeName)
        if oldValue == newValue:
            self.godma.LogInfo('Reduntant update of attribute %s. Values are %s' % (attributeName, newValue))
            return
        self.godma.LogInfo('Processing attribute %s changing from %s (server sent oldVal as %s) to %s' % (attributeName,
         oldValue,
         argumentOldValue,
         newValue))
        self.attributesByItemAttribute[itemKey][attributeName] = newValue
        if self.chargedAttributeTauCaps.has_key(attributeName):
            if not self.chargedAttributesByItemAttribute.has_key(itemKey):
                self.chargedAttributesByItemAttribute[itemKey] = {}
            self.godma.LogInfo('Charge Attribute %s created with value %s' % (attributeName, newValue))
            self.CreateChargedAttribute(itemKey, attributeName, newValue, time, self.chargedAttributeTauCaps[attributeName])
        elif self.chargedAttributeTauCapsByMax.has_key(attributeName):
            for chargeAttName in self.chargedAttributeTauCapsByMax[attributeName]:
                self.godma.LogInfo('Processing chargedAttributeTauCapsByMax attribute %s for attribute %s' % (chargeAttName, attributeName))
                if self.chargedAttributesByItemAttribute.has_key(itemKey):
                    if self.chargedAttributesByItemAttribute[itemKey].has_key(chargeAttName):
                        charge = self.GetAttribute(itemKey, chargeAttName)
                        if oldValue != newValue:
                            maxChangeRatio = float(newValue) / oldValue
                            if charge == oldValue:
                                charge = charge * maxChangeRatio
                            if charge > newValue:
                                charge = newValue
                            self.godma.LogInfo('ChargedAttributeTauCapsByMax Attribute %s re-created with value %s' % (chargeAttName, charge))
                            self.CreateChargedAttribute(itemKey, chargeAttName, charge, time, self.chargedAttributeTauCaps[chargeAttName])
                        break
                    elif self.attributesByItemAttribute[itemKey].get(self.chargedAttributeTauCaps[chargeAttName][0]) and self.attributesByItemAttribute[itemKey].get(self.chargedAttributeTauCaps[chargeAttName][1]):
                        self.godma.LogInfo('ChargedAttributeTauCapsByMax Attribute %s initialized with value %s' % (chargeAttName, self.attributesByItemAttribute[itemKey][chargeAttName]))
                        self.CreateChargedAttribute(itemKey, chargeAttName, self.attributesByItemAttribute[itemKey][chargeAttName], time, self.chargedAttributeTauCaps[chargeAttName])
                        break

        elif self.chargedAttributesByTau.has_key(attributeName):
            for attName in self.chargedAttributesByTau[attributeName]:
                self.godma.LogInfo('Processing chargedAttributesByTau attribute %s for attribute %s' % (attName, attributeName))
                if self.chargedAttributesByItemAttribute.has_key(itemKey):
                    if self.chargedAttributesByItemAttribute[itemKey].has_key(attName):
                        charge = self.GetAttribute(itemKey, attName)
                        self.godma.LogInfo('ChargedAttributesByTau %s created with value %s' % (attName, charge))
                        self.CreateChargedAttribute(itemKey, attName, charge, time, self.chargedAttributeTauCaps[attName])
                        break

        self.godma.LogInfo('Attribute', attributeName, 'of module', itemKey, 'changed from', oldValue, 'to', newValue, 'value I had was', att)
        if attributeID in (const.attributeCapacity,
         const.attributeDroneCapacity,
         const.attributeShipMaintenanceBayCapacity,
         const.attributeFleetHangarCapacity):
            sm.ScatterEvent('OnCapacityChange', itemKey)
        elif attributeID == const.attributeQuantity:
            self.godma.LogInfo('Changing quantity from', att, 'to', newValue)
            if newValue == att:
                return
            locationID, flag, typeID = itemKey
            currSubLocation = self.GetSubLocation(locationID, flag)
            if currSubLocation and currSubLocation.typeID != typeID:
                self.godma.LogWarn("Trying to modify quantity of sublocation that isn't loaded with my type", currSubLocation, itemKey)
                return
            if newValue == 0:
                self.godma.LogInfo('SubLoc.quantityExpelled', itemKey, (oldValue, newValue))
                locationID, flag = itemKey[0], itemKey[1]
                if self.sublocationsByLocationFlag.has_key(locationID) and self.sublocationsByLocationFlag[locationID].has_key(flag):
                    del self.sublocationsByLocationFlag[locationID][flag]
                del self.sublocationsByKey[itemKey]
            item = blue.DBRow(self.godma.sublocrd, [itemKey,
             typeID,
             None,
             locationID,
             flag,
             newValue,
             evetypes.GetGroupID(typeID),
             evetypes.GetCategoryID(typeID),
             None])
            sm.ScatterEvent('OnItemChange', item, {const.ixStackSize: oldValue})
        if attributeID == const.attributeIsOnline:
            sm.ScatterEvent('OnModuleOnlineChange', item, oldValue, newValue)
            if newValue == 0 and oldValue == 1:
                if item.online.isActive:
                    self.godma.LogWarn('Module put offline silently, faking event', itemKey)
                    self.OnGodmaShipEffect(itemKey, const.effectOnline, blue.os.GetSimTime(), 0, 0, [itemKey,
                     item.ownerID,
                     item.locationID,
                     None,
                     None,
                     [],
                     const.effectOnline], None, -1, -1, None, None)
        if scatterAttr:
            sm.ScatterEvent('OnAttribute', attributeName, item, newValue)

    def OnJumpCloneTransitionCompleted(self):
        self.priming = True
        self.PurgeInventories([], skipCapacityEvent=True)
        self.dogmaLM = None
        self.godma.LogInfo('OnJumpCloneTransitionCompleted: Prime (pre)')
        self.Prime(session.shipid)
        self.godma.LogInfo('OnJumpCloneTransitionCompleted: Prime (post)')
        self.priming = False
        if session.stationid or session.solarsystemid:
            dogmaLM = self.GetDogmaLM()
            dogmaLM.Bind()
        sm.StartService('skills').OnJumpCloneTransitionCompleted()

    def CheckFutileSubSystemSwitch(self, typeID, itemID):
        flag = self.godma.GetTypeAttribute(typeID, const.attributeSubSystemSlot)
        if flag is None:
            return False
        ship = self.GetItem(session.shipid)
        slotOccupants = ship.GetSlotOccupants(flag)
        if len(slotOccupants) > 0:
            if slotOccupants[0].itemID == itemID:
                return True
            if slotOccupants[0].typeID == typeID:
                if eve.Message('SubSystemTypeAlreadyFitted', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                    return True
        return False

    def DelayedOnlineAttempt(self, shipID, moduleID, delay = 500):
        blue.pyos.synchro.SleepSim(delay)
        if shipID != session.shipid:
            return
        module = self.GetItem(moduleID)
        if module is None:
            return
        if 'online' not in module.effects:
            return
        effect = module.effects['online']
        if effect.isActive:
            return
        effect.Activate()

    def GetSensorStrengthAttribute(self, shipID):
        ret = None
        max = -1
        ship = self.GetItem(shipID)
        for attribute in ['scanGravimetricStrength',
         'scanLadarStrength',
         'scanMagnetometricStrength',
         'scanRadarStrength']:
            val = getattr(ship, attribute, None)
            if val > max:
                max = val
                ret = (attribute, val)

        return (self.attributesByName[ret[0]].attributeID, ret[1])

    def GetAttributeValueByID(self, itemID, attributeID):
        attribute = self.attributesByID.get(attributeID, None)
        if attribute is None:
            return
        return self.GetAttribute(itemID, attribute.attributeName)

    def CapacitorSimulator(self, capacitorCapacity = None, rechargeTime = None, runSimulation = False):
        if capacitorCapacity is None:
            capacitorCapacity = self.GetAttributeValueByID(session.shipid, const.attributeCapacitorCapacity)
        if rechargeTime is None:
            rechargeTime = self.GetAttributeValueByID(session.shipid, const.attributeRechargeRate)
        ship = self.GetItem(session.shipid)
        totalCapNeed = 0
        modules = []
        TTL = None
        for module in ship.modules:
            if not self.GetAttributeValueByID(module.itemID, const.attributeIsOnline):
                continue
            defaultEffect = self.GetDefaultEffect(module.typeID)
            if defaultEffect is None:
                continue
            durationAttributeID = defaultEffect.durationAttributeID
            dischargeAttributeID = defaultEffect.dischargeAttributeID
            if durationAttributeID is None or dischargeAttributeID is None:
                continue
            duration = self.GetAttributeValueByID(module.itemID, durationAttributeID)
            capNeed = self.GetAttributeValueByID(module.itemID, dischargeAttributeID)
            modules.append([capNeed, long(duration * 10000), 0])
            totalCapNeed += capNeed / duration

        rechargeRateAverage = capacitorCapacity / rechargeTime
        peakRechargeRate = 2.5 * rechargeRateAverage
        tau = rechargeTime / 5
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
        charge = capacitorCapacity
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

    def ChangeAmmoTypeForModule(self, moduleID, typeID):
        self.chargeTypeByModule[moduleID] = typeID

    def GetAmmoTypeForModule(self, moduleID):
        return self.chargeTypeByModule.get(moduleID, None)


exports = {'godma.MODULE_NOT_OVERLOADED': MODULE_NOT_OVERLOADED,
 'godma.MODULE_OVERLOADED': MODULE_OVERLOADED,
 'godma.MODULE_PENDING_OVERLOADING': MODULE_PENDING_OVERLOADING,
 'godma.MODULE_PENDING_STOPOVERLOADING': MODULE_PENDING_STOPOVERLOADING}
