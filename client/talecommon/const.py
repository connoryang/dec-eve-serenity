#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\talecommon\const.py
import collections
from brennivin.itertoolsext import Bundle
from dogma.const import attributeScanGravimetricStrength
from inventorycommon.const import ownerUnknown
from eve.common.lib.appConst import securityClassZeroSec, securityClassLowSec, securityClassHighSec
from eve.common.lib.appConst import rewardTypeLP
templates = Bundle(incursion=2, knownSpace=3, solarSystem=4, spreadingIncursion=5)
actionClass = Bundle(spawnOneDungeonAtEachCelestial=1, spawnManyDungeonsAtLocation=2, disableDjinns=3, addDjinnCommand=4, addSystemEffectBeacon=5, addStartSceneAtSceneInfluenceTrigger=6, initializeInfluence=7, setBountySurcharge=8, endTale=9, spawnDungeonAtDeterministicLocation=10, spawnNPCsAtLocation=11, addPeriodicInfluenceTrigger=12, grantTaleReward=13, clearTaleReward=14)
conditionClass = Bundle(checkSolarSystemSecurity=1, checkInitiationChance=2, checkWorldLocation=3, checkInfluence=4)
systemInfluenceAny = 0
systemInfluenceDecline = 1
systemInfluenceRising = 2
Parameter = collections.namedtuple('Parameter', 'name parameterType defaultValue prettyName description')
parameterByID = {1: Parameter('dungeonID', int, 0, 'Dungeon ID', 'The ID of the dungeon to spawn'),
 2: Parameter('dungeonListID', int, None, 'Dungeon list ID', 'The ID of the list of dungeons to spawn'),
 3: Parameter('dungeonRespawnTime', int, 1, 'Dungeon respawn time', 'Dungeon respawn time in minutes'),
 4: Parameter('dungeonScanStrength', int, 100, 'Dungeon scan strength', 'Dungeon scan strength for scanning down the dungeon'),
 5: Parameter('dungeonSignatureRadius', float, 100.0, 'Dungeon signature radius', 'Dungeon signature radius used for scanning down the dungeon'),
 6: Parameter('dungeonScanStrengthAttrib', float, attributeScanGravimetricStrength, 'Dungeon scan attribute', 'Dungeon scan attribute'),
 7: Parameter('dungeonSpawnLocation', float, None, 'Dungeon spawn location', 'The locations in space where the dungeon is going to respawn'),
 8: Parameter('dungeonSpawnQuantity', int, 1, 'Number of Dungeons', 'The number of dungeons which have to be spawned'),
 9: Parameter('triggeredScene', int, None, 'Triggered Scene', 'The scene which is added to the trigger location when activated'),
 10: Parameter('triggeredSceneLocation', int, None, 'Trigger Location', 'The location the triggered scene is added when the trigger is activated'),
 15: Parameter('disableConvoyDjinn', bool, False, 'Disable convoy djinn', 'Disables the convoy djinn during the tale'),
 16: Parameter('disableCustomsPoliceDjinn', bool, False, 'Disable custom police djinn', 'Disables the custom police during the tale'),
 17: Parameter('disableEmpirePoliceDjinn', bool, False, 'Disable empire police djinn', 'Disables the empire police during the tale'),
 18: Parameter('disableMilitaryFactionDjinn', bool, False, 'Disable military faction djinn', 'Disables the military faction djinn during the tale'),
 19: Parameter('disablePirateDjinn', bool, False, 'Disable pirate djinn', 'Disables the pirate djinn during the tale'),
 20: Parameter('disablePirateAutoDjinn', bool, False, 'Disable pirate auto djinn', 'Disables the pirate auto djinn during the tale'),
 21: Parameter('disablePirateStargateDjinn', bool, False, 'Disable pirate stargate djinn', 'Disables the pirate Stargate djinn during the tale'),
 22: Parameter('djinnCommandID', int, 0, 'Djinn command ID', 'The djinn command ID in this is added to solar system the scene is running in'),
 23: Parameter('systemEffectBeaconTypeID', int, 0, 'System effect beacon type ID', 'The type ID of the systems effect beacon'),
 24: Parameter('systemEffectBeaconBlockCynosural', bool, False, 'System effect beacon blocks cyno', 'The system effect beacon will also block cynosural jump'),
 25: Parameter('systemInfluenceTriggerDirection', int, systemInfluenceAny, 'Trigger direction', 'What direction the influence should change before the trigger is triggered'),
 26: Parameter('systemInfluenceTriggerValue', float, 0.0, 'Trigger value', 'The value around which the trigger should be triggered'),
 27: Parameter('dummyParameter', float, 0.0, 'Dummy Parameter', 'This is a dummy parameter for actions that take no parameters'),
 28: Parameter('surchargeRate', float, 0.2, 'Surcharge Rate', 'This is the surcharge rate that will be applied to this system'),
 29: Parameter('ownerID', int, ownerUnknown, 'Owner ID', 'Specifies the owner for items deployed through the scene.'),
 30: Parameter('entityTypeID', int, 0, 'Entity TypeID', 'The typeID for NPC to spawn.'),
 31: Parameter('entityAmountMin', int, 1, 'Minimum Entity Spawn Amount', 'The minimum amount of NPCs that should spawn.'),
 32: Parameter('entityAmountMax', int, 1, 'Maximum Entity Spawn Amount', 'The maximum amount of NPCs that should spawn.'),
 44: Parameter('entityGroupId', int, 0, 'Entity Group ID', 'NPC Group ID used to spawn a group of picked NPCs. Overwrites entityTypeID if not None.'),
 45: Parameter('entitySpawnListId', int, 0, 'Entity Spawnlist ID', 'Spawnlist used for picking a single NPC group. Overwrites entityGroupId and entityTypeID if not None.'),
 33: Parameter('entityGroupRespawnTimer', int, 30, 'Group Respawn Timer', 'The time (in minutes) it will take for the whole group to respawn if killed.'),
 34: Parameter('entityReinforcementTypeList', int, 0, 'Reinforcement Spawnlist ID', 'The list of entity groups used for reinforcing the NPC spawn - see: gd/npc/classes&groups and gd/spawnlists.'),
 35: Parameter('entityReinforcementCooldownTimer', int, 0, 'Reinforcement Cooldown Timer', 'The time (in seconds) that can pass between the NPC group asking for reinforcements.'),
 41: Parameter('entityBehaviorTree', str, 'None', 'Behavior Tree Type', 'The type of behavior these NPCs will get spawned with'),
 51: Parameter('entityGroupBehaviorTree', str, 'None', 'Behavior Group Tree Type', 'The type of group behavior these NPCs will get spawned with'),
 42: Parameter('entityGlobalExplorationGroups', int, 0, 'Global Groups for Exploration', 'The list of groupIDs that the NPCs will travel to.'),
 43: Parameter('entityGlobalExplorationOverwrite', bool, False, 'Overwrite Global Exploration', 'Overwrites normal exploration groups, else it extends it.'),
 11: Parameter('solarSystemSecurityMin', float, 1.0, 'Security minimum', 'The security level of the solar system has to be above this before the condition is true'),
 12: Parameter('solarSystemSecurityMax', float, 0.0, 'Security maximum', 'The security level of the solar system has to be below this before the condition is true'),
 13: Parameter('solarSystemSecurityMinInclusive', bool, True, 'Security minimum inclusive', 'This is whether the minimum should be inclusive or exclusive'),
 14: Parameter('solarSystemSecurityMaxInclusive', bool, False, 'Security maximum inclusive', 'This is whether the maximum should be inclusive or exclusive'),
 37: Parameter('initiateActionsChance', int, 1, 'Action Initiation Chance', 'Chance of initiating any condition/action after this condition.'),
 40: Parameter('invertCondition', bool, False, 'Invert Condition', 'Inverts the true/false result for the condition check; NOT.'),
 38: Parameter('worldLocationId', int, 0, 'World Location ID', 'The ID of a SolarSystem, Region or Constellation, used along with World Location Type.'),
 39: Parameter('worldLocationListId', int, 0, 'World Location List ID', 'The ID of a list containing a group of locations - overwrites base ID if specified.'),
 50: Parameter('influenceStatus', float, 0, 'Influence Status', 'Checks if influence has reached a certain value.'),
 46: Parameter('influencePeriodicTriggerIntervalMinutes', int, 60, 'Periodic Interval', 'Number of minutes between the trigger firing'),
 47: Parameter('influencePeriodicTriggerInfluenceMin', int, 0.0, 'Min Trigger Influence', 'The minimum influence (inclusive) for trigger firing (two decimals)'),
 48: Parameter('influencePeriodicTriggerInfluenceMax', int, 1.0, 'Max Trigger Influence', 'The maximum influence (inclusive) for trigger firing (two decimals)'),
 49: Parameter('influencePeriodicTriggerActionId', int, 0, 'The action to trigger', 'The action to take when the trigger fires succesfully')}
