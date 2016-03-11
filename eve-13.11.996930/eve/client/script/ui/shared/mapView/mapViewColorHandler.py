#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewColorHandler.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.mapView.colorModes.colorModeInfoSovereignty import ColorModeInfoSearch_Faction
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.client.script.ui.util.uix import EditStationName
from eve.common.script.sys.eveCfg import IsFaction, GetActiveShip, CanUseAgent
import math
import geo2
import eve.client.script.ui.shared.maps.mapcommon as mapcommon
import evetypes
from mapcommon import LegendItem
from collections import defaultdict
from eve.common.script.sys.idCheckers import IsSolarSystem
import talecommon.const as taleConst
from localization import GetByMessageID, GetByLabel
import industry
import sys
import logging
import inventorycommon.typeHelpers
log = logging.getLogger(__name__)
BASE5_COLORRANGE = [(1.0, 1.0, 0.8313725490196079, 1.0),
 (0.996078431372549, 0.8509803921568627, 0.5568627450980392, 1.0),
 (0.996078431372549, 0.6, 0.1607843137254902, 1.0),
 (0.8509803921568627, 0.37254901960784315, 0.054901960784313725, 1.0),
 (0.6, 0.20392156862745098, 0.01568627450980392, 1.0)]
BASE3_COLORRANGE = [(1.0, 0.9686274509803922, 0.7372549019607844, 1.0), (0.996078431372549, 0.7686274509803922, 0.30980392156862746, 1.0), (0.8509803921568627, 0.37254901960784315, 0.054901960784313725, 1.0)]
BASE11_COLORRANGE = [(0.0, 0.40784313725490196, 0.21568627450980393, 1.0),
 (0.10196078431372549, 0.596078431372549, 0.3137254901960784, 1.0),
 (0.4, 0.7411764705882353, 0.38823529411764707, 1.0),
 (0.6470588235294118, 0.0, 0.14901960784313725, 1.0),
 (0.6509803921568628, 0.8509803921568627, 0.41568627450980394, 1.0),
 (0.8431372549019608, 0.18823529411764706, 0.15294117647058825, 1.0),
 (0.8509803921568627, 0.9372549019607843, 0.5450980392156862, 1.0),
 (0.9568627450980393, 0.42745098039215684, 0.2627450980392157, 1.0),
 (0.9921568627450981, 0.6823529411764706, 0.3803921568627451, 1.0),
 (0.996078431372549, 0.8784313725490196, 0.5450980392156862, 1.0),
 (1.0, 1.0, 0.7490196078431373, 1.0)]
BASE4_ORANGES_COLORRANGE = [(0.996078431372549, 0.9294117647058824, 0.8705882352941177, 1.0),
 (0.9921568627450981, 0.7450980392156863, 0.5215686274509804, 1.0),
 (0.9921568627450981, 0.5529411764705883, 0.23529411764705882, 1.0),
 (0.8509803921568627, 0.2784313725490196, 0.00392156862745098, 1.0)]
NEG_NEU_POS_3RANGE = [(0.9882352941176471, 0.5529411764705883, 0.34901960784313724, 1.0), (1.0, 1.0, 0.7490196078431373, 1.0), (0.5686274509803921, 0.8117647058823529, 0.3764705882352941, 1.0)]
INTENSITY_COLORRANGE = [(1.0, 0.7, 0.0, 0.5), (1.0, 0.0, 0.0, 1.0)]
MIN_MAX_COLORRANGE = [(1.0, 0.0, 0.0, 1.0), (1.0, 1.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0)]
COLORCURVE_SECURITY = [(1.0, 0.0, 0.0, 1.0),
 (0.9, 0.2, 0.0, 1.0),
 (1.0, 0.3, 0.0, 1.0),
 (1.0, 0.4, 0.0, 1.0),
 (0.9, 0.5, 0.0, 1.0),
 (1.0, 1.0, 0.0, 1.0),
 (0.6, 1.0, 0.2, 1.0),
 (0.0, 1.0, 0.0, 1.0),
 (0.0, 1.0, 0.3, 1.0),
 (0.3, 1.0, 0.8, 1.0),
 (0.2, 1.0, 1.0, 1.0)]
COLOR_STANDINGS_NEUTRAL = (0.25, 0.25, 0.25, 1.0)
COLOR_STANDINGS_GOOD = (0.0, 1.0, 0.0, 1.0)
COLOR_STANDINGS_BAD = (1.0, 0.0, 0.0, 1.0)
NEUTRAL_COLOR = (0.25, 0.25, 0.25, 1.0)
DEFAULT_MAX_COLOR = BASE5_COLORRANGE[-1]
COLOR_ASSETS = BASE5_COLORRANGE[-1]
COLOR_DEVINDEX = BASE5_COLORRANGE[-1]
CONFISCATED_COLOR = (0.8, 0.4, 0.0, 1.0)
ATTACKED_COLOR = (1.0, 0.0, 0.0, 1.0)
COLOR_ORANGE = (1.0, 0.4, 0.0, 1.0)
COLOR_GREEN = (0.2, 1.0, 1.0, 1.0)
COLOR_RED = (1.0, 0.0, 0.0, 1.0)
COLOR_YELLOW = (1.0, 1.0, 0.0, 1.0)
COLOR_WHITE = (1.0, 1.0, 1.0, 1.0)
COLOR_GRAY = (0.5, 0.5, 0.5, 1.0)
COLOR_PURPLE = (0.5, 0.25, 0.75, 1.0)
STAR_SIZE_UNIFORM = 0.5
STAR_COLORTYPE_PASSIVE = 0
STAR_COLORTYPE_DATA = 1

def GetBase11ColorByID(objectID):
    return BASE11_COLORRANGE[objectID % 11]


