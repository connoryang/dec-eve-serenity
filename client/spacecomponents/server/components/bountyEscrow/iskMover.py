#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\iskMover.py
import eve.common.lib.appConst as const

class IskMover(object):

    def __init__(self, account):
        self.account = account
        self.listeners = []

    def _MoveCash(self, charID, amount):
        self.account.MoveCash2(-1, const.refBountyPrize, const.ownerCONCORD, charID, amount)

    def PayIsk(self, iskByCharID, payingCharID):
        paymentDict = {}
        for charID, amount in iskByCharID.iteritems():
            self._MoveCash(charID, amount)
            paymentDict[charID] = amount

        for listener in self.listeners:
            listener(paymentDict, payingCharID)

    def RegisterForPaymentEvents(self, func):
        self.listeners.append(func)
