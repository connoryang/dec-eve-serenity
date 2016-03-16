#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\graphicLocationUtil.py
import random
import log
import geo2
from eve.common.lib import appConst
DEFAULT_UNDOCKPOINT_CATEGORY = 'undockPoint'
SUPERCAPITAL_UNDOCKPOINT_CATEGORY = 'undockPoint_supercapital'
CAPITAL_UNDOCKPOINT_CATEGORY = 'undockPoint_capital'
LARGE_UNDOCKPOINT_CATEGORY = 'undockPoint_large'
SMALL_UNDOCKPOINT_CATEGORY = 'undockPoint_small'
STATION_SERVICE_FITTING_CATEGORY = 'fittingService'
STATION_SERVICE_REPAIR_FACILITIES_CATEGORY = 'repairFacilitiesService'
STATION_SERVICE_REPROCESSING_PLANE_CATEGORY = 'reprocessingPlantService'
STATION_SERVICE_CLONING_CATEGORY = 'cloningService'
STATION_SERVICE_FACTORY_CATEGORY = 'factoryService'
STATION_SERVICE_LABORATORY_CATEGORY = 'laboratoryService'
ALL_UNDOCK_CATEGORIES = (DEFAULT_UNDOCKPOINT_CATEGORY,
 SUPERCAPITAL_UNDOCKPOINT_CATEGORY,
 CAPITAL_UNDOCKPOINT_CATEGORY,
 LARGE_UNDOCKPOINT_CATEGORY,
 SMALL_UNDOCKPOINT_CATEGORY)
SERVICE_LOCATOR_MAPPING = {appConst.stationServiceFitting: STATION_SERVICE_FITTING_CATEGORY,
 appConst.stationServiceRepairFacilities: STATION_SERVICE_REPAIR_FACILITIES_CATEGORY,
 appConst.stationServiceReprocessingPlant: STATION_SERVICE_REPROCESSING_PLANE_CATEGORY,
 appConst.stationServiceCloning: STATION_SERVICE_CLONING_CATEGORY,
 appConst.stationServiceFactory: STATION_SERVICE_FACTORY_CATEGORY,
 appConst.stationServiceLaboratory: STATION_SERVICE_LABORATORY_CATEGORY}
DEFAULT_SERVICE_POSITIONS = {appConst.stationServiceFitting: geo2.Vector(-1000, 0, 0),
 appConst.stationServiceRepairFacilities: geo2.Vector(0, 1000, 0),
 appConst.stationServiceReprocessingPlant: geo2.Vector(0, -1000, 0),
 appConst.stationServiceCloning: geo2.Vector(1000, 0, 0),
 appConst.stationServiceFactory: geo2.Vector(0, 0, 1000),
 appConst.stationServiceLaboratory: geo2.Vector(0, 0, -1000)}

def GetStationUndockVectors(stationID, typeID = None):
    station = cfg.mapSolarSystemContentCache.npcStations.GetIfExists(stationID)
    typeID = getattr(station, 'typeID', typeID)
    locations = cfg.graphicLocations.GetIfExists(typeID)
    if locations is None:
        log.LogError("GetStationUndockVectors: Can't find locations with id %s and typeID %s" % (stationID, typeID))
        return (geo2.Vector(0.0, 0.0, 0.0), geo2.Vector(0.0, 0.0, 1.0))
    possibleLocators = []
    for directionalLocator in locations.directionalLocators:
        if directionalLocator.category in ALL_UNDOCK_CATEGORIES:
            possibleLocators.append((directionalLocator.position, directionalLocator.direction))

    return random.choice(possibleLocators)


def GetServiceLocatorPosition(typeID, serviceID):
    locations = cfg.graphicLocations.GetIfExists(typeID)
    if serviceID not in SERVICE_LOCATOR_MAPPING or locations is None and serviceID not in DEFAULT_SERVICE_POSITIONS:
        log.LogError("GetLocatorPosition: Can't find locationID with typeID %s for serviceID %s" % (typeID, serviceID))
        return geo2.Vector(0.0, 0.0, 0.0)
    if locations is None:
        log.LogInfo('GetLocatorPosition: Returning default positions for typeID %s and serviceID $s' % (typeID, serviceID))
        return DEFAULT_SERVICE_POSITIONS[serviceID]
    serviceCategory = SERVICE_LOCATOR_MAPPING[serviceID]
    for locator in locations.locators:
        if locator.category == serviceCategory:
            return locator.position

    return geo2.Vector(0.0, 0.0, 0.0)
