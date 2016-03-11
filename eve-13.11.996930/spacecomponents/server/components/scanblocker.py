#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\scanblocker.py
import logging
from spacecomponents.common import helper
from spacecomponents.common.componentConst import SCAN_BLOCKER_CLASS
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_ACTIVE, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
logger = logging.getLogger(__name__)

class ScanBlocker(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.componentRegistry.SubscribeToItemMessage(itemID, MSG_ON_ACTIVE, self.OnActive)

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        if helper.IsActiveComponent(self.componentRegistry, self.typeID, self.itemID):
            logger.debug('Active ScanBlocker added to space %s %s', self.itemID, self.typeID)
            self.__RegisterScanBlocker(ballpark.scanMgr)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        logger.debug('ScanBlocker.OnRemovedFromSpace %s %s', self.itemID, self.typeID)
        ballpark.scanMgr.scanBlockRegistry.UnregisterScanBlockingBall(self.itemID)

    def OnActive(self, ballpark):
        logger.debug('ScanBlocker.OnActive %s %s', self.itemID, self.typeID)
        self.__RegisterScanBlocker(ballpark.scanMgr)

    def __RegisterScanBlocker(self, scanMgr):
        scanMgr.scanBlockRegistry.RegisterScanBlockingBall(self.itemID, self.attributes.range, self.attributes.blocksSelf, self.attributes.systemWideBlock)

    @staticmethod
    def GetEspTypeInfo(typeID, spaceComponentStaticData):
        attributes = spaceComponentStaticData.GetAttributes(typeID, SCAN_BLOCKER_CLASS)
        attributeStrings = []
        attributeStrings.append('Block range: %d m' % attributes.range)
        infoString = '<br>'.join(attributeStrings)
        return infoString