def ColorStarsByDevIndex(colorInfo, starColorMode, indexID, indexName):
    sovSvc = sm.GetService('sov')
    indexData = sovSvc.GetAllDevelopmentIndicesMapped()
    color = COLOR_DEVINDEX
    hintFunc = lambda indexName, level: GetByLabel('UI/Map/StarModeHandler/devIndxLevel', indexName=indexName, level=level)
    maxLevel = 0
    for solarSystemID, info in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        maxLevel = max(maxLevel, levelInfo.level)

    for solarSystemID, info in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        if levelInfo.level == 0:
            continue
        colorInfo.solarSystemDict[solarSystemID] = (levelInfo.level / float(maxLevel),
         None,
         (hintFunc, (indexName, levelInfo.level)),
         color)

    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/devIndxDevloped'), color, data=None))
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsByAssets(colorInfo, starColorMode):
    myassets = sm.GetService('assets').GetAll('allitems', blueprintOnly=0, isCorp=0)
    bySystemID = {}
    stuffToPrime = []
    for solarsystemID, station in myassets:
        stuffToPrime.append(station.stationID)
        stuffToPrime.append(solarsystemID)
        if solarsystemID not in bySystemID:
            bySystemID[solarsystemID] = []
        bySystemID[solarsystemID].append(station)

    if stuffToPrime:
        cfg.evelocations.Prime(stuffToPrime)

    def hintFunc(stationData, solarSystemID):
        hint = ''
        for station in stationData:
            shortStationName = EditStationName(cfg.evelocations.Get(station.stationID).name, usename=1)
            subc = GetByLabel('UI/Map/StarModeHandler/StationNameWithItemCount', shortStationName=shortStationName, numItems=station.itemCount)
            if hint:
                hint += '<br>'
            hint += '<url=localsvc:service=assets&method=Show&stationID=%d>%s</url>' % (station.stationID, subc)

        return hint

    PrepareStandardColorData(colorInfo, bySystemID, hintFunc=hintFunc, hintArgs=None, amountKey='itemCount')
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/assetsHasAssets'), COLOR_ASSETS, data=None))


def ColorStarsByVisited(colorInfo, starColorMode):
    history = sm.RemoteSvc('map').GetSolarSystemVisits()
    visited = []
    maxValue = 0
    for entry in history:
        visited.append((entry.lastDateTime, entry.solarSystemID, entry.visits))
        maxValue = max(maxValue, entry.visits)

    visited.sort()
    if len(visited):
        divisor = 1.0 / float(len(visited))
    hintFunc = lambda solarSystemID, visits, lastDateTime: GetByLabel('UI/Map/ColorModeHandler/VisitedLastVisit', count=visits, lastVisit=lastDateTime)
    for i, (lastDateTime, solarSystemID, visits) in enumerate(visited):
        colorInfo.solarSystemDict[solarSystemID] = (visits / float(maxValue),
         float(i) * divisor,
         (hintFunc, (solarSystemID, visits, lastDateTime)),
         None)

    colorInfo.colorList = INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsBySecurity(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        secStatus = starmap.map.GetSecurityStatus(solarSystemID)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         secStatus,
         None,
         None)

    colorInfo.colorList = COLORCURVE_SECURITY
    for i in xrange(0, 11):
        lbl = GetByLabel('UI/Map/StarModeHandler/securityLegendItem', level=1.0 - i * 0.1)
        colorInfo.legend.add(LegendItem(i, lbl, COLORCURVE_SECURITY[10 - i], data=None))


def ColorStarsBySovChanges(colorInfo, starColorMode, changeMode):
    if changeMode in (mapcommon.SOV_CHANGES_OUTPOST_GAIN, mapcommon.SOV_CHANGES_SOV_GAIN):
        color = NEG_NEU_POS_3RANGE[2]
    elif changeMode in (mapcommon.SOV_CHANGES_OUTPOST_LOST, mapcommon.SOV_CHANGES_SOV_LOST):
        color = NEG_NEU_POS_3RANGE[0]
    else:
        color = NEG_NEU_POS_3RANGE[1]
    changes = GetSovChangeList(changeMode)
    hintFunc = lambda comments: '<br>'.join(comments)
    if changes:
        maxValue = max([ len(comments) for solarSystemID, comments in changes.iteritems() ])
        for solarSystemID, comments in changes.iteritems():
            colorInfo.solarSystemDict[solarSystemID] = (len(comments) / float(maxValue),
             None,
             (hintFunc, (comments,)),
             color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/sovereigntyNoSovChanges'), NEUTRAL_COLOR, None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/sovereigntySovChanges'), color, None))
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsByFreeportStations(colorInfo, starColorMode):
    freeportStations = sm.GetService('sov').GetFreeportStations()
    hintFunc = lambda : GetByLabel('UI/Map/StarModeHandler/sovereigntyFreeportStation')
    for station in freeportStations:
        solarSystemID = station.solarSystemID
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         1.0,
         (hintFunc, ()),
         DEFAULT_MAX_COLOR)

    colorInfo.colorType = STAR_COLORTYPE_DATA


def GetSovChangeList(changeMode):
    data = sm.GetService('sov').GetRecentActivity()
    changes = []
    resultMap = {}
    toPrime = set()
    for item in data:
        if item.stationID is None:
            if bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.ownerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovGained', (None, item.ownerID)))
                toPrime.add(item.ownerID)
            elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_LOST) and item.oldOwnerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovLost', (item.oldOwnerID, None)))
                toPrime.add(item.oldOwnerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_OUTPOST_GAIN) and item.oldOwnerID is None:
            changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntyNewOutpost', (None, item.ownerID)))
            toPrime.add(item.ownerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_OUTPOST_GAIN) and item.ownerID is not None:
            changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntyConqueredOutpost', (item.oldOwnerID, item.ownerID)))
            toPrime.add(item.ownerID)
            toPrime.add(item.oldOwnerID)

    cfg.eveowners.Prime(list(toPrime))
    for solarSystemID, text, owners in changes:
        if owners[0]:
            ownerData = cfg.eveowners.Get(owners[0])
            oldOwner = '<url=showinfo:%d//%d>%s</url>' % (ownerData.typeID, owners[0], ownerData.ownerName)
        else:
            oldOwner = ''
        if owners[1]:
            ownerData = cfg.eveowners.Get(owners[1])
            owner = '<url=showinfo:%d//%d>%s</url>' % (ownerData.typeID, owners[1], ownerData.ownerName)
        else:
            owner = ''
        if solarSystemID not in resultMap:
            resultMap[solarSystemID] = []
        resultMap[solarSystemID].append(GetByLabel(text, owner=owner, oldOwner=oldOwner))

    return resultMap


def ColorStarsByCorporationSettledSystems(colorInfo, starColorMode):
    corporationID = starColorMode[1]
    solarSystems = sm.RemoteSvc('config').GetStationSolarSystemsByOwner(corporationID)
    colorInfo.colorType = STAR_COLORTYPE_DATA
    corporationName = cfg.eveowners.Get(corporationID).name
    mapHintCallback = lambda : GetByLabel('UI/InfoWindow/SystemSettledByCorp', corpName=corporationName)
    for solarSystem in solarSystems:
        colorInfo.solarSystemDict[solarSystem.solarSystemID] = (STAR_SIZE_UNIFORM,
         None,
         (mapHintCallback, ()),
         (1.0, 0.0, 0.0, 1.0))


