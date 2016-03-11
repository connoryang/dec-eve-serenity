#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\marketutil\orderInfo.py
from utillib import KeyVal

class OrderInfo(object):

    def __init__(self, charID, corpID, corpRole, corpAccountKey, currentRegionID, currentSolarsystemID, currentStationID, items, useCorp, orderStationID, orderRange, orderDuration, orderEscrow = 0.0):
        self.charID = charID
        self.corpID = corpID
        self.corpRole = corpRole
        self.corpAccountKey = corpAccountKey
        self.currentRegionID = currentRegionID
        self.currentSolarsystemID = currentSolarsystemID
        self.currentStationID = currentStationID
        self.items = items
        self.useCorp = useCorp
        self.orderStationID = orderStationID
        self.orderRange = orderRange
        self.orderDuration = orderDuration
        self.orderEscrow = orderEscrow


def GetBuyItemInfo(stationID, typeID, price, quantity, minVolume = 1, delta = 0):
    return KeyVal(stationID=stationID, typeID=typeID, price=price, quantity=quantity, minVolume=minVolume, delta=delta)
