#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\fittingDogmaLocationUtil.py
from math import sqrt, log, exp
import math
from carbonui.util.bunch import Bunch
import evetypes
from utillib import KeyVal
DAMAGE_ATTRIBUTES = (const.attributeEmDamage,
 const.attributeExplosiveDamage,
 const.attributeKineticDamage,
 const.attributeThermalDamage)

def GetFittingItemDragData(itemID, dogmaLocation):
    dogmaItem = dogmaLocation.dogmaItems[itemID]
    data = Bunch()
    data.__guid__ = 'listentry.InvItem'
    data.item = KeyVal(itemID=dogmaItem.itemID, typeID=dogmaItem.typeID, groupID=dogmaItem.groupID, categoryID=dogmaItem.categoryID, flagID=dogmaItem.flagID, ownerID=dogmaItem.ownerID, locationID=dogmaItem.locationID, stacksize=dogmaLocation.GetAttributeValue(itemID, const.attributeQuantity))
    data.rec = data.item
    data.itemID = itemID
    data.viewMode = 'icons'
    return [data]


def GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones):
    droneInfo = {}
    for droneID in activeDrones:
        damage = GetDamageFromItem(dogmaLocation, droneID)
        if damage == 0:
            continue
        damageMultiplier = dogmaLocation.GetAttributeValue(droneID, const.attributeDamageMultiplier)
        if damageMultiplier == 0:
            continue
        duration = dogmaLocation.GetAttributeValue(droneID, const.attributeRateOfFire)
        droneDps = damage * damageMultiplier / duration
        droneBandwidth = dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)
        droneDogmaItem = dogmaLocation.dogmaItems[droneID]
        droneInfo[droneID] = (droneDogmaItem.typeID, droneBandwidth, droneDps)

    return droneInfo


def GetSimpleGetDroneDamageOutput(drones, bwLeft, dronesLeft):
    totalDps = 0
    for droneID, droneInfo in drones.iteritems():
        typeID, bwNeeded, dps = droneInfo
        qty = 1
        noOfDrones = min(int(bwLeft) / int(bwNeeded), qty, dronesLeft)
        if noOfDrones == 0:
            break
        totalDps += qty * dps
        dronesLeft -= qty
        bwLeft -= qty * bwNeeded

    return totalDps


def GetOptimalDroneDamage(shipID, dogmaLocation, activeDrones):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    droneInfo = GatherDroneInfo(shipDogmaItem, dogmaLocation, activeDrones)
    dogmaLocation.LogInfo('Gathered drone info and found', len(droneInfo), 'types of drones')
    bandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    maxDrones = dogmaLocation.GetAttributeValue(session.charid, const.attributeMaxActiveDrones)
    dps = GetSimpleGetDroneDamageOutput(droneInfo, bandwidth, maxDrones)
    return (dps * 1000, {})


def GetDroneRanges(shipID, dogmaLocation, activeDrones):
    maxRangeOfAll = 0
    minRangeOfAll = 0
    for droneID in activeDrones:
        maxRange = dogmaLocation.GetAttributeValue(droneID, const.attributeMaxRange)
        maxRangeOfAll = max(maxRangeOfAll, maxRange)
        if not minRangeOfAll:
            minRangeOfAll = maxRange
        else:
            minRangeOfAll = min(minRangeOfAll, maxRange)

    return (minRangeOfAll, maxRangeOfAll)


def GetDroneBandwidth(shipID, dogmaLocation, activeDrones):
    shipBandwidth = dogmaLocation.GetAttributeValue(shipID, const.attributeDroneBandwidth)
    bandwidthUsed = 0
    for droneID in activeDrones:
        bandwidthUsed += dogmaLocation.GetAttributeValue(droneID, const.attributeDroneBandwidthUsed)

    return (bandwidthUsed, shipBandwidth)


def GetFittedItemsByFlag(dogmaLocation, typeHasEffectFunc):
    chargesByFlag = {}
    turretsByFlag = {}
    launchersByFlag = {}
    IsTurret = lambda typeID: typeHasEffectFunc(typeID, const.effectTurretFitted)
    IsLauncher = lambda typeID: typeHasEffectFunc(typeID, const.effectLauncherFitted)
    for module in dogmaLocation.GetFittedItemsToShip().itervalues():
        if IsTurret(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            turretsByFlag[module.flagID] = module.itemID
        elif IsLauncher(module.typeID):
            if not dogmaLocation.IsModuleIncludedInCalculation(module):
                continue
            launchersByFlag[module.flagID] = module.itemID
        elif module.categoryID == const.categoryCharge:
            chargesByFlag[module.flagID] = module.itemID

    return (chargesByFlag, launchersByFlag, turretsByFlag)


def _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag):
    turretDps = 0
    for flagID, itemID in turretsByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        thisTurretDps = GetTurretDps(dogmaLocation, chargeKey, itemID, GAV)
        turretDps += thisTurretDps

    return turretDps


def _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem):
    missileDps = 0
    for flagID, itemID in launchersByFlag.iteritems():
        chargeKey = chargesByFlag.get(flagID)
        if chargeKey is None:
            continue
        ownerID = session.charid
        thisLauncherDps = GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV)
        missileDps += thisLauncherDps

    return missileDps