def ColorStarsByFactionStandings(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    colorByFaction = {}
    neutral = COLOR_STANDINGS_NEUTRAL
    for factionID in mapViewData.GetAllFactionsAndAlliances():
        color = starmap.GetColorByStandings(factionID)
        if len(color) == 3:
            color = tuple(color) + (1.0,)
        colorByFaction[factionID] = color

    lbl = GetByLabel('UI/Map/StarModeHandler/factionStandings')
    hintFunc = lambda : lbl
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        color = colorByFaction.get(solarSystem.factionID, neutral)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         None,
         (hintFunc, ()),
         color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/factionGoodStandings'), COLOR_STANDINGS_GOOD, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/factionNeutralStandings'), COLOR_STANDINGS_NEUTRAL, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/factionBadStandings'), COLOR_STANDINGS_BAD, data=None))


def GetColorStarsByFactionSearchArgs():
    return settings.char.ui.Get('mapView_GetColorStarsByFactionSearchArgs', None)


def SetColorStarsByFactionSearchArgs(filterFactionID):
    return settings.char.ui.Set('mapView_GetColorStarsByFactionSearchArgs', filterFactionID)


def ColorStarsByFactionSearch(colorInfo, starColorMode):
    filterFactionID = GetColorStarsByFactionSearchArgs()
    return _ColorStarsByFaction(colorInfo, filterFactionID)


def ColorStarsByFaction(colorInfo, starColorMode):
    return _ColorStarsByFaction(colorInfo, starColorMode[1])


def _ColorStarsByFaction(colorInfo, factionID):
    starmap = sm.GetService('starmap')
    allianceSolarSystems = mapViewData.GetAllianceSolarSystems()
    sovBySolarSystemID = {}
    toPrime = set()
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        if factionID == mapcommon.STARMODE_FILTER_EMPIRE:
            secClass = starmap.map.GetSecurityStatus(solarSystemID)
            if not IsFaction(solarSystem.factionID) or secClass == const.securityClassZeroSec:
                continue
        sovHolderID = starmap._GetFactionIDFromSolarSystem(allianceSolarSystems, solarSystemID)
        if sovHolderID is None:
            continue
        if factionID >= 0 and sovHolderID != factionID:
            continue
        sovBySolarSystemID[solarSystemID] = sovHolderID
        toPrime.add(sovHolderID)

    cfg.eveowners.Prime(list(toPrime))
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/factionSovereignty', name=name)
    for solarSystemID, sovHolderID in sovBySolarSystemID.iteritems():
        name = cfg.eveowners.Get(sovHolderID).name
        col = GetBase11ColorByID(sovHolderID)
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         None,
         (hintFunc, (name,)),
         col)
        colorInfo.legend.add(LegendItem(None, name, col, data=sovHolderID))


def ColorStarsByMilitia(colorInfo, starColorMode):
    factionID = starColorMode[1]
    if factionID < -1:
        log.error('Invalid factionID %s' % factionID)
        return
    facWar = sm.GetService('facwar')
    starmap = sm.GetService('starmap')
    facWarSolarSystemsOccupiers = facWar.GetFacWarSystemsOccupiers()
    maxPointsByFaction = defaultdict(lambda : 1)
    facWarData = starmap.GetFacWarData()
    occupiedSystems = {}
    for systemID, currentOccupierID in facWarSolarSystemsOccupiers.iteritems():
        if currentOccupierID == factionID or factionID == -1:
            if systemID in facWarData:
                threshold, points, occupierID = facWarData[systemID]
                if occupierID is not None and occupierID != currentOccupierID:
                    state = const.contestionStateCaptured
                elif threshold > points:
                    if points == 0:
                        state = const.contestionStateNone
                    else:
                        state = const.contestionStateContested
                else:
                    state = const.contestionStateVulnerable
                maxPointsByFaction[currentOccupierID] = max(points, maxPointsByFaction[currentOccupierID])
            else:
                points, state = 0, const.contestionStateNone
            occupiedSystems[systemID] = (currentOccupierID, points, state)

    hintFunc = lambda ownerID, status: GetByLabel('UI/Map/StarModeHandler/militiaSystemStatus', name=cfg.eveowners.Get(ownerID).name, status=sm.GetService('infoPanel').GetSolarSystemStatusText(status, True))
    for solarSystemID, (occupierID, points, state) in occupiedSystems.iteritems():
        size = points / float(maxPointsByFaction[occupierID])
        col = GetBase11ColorByID(occupierID)
        colorInfo.solarSystemDict[solarSystemID] = (size,
         None,
         (hintFunc, (occupierID, state)),
         col)


def ColorStarsByRegion(colorInfo, starColorMode):
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/regionNameEntry', name=name)
    for regionID, region in mapViewData.GetKnownUniverseRegions().iteritems():
        regionName = cfg.evelocations.Get(regionID).name
        col = BASE5_COLORRANGE[regionID % len(BASE5_COLORRANGE)]
        for solarSystemID in region.solarSystemIDs:
            colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
             None,
             (hintFunc, (regionName,)),
             col)

        colorInfo.legend.add(LegendItem(None, regionName, col, data=regionID))


def HintCargoIllegality(attackTypeIDs, confiscateTypeIDs):
    systemDescription = ''
    for typeID in attackTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityAttackHint', stuff=evetypes.GetName(typeID))

    for typeID in confiscateTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityConfiscateHint', item=evetypes.GetName(typeID))

    return systemDescription


def ColorStarsByCargoIllegality(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    invCache = sm.GetService('invCache')
    activeShipID = GetActiveShip()
    if activeShipID is None:
        shipCargo = []
    else:
        inv = invCache.GetInventoryFromId(activeShipID, locationID=session.stationid2)
        shipCargo = inv.List()
    factionIllegality = {}
    while len(shipCargo) > 0:
        item = shipCargo.pop(0)
        if item.groupID in [const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer]:
            shipCargo.extend(invCache.GetInventoryFromId(item.itemID).List())
        itemIllegalities = inventorycommon.typeHelpers.GetIllegality(item.typeID)
        if itemIllegalities:
            for factionID, illegality in itemIllegalities.iteritems():
                if factionID not in factionIllegality:
                    factionIllegality[factionID] = {}
                if item.typeID not in factionIllegality[factionID]:
                    factionIllegality[factionID][item.typeID] = [max(0.0, illegality.confiscateMinSec), max(0.0, illegality.attackMinSec)]

    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        colour = None
        factionID = solarSystem.factionID
        if factionID is None or factionID not in factionIllegality:
            continue
        systemIllegality = False
        attackTypeIDs = []
        confiscateTypeIDs = []
        securityStatus = starmap.map.GetSecurityStatus(solarSystemID)
        for typeID in factionIllegality[factionID]:
            if securityStatus >= factionIllegality[factionID][typeID][1]:
                systemIllegality = True
                if not colour or colour[0] < 2:
                    colour = (2, ATTACKED_COLOR)
                attackTypeIDs.append(typeID)
            elif securityStatus >= factionIllegality[factionID][typeID][0]:
                systemIllegality = True
                if not colour:
                    colour = (1, CONFISCATED_COLOR)
                confiscateTypeIDs.append(typeID)

        if systemIllegality:
            colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
             0.0,
             (HintCargoIllegality, (attackTypeIDs, confiscateTypeIDs)),
             colour[1])

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/legalityNoConsequences'), NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/legalityConfiscate'), CONFISCATED_COLOR, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/legalityWillAttack'), ATTACKED_COLOR, data=None))


