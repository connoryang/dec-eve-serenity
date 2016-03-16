#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\cargobay.py
import logging
from eve.common.lib.appConst import locationJunkyard
from eveexceptions import UserError
from eveexceptions.const import UE_TYPEID
import inventorycommon.const as invConst
from spacecomponents.common.componentConst import CARGO_BAY
import random
from spacecomponents.common.components.component import Component
from spacecomponents.common.helper import IsActiveComponent
logger = logging.getLogger(__name__)

class CargoBay(Component):

    def __init__(self, cargoBayItemID, typeID, attributes, componentRegistry):
        Component.__init__(self, cargoBayItemID, typeID, attributes, componentRegistry)
        self.componentRegistry.SubscribeToItemMessage(self.itemID, 'OnRemovedFromSpace', self.OnRemovedFromSpace)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        isExploding = ballpark.IsExploding(self.itemID)
        self.DropLoot(ballpark, isExploding)

    def DropLoot(self, ballpark, isExploding):
        logger.debug('PersonalCargoBay.DropLoot %d isExploding:%s', self.itemID, isExploding)
        droppedItemIDs = []
        killmailItems = []
        for item in ballpark.inventory2.SelectItems(self.itemID):
            destroyed = False
            if isExploding:
                destroyed = random.random() > 0.5
                killmailItems.append((item.typeID,
                 item.singleton,
                 item.stacksize,
                 item.flagID,
                 destroyed))
            if not destroyed:
                droppedItemIDs.append(item.itemID)

        if len(droppedItemIDs) or len(killmailItems):
            shipMgr = ballpark.broker.ship.GetShipAccessEx(ballpark.solarsystemID, invConst.groupSolarSystem)
            shipMgr.JettisonEx(-1, self.itemID, itemIds=droppedItemIDs, isExploding=isExploding, killmailItems=killmailItems, forceShips=True)

    def CheckCanListContents(self, charID, inventory2):
        if not IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            raise UserError('PermissionDenied')
        if not self.attributes.allowFreeForAll and charID not in (-1, inventory2.GetItem(self.itemID).ownerID):
            raise UserError('PermissionDenied')

    def CheckCanAddItem(self, charID, item, inventory2):
        if not IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            raise UserError('PermissionDenied')
        if charID not in (-1, inventory2.GetItem(self.itemID).ownerID) and not self.attributes.allowFreeForAll:
            raise UserError('PermissionDenied')
        if charID != -1 and not self.attributes.allowUserAdd:
            raise UserError('CannotAddToThatLocation')
        if hasattr(self.attributes, 'acceptedTypeIDs') and item.typeID not in self.attributes.acceptedTypeIDs:
            raise UserError('CannotStoreDestinationRestricted', {'ship': self.typeID})

    def CheckCanTakeItem(self, charID, item, inventory2):
        if not IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            raise UserError('PermissionDenied')
        if not self.attributes.allowFreeForAll and charID not in (-1, item.ownerID):
            raise UserError('TheItemIsNotYoursToTake', {'item': item.itemID})

    def CheckAccessDistance(self, ballID, ballpark):
        if not IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            raise UserError('PermissionDenied')
        if not ballpark.HasBall(self.itemID):
            raise UserError('CargoContainerNotFound', {'item': (UE_TYPEID, self.typeID)})
        dist = ballpark.DistanceBetween(self.itemID, ballID)
        accessRange = self.attributes.accessRange
        if dist > accessRange:
            raise UserError('NotCloseEnoughToAdd', {'maxdist': accessRange})

    def GetInventoryID(self):
        if self.attributes.destroyAllDeposits:
            return locationJunkyard
        else:
            return self.itemID

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, CARGO_BAY)
        attributeStrings = []
        attributeStrings.append('Allow inventory add: %s' % attributes.allowUserAdd)
        attributeStrings.append('Allow free-for-all: %s' % attributes.allowFreeForAll)
        attributeStrings.append('Access range: %d m' % attributes.accessRange)
        attributeStrings.append('Destroy all deposits: %s' % attributes.destroyAllDeposits)
        attributeStrings.append('Accepted types: %s' % (attributes.acceptedTypeIDs.keys() if hasattr(attributes, 'acceptedTypeIDs') else 'all'))
        infoString = '<br>'.join(attributeStrings)
        return infoString
