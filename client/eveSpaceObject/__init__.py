#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveSpaceObject\__init__.py
import geo2
import trinity
import eve.common.lib.appConst as const
gfxRaceAmarr = 'amarr'
gfxRaceCaldari = 'caldari'
gfxRaceGallente = 'gallente'
gfxRaceMinmatar = 'minmatar'
gfxRaceJove = 'jove'
gfxRaceAngel = 'angel'
gfxRaceSleeper = 'sleeper'
gfxRaceORE = 'ore'
gfxRaceConcord = 'concord'
gfxRaceRogue = 'rogue'
gfxRaceSansha = 'sansha'
gfxRaceSOCT = 'soct'
gfxRaceTalocan = 'talocan'
gfxRaceGeneric = 'generic'
gfxRaceSoE = 'soe'
gfxRaceMordu = 'mordu'
DEFAULT_SCENE_PATH = 'res:/dx9/Scene/preview/ship_other.red'

def GetScenePathByRaceID(raceID):
    scenePaths = {const.raceCaldari: 'res:/dx9/Scene/preview/ship_caldari.red',
     const.raceMinmatar: 'res:/dx9/Scene/preview/ship_minmatar.red',
     const.raceGallente: 'res:/dx9/Scene/preview/ship_gallente.red',
     const.raceAmarr: 'res:/dx9/Scene/preview/ship_amarr.red'}
    return scenePaths.get(raceID, DEFAULT_SCENE_PATH)


def GetScenePathByRaceName(raceName):
    scenePaths = {gfxRaceAmarr: 'res:/dx9/scene/iconbackground/amarr.red',
     gfxRaceAngel: 'res:/dx9/scene/iconbackground/angel.red',
     gfxRaceCaldari: 'res:/dx9/scene/iconbackground/caldari.red',
     gfxRaceConcord: 'res:/dx9/scene/iconbackground/concord.red',
     gfxRaceGallente: 'res:/dx9/scene/iconbackground/gallente.red',
     gfxRaceGeneric: 'res:/dx9/scene/iconbackground/generic.red',
     gfxRaceJove: 'res:/dx9/scene/iconbackground/jove.red',
     gfxRaceMinmatar: 'res:/dx9/scene/iconbackground/minmatar.red',
     gfxRaceMordu: 'res:/dx9/scene/iconbackground/mordu.red',
     gfxRaceORE: 'res:/dx9/scene/iconbackground/ore.red',
     gfxRaceRogue: 'res:/dx9/scene/iconbackground/rogue.red',
     gfxRaceSansha: 'res:/dx9/scene/iconbackground/sansha.red',
     gfxRaceSleeper: 'res:/dx9/scene/iconbackground/sleeper.red',
     gfxRaceSOCT: 'res:/dx9/scene/iconbackground/soct.red',
     gfxRaceSoE: 'res:/dx9/scene/iconbackground/soe.red',
     gfxRaceTalocan: 'res:/dx9/scene/iconbackground/talocan.red'}
    return scenePaths.get(raceName, 'res:/dx9/scene/iconbackground/generic.red')


droneTurretGfxID_fighterbomber = {gfxRaceAmarr: 11515,
 gfxRaceGallente: 11517,
 gfxRaceCaldari: 11516,
 gfxRaceMinmatar: 11518,
 gfxRaceSansha: 20339}
droneTurretGfxID_mining = 11521
droneTurretGfxID_combat = {gfxRaceAmarr: 11504,
 gfxRaceGallente: 11506,
 gfxRaceCaldari: 11505,
 gfxRaceMinmatar: 11508}