def ColorStarsByNumPilots(colorInfo, starColorMode):
    sol, sta, statDivisor = sm.ProxySvc('machoNet').GetClusterGameStatistics('EVE', ({}, {}, 0))
    pilotcountDict = {}
    for sfoo in sol.iterkeys():
        solarSystemID = sfoo + 30000000
        amount_docked = sta.get(sfoo, 0) / statDivisor
        amount_inspace = (sol.get(sfoo, 0) - sta.get(sfoo, 0)) / statDivisor
        if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
            amount = amount_inspace
        else:
            amount = amount_docked
        if amount:
            pilotcountDict[solarSystemID] = amount

    if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/PilotsInSpace', count=count)
    else:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/PilotsInStation', count=count)
    PrepareStandardColorData(colorInfo, pilotcountDict, hintFunc=hintFunc, colorList=INTENSITY_COLORRANGE)


def ColorStarsByStationCount(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starmap.stationCountCache is None:
        starmap.stationCountCache = sm.RemoteSvc('map').GetStationCount()
    history = starmap.stationCountCache
    hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/StationsCount', count=count)
    PrepareStandardColorData(colorInfo, dict(history), hintFunc=hintFunc)


def HintDungeons(dungeons):
    comments = []
    for dungeonID, difficulty, dungeonName in dungeons:
        ded = ''
        if difficulty:
            ded = GetByLabel('UI/Map/ColorModeHandler/DungeonDedDifficulty', count=difficulty)
        comments.append(GetByLabel('UI/Map/ColorModeHandler/DungeonDedLegendHint', dungeonName=dungeonName, dedName=ded))

    return '<br>'.join(comments)


def ColorStarsByDungeons(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_DUNGEONS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceComplexMap(eve.session.languageID)
    elif starColorMode == mapcommon.STARMODE_DUNGEONSAGENTS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceAgentsMap(eve.session.languageID)
    if dungeons is None:
        return
    solmap = {}
    for solarSystemID, dungeonID, difficulty, dungeonName in dungeons:
        solmap.setdefault(solarSystemID, []).append((dungeonID, difficulty, dungeonName))

    maxDungeons = max([ len(solarSystemDungeons) for solarSystemID, solarSystemDungeons in solmap.iteritems() ])
    for solarSystemID, solarSystemDungeons in solmap.iteritems():
        maxDifficulty = 1
        for dungeonID, difficulty, dungeonName in solarSystemDungeons:
            if difficulty:
                maxDifficulty = max(maxDifficulty, difficulty)

        maxDifficulty = (10 - maxDifficulty) / 9.0
        colorInfo.solarSystemDict[solarSystemID] = (len(solarSystemDungeons) / float(maxDungeons),
         maxDifficulty,
         (HintDungeons, (solarSystemDungeons,)),
         None)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.colorList = COLORCURVE_SECURITY
    colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
    for i in xrange(0, 10):
        lbl = GetByLabel('UI/Map/StarModeHandler/dungeonDedLegendDiffaculty', difficulty=i + 1)
        colorInfo.legend.add(LegendItem(i, lbl, starmap.GetColorCurveValue(colorCurve, (9 - i) / 9.0), data=None))


def ColorStarsByJumps1Hour(colorInfo, starColorMode):
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatJumps, 1)
    history = {}
    for entry in historyDB:
        if entry.value1 > 0:
            history[entry.solarSystemID] = entry.value1

    hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/ColorModeHandler/JumpsLastHour', count=count)
    PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc)


def ColorStarsByKills(colorInfo, starColorMode, statID, hours):
    historyDB = sm.RemoteSvc('map').GetHistory(statID, hours)
    history = {}
    for entry in historyDB:
        if entry.value1 - entry.value2 > 0:
            history[entry.solarSystemID] = entry.value1 - entry.value2

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsShipsInLast', count=count, hours=hours)
    PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByPodKills(colorInfo, starColorMode):
    if starColorMode == mapcommon.STARMODE_PODKILLS24HR:
        hours = 24
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 24)
    else:
        hours = 1
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 1)
    history = {}
    for entry in historyDB:
        if entry.value3 > 0:
            history[entry.solarSystemID] = entry.value3

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsPodInLast', hours=hours, count=count)
    PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByFactionKills(colorInfo, starColorMode):
    hours = 24
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, hours)
    history = {}
    for entry in historyDB:
        if entry.value2 > 0:
            history[entry.solarSystemID] = entry.value2

    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/ColorModeHandler/KillsFactionInLast', hours=hours, count=count)
    PrepareStandardColorData(colorInfo, history, hintFunc=hintFunc, hintArgs=(hours,))


def ColorStarsByCynosuralFields(colorInfo, starColorMode):
    fields = sm.RemoteSvc('map').GetBeaconCount()
    orange = COLOR_ORANGE
    green = COLOR_GREEN
    red = COLOR_RED
    hintFuncTotal = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGeneratorsNumber', count=count)
    hintFuncModule = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsNumber', count=count)
    hintFuncStructure = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveGeneratorNumber', count=count)
    maxModule = 0
    maxStructure = 0
    for solarSystemID, cnt in fields.iteritems():
        moduleCnt, structureCnt = cnt
        maxModule = max(maxModule, moduleCnt)
        maxStructure = max(maxStructure, structureCnt)

    for solarSystemID, cnt in fields.iteritems():
        moduleCnt, structureCnt = cnt
        if moduleCnt > 0 and structureCnt > 0:
            ttlcnt = moduleCnt + structureCnt
            colorInfo.solarSystemDict[solarSystemID] = (ttlcnt / float(maxModule + maxStructure),
             1.0,
             (hintFuncTotal, (ttlcnt,)),
             red)
        elif moduleCnt:
            colorInfo.solarSystemDict[solarSystemID] = (moduleCnt / float(maxModule),
             1.0,
             (hintFuncModule, (moduleCnt,)),
             green)
        elif structureCnt:
            colorInfo.solarSystemDict[solarSystemID] = (structureCnt / float(maxStructure),
             1.0,
             (hintFuncStructure, (structureCnt,)),
             orange)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/cynoActiveFields'), green, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/cynoActiveGenerators'), orange, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGenerators'), red, data=None))


