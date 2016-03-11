#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evePathfinder\factory.py
import pyEvePathfinder
from . import core
from inventorycommon.util import IsWormholeRegion

def CreatePathfinder(mapRegionCache, mapSystemCache, mapJumpCache):
    eveMap = pyEvePathfinder.EveMap()
    for regionID, regionItem in mapRegionCache.iteritems():
        eveMap.CreateRegion(regionID)
        for constellationID in regionItem.constellationIDs:
            eveMap.CreateConstellation(constellationID, regionID)

    for solarSystemID, ssInfo in mapSystemCache.iteritems():
        eveMap.CreateSolarSystem(solarSystemID, ssInfo.constellationID, ssInfo.securityStatus)

    for jump in mapJumpCache:
        eveMap.AddJump(jump.fromSystemID, jump.toSystemID, jump.stargateID)
        eveMap.AddJump(jump.toSystemID, jump.fromSystemID, jump.stargateID)

    eveMap.Finalize()
    return core.EvePathfinderCore(eveMap)
