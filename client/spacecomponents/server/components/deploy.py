#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\deploy.py
import itertools
from ballpark import GRIDSIZE_LEGACY, AlignToLegacyGrid
from ballpark.deploymenthelper import CheckDeploymentPositionNearPlanetIsValid
from ballpark.distances import GetDistanceFromBallSurface, OffsetPositionInRandomDirection
from eveexceptions.const import UE_GROUPID
from inventorycommon.const import groupStation, groupStargate, groupControlTower, groupWormhole, groupInfrastructureHub, groupSovereigntyClaimMarkers
from inventorycommon.util import IsWormholeSystem
from spacecomponents.common.componentConst import DEPLOY_CLASS
from spacecomponents.common.componentConst import MIN_DISTANCE_FROM_CONTROLTOWER_MAX_VALUE
from eveexceptions import UserError
import geo2
import logging
from eve.common.script.mgt.appLogConst import eventSpaceComponentDeployed
import evetypes
logger = logging.getLogger(__name__)

class Deploy(object):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.itemID = itemID
        self.typeID = typeID
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        if attributes.minDistanceFromControlTower > MIN_DISTANCE_FROM_CONTROLTOWER_MAX_VALUE:
            logger.error('Deploy component on type %d authored with excessive minDistanceFromControlTower attribute %f', self.typeID, attributes.minDistanceFromControlTower)

    def OnDeployed(self, ballpark, characterID, shipID):
        ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentDeployed, self.itemID, referenceID=ballpark.solarsystemID, int_1=self.typeID, bigint_1=characterID, bigint_2=shipID)

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, DEPLOY_CLASS)
        attributeStrings = []
        attributeStrings.append('Min distance from own group: %0.f m' % attributes.minDistanceFromOwnGroup)
        if hasattr(attributes, 'minDistanceFromStargatesAndStations'):
            attributeStrings.append('Min distance from stargate/station: %0.f m' % attributes.minDistanceFromStargatesAndStations)
        attributeStrings.append('Min distance from control tower: %0.f m' % attributes.minDistanceFromControlTower)
        if hasattr(attributes, 'maxDistanceFromControlTower'):
            attributeStrings.append('Max distance from control tower: %0.f m' % attributes.maxDistanceFromControlTower)
        attributeStrings.append('Deploy at range: %0.f m' % attributes.deployAtRange)
        if hasattr(attributes, 'minDistanceFromWormhole'):
            attributeStrings.append('Min distance from wormhole: %0.f m' % attributes.minDistanceFromWormhole)
        if hasattr(attributes, 'minPlanetDistance'):
            attributeStrings.append('Min distance from planet: %0.f m' % attributes.minPlanetDistance)
        if hasattr(attributes, 'maxSecurityLevel'):
            attributeStrings.append('Max solarsystem security level: %0.2f' % attributes.maxSecurityLevel)
        if hasattr(attributes, 'maxPerSolarSystem'):
            attributeStrings.append('Max per solarsystem: %d' % attributes.maxPerSolarSystem)
        if hasattr(attributes, 'defaultOwner'):
            attributeStrings.append('Default owner: %s' % attributes.defaultOwner)
        if hasattr(attributes, 'isForPlayerOwnableSpace'):
            attributeStrings.append('Is for player-ownable space only? %s' % attributes.isForPlayerOwnableSpace)
        if hasattr(attributes, 'Disallow in wormhole space'):
            attributeStrings.append('Default owner: %s' % attributes.disallowInWormholeSpace)
        if hasattr(attributes, 'Requires alliance?'):
            attributeStrings.append('Default owner: %s' % attributes.requiresAlliance)
        infoString = '<br>'.join(attributeStrings)
        return infoString


