#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\states.py
import inventorycommon.typeHelpers
from reprocessing.ui.const import STATE_RESTRICTED, STATE_SUSPICIOUS

class States(object):

    def __init__(self, quotes):
        self.quotes = quotes

    def GetState(self, item):
        materials = self.quotes.GetClientMaterial(item.itemID)
        if not materials:
            return STATE_RESTRICTED
        valueOfInput = self._GetAveragePrice(item.typeID) * item.stacksize
        valueOfOutput = sum((self._GetAveragePrice(typeID) * qty for typeID, qty in materials.iteritems()))
        if valueOfOutput * 2 < valueOfInput:
            return STATE_SUSPICIOUS

    def _GetAveragePrice(self, typeID):
        price = inventorycommon.typeHelpers.GetAveragePrice(typeID)
        if price is None:
            return 0.0
        return price
