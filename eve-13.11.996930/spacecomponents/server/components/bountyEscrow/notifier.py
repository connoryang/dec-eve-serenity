#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\notifier.py
from eve.common.script.util.notificationconst import notificationTypeBountyESSShared
from eve.common.script.util.notificationconst import notificationTypeBountyESSTaken

class Notifier(object):

    def __init__(self, notificationMgr):
        self.notificationMgr = notificationMgr

    def RegisterForNotifications(self, escrow):
        escrow.RegisterForPaymentEvents(self.NotifyBountyShared)
        escrow.RegisterForItemCreationEvents(self.NotifyBountyTaken)
        self.senderID = escrow.lpCorpID

    def NotifyBountyShared(self, paymentDict, payingCharID):
        totalIskAmount = sum(paymentDict.itervalues())
        for receiverID, amount in paymentDict.iteritems():
            self.notificationMgr.SendToCharacter(notificationTypeBountyESSShared, receiverID, self.senderID, data={'charID': payingCharID,
             'totalIsk': totalIskAmount,
             'myIsk': amount})

    def NotifyBountyTaken(self, stealerCharID, itemDict, paymentDict):
        totalIskAmount = sum(paymentDict.itervalues())
        for receiverID, amount in paymentDict.iteritems():
            self.notificationMgr.SendToCharacter(notificationTypeBountyESSTaken, receiverID, self.senderID, data={'charID': stealerCharID,
             'totalIsk': totalIskAmount,
             'myIsk': amount})


NOTIFICATION_TIME = 100000000L

class RangeNotifier(object):

    def __init__(self, solarSystemID, ballpark, machoNet, GetTime):
        self.solarSystemID = solarSystemID
        self.GetTime = GetTime
        self.ballpark = ballpark
        self.machoNet = machoNet
        self.lastNotificationTime = None

    def PlayerInRange(self, ballID, entered):
        if entered:
            currentTime = self.GetTime()
            if self.lastNotificationTime is None or currentTime - self.lastNotificationTime > NOTIFICATION_TIME:
                charID = self.ballpark.GetPilotIDFromShipID(ballID)
                if charID is not None:
                    self.lastNotificationTime = currentTime
                    self.machoNet.SinglecastBySolarSystemID(self.solarSystemID, 'OnBountyEscrowPlayerInRange', charID)
