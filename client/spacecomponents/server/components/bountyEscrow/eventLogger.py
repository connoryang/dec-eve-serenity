#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\eventLogger.py
from eveexceptions.exceptionEater import ExceptionEater
EVENT_PAYISK = 'spacecomponent::iskMover_PayIsk'
EVENT_CREATEITEMS = 'spacecomponent::itemCreator_CreateItems'
EVENT_UNLOCK = 'spacecomponent::lock_Unlock'
EVENT_POSSIBLYLOCK = 'spacecomponent::lock_PossiblyLock'
EVENT_REGISTERISK = 'spacecomponent::iskRegistry_RegisterIsk'

class EventLogger(object):

    def __init__(self, eventLog, solarSystemID, ownerID, itemID):
        self.eventLog = eventLog
        self.solarSystemID = solarSystemID
        self.ownerID = ownerID
        self.itemID = itemID

    def RegisterForLogging(self, lock, escrow):
        escrow.RegisterForPaymentEvents(self.LogPayIsk)
        escrow.RegisterForItemCreationEvents(self.LogCreateItems)
        escrow.RegisterForRegisterIskEvents(self.LogRegisterIsk)
        lock.RegisterForUnlockEvents(self.LogUnlock)
        lock.RegisterForPossiblyLockEvents(self.LogPossiblyLock)

    def GetTuplesAsText(self, tuples):
        for each in tuples:
            yield '%d:%d' % each

    def LogPayIsk(self, paymentDict, payingCharID):
        with ExceptionEater('eventLog'):
            txt = ','.join(self.GetTuplesAsText(paymentDict.iteritems()))
            self.eventLog.LogOwnerEvent(EVENT_PAYISK, self.ownerID, self.solarSystemID, self.itemID, payingCharID, txt, otherOwnerID=payingCharID)
            self.eventLog.LogOwnerEventJson(EVENT_PAYISK, self.ownerID, self.solarSystemID, componentItemID=self.itemID, payingCharID=payingCharID, paymentList=txt, otherOwnerID=payingCharID)

    def LogCreateItems(self, charID, itemDict, paymentDict):
        with ExceptionEater('eventLog'):
            itemDictAsTxt = ','.join(self.GetTuplesAsText(itemDict.iteritems()))
            paymentDictAsTxt = ','.join(self.GetTuplesAsText(paymentDict.iteritems()))
            self.eventLog.LogOwnerEvent(EVENT_CREATEITEMS, self.ownerID, self.solarSystemID, self.itemID, charID, itemDictAsTxt, paymentDictAsTxt, otherOwnerID=charID)
            self.eventLog.LogOwnerEventJson(EVENT_CREATEITEMS, self.ownerID, self.solarSystemID, componentItemID=self.itemID, charID=charID, itemList=itemDictAsTxt, paymentList=paymentDictAsTxt, otherOwnerID=charID)

    def LogUnlock(self, charID, shipID):
        self.LogItemAndActorOwnerEvent(charID, EVENT_UNLOCK)

    def LogItemAndActorOwnerEvent(self, charID, eventName):
        with ExceptionEater('eventLog'):
            self.eventLog.LogOwnerEvent(eventName, self.ownerID, self.solarSystemID, self.itemID, charID, otherOwnerID=charID)
            self.eventLog.LogOwnerEventJson(eventName, self.ownerID, self.solarSystemID, componentItemID=self.itemID, charID=charID, otherOwnerID=charID)

    def LogPossiblyLock(self, charID, shipID, reason):
        with ExceptionEater('eventLog'):
            self.eventLog.LogOwnerEvent(EVENT_POSSIBLYLOCK, self.ownerID, self.solarSystemID, self.itemID, charID, reason, otherOwnerID=charID)
            self.eventLog.LogOwnerEventJson(EVENT_POSSIBLYLOCK, self.ownerID, self.solarSystemID, componentItemID=self.itemID, charID=charID, reason=reason, otherOwnerID=charID)

    def LogRegisterIsk(self, charID, amount):
        with ExceptionEater('eventLog'):
            self.eventLog.LogOwnerEvent(EVENT_REGISTERISK, self.ownerID, self.solarSystemID, self.itemID, charID, amount, otherOwnerID=charID)
            self.eventLog.LogOwnerEventJson(EVENT_REGISTERISK, self.ownerID, self.solarSystemID, componentItemID=self.itemID, charID=charID, amount=amount, otherOwnerID=charID)