parameter = Bundle()
for _parameterID, _parameterLine in parameterByID.iteritems():
    setattr(parameter, _parameterLine.name, _parameterID)

sceneTypeMinConditional = 1000001
sceneTypeMinSystem = 5000001
scenesTypes = Bundle()
conditionalScenesTypes = Bundle()
sceneTypesByID = {1: Bundle(name='headquarters', display='Headquarters'),
 2: Bundle(name='assault', display='Assault'),
 3: Bundle(name='vanguard', display='Vanguard'),
 4: Bundle(name='staging', display='Staging'),
 5: Bundle(name='testscene', display='Test Scene'),
 6: Bundle(name='system', display='Solar System'),
 7: Bundle(name='incursionNeutral', display='Incursion Neutral'),
 8: Bundle(name='incursionStaging', display='Incursion Staging'),
 9: Bundle(name='incursionLightInfestation', display='Incursion Light Infestation'),
 10: Bundle(name='incursionMediumInfestation', display='Incursion Medium Infestation'),
 11: Bundle(name='incursionHeavyInfestation', display='Incursion Heavy Infestation'),
 12: Bundle(name='incursionFinalEncounter', display='Incursion Final Encounter'),
 13: Bundle(name='incursionEndTale', display='Incursion End Tale'),
 1000001: Bundle(name='boss', display='Boss Spawn'),
 1000002: Bundle(name='endTale', display='End Tale'),
 2000001: Bundle(name='testscene1', display='Conditional Test Scene 1'),
 2000002: Bundle(name='testscene2', display='Conditional Test Scene 2'),
 2000003: Bundle(name='testscene3', display='Conditional Test Scene 3'),
 2000004: Bundle(name='testscene4', display='Conditional Test Scene 4'),
 2000005: Bundle(name='testscene5', display='Conditional Test Scene 5'),
 5000001: Bundle(name='managerInit', display='Initialize Manager ')}
