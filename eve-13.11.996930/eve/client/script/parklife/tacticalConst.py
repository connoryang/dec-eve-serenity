#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tacticalConst.py
from carbonui.util.various_unsorted import SortListOfTuples
import evetypes
filterGroups = {const.groupStationServices,
 const.groupSecondarySun,
 const.groupTemporaryCloud,
 const.groupSolarSystem,
 const.groupRing,
 const.groupConstellation,
 const.groupRegion,
 const.groupCloud,
 const.groupComet,
 const.groupCosmicAnomaly,
 const.groupCosmicSignature,
 const.groupGlobalWarpDisruptor,
 const.groupPlanetaryCloud,
 const.groupCommandPins,
 const.groupExtractorPins,
 const.groupPlanetaryLinks,
 const.groupProcessPins,
 const.groupSpaceportPins,
 const.groupStoragePins,
 11,
 const.groupExtractionControlUnitPins,
 const.groupDefenseBunkers,
 const.groupAncientCompressedIce,
 const.groupTerranArtifacts,
 const.groupShippingCrates,
 const.groupProximityDrone,
 const.groupRepairDrone,
 const.groupUnanchoringDrone,
 const.groupWarpScramblingDrone,
 const.groupZombieEntities,
 const.groupForceFieldArray,
 const.groupLogisticsArray,
 const.groupMobilePowerCore,
 const.groupMobileShieldGenerator,
 const.groupMobileStorage,
 const.groupStealthEmitterArray,
 const.groupStructureRepairArray,
 const.groupTargetPaintingBattery}
validCategories = (const.categoryStation,
 const.categoryShip,
 const.categoryEntity,
 const.categoryCelestial,
 const.categoryAsteroid,
 const.categoryDrone,
 const.categoryDeployable,
 const.categoryStarbase,
 const.categoryCharge,
 const.categorySovereigntyStructure,
 const.categoryPlanetaryInteraction,
 const.categoryOrbital)
bombGroups = (const.groupBomb,
 const.groupBombECM,
 const.groupBombEnergy,
 const.groupScannerProbe,
 const.groupWarpDisruptionProbe,
 const.groupSurveyProbe)
groups = []
for groupID in evetypes.IterateGroups():
    categoryID = evetypes.GetCategoryIDByGroup(groupID)
    if categoryID == const.categoryCharge and groupID not in bombGroups:
        continue
    if categoryID not in validCategories:
        continue
    if groupID in filterGroups:
        continue
    groupName = evetypes.GetGroupNameByGroup(groupID)
    groups.append((groupName.lower(), (groupID, groupName)))

groupList = SortListOfTuples(groups)
groupIDs = set((each[0] for each in groupList))
