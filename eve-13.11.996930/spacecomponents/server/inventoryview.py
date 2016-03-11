#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\inventoryview.py
import logging
from eve.common.lib.appConst import locationJunkyard
from eve.server.script.mgt.inv.ball import Ball
from carbon.common.script.sys.row import Row
from eveexceptions import UserError
from eveexceptions.exceptionEater import ExceptionEater
import evetypes
from inventorycommon import const
from inventorycommon.util import GetItemVolume
from spacecomponents.server.components.decay import MSG_ON_PLAYER_INTERACTION
logger = logging.getLogger(__name__)

class InventoryView(Ball):

    def __init__(self, broker, component, actor):
        Ball.__init__(self, broker, component.itemID, actor)
        self.componentRegistry = component.componentRegistry
        self.component = component
        self.flagID = const.flagCargo

    def ClassSpecificAdd(self, itemID, sourceID, qty = None, flag = None):
        item = self.GetItemByID(itemID)
        oldOwnerID = item.ownerID
        containerOwner = self.invItem.ownerID
        try:
            self.broker.CanTake(item, self.actor)
        except UserError as e:
            if e.msg == 'SCGeneralPasswordRequired':
                raise UserError('PasswordProtectedCacheInvalid')
            raise

        self.CheckVolumeRestrictions(item, qty or item.stacksize)
        self.CheckCloakingLimitations(sourceID)
        self.component.CheckCanAddItem(self.actor, item, self.broker.inventory2)
        if self.broker.beyonce.GetBallpark(self.broker.locationID).HasBall(sourceID):
            sourceBallID = sourceID
        else:
            sourceBallID = self.GetItemByID(sourceID).locationID
        self.CheckAccessDistance(sourceBallID)
        flag = self.flagID
        locationID = self.component.GetInventoryID()
        newItemID = self.broker.inventory2.MoveItem(itemID, sourceID, locationID, qty, containerOwner, flag)
        self.LogInventoryMovement(item, locationID, oldOwnerID, qty, sourceID)
        self.componentRegistry.SendMessageToItem(self.itemid, MSG_ON_PLAYER_INTERACTION)
        return newItemID

    def List(self, flag = None):
        self.component.CheckCanListContents(self.actor, self.broker.inventory2)
        if self.actor != -1:
            actorItem = self.GetItemByID(self.actor)
            self.CheckAccessDistance(actorItem.locationID)
        if flag != self.flagID:
            logger.error('Trying to list a InventoryView %d with flag %s', self.itemid, flag)
        self.componentRegistry.SendMessageToItem(self.itemid, MSG_ON_PLAYER_INTERACTION)
        return self.broker.inventory2.SelectItems(self.itemid, flag=self.flagID)

    def QueryTake(self, item, charID):
        if charID != -1:
            charItem = self.GetItemByID(charID)
            self.CheckAccessDistance(charItem.locationID)
        self.component.CheckCanTakeItem(charID, item, self.broker.inventory2)
        self.componentRegistry.SendMessageToItem(self.itemid, MSG_ON_PLAYER_INTERACTION)

    def GetCapacity(self, flag = None, capacityItemID = None, skipDistanceCheck = False):
        capacity = 0.0
        used = 0.0
        if self.broker is not None:
            try:
                contents = self.broker.inventory2.SelectItems(self.itemid, flag=self.flagID)
            except UserError:
                contents = []

            capacity = evetypes.GetCapacity(self.invItem.typeID)
            used = 0.0
            for item in contents:
                vol = GetItemVolume(item)
                if vol > 0:
                    used = used + vol

        return Row(['capacity', 'used'], [capacity, used])

    def CheckAccessDistance(self, otherBallId):
        ballpark = self.broker.beyonce.GetBallpark(self.broker.locationID)
        self.component.CheckAccessDistance(otherBallId, ballpark)

    def LogInventoryMovement(self, item, locationID, oldOwnerID, qty, sourceID):
        containerOwner = self.invItem.ownerID
        solarSystemID = self.invItem.locationID
        if locationID == locationJunkyard:
            with ExceptionEater('eventLog'):
                sm.GetService('eventLog').LogOwnerEvent('spacecomponent::cargobay_JunkingItem', containerOwner, solarSystemID, self.component.itemID, sourceID, oldOwnerID, item.itemID, item.typeID, qty)
                sm.GetService('eventLog').LogOwnerEventJson('spacecomponent::cargobay_JunkingItem', containerOwner, solarSystemID, locationID=self.component.itemID, sourceID=sourceID, oldOwnerID=oldOwnerID, itemID=item.itemID, typeID=item.typeID, quantity=qty)
        else:
            self.LogMoveItem(sourceID, locationID, oldOwnerID, containerOwner, self.invItem.groupID, item=item, qty=qty)