def ColorStarsByCorpAssets(colorInfo, starColorMode, assetKey, legendName):
    rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, assetKey)
    solarsystems = {}
    stuffToPrime = []
    for row in rows:
        stationID = row.locationID
        try:
            solarsystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
        except:
            solarsystemID = row.locationID

        if solarsystemID not in solarsystems:
            solarsystems[solarsystemID] = {}
            stuffToPrime.append(solarsystemID)
        if stationID not in solarsystems[solarsystemID]:
            solarsystems[solarsystemID][stationID] = []
            stuffToPrime.append(stationID)
        solarsystems[solarsystemID][stationID].append(row)

    cfg.evelocations.Prime(stuffToPrime)
    hintFunc = lambda stations, solarSystemID: '<br>'.join([ cfg.evelocations.Get(stationID).name for stationID in stations ])
    PrepareStandardColorData(colorInfo, solarsystems, hintFunc=hintFunc)


def ColorStarsByServices(colorInfo, starColorMode, serviceTypeID):
    starmap = sm.GetService('starmap')
    stations, opservices, services = sm.RemoteSvc('map').GetStationExtraInfo()
    opservDict = {}
    stationIDs = []
    solarsystems = defaultdict(list)
    for each in opservices:
        if each.operationID not in opservDict:
            opservDict[each.operationID] = []
        opservDict[each.operationID].append(each.serviceID)

    if starmap.warFactionByOwner is None and serviceTypeID == const.stationServiceNavyOffices:
        starmap.warFactionByOwner = {}
        factions = sm.GetService('facwar').GetWarFactions().keys()
        for stationRow in stations:
            ownerID = stationRow.ownerID
            if ownerID not in starmap.warFactionByOwner:
                faction = sm.GetService('faction').GetFaction(ownerID)
                if faction and faction in factions:
                    starmap.warFactionByOwner[ownerID] = faction

    if serviceTypeID == const.stationServiceSecurityOffice:
        secOfficeSvc = sm.GetService('securityOfficeSvc')
    for stationRow in stations:
        solarSystemID = stationRow.solarSystemID
        if stationRow.operationID == None:
            continue
        if serviceTypeID not in opservDict[stationRow.operationID]:
            continue
        if serviceTypeID == const.stationServiceNavyOffices and stationRow.ownerID not in starmap.warFactionByOwner:
            continue
        if serviceTypeID == const.stationServiceSecurityOffice and not secOfficeSvc.CanAccessServiceInStation(stationRow.stationID):
            continue
        solarsystems[solarSystemID].append(stationRow.stationID)
        stationIDs.append(stationRow.stationID)

    cfg.evelocations.Prime(stationIDs)

    def hintFunc2(stationIDs):
        hint = ''
        for stationID in stationIDs:
            station = sm.StartService('ui').GetStation(stationID)
            stationName = cfg.evelocations.Get(stationID).name
            stationTypeID = station.stationTypeID
            if hint:
                hint += '<br>'
            hint += '<url=showinfo:%d//%d>%s</url>' % (stationTypeID, stationID, stationName)

        return hint

    countAll = [ len(stationIDs) for solarSystemID, stationIDs in solarsystems.iteritems() ]
    minCount = min(countAll)
    maxCount = max(countAll)
    for solarsystemID, stationIDs in solarsystems.iteritems():
        size = ExpValueInRange(len(stationIDs), minCount, maxCount, minValue=0.1, expFactor=3.0)
        colorValue = len(stationIDs) / float(maxCount)
        colorInfo.solarSystemDict[solarsystemID] = (size,
         colorValue,
         (hintFunc2, (stationIDs,)),
         None)

    colorInfo.colorList = INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA


def ColorStarsByFleetMembers(colorInfo, starColorMode):
    fleetComposition = sm.GetService('fleet').GetFleetComposition()
    if fleetComposition is not None:
        solarSystems = defaultdict(list)
        for each in fleetComposition:
            solarSystems[each.solarSystemID].append(each.characterID)

        def hintFunc(characterIDs, solarSystemID):
            return '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])

        PrepareStandardColorData(colorInfo, solarSystems, hintFunc=hintFunc)


def ColorStarsByCorpMembers(colorInfo, starColorMode):
    corp = sm.RemoteSvc('map').GetMyExtraMapInfo()
    if corp is not None:
        solarSystems = defaultdict(list)
        for each in corp:
            if IsSolarSystem(each.locationID):
                solarSystems[each.locationID].append(each.characterID)

        def hintFunc(characterIDs, solarSystemID):
            if len(characterIDs) > 10:
                return GetByLabel('UI/Map/ColorModeHandler/CountCorporationMembers', count=len(characterIDs))
            else:
                return '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])

        PrepareStandardColorData(colorInfo, solarSystems, hintFunc=hintFunc)


def ExpValueInRange(amount, minAmount, maxAmount, minValue = 0.1, expFactor = 3.0):
    minmaxRange = float(maxAmount - minAmount)
    if minmaxRange:
        minExp = math.exp(minAmount / float(maxAmount))
        maxExp = math.exp(expFactor)
        expRange = maxExp - minExp
        pValue = amount / float(maxAmount) * expFactor
        pValueExp = math.exp(pValue)
        return minValue + (1.0 - minValue) * (pValueExp - minExp) / expRange
    return 1.0


def ColorStarsByMyAgents(colorInfo, starColorMode):
    standingInfo = sm.RemoteSvc('map').GetMyExtraMapInfoAgents().Index('fromID')
    solarsystems = {}
    valid = (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent)
    agentsByID = sm.GetService('agents').GetAgentsByID()
    facWarService = sm.GetService('facwar')
    skills = {}
    for agentID in agentsByID:
        agent = agentsByID[agentID]
        fa = standingInfo.get(agent.factionID, 0.0)
        if fa:
            fa = fa.rank * 10.0
        co = standingInfo.get(agent.corporationID, 0.0)
        if co:
            co = co.rank * 10.0
        ca = standingInfo.get(agent.agentID, 0.0)
        if ca:
            ca = ca.rank * 10.0
        isLimitedToFacWar = False
        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarService.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            isLimitedToFacWar = True
        if agent.agentTypeID in valid and CanUseAgent(agent.level, agent.agentTypeID, fa, co, ca, agent.corporationID, agent.factionID, skills) and isLimitedToFacWar == False:
            if agent.stationID:
                solarsystems.setdefault(agent.solarsystemID, []).append(agent)

    def hintFunc(agents, solarSystemID):
        npcDivisions = sm.GetService('agents').GetDivisions()
        caption = ''
        for agent in agents:
            agentOwner = cfg.eveowners.Get(agent.agentID)
            agentString = GetByLabel('UI/Map/StarModeHandler/agentCaptionDetails', divisionName=npcDivisions[agent.divisionID].divisionName, agentName=agentOwner.name, level=agent.level)
            if caption:
                caption += '<br>'
            caption += '<url=showinfo:%d//%d>%s</url>' % (agentOwner.typeID, agent.agentID, agentString)

        return caption

    PrepareStandardColorData(colorInfo, solarsystems, hintFunc=hintFunc, colorList=MIN_MAX_COLORRANGE)


