#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\controllers\test\test_offerPurchase.py
from eve.client.script.ui.shared.vgs.controllers.offerPurchase import OfferPurchaseController, PurchaseFailureError
import mock
import unittest
from vgsclient import Offer, Store, PurchaseFailedError, PurchaseInProgressError
OFFER = Offer(id=101, name='offer name', description='offer description', href='offer href', price=1000, basePrice=2500, imageUrl='image url', productQuantities={1: (10, 1)}, categories=[], label='label')

class OfferPurchaseControllerTest(unittest.TestCase):

    def setUp(self):
        self.store = mock.Mock(spec=Store)
        self.controller = OfferPurchaseController(OFFER, self.store)

    def test_PurchaseHappyPath(self):
        self.controller.Buy()
        self.store.PurchaseOffer.assert_called_once_with(OFFER, quantity=1)

    def test_PurchaseFailure(self):
        self.store.PurchaseOffer.side_effect = PurchaseFailedError()
        with self.assertRaises(PurchaseFailureError):
            self.controller.Buy()


if __name__ == '__main__':
    unittest.main()
