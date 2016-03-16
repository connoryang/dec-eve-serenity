#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\itemtrader.py
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentregistry import ExportCall
import evetypes

class ItemTrader(Component):

    def __init__(self, itemTraderItemId, typeId, attributes, componentRegistry):
        Component.__init__(self, itemTraderItemId, typeId, attributes, componentRegistry)
        self.SubscribeToMessage('OnAddedToSpace', self.OnAddedToSpace)

    def OnAddedToSpace(self, ballpark, spaceComponentDb):
        self.tradeProcessor = TradeProcessor(ballpark, ballpark.inventory2, ballpark.inventoryMgr, self.itemID, self.attributes.inputItems, self.attributes.outputItems, self.attributes.interactionRange)

    @ExportCall
    def ProcessTrade(self, session):
        return self.tradeProcessor.ProcessTrade(session.shipid, session.charid)


class TradeProcessor(object):

    def __init__(self, ballpark, inventory2, inventoryMgr, itemTraderItemId, inputItems, outputItems, interactionRange):
        self.ballpark = ballpark
        self.inventory2 = inventory2
        self.inventoryMgr = inventoryMgr
        self.itemTraderItemId = itemTraderItemId
        self.inputItems = inputItems
        self.outputItems = outputItems
        self.interactionRange = interactionRange
        self.requiredCapacity = self.GetCapacityForItems(outputItems) - self.GetCapacityForItems(inputItems)

    def ProcessTrade(self, shipId, ownerId):
        with self.inventory2.LockedItemAndSubItems(shipId):
            self.CheckDistance(shipId)
            ship = self.inventoryMgr.GetInventoryFromIdEx(shipId, -1)
            self.CheckCargoCapacity(ship)
            cargoItems = ship.List(const.flagCargo)
            itemsForRemoval = self._GetItemsForTrade(cargoItems)
            if itemsForRemoval:
                self._TakeItems(shipId, itemsForRemoval)
                self._GiveItems(shipId, ownerId)
                return True
            return False

    def _GetItemsForTrade(self, cargoItems):
        itemsForTrade = {}
        for requiredTypeId, requiredQuantity in self.inputItems.iteritems():
            quantityLeft = self._GetItemsForTradeFromCargo(cargoItems, itemsForTrade, requiredTypeId, requiredQuantity)
            if quantityLeft != 0:
                return {}

        return itemsForTrade

    def _GetItemsForTradeFromCargo(self, cargoItems, itemsForTrade, requiredTypeId, requiredQuantity):
        quantityLeft = requiredQuantity
        for item in cargoItems:
            if item.typeID == requiredTypeId:
                quantity = min(quantityLeft, item.quantity)
                itemsForTrade[item.itemID] = quantity
                quantityLeft -= quantity
            if quantityLeft == 0:
                break

        return quantityLeft

    def _TakeItems(self, shipId, itemsForRemoval):
        for itemId, quantityForRemoval in itemsForRemoval.iteritems():
            self.inventory2.MoveItem(itemId, shipId, const.locationJunkyard, qty=quantityForRemoval)

    def _GiveItems(self, shipId, ownerId):
        for typeId, quantityForAdd in self.outputItems.iteritems():
            self.inventory2.AddItem2(typeId, ownerId, shipId, qty=quantityForAdd, flag=const.flagCargo)

    def GetCapacityForItems(self, items):
        capacity = 0
        for typeId, quantity in items.iteritems():
            typeVolume = evetypes.GetVolume(typeId)
            capacity += quantity * typeVolume

        return capacity

    def CheckCargoCapacity(self, ship):
        shipCapacity = ship.GetCapacity(flag=const.flagCargo)
        availableCapacity = shipCapacity.capacity - shipCapacity.used
        if availableCapacity < self.requiredCapacity:
            raise UserError('NotEnoughCargoSpace', {'available': shipCapacity.capacity - shipCapacity.used,
             'volume': self.requiredCapacity})

    def CheckDistance(self, shipId):
        actualDistance = self.ballpark.GetSurfaceDist(self.itemTraderItemId, shipId)
        if actualDistance > self.interactionRange:
            typeName = evetypes.GetName(self.inventory2.GetItem(self.itemTraderItemId).typeID)
            raise UserError('TargetNotWithinRange', {'targetGroupName': typeName,
             'desiredRange': self.interactionRange,
             'actualDistance': actualDistance})
