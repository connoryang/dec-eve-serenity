#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\planet\pinContainers\BasePinContainer.py
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveEdit import Edit
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelSmallBold, Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
import evetypes
import uiprimitives
import uicontrols
import uix
import carbonui.const as uiconst
import util
import uicls
import blue
from service import ROLE_GML
import const
import uiutil
from dogma.attributes.format import GetFormatAndValue
import eve.client.script.ui.control.entries as listentry
import base
import localization
import fontConst
import eve.common.script.util.planetCommon as planetCommon
from .. import planetCommon as planetCommonUI

class BasePinContainer(Window):
    __guid__ = 'planet.ui.BasePinContainer'
    __notifyevents__ = ['OnRefreshPins', 'ProcessColonyDataSet']
    default_height = 185
    default_width = 300
    default_minSize = (300, 185)
    default_maxSize = (450, None)
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_name = 'BasePinContainer'
    default_opacity = 0.0
    default_topParentHeight = 0
    default_isCollapseable = False
    default_isPinable = False
    default_isStackable = False
    default_isMinimizable = False
    default_windowID = 'PlanetPinWindow'
    INFO_CONT_HEIGHT = 70

    def GetBaseHeight(self):
        return self.main.height + 26

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.main = ContainerAutoSize(parent=self.sr.main, name='main', padding=3, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.planetUISvc = sm.GetService('planetUI')
        self.planetSvc = sm.GetService('planetSvc')
        self.pin = attributes.Get('pin', None)
        self.uiEffects = uicls.UIEffects()
        self.showingActionContainer = False
        self.currentRoute = None
        self.showNext = None
        self.lastCalled = None
        self.commodityToRoute = None
        self.buttonTextValue = ''
        infoCont = Container(parent=self.main, name='infoCont', padding=5, align=uiconst.TOTOP, height=self.INFO_CONT_HEIGHT)
        self.infoContLeft = Container(name='leftCol', parent=infoCont, align=uiconst.TOLEFT_PROP, width=0.5)
        self.infoContRight = Container(name='rightCol', parent=infoCont, align=uiconst.TOLEFT_PROP, width=0.5)
        self._GetInfoCont()
        self._UpdateInfoCont()
        self.buttonCont = GridContainer(parent=self.main, name='buttonCont', height=40, align=uiconst.TOTOP, padding=(-1, 0, -1, 0))
        BumpedUnderlay(bgParent=self.buttonCont)
        self.buttonCont.lines = 1
        self.buttonCont.columns = 6
        self.buttonTextCont = self._DrawAlignTopCont(22, 'buttonTextCont')
        self.buttonText = EveLabelSmall(parent=self.buttonTextCont, align=uiconst.CENTER, color=(1.0, 1.0, 1.0, 1.0), state=uiconst.UI_NORMAL)
        self.buttonTextCont.height = max(22, self.buttonText.textheight)
        self.actionCont = Container(parent=self.sr.main, name='actionCont', padding=(6, 0, 6, 6), clipChildren=True)
        self.SetCaption(self._GetPinName())
        self.main.SetSizeAutomatically()
        self.height = self.GetBaseHeight()
        self.LoadActionButtons(self._GetActionButtons())
        uicore.animations.FadeTo(self, 0.0, 1.0, duration=0.3)
        self.updateInfoContTimer = base.AutoTimer(100, self._UpdateInfoCont)
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_pininteraction_open_play')
        self.ResizeActionCont(None)

    def ShowDefaultPanel(self):
        if hasattr(self, 'defaultPanel'):
            self.ShowPanel(self.defaultPanel, self.defaultPanelID)

    def _GetPinName(self):
        return planetCommon.GetGenericPinName(self.pin.typeID, self.pin.id)

    def _GetInfoCont(self):
        pass

    def _GetActionButtons(self):
        btns = [util.KeyVal(id=planetCommonUI.PANEL_STATS, panelCallback=self.PanelShowStats),
         util.KeyVal(id=planetCommonUI.PANEL_LINKS, panelCallback=self.PanelShowLinks),
         util.KeyVal(id=planetCommonUI.PANEL_ROUTES, panelCallback=self.PanelShowRoutes),
         util.KeyVal(id=planetCommonUI.PANEL_DECOMMISSION, panelCallback=self.PanelDecommissionPin)]
        return btns

    def ShowPanel(self, panelCallback, panelID, *args):
        _, label = planetCommonUI.PANELDATA[panelID]
        name = localization.GetByLabel(label)
        self.buttonText.text = name
        self.buttonTextValue = name
        if self.showingActionContainer:
            self.showNext = panelCallback
            return
        self.showNext = None
        self.showingActionContainer = True
        self.actionCont.Flush()
        if self.lastCalled != name:
            if args:
                cont = panelCallback(*args)
            else:
                cont = panelCallback()
            if cont:
                cont.state = uiconst.UI_HIDDEN
                self.lastCalled = name
                cont.opacity = 0.0
                self.ResizeActionCont(panelID)
                cont.state = uiconst.UI_PICKCHILDREN
                self.uiEffects.MorphUI(cont, 'opacity', 1.0, time=250.0, float=1, maxSteps=1000)
                uicore.registry.SetFocus(cont)
        else:
            self.HideCurrentPanel()
        self.showingActionContainer = False
        if self.showNext:
            self.ShowPanel(self.showNext, panelID)

    def HideCurrentPanel(self):
        self.actionCont.Flush()
        self.ResizeActionCont()
        self.lastCalled = None
        self.buttonTextValue = ''

    def _DrawAlignTopCont(self, height, name, padding = (0, 0, 0, 0), state = uiconst.UI_PICKCHILDREN):
        return Container(parent=self.main, name=name, pos=(0,
         0,
         0,
         height), padding=padding, state=state, align=uiconst.TOTOP)

    def OnIconButtonMouseEnter(self, iconButton, *args):
        ButtonIcon.OnMouseEnter(iconButton, *args)
        self.buttonText.text = iconButton.name

    def OnIconButtonMouseExit(self, iconButton, *args):
        ButtonIcon.OnMouseExit(iconButton, *args)
        self.buttonText.text = self.buttonTextValue

    def LoadActionButtons(self, buttons):
        iconSize = 32
        w = self.width - 6
        maxIcons = 7.0
        n = float(len(buttons))
        pad = 5 + 1 * iconSize * (1.0 - n / maxIcons)
        w -= 2 * pad
        space = (w - n * iconSize) / n
        self.buttonCont.columns = len(buttons)
        for i, b in enumerate(buttons):
            iconPath, cerberusPath = planetCommonUI.PANELDATA[b.id]
            panelName = localization.GetByLabel(cerberusPath)
            if i == 0:
                self.defaultPanel = b.panelCallback
                self.defaultPanelID = b.id
            cont = Container(name=panelName, parent=self.buttonCont)
            ib = ButtonIcon(texturePath=iconPath, parent=cont, align=uiconst.CENTER, name=panelName, hint=b.Get('hint', ''), width=iconSize, height=iconSize, iconSize=iconSize, func=self._OnIconButtonClicked, args=(b.panelCallback, b.id))
            ib.OnMouseEnter = (self.OnIconButtonMouseEnter, ib)
            ib.OnMouseExit = (self.OnIconButtonMouseExit, ib)

    def _OnIconButtonClicked(self, panelCallback, panelID, *args):
        self.ShowPanel(panelCallback, panelID)

    def CloseByUser(self, *args):
        self.planetUISvc.CloseCurrentlyOpenContainer()

    def PanelShowLinks(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.linkScroll = scroll = Scroll(parent=cont, name='linksScroll', align=uiconst.TOALL)
        self.linkScroll.sr.id = 'planetBasePinLinkScroll'
        self.LoadLinkScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateNew'), self._CreateNewLink, None], [localization.GetByLabel('UI/PI/Common/DeleteLink'), self._DeleteLink, None]]
        ButtonGroup(btns=btns, idx=0, parent=cont)
        return cont

    def LoadLinkScroll(self):
        scrolllist = []
        planet = sm.GetService('planetUI').GetCurrentPlanet()
        colony = planet.GetColony(session.charid)
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            linkedPin = colony.GetPin(linkedPinID)
            distance = link.GetDistance()
            bandwidthUsed = link.GetBandwidthUsage()
            percentageUsed = 100 * (bandwidthUsed / link.GetTotalBandwidth())
            data = util.KeyVal()
            data.label = '%s<t>%s<t>%s' % (planetCommon.GetGenericPinName(linkedPin.typeID, linkedPin.id), util.FmtDist(distance), localization.GetByLabel('UI/Common/Percentage', percentage=percentageUsed))
            data.hint = ''
            data.OnMouseEnter = self.OnLinkEntryHover
            data.OnMouseExit = self.OnLinkEntryExit
            data.OnDblClick = self.OnLinkListentryDblClicked
            data.id = (link.endpoint1.id, link.endpoint2.id)
            sortBy = linkedPinID
            scrolllist.append((sortBy, listentry.Get('Generic', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.linkScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoLinksPresent'), headers=[localization.GetByLabel('UI/PI/Common/Destination'), localization.GetByLabel('UI/Common/Distance'), localization.GetByLabel('UI/PI/Common/CapacityUsed')])

    def OnLinkListentryDblClicked(self, entry):
        myPinManager = sm.GetService('planetUI').myPinManager
        link = myPinManager.linksByPinIDs[entry.sr.node.id]
        for node in self.linkScroll.GetNodes():
            myPinManager.RemoveHighlightLink(node.id)

        sm.GetService('planetUI').OpenContainer(link)

    def OnLinkEntryHover(self, entry):
        node = entry.sr.node
        self.planetUISvc.myPinManager.HighlightLink(self.pin.id, node.id)

    def OnLinkEntryExit(self, entry):
        node = entry.sr.node
        self.planetUISvc.myPinManager.RemoveHighlightLink(node.id)

    def _CreateNewLink(self, *args):
        self.planetUISvc.myPinManager.SetLinkParent(self.pin.id)
        self.CloseByUser()

    def _DeleteLink(self, *args):
        selected = self.linkScroll.GetSelected()
        if len(selected) > 0:
            self.planetUISvc.myPinManager.RemoveLink(selected[0].id)
            self.LoadLinkScroll()

    def _DrawEditBox(self, parent, text):
        textHeight = uix.GetTextHeight(text, width=self.width - 30, fontsize=fontConst.EVE_MEDIUM_FONTSIZE)
        edit = Edit(setvalue=text, parent=parent, align=uiconst.TOTOP, height=textHeight + 18, top=-6, hideBackground=1, readonly=True)
        edit.scrollEnabled = False
        return edit

    def ResizeActionCont(self, panelID = None):
        if panelID:
            minHeight, maxHeight = planetCommonUI.PANEL_MIN_MAX_HEIGHT[panelID]
            if maxHeight:
                height = (minHeight + maxHeight) / 2
            else:
                height = minHeight
        else:
            height = minHeight = maxHeight = 0
        baseHeight = self.GetBaseHeight()
        uicore.animations.MorphScalar(self, 'height', self.height, height + baseHeight, duration=0.3)
        self.SetMinSize((self.default_minSize[0], baseHeight + minHeight))
        if minHeight == maxHeight:
            self.SetFixedHeight(baseHeight + minHeight)
        elif maxHeight:
            self.SetFixedHeight(None)
            self.SetMaxSize((self.default_maxSize[0], baseHeight + maxHeight))
        else:
            self.SetFixedHeight(None)
            self.SetMaxSize((self.default_maxSize[0], None))

    def _UpdateInfoCont(self):
        pass

    def PanelShowStorage(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.storageContentScroll = Scroll(parent=cont, name='storageContentsScroll', id='planetStorageContentsScroll')
        self.storageContentScroll.sr.fixedColumns = {'': 28}
        self.LoadStorageContentScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateRoute'), self._CreateRoute, 'storageContentScroll'], [localization.GetByLabel('UI/PI/Common/ExpeditedTransfer'), self._CreateTransfer, None]]
        self.createRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        return cont

    def LoadStorageContentScroll(self):
        scrolllist = []
        for typeID, amount in self.pin.contents.iteritems():
            data = util.KeyVal()
            volume = evetypes.GetVolume(typeID) * amount
            data.label = '<t>%s<t>%s<t>%s' % (evetypes.GetName(typeID), amount, volume)
            data.amount = amount
            data.typeID = typeID
            data.itemID = None
            data.getIcon = (True,)
            data.OnDblClick = self.OnStorageEntryDblClicked
            sortBy = amount
            scrolllist.append((sortBy, listentry.Get('Item', data=data)))

        scrolllist = uiutil.SortListOfTuples(scrolllist)
        self.storageContentScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoContentsPresent'), headers=['',
         localization.GetByLabel('UI/PI/Common/Type'),
         localization.GetByLabel('UI/Common/Amount'),
         localization.GetByLabel('UI/Common/Volume')])

    def OnStorageEntryDblClicked(self, entry):
        self._CreateRoute('storageContentScroll')

    def PanelShowProducts(self):
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.productScroll = Scroll(parent=cont, name='productsScroll')
        self.productScroll.sr.id = 'planetBasePinProductScroll'
        self.LoadProductScroll()
        btns = [[localization.GetByLabel('UI/PI/Common/CreateRoute'), self._CreateRoute, 'productScroll']]
        self.createRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        btns = [[localization.GetByLabel('UI/PI/Common/DeleteRoute'), self._DeleteRoute, ()]]
        self.deleteRouteButton = ButtonGroup(btns=btns, parent=cont, idx=0)
        self.createRouteButton.state = uiconst.UI_HIDDEN
        self.deleteRouteButton.state = uiconst.UI_HIDDEN
        return cont

    def LoadProductScroll(self):
        scrolllist = []
        colony = self.planetUISvc.planet.GetColony(session.charid)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Cannot load product scroll for pin on a planet that has no colony')
        sourcedRoutes = colony.colonyData.GetSourceRoutesForPin(self.pin.id)
        routesByTypeID = {}
        for route in sourcedRoutes:
            typeID = route.GetType()
            if typeID not in routesByTypeID:
                routesByTypeID[typeID] = []
            routesByTypeID[typeID].append(route)

        for typeID, amount in self.pin.GetProductMaxOutput().iteritems():
            typeName = evetypes.GetName(typeID)
            for route in routesByTypeID.get(typeID, []):
                qty = route.GetQuantity()
                amount -= qty
                data = util.KeyVal(label='%s<t>%s<t>%s' % (qty, typeName, localization.GetByLabel('UI/PI/Common/Routed')), typeID=typeID, itemID=None, getIcon=True, routeID=route.routeID, OnMouseEnter=self.OnRouteEntryHover, OnMouseExit=self.OnRouteEntryExit, OnClick=self.OnProductEntryClicked, OnDblClick=self.OnProductEntryDblClicked)
                scrolllist.append(listentry.Get('Item', data=data))

            if amount > 0:
                data = util.KeyVal()
                data.label = '%s<t>%s<t>%s' % (amount, evetypes.GetName(typeID), localization.GetByLabel('UI/PI/Common/NotRouted'))
                data.typeID = typeID
                data.amount = amount
                data.itemID = None
                data.getIcon = True
                data.OnClick = self.OnProductEntryClicked
                data.OnDblClick = self.OnProductEntryDblClicked
                scrolllist.append(listentry.Get('Item', data=data))

        self.productScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoProductsPresent'), headers=[localization.GetByLabel('UI/Common/Amount'), localization.GetByLabel('UI/PI/Common/Type'), ''])

    def OnProductEntryClicked(self, entry):
        node = entry.sr.node
        if node.Get('routeID', None) is None:
            self.createRouteButton.state = uiconst.UI_NORMAL
            self.deleteRouteButton.state = uiconst.UI_HIDDEN
        else:
            self.createRouteButton.state = uiconst.UI_HIDDEN
            self.deleteRouteButton.state = uiconst.UI_NORMAL

    def OnProductEntryDblClicked(self, entry):
        node = entry.sr.node
        if node.Get('routeID', None) is None:
            self._CreateRoute('productScroll')

    def _CreateRoute(self, scroll):
        selected = getattr(self, scroll).GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            self.planetUISvc.myPinManager.EnterRouteMode(self.pin.id, entry.typeID)
            self.ShowPanel(self.PanelCreateRoute, planetCommonUI.PANEL_CREATEROUTE, entry.typeID, entry.amount)

    def SubmitRoute(self):
        if not getattr(self, 'routeAmountEdit', None):
            return
        sm.GetService('planetUI').myPinManager.CreateRoute(self.routeAmountEdit.GetValue())
        self.HideCurrentPanel()
        self.commodityToRoute = None

    def _DeleteRoute(self):
        selected = self.productScroll.GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            if entry.routeID:
                self.planetUISvc.myPinManager.RemoveRoute(entry.routeID)
                self.LoadProductScroll()
                self.createRouteButton.state = uiconst.UI_HIDDEN
                self.deleteRouteButton.state = uiconst.UI_HIDDEN

    def _DeleteRouteFromEntry(self):
        if not hasattr(self, 'routeScroll'):
            return
        selected = self.routeScroll.GetSelected()
        if len(selected) > 0:
            entry = selected[0]
            if entry.routeID:
                self.planetUISvc.myPinManager.RemoveRoute(entry.routeID)
                self.LoadRouteScroll()
                self.uiEffects.MorphUI(self.routeInfo, 'opacity', 0.0, time=125.0, float=1, newthread=0, maxSteps=1000)

    def _CreateTransfer(self, *args):
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            raise UserError('CannotTransferInEditMode')
        self.planetUISvc.myPinManager.EnterRouteMode(self.pin.id, None, oneoff=True)
        self.ShowPanel(self.PanelSelectTransferDest, planetCommonUI.PANEL_TRANSFER)

    def PanelDecommissionPin(self):
        typeName = evetypes.GetName(self.pin.typeID)
        if evetypes.GetGroupID(self.pin.typeID) == const.groupCommandPins:
            text = localization.GetByLabel('UI/PI/Common/DecommissionCommandPin', typeName=typeName)
        else:
            text = localization.GetByLabel('UI/PI/Common/DecommissionLink', typeName=typeName)
        cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        Label(parent=cont, text=text, align=uiconst.TOTOP)
        btns = [[localization.GetByLabel('UI/PI/Common/Proceed'), self._DecommissionSelf, None]]
        ButtonGroup(btns=btns, idx=0, parent=cont)
        return cont

    def _DecommissionSelf(self, *args):
        sm.GetService('audio').SendUIEvent('wise:/msg_pi_build_decommission_play')
        self.planetUISvc.myPinManager.RemovePin(self.pin.id)
        self.CloseByUser()

    def OnRouteEntryHover(self, entry):
        self.planetUISvc.myPinManager.ShowRoute(entry.sr.node.routeID)

    def OnRouteEntryExit(self, entry):
        self.planetUISvc.myPinManager.StopShowingRoute(entry.sr.node.routeID)

    def OnRefreshPins(self, pinIDs):
        if hasattr(self, 'lastCalled') and self.lastCalled == localization.GetByLabel('UI/PI/Common/Storage'):
            self.LoadStorageContentScroll()

    def ProcessColonyDataSet(self, planetID):
        if self.planetUISvc.planetID != planetID:
            return
        self.pin = sm.GetService('planetSvc').GetPlanet(planetID).GetPin(self.pin.id)

    def PanelShowStats(self, *args):
        cont = Container(parent=self.actionCont, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.statsScroll = scroll = Scroll(parent=cont, name='StatsScroll')
        scrolllist = self.GetStatsEntries()
        scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/PI/Common/Attribute'), localization.GetByLabel('UI/Common/Value')])
        return cont

    def GetStatsEntries(self):
        scrolllist = []
        if self.pin.GetCpuUsage() > 0:
            data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuUsage'), localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=self.pin.GetCpuUsage())))
            scrolllist.append(listentry.Get('Generic', data=data))
        if self.pin.GetCpuOutput() > 0:
            data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/CpuOutput'), localization.GetByLabel('UI/PI/Common/TeraFlopsAmount', amount=self.pin.GetCpuOutput())))
            scrolllist.append(listentry.Get('Generic', data=data))
        if self.pin.GetPowerUsage() > 0:
            data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerUsage'), localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=self.pin.GetPowerUsage())))
            scrolllist.append(listentry.Get('Generic', data=data))
        if self.pin.GetPowerOutput() > 0:
            data = util.KeyVal(label='%s<t>%s' % (localization.GetByLabel('UI/PI/Common/PowerOutput'), localization.GetByLabel('UI/PI/Common/MegaWattsAmount', amount=self.pin.GetPowerOutput())))
            scrolllist.append(listentry.Get('Generic', data=data))
        return scrolllist

    def OnPlanetRouteWaypointAdded(self, currentRoute):
        self.currentRoute = currentRoute
        self.UpdatePanelCreateRoute()

    def PanelCreateRoute(self, typeID, amount):
        cont = Container(parent=self.actionCont, pos=(0, 0, 0, 130), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        cont._OnClose = self.OnPanelCreateRouteClosed
        w = self.width - 5
        self.sourceMaxAmount = amount
        self.routeMaxAmount = amount
        self.commodityToRoute = typeID
        self.commoditySourceMaxAmount = amount
        self.currRouteCycleTime = self.pin.GetCycleTime()
        resourceTxt = localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=evetypes.GetName(typeID), amount=int(self.routeMaxAmount))
        CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/CommodityToRoute'), subtext=resourceTxt, iconTypeID=typeID, top=0, width=w)
        CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/PI/Common/QtyAmount'), width=w, top=30, state=uiconst.UI_DISABLED)
        self.routeAmountEdit = SinglelineEdit(name='routeAmountEdit', parent=cont, setvalue=self.routeMaxAmount, height=14, width=56, align=uiconst.TOPLEFT, top=44, ints=(0, self.routeMaxAmount), OnChange=self.OnRouteAmountEditChanged)
        self.routeAmountText = EveLabelSmall(parent=cont, left=60, top=46, state=uiconst.UI_NORMAL)
        self.routeDestText = CaptionAndSubtext(parent=cont, caption=localization.GetByLabel('UI/Common/Destination'), top=70, width=w)
        btns = [[localization.GetByLabel('UI/PI/Common/CreateRoute'), self.SubmitRoute, ()]]
        self.createRouteButton = ButtonGroup(btns=btns, parent=cont, line=False, alwaysLite=True)
        self.UpdatePanelCreateRoute()
        return cont

    def OnPanelCreateRouteClosed(self, *args):
        sm.GetService('planetUI').myPinManager.LeaveRouteMode()

    def OnRouteAmountEditChanged(self, newVal):
        try:
            routeAmount = int(newVal)
        except ValueError:
            return

        if not self.currRouteCycleTime:
            return
        routeAmount = min(routeAmount, self.routeMaxAmount)
        routeAmount = max(routeAmount, 0.0)
        volume = planetCommon.GetCommodityTotalVolume({self.commodityToRoute: routeAmount})
        volumePerHour = planetCommon.GetBandwidth(volume, self.currRouteCycleTime)
        sm.GetService('planetUI').myPinManager.OnRouteVolumeChanged(volumePerHour)

    def UpdatePanelCreateRoute(self):
        if not self.currentRoute or len(self.currentRoute) < 2:
            destName = localization.GetByLabel('UI/PI/Common/NoDestinationSelected')
            self.routeMaxAmount = self.sourceMaxAmount
            self.currRouteCycleTime = self.pin.GetCycleTime()
        else:
            self.routeDestPin = sm.GetService('planetUI').GetCurrentPlanet().GetColony(session.charid).GetPin(self.currentRoute[-1])
            isValid, invalidTxt, self.currRouteCycleTime = planetCommon.GetRouteValidationInfo(self.pin, self.routeDestPin, self.commodityToRoute)
            destName = planetCommon.GetGenericPinName(self.routeDestPin.typeID, self.routeDestPin.id)
            if not isValid:
                destName = localization.GetByLabel('UI/PI/Common/InvalidDestination', destName=destName, reason=invalidTxt)
            if not isValid:
                self.routeMaxAmount = 0
            elif self.routeDestPin.IsProcessor() and self.commodityToRoute in self.routeDestPin.GetConsumables():
                destMaxAmount = self.routeDestPin.GetConsumables().get(self.commodityToRoute)
                if self.pin.IsStorage():
                    self.routeMaxAmount = destMaxAmount
                else:
                    self.routeMaxAmount = min(destMaxAmount, self.commoditySourceMaxAmount)
            else:
                self.routeMaxAmount = self.commoditySourceMaxAmount
        self.routeAmountEdit.SetText(self.routeMaxAmount)
        self.routeAmountEdit.IntMode(0, self.routeMaxAmount)
        self.routeAmountText.text = localization.GetByLabel('UI/PI/Common/RoutedPortion', maxAmount=self.routeMaxAmount)
        self.OnRouteAmountEditChanged(self.routeMaxAmount)
        self.routeDestText.SetSubtext(destName)

    def PanelSelectTransferDest(self, *args):
        cont = Container(parent=self.actionCont, pos=(0, 0, 0, 15), align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        cont._OnClose = self.OnPanelSelectTransferDestClosed
        Label(parent=cont, text=localization.GetByLabel('UI/PI/Common/SelectTransferDestination'), align=uiconst.TOTOP)
        return cont

    def OnPanelSelectTransferDestClosed(self, *args):
        sm.GetService('planetUI').myPinManager.LeaveRouteMode()

    def SetPin(self, pin):
        self.pin = pin

    def PanelShowRoutes(self, *args):
        self.showRoutesCont = cont = Container(parent=self.actionCont, state=uiconst.UI_HIDDEN)
        self.routeScroll = Scroll(parent=cont, name='routeScroll')
        self.routeScroll.multiSelect = False
        self.routeScroll.sr.id = 'planetBaseShowRoutesScroll'
        self.routeInfo = Container(parent=cont, pos=(0, 0, 0, 100), align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, idx=0, padTop=4)
        w = self.width / 2 - 10
        self.routeInfoSource = CaptionAndSubtext(parent=self.routeInfo, caption=localization.GetByLabel('UI/PI/Common/Origin'), width=w)
        self.routeInfoDest = CaptionAndSubtext(parent=self.routeInfo, caption=localization.GetByLabel('UI/PI/Common/Destination'), width=w, top=38)
        self.routeInfoType = CaptionAndSubtext(parent=self.routeInfo, caption=localization.GetByLabel('UI/Common/Commodity'), width=w, left=w)
        self.routeInfoBandwidth = CaptionAndSubtext(parent=self.routeInfo, caption=localization.GetByLabel('UI/PI/Common/CapacityUsed'), width=w, left=w, top=38)
        btns = []
        if self.pin.IsStorage() and hasattr(self, '_CreateRoute'):
            btns.append([localization.GetByLabel('UI/PI/Common/CreateRoute'), self._CreateRoute, 'routeScroll'])
        btns.append([localization.GetByLabel('UI/PI/Common/DeleteRoute'), self._DeleteRouteFromEntry, ()])
        self.routeInfoBtns = ButtonGroup(btns=btns, parent=self.routeInfo, idx=0)
        self.LoadRouteScroll()
        return cont

    def GetRouteTypeLabel(self, route, pin):
        if not route or not pin:
            return localization.GetByLabel('UI/Common/Unknown')
        elif route.GetSourcePinID() == pin.id:
            return localization.GetByLabel('UI/PI/Common/Outgoing')
        elif route.GetDestinationPinID() == pin.id:
            return localization.GetByLabel('UI/PI/Common/Incoming')
        else:
            return localization.GetByLabel('UI/PI/Common/Transiting')

    def LoadRouteScroll(self):
        scrolllist = []
        routesShown = []
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(self.pin.ownerID)
        if colony is None or colony.colonyData is None:
            raise RuntimeError('Unable to load route scroll without active colony on planet')
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            for routeID in link.routesTransiting:
                if routeID in routesShown:
                    continue
                route = colony.GetRoute(routeID)
                typeID = route.GetType()
                qty = route.GetQuantity()
                typeName = evetypes.GetName(typeID)
                data = util.KeyVal(label='<t>%s<t>%s<t>%s' % (typeName, qty, self.GetRouteTypeLabel(route, self.pin)), typeID=typeID, itemID=None, getIcon=True, OnMouseEnter=self.OnRouteEntryHover, OnMouseExit=self.OnRouteEntryExit, routeID=route.routeID, OnClick=self.OnRouteEntryClick, amount=qty)
                scrolllist.append(listentry.Get('Item', data=data))
                routesShown.append(route.routeID)

        self.routeScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/PI/Common/NoIncomingOrOutgoingRoutes'), headers=['',
         localization.GetByLabel('UI/Common/Commodity'),
         localization.GetByLabel('UI/Common/Quantity'),
         localization.GetByLabel('UI/PI/Common/Type')])

    def OnRouteEntryClick(self, *args):
        selectedRoutes = self.routeScroll.GetSelected()
        if len(selectedRoutes) < 1:
            self.routeInfo.state = uiconst.UI_HIDDEN
            return
        selectedRouteData = selectedRoutes[0]
        selectedRoute = None
        colony = self.planetUISvc.GetCurrentPlanet().GetColony(session.charid)
        links = colony.colonyData.GetLinksForPin(self.pin.id)
        for linkedPinID in links:
            link = colony.GetLink(self.pin.id, linkedPinID)
            for routeID in link.routesTransiting:
                if routeID == selectedRouteData.routeID:
                    selectedRoute = route = colony.GetRoute(routeID)
                    break

        if selectedRoute is None or not evetypes.Exists(selectedRoute.GetType()):
            return
        if selectedRoute.GetSourcePinID() == self.pin.id:
            self.routeInfoSource.SetSubtext(localization.GetByLabel('UI/PI/Common/ThisStructure'))
        else:
            sourcePin = sm.GetService('planetUI').planet.GetPin(selectedRoute.GetSourcePinID())
            self.routeInfoSource.SetSubtext(planetCommon.GetGenericPinName(sourcePin.typeID, sourcePin.id))
        if selectedRoute.GetDestinationPinID() == self.pin.id:
            self.routeInfoDest.SetSubtext(localization.GetByLabel('UI/PI/Common/ThisStructure'))
        else:
            destPin = sm.GetService('planetUI').planet.GetPin(selectedRoute.GetDestinationPinID())
            self.routeInfoDest.SetSubtext(planetCommon.GetGenericPinName(destPin.typeID, destPin.id))
        routeTypeID = route.GetType()
        routeQty = route.GetQuantity()
        self.routeInfoType.SetSubtext(localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=evetypes.GetName(routeTypeID), amount=int(routeQty)))
        bandwidthAttr = cfg.dgmattribs.Get(const.attributeLogisticalCapacity)
        self.routeInfoBandwidth.SetSubtext(GetFormatAndValue(bandwidthAttr, selectedRoute.GetBandwidthUsage()))
        createRouteBtn = self.routeInfoBtns.GetBtnByLabel(localization.GetByLabel('UI/PI/Common/CreateRoute'))
        if createRouteBtn:
            if selectedRoute.GetDestinationPinID() == self.pin.id:
                createRouteBtn.state = uiconst.UI_NORMAL
            else:
                createRouteBtn.state = uiconst.UI_HIDDEN
        self.routeInfo.opacity = 0.0
        self.routeInfo.state = uiconst.UI_PICKCHILDREN
        self.uiEffects.MorphUI(self.routeInfo, 'opacity', 1.0, time=125.0, float=1, newthread=0, maxSteps=1000)


class IconButton(Container):
    __guid__ = 'planet.ui.IconButton'
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_size = 32
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.RELATIVE

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        size = attributes.get('size', self.default_size)
        color = attributes.get('color', self.default_color)
        self.isSelected = attributes.get('isSelected', False)
        self.icon = Icon(icon=attributes.icon, typeID=attributes.typeID, parent=self, pos=(0,
         0,
         size,
         size), state=uiconst.UI_DISABLED, size=size, ignoreSize=True, color=color)
        self.selectedFrame = Frame(parent=self, color=(1.0, 1.0, 1.0, 0.5), state=uiconst.UI_HIDDEN)
        self.frame = Frame(parent=self, color=(1.0, 1.0, 1.0, 0.8), state=uiconst.UI_HIDDEN)
        if self.isSelected:
            self.SetSelected(True)

    def OnMouseEnter(self, *args):
        self.ShowFrame()

    def OnMouseExit(self, *args):
        self.HideFrame()

    def SetSelected(self, isSelected):
        self.isSelected = isSelected
        if self.isSelected:
            self.selectedFrame.state = uiconst.UI_DISABLED
        else:
            self.selectedFrame.state = uiconst.UI_HIDDEN

    def ShowFrame(self):
        if not hasattr(self, 'frame'):
            return
        self.frame.state = uiconst.UI_DISABLED
        self.icon.color.a = 0.3

    def HideFrame(self):
        if not hasattr(self, 'frame'):
            return
        self.frame.state = uiconst.UI_HIDDEN
        self.icon.color.a = 1.0


class CaptionAndSubtext(Container):
    __guid__ = 'planet.ui.CaptionAndSubtext'
    default_state = uiconst.UI_NORMAL
    default_name = 'CaptionAndSubtext'
    default_align = uiconst.TOPLEFT
    default_width = 150
    default_height = 24

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.captionTxt = attributes.Get('caption', '')
        self.subtextTxt = attributes.Get('subtext', '')
        self.iconTypeID = attributes.Get('iconTypeID', None)
        self.height = attributes.Get('height', self.default_height)
        self.width = attributes.Get('width', self.default_width)
        self.iconSize = 25
        self.icon = None
        self.CreateLayout()

    def CreateLayout(self):
        l, t, w, h = self.GetAbsolute()
        if self.iconTypeID:
            width = w - self.iconSize - 15
            left = self.iconSize
        else:
            width = w
            left = 0
        self.caption = CaptionLabel(parent=self, text=self.captionTxt, pos=(left,
         0,
         width,
         0), maxLines=1)
        self.subtext = SubTextLabel(parent=self, text=self.subtextTxt, pos=(left,
         self.caption.height - 2,
         width,
         0))
        if self.iconTypeID:
            self.icon = Icon(parent=self, pos=(-5,
             0,
             self.iconSize,
             self.iconSize), state=uiconst.UI_DISABLED, typeID=self.iconTypeID, size=self.iconSize, ignoreSize=True)

    def SetSubtext(self, subtext):
        self.subtextTxt = subtext
        self.subtext.text = self.subtextTxt

    def SetCaption(self, caption):
        self.captionTxt = caption
        self.caption.text = self.captionTxt

    def SetIcon(self, typeID):
        if typeID == self.iconTypeID:
            return
        self.iconTypeID = typeID
        self.Flush()
        self.CreateLayout()

    def GetMenu(self):
        if not self.iconTypeID:
            return None
        ret = [(uiutil.MenuLabel('UI/Commands/ShowInfo'), sm.GetService('info').ShowInfo, [self.iconTypeID])]
        if session.role & ROLE_GML == ROLE_GML:
            ret.append(('GM / WM Extras', self.GetGMMenu()))
        return ret

    def GetGMMenu(self):
        ret = []
        if self.iconTypeID:
            ret.append(('TypeID: %s' % self.iconTypeID, blue.pyos.SetClipboardData, [str(int(self.iconTypeID))]))
        return ret


class CaptionLabel(EveLabelSmallBold):
    __guid__ = 'planet.ui.CaptionLabel'
    default_state = uiconst.UI_DISABLED
    default_color = (1.0, 1.0, 1.0, 0.95)


class SubTextLabel(CaptionLabel):
    __guid__ = 'planet.ui.SubTextLabel'
    default_color = (1.0, 1.0, 1.0, 0.8)
