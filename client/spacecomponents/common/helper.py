#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\helper.py
from ccpProfile import TimedFunction
import componentConst

def TypeHasComponent(typeID, componentClassName):
    return cfg.spaceComponentStaticData.TypeHasComponentWithName(typeID, componentClassName)


@TimedFunction('SpaceComponent::Helper::HasScoopComponent')
def HasScoopComponent(typeID):
    return TypeHasComponent(typeID, componentConst.SCOOP_CLASS)


@TimedFunction('SpaceComponent::Helper::HasActivateComponent')
def HasActivateComponent(typeID):
    return TypeHasComponent(typeID, componentConst.ACTIVATE_CLASS)


@TimedFunction('SpaceComponent::Helper::HasDeployComponent')
def HasDeployComponent(typeID):
    return TypeHasComponent(typeID, componentConst.DEPLOY_CLASS)


@TimedFunction('SpaceComponent::Helper::HasDecayComponent')
def HasDecayComponent(typeID):
    return TypeHasComponent(typeID, componentConst.DECAY_CLASS)


@TimedFunction('SpaceComponent::Helper::HasDogmaticComponent')
def HasDogmaticComponent(typeID):
    return TypeHasComponent(typeID, componentConst.DOGMATIC_CLASS)


@TimedFunction('SpaceComponent::Helper::HasFittingComponent')
def HasFittingComponent(typeID):
    return TypeHasComponent(typeID, componentConst.FITTING_CLASS)


@TimedFunction('SpaceComponent::Helper::HasCargoBayComponent')
def HasCargoBayComponent(typeID):
    return TypeHasComponent(typeID, componentConst.CARGO_BAY)


@TimedFunction('SpaceComponent::Helper::HasReinforceComponent')
def HasReinforceComponent(typeID):
    return TypeHasComponent(typeID, componentConst.REINFORCE_CLASS)


@TimedFunction('SpaceComponent::Helper::HasPhysicsComponent')
def HasPhysicsComponent(typeID):
    return TypeHasComponent(typeID, componentConst.PHYSICS_CLASS)


@TimedFunction('SpaceComponent::Helper::HasBountyEscrowComponent')
def HasBountyEscrowComponent(typeID):
    return TypeHasComponent(typeID, componentConst.BOUNTYESCROW_CLASS)


@TimedFunction('SpaceComponent::Helper::HasSiphonComponent')
def HasSiphonComponent(typeID):
    return TypeHasComponent(typeID, componentConst.SIPHON_CLASS)


@TimedFunction('SpaceComponent::Helper::HasBountyEscrowComponent')
def HasBountyEscrowComponent(typeID):
    return TypeHasComponent(typeID, componentConst.BOUNTYESCROW_CLASS)


@TimedFunction('SpaceComponent::Helper::HasMicroJumpDriverComponent')
def HasMicroJumpDriverComponent(typeID):
    return TypeHasComponent(typeID, componentConst.MICRO_JUMP_DRIVER_CLASS)


@TimedFunction('SpaceComponent::Helper::HasTurboShieldComponent')
def HasTurboShieldComponent(typeID):
    return TypeHasComponent(typeID, componentConst.TURBO_SHIELD_CLASS)


@TimedFunction('SpaceComponent::Helper::HasShipGroupComponent')
def HasShipGroupComponent(typeID):
    return TypeHasComponent(typeID, componentConst.SHIP_GROUP_CLASS)


@TimedFunction('SpaceComponent::Helper::IsActiveComponent')
def IsActiveComponent(componentRegistry, typeID, itemID):
    if HasActivateComponent(typeID):
        activateComponent = componentRegistry.GetComponentForItem(itemID, componentConst.ACTIVATE_CLASS)
        return activateComponent.IsActive()
    return True


@TimedFunction('SpaceComponent::Helper::IsReinforcedComponent')
def IsReinforcedComponent(componentRegistry, typeID, itemID):
    if HasReinforceComponent(typeID):
        reinforceComponent = componentRegistry.GetComponentForItem(itemID, componentConst.REINFORCE_CLASS)
        return reinforceComponent.IsReinforced()
    return False


