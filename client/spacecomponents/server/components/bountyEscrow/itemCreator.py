#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\itemCreator.py
import inventorycommon.const as invconst
from spacecomponents.common.components.bountyEscrow import TagCalculator

class ItemCreator(object):

    def __init__(self, inventory2, ballpark, iskValueByTypeID):
        self.inventory2 = inventory2
        self.listeners = []
        self.tagCalculator = TagCalculator(iskValueByTypeID)
        self.ballpark = ballpark

    def CreateContainer(self, charID, essID):
        essBall = self.ballpark.GetBall(essID)
        containerID = self.inventory2.MapInsertCargoContainer(invconst.typeCargoContainer, charID, self.ballpark.solarsystemID, essBall.x + 500, essBall.y, essBall.z).itemID
        return containerID

    def CreateItems(self, charID, essID, paymentDict):
        containerID = self.CreateContainer(charID, essID)
        itemDict = {}
        items = self.GetIskAsTags(paymentDict)
        for typeID, qty in items.iteritems():
            self.inventory2.AddItem2(typeID, charID, containerID, qty, invconst.flagCargo)
            itemDict[typeID] = qty

        for listener in self.listeners:
            listener(charID, itemDict, paymentDict)

    def GetIskAsTags(self, paymentDict):
        return self.tagCalculator.GetIskAsTags(sum(paymentDict.itervalues()))

    def RegisterForItemCreationEvents(self, func):
        self.listeners.append(func)
