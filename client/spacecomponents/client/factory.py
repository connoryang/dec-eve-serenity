#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\factory.py
from billboards.spacecomponents.client import billboard
from entosis.spacecomponents.client.disruptableStationService import DisruptableStationService
from entosis.spacecomponents.client.entosisCommandNode import EntosisCommandNode
from entosis.spacecomponents.client.entosisSovereigntyStructure import EntosisSovereigntyStructure
from spacecomponents.common import componentConst
from spacecomponents.client.components import dogmatic
from spacecomponents.client.components import scoop
from spacecomponents.client.components import cargobay
from spacecomponents.client.components import decay
from spacecomponents.client.components import activate
from spacecomponents.client.components import deploy
from spacecomponents.client.components import fitting
from spacecomponents.client.components import cynoInhibitor
from spacecomponents.client.components import reinforce
from spacecomponents.client.components import autoTractorBeam
from spacecomponents.client.components import autoLooter
from spacecomponents.client.components import siphon
from spacecomponents.client.components import bountyEscrow
from spacecomponents.common.components import bookmark
from spacecomponents.common.components import physics
from spacecomponents.client.components import scanblocker
from spacecomponents.client.components import microJumpDriver
from spacecomponents.client.components import warpDisruption
from spacecomponents.client.components import behavior
from spacecomponents.client.components import turboshield
from spacecomponents.client.components import itemtrader
from spacecomponents.client.components import jumpPolarization
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
 componentConst.SIPHON_CLASS: siphon.Siphon,
 componentConst.PHYSICS_CLASS: physics.Physics,
 componentConst.BOUNTYESCROW_CLASS: bountyEscrow.BountyEscrow,
 componentConst.SCAN_BLOCKER_CLASS: scanblocker.ScanBlocker,
 componentConst.MICRO_JUMP_DRIVER_CLASS: microJumpDriver.MicroJumpDriver,
 componentConst.WARP_DISRUPTION_CLASS: warpDisruption.WarpDisruption,
 componentConst.BEHAVIOR: behavior.Behavior,
 componentConst.TURBO_SHIELD_CLASS: turboshield.TurboShield,
 componentConst.ENTOSIS_COMMAND_NODE: EntosisCommandNode,
 componentConst.DISRUPTABLE_STATION_SERVICE: DisruptableStationService,
 componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE: EntosisSovereigntyStructure,
 componentConst.CONQUERABLE_STATION: EntosisSovereigntyStructure,
 componentConst.ITEM_TRADER: itemtrader.ItemTrader,
 componentConst.JUMP_POLARIZATION_CLASS: jumpPolarization.JumpPolarization,
 componentConst.BILLBOARD_CLASS: billboard.BillboardComponent}

def GetComponentClass(componentName):
    return COMPONENTS[componentName]