def ColorStarsByAvoidedSystems(colorInfo, starColorMode):
    avoidanceSolarSystemIDs = sm.GetService('clientPathfinderService').GetExpandedAvoidanceItems()
    hintFunc = lambda : GetByLabel('UI/Map/StarModeHandler/advoidSystemOnList')
    for solarSystemID in avoidanceSolarSystemIDs:
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         1.0,
         (hintFunc, ()),
         DEFAULT_MAX_COLOR)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/advoidNotAdvoided'), NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/advoidAdvoided'), DEFAULT_MAX_COLOR, data=None))


def ColorStarsByRealSunColor(colorInfo, starColorMode):
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        colorInfo.solarSystemDict[solarSystemID] = (STAR_SIZE_UNIFORM,
         0.0,
         None,
         solarSystem.star.color)

    for typeID, sunType in mapcommon.SUN_DATA.iteritems():
        name = evetypes.GetName(typeID)
        colorInfo.legend.add(LegendItem(name, name, sunType.color, data=None))


def ColorStarsByPIScanRange(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    playerLoc = cfg.evelocations.Get(session.solarsystemid2)
    playerPos = (playerLoc.x, playerLoc.y, playerLoc.z)
    skills = sm.GetService('skills').MySkillLevelsByID()
    remoteSensing = skills.get(const.typeRemoteSensing, 0)
    hintFunc = lambda range: GetByLabel('UI/Map/StarModeHandler/scanHintDistance', range=range)
    for solarSystemID, solarSystem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        systemLoc = cfg.evelocations.Get(solarSystemID)
        systemPos = (systemLoc.x, systemLoc.y, systemLoc.z)
        dist = geo2.Vec3Distance(playerPos, systemPos) / const.LIGHTYEAR
        proximity = None
        for i, each in enumerate(const.planetResourceScanningRanges):
            if not i >= 5 - remoteSensing:
                continue
            if each >= dist:
                proximity = i

        if proximity is not None:
            colorInfo.solarSystemDict[solarSystemID] = (0.5 + 0.1 * proximity,
             0.2 * proximity,
             (hintFunc, (dist,)),
             None)

    colorInfo.colorList = BASE5_COLORRANGE
    colorCurve = starmap.GetColorCurve(colorInfo.colorList)
    for i, each in enumerate(const.planetResourceScanningRanges):
        if not i >= 5 - remoteSensing:
            continue
        lbl = GetByLabel('UI/Map/StarModeHandler/scanLegendDistance', range=const.planetResourceScanningRanges[i])
        colorInfo.legend.add(LegendItem(i, lbl, starmap.GetColorCurveValue(colorCurve, 1.0 / 5.0 * i), data=None))


def ColorStarsByPlanetType(colorInfo, starColorMode):
    planetTypeID = starColorMode[1]
    systems = defaultdict(int)
    for solarSystemID, d in mapViewData.GetKnownUniverseSolarSystems().iteritems():
        if planetTypeID in d.planetCountByType:
            systems[solarSystemID] = v = d.planetCountByType[planetTypeID]

    def hintFunc(amount, solarSystemID):
        planetTypeName = evetypes.GetName(planetTypeID)
        return '%s: %d' % (planetTypeName, amount)

    PrepareStandardColorData(colorInfo, systems, minValue=0.1, hintFunc=hintFunc, expFactor=6.0)


def ColorStarsByMyColonies(colorInfo, starColorMode):
    planetSvc = sm.GetService('planetSvc')
    planetRows = planetSvc.GetMyPlanets()
    if len(planetRows):
        systems = defaultdict(int)
        for row in planetRows:
            systems[row.solarSystemID] += 1

        def hintFunc(count, solarSystemID):
            return GetByLabel('UI/Map/StarModeHandler/planetsColoniesCount', count=count)

        PrepareStandardColorData(colorInfo, systems, hintFunc=hintFunc)


def ColorStarsByIncursions(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursions()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystem(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), BASE3_COLORRANGE[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionPraticipant'), BASE3_COLORRANGE[-1], data=None))


def ColorStarsByIncursionsGM(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursionsGM()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystemGm(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.colorType = STAR_COLORTYPE_DATA
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_GREEN, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionVanguard'), COLOR_YELLOW, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/incursionAssault'), COLOR_ORANGE, data=None))
    colorInfo.legend.add(LegendItem(3, GetByLabel('UI/Map/StarModeHandler/incursionHQ'), COLOR_RED, data=None))
    colorInfo.legend.add(LegendItem(4, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_WHITE, data=None))
    colorInfo.legend.add(LegendItem(5, 'Incursion Spread', COLOR_GRAY, data=None))
    colorInfo.legend.add(LegendItem(6, 'Incursion Final Encounter', COLOR_PURPLE, data=None))


def GetColorAndHintForIncursionSystem(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType == taleConst.scenesTypes.staging:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionStageing')
        return (1.0,
         0,
         (incursionHint, ()),
         BASE3_COLORRANGE[0])
    if sceneType == taleConst.scenesTypes.vanguard:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionPraticipant')
        return (0.5,
         1,
         (incursionHint, ()),
         BASE3_COLORRANGE[-1])
    if sceneType == taleConst.scenesTypes.incursionStaging:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionStageing')
        return (0.75,
         2,
         (incursionHint, ()),
         BASE3_COLORRANGE[0])


def GetColorAndHintForIncursionSystemGm(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType == taleConst.scenesTypes.staging:
        return (1.0,
         0,
         (lambda : distributionName + 'Staging', ()),
         COLOR_GREEN)
    if sceneType == taleConst.scenesTypes.vanguard:
        return (0.5,
         1,
         (lambda : distributionName + 'Vanguard', ()),
         COLOR_YELLOW)
    if sceneType == taleConst.scenesTypes.assault:
        return (0.5,
         2,
         (lambda : distributionName + 'Assault', ()),
         COLOR_ORANGE)
    if sceneType == taleConst.scenesTypes.headquarters:
        return (0.5,
         3,
         (lambda : distributionName + 'HeadQuarters', ()),
         COLOR_RED)
    if sceneType in (taleConst.scenesTypes.incursionStaging, taleConst.scenesTypes.incursionLightInfestation):
        return (0.75,
         4,
         (lambda : distributionName + 'Staging', ()),
         COLOR_WHITE)
    if sceneType in (taleConst.scenesTypes.incursionMediumInfestation, taleConst.scenesTypes.incursionHeavyInfestation):
        return (0.5,
         5,
         (lambda : distributionName + 'Incursion Spread', ()),
         COLOR_GRAY)
    if sceneType == taleConst.scenesTypes.incursionFinalEncounter:
        return (0.5,
         6,
         (lambda : distributionName + 'Incursion Final Encounter', ()),
         COLOR_PURPLE)


def ColorStarsByJobs24Hours(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryJobsOverLast24Hours(activityID)
    if systemRows:

        def hintFunc(amount, solarSystemID):
            return GetByLabel('UI/Map/StarModeHandler/jobsStartedLast24Hours', noOfJobs=amount)

        jobsBySystem = {row.solarSystemID:row.noOfJobs for row in systemRows}
        PrepareStandardColorData(colorInfo, jobsBySystem, hintFunc=hintFunc)


def ColorStarsByIndustryCostModifier(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryCostModifier(activityID)

    def hintFunc(value, solarSystemID):
        return GetByLabel('UI/Map/StarModeHandler/industryCostModifier', index=value * 100.0)

    PrepareStandardColorData(colorInfo, systemRows, hintFunc=hintFunc, minValue=0.05, expFactor=1.0)


def _GetMilitiaHeader(colorMode):
    factionID = colorMode[1]
    if factionID == mapcommon.STARMODE_FILTER_FACWAR_ENEMY:
        return GetByLabel('UI/Map/MapPallet/cbModeMilitias')
    return cfg.eveowners.Get(factionID).name


def _GetPlanetsHeader(colorMode):
    planetTypeID = colorMode[1]
    return evetypes.GetName(planetTypeID)


functionMapping = {mapcommon.STARMODE_ASSETS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyAssets'), loadFunction=ColorStarsByAssets),
 mapcommon.STARMODE_VISITED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIVisited'), loadFunction=ColorStarsByVisited),
 mapcommon.STARMODE_SECURITY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsSecurity'), loadFunction=ColorStarsBySecurity),
 mapcommon.STARMODE_INDEX_STRATEGIC: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxStrategic'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexSovereignty, GetByLabel('UI/Map/StarMap/Strategic'))),
 mapcommon.STARMODE_INDEX_MILITARY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxMilitary'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexMilitary, GetByLabel('UI/Map/StarMap/Military'))),
 mapcommon.STARMODE_INDEX_INDUSTRY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByDevIdxIndustry'), loadFunction=ColorStarsByDevIndex, loadArguments=(const.attributeDevIndexIndustrial, GetByLabel('UI/Map/StarMap/Industry'))),
 mapcommon.STARMODE_SOV_CHANGE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByRecientSovChanges'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_ALL,)),
 mapcommon.STARMODE_SOV_GAIN: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsBySovGain'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_SOV_GAIN,)),
 mapcommon.STARMODE_SOV_LOSS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsBySovLoss'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_SOV_LOST,)),
 mapcommon.STARMODE_OUTPOST_GAIN: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByStationGain'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_OUTPOST_GAIN,)),
 mapcommon.STARMODE_OUTPOST_LOSS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByStationLoss'), loadFunction=ColorStarsBySovChanges, loadArguments=(mapcommon.SOV_CHANGES_OUTPOST_LOST,)),
 mapcommon.STARMODE_STATION_FREEPORT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByFreeportStations'), loadFunction=ColorStarsByFreeportStations),
 mapcommon.STARMODE_SOV_STANDINGS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByStandings'), loadFunction=ColorStarsByFactionStandings),
 mapcommon.STARMODE_FACTION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbModeFactions'), loadFunction=ColorStarsByFactionSearch, searchHandler=ColorModeInfoSearch_Faction),
 mapcommon.STARMODE_FACTIONEMPIRE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByEmpireFactions'), loadFunction=ColorStarsByFaction),
 mapcommon.STARMODE_MILITIA: Bunch(header=_GetMilitiaHeader, loadFunction=ColorStarsByMilitia),
 mapcommon.STARMODE_REGION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRegion'), loadFunction=ColorStarsByRegion),
 mapcommon.STARMODE_CARGOILLEGALITY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCargoLeagal'), loadFunction=ColorStarsByCargoIllegality),
 mapcommon.STARMODE_PLAYERCOUNT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPilots30Min'), loadFunction=ColorStarsByNumPilots),
 mapcommon.STARMODE_PLAYERDOCKED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPilotsDocked'), loadFunction=ColorStarsByNumPilots),
 mapcommon.STARMODE_STATIONCOUNT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsStationCount'), loadFunction=ColorStarsByStationCount),
 mapcommon.STARMODE_DUNGEONS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDedDeadspace'), loadFunction=ColorStarsByDungeons),
 mapcommon.STARMODE_DUNGEONSAGENTS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDedAgents'), loadFunction=ColorStarsByDungeons),
 mapcommon.STARMODE_JUMPS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsJumps'), loadFunction=ColorStarsByJumps1Hour),
 mapcommon.STARMODE_SHIPKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDestroyed'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatKills, 1)),
 mapcommon.STARMODE_SHIPKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsDestroyed24H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatKills, 24)),
 mapcommon.STARMODE_MILITIAKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed1H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatFacWarKills, 1)),
 mapcommon.STARMODE_MILITIAKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitiaDestroyed24H'), loadFunction=ColorStarsByKills, loadArguments=(const.mapHistoryStatFacWarKills, 24)),
 mapcommon.STARMODE_PODKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPoded1H'), loadFunction=ColorStarsByPodKills),
 mapcommon.STARMODE_PODKILLS24HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPoded24H'), loadFunction=ColorStarsByPodKills),
 mapcommon.STARMODE_FACTIONKILLS1HR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsNPCDestroyed'), loadFunction=ColorStarsByFactionKills),
 mapcommon.STARMODE_CYNOSURALFIELDS: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCynosuarl'), loadFunction=ColorStarsByCynosuralFields),
 mapcommon.STARMODE_CORPOFFICES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpOffices'), loadFunction=ColorStarsByCorpAssets, loadArguments=('offices', GetByLabel('UI/Map/StarMap/Offices'))),
 mapcommon.STARMODE_CORPIMPOUNDED: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpImpounded'), loadFunction=ColorStarsByCorpAssets, loadArguments=('junk', GetByLabel('UI/Map/StarMap/Impounded'))),
 mapcommon.STARMODE_CORPPROPERTY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpProperty'), loadFunction=ColorStarsByCorpAssets, loadArguments=('property', GetByLabel('UI/Map/StarMap/Property'))),
 mapcommon.STARMODE_CORPDELIVERIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpDeliveries'), loadFunction=ColorStarsByCorpAssets, loadArguments=('deliveries', GetByLabel('UI/Map/StarMap/Deliveries'))),
 mapcommon.STARMODE_FRIENDS_FLEET: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFleetMembers'), loadFunction=ColorStarsByFleetMembers),
 mapcommon.STARMODE_FRIENDS_CORP: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsCorpMembers'), loadFunction=ColorStarsByCorpMembers),
 mapcommon.STARMODE_FRIENDS_AGENT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyAgents'), loadFunction=ColorStarsByMyAgents),
 mapcommon.STARMODE_AVOIDANCE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsAdvoidance'), loadFunction=ColorStarsByAvoidedSystems),
 mapcommon.STARMODE_REAL: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsActual'), loadFunction=ColorStarsByRealSunColor),
 mapcommon.STARMODE_STATION_SERVICE_CLONING: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsClone'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceCloning,)),
 mapcommon.STARMODE_STATION_SERVICE_FACTORY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFactory'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceFactory,)),
 mapcommon.STARMODE_STATION_SERVICE_FITTING: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsFitting'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceFitting,)),
 mapcommon.STARMODE_STATION_SERVICE_INSURANCE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsInsurance'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceInsurance,)),
 mapcommon.STARMODE_STATION_SERVICE_LABORATORY: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsLaboratory'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceLaboratory,)),
 mapcommon.STARMODE_STATION_SERVICE_REPAIRFACILITIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRepair'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceRepairFacilities,)),
 mapcommon.STARMODE_STATION_SERVICE_NAVYOFFICES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMilitia'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceNavyOffices,)),
 mapcommon.STARMODE_STATION_SERVICE_REPROCESSINGPLANT: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsRefinery'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceReprocessingPlant,)),
 mapcommon.STARMODE_STATION_SERVICE_SECURITYOFFICE: Bunch(header=GetByLabel('UI/Map/MapPallet/StarmodeSecurityOffices'), loadFunction=ColorStarsByServices, loadArguments=(const.stationServiceSecurityOffice,)),
 mapcommon.STARMODE_PISCANRANGE: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsPIScanRange'), loadFunction=ColorStarsByPIScanRange),
 mapcommon.STARMODE_MYCOLONIES: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsMyColonies'), loadFunction=ColorStarsByMyColonies),
 mapcommon.STARMODE_PLANETTYPE: Bunch(header=_GetPlanetsHeader, loadFunction=ColorStarsByPlanetType),
 mapcommon.STARMODE_INCURSION: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIncursion'), loadFunction=ColorStarsByIncursions),
 mapcommon.STARMODE_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(None,)),
 mapcommon.STARMODE_MANUFACTURING_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.MANUFACTURING,)),
 mapcommon.STARMODE_RESEARCHTIME_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.RESEARCH_TIME,)),
 mapcommon.STARMODE_RESEARCHMATERIAL_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.RESEARCH_MATERIAL,)),
 mapcommon.STARMODE_COPY_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByCopyJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.COPYING,)),
 mapcommon.STARMODE_INVENTION_JOBS24HOUR: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByInventionJobsStartedLast24Hours'), loadFunction=ColorStarsByJobs24Hours, loadArguments=(industry.INVENTION,)),
 mapcommon.STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByManufacturingIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.MANUFACTURING,)),
 mapcommon.STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchTimeIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.RESEARCH_TIME,)),
 mapcommon.STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByResearchMaterialIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.RESEARCH_MATERIAL,)),
 mapcommon.STARMODE_INDUSTRY_COPY_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByCopyIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.COPYING,)),
 mapcommon.STARMODE_INDUSTRY_INVENTION_COST_INDEX: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsByInventionIndustryCostModifier'), loadFunction=ColorStarsByIndustryCostModifier, loadArguments=(industry.INVENTION,)),
 mapcommon.STARMODE_INCURSIONGM: Bunch(header=GetByLabel('UI/Map/MapPallet/cbStarsIncursionGM'), loadFunction=ColorStarsByIncursionsGM),
 mapcommon.STARMODE_SETTLED_SYSTEMS_BY_CORP: Bunch(header=GetByLabel('UI/InfoWindow/SettledSystems'), loadFunction=ColorStarsByCorporationSettledSystems)}

