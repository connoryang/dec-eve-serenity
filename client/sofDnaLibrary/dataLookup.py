#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sofDnaLibrary\dataLookup.py
import re
from sofDnaLibrary.data import GetSkins, GetMaterials, GetGraphicIDs, GetTypes, GetMaterialSets

def Matches(actualValue, queryValue):
    if actualValue is None:
        return False
    if actualValue.lower() == queryValue.lower():
        return True
    match = re.match('^%s$' % queryValue, actualValue)
    return match is not None


def GetMaterialIDAndFactionOverrideMatchingFaction(factionQuery = '.*'):
    return {materialID:getattr(materialInfo, 'sofFactionName', None) for materialID, materialInfo in GetMaterials().iteritems() if Matches(getattr(materialInfo, 'sofFactionName', None), factionQuery)}


def GetTypeFactionOverridesThatMatchFaction(factionQuery = '.*'):
    skins = GetSkins()
    matchingMaterials = GetMaterialIDAndFactionOverrideMatchingFaction(factionQuery)
    matchingSkins = {}
    for skinID, skinInfo in skins.iteritems():
        if int(skinInfo.skinMaterialID) in matchingMaterials:
            matchingSkins[skinID] = matchingMaterials[int(skinInfo.skinMaterialID)]

    typeFactionOverride = {}
    for skinID, factionOverride in matchingSkins.iteritems():
        for typeID in skins[skinID].types:
            typeFactionOverride[typeID] = typeFactionOverride.get(typeID, [])
            typeFactionOverride[typeID].append(factionOverride)

    return typeFactionOverride


def GetDefaultTypeDnaInfoForDnaQuery(hullQuery = '.*', factionQuery = '.*', raceQuery = '.*'):
    hullAndRaceMatchingGraphicIDs = []
    matchingGraphicIDs = []
    graphicIDs = GetGraphicIDs()
    for graphicID, graphicInfo in graphicIDs.iteritems():
        raceName = getattr(graphicInfo, 'sofRaceName', None)
        hullName = getattr(graphicInfo, 'sofHullName', None)
        factionName = getattr(graphicInfo, 'sofFactionName', None)
        if Matches(raceName, raceQuery) and Matches(hullName, hullQuery):
            hullAndRaceMatchingGraphicIDs.append(graphicID)
            if Matches(factionName, factionQuery):
                matchingGraphicIDs.append(graphicID)

    matchingTypes = {}
    for typeID, typeInfo in GetTypes().iteritems():
        graphicID = typeInfo.graphicID
        if graphicID is None:
            continue
        graphic = graphicIDs[graphicID]
        factionOverride = typeInfo.sofFactionName
        materialSetFactionOverride = None
        sofMaterialSetID = getattr(typeInfo, 'sofMaterialSetID', None)
        materialSet = GetMaterialSets().get(sofMaterialSetID, None)
        dnaAddition = None
        if materialSet:
            materialSetFactionOverride = getattr(materialSet, 'sofFactionName', None)
            materials = [ getattr(materialSet, attribute, 'none') for attribute in ['material1',
             'material2',
             'material3',
             'material4'] ]
            if any([ m != 'none' for m in materials ]):
                dnaAddition = 'mesh?%s' % ';'.join(materials)
        if Matches(materialSetFactionOverride, factionQuery) and graphicID in hullAndRaceMatchingGraphicIDs:
            matchingTypes[typeID] = GenerateMatch(getattr(graphic, 'sofRaceName', None), getattr(graphic, 'sofHullName', None), materialSetFactionOverride, dnaAddition)
        if Matches(factionOverride, factionQuery) and graphicID in hullAndRaceMatchingGraphicIDs:
            matchingTypes[typeID] = GenerateMatch(getattr(graphic, 'sofRaceName', None), getattr(graphic, 'sofHullName', None), factionOverride, dnaAddition)
        elif graphicID in matchingGraphicIDs:
            matchingTypes[typeID] = GenerateMatch(getattr(graphic, 'sofRaceName', None), getattr(graphic, 'sofHullName', None), getattr(graphic, 'sofFactionName', None), dnaAddition)

    return matchingTypes


def GenerateMatch(race, hull, faction, dnaAddition):
    match = {'race': race,
     'hull': hull,
     'faction': faction}
    if dnaAddition:
        match['dnaAddition'] = dnaAddition
    return match
