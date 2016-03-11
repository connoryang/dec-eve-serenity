#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\starmap\util.py
from collections import namedtuple
StarmapInterest = namedtuple('StarmapInterest', ['regionID', 'constellationID', 'solarSystemID'])

def OverrideColour(initial, override):
    i = list(initial)
    i[:len(override)] = override
    return tuple(i)


def OverrideAlpha(initial, alpha):
    return (initial[0],
     initial[1],
     initial[2],
     alpha)


def ScaleColour(initial, scale):
    return (scale * initial[0],
     scale * initial[1],
     scale * initial[2],
     initial[3])


def SelectiveIndexedIterItems(indexable, indexes):
    for idx in indexes:
        yield (idx, indexable[idx])


def Pairwise(l):
    first = True
    last = None
    for i in l:
        if not first:
            yield (last, i)
        first = False
        last = i


class SolarSystemMapInfo(object):
    __slots__ = ('regionID', 'constellationID', 'star', 'center', 'scaledCenter', 'factionID', 'neighbours', 'planetCountByType')


class RegionMapInfo(object):
    __slots__ = ('scaledCenter', 'neighbours', 'solarSystemIDs', 'constellationIDs')


class ConstellationMapInfo(object):
    __slots__ = ('regionID', 'neighbours', 'scaledCenter', 'solarSystemIDs')


class MapJumpInfo(object):
    __slots__ = ('jumpType', 'fromSystemID', 'toSystemID', 'adjustedFromVector', 'adjustedToVector')