droneTurretGfxID_salvager = 20925
droneTurretGfxID_generic = 11507
gfxDroneGroupFighterBomber = 1
gfxDroneGroupCombat = 2
gfxDroneGroupUtility = 3
gfxDroneGroupMining = 4
gfxDroneGroupNpc = 5
gfxDroneGroupSalvager = 6
droneGroupFromTypeGroup = {const.groupFighterBomber: gfxDroneGroupFighterBomber,
 const.groupMiningDrone: gfxDroneGroupMining,
 const.groupSalvageDrone: gfxDroneGroupSalvager,
 const.groupCombatDrone: gfxDroneGroupCombat,
 const.groupFighterDrone: gfxDroneGroupCombat,
 const.groupElectronicWarfareDrone: gfxDroneGroupCombat,
 const.groupStasisWebifyingDrone: gfxDroneGroupCombat,
 const.groupUnanchoringDrone: gfxDroneGroupCombat,
 const.groupRepairDrone: gfxDroneGroupCombat,
 const.groupWarpScramblingDrone: gfxDroneGroupCombat,
 const.groupCapDrainDrone: gfxDroneGroupCombat,
 const.groupLogisticDrone: gfxDroneGroupCombat,
 const.groupSupportFighter: gfxDroneGroupCombat,
 const.groupLCODrone: gfxDroneGroupNpc,
 const.groupRogueDrone: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneBattleCruiser: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneBattleship: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneCruiser: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneDestroyer: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneFrigate: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneHauler: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneSwarm: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneOfficer: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneBattleCruiser: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneBattleship: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneCruiser: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneDestroyer: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneFrigate: gfxDroneGroupNpc,
 const.groupDeadspaceRogueDroneSwarm: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneCommanderFrigate: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneCommanderDestroyer: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneCommanderCruiser: gfxDroneGroupNpc,
 const.groupAsteroidRogueDroneCommanderBattleCruiser: gfxDroneGroupNpc,
 const.groupMissionFighterDrone: gfxDroneGroupNpc}
droneTurretGfxID = {gfxDroneGroupFighterBomber: (droneTurretGfxID_fighterbomber, droneTurretGfxID_generic),
 gfxDroneGroupCombat: (droneTurretGfxID_combat, droneTurretGfxID_generic),
 gfxDroneGroupUtility: (None, None),
 gfxDroneGroupMining: (None, droneTurretGfxID_mining),
 gfxDroneGroupNpc: (droneTurretGfxID_combat, droneTurretGfxID_generic),
 gfxDroneGroupSalvager: (None, droneTurretGfxID_salvager)}
EXPLOSION_BASE_PATH = 'res:/fisfx/deathexplosion/death'

def GetDeathExplosionInfo(model, radius, raceName):
    if raceName is None:
        raceName = gfxRaceRogue
    radius = getattr(model, 'boundingSphereRadius', radius)
    if radius < 20.0:
        size = '_d_'
        delay = 0
        scale = radius / 20.0
    elif radius < 100.0:
        size = '_s_'
        delay = 100
        scale = radius / 100.0
    elif radius < 400.0:
        size = '_m_'
        delay = 250
        scale = radius / 400.0
    elif radius < 1500.0:
        size = '_l_'
        delay = 500
        scale = radius / 700.0
    elif radius < 6000.0:
        size = '_h_'
        delay = 1000
        scale = radius / 6000.0
    else:
        size = '_t_'
        delay = 2000
        scale = 1.0
    path = EXPLOSION_BASE_PATH + size + raceName + '.red'
    info = (delay, scale)
    return (path, info)


def GetDeathExplosionLookDelay(model, radius):
    radius = getattr(model, 'boundingSphereRadius', radius)
    if radius < 20.0:
        radius = 20.0
    elif radius > 6000.0:
        radius = 6000.0
    lerpValue = (radius - 20.0) / 5980.0
    milliseconds = 4000.0 + lerpValue * 4000.0
    return milliseconds


def _GetEffectParameter(effect, name):
    for each in effect.constParameters:
        if each[0] == name:
            return each[1]

    for each in effect.parameters:
        if each.name == name:
            if type(each.value) != tuple or len(each.value) != 4:
                raise KeyError()
            return each.value

    raise KeyError()


def _EnhanceColor(rgb):
    color = trinity.TriColor(*rgb)
    h, s, v = color.GetHSV()
    s = min(s * 1.5, 1)
    color.SetHSV(h, s, v)
    return (color.r, color.g, color.b)


def GetAlbedoColor(spaceObject):
    mesh = spaceObject.mesh or spaceObject.meshLod
    if not mesh:
        return (0, 0, 0, 0)
    color = (0, 0, 0, 0)
    count = 0
    parameterSuffixes = ('DiffuseColor', 'FresnelColor')
    for area in mesh.opaqueAreas:
        if not area.effect:
            continue
        for param in area.effect.parameters:
            if param.name.endswith(parameterSuffixes) and type(param.value) == tuple and len(param.value) == 4:
                color = geo2.Vec4Add(color, param.value)
                count += 1

        for name, value in area.effect.constParameters:
            if name.endswith(parameterSuffixes):
                color = geo2.Vec4Add(color, value)
                count += 1

    if count == 0:
        return (0, 0, 0, 0)
    return _EnhanceColor(geo2.Vec4Scale(color, 1.0 / count))
