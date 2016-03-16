#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\buyMultiFromBase.py
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.shared.market.buySellMultiBase import SellBuyItemsWindow, COL_RED
from eve.client.script.ui.shared.market.buytItemEntry import BuyItemContainer
from eve.client.script.util.contractutils import FmtISKWithDescription
from eve.common.script.util.eveFormat import FmtISK
from eveexceptions.exceptionEater import ExceptionEater
import evetypes
from localization import GetByLabel
from marketutil import GetTypeIDFromDragItem
from marketutil.orderInfo import GetBuyItemInfo
import uthread
from utillib import KeyVal
import blue
import log
MILLION = 1000000

class MultiBuy(SellBuyItemsWindow):
    __guid__ = 'form.BuyItems'
    default_iconNum = 'res:/UI/Texture/classes/MultiSell/multiBuy.png'
    default_windowID = 'MultiBuy'
    default_name = 'multiBuy'
    captionTextPath = 'UI/Inventory/ItemActions/MultiBuy'
    scrollId = 'MultiBuyScroll'
    tradeForCorpSettingConfig = 'buyUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandBuy'
    orderCap = 'MultiBuyOrderCap'
    tradeOnConfirm = False
    dropLabelPath = 'UI/Market/Marketbase/DropItemsToAddToBuy'
    corpCheckboxTop = 0
    numbersGridTop = 1
    showTaxAndBrokersFee = False
    belowColor = '<color=0xff00ff00>'
    aboveColor = '<color=0xffff5050>'
    __notifyevents__ = ['OnOwnOrdersChanged', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        self.blinkEditBG = None
        SellBuyItemsWindow.ApplyAttributes(self, attributes)
        self.dropCont.OnDropData = self.DropItems
        self.infoCont.height = 40
        self.totalAmt.LoadTooltipPanel = self.LoadTotalTooltip
        self.itemsScroll.OnDropData = self.DropItems
        self.DrawStationWarning()
        self.AddToLocationCont()
        self.StartAddItemsThread()

    def InitializeVariables(self, attributes):
        SellBuyItemsWindow.InitializeVariables(self, attributes)
        self.entriesInScrollByTypeID = {}
        self.orderMultiplier = 1
        self.activeOrders = set()
        self.orderDisabled = False
        self.preItems = self.GetKeyValsForWantedTypes(attributes.get('wantToBuy'))
        self.reloadingItemsCounter = 0
        self.verifyMultiplierTimer = None

    def GetKeyValsForWantedTypes(self, wantToBuy):
        keyVals = []
        for typeID, qty in wantToBuy.iteritems():
            keyVals.append(KeyVal(typeID=typeID, qty=qty))

        return keyVals

    def AddToLocationCont(self):
        self.locationCont.height = 28
        self.orderMultiplierEdit = SinglelineEdit(name='orderMultiplierEdit', parent=self.locationCont, align=uiconst.TOPRIGHT, label=GetByLabel('UI/Market/MarketQuote/NumberOfOrders'), adjustWidth=True, ints=[1, 1000], left=const.defaultPadding, OnChange=self.OnMultiplierEditChange)
        self.stationCombo = Combo(parent=self.locationCont, callback=self.OnStationChanged, left=const.defaultPadding, width=200, noChoiceLabel=GetByLabel('UI/Market/MarketQuote/NotStationsAvailable'))
        self.LoadStationOptions()

    def LoadStationOptions(self):
        currentSelection = self.stationCombo.GetValue()
        stations = self.GetStations()
        if currentSelection:
            select = currentSelection
        elif session.stationid2:
            select = session.stationid2
        elif stations:
            select = stations[0][1]
        else:
            select = None
        self.stationCombo.LoadOptions(stations, select)
        self.stationCombo.Confirm()

    def DrawStationWarning(self):
        self.stationWarning = EveLabelLargeBold(parent=self.bottomLeft, text='', align=uiconst.CENTERBOTTOM)
        self.stationWarning.SetRGB(*COL_RED)
        self.stationWarning.display = False

    def AddToOrder(self, wantToBuy):
        wantedTypes = self.GetKeyValsForWantedTypes(wantToBuy)
        self.AddPreItems(wantedTypes)

    def AddPreItems(self, preItems):
        self.reloadingItemsCounter += 1
        items = self.CheckOrderAvailability(preItems)
        self.ClearErrorLists()
        for item in items:
            self.AddItem(item)

        self.DisplayErrorHints()
        self.reloadingItemsCounter -= 1

    def AddItem(self, itemKeyVal):
        if not self.IsBuyable(itemKeyVal):
            return
        existingEntry = self.entriesInScrollByTypeID.get(itemKeyVal.typeID, None)
        if existingEntry and not existingEntry.destroyed:
            existingEntry.AddQtyToEntry(itemKeyVal.qty)
        else:
            self.DoAddItem(itemKeyVal)

    def AddItemToCollection(self, itemKeyVal, itemEntry):
        self.entriesInScrollByTypeID[itemKeyVal.typeID] = itemEntry

    def GetItemEntry(self, itemKeyVal):
        itemEntry = BuyItemContainer(typeID=itemKeyVal.typeID, qty=int(itemKeyVal.qty), parentFunc=self.RemoveItem, editFunc=self.OnEntryEdit, stationID=self.baseStationID, orderMultiplier=self.orderMultiplier, dropParentFunc=self.DropItems)
        return itemEntry

    def PerformTrade(self, *args):
        useCorp = self.TradingForCorp()
        buyItemList, failedItems = self.GetValidatedAndFailedTypes()
        if not len(buyItemList):
            uicore.Message('uiwarning03')
            return
        if not self.ContinueAfterWarning(buyItemList):
            return
        with ExceptionEater():
            self.LogBuy(buyItemList)
        ordersCreated = sm.GetService('marketQuote').BuyMulti(self.baseStationID, buyItemList, useCorp)
        orderIDs = {order.orderID for order in ordersCreated}
        self.activeOrders.update(orderIDs)
        self.CreateNewBuyOrder(failedItems)

    def ContinueAfterWarning(self, buyItemList):
        highItems = []
        for item in buyItemList:
            if item.delta > 1.0:
                highItems.append((item.delta, item))

        orderPercentage = self.GetOrderDelta()
        orderText = ''
        if orderPercentage > 1.0:
            percText = GetByLabel('UI/Common/Percentage', percentage=FmtAmt(abs(orderPercentage * 100), showFraction=0))
            orderText = GetByLabel('UI/Market/MarketQuote/MultiBuyAboveAverage', percentage=percText)
        hightText = ''
        if highItems:
            highTextList = [GetByLabel('UI/Market/MarketQuote/MultiBuyTypesAboveAverage')]
            highItems.sort(key=lambda x: x[0], reverse=True)
            for perc, item in highItems:
                percText = GetByLabel('UI/Common/Percentage', percentage=FmtAmt(perc * 100, showFraction=0))
                highTextList.append('- %s (%s)' % (evetypes.GetName(item.typeID), percText))

            hightText = '<br>'.join(highTextList)
        if orderText or hightText:
            warningTextList = []
            if orderText:
                warningTextList.append(orderText)
                warningTextList.append('')
            if hightText:
                warningTextList.append(hightText)
                warningTextList.append('')
            warningTextList.append(GetByLabel('UI/Market/MarketQuote/MultiBuyAboveAverageConfirmation'))
            warningText = '<br>'.join(warningTextList)
            headerLabel = GetByLabel('UI/Generic/Warning')
            ret = eve.Message('CustomQuestion', {'header': headerLabel,
             'question': warningText}, uiconst.YESNO, default=uiconst.ID_NO)
            if ret != uiconst.ID_YES:
                return False
        return True

    def GetValidatedAndFailedTypes(self):
        allItems = self.GetItems()
        failedItemsList = []
        buyItemsList = []
        for item in allItems:
            if item.isUpdating:
                return ([], [])
            if item.newBestPrice:
                validatedItem = self.GetValidatedItem(item)
                if validatedItem:
                    buyItemsList.append(validatedItem)
                    continue
            failedBuyInfo = KeyVal(typeID=item.typeID, qty=item.GetTotalQty())
            failedItemsList.append(failedBuyInfo)

        return (buyItemsList, failedItemsList)

    def GetValidatedItem(self, item):
        if item.isUpdating:
            return
        price = item.GetPrice()
        if not price:
            return
        if price > self.MAX_PRICE:
            return
        price = round(price, 2)
        qty = item.GetTotalQty()
        if qty < 1:
            return
        validatedItem = GetBuyItemInfo(stationID=session.stationid, typeID=item.typeID, price=price, quantity=qty, minVolume=1, delta=item.GetDelta())
        return validatedItem

    def CreateNewBuyOrder(self, failedItems):
        self.ChangeOrderUIState(disable=True)
        self.RemoveAllItem()
        if self.orderMultiplierEdit.GetValue() != 1:
            self.BlinkNumOrdersEdit()
        self.orderMultiplierEdit.SetValue(1)
        if failedItems:
            self.AddPreItems(failedItems)

    def ChangeOrderUIState(self, disable):
        if disable:
            opacity = 0.5
        else:
            opacity = 1.0
        mainArea = self.GetMainArea()
        mainArea.opacity = opacity
        self.orderDisabled = disable

    def GetStations(self):
        solarsytemItems = sm.GetService('map').GetSolarsystemItems(session.solarsystemid2, True, False)
        stations = {i for i in solarsytemItems if i.groupID == const.groupStation}
        stationList = []
        for eachStation in stations:
            if eachStation.itemID == session.stationid:
                continue
            sortValue = (eachStation.celestialIndex, eachStation.orbitIndex, eachStation.itemName)
            stationList.append((sortValue, (eachStation.itemName, eachStation.itemID)))

        stationList = SortListOfTuples(stationList)
        if session.stationid:
            stationName = cfg.evelocations.Get(session.stationid).name
            currentStationOption = (GetByLabel('UI/Market/MarketQuote/CurrentStation', stationName=stationName), session.stationid)
            stationList = [currentStationOption] + stationList
        return stationList

    def RemoveItemFromCollection(self, itemEntry):
        self.entriesInScrollByTypeID.pop(itemEntry.typeID, None)

    def OnMultiplierEditChange(self, *args):
        self.UpdateOrderMultiplierInEntries()
        if self.verifyMultiplierTimer:
            self.verifyMultiplierTimer.KillTimer()
        self.verifyMultiplierTimer = AutoTimer(2000, self.VerifyOrderMultiplier_thread)

    def UpdateOrderMultiplierInEntries(self, force = True):
        self.orderMultiplier = self.orderMultiplierEdit.GetValue()
        for item in self.GetItemsIterator():
            if force or item.orderMultiplier != self.orderMultiplier:
                item.UpdateOrderMultiplier(self.orderMultiplier)

    def VerifyOrderMultiplier_thread(self):
        self.verifyMultiplierTimer = None
        self.UpdateOrderMultiplierInEntries(force=False)

    def OnEntryEdit(self, *args):
        uthread.new(self.UpdateNumbers)

    def UpdateNumbers(self):
        totalShown = self.GetSum()
        if totalShown >= MILLION:
            totalAmtText = '%s (%s)' % (FmtISK(totalShown), FmtISKWithDescription(totalShown, justDesc=True))
        else:
            totalAmtText = FmtISK(totalShown)
        self.totalAmt.text = totalAmtText
        self.totalAmt.SetRGB(*COL_RED)
        self.ShowOrHideStationWarning()

    def ShowOrHideStationWarning(self):
        if self.baseStationID is None:
            self.stationWarning.text = GetByLabel('UI/Market/MarketQuote/NoStationSelected')
            self.stationWarning.display = True
        elif self.baseStationID == session.stationid2:
            self.stationWarning.display = False
        else:
            self.stationWarning.text = GetByLabel('UI/Market/MarketQuote/StationWarning')
            self.stationWarning.display = True

    def GetSum(self):
        totalSum = 0
        for item in self.GetItemsIterator():
            totalSum += item.GetTotalSum()

        return totalSum

    def LoadTotalTooltip(self, tooltipPanel, *args):
        totalShown = self.GetSum()
        if not totalShown or not self.orderMultiplier:
            return
        numTypes, numAvailableTypes = self.GetNumTypesAndNumAvailableTypes()
        pricePerOrder = totalShown / float(self.orderMultiplier)
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/NumOrders'))
        tooltipPanel.AddLabelMedium(text=FmtAmt(self.orderMultiplier), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/PricePerOrder'))
        tooltipPanel.AddLabelMedium(text=FmtISK(pricePerOrder), align=uiconst.CENTERRIGHT)
        if pricePerOrder >= MILLION:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text='=%s' % FmtISKWithDescription(pricePerOrder, justDesc=True), align=uiconst.CENTERRIGHT)
        buyingText = GetByLabel('UI/Market/MarketQuote/TypesAvailableAndTotalInOrder', numAvailable=numAvailableTypes, numTypes=numTypes)
        buyingLabel = tooltipPanel.AddLabelSmall(text=buyingText, align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
        buyingLabel.SetAlpha(0.6)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        deltaText = self.GetOrderDeltaText()
        tooltipPanel.AddLabelMedium(text=deltaText, colSpan=tooltipPanel.columns)

    def GetOrderDelta(self):
        totalPrice = sum((i.GetTotalSum() for i in self.GetItemsIterator(onlyValid=True)))
        change = 0
        for item in self.GetItemsIterator(onlyValid=True):
            price = item.GetTotalSum()
            qty = item.GetTotalQty()
            avgPriceForQty = qty * item.averagePrice
            change += (price - avgPriceForQty) / avgPriceForQty * price / totalPrice

        return change

    def GetOrderDeltaText(self):
        percentage = self.GetOrderDelta()
        if percentage == 0:
            return ''
        if percentage < 0:
            percColor = self.belowColor
            devLabelPath = 'UI/Market/MarketQuote/BelowRegionalAverageWithPercentage'
        else:
            percColor = self.aboveColor
            devLabelPath = 'UI/Market/MarketQuote/AboveRegionalAverageWithPercentage'
        percentage = abs(percentage)
        percentageText = FmtAmt(percentage * 100, showFraction=1)
        percText = '%s%s</color>' % (percColor, GetByLabel('UI/Common/Percentage', percentage=percentageText))
        return GetByLabel(devLabelPath, percentage=percText)

    def GetNumTypesAndNumAvailableTypes(self):
        numTypes = 0
        numAvailableTypes = 0
        for item in self.GetItemsIterator():
            numTypes += 1
            if item.GetPrice():
                numAvailableTypes += 1

        return (numTypes, numAvailableTypes)

    def GetItemsIterator(self, onlyValid = False):
        for item in self.GetItems():
            if not item:
                continue
            if onlyValid and not self.GetValidatedItem(item):
                continue
            yield item

    def DropItems(self, dragObj, nodes):
        if dragObj is None:
            return
        items = self.CheckOrderAvailability(nodes)
        self.ClearErrorLists()
        for node in items:
            typeID = GetTypeIDFromDragItem(node)
            if typeID:
                self.AddItem(KeyVal(typeID=typeID, qty=1))

        self.DisplayErrorHints()

    def GetTypeIDFromDragItem(self, node):
        return GetTypeIDFromDragItem(node)

    def OnStationChanged(self, combo, key, value):
        self.baseStationID = value
        self.UpdateStationID()

    def UpdateStationID(self):
        for item in self.GetItemsIterator():
            item.UpdateStationID(self.baseStationID)

        self.UpdateHeaderCount()
        self.UpdateNumbers()

    def OnOwnOrdersChanged(self, orders, reason, isCorp):
        if reason != 'Expiry':
            return
        failedItems = []
        for eachOrder in orders:
            if eachOrder.orderID not in self.activeOrders:
                continue
            if eachOrder.volRemaining != 0:
                failedBuyInfo = KeyVal(typeID=eachOrder.typeID, qty=eachOrder.volRemaining)
                failedItems.append(failedBuyInfo)
            self.activeOrders.discard(eachOrder.orderID)

        if failedItems:
            self.AddPreItems(failedItems)
        if not failedItems and not self.AreStillItemsInWindow():
            self.Close()
            return
        if self.orderDisabled and not self.activeOrders:
            self.ChangeOrderUIState(disable=False)

    def AreStillItemsInWindow(self):
        if self.activeOrders:
            return True
        if self.reloadingItemsCounter > 0:
            return True
        if self.itemList:
            return True
        return False

    def RemoveAllItem(self):
        self.itemsScroll.Flush()
        self.itemList = []
        self.entriesInScrollByTypeID = {}
        self.UpdateNumbers()
        self.UpdateHeaderCount()
        self.ClearErrorLists()

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid2' in change or 'stationid2' in change:
            self.LoadStationOptions()

    def IsBuyable(self, itemKeyVal):
        buyable = True
        if evetypes.GetMarketGroupID(itemKeyVal.typeID) is None:
            self.cannotTradeItemList.append(itemKeyVal)
            buyable = False
        return buyable

    def BlinkNumOrdersEdit(self):
        self.ConstructBlinkBG()
        uicore.animations.FadeTo(self.blinkEditBG, 0.0, 0.5, duration=0.5, curveType=uiconst.ANIM_WAVE, loops=2)

    def ConstructBlinkBG(self):
        if self.blinkEditBG is None:
            self.blinkEditBG = Sprite(name='blinkEditBG', bgParent=self.orderMultiplierEdit, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgSelected.png', opacity=0.0, idx=0)

    def LogBuy(self, buyItemList):
        totalDisplayed = self.totalAmt.text
        totalSum = self.GetSum()
        multiplier = self.orderMultiplierEdit.GetValue()
        buyTextList = []
        for eachItem in buyItemList:
            text = '[typeID=%s, price=%s, qty=%s]' % (eachItem.typeID, eachItem.price, eachItem.quantity)
            buyTextList.append(text)

        buyText = ','.join(buyTextList)
        logInfo = 'Multibuy: totalDisplayed=%s, totalSum=%s, multiplier=%s, buyText=%s' % (totalDisplayed,
         totalSum,
         multiplier,
         buyText)
        log.LogNotice(logInfo)

    def Close(self, *args, **kwds):
        self.verifyMultiplierTimer = None
        return SellBuyItemsWindow.Close(self, *args, **kwds)
