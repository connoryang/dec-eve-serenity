#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\__init__.py
from spacecomponents.common.components.bountyEscrow import GetPriceByTagTypeID
from spacecomponents.common.components.component import Component
from eventLogger import EventLogger
from iskRegistry import IskRegistry
from itemCreator import ItemCreator
from iskMover import IskMover
from escrow import Escrow
from lock import Lock
from persister import Persister
from spacecomponents.server.components.bountyEscrow.notifier import RangeNotifier
from warpScrambler import WarpScrambler
from spacecomponents.common.componentregistry import ExportCall
from notifier import Notifier

class BountyEscrow(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.isPaying = False
        self.SubscribeToMessage('OnAddedToSpace', self.OnAddedToSpace)
        self.SubscribeToMessage('OnRemovedFromSpace', self.OnRemovedFromSpace)

    def Initialize(self, ballpark, escrow, lock, persister, eventLogger, notifier):
        self.ballpark = ballpark
        self.lock = lock
        self.lock.RegisterBallpark(ballpark)
        self.persister = persister
        self.escrow = escrow
        self.eventLogger = eventLogger
        self.eventLogger.RegisterForLogging(self.lock, self.escrow)
        self.notifier = notifier
        self.notifier.RegisterForNotifications(self.escrow)

    def OnAddedToSpace(self, ballpark, dbspacecomponent):
        persister = Persister(ballpark.solarsystemID, self.itemID, dbspacecomponent)
        bountyEscrowBonus, bounties = persister.GetStateForSystem()
        iskRegistry = IskRegistry(bounties)
        iskMover = IskMover(ballpark.broker.account)
        itemCreator = GetItemCreator(ballpark.inventory2, ballpark, self.attributes.tagTypeIDs.keys())
        escrow = Escrow(self, ballpark, iskRegistry, iskMover, itemCreator, persister)
        item = ballpark.inventory2.GetItem(self.itemID)
        eventLogger = EventLogger(ballpark.broker.eventLog, ballpark.solarsystemID, item.ownerID, self.itemID)
        notifier = Notifier(ballpark.broker.notificationMgr)
        self.rangeNotifier = RangeNotifier(ballpark.solarsystemID, ballpark, ballpark.broker.machoNet, self.GetWallclockTime)
        ballpark.proximityRegistry.RegisterForProximity(self.itemID, 30000, self.rangeNotifier.PlayerInRange)
        lock = Lock(self)
        self.warpScrambler = WarpScrambler(self.itemID, lock, ballpark.dogmaLM)
        self.Initialize(ballpark, escrow, lock, persister, eventLogger, notifier)
        self.escrow.SetBonus(bountyEscrowBonus)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        self.escrow.SetBonus(0.0)
        self.PersistEverything()

    def EscrowPartOfBounty(self, bountyAmount, charID):
        return self.escrow.EscrowPartOfBounty(bountyAmount, charID)

    def GetLPBounty(self, bountyAmount):
        return self.escrow.GetLPBounty(bountyAmount)

    def GetBounty(self):
        return self.escrow.GetBounty()

    def PlayerInRangeCallback(self, ballID, entered):
        if entered:
            charID = sm.GetService('beyonce').GetBallpark(self.ballpark.solarsystemID).slims[ballID].charID
            sm.GetService('machoNet').SinglecastBySolarSystemID(self.ballpark.solarsystemID, 'OnBountyEscrowPlayerInRange', charID)

    def SlashLock(self):
        return self.lock.SlashLock()

    def Lock(self):
        return self.lock.Lock()

    @ExportCall
    def Unlock(self, sess):
        self.lock.Unlock(sess.charid, sess.shipid)

    @ExportCall
    def GetBountyContributors(self, sess):
        return dict(self.escrow.GetIskContributors())

    @ExportCall
    def GetIskAsTags(self, sess):
        charID = sess.charid
        shipID = sess.shipid
        paymentFunc = lambda : self.escrow.CreateItems(charID, self.itemID)
        self._PayIsk(charID, shipID, self.attributes.tagSpawnDelay, paymentFunc)

    @ExportCall
    def DistributeIsk(self, sess):
        charID = sess.charid
        paymentFunc = lambda : self.escrow.PayIsk(charID)
        self._PayIsk(sess.charid, sess.shipid, self.attributes.distributeIskDelay, paymentFunc)

    def _PayIsk(self, charID, shipID, duration, paymentFunc):
        if self.isPaying:
            return
        self.isPaying = True
        try:
            self.lock.Unlock(charID, shipID, duration, paymentFunc)
        finally:
            self.isPaying = False

    def PersistEverything(self):
        self.escrow.PersistEverything()

    def IsLocked(self):
        return self.lock.IsLocked()

    def SetBonusChance(self, bonusChance):
        return self.escrow.SetBonusChance(bonusChance)

    def GetBonus(self):
        return self.escrow.bonus


def GetItemCreator(inventory, ballpark, typeIDs):
    return ItemCreator(inventory, ballpark, GetPriceByTagTypeID(typeIDs))
