#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\buySellMultiBase.py
import math
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelMedium, EveLabelMediumBold, EveLabelLargeBold
from eve.client.script.ui.control.eveWindow import Window
from eve.common.lib.appConst import corpRoleAccountant, corpRoleTrader
import evetypes
from localization import GetByLabel
import uthread
COL_GREEN = (0.3, 0.9, 0.1)
COL_RED = (1.0, 0.275, 0.0)

class SellBuyItemsWindow(Window):
    __notifyevents__ = ['OnSessionChanged']
    default_width = 520
    default_height = 280
    default_minSize = (default_width, default_height)
    default_windowID = 'SellBuyItemsWindow'
    captionTextPath = 'UI/Inventory/ItemActions/MultiBuy'
    scrollId = 'MultiBuyScroll'
    tradeForCorpSettingConfig = 'buyUseCorp'
    tradeTextPath = 'UI/Market/MarketQuote/CommandSell'
    orderCap = 'MultiSellOrderCap'
    tradeOnConfirm = True
    MAX_PRICE = 9223372036854.0
    corpCheckboxTop = 28
    numbersGridTop = 6
    showTaxAndBrokersFee = True
    dropLabelPath = 'UI/Market/Marketbase/DropItemsToAdd'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.marketQuoteSvc = sm.GetService('marketQuote')
        self.InitializeVariables(attributes)
        self.SetCaption(GetByLabel(self.captionTextPath))
        self.scope = 'station_inflight'
        self.SetTopparentHeight(0)
        mainCont = Container(parent=self.sr.main, name='mainCont', padding=4)
        self.infoCont = Container(parent=mainCont, name='bottomCont', align=uiconst.TOBOTTOM, height=88, padTop=4)
        Line(parent=self.infoCont, align=uiconst.TOTOP)
        self.bottomLeft = Container(parent=self.infoCont, name='bottomLeft', padLeft=6, padTop=6)
        self.bottomRight = Container(parent=self.infoCont, name='bottomRight', align=uiconst.TORIGHT, width=250, padRight=6, padTop=6)
        self.dropCont = Container(parent=mainCont, name='dropCont', align=uiconst.TOTOP, height=28, state=uiconst.UI_NORMAL, padBottom=4)
        self.dropLabel = EveCaptionSmall(text=GetByLabel(self.dropLabelPath), parent=self.dropCont, align=uiconst.CENTER)
        self.dropLabel.opacity = 0.6
        self.fakeItemsCont = Container(parent=self.dropCont, align=uiconst.TOALL, clipChildren=True)
        self.locationCont = Container(parent=mainCont, name='locationCont', align=uiconst.TOTOP)
        scrollCont = Container(parent=mainCont, name='scrollCont')
        self.itemsScroll = ScrollContainer(parent=scrollCont, id=self.scrollId)
        btnGroup = ButtonGroup(parent=self.sr.main, idx=0, line=False)
        btnGroup.AddButton(GetByLabel(self.tradeTextPath), self.PerformTrade, isDefault=self.tradeOnConfirm)
        btnGroup.AddButton(GetByLabel('UI/Generic/Cancel'), self.Cancel)
        self.DrawNumbers()
        corpAcctName = self._CanTradeForCorp()
        if corpAcctName is not None:
            self.DrawCheckBox(corpAcctName)
        self.globalDragHover = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)

    def StartAddItemsThread(self):
        if len(self.preItems):
            self.addItemsThread = uthread.new(self.AddPreItems, self.preItems)

    def InitializeVariables(self, attributes):
        self.globalDragHover = None
        self.cannotTradeItemList = []
        self.itemList = []
        self.preItems = attributes.preItems or []
        self.useCorp = None
        self.hasDrawn = False
        self.addItemsThread = None
        self.baseStationID = None

    def DrawNumbers(self):
        self.numbersGrid = LayoutGrid(parent=self.bottomRight, columns=2, align=uiconst.TORIGHT, top=self.numbersGridTop)
        if self.showTaxAndBrokersFee:
            self.brokersFee = EveLabelMedium(text='', padRight=4)
            self.numbersGrid.AddCell(self.brokersFee)
            self.brokersFeeAmt = EveLabelMediumBold(text='', align=uiconst.CENTERRIGHT, padLeft=4)
            self.numbersGrid.AddCell(self.brokersFeeAmt)
            self.salesTax = EveLabelMedium(text='', padRight=4)
            self.numbersGrid.AddCell(self.salesTax)
            self.salesTaxAmt = EveLabelMediumBold(text='', align=uiconst.CENTERRIGHT, padLeft=4)
            self.numbersGrid.AddCell(self.salesTaxAmt)
            spacer = Container(align=uiconst.TOTOP, height=12)
            self.numbersGrid.AddCell(spacer, colSpan=2)
        self.totalAmt = EveLabelLargeBold(text='', align=uiconst.CENTERRIGHT, padLeft=4, state=uiconst.UI_NORMAL)
        self.numbersGrid.AddCell(self.totalAmt, colSpan=2)

    def DrawCheckBox(self, corpAcctName):
        useCorpWallet = settings.user.ui.Get(self.tradeForCorpSettingConfig, False)
        top = self.corpCheckboxTop
        self.useCorp = Checkbox(text=GetByLabel('UI/Market/MarketQuote/UseCorpAccount', accountName=corpAcctName), parent=self.bottomLeft, configName='usecorp', checked=useCorpWallet, callback=self.OnUseCorp, pos=(0,
         top,
         350,
         0), align=uiconst.TOPLEFT)

    def _CanTradeForCorp(self):
        if session.corprole & (corpRoleAccountant | corpRoleTrader):
            corpAcctName = sm.GetService('corp').GetMyCorpAccountName()
            if corpAcctName is not None:
                return corpAcctName

    def OnUseCorp(self, *args):
        if self.useCorp.checked:
            newValue = True
        else:
            newValue = False
        settings.user.ui.Set(self.tradeForCorpSettingConfig, newValue)

    def TradingForCorp(self):
        if self.useCorp:
            useCorp = self.useCorp.checked
        else:
            useCorp = False
        return useCorp

    def DropItems(self, dragObj, nodes):
        pass

    def PerformTrade(self, *args):
        pass

    def UpdateNumbers(self):
        pass

    def GetItems(self):
        return self.itemList

    def AddPreItems(self, preItems):
        pass

    def IsAllowedGuid(self, guid):
        return True

    def DrawDraggedItems(self, dragData):
        if not self.IsAllowedGuid(getattr(dragData[0], '__guid__', None)):
            return
        self.hasDrawn = True
        uicore.animations.FadeOut(self.dropLabel, duration=0.15)
        noOfItems = len(dragData)
        noOfAvailable = math.floor((self.width - 16) / 28)
        for i, dragItem in enumerate(dragData):
            c = Container(parent=self.fakeItemsCont, align=uiconst.TOLEFT, padding=2, width=24)
            if noOfItems > noOfAvailable and i == noOfAvailable - 1:
                icon = Sprite(parent=c, texturePath='res:/UI/Texture/classes/MultiSell/DotDotDot.png', state=uiconst.UI_DISABLED, width=24, height=24, align=uiconst.CENTER)
                icon.SetAlpha(0.6)
                return
            typeID = self.GetTypeIDFromDragItem(dragItem)
            icon = Icon(parent=c, typeID=typeID, state=uiconst.UI_DISABLED)
            icon.SetSize(24, 24)

    def GetTypeIDFromDragItem(self, dragItem):
        getTypeID = dragItem.item.typeID
        return getTypeID

    def OnDropData(self, dragSource, dragData):
        self.ClearDragData()

    def ClearDragData(self):
        self.fakeItemsCont.Flush()
        uicore.animations.FadeIn(self.dropLabel, 0.6, duration=0.3)
        self.hasDrawn = False

    def OnGlobalMouseHover(self, *args, **kw):
        shouldClearDragData = True
        if uicore.IsDragging() and uicore.dragObject:
            mo = uicore.uilib.mouseOver
            if mo == self or mo.IsUnder(self):
                shouldClearDragData = False
                if not self.hasDrawn:
                    self.DrawDraggedItems(uicore.dragObject.dragData)
        if shouldClearDragData:
            self.ClearDragData()
        return True

    def Cancel(self, *args):
        self.Close()

    def Close(self, *args, **kwds):
        Window.Close(self, *args, **kwds)
        if self.addItemsThread:
            self.addItemsThread.kill()
        uicore.event.UnregisterForTriuiEvents(self.globalDragHover)

    def CheckOrderAvailability(self, preItems):
        availableOrders = int(sm.GetService('machoNet').GetGlobalConfig().get(self.orderCap, 100)) - len(self.itemList)
        if len(preItems) > availableOrders:
            eve.Message('CustomNotify', {'notify': GetByLabel('UI/Market/MarketQuote/TooManyItemsForOrder')})
            return preItems[:availableOrders]
        return preItems

    def RemoveItem(self, itemEntry):
        self.itemsScroll._RemoveChild(itemEntry)
        self.itemList.remove(itemEntry)
        self.RemoveItemFromCollection(itemEntry)
        self.UpdateNumbers()
        self.UpdateHeaderCount()

    def RemoveItemFromCollection(self, itemEntry):
        pass

    def DoAddItem(self, item):
        itemEntry = self.GetItemEntry(item)
        self.AddItemToCollection(item, itemEntry)
        itemEntry.state = uiconst.UI_NORMAL
        self.itemsScroll._InsertChild(0, itemEntry)
        self.itemList.append(itemEntry)
        self.UpdateNumbers()
        self.UpdateHeaderCount()
        return itemEntry

    def UpdateHeaderCount(self):
        self.SetCaption('%s (%i) - %s' % (GetByLabel(self.captionTextPath), len(self.itemList), self.GetStationLocationText()))

    def GetStationLocationText(self):
        if self.baseStationID is None:
            return ''
        stationLocation = cfg.evelocations.Get(self.baseStationID).locationName
        return stationLocation

    def DisplayErrorHints(self):
        hintTextList = self.GetErrorHints()
        if hintTextList:
            hintText = '<br>'.join(hintTextList)
            eve.Message('CustomNotify', {'notify': hintText})

    def GetErrorHints(self):
        hintTextList = self.BuildHintTextList(self.cannotTradeItemList, 'UI/Market/MarketQuote/CannotBeSold')
        return hintTextList

    def BuildHintTextList(self, itemList, labelPath):
        hintTextList = []
        if len(itemList):
            text = '<b>%s</b>' % GetByLabel(labelPath)
            hintTextList.append(text)
            for item in itemList:
                hintTextList.append(evetypes.GetName(item.typeID))

        return hintTextList

    def ClearErrorLists(self):
        self.cannotTradeItemList = []
