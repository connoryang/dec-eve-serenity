#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewData.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.mapView.mapViewUtil import WorldPosToMapPos
from eve.client.script.ui.shared.maps.mapcommon import SUN_DATA
from inventorycommon.util import IsWormholeConstellation, IsWormholeRegion, IsWormholeSystem
from utillib import KeyVal
import cPickle
import blue
import logging
log = logging.getLogger(__name__)

class MapViewData(object):
    starMapCache = None
    knownSolarSystems = None
    knownRegions = None
    knownConstellations = None
    mapJumps = None

    def GetStarMapCache(self):
        if self.starMapCache is None:
            res = blue.ResFile()
            starMapResPath = 'res:/staticdata/starMapCache.pickle'
            if not res.open('%s' % starMapResPath):
                log.error('Could not load Starmap Cache data file: %s' % starMapResPath)
            else:
                try:
                    pickleData = res.Read()
                    self.starMapCache = cPickle.loads(pickleData)
                finally:
                    res.Close()

        return self.starMapCache

    def GetKnownUniverseSolarSystems(self):
        if self.knownSolarSystems is None:
            self.knownSolarSystems = {}
            for systemID, system in self.GetStarMapCache()['solarSystems'].iteritems():
                if IsWormholeSystem(systemID):
                    continue
                center = system['center']
                solarSystemInfo = Bunch()
                solarSystemInfo.center = center
                solarSystemInfo.mapPosition = WorldPosToMapPos(center)
                solarSystemInfo.regionID = system['regionID']
                solarSystemInfo.constellationID = system['constellationID']
                solarSystemInfo.star = SUN_DATA[system['sunTypeID']]
                solarSystemInfo.factionID = system['factionID']
                solarSystemInfo.neighbours = system['neighbours']
                solarSystemInfo.planetCountByType = system['planetCountByType']
                self.knownSolarSystems[systemID] = solarSystemInfo

        return self.knownSolarSystems

    def GetKnownUniverseRegions(self):
        if self.knownRegions is None:
            self.knownRegions = {}
            for regionID, region in self.GetStarMapCache()['regions'].iteritems():
                if IsWormholeRegion(regionID):
                    continue
                regionInfo = Bunch()
                regionInfo.neighbours = region['neighbours']
                regionInfo.solarSystemIDs = region['solarSystemIDs']
                regionInfo.constellationIDs = region['constellationIDs']
                regionInfo.center = region['center']
                regionInfo.mapPosition = WorldPosToMapPos(region['center'])
                self.knownRegions[regionID] = regionInfo

        return self.knownRegions

    def GetKnownUniverseConstellations(self):
        if self.knownConstellations is None:
            self.knownConstellations = {}
            for constellationID, constellation in self.GetStarMapCache()['constellations'].iteritems():
                if IsWormholeConstellation(constellationID):
                    continue
                constellationInfo = Bunch()
                constellationInfo.regionID = constellation['regionID']
                constellationInfo.neighbours = constellation['neighbours']
                constellationInfo.solarSystemIDs = constellation['solarSystemIDs']
                constellationInfo.center = constellation['center']
                constellationInfo.mapPosition = WorldPosToMapPos(constellation['center'])
                self.knownConstellations[constellationID] = constellationInfo

        return self.knownConstellations

    def GetKnownSolarSystem(self, solarSystemID):
        return self.GetKnownUniverseSolarSystems()[solarSystemID]

    def GetKnownConstellation(self, constellationID):
        return self.GetKnownUniverseConstellations()[constellationID]

    def GetKnownRegion(self, regionID):
        return self.GetKnownUniverseRegions()[regionID]

    def GetAllianceSolarSystems(self):
        allianceSolarSystems = {}
        allianceSystemCache = sm.RemoteSvc('stationSvc').GetAllianceSystems()
        for x in allianceSystemCache:
            allianceSolarSystems[x.solarSystemID] = x.allianceID

        facwarSystems = sm.GetService('facwar').GetFacWarSystemsOccupiers()
        for systemID, occupierID in facwarSystems.iteritems():
            allianceSolarSystems[systemID] = occupierID

        return allianceSolarSystems

    def GetAllFactions(self):
        return list(cfg.mapFactionsOwningSolarSystems)

    def GetAllFactionsAndAlliances(self):
        factions = self.GetAllFactions()
        alliances = self.GetAllianceSolarSystems().values()
        return list(set(factions + alliances))

    def IterateJumps(self):
        if self.mapJumps is None:
            self.mapJumps = []
            for jump in self.GetStarMapCache()['jumps']:
                jumpInfo = self.PrimeJumpData(jump['fromSystemID'], jump['toSystemID'], jump['jumpType'])
                self.mapJumps.append(jumpInfo)
                yield jumpInfo

        else:
            for jump in self.mapJumps:
                yield jump

    def PrimeJumpData(self, fromSolarSystemID, toSolarSystemID, jumpType):
        jumpInfo = KeyVal()
        jumpInfo.jumpType = jumpType
        jumpInfo.fromSolarSystemID = fromSolarSystemID
        jumpInfo.toSolarSystemID = toSolarSystemID
        return jumpInfo


mapViewData = MapViewData()