def GetFormatFunction(colorMode):
    return functionMapping.get(colorMode, None)


def GetFormatFunctionLabel(colorMode):
    if isinstance(colorMode, tuple):
        colorModeKey = colorMode[0]
    else:
        colorModeKey = colorMode
    colorModeMapping = GetFormatFunction(colorModeKey)
    if colorModeMapping is None:
        return
    if callable(colorModeMapping.header):
        label = colorModeMapping.header(colorMode)
    else:
        label = colorModeMapping.header
    return label


def PrepareStandardColorData(colorInfo, dataPerSolarSystem, minValue = 0.2, hintFunc = None, hintArgs = None, amountKey = None, expFactor = 3.0, colorList = None):
    dataWithAmount = {}
    allAmounts = []
    if amountKey:
        for solarSystemID, solarSystemData in dataPerSolarSystem.iteritems():
            if isinstance(solarSystemData, list):
                amount = sum((getattr(data, amountKey, 0) for data in solarSystemData))
            else:
                amount = getattr(solarSystemData, amountKey, 0)
            dataWithAmount[solarSystemID] = (amount, solarSystemData)
            allAmounts.append(amount)

    else:
        for solarSystemID, solarSystemData in dataPerSolarSystem.iteritems():
            if hasattr(solarSystemData, '__iter__'):
                amount = len(solarSystemData)
            else:
                amount = solarSystemData
            dataWithAmount[solarSystemID] = (amount, solarSystemData)
            allAmounts.append(amount)

    if not allAmounts:
        return
    maxAmount = max(allAmounts)
    minAmount = min(allAmounts)
    for solarSystemID, (amount, solarSystemData) in dataWithAmount.iteritems():
        sizeFactor = ExpValueInRange(amount, minAmount, maxAmount, minValue=minValue, expFactor=expFactor)
        colorValue = amount / float(maxAmount)
        hintFuncArgs = (solarSystemData, solarSystemID)
        if hintArgs:
            hintFuncArgs += hintArgs
        colorInfo.solarSystemDict[solarSystemID] = (sizeFactor,
         colorValue,
         (hintFunc, hintFuncArgs),
         None)

    colorInfo.maxAmount = maxAmount
    colorInfo.minAmount = minAmount
    colorInfo.colorList = colorList or INTENSITY_COLORRANGE
    colorInfo.colorType = STAR_COLORTYPE_DATA
