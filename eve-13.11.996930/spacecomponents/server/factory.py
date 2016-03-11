#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\factory.py
from entosis.spacecomponents.server.conquerableStation import ConquerableStation
from entosis.spacecomponents.server.entosisLootTarget import EntosisLootTarget
from entosis.spacecomponents.server.disruptableStationService import DisruptableStationService
from entosis.spacecomponents.server.entosisCommandNode import EntosisCommandNode
from entosis.spacecomponents.server.entosisSovereigntyStructure import EntosisSovereigntyStructure
from spacecomponents.common.components import bookmark
from spacecomponents.common import componentConst
from spacecomponents.common.components.component import Component
from spacecomponents.server.components import autoTractorBeam
from spacecomponents.server.components import autoLooter
from spacecomponents.server.components import bountyEscrow
from spacecomponents.server.components import dogmatic
from spacecomponents.server.components import scoop
from spacecomponents.server.components import cargobay
from spacecomponents.server.components import decay
from spacecomponents.server.components import activate
from spacecomponents.server.components import deploy
from spacecomponents.server.components import fitting
from spacecomponents.server.components import cynoInhibitor
from spacecomponents.server.components import reinforce
from spacecomponents.server.components import siphon
from spacecomponents.server.components import microJumpDriver
from spacecomponents.common.components import physics
from spacecomponents.server.components import scanblocker
from spacecomponents.server.components import warpDisruption
from spacecomponents.server.components import behavior
from spacecomponents.server.components import npcpilot
from spacecomponents.server.components import turboshield
from spacecomponents.server.components import proximitysensor
from spacecomponents.server.components import itemtrader
COMPONENTS = {componentConst.DEPLOY_CLASS: deploy.Deploy,
 componentConst.ACTIVATE_CLASS: activate.Activate,
 componentConst.DOGMATIC_CLASS: dogmatic.Dogmatic,
 componentConst.SCOOP_CLASS: scoop.Scoop,
 componentConst.DECAY_CLASS: decay.Decay,
 componentConst.FITTING_CLASS: fitting.Fitting,
 componentConst.CARGO_BAY: cargobay.CargoBay,
 componentConst.CYNO_INHIBITOR_CLASS: cynoInhibitor.CynoInhibitor,
 componentConst.REINFORCE_CLASS: reinforce.Reinforce,
 componentConst.AUTO_TRACTOR_BEAM_CLASS: autoTractorBeam.AutoTractorBeam,
 componentConst.AUTO_LOOTER_CLASS: autoLooter.AutoLooter,
 componentConst.BOOKMARK_CLASS: bookmark.Bookmark,
 componentConst.BOUNTYESCROW_CLASS: bountyEscrow.BountyEscrow,
 componentConst.SIPHON_CLASS: siphon.Siphon,
 componentConst.PHYSICS_CLASS: physics.Physics,
 componentConst.SCAN_BLOCKER_CLASS: scanblocker.ScanBlocker,
 componentConst.MICRO_JUMP_DRIVER_CLASS: microJumpDriver.MicroJumpDriver,
 componentConst.WARP_DISRUPTION_CLASS: warpDisruption.WarpDisruption,
 componentConst.BEHAVIOR: behavior.Behavior,
 componentConst.NPC_PILOT: npcpilot.NpcPilot,
 componentConst.TURBO_SHIELD_CLASS: turboshield.TurboShield,
 componentConst.PROXIMITY_SENSOR_CLASS: proximitysensor.ProximitySensor,
 componentConst.TARGETING: Component,
 componentConst.ENTOSIS_LOOT_TARGET: EntosisLootTarget,
 componentConst.DISRUPTABLE_STATION_SERVICE: DisruptableStationService,
 componentConst.ENTOSIS_COMMAND_NODE: EntosisCommandNode,
 componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE: EntosisSovereigntyStructure,
 componentConst.CONQUERABLE_STATION: ConquerableStation,
 componentConst.NPC_WARP_BEACON: Component,
 componentConst.ITEM_TRADER: itemtrader.ItemTrader}

def GetComponentClass(componentName):
    return COMPONENTS[componentName]