@TimedFunction('SpaceComponent::Helper::HasWarpDisruptionComponent')
def HasWarpDisruptionComponent(typeID):
    return TypeHasComponent(typeID, componentConst.WARP_DISRUPTION_CLASS)


@TimedFunction('SpaceComponent::Helper::HasBehaviorComponent')
def HasBehaviorComponent(typeID):
    return TypeHasComponent(typeID, componentConst.BEHAVIOR)


@TimedFunction('SpaceComponent::Helper::HasNpcPilotComponent')
def HasNpcPilotComponent(typeID):
    return TypeHasComponent(typeID, componentConst.NPC_PILOT)


@TimedFunction('SpaceComponent::Helper::HasTargetingComponent')
def HasTargetingComponent(typeID):
    return TypeHasComponent(typeID, componentConst.TARGETING)


def GetTypesWithBehaviorComponent():
    return cfg.spaceComponentStaticData.GetTypeIDsForComponentName(componentConst.BEHAVIOR)


@TimedFunction('SpaceComponent::Helper::GetReinforcedComponent')
def GetReinforcedComponent(componentRegistry, typeID, itemID):
    if HasReinforceComponent(typeID):
        return componentRegistry.GetComponentForItem(itemID, componentConst.REINFORCE_CLASS)
    elif HasTurboShieldComponent(typeID):
        return componentRegistry.GetComponentForItem(itemID, componentConst.TURBO_SHIELD_CLASS)
    else:
        return None


@TimedFunction('SpaceComponent::Helper::HasDisruptableStationServiceComponent')
def HasDisruptableStationServiceComponent(typeID):
    return TypeHasComponent(typeID, componentConst.DISRUPTABLE_STATION_SERVICE)


@TimedFunction('SpaceComponent::Helper::HasEntosisCommandNodeComponent')
def HasEntosisCommandNodeComponent(typeID):
    return TypeHasComponent(typeID, componentConst.ENTOSIS_COMMAND_NODE)


@TimedFunction('SpaceComponent::Helper::HasEntosisLootTargetComponent')
def HasEntosisLootTargetComponent(typeID):
    return TypeHasComponent(typeID, componentConst.ENTOSIS_LOOT_TARGET)


@TimedFunction('SpaceComponent::Helper::HasEntosisSovereigntyStructureComponent')
def HasEntosisSovereigntyStructureComponent(typeID):
    return TypeHasComponent(typeID, componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE)


@TimedFunction('SpaceComponent::Helper::HasConquerableStationComponent')
def HasConquerableStationComponent(typeID):
    return TypeHasComponent(typeID, componentConst.CONQUERABLE_STATION)


def GetEntosisTargetComponentClasses(typeID):
    componentClasses = []
    if HasEntosisCommandNodeComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_COMMAND_NODE)
    if HasEntosisLootTargetComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_LOOT_TARGET)
    if HasDisruptableStationServiceComponent(typeID):
        componentClasses.append(componentConst.DISRUPTABLE_STATION_SERVICE)
    if HasEntosisSovereigntyStructureComponent(typeID):
        componentClasses.append(componentConst.ENTOSIS_SOVEREIGNTY_STRUCTURE)
    if HasConquerableStationComponent(typeID):
        componentClasses.append(componentConst.CONQUERABLE_STATION)
    return componentClasses


@TimedFunction('SpaceComponent::Helper::HasNpcWarpBeacon')
def HasNpcWarpBeacon(typeID):
    return TypeHasComponent(typeID, componentConst.NPC_WARP_BEACON)


@TimedFunction('SpaceComponent::Helper::HasItemTrader')
def HasItemTrader(typeID):
    return TypeHasComponent(typeID, componentConst.ITEM_TRADER)


@TimedFunction('SpaceComponent::Helper::HasJumpPolarizationComponent')
def HasJumpPolarizationComponent(typeID):
    return TypeHasComponent(typeID, componentConst.JUMP_POLARIZATION_CLASS)
