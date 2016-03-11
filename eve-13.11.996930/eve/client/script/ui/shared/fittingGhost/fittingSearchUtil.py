#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingSearchUtil.py
import itertools
from eve.common.lib.appConst import GROUP_CAPITALSHIPS
import evetypes
from shipfitting.fittingDogmaLocationUtil import CanFitModuleToShipTypeOrGroup, IsRigSizeRestricted
from shipfitting.fittingStuff import IsModuleTooBig, GetSlotTypeForType

class SearchFittingHelper(object):

    def __init__(self, cfg, *args):
        self.cfg = cfg
        self.dogmaStaticMgr = sm.GetService('clientDogmaIM').GetDogmaLocation().dogmaStaticMgr
        self.typeNames_lower = {}
        self.canFitModuleToShip = {}
        self.rigRestricted = {}
        self.tooBigModule = {}
        self.slotTypeByTypeID = {}
        self.shipRigSizeByTypeID = {}
        self.isCapitalShipByTypeID = {}
        self.marketCategoryByTypeID = {}
        self.isHiSlot = {}
        self.isMedSlot = {}
        self.isLoSlot = {}
        self.isRigSlot = {}
        self.cpuRequirementsByModuleTypeID = {}
        self.powergridRequirementsByModuleTypeID = {}
        self.searchableTypeIDs = None

    def GetTypeName(self, typeID):
        try:
            return self.typeNames_lower[typeID]
        except KeyError:
            t = evetypes.GetName(typeID)
            lower = t.lower()
            self.typeNames_lower[typeID] = lower
            return lower

    def CanFitModuleToShipTypeOrGroup(self, shipTypeID, dogmaLocation, moduleTypeID):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.canFitModuleToShip[dictKey]
        except KeyError:
            canFit = CanFitModuleToShipTypeOrGroup(dogmaLocation, moduleTypeID)
            self.canFitModuleToShip[dictKey] = canFit
            return canFit

    def IsRigSizeRestricted(self, dogmaStaticMgr, moduleTypeID, shipRigSize):
        dictKey = (moduleTypeID, shipRigSize)
        try:
            return self.rigRestricted[dictKey]
        except KeyError:
            isRestricted = IsRigSizeRestricted(dogmaStaticMgr, moduleTypeID, shipRigSize)
            self.rigRestricted[dictKey] = isRestricted
            return isRestricted

    def IsModuleTooBig(self, shipTypeID, moduleTypeID, isCapitalShip):
        dictKey = (shipTypeID, moduleTypeID)
        try:
            return self.tooBigModule[dictKey]
        except KeyError:
            tooBig = IsModuleTooBig(moduleTypeID, shipTypeID, isCapitalShip)
            self.tooBigModule[dictKey] = tooBig
            return tooBig

    def IsHislotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectHiPower, self.isHiSlot)

    def IsMedslotModule(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectMedPower, self.isMedSlot)

    def IsLoSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectLoPower, self.isLoSlot)

    def IsRigSlot(self, moduleTypeID):
        return self.IsSpecificSlotType(moduleTypeID, const.effectRigSlot, self.isRigSlot)

    def IsSpecificSlotType(self, moduleTypeID, slotTypeWanted, cacheDict):
        try:
            return cacheDict[moduleTypeID]
        except KeyError:
            slotType = self.GetSlotTypeForModuleType(moduleTypeID)
            if slotType == slotTypeWanted:
                isRightType = True
            else:
                isRightType = False
            cacheDict[moduleTypeID] = isRightType
            return isRightType

    def GetSlotTypeForModuleType(self, moduleTypeID):
        try:
            return self.slotTypeByTypeID[moduleTypeID]
        except KeyError:
            slotType = GetSlotTypeForType(moduleTypeID)
            self.slotTypeByTypeID[moduleTypeID] = slotType
            return slotType

    def GetShipRigSize(self, dogmaStaticMgr, shipTypeID):
        try:
            return self.shipRigSizeByTypeID[shipTypeID]
        except KeyError:
            rigSize = dogmaStaticMgr.GetTypeAttribute2(shipTypeID, const.attributeRigSize)
            self.shipRigSizeByTypeID[shipTypeID] = rigSize
            return rigSize

    def IsCapitalSize(self, groupID):
        try:
            return self.isCapitalShipByTypeID[groupID]
        except KeyError:
            isCapitalSize = groupID in self.cfg.GetShipGroupByClassType()[GROUP_CAPITALSHIPS]
            self.isCapitalShipByTypeID[groupID] = isCapitalSize
            return isCapitalSize

    def GetCPUForModuleType(self, moduleTypeID):
        try:
            return self.cpuRequirementsByModuleTypeID[moduleTypeID]
        except KeyError:
            cpu = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributeCpu)
            self.cpuRequirementsByModuleTypeID[moduleTypeID] = cpu
            return cpu

    def GetPowergridForModuleType(self, moduleTypeID):
        try:
            return self.powergridRequirementsByModuleTypeID[moduleTypeID]
        except KeyError:
            power = self.dogmaStaticMgr.GetTypeAttribute2(moduleTypeID, const.attributePower)
            self.powergridRequirementsByModuleTypeID[moduleTypeID] = power
            return power

    def GetSearcableTypeIDs(self, marketGroups):
        if not self.searchableTypeIDs:
            marketGroups = sm.GetService('marketutils').GetMarketGroups()
            myGroups = marketGroups[const.marketCategoryShipEquipment] + marketGroups[const.marketCategoryShipModifications]
            typeIDs = [ i for i in itertools.chain.from_iterable([ x.types for x in myGroups ]) ]
            self.searchableTypeIDs = typeIDs
        return self.searchableTypeIDs

    def GetMarketCategoryForType(self, typeID, allMarketGroups):
        try:
            return self.marketCategoryByTypeID[typeID]
        except KeyError:
            for mg in allMarketGroups:
                if typeID in mg.types:
                    topMarketCategory = mg
                    break
            else:
                topMarketCategory = None

            self.marketCategoryByTypeID[typeID] = topMarketCategory
