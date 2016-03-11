#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\fittingUtil.py
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes
import invCtrl
from inventorycommon.util import IsShipFittingFlag
from utillib import KeyVal
import inventorycommon.const as invConst
import dogma.const as dogmaConst
import carbonui.const as uiconst
import blue
FONTCOLOR_HILITE = '<color=0xffffff00>'
FONTCOLOR_DEFAULT = '<color=0xc0ffffff>'
FONTCOLOR_HILITE2 = 4294967040L
FONTCOLOR_DEFAULT2 = 3238002687L
PASSIVESHIELDRECHARGE = 0
SHIELDBOOSTRATEACTIVE = 1
ARMORREPAIRRATEACTIVE = 2
HULLREPAIRRATEACTIVE = 3
PANEL_WIDTH = 280
FITKEYS = ('Hi', 'Med', 'Lo')
NUM_SUBSYSTEM_SLOTS = 5
GHOST_FITTABLE_GROUPS = (const.categoryModule, const.categorySubSystem)

def GetTypeAttributesByID(typeID):
    if not typeID:
        return {}
    return {attribute.attributeID:attribute.value for attribute in cfg.dgmtypeattribs.get(typeID, [])}


def GetXtraColor2(xtra):
    if xtra != 0.0:
        return FONTCOLOR_HILITE2
    return FONTCOLOR_DEFAULT2


def GetMultiplyColor2(multiply):
    if multiply != 1.0:
        return FONTCOLOR_HILITE2
    return FONTCOLOR_DEFAULT2


def GetColor(xtra = 0.0, multi = 1.0):
    if multi != 1.0 or xtra != 0.0:
        return FONTCOLOR_HILITE
    return FONTCOLOR_DEFAULT


def GetColor2(xtra = 0.0, multi = 1.0):
    if multi != 1.0 or xtra != 0.0:
        return FONTCOLOR_HILITE2
    return FONTCOLOR_DEFAULT2


def GetXtraColor(xtra):
    if xtra != 0.0:
        return FONTCOLOR_HILITE
    return FONTCOLOR_DEFAULT


def GetMultiplyColor(multiply):
    if multiply != 1.0:
        return FONTCOLOR_HILITE
    return FONTCOLOR_DEFAULT


def GetShipAttribute(shipID, attributeID):
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    return GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, attributeID)


def GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, attributeID):
    if session.shipid == shipID:
        ship = sm.GetService('godma').GetItem(shipID)
        attributeName = dogmaLocation.dogmaStaticMgr.attributes[attributeID].attributeName
        return getattr(ship, attributeName)
    else:
        return dogmaLocation.GetAttributeValue(shipID, attributeID)


def GetSensorStrengthAttribute(dogmaLocation, shipID):
    if session.shipid == shipID:
        return sm.GetService('godma').GetStateManager().GetSensorStrengthAttribute(shipID)
    else:
        maxAttributeID = None
        maxValue = None
        for attributeID in dogmaConst.sensorStrength:
            val = dogmaLocation.GetAttributeValue(shipID, attributeID)
            if val > maxValue:
                maxValue, maxAttributeID = val, attributeID

        return (maxAttributeID, maxValue)


def GetFittingDragData():
    fittingSvc = sm.StartService('fittingSvc')
    fitting = KeyVal()
    fitting.shipTypeID, fitting.fitData = fittingSvc.GetFittingDictForActiveShip()
    fitting.fittingID = None
    fitting.description = ''
    fitting.name = cfg.evelocations.Get(GetActiveShip()).locationName
    fitting.ownerID = 0
    entry = KeyVal()
    entry.fitting = fitting
    entry.label = fitting.name
    entry.displayText = fitting.name
    entry.__guid__ = 'listentry.FittingEntry'
    return [entry]


def GetScaleFactor():
    dw = uicore.desktop.width
    minWidth = 1400
    return min(1.0, max(0.75, dw / float(minWidth)))


def GetBaseShapeSize():
    return int(640 * GetScaleFactor())


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) in (const.categoryCharge, const.groupFrequencyCrystal)