for _constID, _constNames in sceneTypesByID.iteritems():
    setattr(scenesTypes, _constNames.name, _constID)

distributionStatus = Bundle(success=1, locationAlreadyUsed=2, failedRequirementFromTemplate=3, exception=4, hardKilled=5)
securityClassToParameterString = {securityClassZeroSec: 'DistributeNullSec',
 securityClassLowSec: 'DistributeLowSec',
 securityClassHighSec: 'DistributeHighSec'}
KNOWN_SPACE_RANDOM_SEED = 42
BLACKLIST_GENERIC = 1
BLACKLIST_INCURSIONS = 3
BLACKLIST_SLEEPER_SCOUTS = 4
DETERMINISTIC_PLACEMENT_AU_DISTANCE = 0.2
INCURSION_TEMPLATES = (templates.incursion, templates.spreadingIncursion)
INCURSION_DISTRIBUTIONS_STRING = '%d,%d' % INCURSION_TEMPLATES
INCURSION_STAGING_SCENE_TYPES_STRING = '%d,%d' % (scenesTypes.staging, scenesTypes.incursionStaging)
TALE_VISUAL_OVERLAYS = {1: 'INCURSION_OVERLAY'}
TALE_REWARD_ADJUSTMENTS = {'finalRewardAdjustmentType': rewardTypeLP,
 'finalRewardMaxAdjustment': 0.2,
 'finalRewardAdjustmentStep': 0.02}
TALE_SYSTEM_MODIFIERS = {1: [{'name': 'effectIcon_cyno',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectCyno.png',
      'hint': 'UI/Incursion/HUD/SystemEffectCynoHint',
      'isScalable': False},
     {'name': 'effectIcon_tax',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectTax.png',
      'hint': 'UI/Incursion/HUD/SystemEffectTaxHint',
      'isScalable': False},
     {'name': 'effectIcon_tank',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectResistanceDecrease.png',
      'hint': 'UI/Incursion/HUD/SystemEffectTankingHint',
      'isScalable': True},
     {'name': 'effectIcon_damage',
      'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectDamageDecrease.png',
      'hint': 'UI/Incursion/HUD/SystemEffectDamageHint',
      'isScalable': True}],
 36: [{'name': 'effectIcon_cyno',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectCyno.png',
       'hint': 'UI/Incursion/HUD/SystemEffectCynoHint',
       'isScalable': False},
      {'name': 'effectIcon_damage',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectDamageDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectDamageHint',
       'isScalable': True},
      {'name': 'effectIcon_armor',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectResistanceDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectArmorHint',
       'isScalable': True},
      {'name': 'effectIcon_shield',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectShieldDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectShieldHint',
       'isScalable': True},
      {'name': 'effectIcon_velocity',
       'texturePath': 'res:/UI/Texture/classes/InfluenceBar/effectVelocityDecrease.png',
       'hint': 'UI/Incursion/HUD/SystemEffectVelocityHint',
       'isScalable': True}]}
TALE_DISTRIBUTION_BLACKLIST = 11
GROW_TALE_TRIGGER_ACTION = 1
SHRINK_TALE_TRIGGER_ACTION = 2
