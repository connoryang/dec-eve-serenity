#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\buytItemEntry.py
from carbon.common.script.util.format import FmtAmt
from carbon.common.script.util.linkUtil import GetShowInfoLink
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, Label
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.market.buySellItemContainerBase import BuySellItemContainerBase
from eve.client.script.ui.shared.market.deltaContainer import BuyDeltaContainer
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.lib.appConst import rangeStation, rangeRegion, rangeSolarSystem
from eve.common.script.util.eveFormat import FmtISK
import evetypes
from localization import GetByLabel
NA_CHAR = '-'

class BuyItemContainer(BuySellItemContainerBase):
    __guid__ = 'uicls.BuytemContainer'
    default_height = 52
    belowColor = '<color=0xff00ff00>'
    aboveColor = '<color=0xffff5050>'
    totaLabelPath = 'UI/Market/MarketQuote/PayTotal'

    def ApplyAttributes(self, attributes):
        self.blinkBG = None
        self.typeID = attributes.typeID
        self.dropParentFunc = attributes.dropParentFunc
        BuySellItemContainerBase.ApplyAttributes(self, attributes)
        self.adjustQtyTimer = None
        self.isUpdating = False
        self.totalSum = 0.0
        self.orderMultiplier = attributes.orderMultiplier
        self.qty = attributes.qty
        self.stationID = attributes.stationID
        self.newBestPrice, self.numOrders = self.quoteSvc.GetBestAskPriceInStationAndNumberOrders(self.typeID, self.stationID, self.qty)
        self.DrawUI()
        self.UpdateUIElements()
        self.GetBestPrice()

    def DrawUI(self):
        self.errorBg = ErrorFrame(bgParent=self)
        self.deltaCont = Container(parent=self, align=uiconst.TORIGHT, width=30)
        theRestCont = Container(parent=self, align=uiconst.TOALL)
        self.totalCont = Container(parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.3)
        self.priceCont = Container(parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.22)
        self.qtyCont = Container(parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.15)
        self.itemCont = Container(parent=theRestCont, align=uiconst.TORIGHT_PROP, width=0.33)
        self.deleteCont = Container(parent=self.itemCont, align=uiconst.TORIGHT, width=24)
        self.deleteButton = ButtonIcon(texturePath='res:/UI/Texture/Icons/73_16_210.png', pos=(0, 0, 16, 16), align=uiconst.CENTERRIGHT, parent=self.deleteCont, hint=GetByLabel('UI/Generic/RemoveItem'), idx=0, func=self.RemoveItem)
        self.deleteCont.display = False
        self.textCont = Container(parent=self.itemCont, align=uiconst.TOALL)
        self.DrawItem()
        self.DrawQty()
        self.DrawPrice()
        self.DrawTotal()
        self.DrawDelta()

    def UpdateUIElements(self):
        self.UpdateOrderStateInUI()
        self.GetBestPrice()
        self.SetPrice()
        self.UpdateDelta()

    def GetBestOrderInRange(self):
        stationID = self.stationID
        bidRange = None
        return self.quoteSvc.GetBestAskInRange(typeID=self.typeID, stationID=stationID, bidRange=bidRange, amount=self.qty)

    def ShowNoSellOrders(self):
        if self.newBestPrice is None:
            uicore.animations.FadeIn(self.errorBg, 0.35, duration=0.3)

    def DrawQty(self):
        self.qtySubCont = ContainerAutoSize(name='qtySubCont', parent=self.qtyCont, align=uiconst.TOTOP, callback=self.PositionQtyContainer)
        qty = self.qty
        self.qtyEdit = SinglelineEdit(name='qtyEdit', parent=self.qtySubCont, align=uiconst.TOTOP, padLeft=4, ints=[1, None], setvalue=qty, OnChange=self.OnChange, hint=GetByLabel('UI/Common/Quantity'))
        self.qtyEdit.OnMouseWheel = self.OnMouseWheelForQtyEdit
        self.qtyTotal = EveLabelMediumBold(text='', parent=self.qtySubCont, padLeft=8, padTop=6, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, autoFadeSides=35)
        self.SetTotalQtyText()

    def OnMouseWheelForQtyEdit(self, *args):
        if uicore.registry.GetFocus() != self.qtyEdit:
            return
        SinglelineEdit.MouseWheel(self.qtyEdit, *args)

    def PositionQtyContainer(self):
        subContTop = self.height / 2.0 - self.qtySubCont.GetAutoSize()[1] / 2.0
        self.qtySubCont.top = int(subContTop)

    def DrawPrice(self):
        self.priceLabel = EveLabelMediumBold(name='priceLabel', text='', parent=self.priceCont, left=4, align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)

    def DrawDelta(self):
        self.deltaContainer = BuyDeltaContainer(parent=self.deltaCont, delta=self.GetDelta(), func=self.OpenMarket, align=uiconst.CENTERRIGHT)
        self.deltaContainer.LoadTooltipPanel = self.LoadDeltaTooltip

    def DrawItem(self):
        iconCont = Container(name='iconCont', parent=self.textCont, align=uiconst.TOLEFT, width=32, padding=4)
        iconInnerCont = Container(name='iconInnerCont', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 32, 32))
        self.wheel = LoadingWheel(parent=iconCont, pos=(0, 0, 48, 48), align=uiconst.CENTER)
        self.wheel.display = False
        self.techIcon = Sprite(parent=iconInnerCont, pos=(0, 0, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        GetTechLevelIcon(self.techIcon, 1, self.typeID)
        self.icon = Icon(parent=iconInnerCont, typeID=self.typeID, state=uiconst.UI_DISABLED, align=uiconst.CENTER)
        self.icon.SetSize(32, 32)
        itemName = GetShowInfoLink(typeID=self.typeID, text=evetypes.GetName(self.typeID))
        self.itemNameLabel = Label(text=itemName, parent=self.textCont, left=40, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, autoFadeSides=35, fontsize=12)

    def SetPrice(self):
        self.priceLabel.text = self.GetPriceText()

    def GetPriceText(self):
        if self.newBestPrice:
            return FmtISK(self.newBestPrice)
        else:
            return NA_CHAR

    def GetBestPrice(self):
        totalQty = self.qty * self.orderMultiplier
        self.newBestPrice, self.numOrders = self.quoteSvc.GetBestAskPriceInStationAndNumberOrders(self.typeID, self.stationID, totalQty)
        self.UpdateOrderStateInUI()

    def UpdateOrderStateInUI(self):
        if self.newBestPrice:
            self.HideNoSellOrders()
        else:
            self.ShowNoSellOrders()

    def GetTotalSum(self):
        price = self.GetPrice() or 0
        totalQty = self.GetQty() * self.orderMultiplier
        self.totalSum = price * totalQty
        self.SetTotalText(self.totalSum)
        return self.totalSum

    def SetTotalText(self, totalSum):
        if totalSum:
            self.totalLabel.text = FmtISK(totalSum)
        else:
            self.totalLabel.text = NA_CHAR

    def UpdateOrderMultiplier(self, multiplier):
        self.orderMultiplier = multiplier
        self.OnChange()

    def UpdateStationID(self, stationID):
        self.stationID = stationID
        self.UpdateUIElements()

    def OnChange(self, *args):
        if self.adjustQtyTimer:
            self.adjustQtyTimer.KillTimer()
        self.adjustQtyTimer = AutoTimer(1000, self.AdjustQty_thread, *args)
        self.SetItemLoading()

    def SetItemLoading(self):
        self.wheel.display = True
        self.qtyTotal.text = ''
        self.totalLabel.text = ''
        self.priceLabel.text = NA_CHAR
        self.deltaContainer.display = False
        self.totalLabel.text = NA_CHAR
        self.isUpdating = True

    def AdjustQty_thread(self, *args):
        self.adjustQtyTimer = None
        if self.destroyed:
            return
        self.qty = self.GetQty()
        self.SetTotalQtyText()
        self.GetBestPrice()
        self.SetPrice()
        self.deltaContainer.display = True
        self.UpdateDelta()
        self.GetTotalSum()
        self.wheel.display = False
        self.isUpdating = False
        if self.parentEditFunc:
            self.parentEditFunc(args)

    def SetTotalQtyText(self):
        totalQty = self.GetTotalQty()
        if totalQty is None:
            self.qtyTotal.text = ''
            self.qtyTotal.hint = ''
        elif self.orderMultiplier > 1:
            self.qtyTotal.display = True
            self.qtyTotal.text = '= %s' % FmtAmt(totalQty)
            self.qtyTotal.hint = GetByLabel('UI/Market/MarketQuote/TotalAmountToBuy', numOrders=self.orderMultiplier, qty=self.GetQty())
        else:
            self.qtyTotal.display = False

    def GetPrice(self):
        return self.newBestPrice

    def GetQty(self):
        qty = self.qtyEdit.GetValue()
        return qty

    def GetTotalQty(self):
        qty = self.GetQty()
        return self.orderMultiplier * qty

    def GetTradeWndClass(self):
        from eve.client.script.ui.shared.market.buyMultiFromBase import MultiBuy
        return MultiBuy

    def GetDiffFromAvgText(self):
        return '%s %s' % (GetByLabel('UI/Market/MarketQuote/RegionalAdverage'), self.GetDeltaText())

    def LoadDeltaTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Market/Marketbase/PricePerUnit'))
        tooltipPanel.AddLabelLarge(text=self.GetPriceText(), align=uiconst.CENTERRIGHT)
        bestMatchDetails = tooltipPanel.AddLabelSmall(text='', align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text=self.GetDiffFromAvgText(), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=FmtISK(self.averagePrice), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/BestInStation'))
        stationBestPrice = self.GetBestMatchText(rangeStation)
        tooltipPanel.AddLabelMedium(text=stationBestPrice, align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/BestInSystem'))
        stationBestPrice = self.GetBestMatchText(rangeSolarSystem)
        tooltipPanel.AddLabelMedium(text=stationBestPrice, align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/BestRegional'))
        regBestPrice = self.GetBestMatchText(rangeRegion)
        tooltipPanel.AddLabelMedium(text=regBestPrice, align=uiconst.CENTERRIGHT)
        if not self.newBestPrice:
            bestMatchDetails.text = GetByLabel('UI/Market/MarketQuote/NoMatchForOrder')
            bestMatchDetails.color = (1.0, 0.275, 0.0, 1.0)
        else:
            bestMatchDetails.text = GetByLabel('UI/Market/MarketQuote/FromNumberOfOrders', numOrders=self.numOrders)
            bestMatchDetails.SetAlpha(0.6)

    def GetBestMatchText(self, orderRange):
        bestOrder = self.quoteSvc.GetBestAskInRange(self.typeID, self.stationID, orderRange)
        if bestOrder:
            return FmtISK(bestOrder.price)
        return NA_CHAR

    def AddQtyToEntry(self, extraQty):
        self.Blink()
        qty = self.qtyEdit.GetValue()
        newQty = extraQty + qty
        self.qtyEdit.SetValue(newQty)

    def Blink(self):
        self.ConstructBlinkBG()
        uicore.animations.FadeTo(self.blinkBG, 0.0, 0.25, duration=0.25, curveType=uiconst.ANIM_WAVE, loops=2)

    def ConstructBlinkBG(self):
        if self.blinkBG is None:
            self.blinkBG = Sprite(name='blinkBg', bgParent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/InvItem/bgSelected.png', opacity=0.0, idx=0)

    def OnDropData(self, dragSource, dragData):
        if self.dropParentFunc:
            self.dropParentFunc(dragSource, dragData)