def GetTurretAndMissileDps(shipID, dogmaLocation, typeHasEffectFunc):
    shipDogmaItem = dogmaLocation.dogmaItems[shipID]
    godmaShipItem = dogmaLocation.godma.GetItem(shipID)
    GAV = dogmaLocation.GetAttributeValue
    chargesByFlag, launchersByFlag, turretsByFlag = GetFittedItemsByFlag(dogmaLocation, typeHasEffectFunc)
    turretDps = _GetTurretDps(GAV, chargesByFlag, dogmaLocation, turretsByFlag)
    missileDps = _GetMissileDps(GAV, chargesByFlag, dogmaLocation, launchersByFlag, shipDogmaItem)
    return (turretDps, missileDps)


def GetLauncherDps(dogmaLocation, chargeKey, itemID, ownerID, GAV, damageMultiplier = None):
    damage = GetDamageFromItem(dogmaLocation, chargeKey)
    duration = GAV(itemID, const.attributeRateOfFire)
    if damageMultiplier is None:
        damageMultiplier = GAV(ownerID, const.attributeMissileDamageMultiplier)
    missileDps = damage * damageMultiplier / duration
    return missileDps * 1000


def GetTurretDps(dogmaLocation, chargeKey, itemID, GAV, *args):
    turretDps = 0.0
    if chargeKey is not None:
        damage = GetDamageFromItem(dogmaLocation, chargeKey)
    else:
        damage = GetDamageFromItem(dogmaLocation, itemID)
    if abs(damage) > 0:
        damageMultiplier = GAV(itemID, const.attributeDamageMultiplier)
        duration = GAV(itemID, const.attributeRateOfFire)
        if abs(duration) > 0:
            turretDps = damage * damageMultiplier / duration
    return turretDps * 1000


def GetDamageFromItem(dogmaLocation, itemID):
    accDamage = 0
    for attributeID in DAMAGE_ATTRIBUTES:
        d = dogmaLocation.GetAttributeValue(itemID, attributeID)
        accDamage += d

    return accDamage


def CheckCanFitType(dogmaLocation, typeID, locationID):
    maxGroupFitted = dogmaLocation.dogmaStaticMgr.GetTypeAttribute(typeID, const.attributeMaxGroupFitted)
    if maxGroupFitted is None:
        return
    groupID = evetypes.GetGroupID(typeID)
    modulesByGroup = dogmaLocation.GetModuleListByShipGroup(locationID, groupID)
    if len(modulesByGroup) >= maxGroupFitted:
        shipItem = dogmaLocation.dogmaItems[locationID]
        raise UserError('CantFitTooManyByGroup', {'ship': shipItem.typeID,
         'module': typeID,
         'groupName': evetypes.GetGroupName(typeID),
         'noOfModules': int(maxGroupFitted),
         'noOfModulesFitted': len(modulesByGroup)})


def CanFitModuleToShipTypeOrGroup(dogmaLocation, typeID):
    shipItem = dogmaLocation.dogmaItems[dogmaLocation.shipID]
    return GetFitModuleTypeToShipType(dogmaLocation, shipItem.typeID, typeID)


def GetFitModuleTypeToShipType(dogmaLocation, shipTypeID, moduleTypeID):
    groupID = evetypes.GetGroupID(shipTypeID)
    return dogmaLocation.dogmaStaticMgr.CanFitModuleToShipTypeOrGroup(moduleTypeID, shipTypeID, groupID)


def IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize):
    if not dogmaStaticMgr.TypeHasEffect(moduleTypeID, const.effectRigSlot):
        return False
    rigSize = dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeRigSize)
    if shipRigSize != rigSize:
        return True
    return False


def CapacitorSimulator(dogmaLocation, shipID):
    dogmaItem = dogmaLocation.dogmaItems[shipID]
    capacitorCapacity = dogmaLocation.GetAttributeValue(shipID, const.attributeCapacitorCapacity)
    rechargeTime = dogmaLocation.GetAttributeValue(shipID, const.attributeRechargeRate)
    modules = []
    totalCapNeed = 0
    for moduleID, module in dogmaItem.GetFittedItems().iteritems():
        if not module.IsOnline():
            continue
        try:
            defaultEffectID = dogmaLocation.dogmaStaticMgr.GetDefaultEffect(module.typeID)
        except KeyError:
            defaultEffectID = None

        if defaultEffectID is None:
            continue
        defaultEffect = dogmaLocation.dogmaStaticMgr.effects[defaultEffectID]
        durationAttributeID = defaultEffect.durationAttributeID
        dischargeAttributeID = defaultEffect.dischargeAttributeID
        if durationAttributeID is None or dischargeAttributeID is None:
            continue
        duration = dogmaLocation.GetAttributeValue(moduleID, durationAttributeID)
        capNeed = dogmaLocation.GetAttributeValue(moduleID, dischargeAttributeID)
        modules.append([capNeed, long(duration * const.dgmTauConstant), 0])
        totalCapNeed += capNeed / duration

    rechargeRateAverage = capacitorCapacity / rechargeTime
    peakRechargeRate = 2.5 * rechargeRateAverage
    tau = rechargeTime / 5
    TTL = None
    if totalCapNeed > peakRechargeRate:
        TTL = RunSimulation(capacitorCapacity, rechargeTime, modules)
        loadBalance = 0
    else:
        c = 2 * capacitorCapacity / tau
        k = totalCapNeed / c
        exponent = (1 - sqrt(1 - 4 * k)) / 2
        if exponent == 0:
            loadBalance = 1
        else:
            t = -log(exponent) * tau
            loadBalance = (1 - exp(-t / tau)) ** 2
    return (peakRechargeRate,
     totalCapNeed,
     loadBalance,
     TTL)


def RunSimulation(capacitorCapacity, rechargeRate, modules):
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