def GetPowerType(flagID):
    if flagID in invConst.loSlotFlags:
        return dogmaConst.effectLoPower
    if flagID in invConst.medSlotFlags:
        return dogmaConst.effectMedPower
    if flagID in invConst.hiSlotFlags:
        return dogmaConst.effectHiPower
    if flagID in invConst.subSystemSlotFlags:
        return dogmaConst.effectSubSystem
    if flagID in invConst.rigSlotFlags:
        return dogmaConst.effectRigSlot


def TryFit(invItems, shipID = None):
    if not shipID:
        shipID = GetActiveShip()
        if not shipID:
            return
    godma = sm.services['godma']
    invCache = sm.GetService('invCache')
    shipInv = invCache.GetInventoryFromId(shipID, locationID=session.stationid2)
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    godmaSM = godma.GetStateManager()
    useRigs = None
    charges = set()
    drones = []
    subSystemGroupIDs = set()
    for invItem in invItems[:]:
        if invItem.categoryID == const.categoryModule:
            moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
            for mEff in moduleEffects:
                if mEff.effectID == const.effectRigSlot:
                    if useRigs is None:
                        useRigs = True if RigFittingCheck(invItem) else False
                    if not useRigs:
                        invItems.remove(invItem)
                        invCache.UnlockItem(invItem.itemID)
                        break

        if invItem.categoryID == const.categorySubSystem:
            if invItem.groupID in subSystemGroupIDs:
                invItems.remove(invItem)
            else:
                subSystemGroupIDs.add(invItem.groupID)
        elif invItem.categoryID == const.categoryCharge:
            charges.add(invItem)
            invItems.remove(invItem)
        elif invItem.categoryID == const.categoryDrone:
            drones.append(invItem)
            invItems.remove(invItem)

    if len(invItems) > 0:
        shipInv.moniker.MultiAdd([ invItem.itemID for invItem in invItems ], invItems[0].locationID, flag=const.flagAutoFit)
    if charges:
        shipStuff = shipInv.List()
        shipStuff.sort(key=lambda r: (r.flagID, isinstance(r.itemID, tuple)))
        loadedSlots = set()
    if drones:
        invCtrl.ShipDroneBay(shipID or GetActiveShip()).AddItems(drones)
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    shipDogmaItem = dogmaLocation.dogmaItems.get(shipID, None)
    loadedSomething = False
    for DBRowInvItem in charges:
        invItem = KeyVal(DBRowInvItem)
        chargeDgmType = godmaSM.GetType(invItem.typeID)
        isCrystalOrScript = invItem.groupID in cfg.GetCrystalGroups()
        for row in shipStuff:
            if row in loadedSlots:
                continue
            if not IsShipFittingFlag(row.flagID):
                continue
            if dogmaLocation.IsInWeaponBank(row.locationID, row.itemID) and dogmaLocation.IsModuleSlave(row.itemID, row.locationID):
                continue
            if row.categoryID == const.categoryCharge:
                continue
            moduleDgmType = godmaSM.GetType(row.typeID)
            desiredSize = getattr(moduleDgmType, 'chargeSize', None)
            for x in xrange(1, 5):
                chargeGroup = getattr(moduleDgmType, 'chargeGroup%d' % x, False)
                if not chargeGroup:
                    continue
                if chargeDgmType.groupID != chargeGroup:
                    continue
                if desiredSize and getattr(chargeDgmType, 'chargeSize', -1) != desiredSize:
                    continue
                leftOvers = False
                for i, squatter in enumerate([ i for i in shipStuff if i.flagID == row.flagID ]):
                    if isCrystalOrScript and i > 0:
                        break
                    if shipDogmaItem is None:
                        continue
                    subLocation = dogmaLocation.GetSubLocation(shipID, squatter.flagID)
                    if subLocation is None:
                        continue
                    chargeVolume = chargeDgmType.volume * dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                    if godmaSM.GetType(row.typeID).capacity <= chargeVolume:
                        break
                else:
                    moduleCapacity = godmaSM.GetType(row.typeID).capacity
                    numCharges = moduleCapacity / chargeDgmType.volume
                    subLocation = dogmaLocation.GetSubLocation(shipID, row.flagID)
                    if subLocation:
                        numCharges -= dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                    dogmaLocation.LoadAmmoToModules(shipID, [row.itemID], invItem.typeID, invItem.itemID, invItem.locationID)
                    loadedSomething = True
                    invItem.stacksize -= numCharges
                    loadedSlots.add(row)
                    blue.pyos.synchro.SleepWallclock(100)
                    break

            else:
                continue

            if invItem.stacksize <= 0:
                break
        else:
            if not loadedSomething:
                uicore.Message('NoSuitableModules')