def CheckBallForProximityRestrictions(ballID, position, radius, typeID, ballpark, groupProximityChecks, forbidOverlap = False):
    ballSlimItem = ballpark.slims[ballID]
    ballGroupID = ballSlimItem.groupID
    distance = GetDistanceFromBallSurface(ballID, position, radius, ballpark)
    if ballGroupID in groupProximityChecks:
        distanceToCheck = groupProximityChecks[ballGroupID]
        if distanceToCheck > 0 and distance < distanceToCheck:
            errorAttributes = {'distance': distanceToCheck,
             'typeID': typeID,
             'groupName': (UE_GROUPID, ballGroupID)}
            raise UserError('CantDeployNearGroup', errorAttributes)
    elif forbidOverlap and distance <= 0.0:
        ball = ballpark.GetBall(ballID)
        if not ball.isFree:
            raise UserError('CantDeployTypeInWay', {'typeID': ballSlimItem.typeID,
             'deployTypeID': typeID})


def CheckForControlTowerInRange(ballPark, typeID, position, radius, maxDistanceFromControlTower):
    found = False
    for ballID in ballPark.controlTowers:
        distance = GetDistanceFromBallSurface(ballID, position, radius, ballPark)
        if distance <= maxDistanceFromControlTower:
            found = True

    if not found:
        errorAttributes = {'typeID': typeID,
         'maxDistance': maxDistanceFromControlTower}
        raise UserError('CantDeployTooFarFromControlTower', errorAttributes)


def CheckSecurityLevel(typeID, ballpark, componentAttributes):
    if ballpark.security > componentAttributes.maxSecurityLevel:
        raise UserError('CantDeploySecurityLevelRestrictionTooHigh', {'typeID': typeID,
         'maxSecurityLevel': componentAttributes.maxSecurityLevel,
         'systemSecurity': ballpark.security})


def CheckMaxPerSolarSystem(maxPerSolarSystem, typeID, componentRegistry):
    numComponents = 0
    groupID = evetypes.GetGroupID(typeID)
    for component in componentRegistry.GetInstancesWithComponentClass(DEPLOY_CLASS):
        if evetypes.GetGroupID(component.typeID) == groupID:
            numComponents += 1
        if numComponents >= maxPerSolarSystem:
            raise UserError('CantDeployMaxPerSolarSystemExceeded', {'typeID': typeID,
             'maxPerSolarSystem': maxPerSolarSystem})


def CheckWormholeSpaceRestriction(solarSystemID, typeID, componentAttributes):
    if componentAttributes.disallowInWormholeSpace and IsWormholeSystem(solarSystemID):
        raise UserError('NotAllowedToDeployInWormholeSpace', {'deployTypeID': typeID})


def CheckPlanetProximity(shipID, position, radius, componentAttributes, typeID, ballpark):
    if hasattr(componentAttributes, 'minPlanetDistance'):
        planetID = ballpark.FindClosestPlanet(shipID)
        CheckDeploymentPositionNearPlanetIsValid(position, planetID, typeID, componentAttributes.minPlanetDistance, ballpark, 'CantLaunchItemNotNearPlanet', 'CantLaunchGlobalNearby')


def CheckPlayerOwnableSpace(ballpark, typeID, componentAttributes):
    if componentAttributes.isForPlayerOwnableSpace and ballpark.IsOwnedByEmpire():
        raise UserError('CanOnlyBeDeployedInNonEmpireSpace', {'deployTypeID': typeID})


def GetLauncherOwnerID(spaceComponentStaticData, typeID):
    componentAttributes = spaceComponentStaticData.GetAttributes(typeID, DEPLOY_CLASS)
    return getattr(componentAttributes, 'defaultOwner', None)


