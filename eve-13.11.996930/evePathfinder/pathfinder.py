#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evePathfinder\pathfinder.py
from collections import defaultdict
import sys
from inventorycommon.util import IsWormholeSystem

class ClientPathfinder(object):

    def __init__(self, pathfinderCore, standardStateInterface, autopilotStateInterface, convertStationIDToSolarSystemIDIfNecessaryMethod, getCurrentSystemMethod):
        self._standardStateInterface = standardStateInterface
        self._autopilotStateInterface = autopilotStateInterface
        self.pathfinderCore = pathfinderCore
        self.pathfinderCore.SetGetCachedEntryMethod(self.GetCachedEntry)
        self.pathfinderCacheByStateInterfaceAndRouteType = defaultdict(self.pathfinderCore.CreateCacheEntry)
        self.ConvertStationIDToSolarSystemIDIfNecessary = convertStationIDToSolarSystemIDIfNecessaryMethod
        self.GetCurrentSystem = getCurrentSystemMethod

    def GetCachedEntry(self, stateInterface, fromID):
        return self.pathfinderCacheByStateInterfaceAndRouteType[id(stateInterface), stateInterface.GetRouteType()]

    def SetSecurityPenaltyFactor(self, securityPenalty):
        self._autopilotStateInterface.SetSecurityPenaltyFactor(securityPenalty)

    def SetPodKillAvoidance(self, pkAvoid):
        self._autopilotStateInterface.SetPodKillAvoidance(pkAvoid)

    def SetSystemAvoidance(self, pkAvoid = None):
        self._autopilotStateInterface.SetSystemAvoidance(pkAvoid)

    def GetAvoidanceItems(self):
        return self._autopilotStateInterface.GetAvoidanceItems(expandSystems=False)

    def GetExpandedAvoidanceItems(self):
        return self._autopilotStateInterface.GetAvoidanceItems(expandSystems=True)

    def AddAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        items.append(itemID)
        self._autopilotStateInterface.SetAvoidanceItems(items)

    def RemoveAvoidanceItem(self, itemID):
        items = self.GetAvoidanceItems()
        if itemID in items:
            items.remove(itemID)
            self._autopilotStateInterface.SetAvoidanceItems(items)
            self.SetSystemAvoidance()

    def SetAutopilotRouteType(self, routeType):
        self._autopilotStateInterface.SetRouteType(routeType)

    def GetAutopilotRouteType(self):
        return self._autopilotStateInterface.GetRouteType()

    def GetCompleteWaypointList(self, waypointWithOnlySystems, waypoints):
        completeWaypointList = []
        currentWaypointIndex = 1
        currentSolarSystem = None
        for pathWithSolarSystems in waypointWithOnlySystems:
            if len(pathWithSolarSystems) == 0:
                continue
            pathEndpoint = pathWithSolarSystems[-1]
            pathStartPoint = pathWithSolarSystems[0]
            currentWaypoint = waypoints[currentWaypointIndex]
            if pathWithSolarSystems[-1] != currentWaypoint:
                pathWithSolarSystems.append(currentWaypoint)
            if pathStartPoint == currentSolarSystem:
                pathWithSolarSystems.pop(0)
            currentSolarSystem = pathEndpoint
            completeWaypointList.extend(pathWithSolarSystems)
            currentWaypointIndex += 1

        return completeWaypointList

    def GetWaypointPath(self, waypoints):
        solarSystemWaypoints = map(self.ConvertStationIDToSolarSystemIDIfNecessary, waypoints)
        waypointListsContainingOnlySystems = self.pathfinderCore.GetListOfWaypointPaths(self._autopilotStateInterface, self.GetCurrentSystem(), solarSystemWaypoints)
        return self.GetCompleteWaypointList(waypointListsContainingOnlySystems, waypoints)

    def GetJumpCountsBetweenSystemPairs(self, sourceDestinationPairList):
        return self.pathfinderCore.GetJumpCountsBetweenSystemPairs(self._standardStateInterface, sourceDestinationPairList)

    def _GetPathBetween(self, stateInterface, fromID, toID):
        if IsWormholeSystem(fromID) or IsWormholeSystem(toID):
            return []
        return self.pathfinderCore.GetPathBetween(stateInterface, fromID, toID)

    def GetPathBetween(self, fromID, toID):
        return self._GetPathBetween(self._standardStateInterface, fromID, toID)

    def GetAutopilotPathBetween(self, fromID, toID):
        convertedFromID = self.ConvertStationIDToSolarSystemIDIfNecessary(fromID)
        convertedToID = self.ConvertStationIDToSolarSystemIDIfNecessary(toID)
        return self._GetPathBetween(self._autopilotStateInterface, convertedFromID, convertedToID)

    def _GetJumpCount(self, stateInterface, fromID, toID):
        if fromID is None or toID is None:
            return
        if fromID == toID:
            return 0
        if IsWormholeSystem(fromID) or IsWormholeSystem(toID):
            return sys.maxint
        return self.pathfinderCore.GetJumpCountBetween(stateInterface, fromID, toID)

    def GetJumpCount(self, fromID, toID):
        return self._GetJumpCount(self._standardStateInterface, fromID, toID)

    def GetAutopilotJumpCount(self, fromID, toID):
        return self._GetJumpCount(self._autopilotStateInterface, fromID, toID)

    def GetJumpCountFromCurrent(self, toID):
        return self._GetJumpCount(self._standardStateInterface, self.GetCurrentSystem(), toID)

    def GetSystemsWithinJumpRange(self, fromID, jumpCountMin, jumpCountMax):
        if IsWormholeSystem(fromID):
            return {}
        return self.pathfinderCore.GetSystemsWithinJumpRange(self._standardStateInterface, fromID, jumpCountMin, jumpCountMax)
