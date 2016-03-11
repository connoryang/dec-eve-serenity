#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\browsers\filtering.py
import evetypes
from utillib import KeyVal

def GetFilters():
    slotFilterInfo = KeyVal(showHiSlots=settings.user.ui.Get('fitting_filter_hardware_hiSlot', False), showMedSlots=settings.user.ui.Get('fitting_filter_hardware_medSlot', False), showLoSlots=settings.user.ui.Get('fitting_filter_hardware_loSlot', False), showRigSlots=settings.user.ui.Get('fitting_filter_hardware_rigSlot', False))
    filters = KeyVal(filterByShipCanUse=settings.user.ui.Get('fitting_filter_hardware_fitShip', False), filterString=settings.user.ui.Get('fitting_hardwareSearchField', '').lower(), filterOnCpu=settings.user.ui.Get('fitting_filter_hardware_cpu', False), filterOnPowergrid=settings.user.ui.Get('fitting_filter_hardware_powergrid', False), slotFilterInfo=slotFilterInfo)
    return filters


def GetCpuAndPowerLeft(dogmaLocation):
    cpuOutput = dogmaLocation.GetAttributeValue(dogmaLocation.shipID, const.attributeCpuOutput)
    cpuUsed = dogmaLocation.GetAttributeValue(dogmaLocation.shipID, const.attributeCpuLoad)
    cpuLeft = cpuOutput - cpuUsed
    powerOutput = dogmaLocation.GetAttributeValue(dogmaLocation.shipID, const.attributePowerOutput)
    powerUsed = dogmaLocation.GetAttributeValue(dogmaLocation.shipID, const.attributePowerLoad)
    powerLeft = powerOutput - powerUsed
    return (cpuLeft, powerLeft)


def GetValidTypeIDs(typeList, searchFittingHelper):
    filters = GetFilters()
    fittingHelper = searchFittingHelper
    dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
    shipTypeID = dogmaLocation.dogmaItems[dogmaLocation.shipID].typeID
    dogmaStaticMgr = dogmaLocation.dogmaStaticMgr
    shipRigSize = fittingHelper.GetShipRigSize(dogmaStaticMgr, shipTypeID)
    isCapitalShip = fittingHelper.IsCapitalSize(evetypes.GetGroupID(shipTypeID))
    cpuLeft, powerLeft = GetCpuAndPowerLeft(dogmaLocation)
    ret = []
    for typeID in typeList:
        if filters.filterByShipCanUse:
            if not fittingHelper.CanFitModuleToShipTypeOrGroup(shipTypeID, dogmaLocation, typeID):
                pass
            if fittingHelper.IsRigSizeRestricted(dogmaStaticMgr, typeID, shipRigSize):
                pass
            if fittingHelper.IsModuleTooBig(shipTypeID, typeID, isCapitalShip):
                pass
        filterOutFromSlotType = DoSlotTypeFiltering(fittingHelper, typeID, filters.slotFilterInfo)
        if filterOutFromSlotType:
            continue
        if filters.filterOnCpu:
            usedByType = fittingHelper.GetCPUForModuleType(typeID)
            if usedByType > cpuLeft:
                continue
        if filters.filterOnPowergrid:
            usedByType = fittingHelper.GetPowergridForModuleType(typeID)
            if usedByType > powerLeft:
                continue
        if not filters.filterString or fittingHelper.GetTypeName(typeID).find(filters.filterString) > -1:
            ret.append(typeID)

    return ret


def DoSlotTypeFiltering(fittingHelper, moduleTypeID, filterInfo):
    if filterInfo.showHiSlots + filterInfo.showLoSlots + filterInfo.showMedSlots + filterInfo.showRigSlots in (0,):
        return False
    toCheck = [(filterInfo.showHiSlots, fittingHelper.IsHislotModule),
     (filterInfo.showLoSlots, fittingHelper.IsLoSlot),
     (filterInfo.showMedSlots, fittingHelper.IsMedslotModule),
     (filterInfo.showRigSlots, fittingHelper.IsRigSlot)]
    for doCheck, checkFunc in toCheck:
        if doCheck:
            isSlotType = checkFunc(moduleTypeID)
            if isSlotType:
                return False

    return True
