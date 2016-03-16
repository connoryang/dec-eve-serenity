#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evePathfinder\core.py
import time
import logging
from collections import defaultdict
log = logging.getLogger(__name__)
import pyEvePathfinder
from cache import NewPathfinderCache
import pathfinderconst as const

class MissingGetCacheEntryMethod(Exception):
    pass


def PairSequence(s):
    i = iter(s)
    last = i.next()
    for current in i:
        yield (last, current)
        last = current


class PathfinderCacheEntry(object):

    def __init__(self, hashValue, cache):
        self.hashValue = hashValue
        self.cache = cache


class SecurityInterval(object):

    def __init__(self, minSecurity, maxSecurity):
        self.minSecurity = minSecurity
        self.maxSecurity = maxSecurity


def IsUnreachableJumpCount(jumpCount):
    return jumpCount == const.UNREACHABLE_JUMP_COUNT


ROUTE_TYPES = {const.ROUTE_TYPE_SAFE: SecurityInterval(0.45, 1.0),
 const.ROUTE_TYPE_UNSAFE: SecurityInterval(0.0, 0.45),
 const.ROUTE_TYPE_UNSAFE_AND_NULL: SecurityInterval(-1.0, 0.45),
 const.ROUTE_TYPE_SHORTEST: SecurityInterval(-1.0, 1.0)}

class StatefulPathfinderInterfaceTemplate(object):

    def GetStartingSystem(self):
        raise NotImplementedError('EvePathfinderCore requires this function')

    def GetSecurityPenalty(self):
        raise NotImplementedError('EvePathfinderCore requires this function')

    def GetAvoidanceList(self):
        raise NotImplementedError('EvePathfinderCore requires this function')

    def GetRouteType(self):
        raise NotImplementedError('EvePathfinderCore requires this function')

    def GetCurrentStateHash(self, fromSolarSystemID):
        raise NotImplementedError('EvePathfinderCore requires this function')


class EvePathfinderCore(object):

    def __init__(self, newPathfinderMap):
        self.newPathfinderMap = newPathfinderMap
        self.newPathfinderExecutionCount = 0
        self.newPathfinderGoal = pyEvePathfinder.EveStandardFloodFillGoal()

    def CreateCacheEntry(self):
        log.debug('default cache entry called')
        return PathfinderCacheEntry(None, NewPathfinderCache(self.newPathfinderMap))

    def _RunNewPathfinderFrom(self, solarSystemID, cache, routeType, penalty, minSec, maxSec, avoidanceSystems, goalSystems):
        if solarSystemID is None or cache is None:
            raise TypeError('Must supply a solarSystemID and a cache')
        cache.ClearCache()
        universe = self.newPathfinderMap
        if routeType == const.ROUTE_TYPE_SHORTEST:
            self.newPathfinderGoal.IgnoreSecurityLimits()
        else:
            self.newPathfinderGoal.AvoidSystemsOutsideSecurityLimits(minSec, maxSec, penalty)
        self.newPathfinderGoal.ClearOrigins()
        self.newPathfinderGoal.AddOrigin(universe, solarSystemID)
        self.newPathfinderGoal.ClearGoalSystems()
        for i in goalSystems:
            self.newPathfinderGoal.AddGoalSystem(universe, i)

        self.newPathfinderGoal.ClearAvoidSystems()
        for itemID in avoidanceSystems:
            self.newPathfinderGoal.AddAvoidSystem(universe, itemID)

        start = time.clock()
        pyEvePathfinder.FindRoute(self.newPathfinderMap, self.newPathfinderGoal, cache.GetCacheForPathfinding())
        self.newPathfinderExecutionCount += 1
        log.debug('EvePathfinder pathfind done in: %f ms', (time.clock() - start) * 1000)

    def GetCachedEntry(self, stateInterface, fromID):
        raise MissingGetCacheEntryMethod('Pathfinder needs an external method to provide the caching strategy.')

    def GoalSystemsContainAnyAvoidedSystem(self, goalSystems, avoidedSystems):
        return len(set(goalSystems).intersection(set(avoidedSystems))) != 0

    def GetPathfinderCache(self, stateInterface, fromID, goalSystems):
        cacheEntry = self._GetCachedEntry(stateInterface, fromID)
        currentHashValue = stateInterface.GetCurrentStateHash(fromID)
        cache = cacheEntry.cache
        if self.GoalSystemsContainAnyAvoidedSystem(goalSystems, stateInterface.GetAvoidanceList()):
            cache.MarkAsDirty()
        if cache.IsDirty() or currentHashValue != cacheEntry.hashValue:
            self.RefreshCache(cache, stateInterface, fromID, goalSystems)
            cacheEntry.hashValue = currentHashValue
        return cache

    def RefreshCache(self, pathfindingCache, stateInterface, startingSolarSystemID, goalSystems):
        avoidedSystems = stateInterface.GetAvoidanceList()
        routeType = stateInterface.GetRouteType()
        secInterval = ROUTE_TYPES[routeType]
        self._RunNewPathfinderFrom(startingSolarSystemID, pathfindingCache, routeType, stateInterface.GetSecurityPenalty(), secInterval.minSecurity, secInterval.maxSecurity, avoidedSystems, goalSystems)
        pathfindingCache.MarkAsClean()
        for goalSystem in goalSystems:
            if goalSystem in avoidedSystems:
                pathfindingCache.MarkAsDirty()
                break

    def GetJumpCountsBetweenSystemPairs(self, stateInterface, solarSystemPairs):
        result = {}
        for originID, destinationID in solarSystemPairs:
            result[originID, destinationID] = self.GetJumpCountBetween(stateInterface, originID, destinationID)

        return result

    def GetListOfWaypointPaths(self, stateInterface, fromID, waypoints):
        if len(waypoints) < 2:
            raise AttributeError('There should be at least two waypoints')
        fullRoute = []
        for fromID, toID in PairSequence(waypoints):
            fullRoute.append(self.GetPathBetween(stateInterface, fromID, toID))

        return fullRoute

    def GetPathBetween(self, stateInterface, fromID, toID):
        log.debug('GetPathBetween: %s to %s', fromID, toID)
        cache = self.GetPathfinderCache(stateInterface, fromID, [toID])
        return cache.GetPathTo(toID)

    def GetJumpCountBetween(self, stateInterface, fromID, toID):
        log.debug('GetPathBetween: %s to %s', fromID, toID)
        cache = self.GetPathfinderCache(stateInterface, fromID, [toID])
        jumpCount = cache.GetJumpCountTo(toID)
        if jumpCount == -1:
            return const.UNREACHABLE_JUMP_COUNT
        else:
            return jumpCount

    def GetSystemsWithinJumpRange(self, stateInterface, fromID, jumpCountMin, jumpCountMax):
        cache = self.GetPathfinderCache(stateInterface, fromID, [])
        systemsWithinJumpCountGenerator = cache.GetSystemsWithinJumpCount(jumpCountMin, jumpCountMax)
        m = defaultdict(list)
        for system, jumpCount in systemsWithinJumpCountGenerator.iteritems():
            m[jumpCount].append(system)

        return m

    def SetGetCachedEntryMethod(self, GetCachedEntryMethod):
        self._GetCachedEntry = GetCachedEntryMethod
