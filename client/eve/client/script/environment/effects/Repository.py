#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\Repository.py
from eve.client.script.environment.effects.accelerationGate import AccelerationGate
from eve.client.script.environment.effects.anchoring import AnchorDrop, AnchorLift
from eve.client.script.environment.effects.cloaking import CloakNoAnim, Cloaking, CloakRegardless, Cloak, Uncloak
from eve.client.script.environment.effects.EMPWave import EMPWave
from eve.client.script.environment.effects.GenericEffect import ShipEffect, ShipRenderEffect, StretchEffect, GenericEffect
from eve.client.script.environment.effects.Jump import JumpDriveIn, JumpDriveInBO, JumpDriveOut, JumpDriveOutBO, JumpIn, JumpOut, JumpOutWormhole
from eve.client.script.environment.effects.Jump import GateActivity, WormholeActivity
from eve.client.script.environment.effects.JumpPortal import JumpPortal, JumpPortalBO
from eve.client.script.environment.effects.locatorStretchEffect import LocatorStretchEffect
from eve.client.script.environment.effects.MicroJumpDrive import MicroJumpDriveJump, MicroJumpDriveEngage
from eve.client.script.environment.effects.orbitalStrike import OrbitalStrike
from eve.client.script.environment.effects.siegeMode import SiegeMode
from eve.client.script.environment.effects.skinChange import SkinChange
from eve.client.script.environment.effects.soundEffect import SoundEffect
from eve.client.script.environment.effects.structures import StructureOnlined, StructureOnline, StructureOffline
from eve.client.script.environment.effects.superWeapon import SuperWeapon, SlashWeapon
from eve.client.script.environment.effects.turrets import StandardWeapon, CloudMining, MissileLaunch
from eve.client.script.environment.effects.Warp import Warping
from eve.client.script.environment.effects.WarpDisruptFieldGenerating import WarpDisruptFieldGenerating
from eve.client.script.environment.effects.WarpFlash import WarpFlashOut, WarpFlashIn
from eve.client.script.environment.effects.impactEffect import ImpactEffect
typeToClass = {'AccelerationGate': AccelerationGate,
 'AnchorDrop': AnchorDrop,
 'AnchorLift': AnchorLift,
 'CloakNoAnim': CloakNoAnim,
 'Cloaking': Cloaking,
 'CloakRegardless': CloakRegardless,
 'Cloak': Cloak,
 'Uncloak': Uncloak,
 'EMPWave': EMPWave,
 'ShipEffect': ShipEffect,
 'ShipRenderEffect': ShipRenderEffect,
 'StretchEffect': StretchEffect,
 'LocatorStretchEffect': LocatorStretchEffect,
 'GenericEffect': GenericEffect,
 'ImpactEffect': ImpactEffect,
 'JumpDriveIn': JumpDriveIn,
 'JumpDriveInBO': JumpDriveInBO,
 'JumpDriveOut': JumpDriveOut,
 'JumpDriveOutBO': JumpDriveOutBO,
 'JumpIn': JumpIn,
 'JumpOut': JumpOut,
 'JumpOutWormhole': JumpOutWormhole,
 'GateActivity': GateActivity,
 'WormholeActivity': WormholeActivity,
 'JumpPortal': JumpPortal,
 'JumpPortalBO': JumpPortalBO,
 'MicroJumpDriveJump': MicroJumpDriveJump,
 'MicroJumpDriveEngage': MicroJumpDriveEngage,
 'OrbitalStrike': OrbitalStrike,
 'SiegeMode': SiegeMode,
 'SkinChange': SkinChange,
 'SlashWeapon': SlashWeapon,
 'SoundEffect': SoundEffect,
 'StructureOnlined': StructureOnlined,
 'StructureOnline': StructureOnline,
 'StructureOffline': StructureOffline,
 'StandardWeapon': StandardWeapon,
 'SuperWeapon': SuperWeapon,
 'CloudMining': CloudMining,
 'MissileLaunch': MissileLaunch,
 'Warping': Warping,
 'WarpDisruptFieldGenerating': WarpDisruptFieldGenerating,
 'WarpFlashOut': WarpFlashOut,
 'WarpFlashIn': WarpFlashIn}

def GetClassification(guid):
    effect = cfg.graphicEffects.get(guid, None)
    if effect is None:
        return
    classType = typeToClass.get(effect.type, None)
    graphicID = getattr(effect, 'graphicID', None)
    graphic = cfg.graphics.get(graphicID, None)
    resPath = getattr(graphic, 'graphicFile', None)
    return (classType, effect, resPath)
