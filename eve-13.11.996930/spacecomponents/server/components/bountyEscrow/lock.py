#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\lock.py
import weakref
import uthread2
from eveexceptions import UserError
import spacecomponents.common.components.bountyEscrow as bountyEscrow
REASON_PROXIMITY = 'Ship out of proximity'
REASON_CLOAKED = 'Ship cloaked'
REASON_UNBOARDED = 'Ship unboarded'
REASON_GONE = 'Ship has left the bubble'
REASON_UNLOCK_SUCCESSFUL = 'Unlock was successful'

class Lock(object):

    def __init__(self, bountyEscrow):
        self.shipIDOfInterest = None
        self.bountyEscrow = weakref.proxy(bountyEscrow)
        self.itemID = bountyEscrow.itemID
        self.typeID = bountyEscrow.typeID
        self.GetSimTime = bountyEscrow.GetSimTime
        self.unlockingFor = None
        self.unlockingThread = None
        self.accessRange = bountyEscrow.attributes.accessRange
        self.listenersForUnlock = []
        self.listenerForSetUnlockedFor = None
        self.listenersForPossiblyLock = []

    def RegisterBallpark(self, ballpark):
        self.ballpark = ballpark
        ballpark.proximityRegistry.RegisterForProximity(self.bountyEscrow.itemID, self.accessRange, self.DoProximity)

    def RegisterForEvents(self, shipID):
        self.shipIDOfInterest = shipID
        self.ballpark.RegisterForCloakEvents(shipID, self.OnShipCloaked)
        self.ballpark.RegisterForUnboardEvents(shipID, self.OnShipUnboarded)
        sm.RegisterForNotifyEvent(self, 'ProcessBallRemoval')

    def UnregisterForEvents(self, shipID):
        self.ballpark.UnregisterForCloakEvents(shipID)
        self.ballpark.UnregisterForUnboardEvents(shipID)
        sm.UnregisterForNotifyEvent(self, 'ProcessBallRemoval')
        self.shipIDOfInterest = None

    def _NotifyForLockEvent(self, shipID, reason):
        ownerID = self.GetOwnerOfShip(shipID)
        for listener in self.listenersForPossiblyLock:
            listener(ownerID, shipID, reason)

    def _PossiblyLock(self, shipID, reason):
        if self.shipIDOfInterest is not None and self.shipIDOfInterest == shipID:
            self.Lock()
            self._NotifyForLockEvent(shipID, reason)

    def SlashLock(self):
        self._PossiblyLock(self.shipIDOfInterest, 'SlashLock')

    def Lock(self):
        if self.unlockingThread is not None:
            self.unlockingFor = None
            self._KillUnlockThread()
        self.SetLocked()

    def SetLocked(self):
        self._UpdateSlimItem(bountyEscrow.GetSlimStateForLocked())
        self.unlockingFor = None
        if self.shipIDOfInterest is not None:
            self.UnregisterForEvents(self.shipIDOfInterest)

    def DoProximity(self, ballID, entered):
        if not entered:
            self._PossiblyLock(ballID, REASON_PROXIMITY)

    def OnShipCloaked(self, shipID):
        self._PossiblyLock(shipID, REASON_CLOAKED)

    def OnShipUnboarded(self, shipID, charID):
        self._PossiblyLock(shipID, REASON_UNBOARDED)

    def ProcessBallRemoval(self, solarSystemID, item, isInteractive, position, bubbleID):
        self._PossiblyLock(item.itemID, REASON_GONE)

    def Unlock(self, charID, shipID, unlockDelay, callback):
        self._CheckCanUnlock(shipID)
        self.SetUnlockingFor(charID, shipID)
        self._UpdateSlimItem(bountyEscrow.GetSlimStateForUnlocking(self.GetSimTime(), unlockDelay, shipID))
        self.RegisterForEvents(shipID)
        self.unlockingThread = uthread2.StartTasklet(self._UnlockThread, charID, unlockDelay, callback)

    def _CheckCanUnlock(self, shipID):
        if self.ballpark.IsCloaked(shipID):
            raise UserError('CantAccessWhileCloaked')
        distance = self.ballpark.GetSurfaceDist(self.itemID, shipID)
        if distance > self.accessRange:
            raise UserError('BountyEscrowOutOfRange')
        unlockingCharID = self._GetUnlockingCharID()
        if unlockingCharID is not None:
            raise UserError('BountyEscrowAlreadyUnlocked', {'typeID': self.typeID,
             'charID': unlockingCharID})

    def _GetUnlockingCharID(self):
        if self.unlockingFor is not None:
            return self.unlockingFor[0]

    def _UnlockThread(self, charID, unlockDelay, callback):
        try:
            uthread2.SleepSim(unlockDelay)
            callback()
            self._NotifyForLockEvent(self.unlockingFor[1], REASON_UNLOCK_SUCCESSFUL)
        finally:
            self.SetLocked()

    def _KillUnlockThread(self):
        self.unlockingThread.Kill()
        self.unlockingThread = None

    def SetUnlockingFor(self, charID, shipID):
        self.unlockingFor = (charID, shipID)
        for listener in self.listenersForUnlock:
            listener(charID, shipID)

    def _UpdateSlimItem(self, *args):
        self.ballpark.UpdateSlimItemField(self.itemID, 'unlockState', *args)

    def IsLocked(self):
        return self.unlockingFor is None

    def RegisterForUnlockEvents(self, func):
        self.listenersForUnlock.append(func)

    def RegisterForPossiblyLockEvents(self, func):
        self.listenersForPossiblyLock.append(func)

    def GetOwnerOfShip(self, shipID):
        return self.ballpark.inventory2.GetItem(shipID).ownerID
