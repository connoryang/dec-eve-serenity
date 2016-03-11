#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\autoLooter.py
from eve.common.lib.appConst import maxCargoContainerTransferDistance
from inventorycommon.const import typeCargoContainer, groupWreck, flagCargo
from inventorycommon.util import GetItemVolume
from spacecomponents.common.componentConst import AUTO_LOOTER_CLASS
from spacecomponents.common.components.component import Component
from spacecomponents.common.helper import IsActiveComponent
import logging
from spacecomponents.server.messages import MSG_ON_BALLPARK_RELEASE
from ccpProfile import TimedFunction
logger = logging.getLogger(__name__)
MIN_CARGO_THRESHOLD = 0.0001

class AutoLooter(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        logger.debug('Looter component created for item %s of type %s', itemID, typeID)
        self.lootRange = getattr(self.attributes, 'range', maxCargoContainerTransferDistance)
        self.isThreadActive = False
        self.ballpark = None
        self.componentRegistry.SubscribeToItemMessage(itemID, 'OnAddedToSpace', self.OnAddedToSpace)
        self.componentRegistry.SubscribeToItemMessage(itemID, 'OnRemovedFromSpace', self.OnRemovedFromSpace)
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_BALLPARK_RELEASE, self.OnBallparkRelease)
        self.SetIntervalInSeconds(self.attributes.cycleTimeSeconds)

    def SetBallpark(self, ballpark):
        self.ballpark = ballpark
        self.inventory2 = self.ballpark.inventory2
        self.inventoryMgr = self.ballpark.inventoryMgr

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        self.SetBallpark(ballpark)
        self.ownerID = ballpark.slims[self.itemID].ownerID
        self.UThreadNew(self.ThreadWorker)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        self.StopWorkerThread()

    def OnBallparkRelease(self):
        self.StopWorkerThread()

    def StopWorkerThread(self):
        logger.debug('%s worker thread is stopping', self.itemID)
        self.isThreadActive = False

    @TimedFunction('SpaceComponent::AutoLooter::DoUnitOfWork')
    def DoUnitOfWork(self):
        if not IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            return
        if self.IfLooterIsFull():
            logger.debug('%s cargo is full', self.itemID)
            return
        targetID = self.FindValidTarget()
        if targetID is not None:
            self.LootTarget(targetID)

    def ThreadWorker(self):
        if self.IsWorkerThreadActive():
            return
        self.isThreadActive = True
        logger.debug('%s starting worker thread', self.itemID)
        self.SleepSim(self.intervalMS)
        try:
            self.localInventory = self.GetInventoryForTarget(self.itemID)
            while self.IsWorkerThreadActive():
                self.DoUnitOfWork()
                self.SleepSim(self.intervalMS)

        finally:
            self.StopWorkerThread()

    @TimedFunction('SpaceComponent::AutoLooter::FindValidTarget')
    def FindValidTarget(self):
        ballIDsInRange = self.ballpark.GetBallIdsAndDistInRange(self.itemID, self.lootRange)
        if len(ballIDsInRange) == 0:
            return None
        ballIDsInRange.sort()
        capacityLeft = self.GetCapacityLeft()
        for distanceSq, ballID in ballIDsInRange:
            if ballID < 0:
                continue
            slimItem = self.ballpark.slims[ballID]
            if self.IsTargetValid(slimItem, capacityLeft):
                logger.debug('%s searched for a valid target and found %s', self.itemID, ballID)
                return ballID

    @TimedFunction('SpaceComponent::AutoLooter::IsTargetValid')
    def IsTargetValid(self, slimItem, capacityLeft):
        if not (slimItem.typeID == typeCargoContainer or slimItem.groupID == groupWreck):
            return False
        if getattr(slimItem, 'isEmpty', False):
            return False
        if not self.ballpark.lootRights.HaveLootRight(slimItem.itemID, self.ownerID):
            return False
        if not self.TargetHasCargoWeCanTake(slimItem.itemID, capacityLeft):
            return False
        return True

    @TimedFunction('SpaceComponent::AutoLooter::GetCapacityLeft')
    def GetCapacityLeft(self):
        looterCapacity = self.localInventory.GetCapacity()
        return looterCapacity.capacity - looterCapacity.used

    @TimedFunction('SpaceComponent::AutoLooter::GetInventoryForTarget')
    def GetInventoryForTarget(self, targetID):
        return self.inventoryMgr.GetInventoryFromIdEx(targetID, -1)

    def IfLooterIsFull(self):
        capacityLeft = self.GetCapacityLeft()
        return capacityLeft < MIN_CARGO_THRESHOLD

    @TimedFunction('SpaceComponent::AutoLooter::TargetHasCargoWeCanTake')
    def TargetHasCargoWeCanTake(self, itemID, capacityLeft):
        targetCargo = self.GetInventoryForTarget(itemID)
        targetCapacity = targetCargo.GetCapacity()
        canTake = False
        if targetCapacity.used < MIN_CARGO_THRESHOLD and len(targetCargo.List()) == 0:
            pass
        elif targetCapacity.used < capacityLeft:
            canTake = True
        else:
            for item in targetCargo.List():
                if GetItemVolume(item) <= capacityLeft and self.IsLegalInventoryMove(item):
                    canTake = True
                    break

        return canTake

    def IsWorkerThreadActive(self):
        return self.isThreadActive

    def SetIntervalInSeconds(self, interval):
        self.intervalMS = max(1, interval) * 1000

    def IsLegalInventoryMove(self, item):
        return self.inventory2.IsLegalInventoryMove(item, self.itemID)

    @TimedFunction('SpaceComponent::AutoLooter::LootTarget')
    def LootTarget(self, targetID):
        targetCargo = self.GetInventoryForTarget(targetID)
        capacityLeft = self.GetCapacityLeft()
        itemVolumesAndIds = [ (GetItemVolume(item), item.itemID) for item in targetCargo.List() if self.IsLegalInventoryMove(item) ]
        itemVolumesAndIds.sort()
        itemIDsToTake = []
        for volume, itemID in itemVolumesAndIds:
            if capacityLeft < volume:
                break
            capacityLeft -= volume
            itemIDsToTake.append(itemID)

        with self.inventory2.LockedItems(itemIDsToTake):
            self.inventory2.MoveManyItems(itemIDsToTake, targetID, self.itemID, flagCargo, self.ownerID)
            logger.debug('%s looted items %s from %s', self.itemID, itemIDsToTake, targetID)

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, AUTO_LOOTER_CLASS)
        attributeStrings = []
        attributeStrings.append('Cycle time: %d seconds' % attributes.cycleTimeSeconds)
        if hasattr(attributes, 'range'):
            attributeStrings.append('Loot range: %d m' % attributes.range)
        infoString = '<br>'.join(attributeStrings)
        return infoString
