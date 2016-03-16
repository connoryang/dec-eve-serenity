#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\sellItemEntry.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.market.buySellItemContainerBase import BuySellItemContainerBase
from eve.client.script.ui.shared.market.deltaContainer import SellDeltaContainer
from eve.client.script.ui.util.uix import GetTechLevelIcon
from eve.common.script.util.eveFormat import FmtISK
import evetypes
from localization import GetByLabel

class SellItemContainer(BuySellItemContainerBase):
    __guid__ = 'uicls.SellItemContainer'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'
    totaLabelPath = 'UI/Market/MarketQuote/AskTotal'

    def ApplyAttributes(self, attributes):
        self.item = attributes.item
        self.typeID = self.item.typeID
        BuySellItemContainerBase.ApplyAttributes(self, attributes)
        self.singleton = self.item.singleton
        self.itemID = self.item.itemID
        self.itemName = evetypes.GetName(self.typeID)
        self.brokersFee = 0.0
        self.salesTax = 0.0
        self.totalSum = 0.0
        self.limits = self.quoteSvc.GetSkillLimits()
        self.stationID, officeFolderID, officeID = sm.GetService('invCache').GetStationIDOfficeFolderIDOfficeIDOfItem(self.item)
        self.located = None
        if officeFolderID is not None:
            self.located = [officeFolderID, officeID]
        station = sm.GetService('ui').GetStation(self.stationID)
        self.solarSystemID = station.solarSystemID
        self.regionID = self.GetRegionID(self.stationID)
        self.bestBid = self.quoteSvc.GetBestBid(self.typeID, locationID=self.solarSystemID)
        self.GetBestPrice()
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
        self.errorBg = ErrorFrame(bgParent=self)
        self.DrawItem()
        self.DrawQty()
        self.DrawPrice()
        self.DrawTotal()
        self.DrawDelta()
        self.GetTotalSum()
        self.GetBrokersFee()
        self.GetSalesTax()
        self.ShowNoSellOrders()

    def GetRegionID(self, stationID):
        regionID = cfg.evelocations.Get(stationID).Station().regionID
        return regionID

    def ShowNoSellOrders(self):
        from eve.client.script.ui.shared.market.sellMulti import SellItems
        wnd = SellItems.GetIfOpen()
        if not wnd:
            return
        if wnd.durationCombo.GetValue() == 0 and self.bestBid is None:
            uicore.animations.FadeIn(self.errorBg, 0.35, duration=0.3)

    def DrawQty(self):
        qty = self.item.stacksize
        self.qtyEdit = SinglelineEdit(name='qtyEdit', parent=self.qtyCont, align=uiconst.TOTOP, top=11, padLeft=4)
        self.qtyEdit.IntMode(*(1, long(qty)))
        self.qtyEdit.SetValue(qty)
        self.qtyEdit.OnChange = self.OnChange
        self.qtyEdit.hint = GetByLabel('UI/Common/Quantity')

    def DrawPrice(self):
        self.priceEdit = SinglelineEdit(name='priceEdit', parent=self.priceCont, align=uiconst.TOTOP, top=11, padLeft=8)
        self.priceEdit.FloatMode(*(0.01, 9223372036854.0, 2))
        self.priceEdit.SetValue(self.bestPrice)
        self.priceEdit.OnChange = self.OnChange
        self.priceEdit.hint = GetByLabel('UI/Market/MarketQuote/AskPrice')

    def DrawDelta(self):
        self.deltaContainer = SellDeltaContainer(parent=self.deltaCont, delta=self.GetDelta(), func=self.OpenMarket, align=uiconst.CENTERRIGHT)
        self.deltaContainer.LoadTooltipPanel = self.LoadDeltaTooltip
        self.UpdateDelta()

    def GetTradeWndClass(self):
        from eve.client.script.ui.shared.market.sellMulti import SellItems
        return SellItems

    def LoadDeltaTooltip(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelLarge(text=GetByLabel('UI/Market/MarketQuote/AskPrice'))
        tooltipPanel.AddLabelLarge(text=FmtISK(self.priceEdit.GetValue()), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddSpacer(1, 8, colSpan=tooltipPanel.columns)
        tooltipPanel.AddLabelMedium(text='%s %s' % (GetByLabel('UI/Market/MarketQuote/RegionalAdverage'), self.GetDeltaText()))
        tooltipPanel.AddLabelMedium(text=FmtISK(self.averagePrice), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Market/MarketQuote/BestRegional'))
        bestMatch = tooltipPanel.AddLabelMedium(text='', align=uiconst.CENTERRIGHT)
        bestMatchDetails = tooltipPanel.AddLabelSmall(text='', align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
        if not self.bestBid:
            bestMatch.text = GetByLabel('UI/Contracts/ContractEntry/NoBids')
            bestMatchDetails.text = GetByLabel('UI/Market/MarketQuote/ImmediateWillFail')
            bestMatch.color = (1.0, 0.275, 0.0, 1.0)
            bestMatchDetails.color = (1.0, 0.275, 0.0, 1.0)
        else:
            bestMatch.text = FmtISK(self.bestBid.price)
            bestMatchText, volRemaining = self.GetBestMatchText()
            bestMatchDetails.text = bestMatchText
            bestMatchDetails.SetAlpha(0.6)
            if volRemaining:
                vol = tooltipPanel.AddLabelSmall(text=volRemaining, align=uiconst.CENTERRIGHT, colSpan=tooltipPanel.columns)
                vol.SetAlpha(0.6)

    def GetBestMatchText(self):
        jumps = max(self.bestBid.jumps - max(0, self.bestBid.range), 0)
        minVolumeText = None
        if jumps == 0 and self.stationID == self.bestBid.stationID:
            jumpText = GetByLabel('UI/Market/MarketQuote/ItemsInSameStation')
        else:
            jumpText = GetByLabel('UI/Market/MarketQuote/JumpsFromThisSystem', jumps=jumps)
        if self.bestBid.minVolume > 1 and self.bestBid.volRemaining >= self.bestBid.minVolume:
            minVolumeText = GetByLabel('UI/Market/MarketQuote/SimpleMinimumVolume', min=self.bestBid.minVolume)
        return (GetByLabel('UI/Market/MarketQuote/SellQuantity', volRemaining=long(self.bestBid.volRemaining), jumpText=jumpText), minVolumeText)

    def DrawItem(self):
        iconCont = Container(parent=self.textCont, align=uiconst.TOLEFT, width=32, padding=4)
        self.iconInnerCont = Container(name='iconInnerCont', parent=iconCont, align=uiconst.CENTERLEFT, pos=(0, 0, 32, 32))
        self.techIcon = Sprite(parent=self.iconInnerCont, pos=(0, 0, 16, 16), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL)
        self.icon = Icon(parent=self.iconInnerCont, typeID=self.typeID, state=uiconst.UI_DISABLED, ignoreSize=True, pos=(0, 0, 32, 32))
        GetTechLevelIcon(self.techIcon, 1, self.typeID)
        itemName = GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=self.itemName, info=('showinfo', self.typeID, self.item.itemID))
        self.itemNameLabel = Label(text=itemName, parent=self.textCont, left=40, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, autoFadeSides=35, fontsize=12)

    def GetBestPrice(self):
        bestMatchableBid = self.quoteSvc.GetBestMatchableBid(self.typeID, self.stationID, self.item.stacksize)
        if bestMatchableBid:
            self.bestPrice = bestMatchableBid.price
        else:
            self.bestPrice = self.averagePrice

    def GetBrokersFee(self):
        fee = self.quoteSvc.BrokersFee(self.stationID, self.totalSum, self.limits['fee'])
        feeAmount = fee.amt
        self.brokersFee = feeAmount

    def GetSalesTax(self):
        tax = self.totalSum * self.limits['acc']
        self.salesTax = tax

    def GetTotalSum(self):
        price = self.GetPrice()
        qty = self.GetQty()
        self.totalSum = price * qty
        self.totalLabel.text = FmtISK(self.totalSum)
        return self.totalSum

    def OnChange(self, *args):
        self.GetTotalSum()
        self.GetBrokersFee()
        self.GetSalesTax()
        self.UpdateDelta()
        if self.parentEditFunc:
            self.parentEditFunc(args)

    def GetPrice(self):
        price = self.priceEdit.GetValue()
        return price

    def GetQty(self):
        qty = self.qtyEdit.GetValue()
        return qty

    def GetSellCountEstimate(self):
        return self.quoteSvc.GetSellCountEstimate(self.typeID, self.stationID, self.GetPrice(), self.GetQty())

    def MakeSingle(self):
        self.height = 80
        self.qtyCont.width = 0
        self.itemCont.width = 0.42
        self.totalCont.width = 0.36
        self.itemNameLabel.fontsize = 14
        self.totalLabel.fontsize = 14
        self.itemNameLabel.left = 72
        self.icon.SetSize(64, 64)
        self.iconInnerCont.SetSize(64, 64)
        self.priceEdit.padLeft = 4
        self.priceEdit.align = uiconst.TOBOTTOM
        self.qtyEdit.top = 20
        self.priceEdit.top = 20
        self.qtyEdit.SetParent(self.priceCont)

    def RemoveSingle(self):
        self.height = 40
        self.qtyCont.width = 0.15
        self.itemCont.width = 0.33
        self.totalCont.width = 0.3
        self.itemNameLabel.fontsize = 12
        self.totalLabel.fontsize = 12
        self.itemNameLabel.left = 40
        self.icon.SetSize(32, 32)
        self.iconInnerCont.SetSize(32, 32)
        self.priceEdit.align = uiconst.TOTOP
        self.qtyEdit.top = 11
        self.priceEdit.top = 11
        self.priceEdit.padLeft = 8
        self.qtyEdit.SetParent(self.qtyCont)