def CheckLaunchRestrictions(shipID, spaceComponentStaticData, position, radius, typeID, ballpark, forbidOverlap = False):
    componentAttributes = spaceComponentStaticData.GetAttributes(typeID, DEPLOY_CLASS)
    CheckPlayerOwnableSpace(ballpark, typeID, componentAttributes)
    if hasattr(componentAttributes, 'maxPerSolarSystem'):
        CheckMaxPerSolarSystem(componentAttributes.maxPerSolarSystem, typeID, ballpark.componentRegistry)
    minDistanceFromStargatesAndStations = getattr(componentAttributes, 'minDistanceFromStargatesAndStations', 0.0)
    minDistanceFromWormhole = getattr(componentAttributes, 'minDistanceFromWormhole', 0.0)
    CheckSecurityLevel(typeID, ballpark, componentAttributes)
    CheckWormholeSpaceRestriction(ballpark.solarsystemID, typeID, componentAttributes)
    ballSearchDistance = max(minDistanceFromStargatesAndStations, componentAttributes.minDistanceFromOwnGroup, componentAttributes.minDistanceFromControlTower, minDistanceFromWormhole, radius)
    groupProximityChecks = {evetypes.GetGroupID(typeID): componentAttributes.minDistanceFromOwnGroup,
     groupControlTower: componentAttributes.minDistanceFromControlTower,
     groupStargate: minDistanceFromStargatesAndStations,
     groupStation: minDistanceFromStargatesAndStations,
     groupWormhole: minDistanceFromWormhole}
    ballsInRange = ballpark.GetBallIdsInRange(position[0], position[1], position[2], ballSearchDistance)
    for ballID in ballsInRange:
        if ballID < 0:
            continue
        CheckBallForProximityRestrictions(ballID, position, radius, typeID, ballpark, groupProximityChecks, forbidOverlap)

    if hasattr(componentAttributes, 'maxDistanceFromControlTower'):
        CheckForControlTowerInRange(ballpark, typeID, position, radius, componentAttributes.maxDistanceFromControlTower)
    CheckPlanetProximity(shipID, position, radius, componentAttributes, typeID, ballpark)


def IterViablePositions(shipID, typeID, radius, spaceComponentStaticData, ballpark):
    componentAttributes = spaceComponentStaticData.GetAttributes(typeID, DEPLOY_CLASS)
    minDistanceFromAPlanet = getattr(componentAttributes, 'minPlanetDistance', 0)
    shipPosition = ballpark.GetBallPosition(shipID)
    if not minDistanceFromAPlanet:
        deployAtRange = getattr(spaceComponentStaticData, 'deployAtRange', 0) + radius + ballpark.GetBallRadius(shipID)
        yield OffsetPositionInRandomDirection(shipPosition, deployAtRange)
    else:
        offsets = [0, -1 * GRIDSIZE_LEGACY, 1 * GRIDSIZE_LEGACY]
        shipPosition = AlignToLegacyGrid(shipPosition)
        for offset in itertools.product(offsets, repeat=3):
            yield geo2.Vec3AddD(shipPosition, offset)


def CheckOwnerRestrictions(spaceComponentStaticData, typeID, corpID, allianceRegistry):
    componentAttributes = spaceComponentStaticData.GetAttributes(typeID, DEPLOY_CLASS)
    if componentAttributes.requiresAlliance and allianceRegistry.AllianceIDFromCorpID(corpID) is None:
        raise UserError('CannotLaunchRequiresAlliance', {'deployTypeID': typeID})


def DeployItem(charID, corpID, shipItem, deployableItem, ownerID, radius, ballpark, allianceRegistry, spaceComponentStaticData, deployAction):
    CheckOwnerRestrictions(spaceComponentStaticData, deployableItem.typeID, corpID, allianceRegistry)
    errors = []
    pos = None
    groupID = evetypes.GetGroupID(deployableItem.typeID)
    forbidOverlap = groupID in [groupInfrastructureHub, groupSovereigntyClaimMarkers]
    for pos in IterViablePositions(shipItem.itemID, deployableItem.typeID, radius, spaceComponentStaticData, ballpark):
        try:
            CheckLaunchRestrictions(shipItem.itemID, spaceComponentStaticData, pos, radius, deployableItem.typeID, ballpark, forbidOverlap)
            break
        except UserError as e:
            errors.append(e)

    else:
        if errors:
            raise errors[0]

    if pos is None:
        raise RuntimeError('IterViablePositions yielded no results')
    return deployAction(charID, shipItem.itemID, deployableItem, deployableItem.itemID, ownerID, shipItem, pos)
