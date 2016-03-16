#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\dogmatic.py
import logging
from carbon.common.lib import const
from carbon.common.lib.const import minFakeItem
from dogma.const import attributeShieldCharge, attributeShieldCapacity
from eveexceptions.exceptionEater import ExceptionEater
from eve.common.script.mgt.appLogConst import eventSpaceComponentExploding
from spacecomponents.common.components.component import Component
from spacecomponents.server.messages import MSG_ON_BALLPARK_RELEASE, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
PERSIST_INTERVAL_MSEC = 60 * const.MIN / const.MSEC
logger = logging.getLogger(__name__)

class Dogmatic(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(Dogmatic, self).__init__(itemID, typeID, attributes, componentRegistry)
        componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        componentRegistry.SubscribeToItemMessage(self.itemID, MSG_ON_BALLPARK_RELEASE, self.OnBallparkRelease)
        self.keepPersisting = False

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        ballpark.dogmaLM.LoadItem(self.itemID)
        if self.attributes.isPersisted and self.itemID < minFakeItem:
            self.keepPersisting = True
            self.UThreadNew(self.PersistThread, ballpark.dogmaLM)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        if not self.attributes.isPersisted:
            return
        self.keepPersisting = False
        isExploding = ballpark.IsExploding(self.itemID)
        if not isExploding:
            self.PersistNow(ballpark.dogmaLM)

    def OnBallparkRelease(self):
        self.keepPersisting = False

    def PersistThread(self, dogmaLocation):
        self.SleepWallclock(PERSIST_INTERVAL_MSEC)
        while self.keepPersisting:
            with ExceptionEater('Dogmatic.PersistThread'):
                self.PersistNow(dogmaLocation)
            self.SleepWallclock(PERSIST_INTERVAL_MSEC)

    def PersistNow(self, dogmaLocation):
        if not dogmaLocation.IsItemLoaded(self.itemID):
            logger.debug("Dogmatic.PersistNow %s still running for unloaded item. Hopefully I'll be cleaned up soon!" % self.itemID)
            return
        shieldLevel = dogmaLocation.GetAttributeValue(self.itemID, attributeShieldCharge)
        shieldCapacity = dogmaLocation.GetAttributeValue(self.itemID, attributeShieldCapacity)
        logger.debug('Dogmatic.PersistNow %d (%f / %f)', self.itemID, shieldLevel, shieldCapacity)
        if shieldLevel / shieldCapacity < 0.95:
            dogmaLocation.MarkItemDirty(self.itemID)
        dogmaLocation.PersistItem(self.itemID)

    def OnExplode(self, ballpark):
        ballpark.dbLog.LogItemGenericEvent(None, eventSpaceComponentExploding, self.itemID, referenceID=ballpark.solarsystemID, int_1=self.typeID)