def RigFittingCheck(invItem):
    moduleEffects = cfg.dgmtypeeffects.get(invItem.typeID, [])
    for mEff in moduleEffects:
        if mEff.effectID == const.effectRigSlot:
            if uicore.Message('RigFittingInfo', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return False

    return True


class ModifiedAttribute(object):

    def __init__(self, value, multiplier = 1.0, addition = 0.0, higherIsBetter = True, oldValue = None, attributeID = None):
        self.baseValue = value
        self.multiplier = multiplier
        self.addition = addition
        self.higherIsBetter = higherIsBetter
        self.oldValue = oldValue
        self.attributeID = attributeID

    @property
    def value(self):
        return (self.baseValue + self.addition) * self.multiplier

    @value.setter
    def value(self, value):
        self.baseValue = value

    @property
    def diff(self):
        return self.value - self.baseValue

    @property
    def diffNormalized(self):
        if not self.higherIsBetter:
            return -self.diff
        else:
            return self.diff

    @property
    def isBetterThanBefore(self):
        if self.oldValue is None or self.value == self.oldValue:
            return
        else:
            currentIsHigher = self.value > self.oldValue
            if self.higherIsBetter:
                return currentIsHigher
            return not currentIsHigher


def GetDefensiveLayersInfo(controller):
    shieldResistanceInfo = {'em': controller.GetShieldEmDamageResonance(),
     'explosive': controller.GetShieldExplosiveDamageResonance(),
     'kinetic': controller.GetShieldKineticDamageResonance(),
     'thermal': controller.GetShieldThermalDamageResonance()}
    armorResistanceInfo = {'em': controller.GetArmorEmDamageResonance(),
     'explosive': controller.GetArmorExplosiveDamageResonance(),
     'kinetic': controller.GetArmorKineticDamageResonance(),
     'thermal': controller.GetArmorThermalDamageResonance()}
    structureResistanceInfo = {'em': controller.GetStructureEmDamageResonance(),
     'explosive': controller.GetStructureExplosiveDamageResonance(),
     'kinetic': controller.GetStructureKineticDamageResonance(),
     'thermal': controller.GetStructureThermalDamageResonance()}
    allLayersInfo = {'shield': KeyVal(resistances=shieldResistanceInfo, hpInfo=controller.GetShieldHp(), isRechargable=True),
     'armor': KeyVal(resistances=armorResistanceInfo, hpInfo=controller.GetArmorHp(), isRechargable=False),
     'structure': KeyVal(resistances=structureResistanceInfo, hpInfo=controller.GetStructureHp(), isRechargable=False)}
    return allLayersInfo


def GetEffectiveHp(controller):
    effectiveHp = 0.0
    allDefensiveLayersInfo = GetDefensiveLayersInfo(controller)
    for whatLayer, layerInfo in allDefensiveLayersInfo.iteritems():
        minResistance = 0.0
        layerHp = layerInfo.hpInfo.value
        layerResistancesInfo = layerInfo.resistances
        for dmgType, valueInfo in layerResistancesInfo.iteritems():
            value = valueInfo.value
            minResistance = max(minResistance, value)

        if minResistance:
            effectiveHpForLayer = layerHp / minResistance
            effectiveHp += effectiveHpForLayer

    return effectiveHp
