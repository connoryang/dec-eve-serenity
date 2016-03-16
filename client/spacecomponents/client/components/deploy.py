#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\components\deploy.py
from inventorycommon.const import groupControlTower, groupStation, groupStargate, groupWormhole
from carbon.common.script.util.format import FmtDist
from spacecomponents.client.display import EntryData, RANGE_ICON, BANNED_ICON
from spacecomponents.common.components.component import Component
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.util.eveMisc import LaunchFromShip
import evetypes

class Deploy(Component):

    @staticmethod
    def GetAttributeInfo(godmaService, typeID, attributes, instance, localization):
        attributeEntries = [EntryData('Header', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/InfoAttributesHeader')),
         EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DeployAtRange'), FmtDist(attributes.deployAtRange), iconID=RANGE_ICON),
         EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromOwnGroup', groupName=evetypes.GetGroupName(typeID)), FmtDist(attributes.minDistanceFromOwnGroup), iconID=RANGE_ICON),
         EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromControlTower', groupName=evetypes.GetGroupNameByGroup(groupControlTower)), FmtDist(attributes.minDistanceFromControlTower), iconID=RANGE_ICON)]
        if hasattr(attributes, 'maxDistanceFromControlTower'):
            attributeEntries.append(EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MaxDistanceFromControlTower', groupName=evetypes.GetGroupNameByGroup(groupControlTower)), FmtDist(attributes.maxDistanceFromControlTower), iconID=RANGE_ICON))
        if hasattr(attributes, 'minDistanceFromStargatesAndStations'):
            attributeEntries.append(EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromStargatesAndStations', stargateGroupName=evetypes.GetGroupNameByGroup(groupStargate), stationGroupName=evetypes.GetGroupNameByGroup(groupStation)), FmtDist(attributes.minDistanceFromStargatesAndStations), iconID=RANGE_ICON))
        if hasattr(attributes, 'minDistanceFromWormhole'):
            attributeEntries.append(EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/MinDistanceFromWormhole', wormholeGroupName=evetypes.GetGroupNameByGroup(groupWormhole)), FmtDist(attributes.minDistanceFromStargatesAndStations), iconID=RANGE_ICON))
        if getattr(attributes, 'disallowInWormholeSpace', True):
            attributeEntries.append(EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Deploy/DisallowedFromWormholeSpace'), '', iconID=BANNED_ICON))
        return attributeEntries


def DeployAction(invItems):
    LaunchFromShip(invItems, session.charid, maxQty=1)


def GetDeployMenu(invItem):
    itemIsInMyShip = invItem.locationID == session.shipid
    if itemIsInMyShip:
        return [[MenuLabel('UI/Inventory/ItemActions/LaunchForSelf'), DeployAction, [invItem]]]
    else:
        return []
