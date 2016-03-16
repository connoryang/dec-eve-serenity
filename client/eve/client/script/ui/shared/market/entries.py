#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\entries.py
from carbonui import const as uiconst
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.fitting.ghostFittingHelpers import TryGhostFitItemOnMouseAction
import localization
from marketutil.quickbarUtil import GetTypesUnderFolder
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
from util import Color
import evetypes

class MarketOrder(listentry.Generic):
    __guid__ = 'listentry.MarketOrder'

    def Startup(self, *args):
        listentry.Generic.Startup(self, args)
        self.sr.green = None

    def Load(self, node):
        listentry.Generic.Load(self, node)
        data = self.sr.node
        if data.inMyPath:
            self.sr.label.color = Color.YELLOW
        if data.markAsMine:
            self.ShowBackground(color=Color.BLUE)
        elif data.flag == 1 and data.mode == 'sell':
            self.ShowBackground(color=(0.0, 1.0, 0.0))
        elif self.sr.green:
            self.sr.bgFill.state = uiconst.UI_HIDDEN

    def ShowBackground(self, color, *args):
        if self.sr.bgFill is None:
            self.sr.bgFill = Fill(bgParent=self, color=(1.0, 1.0, 1.0, 0.25), state=uiconst.UI_DISABLED)
        self.sr.bgFill.color.SetRGB(a=0.25, *color[:3])
        self.sr.bgFill.state = uiconst.UI_DISABLED

    def Buy(self, node = None, ignoreAdvanced = False, *args):
        if not hasattr(self, 'sr'):
            return
        node = node if node is not None else self.sr.node
        sm.GetService('marketutils').Buy(self.sr.node.order.typeID, node.order, 0, ignoreAdvanced=ignoreAdvanced)

    def ShowInfo(self, node = None, *args):
        node = node if node is not None else self.sr.node
        sm.GetService('info').ShowInfo(node.order.typeID)

    def GetMenu(self):
        self.OnClick()
        m = []
        if self.sr.node.mode == 'buy':
            m.append((MenuLabel('UI/Market/Marketbase/BuyThis'), self.Buy, (self.sr.node, True)))
        m.append(None)
        m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo, (self.sr.node,))]
        stationID = self.sr.node.order.stationID
        if stationID:
            stationInfo = sm.GetService('ui').GetStation(stationID)
            m += [(MenuLabel('UI/Common/Location'), sm.GetService('menu').CelestialMenu(stationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID, mapItem=None))]
        if self.sr.node.markAsMine:
            m.append((MenuLabel('UI/Market/Orders/ModifyOrder'), self.ModifyPrice, (self.sr.node,)))
            m.append((MenuLabel('UI/Market/Orders/CancelOrder'), self.CancelOffer, (self.sr.node,)))
        return m

    def OnDblClick(self, *args):
        self.Buy(ignoreAdvanced=True)

    def ModifyPrice(self, node):
        sm.GetService('marketutils').ModifyOrder(node.order)

    def CancelOffer(self, node):
        sm.GetService('marketutils').CancelOffer(node.order)


class GenericMarketItem(listentry.Generic):
    __guid__ = 'listentry.GenericMarketItem'
    isDragObject = True

    def Startup(self, *args):
        listentry.Generic.Startup(self, *args)

    def Load(self, node):
        listentry.Generic.Load(self, node)
        if not node.get('inRange', True):
            self.SetOpacity(0.5)
            self.hint = localization.GetByLabel('UI/Market/Marketbase/NotAvailableInRange')

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def OnMouseEnter(self, *args):
        listentry.Generic.OnMouseEnter(self, *args)
        TryGhostFitItemOnMouseAction(self.sr.node, oldWindow=False)

    def OnMouseExit(self, *args):
        listentry.Generic.OnMouseExit(self, *args)
        TryGhostFitItemOnMouseAction(None, oldWindow=False)


class QuickbarItem(GenericMarketItem):
    __guid__ = 'listentry.QuickbarItem'

    def Load(self, node):
        GenericMarketItem.Load(self, node)
        self.sr.sublevel = node.Get('sublevel', 0)
        self.sr.label.left = 12 + max(0, self.sr.sublevel * 16)
        if node.get('extraText', ''):
            self.sr.label.text = localization.GetByLabel('UI/Market/Marketbase/QuickbarTypeNameWithExtraText', typeName=node.label, extraText=node.get('extraText', ''))
        else:
            self.sr.label.text = node.label
        if evetypes.GetMarketGroupID(node.invtype) is None:
            self.SetOpacity(0.5)
            if self.hint is not None:
                self.hint += '<br>'
            else:
                self.hint = ''
            self.hint += localization.GetByLabel('UI/Market/Marketbase/NotAvailableOnMarket')

    def OnClick(self, *args):
        if self.sr.node:
            if evetypes.GetMarketGroupID(self.sr.node.invtype) is None:
                return
            self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetMenu(self):
        m = []
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            m += self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            m += sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None), ignoreMarketDetails=0)
        return m

    def GetDragData(self, *args):
        nodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        return nodes

    def OnDropData(self, dragObj, nodes):
        if self.sr.node.get('DropData', None):
            self.sr.node.DropData(('quickbar', self.sr.node.parent), nodes)


class QuickbarGroup(ListGroup):
    __guid__ = 'listentry.QuickbarGroup'
    isDragObject = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes

    def GetMenu(self):
        m = ListGroup.GetMenu(self)
        quickbar = settings.user.ui.Get('quickbar', {})
        parentID = self.sr.node.id[1]
        buyDict = GetTypesUnderFolder(parentID, quickbar)
        if buyDict:
            m += [(localization.GetByLabel('UI/Market/MarketQuote/BuyAll'), BuyMultipleTypesWithQty, (buyDict,))]
        return m


class MarketMetaGroupEntry(ListGroup):
    __guid__ = 'listentry.MarketMetaGroupEntry'

    def Load(self, node):
        ListGroup.Load(self, node)
        self.OnToggle = node.OnToggle

    def OnClick(self, *args):
        ListGroup.OnClick(self, *args)
        if self.OnToggle is not None:
            self.OnToggle()
