#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\components\itemtrader.py
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentConst import ITEM_TRADER
from carbonui.control.menuLabel import MenuLabel
from eve.client.script.ui.inflight.itemtraderwindow import ItemTraderWindow
import evetypes

class ItemTrader(Component):

    def RequestTrade(self):
        sm.GetService('menu').GetCloseAndTryCommand(self.itemID, self.InitiateTrade, (), interactionRange=self.attributes.interactionRange)

    def InitiateTrade(self):
        shipInventory = sm.GetService('invCache').GetInventoryFromId(session.shipid)
        cargoChecker = CargoChecker(shipInventory, self.attributes.inputItems, self.attributes.outputItems)
        ItemTraderWindow.CloseIfOpen()
        ItemTraderWindow(itemTrader=self, shipId=session.shipid, cargoChecker=cargoChecker)

    def ProcessTrade(self):
        return self.CallServerComponent('ProcessTrade')

    def CallServerComponent(self, methodName):
        remoteBallpark = sm.GetService('michelle').GetRemotePark()
        return remoteBallpark.CallComponentFromClient(self.itemID, ITEM_TRADER, methodName)

    def GetInputItems(self):
        return self.attributes.inputItems

    def GetOutputItems(self):
        return self.attributes.outputItems


class CargoChecker(object):

    def __init__(self, shipInventory, inputItems, outputItems):
        self.shipInventory = shipInventory
        self.inputItems = inputItems
        self.outputItems = outputItems
        self.requiredCapacity = self.GetCapacityForItems(outputItems) - self.GetCapacityForItems(inputItems)

    def GetCapacityForItems(self, items):
        capacity = 0
        for typeId, quantity in items.iteritems():
            typeVolume = evetypes.GetVolume(typeId)
            capacity += quantity * typeVolume

        return capacity

    def IsRequiredCargoSpaceAvailable(self):
        if self.requiredCapacity <= 0:
            return True
        shipCapacity = self.shipInventory.GetCapacity(const.flagCargo)
        availableCapacity = shipCapacity.capacity - shipCapacity.used
        return availableCapacity > self.requiredCapacity

    def AreRequiredItemsPresent(self):
        cargoItems = self.shipInventory.List(const.flagCargo)
        for requiredTypeId, requiredQuantity in self.inputItems.iteritems():
            if not self.IsTypeAndQuantityInCargo(requiredTypeId, requiredQuantity, cargoItems):
                return False

        return True

    def IsTypeAndQuantityInCargo(self, requiredTypeId, requiredQuantity, cargoItems):
        quantityInCargo = 0
        for item in cargoItems:
            if item.typeID == requiredTypeId:
                quantityInCargo += item.quantity
            if quantityInCargo >= requiredQuantity:
                return True

        return False


def GetMenu(ballpark, itemTraderItemId):
    itemTrader = ballpark.componentRegistry.GetComponentForItem(itemTraderItemId, ITEM_TRADER)
    menu = [[MenuLabel('UI/Inflight/SpaceComponents/ItemTrader/Access'), itemTrader.RequestTrade]]
    return menu
