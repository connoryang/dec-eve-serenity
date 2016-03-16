#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\vgsclient\account.py
import logging
import signals
log = logging.getLogger(__name__)

class Account:

    def __init__(self, vgsCrestConnection):
        self.vgsCrestConnection = vgsCrestConnection
        self.aurumBalance = None
        self.transactionHref = None
        self.accountAurumBalanceChanged = signals.Signal()
        self.redeemingTokensUpdated = signals.Signal()

    def ClearCache(self):
        self.aurumBalance = None
        self.vgsCrestConnection.ClearCache()

    def SubscribeToAurumBalanceChanged(self, callBackFunction):
        self.accountAurumBalanceChanged.connect(callBackFunction)

    def SubscribeToRedeemingTokensUpdatedEvent(self, callBackFunction):
        self.redeemingTokensUpdated.connect(callBackFunction)

    def UnsubscribeFromAurumBalanceChanged(self, callBackFunction):
        self.accountAurumBalanceChanged.disconnect(callBackFunction)

    def UnsubscribeFromRedeemingTokensUpdatedEvent(self, callBackFunction):
        self.redeemingTokensUpdated.disconnect(callBackFunction)

    def OnAurumChangeFromVgs(self, newBalance):
        log.debug('OnAurumChangeFromVgs %s' % newBalance)
        self.aurumBalance = newBalance
        self.accountAurumBalanceChanged(self.aurumBalance)

    def OnRedeemingTokensUpdated(self):
        self.redeemingTokensUpdated()

    def GetAurumBalance(self):
        if self.aurumBalance is None:
            self._GetAurumAccount()
        return self.aurumBalance

    def _GetAurumAccount(self):
        account = self.vgsCrestConnection.GetAurAccount()
        self.aurumBalance = account['balance']
        self.transactionHref = account['transactions']['href']

    def GetTransactionHref(self):
        if self.transactionHref is None:
            self._GetAurumAccount()
        return self.transactionHref
