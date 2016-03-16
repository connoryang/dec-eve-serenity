#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\leftPanel.py
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_CENTER, CONTENT_ALIGN_LEFT
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.buttons import Button, ToggleButtonGroup
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
import carbonui.const as uiconst
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.export import ImportLegacyFittingsWindow
from eve.client.script.ui.shared.fittingGhost.browsers.fittingBrowser import FittingBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.browsers.hardwareBrowser import HardwareBrowserListProvider
from eve.client.script.ui.shared.fittingGhost.browsers.searchBrowser import SearchBrowserListProvider
from eve.client.script.ui.shared.fittingMgmtWindow import FittingMgmt
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes
import inventorycommon.typeHelpers
from localization import GetByLabel
from utillib import KeyVal
from eve.client.script.ui.control import entries as listentry

class LeftPanel(Container):
    default_clipChildren = True
    __notifyevents__ = ['OnSimulatedShipLoaded', 'OnFakeUpdateFittingWindow', 'OnFittingsUpdated']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fittingSvc = sm.GetService('fittingSvc')
        self.loaded = False
        padding = 10
        self.ammoShowingForType = None
        self.shipCont = Container(name='currentShip', parent=self, align=uiconst.TOTOP, pos=(0, 0, 0, 42), padding=(10, 0, 10, 2), state=uiconst.UI_NORMAL)
        self.CreateCurrentShipCont()
        btnCont = FlowContainer(parent=self, align=uiconst.TOBOTTOM, contentAlignment=CONTENT_ALIGN_CENTER, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        self.fitBtn = Button(parent=btnCont, label='Fit', func=self.FitShip, align=uiconst.NOALIGN)
        self.saveBtn = Button(parent=btnCont, label='Save', func=self.SaveFitting, align=uiconst.NOALIGN)
        self.AdjustButtons()
        self.btnGroup = ToggleButtonGroup(name='fittingToggleBtnGroup', parent=self, align=uiconst.TOTOP, callback=self.BrowserSelected, height=30, padding=(padding,
         0,
         padding,
         0), idx=-1)
        self.AddFittingFilterButtons()
        self.AddSearchFields()
        self.AddHardwareFilterButtons()
        for btnID, label, dblClickCallback in (('fittings', '.Fittings', self.LoadFittingSetup), ('hardware', '.Hardware', None)):
            btn = self.btnGroup.AddButton(btnID, label)
            if dblClickCallback:
                btn.OnDblClick = dblClickCallback

        self.ammoScrollCont = DragResizeCont(name='ammoScrollCont', parent=self, align=uiconst.TOBOTTOM_PROP, settingsID='fitting_ammoScrollCont', minSize=0.15, maxSize=0.7)
        self.ammoPicker = FlowContainer(parent=self.ammoScrollCont, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_CENTER, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        self.ammoScroll = Scroll(parent=self.ammoScrollCont, align=uiconst.TOALL, padding=(padding,
         0,
         padding,
         0))
        self.scroll = Scroll(parent=self, align=uiconst.TOALL, padding=(padding,
         2,
         padding,
         0))
        self.ammoScroll.sr.content.OnDropData = self.OnDropData
        self.scroll.sr.content.OnDropData = self.OnDropData
        sm.RegisterNotify(self)

    def Load(self):
        if self.loaded:
            return
        self.btnGroup.SelectByID(settings.user.ui.Get('fitting_browserBtnID', 'fittings'))
        self.loaded = True

    def AddSearchFields(self):
        self.searchparent = Container(name='searchparent', parent=self, align=uiconst.TOTOP, height=18, padding=(10, 4, 10, 4))
        self.searchBtn = Button(parent=self.searchparent, label=GetByLabel('UI/Common/Search'), func=self.SearchHardware, btn_default=1, idx=0, align=uiconst.CENTERRIGHT)
        searchText = settings.user.ui.Get('fitting_hardwareSearchField', '')
        self.searchInput = QuickFilterEdit(name='searchField', parent=self.searchparent, setvalue=searchText, hinttext=GetByLabel('UI/Market/Marketbase/SearchTerm'), pos=(0, 0, 18, 0), padRight=self.searchBtn.width + self.searchBtn.padRight + 4, maxLength=64, align=uiconst.TOTOP, OnClearFilter=self.SearchHardware)
        self.searchInput.ReloadFunction = self.OnHardwareSearchFieldChanged
        self.searchInput.OnReturn = self.SearchHardware
        self.searchFittingBtn = Button(parent=self.fittingSearchCont, label=GetByLabel('UI/Common/Search'), func=self.SearchFittings, btn_default=1, idx=0, align=uiconst.TOPRIGHT)
        searchText = settings.user.ui.Get('fitting_fittingSearchField', '')
        self.searchFittingInput = QuickFilterEdit(name='searchFittingInput', parent=self.fittingSearchCont, setvalue=searchText, hinttext=GetByLabel('UI/Market/Marketbase/SearchTerm'), pos=(0, 0, 18, 0), padRight=self.searchFittingBtn.width + self.searchFittingBtn.padRight + 4, maxLength=64, padTop=0, align=uiconst.TOTOP, OnClearFilter=self.SearchFittings)
        self.searchFittingInput.ReloadFunction = self.OnSearchFieldChanged
        self.searchFittingInput.OnReturn = self.SearchFittings

    def ReloadBrowser(self):
        btnID = settings.user.ui.Get('fitting_browserBtnID', 'fittings')
        self.BrowserSelected(btnID)

    def BrowserSelected(self, btnID, *args):
        settings.user.ui.Set('fitting_browserBtnID', btnID)
        if btnID == 'fittings':
            self.ShowOrHideElements(display=False)
            self.LoadFittings()
        elif btnID == 'hardware':
            self.AddHardwareButtons()
            self.ShowOrHideElements(display=True)
            self.LoadHardware()

    def ShowOrHideElements(self, display = True):
        self.filterCont.display = display
        self.ammoScrollCont.display = display
        self.searchparent.display = display
        self.searchInput.display = display
        self.searchBtn.display = display
        self.fittingFilterCont.display = not display

    def OnFittingsUpdated(self):
        if settings.user.ui.Get('fitting_browserBtnID', 'fittings') == 'fittings':
            self.ReloadBrowser()

    def LoadFittings(self):
        scrolllist = self.GetFittingScrolllist(session.charid)
        self.scroll.Load(contentList=scrolllist, scrolltotop=0)

    def LoadHardware(self):
        if settings.user.ui.Get('fitting_hardwareSearchField', ''):
            scrolllist = self.GetSearchResults()
        else:
            hardwareBrowserListProvider = HardwareBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData)
            scrolllist = hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=const.marketCategoryShipEquipment)
            scrolllist += hardwareBrowserListProvider.GetGroupListForBrowse(marketGroupID=955)
        self.scroll.Load(contentList=scrolllist, scrolltotop=0)

    def ExitSimulation(self, *args):
        sm.GetService('fittingSvc').simulated = False
        shipID = GetActiveShip()
        sm.ScatterEvent('OnSimulatedShipLoaded', shipID)

    def LoadCurrentShip(self, *args):
        sm.GetService('ghostFittingSvc').LoadCurrentShip()

    def SaveFitting(self, *args):
        return self.fittingSvc.SaveFitting()

    def FitShip(self, *args):
        pass

    def GetFittingScrolllist(self, ownerID, *args):
        fittingListProvider = FittingBrowserListProvider(self.OnDropData)
        return fittingListProvider.GetFittingScrolllist(ownerID)

    def SearchHardware(self, *args):
        self.Search(self.searchInput, 'fitting_hardwareSearchField')

    def SearchFittings(self, *args):
        self.Search(self.searchFittingInput, 'fitting_fittingSearchField')

    def Search(self, inputField, settingConfig):
        settings.user.ui.Set(settingConfig, inputField.GetValue().strip())
        self.ReloadBrowser()

    def OnHardwareSearchFieldChanged(self, *args):
        self.SearchFieldChanged(self.searchInput, 'fitting_hardwareSearchField')

    def OnSearchFieldChanged(self, *args):
        self.SearchFieldChanged(self.searchFittingInput, 'fitting_fittingSearchField')

    def SearchFieldChanged(self, inputField, settingConfig):
        self.Search(inputField, settingConfig)

    def LoadFittingSetup(self, *args):
        if sm.GetService('fittingSvc').HasLegacyClientFittings():
            wnd = ImportLegacyFittingsWindow.Open()
        else:
            wnd = FittingMgmt.Open()
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()

    def OnSimulatedShipLoaded(self, *args):
        self.CreateCurrentShipCont()
        self.AdjustButtons()

    def AdjustButtons(self):
        pass

    def AddHardwareButtons(self):
        self.ammoPicker.Flush()
        hardware = self.GetHardware()
        foundCurrentAmmoType = False
        for moduleTypeID in hardware:
            chargeTypeIDs = sm.GetService('info').GetUsedWithTypeIDs(moduleTypeID)
            if not chargeTypeIDs:
                continue
            moduleName = evetypes.GetName(moduleTypeID)
            cont = Container(parent=self.ammoPicker, pos=(0, 0, 32, 32), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL)
            cont.hint = moduleName
            cont.fill = Fill(parent=cont, color=(1, 1, 1, 0.1))
            if self.ammoShowingForType == moduleTypeID:
                foundCurrentAmmoType = True
            else:
                cont.fill.display = False
            icon = Icon(parent=cont, name='icon', pos=(0, 0, 32, 32), align=uiconst.CENTER, state=uiconst.UI_DISABLED, typeID=moduleTypeID, ignoreSize=True)
            cont.GetMenu = (self.ModuleTypeMenu, moduleTypeID)
            cont.OnClick = (self.OnHardwareIconClicked,
             cont,
             moduleTypeID,
             chargeTypeIDs)

        if not foundCurrentAmmoType:
            self.ammoScroll.Load(contentList=[])

    def ModuleTypeMenu(self, moduleTypeID, *args):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, moduleTypeID, ignoreMarketDetails=0)

    def OnHardwareIconClicked(self, cont, moduleTypeID, chargeTypeIDs, *args):
        self.ammoShowingForType = moduleTypeID
        for child in self.ammoPicker.children:
            child.fill.display = False

        cont.fill.display = True
        godma = sm.GetService('godma')
        scrolllist = []
        for eachTypeID in chargeTypeIDs:
            label = evetypes.GetName(eachTypeID)
            data = KeyVal(label=label, typeID=eachTypeID, itemID=None, getIcon=1, OnDropData=self.OnDropData, OnDblClick=(self.TryFit, eachTypeID))
            techLevel = godma.GetTypeAttribute(eachTypeID, const.attributeTechLevel)
            metaGroup = sm.GetService('godma').GetTypeAttribute(eachTypeID, const.attributeMetaGroupID)
            scrolllist.append(((metaGroup, techLevel, label), listentry.Get('Item', data=data)))

        scrolllist = SortListOfTuples(scrolllist)
        self.ammoScroll.Load(contentList=scrolllist)

    def TryFit(self, entry, ammoTypeID):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.TryFitAmmoTypeToAll(ammoTypeID)

    def GetHardware(self):
        dogmaLocation = sm.GetService('fittingSvc').GetCurrentDogmaLocation()
        shipID = sm.GetService('fittingSvc').GetShipIDForFittingWindow()
        shipDogmaItem = dogmaLocation.dogmaItems[shipID]
        hardware = set()
        for module in shipDogmaItem.GetFittedItems().itervalues():
            if self.IsCharge(module.typeID):
                continue
            hardware.add(module.typeID)

        return hardware

    def IsCharge(self, typeID):
        return evetypes.GetCategoryID(typeID) == const.categoryCharge

    def OnFakeUpdateFittingWindow(self):
        self.AddHardwareButtons()

    def OnDropData(self, dragObj, nodes):
        node = nodes[0]
        itemKey = node.itemID
        if isinstance(itemKey, tuple):
            isCharge = True
        else:
            isCharge = False
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.UnfitModule(itemKey)
        sm.ScatterEvent('OnFakeUpdateFittingWindow')

    def AddFilterButtons2(self, buttonData, parentCont, settingConfig, func, buttonSize = 26):
        for buttonType, texturePath in buttonData:
            cont = Container(parent=parentCont, pos=(0,
             0,
             buttonSize,
             buttonSize), align=uiconst.NOALIGN, state=uiconst.UI_NORMAL)
            cont.hint = buttonType
            cont.fill = Fill(parent=cont, color=(1, 1, 1, 0.1))
            cont.settingConfig = settingConfig % buttonType
            filterOn = settings.user.ui.Get(cont.settingConfig, False)
            if not filterOn:
                cont.fill.display = False
            icon = Sprite(parent=cont, name=buttonType, pos=(0,
             0,
             buttonSize,
             buttonSize), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=texturePath)
            cont.OnClick = (func, cont, buttonType)

    def AddHardwareFilterButtons(self):
        self.filterCont = FlowContainer(parent=self, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_CENTER, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        buttonData = (('fitShip', 'res:/UI/Texture/Icons/44_32_46.png'),
         ('hiSlot', 'res:/UI/Texture/Icons/8_64_11.png'),
         ('medSlot', 'res:/UI/Texture/Icons/8_64_10.png'),
         ('loSlot', 'res:/UI/Texture/Icons/8_64_9.png'),
         ('rigSlot', 'res:/UI/Texture/Icons/68_64_1.png'),
         ('powergrid', 'res:/UI/Texture/classes/Market/powerRequirementNotMet.png'),
         ('cpu', 'res:/UI/Texture/classes/Market/cpuRequirementNotMet.png'),
         ('skills', 'res:/UI/Texture/classes/Skills/doNotHaveFrame.png'))
        self.AddFilterButtons2(buttonData, self.filterCont, 'fitting_filter_hardware_%s', self.HardwareFilterClicked)

    def AddFittingFilterButtons(self):
        self.fittingFilterCont = Container(name='fittingFilterCont', parent=self, align=uiconst.TOTOP, height=26, padding=(10, 4, 10, 4))
        filterCont = Container(name='filterCont', parent=self.fittingFilterCont, align=uiconst.TOLEFT, width=50)
        fittingFilter = FlowContainer(name='fittingFilter', parent=filterCont, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_LEFT, padTop=4, contentSpacing=uiconst.BUTTONGROUPMARGIN)
        self.fittingSearchCont = Container(name='fittingSearchCont', parent=self.fittingFilterCont, align=uiconst.TOALL, padTop=5)
        buttonData = (('personalFittings', 'res:/UI/Texture/WindowIcons/member.png'), ('corpFittings', 'res:/UI/Texture/WindowIcons/corporation.png'))
        self.AddFilterButtons2(buttonData, fittingFilter, 'fitting_filter_hardware_%s', self.FittingFilterClicked, 20)

    def FittingFilterClicked(self, cont, buttonType):
        self.FilterButtonClicked(cont, buttonType)
        self.LoadFittings()

    def HardwareFilterClicked(self, cont, buttonType):
        self.FilterButtonClicked(cont, buttonType)
        self.LoadHardware()

    def FilterButtonClicked(self, cont, buttonType):
        settingConfig = cont.settingConfig
        filterOn = settings.user.ui.Get(settingConfig, False)
        settings.user.ui.Set(settingConfig, not filterOn)
        if filterOn:
            cont.fill.display = False
        else:
            cont.fill.display = True

    def GetSearchResults(self):
        listProvider = SearchBrowserListProvider(self.fittingSvc.searchFittingHelper, self.OnDropData)
        scrolllist = listProvider.GetSearchResults()
        return scrolllist

    def CreateCurrentShipCont(self):
        self.shipCont.Flush()
        Frame(parent=self.shipCont, color=(1, 1, 1, 0.1))
        activeShip = GetActiveShip()
        clientDogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        shipDogmaItem = clientDogmaLocation.GetShip()
        shipTypeID = shipDogmaItem.typeID
        icon = Icon(parent=self.shipCont, pos=(0, 0, 40, 40), ignoreSize=True, state=uiconst.UI_DISABLED)
        if self.fittingSvc.IsShipSimulated():
            self.shipCont.OnClick = self.ExitSimulation
            icon.LoadIconByTypeID(shipTypeID)
        else:
            self.shipCont.OnClick = self.LoadCurrentShip
            hologramTexture = inventorycommon.typeHelpers.GetGraphic(shipTypeID).isisIconPath
            icon.LoadTexture(hologramTexture)
        shipName = cfg.evelocations.Get(activeShip).name
        text = '%s<br>%s' % (evetypes.GetName(shipTypeID), shipName)
        self.shipnametext = EveLabelMedium(text=text, parent=self.shipCont, align=uiconst.TOTOP, top=2, padLeft=48)
