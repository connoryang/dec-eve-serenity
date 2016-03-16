#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipfitting\multiBuyUtil.py
from collections import defaultdict
import carbonui.const as uiconst
from localization import GetByLabel

def AddBuyButton(parent, fittingMgmtWnd):
    from eve.client.script.ui.control.buttons import Button

    def CallBuyFit():
        fitting = fittingMgmtWnd.fitting
        BuyFit(fitting.shipTypeID, fitting.fitData)

    buyBtn = Button(parent=parent, label=GetByLabel('UI/Market/MarketQuote/BuyAll'), func=lambda *args: CallBuyFit(), align=uiconst.NOALIGN)


def BuyFit(shipTypeID, fitData, *args):
    buyDict = defaultdict(int)
    for typeID, flag, qty in fitData:
        buyDict[typeID] += qty

    buyDict[shipTypeID] = 1
    BuyMultipleTypesWithQty(buyDict)


def BuyMultipleTypes(items, *args):
    buyDict = {}
    for eachItem in items[0]:
        buyDict[eachItem[0].typeID] = 1

    BuyMultipleTypesWithQty(buyDict)


def BuyMultipleTypesWithQty(buyDict):
    multiBuyClass = GetMultiBuyClass()
    wnd = multiBuyClass.GetIfOpen()
    if wnd and not wnd.destroyed:
        wnd.AddToOrder(wantToBuy=buyDict)
    else:
        wnd = multiBuyClass(wantToBuy=buyDict)
    return wnd


def GetMultiBuyClass():
    from eve.client.script.ui.shared.market.buyMultiFromBase import MultiBuy
    return MultiBuy
