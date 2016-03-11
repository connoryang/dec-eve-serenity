#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\sellMulti.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst, const
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.services.menuSvcExtras.invItemFunctions import CheckIfInHangarOrCorpHangarAndCanTake
from eve.client.script.ui.shared.market.buySellMultiBase import SellBuyItemsWindow, COL_RED, COL_GREEN
from eve.client.script.ui.shared.market.sellItemEntry import SellItemContainer
from eve.common.script.sys.eveCfg import GetActiveShip, IsStation
from eve.common.script.util.eveFormat import FmtISK
import evetypes
from localization import GetByLabel
from marketutil import INVENTORY_GUIDS
import uthread
from utillib import KeyVal

class SellItems(SellBuyItemsWindow):
    __guid__ = 'form.SellItems'
    default_windowID = 'SellItemsWindow'
    default_name = 'SellItems'
    captionTextPath = 'UI/Inventory/ItemActions/MultiSell'
    scrollId = 'MultiSellScroll'
    durationSettingConfig = 'multiSellDuration'
    tradeForCorpSettingConfig = 'sellUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandSell'
    orderCap = 'MultiSellOrderCap'

    def ApplyAttributes(self, attributes):
        SellBuyItemsWindow.ApplyAttributes(self, attributes)
        if self.useCorp:
            top = 48
        else:
            top = 30
        self.orderCountLabel = EveLabelSmall(parent=self.bottomLeft, top=top, left=2)
        self.maxCount = self.GetMaxOrderCount()
        self.myOrderCount = self.GetCurrentOrderCount()
        self.UpdateOrderCount()
        self.DrawDurationCombo()
        self.StartAddItemsThread()

    def InitializeVariables(self, attributes):
        SellBuyItemsWindow.InitializeVariables(self, attributes)
        self.itemDict = {}
        self.sellItemList = []
        self.itemsNeedRepackaging = []
        self.itemAlreadyInList = []

    def AddPreItems(self, preItems):
        if not self.CheckItemLocation(preItems[0][0]):
            return
        items = self.CheckOrderAvailability(preItems)
        self.ClearErrorLists()
        for item in items:
            self.AddItem(item[0])

        self.DisplayErrorHints()

    def CheckItemLocation(self, item):
        if not self.CheckStation(item) and len(self.itemList) > 0:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/LocationNotShared')})
            return False
        return True

    def GetErrorHints(self):
        hintTextList = SellBuyItemsWindow.GetErrorHints(self)
        alreadyInList = self.BuildHintTextList(self.itemAlreadyInList, 'UI/Market/MarketQuote/AlreadyInList')
        if hintTextList and alreadyInList:
            hintTextList.append('')
        hintTextList += alreadyInList
        needsRepackaging = self.BuildHintTextList(self.itemsNeedRepackaging, 'UI/Market/MarketQuote/NeedsRepackaging')
        if hintTextList and needsRepackaging:
            hintTextList.append('')
        hintTextList += needsRepackaging
        return hintTextList

    def AddItem(self, item):
        if not self.IsSellable(item):
            return
        self.itemDict[item.itemID] = item
        itemEntry = self.DoAddItem(item)
        if len(self.itemList) == 1:
            self.UpdateStationInfo(itemEntry.stationID)
        self.CheckItemSize()
        uicore.registry.SetFocus(itemEntry.priceEdit)

    def GetItemEntry(self, item):
        itemEntry = SellItemContainer(item=item, editFunc=self.OnEntryEdit, align=uiconst.TOTOP, parentFunc=self.RemoveItem)
        return itemEntry

    def AddItemToCollection(self, item, itemEntry):
        self.itemDict[item.itemID] = item

    def CheckItemSize(self):
        if not len(self.itemList):
            return
        firstItem = self.itemList[0]
        if len(self.itemList) == 1:
            firstItem.MakeSingle()
        elif len(self.itemList) == 2:
            firstItem.RemoveSingle()

    def UpdateStationInfo(self, stationID):
        self.baseStationID = stationID
        if self.baseStationID:
            self.UpdateHeaderCount()
        else:
            self.SetCaption(GetByLabel(self.captionTextPath))

    def RemoveItem(self, itemEntry):
        SellBuyItemsWindow.RemoveItem(self, itemEntry)
        self.CheckItemSize()
        if len(self.itemList) == 0:
            self.baseStationID = None
            self.UpdateStationInfo(None)

    def RemoveItemFromCollection(self, itemEntry):
        self.itemDict.pop(itemEntry.itemID)

    def CheckStation(self, item):
        itemStationID, _, _ = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(item)
        if itemStationID != self.baseStationID:
            return False
        return True

    def ClearErrorLists(self):
        SellBuyItemsWindow.ClearErrorLists(self)
        self.itemsNeedRepackaging = []
        self.itemAlreadyInList = []

    def IsSellable(self, item):
        sellable = True
        if item.itemID in self.itemDict.keys():
            self.itemAlreadyInList.append(item)
            sellable = False
        elif item.singleton:
            self.itemsNeedRepackaging.append(item)
            sellable = False
        elif IsStation(item.itemID):
            self.cannotTradeItemList.append(item)
            sellable = False
        elif evetypes.GetMarketGroupID(item.typeID) is None:
            self.cannotTradeItemList.append(item)
            sellable = False
        elif item.ownerID not in [session.corpid, session.charid]:
            self.cannotTradeItemList.append(item)
            sellable = False
        elif item.itemID == GetActiveShip():
            self.cannotTradeItemList.append(item)
            sellable = False
        elif bool(item.singleton) and item.categoryID == const.categoryBlueprint:
            self.cannotTradeItemList.append(item)
            sellable = False
        elif not CheckIfInHangarOrCorpHangarAndCanTake(item):
            self.cannotTradeItemList.append(item)
            sellable = False
        return sellable

    def OnEntryEdit(self, *args):
        uthread.new(self.UpdateNumbers)

    def DropItems(self, dragObj, nodes):
        if not self.CheckItemLocation(nodes[0].item):
            return
        items = self.CheckOrderAvailability(nodes)
        self.ClearErrorLists()
        for node in items:
            if getattr(node, '__guid__', None) in INVENTORY_GUIDS:
                self.AddItem(node.item)

        self.DisplayErrorHints()

    def DrawDurationCombo(self):
        durations = [[GetByLabel('UI/Market/MarketQuote/Immediate'), 0],
         [GetByLabel('UI/Common/DateWords/Day'), 1],
         [GetByLabel('UI/Market/MarketQuote/ThreeDays'), 3],
         [GetByLabel('UI/Common/DateWords/Week'), 7],
         [GetByLabel('UI/Market/MarketQuote/TwoWeeks'), 14],
         [GetByLabel('UI/Common/DateWords/Month'), 30],
         [GetByLabel('UI/Market/MarketQuote/ThreeMonths'), 90]]
        durationValue = settings.user.ui.Get(self.durationSettingConfig, 0)
        self.durationCombo = Combo(parent=self.bottomLeft, options=durations, select=durationValue, top=6, callback=self.OnDurationChange)

    def UpdateNumbers(self):
        brokersFee, salesTax, totalSum = self.GetSums()
        totalShown = totalSum - salesTax - brokersFee
        if totalSum > 0:
            brokersPerc = round(brokersFee / totalSum * 100, 2)
            salesPerc = round(salesTax / totalSum * 100, 2)
        else:
            brokersPerc = 0.0
            salesPerc = 0.0
        self.brokersFeeAmt.text = FmtISK(brokersFee)
        self.brokersFee.text = GetByLabel('UI/Market/MarketQuote/BrokersFeePerc', percentage=brokersPerc)
        self.salesTaxAmt.text = FmtISK(salesTax)
        self.salesTax.text = GetByLabel('UI/Market/MarketQuote/SalesTaxPerc', percentage=salesPerc)
        self.totalAmt.text = FmtISK(totalShown)
        if totalShown < 0:
            self.totalAmt.SetRGB(*COL_RED)
        else:
            self.totalAmt.SetRGB(*COL_GREEN)

    def GetSums(self):
        brokersFee = 0.0
        salesTax = 0
        totalSum = 0
        isImmediate = self.durationCombo.GetValue() == 0
        for item in self.GetItems():
            if item:
                brokersFee += item.brokersFee
                if isImmediate and item.bestBid is None:
                    salesTax += 0
                else:
                    salesTax += item.salesTax
                totalSum += item.totalSum

        if isImmediate:
            brokersFee = 0.0
        return (brokersFee, salesTax, totalSum)

    def PerformTrade(self, *args):
        self.sellItemList = []
        unitCount = self.GetUnitCount()
        allItems = self.GetItems()
        if unitCount == 0:
            return
        if eve.Message('ConfirmSellingItems', {'noOfItems': int(unitCount)}, uiconst.OKCANCEL, suppress=uiconst.ID_OK) != uiconst.ID_OK:
            return
        self.errorItemList = []
        useCorp = self.TradingForCorp()
        duration = self.durationCombo.GetValue()
        for item in allItems:
            if duration == 0:
                if item.bestBid:
                    self.ValidateItem(item)
                else:
                    continue
            else:
                self.ValidateItem(item)

        if not len(self.sellItemList):
            return
        sm.GetService('marketQuote').SellMulti(self.sellItemList, useCorp, duration)
        self.Close()

    def GetUnitCount(self):
        unitCount = 0
        isImmediate = self.durationCombo.GetValue() == 0
        for item in self.itemList:
            if isImmediate:
                unitCount += item.GetSellCountEstimate()
            else:
                unitCount += item.GetQty()

        return unitCount

    def ValidateItem(self, item):
        price = round(item.GetPrice(), 2)
        if price > self.MAX_PRICE:
            return
        if self.durationCombo.GetValue() == 0:
            if not item.bestBid:
                return
        qty = item.GetQty()
        validatedItem = KeyVal(stationID=int(item.stationID), typeID=int(item.typeID), itemID=item.itemID, price=price, quantity=int(qty), located=item.located)
        self.sellItemList.append(validatedItem)

    def IsAllowedGuid(self, guid):
        if guid not in INVENTORY_GUIDS:
            return False
        return True

    def OnDurationChange(self, *args):
        settings.user.ui.Set(self.durationSettingConfig, self.durationCombo.GetValue())
        self.UpdateNumbers()
        for item in self.GetItems():
            if self.durationCombo.GetValue() == 0:
                item.ShowNoSellOrders()
            else:
                item.HideNoSellOrders()

    def UpdateOrderCount(self):
        self.orderCountLabel.text = GetByLabel('UI/Market/MarketQuote/OpenOrdersRemaining', orders=FmtAmt(self.maxCount - self.myOrderCount), maxOrders=FmtAmt(self.maxCount))

    def OnUseCorp(self, *args):
        SellBuyItemsWindow.OnUseCorp(self, *args)
        self.UpdateOrderCount()

    def GetMaxOrderCount(self):
        limits = self.marketQuoteSvc.GetSkillLimits()
        maxCount = limits['cnt']
        return maxCount

    def GetCurrentOrderCount(self):
        myOrders = self.marketQuoteSvc.GetMyOrders()
        return len(myOrders)
