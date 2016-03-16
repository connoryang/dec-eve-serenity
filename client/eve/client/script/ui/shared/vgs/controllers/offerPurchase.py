#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\controllers\offerPurchase.py
from eve.client.script.ui.shared.vgs.events import LogPurchaseOffer
import evetypes
import signals
from inventorycommon.const import groupShipSkins

class PurchaseFailureError(Exception):
    pass


class NotEnoughAurumError(PurchaseFailureError):
    pass


class OfferPurchaseController(object):

    def __init__(self, offer, store):
        self.offer = offer
        self.store = store
        self.account = store.GetAccount()
        self.onAurBalanceChanged = signals.Signal()
        self.account.SubscribeToAurumBalanceChanged(self.onAurBalanceChanged)

    @property
    def balance(self):
        return self.account.GetAurumBalance()

    @property
    def totalPrice(self):
        return self.offer.price

    def Buy(self):
        if self.balance < self.totalPrice:
            raise NotEnoughAurumError()
        try:
            self.store.PurchaseOffer(self.offer, quantity=1)
        except Exception as e:
            raise PurchaseFailureError(e)
        else:
            LogPurchaseOffer(self.offer.id, 1)

    def IsProductActivatable(self):
        if len(self.offer.productQuantities) != 1:
            return False
        return evetypes.GetGroupID(self.activatableProductTypeID) == groupShipSkins

    @property
    def activatableProductTypeID(self):
        return self.offer.productQuantities.values()[0][0]
