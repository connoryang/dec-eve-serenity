#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\siphon.py
from collections import defaultdict
import dogma.const
from spacecomponents.common.components.component import Component
import inventorycommon.const
from starbase.eventLogger import EventLogger
from starbase.inventoryAccess import InventoryAccess
from starbase.siphonSourcePicker import PickStructureToSiphon
from ccpProfile import TimedFunction
import evetypes

class Siphon(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        self.harvesterSiphonQuantity = (attributes.rawMaterialQuantity, attributes.isRawPercentage)
        self.reactionSiphonQuantity = (attributes.proMaterialQuantity, attributes.isProPercentage)
        self.polySiphonQuantity = (attributes.polyMaterialQuantity, attributes.isPolyPercentage)
        self.attributes = attributes
        self.componentRegistry = componentRegistry
        self.itemID = itemID
        self.typeID = typeID
        self.siphoningFrom = None
        self.destinationSilo = None
        self.cachedStorageQuantities = defaultdict(long)
        self.SubscribeToMessage('OnAddedToSpace', self.OnAddedToSpace)
        self.SubscribeToMessage('OnRemovedFromSpace', self.OnRemovedFromSpace)

    def GetTypeBatchSize(self, typeID):
        return self.ballpark.broker.dogmaIM.GetTypeAttribute2(typeID, dogma.const.attributeMoonMiningAmount)

    def GetEventLogger(self):
        return self.eventLogger

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.ballpark = ballpark
        towerID = self.ballpark.RegisterSiphon(self.itemID)
        if towerID is None:
            return
        tower = self.ballpark.GetBall(towerID)
        GetTypeAttribute = self.ballpark.broker.dogmaIM.GetTypeAttribute2
        siphonWasteAmount = GetTypeAttribute(self.typeID, dogma.const.attributeSiphonWasteAmount)
        self.eventLogger = EventLogger(self.itemID, self.ballpark.inventory2, self.ballpark.broker.eventLog, tower)
        self.inventoryAccess = InventoryAccess(self.ballpark.inventory2, self.ballpark.broker.dbpos, self.eventLogger, siphonWasteAmount)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        ballpark.RemoveSiphon(self.itemID)

    @TimedFunction('SpaceComponent::Siphon::EvaluateCycle')
    def EvaluateCycle(self, active):
        capacity = self.ballpark.inventoryMgr.GetInventoryFromIdEx(self.itemID, -1).GetCapacity()
        capacity = capacity.capacity - capacity.used
        supplier = self.ballpark.GetBall(self.siphoningFrom)
        if supplier is None:
            return
        supplyType, supplyAmount = supplier.GetSupplyInfo()[0]
        batchSize = self.GetTypeBatchSize(supplyType)
        supplyAmount = supplyAmount * batchSize
        demand = self.GetSiphonAmount(supplyType, capacity, supplyAmount)
        if not demand:
            return
        supplier.SiphonResources(supplyType, demand / float(batchSize))
        self.cachedStorageQuantities[supplyType] += demand

    def GetSiphonedItems(self):
        return self.cachedStorageQuantities

    @TimedFunction('SpaceComponent::Siphon::GetSiphonAmount')
    def GetSiphonAmount(self, typeID, capacity, supplyAmount):
        demand, isPercentage = self.GetDemand(typeID)
        if isPercentage:
            demand = supplyAmount * demand / 100.0
        roomLeft = max(self.GetRoomLeft(capacity, typeID), 0)
        return min(roomLeft, demand, supplyAmount)

    @TimedFunction('SpaceComponent::Siphon::GetRoomLeft')
    def GetRoomLeft(self, capacity, typeID):
        roomTaken = 0
        for typeID, qty in self.cachedStorageQuantities.iteritems():
            roomTaken += qty * evetypes.GetVolume(typeID)

        return (capacity - roomTaken) / evetypes.GetVolume(typeID)

    def GetDemand(self, typeID):
        if evetypes.GetGroupID(typeID) == inventorycommon.const.groupMoonMaterials:
            return self.harvesterSiphonQuantity
        elif evetypes.GetGroupID(typeID) == inventorycommon.const.groupHybridPolymers:
            return self.polySiphonQuantity
        else:
            return self.reactionSiphonQuantity
        return (0, False)

    @TimedFunction('SpaceComponent::Siphon::Siphon')
    def Siphon(self, links):
        siloID, productionStructureID = PickStructureToSiphon(links, self.ballpark, self.attributes.materials, self.attributes.materialGroupPriority, self.eventLogger)
        if productionStructureID is None:
            return
        self.SetSiphonSource(siloID, productionStructureID)
        self.EvaluateCycle(True)

    def SetSiphonSource(self, silo, siphonFrom):
        self.destinationSilo = silo
        self.siphoningFrom = siphonFrom

    def ApplyState(self):
        items = self.GetSiphonedItems()
        if items:
            self.inventoryAccess.CreateItems(self.itemID, items, self.destinationSilo)
        self.cachedStorageQuantities.clear()
