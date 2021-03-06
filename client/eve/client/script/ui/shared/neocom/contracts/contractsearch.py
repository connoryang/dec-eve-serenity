#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\contracts\contractsearch.py
import evetypes
import form
import uiprimitives
import uicontrols
import uix
import uiutil
import listentry
import uthread
import util
import blue
import uicls
import carbonui.const as uiconst
import contractscommon as cc
from contractutils import GetContractTitle, SelectItemTypeDlg
import copy
import sys
import xtriui
import localization
import searchUtil
from eve.client.script.ui.control.buttons import IconButton
LEFT_WIDTH = 150
MILLION = 1000000
MAXJUMPROUTENUM = 100
PAGINGRANGE = 10
NUM_SAVED_LOCATIONS = 5
MAX_NUM_MILLIONS = 100000
CONTRACT_SEARCH_MAPPINGS = {cc.SORT_ID: 'UI/Contracts/ContractsSearch/columnCreated',
 cc.SORT_EXPIRED: 'UI/Contracts/ContractsSearch/columnTimeLeft',
 cc.SORT_PRICE: 'UI/Contracts/ContractsSearch/columnPrice',
 cc.SORT_REWARD: 'UI/Contracts/ContractsSearch/columnReward',
 cc.SORT_COLLATERAL: 'UI/Contracts/ContractsSearch/columnCollateral'}

class ContractSearchWindow(uiprimitives.Container):
    __guid__ = 'form.ContractSearchWindow'
    default_clipChildren = True

    def GetTypesFromName(self, itemTypeName, categoryID, groupID):
        itemTypes = searchUtil.QuickSearch(itemTypeName, [const.searchResultInventoryType])
        retDict = {}
        for x in itemTypes or []:
            if not evetypes.IsPublished(x):
                continue
            if groupID and evetypes.GetGroupID(x) != groupID:
                continue
            if categoryID and evetypes.GetCategoryID(x) != categoryID:
                continue
            retDict[x] = evetypes.GetName(x)

        return retDict

    def ChangeViewMode(self, viewMode):
        oldViewMode = int(not viewMode)
        prefs.SetValue('contractsSimpleView', viewMode)
        blue.pyos.synchro.Yield()
        self.sr.Get('viewMode%s' % oldViewMode, None).Deselect()
        if self.currPage in self.pageData:
            self.RenderPage()

    def PopulateSortCombo(self):
        contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
        oldestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/OldestFirst')
        newestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/NewestFirst')
        shortestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/ShortestFirst')
        longestFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/LongestFirst')
        lowFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/LowerstFirst')
        highFirst = localization.GetByLabel('UI/Contracts/ContractsSearch/HighestFirst')
        opt = [(localization.GetByLabel('UI/Contracts/ContractsSearch/DateCreatedOption', text=oldestFirst), (cc.SORT_ID, 0)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/DateCreatedOption', text=newestFirst), (cc.SORT_ID, 1)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/TimeLeftOption', text=shortestFirst), (cc.SORT_EXPIRED, 0)),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/TimeLeftOption', text=longestFirst), (cc.SORT_EXPIRED, 1))]
        if contractType == const.conTypeCourier:
            opt.extend([(localization.GetByLabel('UI/Contracts/ContractsSearch/RewardOption', text=lowFirst), (cc.SORT_REWARD, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/RewardOption', text=highFirst), (cc.SORT_REWARD, 1)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/CollateralOption', text=lowFirst), (cc.SORT_COLLATERAL, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/CollateralOption', text=highFirst), (cc.SORT_COLLATERAL, 1)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/VolumnOptions', text=lowFirst), (cc.SORT_VOLUME, 0)),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/VolumnOptions', text=highFirst), (cc.SORT_VOLUME, 1))])
        else:
            opt.extend([(localization.GetByLabel('UI/Contracts/ContractsSearch/PriceOption', text=lowFirst), (cc.SORT_PRICE, 0)), (localization.GetByLabel('UI/Contracts/ContractsSearch/PriceOption', text=highFirst), (cc.SORT_PRICE, 1))])
        sel = settings.user.ui.Get('contracts_search_sort_%s' % contractType, (cc.SORT_PRICE, 0) if contractType == cc.CONTYPE_AUCTIONANDITEMECHANGE else None)
        self.sr.fltSort.LoadOptions(opt, sel)

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.svc = sm.GetService('contracts')
        self.inited = False
        self.searchThread = None
        self.currPage = 0
        self.numPages = 0
        self.pageData = {}
        self.pages = {0: None}
        self.fetchingContracts = 0
        self.mouseCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)
        pad = 2 * const.defaultPadding
        self.sr.leftSide = uiprimitives.Container(name='leftSide', parent=self, align=uiconst.TOLEFT, width=LEFT_WIDTH, padding=(pad,
         0,
         pad,
         0))
        self.sr.topContainer = uiprimitives.Container(name='topCont', parent=self, pos=(0, 2, 0, 26), align=uiconst.TOTOP)
        self.sr.viewMode0 = icon = uicontrols.MiniButton(icon='ui_38_16_157', selectedIcon='ui_38_16_173', mouseOverIcon='ui_38_16_189', parent=self.sr.topContainer, pos=(6, 10, 16, 16), align=uiconst.TOPLEFT)
        icon.hint = localization.GetByLabel('UI/Common/Details')
        icon.Click = lambda : self.ChangeViewMode(0)
        self.sr.viewMode1 = icon = uicontrols.MiniButton(icon='ui_38_16_158', selectedIcon='ui_38_16_174', mouseOverIcon='ui_38_16_190', parent=self.sr.topContainer, pos=(22, 10, 16, 16), align=uiconst.TOPLEFT)
        icon.hint = localization.GetByLabel('UI/Inventory/List')
        icon.Click = lambda : self.ChangeViewMode(1)
        self.sr.Get('viewMode%s' % int(prefs.GetValue('contractsSimpleView', 0) or 0), None).Select()
        sortCont = c = uiprimitives.Container(name='sortCont', parent=self.sr.topContainer, pos=(0, 12, 0, 20), align=uiconst.TOTOP)
        sortDirWidth = 62
        self.sr.fltSort = c = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/SortPageBy'), parent=sortCont, options=[], name='sort', align=uiconst.TOPRIGHT, callback=self.ComboChange)
        self.PopulateSortCombo()
        c.width = 160
        c.left = 4
        self.sr.contractlistParent = contractlistParent = uiprimitives.Container(name='contractlistParent', align=uiconst.TOALL, padding=(const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding), parent=self)
        hint, icon, isFiltered = self.GetClientFilterTextAndIcon()
        if settings.user.ui.Get('contracts_search_expander_clientFilterExpander', 0) and prefs.GetValue('contractsClientFilters2', 1):
            filterState = uiconst.UI_PICKCHILDREN
        else:
            filterState = uiconst.UI_HIDDEN
        self.sr.filterCont = uiprimitives.Container(name='filterCont', parent=self.sr.contractlistParent, pos=(0, 0, 0, 54), align=uiconst.TOBOTTOM, idx=0, state=filterState)
        expanderCont = uiprimitives.Container(name='clientFilterExpander', parent=self.sr.contractlistParent, pos=(0, 0, 0, 28), align=uiconst.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, padTop=0)
        self.sr.expanderTextCont = uiprimitives.Container(name='expanderTextCont', parent=expanderCont, align=uiconst.TOLEFT, pos=(0, 0, 200, 0), state=uiconst.UI_NORMAL)
        if prefs.GetValue('contractsClientFilters2', 1):
            self.sr.expanderTextCont.OnClick = self.ToggleClientFilters
        foundLabelText = localization.GetByLabel('UI/Contracts/ContractsSearch/NoSearch')
        self.sr.foundLabel = uicontrols.EveLabelSmall(text=foundLabelText, parent=self.sr.expanderTextCont, align=uiconst.TOPLEFT, left=2, top=5)
        self.sr.expanderTextCont.width = self.sr.foundLabel.textwidth + 50
        pageArea = uiprimitives.Container(name='pageArea', parent=expanderCont, pos=(10,
         2,
         25 * PAGINGRANGE + 40,
         20), align=uiconst.CENTERRIGHT, state=uiconst.UI_NORMAL)
        fwdCont = uiprimitives.Container(name='fwdCont', parent=pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.sr.pageFwdBtn = IconButton(name='pageFwdBtn', icon='ui_38_16_224', parent=fwdCont, pos=(0, 0, 20, 20), align=uiconst.CENTERRIGHT, iconPos=(-2, 0, 16, 16), iconAlign=uiconst.CENTER, func=self.DoPageNext, state=uiconst.UI_HIDDEN)
        self.sr.pagingCont = uiprimitives.Container(name='pagingCont', parent=pageArea, pos=(0,
         0,
         25 * PAGINGRANGE,
         0), align=uiconst.TORIGHT)
        backCont = uiprimitives.Container(name='backCont', parent=pageArea, pos=(0, 0, 20, 0), align=uiconst.TORIGHT, state=uiconst.UI_NORMAL)
        self.sr.pageBackBtn = IconButton(name='pageBackBtn', icon='ui_38_16_223', parent=backCont, pos=(0, 0, 20, 20), align=uiconst.CENTERLEFT, iconPos=(0, 0, 16, 16), iconAlign=uiconst.CENTER, func=self.DoPagePrev, state=uiconst.UI_HIDDEN)
        self.sr.pageFilterIcon = IconButton(name='pageFilterIcon', icon=icon, parent=self.sr.expanderTextCont, hint=hint, pos=(10, 0, 16, 16), align=uiconst.CENTERLEFT)
        self.sr.contractlist = contractlist = uicontrols.Scroll(parent=contractlistParent, name='contractsearchlist')
        contractlist.sr.id = 'contractlist'
        contractlist.multiSelect = 0
        contractlistParent.top = 5
        contractlist.ShowHint(localization.GetByLabel('UI/Contracts/ContractsSearch/ClickSearchHint'))
        self.sr.loadingWheel = uicls.LoadingWheel(parent=self.sr.contractlist, align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.sr.loadingWheel.Hide()
        contractlist.sr.defaultColumnWidth = {localization.GetByLabel('UI/Contracts/ContractsSearch/columPickup'): 120,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'): 200,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnBids'): 20,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'): 90,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnRoute'): 80,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'): 60,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'): 70,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnPrice'): 100,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'): 100,
         localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'): 100}
        self.InitFilters()

    def GetContractFiltersMenu(self, *args):
        m = []
        m.append((uiutil.MenuLabel('UI/Contracts/ContractsSearch/ExcludeUnreacable'), self.ToggleExcludeUnreachable, (None,)))
        m.append((uiutil.MenuLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), self.ToggleExcludeIgnored, (None,)))
        return m

    def ToggleExcludeUnreachable(self, *args):
        k = 'contracts_search_client_excludeunreachable'
        v = 0 if settings.user.ui.Get(k, 0) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()

    def ToggleExcludeIgnored(self, *args):
        k = 'contracts_search_client_excludeignore'
        v = 0 if settings.user.ui.Get(k, 1) else 1
        settings.user.ui.Set(k, v)
        if self.currPage in self.pageData:
            self.RenderPage()

    def InitFilters(self):
        leftSide = self.sr.leftSide
        leftSide.Flush()
        EDIT_WIDTH = 61
        self.sr.caption = uicontrols.CaptionLabel(text=localization.GetByLabel('UI/Contracts/ContractsSearch/ContractSearch'), parent=leftSide, align=uiconst.TOTOP, top=4, uppercase=False, letterspace=0)
        contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
        MENU_HEIGHT = 28
        self.sr.menu = uiprimitives.Container(name='menu', parent=leftSide, align=uiconst.TOTOP, pos=(0,
         0,
         0,
         MENU_HEIGHT), padding=(2, 0, 2, 0))
        self.pushButtons = uicls.ToggleButtonGroup(parent=self.sr.menu, align=uiconst.TOTOP, callback=self.OnButtonSelected)
        for btnID, label, panel in ((cc.CONTYPE_AUCTIONANDITEMECHANGE, localization.GetByLabel('UI/Contracts/ContractsSearch/tabBuyAndSell'), None), (const.conTypeCourier, localization.GetByLabel('UI/Contracts/ContractsSearch/tabCourier'), None)):
            self.pushButtons.AddButton(btnID, label, panel)

        self.pushButtons.SelectByID(contractType)
        if contractType != const.conTypeCourier:
            typeCont = uiprimitives.Container(name='typeCont', parent=leftSide, pos=(0, -12, 0, 41), align=uiconst.TOTOP)
            self.sr.typeName = c = uicontrols.SinglelineEdit(name='type', parent=typeCont, label='', hinttext=localization.GetByLabel('UI/Wallet/WalletWindow/ItemType'), setvalue=settings.user.ui.Get('contracts_search_typename', ''), align=uiconst.TOTOP, padTop=20, OnReturn=self.DoSearch)
            self.sr.typeName.ShowClearButton(showOnLetterCount=3)
            self.sr.typeName.OnDropData = self.OnDropType
        locationCont = uiprimitives.Container(name='locationCont', parent=leftSide, padTop=-3, height=40, align=uiconst.TOTOP)
        self.sr.fltLocation = c = uicontrols.Combo(label=localization.GetByLabel('UI/Common/Location'), parent=locationCont, options=[], name='location', callback=self.ComboChange, align=uiconst.TOTOP, padTop=20)
        self.PopulateLocationCombo()
        self.sr.advancedCont = advancedCont = uiprimitives.Container(name='advancedCont', parent=leftSide, padTop=const.defaultPadding, align=uiconst.TOTOP)
        expanded = settings.user.ui.Get('contracts_search_expander_advanced', 0)
        self.sr.advancedDivider = self.GetExpanderDivider(leftSide, 'advanced', localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowLessOptions'), localization.GetByLabel('UI/Contracts/ContractsSearch/buttonShowMoreOptions'), expanded, self.sr.advancedCont, padTop=const.defaultPadding)
        if contractType != const.conTypeCourier:
            contractOptions = [(localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/comboSellContracts'), 2),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/comboWantToBuy'), 3),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/combo'), 1),
             (localization.GetByLabel('UI/Contracts/ContractsSearch/comboExcluedWantToBuy'), 4)]
            self.sr.fltContractOptions = c = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsWindow/ContractType'), parent=advancedCont, options=contractOptions, name='contractOptions', select=settings.user.ui.Get('contracts_search_contractOptions', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=17)
            catOptions = [(localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None)]
            categories = []
            principalCategories = [const.categoryBlueprint, const.categoryModule, const.categoryShip]
            for categoryID in evetypes.IterateCategories():
                if categoryID > 0 and evetypes.IsCategoryPublishedByCategory(categoryID) and categoryID not in principalCategories:
                    categories.append([evetypes.GetCategoryNameByCategory(categoryID), categoryID, 0])

            categories.sort()
            for catID in principalCategories:
                categoryName = evetypes.GetCategoryNameByCategory(catID)
                catOptions.append([categoryName, (catID, 0)])
                if catID == const.categoryBlueprint:
                    catOptions.append([localization.GetByLabel('UI/Contracts/ContractsSearch/BlueprintCategoryOriginal', categoryName=categoryName), (catID, cc.SEARCHHINT_BPO)])
                    catOptions.append([localization.GetByLabel('UI/Contracts/ContractsSearch/BlueprintCategoryCopy', categoryName=categoryName), (catID, cc.SEARCHHINT_BPC)])

            catOptions.append(['', -1])
            for c in categories:
                catOptions.append((c[0], (c[1], c[2])))

            self.sr.fltCategories = c = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/ContractCategory'), parent=advancedCont, options=catOptions, name='category', select=settings.user.ui.Get('contracts_search_category', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=17)
            grpOptions = [(localization.GetByLabel('UI/Contracts/ContractsSearch/SelectCategory'), None)]
            self.sr.fltGroups = c = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/contractroup'), parent=advancedCont, options=grpOptions, name='group', select=settings.user.ui.Get('contracts_search_group', None), align=uiconst.TOTOP, callback=self.ComboChange, padTop=20)
            self.sr.fltExcludeMultiple = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelExcludeMultipleItems'), configName='contracts_search_excludemultiple', checked=settings.user.ui.Get('contracts_search_excludemultiple', 0), parent=advancedCont, callback=self.CheckBoxChange, padTop=4, align=uiconst.TOTOP)
            self.sr.fltExactType = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelExactTypeMatch'), configName='contracts_search_exacttype', checked=settings.user.ui.Get('contracts_search_exacttype', 0), parent=advancedCont, callback=self.CheckBoxChange)
            self.PopulateGroupCombo(isSel=True)
            self.sr.priceCont = cont = uiprimitives.Container(name='priceCont', parent=advancedCont, padTop=19, height=20, align=uiconst.TOTOP)
            self.sr.fltMinPrice = c = uicontrols.SinglelineEdit(name='minprice', parent=cont, label=localization.GetByLabel('UI/Contracts/ContractsSearch/labelPriceMillions'), width=EDIT_WIDTH, align=uiconst.TOPLEFT, hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMin'), ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_minprice', ''), OnReturn=self.DoSearch)
            uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Common/ToNumber'), parent=cont, align=uiconst.CENTER)
            self.sr.fltMaxPrice = c = uicontrols.SinglelineEdit(name='maxprice', parent=cont, width=EDIT_WIDTH, align=uiconst.TOPRIGHT, label='', hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_maxprice', ''), OnReturn=self.DoSearch)
        options = [(localization.GetByLabel('UI/Generic/Public'), const.conAvailPublic), (localization.GetByLabel('UI/Contracts/ContractsWindow/Me'), const.conAvailMyself)]
        if not util.IsNPC(session.corpid):
            options.append((localization.GetByLabel('UI/Generic/MyCorp'), const.conAvailMyCorp))
        if session.allianceid:
            options.append((localization.GetByLabel('UI/Generic/MyAlliance'), const.conAvailMyAlliance))
        if contractType == const.conTypeCourier:
            dropoffCont = uiprimitives.Container(name='dropoffCont', parent=advancedCont, padTop=9, height=20, align=uiconst.TOTOP)
            w = 22 + 2 * const.defaultPadding
            self.sr.fltDropOff = c = uicontrols.SinglelineEdit(name='dropoff', parent=dropoffCont, setvalue=settings.user.ui.Get('contracts_search_dropoff', ''), align=uiconst.TOTOP, label='', padRight=w, hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/DropOffLocation'), OnReturn=self.OnDropOffReturn)
            self.sr.fltDropOff.ShowClearButton(showOnLetterCount=3)
            self.sr.fltDropOffID = settings.user.ui.Get('contracts_search_dropoff_id', None)
            buttonbox = uiprimitives.Container(name='buttonbox', align=uiconst.TOPRIGHT, parent=dropoffCont, pos=(0, 1, 20, 20))
            btn = uix.GetBigButton(10, buttonbox, width=20, height=20)
            btn.sr.icon.LoadIcon('ui_38_16_228')
            btn.OnClick = self.ParseDropOff
            self.sr.rewardCont = rewardCont = uiprimitives.Container(name='rewardCont', parent=advancedCont, padTop=19, height=20, align=uiconst.TOTOP)
            self.sr.fltMinReward = c = uicontrols.SinglelineEdit(name='minreward', parent=rewardCont, width=EDIT_WIDTH, label=localization.GetByLabel('UI/Contracts/ContractsSearch/CourierRewardInMillions'), hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMin'), left=0, top=0, ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_minreward', ''), OnReturn=self.DoSearch)
            uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Common/ToNumber'), parent=rewardCont, align=uiconst.TOPLEFT, pos=(c.width + 8,
             4,
             20,
             0))
            self.sr.fltMaxReward = c = uicontrols.SinglelineEdit(name='maxreward', parent=rewardCont, label='', hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_maxreward', ''), OnReturn=self.DoSearch)
            self.sr.collateralCont = cont = uiprimitives.Container(name='collateralCont', parent=advancedCont, pos=(0, 17, 0, 20), align=uiconst.TOTOP)
            self.sr.fltMinCollateral = c = uicontrols.SinglelineEdit(name='mincollateral', parent=cont, pos=(0,
             0,
             EDIT_WIDTH,
             0), label=localization.GetByLabel('UI/Contracts/ContractsSearch/CourierCollateralInMillions'), hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMin'), ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_mincollateral', ''), OnReturn=self.DoSearch)
            uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Common/ToNumber'), parent=cont, align=uiconst.TOPLEFT, width=20, left=c.width + 8, top=4)
            self.sr.fltMaxCollateral = c = uicontrols.SinglelineEdit(name='maxcollateral', parent=cont, align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), label='', hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), ints=(0, MAX_NUM_MILLIONS), setvalue=settings.user.ui.Get('contracts_search_maxcollateral', ''), OnReturn=self.DoSearch)
            self.sr.volumeCont = cont = uiprimitives.Container(name='volumeCont', parent=advancedCont, pos=(0, 17, 0, 20), align=uiconst.TOTOP)
            self.sr.fltMinVolume = c = uicontrols.SinglelineEdit(name='minvolume', parent=cont, pos=(0,
             0,
             EDIT_WIDTH,
             0), label=localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'), hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMin'), ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_minvolume', ''), OnReturn=self.DoSearch)
            uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Common/ToNumber'), parent=cont, align=uiconst.TOPLEFT, width=20, left=c.width + 8, top=4)
            self.sr.fltMaxVolume = c = uicontrols.SinglelineEdit(name='maxvolume', parent=cont, align=uiconst.TOPRIGHT, pos=(0,
             0,
             EDIT_WIDTH,
             0), label='', hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), ints=(0, None), setvalue=settings.user.ui.Get('contracts_search_maxvolume', ''), OnReturn=self.DoSearch)
        contractAvailability = settings.user.ui.Get('contracts_search_avail', const.conAvailPublic)
        self.sr.fltAvail = c = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsSearch/Availability'), parent=advancedCont, options=options, name='avail', select=contractAvailability, callback=self.ComboChange, align=uiconst.TOTOP, pos=(0, 18, 140, 20))
        securityCont = c = uiprimitives.Container(name='securityCont', parent=advancedCont, pos=(0, 6, 0, 30), align=uiconst.TOTOP)
        c = uicontrols.EveLabelSmall(text=localization.GetByLabel('UI/Contracts/ContractsSearch/SecurityFilters'), parent=securityCont, left=5, top=0, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT)
        self.sr.fltSecHigh = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Common/HighSecurityShort'), configName='contracts_search_sechigh', checked=settings.user.ui.Get('contracts_search_sechigh', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/HighSec'), width=55, left=const.defaultPadding, top=12, align=uiconst.TOPLEFT)
        self.sr.fltSecLow = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Common/LowSecurityShort'), configName='contracts_search_seclow', checked=settings.user.ui.Get('contracts_search_seclow', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/LowSec'), width=55, left=c.left + c.width + 5, top=12, align=uiconst.TOPLEFT)
        self.sr.fltSecNull = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Common/NullSecurityShort'), configName='contracts_search_secnull', checked=settings.user.ui.Get('contracts_search_secnull', 1), parent=securityCont, callback=self.CheckBoxChange, hint=localization.GetByLabel('UI/Common/NullSec'), width=55, left=c.left + c.width + 5, top=12, align=uiconst.TOPLEFT)
        issuerCont = uiprimitives.Container(name='issuerCont', parent=advancedCont, pos=(0, 6, 0, 20), align=uiconst.TOTOP)
        w = 22 + 2 * const.defaultPadding
        issuerID = settings.user.ui.Get('contracts_search_issuer_id', None)
        issuerName = ''
        if issuerID is not None:
            issuerName = cfg.eveowners.Get(issuerID).name
        self.sr.fltIssuer = c = uicontrols.SinglelineEdit(name='issuer', parent=issuerCont, setvalue=issuerName, align=uiconst.TOTOP, padding=(0,
         0,
         w,
         0), hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'), OnReturn=self.DoSearch, OnChange=self.OnIssuerChange)
        self.sr.fltIssuer.ShowClearButton(showOnLetterCount=3)
        self.OnIssuerChange(issuerName)
        self.sr.fltIssuerID = issuerID
        self.sr.fltIssuer.OnDropData = self.OnDropIssuer
        buttonbox = uiprimitives.Container(name='buttonbox', align=uiconst.TOPRIGHT, parent=issuerCont, pos=(0, 1, 20, 20))
        btn = uix.GetBigButton(10, buttonbox, width=20, height=20)
        btn.sr.icon.LoadIcon('ui_38_16_228')
        btn.OnClick = self.ParseIssuers
        for each in ['fltMinPrice',
         'fltMaxPrice',
         'fltMinReward',
         'fltMaxReward',
         'fltMinCollateral',
         'fltMaxCollateral',
         'fltMinVolume',
         'fltMaxVolume']:
            wnd = getattr(self.sr, each, None)
            try:
                if not settings.user.ui.Get('contracts_search_%s' % wnd.name, ''):
                    wnd.SetText('')
                    wnd.CheckHintText()
            except:
                sys.exc_clear()

        advancedCont.height = sum([ each.height + each.padTop + each.padBottom + each.top for each in advancedCont.children ])
        self.sr.filterCont.Flush()
        uicontrols.Frame(parent=self.sr.filterCont, color=(0.5, 0.5, 0.5, 0.2))
        leftCont = uiprimitives.Container(name='leftCont', parent=self.sr.filterCont, pos=(14, 0, 200, 0), align=uiconst.TOLEFT)
        rightCont = uiprimitives.Container(name='rightCont', parent=self.sr.filterCont, pos=(0, 0, 0, 0), align=uiconst.TOALL)
        self.sr.fltClientExcludeUnreachable = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeUnreacable'), configName='contracts_search_client_excludeunreachable', checked=settings.user.ui.Get('contracts_search_client_excludeunreachable', 0), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        self.sr.fltClientExcludeIgnore = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), configName='contracts_search_client_excludeignore', checked=settings.user.ui.Get('contracts_search_client_excludeignore', 1), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        self.sr.fltClientOnlyCurrentSecurity = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/OnlyCurrentSecurity'), configName='contracts_search_client_currentsecurity', checked=settings.user.ui.Get('contracts_search_client_currentsecurity', 0), parent=leftCont, callback=self.FilterCheckBoxChange, pos=(0, 0, 160, 20), align=uiconst.TOTOP)
        jumpSettings = settings.user.ui.Get('contracts_search_client_maxjumps', 0)
        self.sr.fltClientMaxJumps = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaximumJumps'), configName='maxjumps', checked=jumpSettings, parent=rightCont, callback=self.FilterCheckBoxChange, pos=(0, 6, 160, 40), align=uiconst.TOPLEFT)
        numJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', 10)
        self.sr.maxjumpsInput = c = uicontrols.SinglelineEdit(name='maxjumpsInput', parent=rightCont, align=uiconst.TOPLEFT, pos=(self.sr.fltClientMaxJumps.width + 20,
         5,
         40,
         10), label='', setvalue=str(numJumps), hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), ints=(0, MAXJUMPROUTENUM), OnReturn=self.OnJumpInputReturn, OnFocusLost=self.OnJumpFocusLost)
        if not jumpSettings:
            c.Disable()
        cLabel = self.sr.fltClientMaxJumps.sr.label
        inputLeft = cLabel.textwidth + cLabel.left + 20
        if contractType == const.conTypeCourier:
            routeSettings = settings.user.ui.Get('contracts_search_client_maxroute', 0)
            self.sr.fltClientMaxRoute = c = uicontrols.Checkbox(text=localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaxRoute'), configName='maxroute', checked=routeSettings, parent=rightCont, callback=self.FilterCheckBoxChange, pos=(0, 32, 160, 40), align=uiconst.TOPLEFT)
            cLabel = self.sr.fltClientMaxRoute.sr.label
            inputLeft = max(inputLeft, cLabel.textwidth + cLabel.left + 20)
            self.sr.fltClientMaxRoute.width = inputLeft
            numRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', 10)
            self.sr.maxrouteInput = c = uicontrols.SinglelineEdit(name='maxrouteInput', parent=rightCont, align=uiconst.TOPLEFT, pos=(inputLeft + 30,
             31,
             40,
             10), label='', setvalue=numRoute, hinttext=localization.GetByLabel('UI/Contracts/ContractsSearch/hintMax'), ints=(0, MAXJUMPROUTENUM), OnReturn=self.OnRouteInputReturn, OnFocusLost=self.OnRouteFocusLost)
            if not routeSettings:
                c.Disable()
        self.sr.fltClientMaxJumps.width = inputLeft
        self.sr.maxjumpsInput.left = inputLeft + 30
        hint, icon, isFiltered = self.GetClientFilterTextAndIcon()
        self.sr.pageFilterIcon.hint = hint
        self.sr.pageFilterIcon.LoadIcon(icon)
        self.sr.pageFilterIcon.state = uiconst.UI_HIDDEN
        buttonbox = uiprimitives.Container(name='buttonbox', align=uiconst.TOBOTTOM, parent=leftSide, pos=(0, 0, 0, 40), idx=0)
        self.sr.SearchButton = btn = uix.GetBigButton(10, buttonbox, width=140, height=32)
        btn.SetInCaption(localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch'))
        btn.SetAlign(uiconst.CENTER)
        btn.OnClick = self.DoSearch
        self.inited = True

    def SetInitialFocus(self):
        uicore.registry.SetFocus(self.sr.contractlist)

    def OnButtonSelected(self, mode):
        if mode == settings.user.ui.Get('contracts_search_type', const.conTypeItemExchange):
            return
        settings.user.ui.Set('contracts_search_type', mode)
        self.PopulateSortCombo()
        uthread.new(self.InitFilters)

    def ComboChange(self, wnd, *args):
        if wnd.name == 'sort':
            contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
            settings.user.ui.Set('contracts_search_sort_%s' % contractType, wnd.GetValue())
        else:
            settings.user.ui.Set('contracts_search_%s' % wnd.name, wnd.GetValue())
        if wnd.name == 'category':
            self.PopulateGroupCombo()
        elif wnd.name == 'type':
            self.InitFilters()
        elif wnd.name == 'location':
            v = wnd.GetValue()
            if v == 10:
                self.PickLocation()
        elif wnd.name == 'sort':
            val = wnd.GetValue()
            sortBy = localization.GetByLabel(CONTRACT_SEARCH_MAPPINGS.get(val[0], 'UI/Contracts/ContractsSearch/columnCreated'))
            pr = settings.user.ui.Get('scrollsortby_%s' % uiconst.SCROLLVERSION, {})
            pr[self.sr.contractlist.sr.id] = (sortBy, not not val[1])
            if self.currPage in self.pageData:
                self.DoSearch()

    def PickLocation(self):
        desc = localization.GetByLabel('UI/Contracts/ContractsSearch/labelEnterLocationName')
        ret = uiutil.NamePopup(localization.GetByLabel('UI/Contracts/ContractsSearch/labelEnterName'), desc, '', maxLength=20)
        if ret:
            name = ret.lower()
            locationID = self.SearchLocation(name)
            if locationID:
                self.DoPickLocation(locationID)

    def DoPickLocation(self, locationID):
        settings.user.ui.Set('contracts_search_location', locationID)
        customLocations = settings.user.ui.Get('contracts_search_customlocations', [])
        loc = (cfg.evelocations.Get(locationID).name, locationID)
        try:
            customLocations.remove(loc)
        except:
            pass

        customLocations.append(loc)
        if len(customLocations) > NUM_SAVED_LOCATIONS:
            del customLocations[0]
        settings.user.ui.Set('contracts_search_customlocations', customLocations)
        self.PopulateLocationCombo()

    def CheckBoxChange(self, wnd, *args):
        pass

    def OnGlobalMouseUp(self, obj, msgID, param):
        if uicore.uilib.mouseOver is self.sr.secCont or uiutil.IsUnder(obj, self.sr.secCont):
            return 1
        return 1

    def GetClientFilterTextAndIcon(self, *args):
        contractType = settings.user.ui.Get('contracts_search_type', const.conTypeItemExchange)
        excluded = ''
        for each, text, default in [('excludeunreachable', localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeUnreacable'), 1), ('excludeignore', localization.GetByLabel('UI/Contracts/ContractsSearch/ExcludeIgnored'), 1), ('currentsecurity', localization.GetByLabel('UI/Contracts/ContractsSearch/OnlyCurrentSecurity'), 0)]:
            isChecked = settings.user.ui.Get('contracts_search_client_%s' % each, default)
            if isChecked is None:
                continue
            if isChecked:
                excluded += '<br>%s' % text

        isChecked = settings.user.ui.Get('contracts_search_client_maxjumps', None)
        if isChecked:
            maxJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', '-')
            excluded += '<br>%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaximumJumpsDisttance', maxJumps=maxJumps)
        if contractType == const.conTypeCourier:
            isChecked = settings.user.ui.Get('contracts_search_client_maxroute', None)
            if isChecked:
                maxRoute = settings.user.ui.Get('contracts_search_client_maxroute_num', '-')
                excluded += '<br>%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/labelMaxRouteDistance', maxRoute=maxRoute)
        hintText = '<b>%s</b>' % localization.GetByLabel('UI/Contracts/ContractsSearch/hintPageFilter')
        if excluded:
            hintText += excluded
            icon = 'ui_38_16_205'
        else:
            hintText += '<br>%s' % localization.GetByLabel('UI/Common/Show all')
            icon = 'ui_38_16_204'
        return (hintText, icon, bool(excluded))

    def UpdatePaging(self, currentPage, numPages):
        self.sr.pagingCont.Flush()
        if numPages == 1:
            self.sr.pageBackBtn.state = uiconst.UI_HIDDEN
            self.sr.pageFwdBtn.state = uiconst.UI_HIDDEN
            return
        currentRange = (currentPage - 1) / PAGINGRANGE * PAGINGRANGE
        pages = []
        for i in xrange(0, PAGINGRANGE):
            page = currentRange + i
            if page >= numPages:
                break
            pages.append(page)

        left = 0
        for pageNum in pages:
            pageCont = IconButton(name='pageNum', parent=self.sr.pagingCont, pos=(left,
             0,
             20,
             0), align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, padTop=0, func=self.GoToPage, args=(pageNum,))
            pageName = pageNum + 1
            if pageNum + 1 == currentPage:
                f = uicontrols.Frame(parent=pageCont, frameConst=uiconst.FRAME_BORDER2_CORNER0)
                f.SetAlpha(1.0)
                bold = 1
            else:
                f = uicontrols.Frame(parent=pageCont, frameConst=uiconst.FRAME_BORDER1_CORNER0)
                bold = 0
            uicontrols.EveLabelMedium(text=pageName, parent=pageCont, pos=(1, 1, 0, 0), align=uiconst.CENTER, bold=bold)
            left = 5

        backState = uiconst.UI_NORMAL
        if currentPage <= 1:
            backState = uiconst.UI_HIDDEN
        fwdState = uiconst.UI_NORMAL
        if currentPage >= numPages:
            fwdState = uiconst.UI_HIDDEN
        self.sr.pageBackBtn.state = backState
        self.sr.pageFwdBtn.state = fwdState
        self.sr.pagingCont.width = 25 * len(pages) - 5

    def GetExpanderDivider(self, parent, name, onText, offText, nowExpanded, collapsingCont, belowCollapsed = 1, padTop = 0, *args):
        expanderCont = uiprimitives.Container(name=name, parent=parent, height=18, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, padTop=padTop)
        expanderCont.onText = onText
        expanderCont.offText = offText
        expanderCont.collapsingCont = collapsingCont
        if not belowCollapsed:
            expanderCont.SetAlign(uiconst.TOBOTTOM)
        expandText = [offText, onText][nowExpanded]
        expanderCont.label = uicontrols.EveLabelSmall(text=expandText, parent=expanderCont, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=4, bold=True)
        expanderCont.OnClick = (self.ToggleAdvanced, expanderCont)
        expanderCont.expander = expander = IconButton(icon='', parent=expanderCont, pos=(4, 4, 11, 11), align=uiconst.TOPRIGHT, ignoreSize=True, func=self.ToggleAdvanced, args=(expanderCont,))
        icon = expander.sr.icon
        if nowExpanded:
            icon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
        else:
            icon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
        collapsingCont.state = [uiconst.UI_HIDDEN, uiconst.UI_PICKCHILDREN][nowExpanded]
        return expanderCont

    def ToggleAdvanced(self, expanderCont, force = None, *args):
        settingsName = 'contracts_search_expander_%s' % expanderCont.name
        if force is None:
            expanded = not settings.user.ui.Get(settingsName, 0)
        else:
            expanded = force
        settings.user.ui.Set(settingsName, expanded)
        if expanded:
            expanderCont.expander.sr.icon.LoadTexture('res:/UI/Texture/Shared/expanderUp.png')
        else:
            expanderCont.expander.sr.icon.LoadTexture('res:/UI/Texture/Shared/expanderDown.png')
        expanderCont.label.text = [expanderCont.offText, expanderCont.onText][expanded]
        if expanded:
            expanderCont.collapsingCont.state = uiconst.UI_PICKCHILDREN
        else:
            expanderCont.collapsingCont.state = uiconst.UI_HIDDEN

    def ToggleClientFilters(self, *args):
        settingsName = 'contracts_search_expander_clientFilterExpander'
        expanded = not settings.user.ui.Get(settingsName, 0)
        settings.user.ui.Set(settingsName, expanded)
        if expanded:
            self.sr.filterCont.state = uiconst.UI_PICKCHILDREN
        else:
            self.sr.filterCont.state = uiconst.UI_HIDDEN

    def FilterCheckBoxChange(self, cb, *args):
        if cb.name in ('maxjumps', 'maxroute'):
            cfgname = 'contracts_search_client_%s' % cb.name
            cfgnameNum = '%s_num' % cfgname
            inputField = getattr(self.sr, '%sInput' % cb.name, None)
            if cb.checked:
                inputField.Enable()
                input = inputField.GetValue()
                num = min(input, MAXJUMPROUTENUM)
                inputField.SetValue(str(num))
                settings.user.ui.Set(cfgname, 1)
                settings.user.ui.Set(cfgnameNum, num)
            else:
                inputField.Disable()
                settings.user.ui.Set(cfgname, 0)
        if self.currPage in self.pageData:
            self.RenderPage()
        hint, icon, isFiltered = self.GetClientFilterTextAndIcon()
        self.sr.pageFilterIcon.hint = hint
        self.sr.pageFilterIcon.LoadIcon(icon)

    def OnJumpInputReturn(self, *args):
        value = min(self.sr.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxjumps_num', value)
        if self.currPage in self.pageData:
            self.RenderPage()

    def OnJumpFocusLost(self, *args):
        value = min(self.sr.maxjumpsInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxjumps_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()

    def OnRouteInputReturn(self, *args):
        value = min(self.sr.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settings.user.ui.Set('contracts_search_client_maxroute_num', value)
        if self.currPage in self.pageData:
            self.RenderPage()

    def OnRouteFocusLost(self, *args):
        value = min(self.sr.maxrouteInput.GetValue(), MAXJUMPROUTENUM)
        settingsValue = settings.user.ui.Get('contracts_search_client_maxroute_num', MAXJUMPROUTENUM)
        if settingsValue != value:
            self.OnJumpInputReturn()

    def OnDropOffReturn(self, *args):
        self.ParseDropOff()
        self.DoSearch()

    def OnDropIssuer(self, dragObj, nodes):
        node = nodes[0]
        if node.Get('__guid__', None) not in uiutil.AllUserEntries():
            return
        charID = node.charID
        if util.IsCharacter(charID) or util.IsCorporation(charID):
            issuerName = cfg.eveowners.Get(charID).name
            self.sr.fltIssuer.SetValue(issuerName)
            self.sr.fltIssuerID = charID

    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        typeID = None
        if guid in ('xtriui.InvItem', 'listentry.InvItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem'):
            typeID = getattr(node, 'typeID', None)
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.sr.typeName.SetValue(typeName)
            self.sr.fltExactType.SetChecked(1, 0)

    def PopulateLocationCombo(self):
        self.locationOptions = [(localization.GetByLabel('UI/Generic/CurrentStation'), 0),
         (localization.GetByLabel('UI/Generic/CurrentSystem'), 1),
         (localization.GetByLabel('UI/Generic/CurrentConstellation'), 3),
         (localization.GetByLabel('UI/Corporations/Assets/CurrentRegion'), 2),
         (localization.GetByLabel('UI/Corporations/Assets/AllRegions'), 7),
         (localization.GetByLabel('UI/Contracts/ContractsSearch/PickLocation'), 10)]
        settingsLocationID = settings.user.ui.Get('contracts_search_location', 2)
        customLocations = copy.copy(settings.user.ui.Get('contracts_search_customlocations', []))
        customLocations.reverse()
        if customLocations:
            mrk = ''
            self.locationOptions.append((mrk, None))
            for l in customLocations:
                self.locationOptions.append((l[0], l[1]))

        if settingsLocationID is not None and settingsLocationID > 100:
            try:
                self.locationOptions.insert(0, (cfg.evelocations.Get(settingsLocationID).name, settingsLocationID))
            except:
                pass

        self.sr.fltLocation.LoadOptions(self.locationOptions, settingsLocationID)

    def PopulateGroupCombo(self, isSel = False):
        v = self.sr.fltCategories.GetValue()
        categoryID = v[0] if v and v != -1 else None
        groups = [(localization.GetByLabel('UI/Contracts/ContractsSearch/SelectCategory'), None)]
        if categoryID:
            groups = [(localization.GetByLabel('UI/Contracts/ContractsSearch/comboAll'), None)]
            if evetypes.CategoryExists(categoryID):
                for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                    if evetypes.IsGroupPublishedByGroup(groupID):
                        groups.append((evetypes.GetGroupNameByGroup(groupID), groupID))

        sel = None
        if isSel:
            sel = settings.user.ui.Get('contracts_search_group', None)
        self.sr.fltGroups.LoadOptions(groups, sel)
        if categoryID is None:
            self.sr.fltGroups.state = uiconst.UI_HIDDEN
        else:
            self.sr.fltGroups.state = uiconst.UI_NORMAL

    def Load(self, args):
        if not self.inited:
            return

    def Height(self):
        return self.height or self.absoluteBottom - self.absoluteTop

    def Width(self):
        return self.width or self.absoluteRight - self.absoluteLeft

    def ShowLoad(self):
        form.ContractsWindow.GetIfOpen().ShowLoad()

    def HideLoad(self):
        form.ContractsWindow.GetIfOpen().HideLoad()

    def DoSearch(self, *args):
        if self.sr.SearchButton.state == uiconst.UI_DISABLED:
            raise UserError('ConPleaseWait')
        self.pageData = {}
        self.sr.SearchButton.state = uiconst.UI_DISABLED
        self.sr.SearchButton.SetInCaption('<color=gray>' + localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch') + '</color>')
        uthread.new(self.EnableSearchButton)
        self.ShowLoad()
        try:
            self.SearchContracts(reset=True)
        finally:
            self.HideLoad()
            self.IndicateLoading(loading=0)

    def EnableSearchButton(self):
        blue.pyos.synchro.SleepWallclock(2000)
        try:
            self.sr.SearchButton.state = uiconst.UI_NORMAL
            self.sr.SearchButton.SetInCaption(localization.GetByLabel('UI/Contracts/ContractsSearch/buttonSearch'))
        except:
            pass

    def GoToPage(self, pageNum):
        if pageNum < 0:
            return
        if pageNum >= self.numPages:
            return
        self.currPage = pageNum
        self.DoPage(nav=0)

    def DoPagePrev(self, *args):
        self.DoPage(-1)

    def DoPageNext(self, *args):
        self.DoPage(1)

    def DoPage(self, nav = 1, *args):
        p = self.currPage + nav
        if p < 0:
            return
        if p >= self.numPages:
            return
        self.currPage = p
        if self.currPage in self.pageData:
            self.svc.LogInfo('Page', self.currPage, 'found in cache')
            self.RenderPage()
            return
        self.svc.LogInfo('Page', self.currPage, 'not found in cache')
        if self.searchThread:
            self.searchThread.kill()
        self.searchThread = uthread.new(self.DoPageThread)

    def DoPageThread(self):
        self.IndicateLoading(loading=1)
        blue.pyos.synchro.SleepWallclock(500)
        self.SearchContracts(page=self.currPage, contractType=self.contractType, availability=self.availability, override=self.override)

    def OnIssuerChange(self, text, *args):
        if self.sr.fltIssuerID is not None:
            self.sr.fltIssuerID = None
            settings.user.ui.Set('contracts_search_issuer_id', None)

    def ClearEditField(self, editField, *args):
        editField.SetValue('')

    def ParseIssuers(self, *args):
        if self.destroyed:
            return
        wnd = self.sr.fltIssuer
        if not wnd or wnd.destroyed:
            return
        name = wnd.GetValue().strip()
        if not name:
            return
        ownerID = uix.Search(name.lower(), const.groupCharacter, const.categoryOwner, hideNPC=1, filterGroups=[const.groupCharacter, const.groupCorporation], searchWndName='contractIssuerSearch')
        if ownerID:
            self.sr.fltIssuer.SetValue(cfg.eveowners.Get(ownerID).name)
            self.sr.fltIssuerID = ownerID

    def GetLocationGroupID(self, locationID):
        if util.IsSolarSystem(locationID):
            return const.groupSolarSystem
        if util.IsConstellation(locationID):
            return const.groupConstellation
        if util.IsRegion(locationID):
            return const.groupRegion

    def ParseDropOff(self, *args):
        if self.destroyed:
            return
        wnd = self.sr.fltDropOff
        if not wnd or wnd.destroyed:
            return
        name = wnd.GetValue().strip().lower()
        locationID = self.SearchLocation(name)
        if locationID:
            name = cfg.evelocations.Get(locationID).name
            self.sr.fltDropOffID = locationID
            wnd.SetValue(name)

    def SearchLocation(self, name):
        if not name:
            return None
        resultList = searchUtil.QuickSearch(name, const.searchResultAllLocations)
        foundList = []
        for l in resultList:
            groupID = self.GetLocationGroupID(l)
            if not groupID:
                continue
            groupName = {const.groupSolarSystem: localization.GetByLabel('UI/Common/LocationTypes/SolarSystem'),
             const.groupConstellation: localization.GetByLabel('UI/Common/LocationTypes/Constellation'),
             const.groupRegion: localization.GetByLabel('UI/Common/LocationTypes/Region')}.get(groupID, '')
            foundList.append((localization.GetByLabel('UI/Contracts/ContractsSearch/FormatSearchLocation', locationID=l, groupName=groupName), l, groupID))

        if not foundList:
            raise UserError('NoLocationFound', {'name': name})
        if len(foundList) == 1:
            chosen = foundList[0]
        else:
            chosen = uix.ListWnd(foundList, '', localization.GetByLabel('UI/Contracts/ContractsSearch/SelectLocation'), localization.GetByLabel('UI/Contracts/ContractsSearch/LocationSearchHint', foundList=len(foundList)), 1, minChoices=1, isModal=1, windowName='locationsearch', unstackable=1)
        if chosen:
            return chosen[1]
        else:
            return None

    def ResetTypeFilters(self):
        self.sr.typeName.SetValue('')
        self.sr.fltExactType.SetChecked(0, 0)
        self.sr.fltCategories.SelectItemByValue(None)
        settings.user.ui.Set('contracts_search_category', None)
        self.PopulateGroupCombo()

    def ResetFields(self, *args):
        fields = ['fltMaxPrice',
         'fltMinPrice',
         'fltMaxVolume',
         'fltMinVolume',
         'fltMaxCollateral',
         'fltMinCollateral',
         'fltMinReward',
         'fltMaxReward']
        for name in fields:
            field = getattr(self.sr, name, None)
            if field is None or field.destroyed:
                continue
            field.SetValue('')
            field.SetText('')
            field.CheckHintText()

        if self.sr.fltDropOff:
            self.sr.fltDropOff.SetValue('')
            self.sr.fltDropOffID = None
        if self.sr.fltIssuer:
            self.sr.fltIssuer.SetValue('')
        self.sr.fltIssuerID = None
        try:
            if self.sr.fltDropOff:
                self.sr.fltDropOff.SetValue('')
                self.sr.fltDropOffID = None
        except:
            pass

    def ResetCheckboxes(self, *args):
        checkboxes = [('fltExcludeTrade', 0),
         ('fltExcludeMultiple', 0),
         ('fltSecNull', 1),
         ('fltSecLow', 1),
         ('fltSecHigh', 1)]
        for name, val in checkboxes:
            cb = getattr(self.sr, name, None)
            if cb is None or cb.destroyed:
                continue
            cb.SetValue(val)

    def FindMyContracts(self, contractType = cc.CONTYPE_AUCTIONANDITEMECHANGE, isCorp = False):
        self.SearchContracts(contractType=contractType, availability=const.conAvailMyCorp if isCorp else const.conAvailMyself, override=True)

    def FindRelated(self, typeID, groupID, categoryID, issuerID, locationID, endLocationID, avail, contractType, reset = True):
        self.ToggleAdvanced(expanderCont=self.sr.advancedDivider, force=1)
        if contractType and settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE) != contractType:
            settings.user.ui.Set('contracts_search_type', contractType)
            self.PopulateSortCombo()
            self.InitFilters()
        if reset:
            if self.sr.fltAvail.GetValue() != avail:
                settings.user.ui.Set('contracts_search_avail', avail)
                self.InitFilters()
            if contractType and contractType != const.conTypeCourier:
                self.ResetTypeFilters()
            self.ResetFields()
            self.sr.fltLocation.SelectItemByValue(7)
        if issuerID:
            issuerName = cfg.eveowners.Get(issuerID).name
            self.sr.fltIssuer.SetValue(issuerName)
            self.sr.fltIssuerID = issuerID
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.sr.typeName.SetValue(typeName)
            self.sr.fltExactType.SetChecked(1, 0)
        elif categoryID:
            self.sr.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
        elif groupID:
            categoryID = evetypes.GetCategoryIDByGroup(groupID)
            self.sr.fltCategories.SelectItemByValue((categoryID, 0))
            self.PopulateGroupCombo()
            self.sr.fltGroups.SelectItemByValue(groupID)
        if locationID:
            self.DoPickLocation(locationID)
        if endLocationID:
            locationName = cfg.evelocations.Get(endLocationID).name
            self.sr.fltDropOff.SetValue(locationName)
            self.sr.fltDropOffID = endLocationID
        self.SearchContracts()

    def SearchContracts(self, page = 0, reset = False, contractType = None, availability = None, override = False):
        self.IndicateLoading(loading=1)
        self.currPage = page
        self.override = override
        self.contractType = contractType
        self.availability = availability
        advancedVisible = self.sr.advancedCont.state != uiconst.UI_HIDDEN
        if override:
            itemTypes = None
            itemTypeName = None
            itemCategoryID = None
            itemGroupID = None
            contractType = contractType
            securityClasses = [const.securityClassZeroSec, const.securityClassLowSec, const.securityClassHighSec]
            locationID = None
            endLocationID = None
            issuerID = None
            minPrice = None
            maxPrice = None
            minReward = None
            maxReward = None
            minCollateral = None
            maxCollateral = None
            minVolume = None
            maxVolume = None
            excludeTrade = False
            excludeMultiple = False
            excludeNoBuyout = False
            availability = availability
            description = None
            searchHint = None
        else:
            issuerID = None
            if advancedVisible:
                if self.sr.fltIssuerID is None and self.sr.fltIssuer.GetValue():
                    self.ParseIssuers()
                if self.sr.fltIssuerID:
                    issuerID = self.sr.fltIssuerID
                    settings.user.ui.Set('contracts_search_issuer_id', issuerID)
            if contractType is None:
                contractType = settings.user.ui.Get('contracts_search_type', cc.CONTYPE_AUCTIONANDITEMECHANGE)
            if availability is None:
                if advancedVisible:
                    availability = self.sr.fltAvail.GetValue()
                else:
                    availability = const.conAvailPublic
            locationID = self.sr.fltLocation.GetValue()
            if locationID < 100:
                if locationID == 0 and not session.stationid:
                    raise UserError('ConNotInStation')
                locationID = {0: session.stationid,
                 1: session.solarsystemid2,
                 2: session.regionid,
                 3: session.constellationid}.get(locationID, None)
            endLocationID = None
            if advancedVisible and contractType == const.conTypeCourier:
                endLocationName = self.sr.fltDropOff.GetValue()
                if endLocationName and self.sr.fltDropOffID:
                    endLocationID = self.sr.fltDropOffID
                    if endLocationID is None:
                        raise UserError('ConDropOffNotFound', {'name': endLocationName})
                settings.user.ui.Set('contracts_search_dropoff', endLocationName or '')
                settings.user.ui.Set('contracts_search_dropoff_id', endLocationID)
            securityClasses = None
            if advancedVisible:
                secNull = not not self.sr.fltSecNull.checked
                secLow = not not self.sr.fltSecLow.checked
                secHigh = not not self.sr.fltSecHigh.checked
                if False in (secNull, secLow, secHigh):
                    securityClasses = []
                    if secNull:
                        securityClasses.append(const.securityClassZeroSec)
                    if secLow:
                        securityClasses.append(const.securityClassLowSec)
                    if secHigh:
                        securityClasses.append(const.securityClassHighSec)
                    securityClasses = securityClasses or None
            minPrice = None
            maxPrice = None
            if advancedVisible and const.conTypeCourier != contractType:
                m = self.sr.fltMinPrice.GetValue()
                settings.user.ui.Set('contracts_search_minprice', m)
                if m:
                    minPrice = int(m) * MILLION
                m = self.sr.fltMaxPrice.GetValue()
                settings.user.ui.Set('contracts_search_maxprice', m)
                if m:
                    maxPrice = int(m) * MILLION
            minReward = None
            maxReward = None
            minCollateral = None
            maxCollateral = None
            minVolume = None
            maxVolume = None
            if advancedVisible and const.conTypeCourier == contractType:
                m = self.sr.fltMinReward.GetValue()
                settings.user.ui.Set('contracts_search_minreward', m)
                if m:
                    minReward = int(m) * MILLION
                m = self.sr.fltMaxReward.GetValue()
                settings.user.ui.Set('contracts_search_maxreward', m)
                if m:
                    maxReward = int(m) * MILLION
                m = self.sr.fltMinCollateral.GetValue()
                settings.user.ui.Set('contracts_search_mincollateral', m)
                if m:
                    minCollateral = int(m) * MILLION
                m = self.sr.fltMaxCollateral.GetValue()
                settings.user.ui.Set('contracts_search_maxcollateral', m)
                if m:
                    maxCollateral = int(m) * MILLION
                m = self.sr.fltMinVolume.GetValue()
                settings.user.ui.Set('contracts_search_minvolume', m)
                if m:
                    minVolume = int(m)
                m = self.sr.fltMaxVolume.GetValue()
                settings.user.ui.Set('contracts_search_maxvolume', m)
                if m:
                    maxVolume = int(m)
            itemCategoryID = None
            itemGroupID = None
            itemTypes = None
            excludeTrade = None
            excludeMultiple = None
            excludeNoBuyout = None
            itemTypeName = None
            searchHint = None
            if contractType != const.conTypeCourier:
                isExact = False
                if advancedVisible:
                    cv = self.sr.fltCategories.GetValue()
                    if cv and cv != -1:
                        itemCategoryID = int(cv[0])
                        searchHint = int(cv[1])
                    if self.sr.fltGroups.GetValue():
                        itemGroupID = int(self.sr.fltGroups.GetValue())
                    isExact = self.sr.fltExactType.checked
                typeName = self.sr.typeName.GetValue()
                if typeName:
                    metaLevels = []
                    if '|' in typeName:
                        lst = typeName.split('|')
                        typeName = lst[0]
                        metaNames = lst[1].lower()
                        for metaName in metaNames.split(','):
                            groupIDsByName = {'tech i': 1,
                             'tech ii': 2,
                             'tech iii': 14,
                             'storyline': 3,
                             'faction': 4,
                             'officer': 5,
                             'deadspace': 6}
                            vals = groupIDsByName.values()
                            groupIDsByName = {}
                            legalGroups = {}
                            for v in vals:
                                legalGroups[cfg.invmetagroups.Get(v).name] = v

                            groupIDsByName = {k.lower():v for k, v in legalGroups.iteritems()}
                            legalGroups = legalGroups.keys()
                            legalGroups.sort()
                            metaLevel = groupIDsByName.get(metaName, None)
                            if metaName and metaLevel is None:
                                raise UserError('ConMetalevelNotFound', {'level': metaName,
                                 'legal': ', '.join(legalGroups)})
                            metaLevels.append(metaLevel)

                    groupOrCategory = ''
                    if ':' in typeName:
                        lst = typeName.split(':')
                        groupOrCategory = lst[0].lower()
                        found = False
                        for groupID in evetypes.IterateGroups():
                            if evetypes.GetGroupNameByGroup(groupID).lower() == groupOrCategory:
                                itemGroupID = groupID
                                itemCategoryID = evetypes.GetCategoryIDByGroup(groupID)
                                found = True
                                sm.GetService('contracts').LogInfo('Found group:', groupID)
                                break

                        for categoryID in evetypes.IterateCategories():
                            if evetypes.GetCategoryNameByCategory(categoryID).lower() == groupOrCategory:
                                itemGroupID = None
                                itemCategoryID = categoryID
                                found = True
                                sm.GetService('contracts').LogInfo('Found category:', categoryID)
                                break

                        if found:
                            typeName = lst[1]
                        else:
                            sm.GetService('contracts').LogInfo('Did not find group or category matching', groupOrCategory)
                            groupOrCategory = ''
                    itemTypes = self.GetTypesFromName(typeName, itemCategoryID, itemGroupID)
                    if metaLevels:
                        typeIDs = itemTypes.keys()
                        itemTypes = set()
                        godma = sm.GetService('godma')
                        for typeID in typeIDs:
                            try:
                                tech = int(godma.GetType(typeID).techLevel)
                                meta = godma.GetTypeAttribute(typeID, const.attributeMetaGroupID)
                                if meta:
                                    if meta in metaLevels:
                                        itemTypes.add(typeID)
                                elif tech in metaLevels:
                                    itemTypes.add(typeID)
                            except:
                                pass

                    else:
                        itemTypes = set(itemTypes.keys())
                    if isExact and itemTypes:
                        typeID = None
                        if len(itemTypes) > 1:
                            for checkTypeID in itemTypes:
                                if evetypes.GetName(checkTypeID).lower() == typeName.lower():
                                    typeID = checkTypeID
                                    break
                            else:
                                typeID = SelectItemTypeDlg(itemTypes)

                        else:
                            typeID = list(itemTypes)[0]
                        if not typeID:
                            return
                        name = evetypes.GetName(typeID)
                        if groupOrCategory:
                            name = '%s:%s' % (groupOrCategory, name)
                        self.sr.typeName.SetValue(name)
                        itemTypes = {typeID: None}
                if not itemTypes and typeName:
                    raise UserError('ConNoTypeMatchFound', {'name': typeName})
                itemTypeName = self.sr.typeName.GetValue() or None
                settings.user.ui.Set('contracts_search_typename', itemTypeName or '')
                excludeMultiple = self.sr.fltExcludeMultiple.checked
                if contractType != const.conTypeCourier:
                    opt = self.sr.fltContractOptions.GetValue()
                    if opt:
                        if opt == 1:
                            contractType = const.conTypeAuction
                        elif opt == 2:
                            contractType = const.conTypeItemExchange
                            if not minPrice:
                                minPrice = 1
                            excludeTrade = True
                        elif opt == 3:
                            contractType = const.conTypeItemExchange
                            if not maxPrice:
                                maxPrice = 0
                        elif opt == 4:
                            contractType = cc.CONTYPE_AUCTIONANDITEMECHANGE
                            if not minPrice:
                                minPrice = 1
                            excludeTrade = True
        startNum = page * cc.CONTRACTS_PER_PAGE
        sortBy, sortDir = self.sr.fltSort.GetValue()
        description = None
        ret = sm.ProxySvc('contractProxy').SearchContracts(itemTypes=itemTypes, itemTypeName=itemTypeName, itemCategoryID=itemCategoryID, itemGroupID=itemGroupID, contractType=contractType, securityClasses=securityClasses, locationID=locationID, endLocationID=endLocationID, issuerID=issuerID, minPrice=minPrice, maxPrice=maxPrice, minReward=minReward, maxReward=maxReward, minCollateral=minCollateral, maxCollateral=maxCollateral, minVolume=minVolume, maxVolume=maxVolume, excludeTrade=excludeTrade, excludeMultiple=excludeMultiple, excludeNoBuyout=excludeNoBuyout, availability=availability, description=description, searchHint=searchHint, sortBy=sortBy, sortDir=sortDir, startNum=startNum)
        contracts = ret.contracts
        numFound = ret.numFound
        searchTime = ret.searchTime
        maxResults = ret.maxResults
        self.numPages = int(int(numFound) / cc.CONTRACTS_PER_PAGE)
        if not numFound or self.numPages * cc.CONTRACTS_PER_PAGE < numFound:
            self.numPages += 1
        if numFound >= maxResults:
            numFound = '%s+' % maxResults
        if len(contracts) >= 2:
            self.pages[self.currPage] = contracts[0].contract.contractID
            self.pages[self.currPage + 1] = contracts[-1].contract.contractID - 1
        ownerIDs = set()
        for r in contracts:
            ownerIDs.add(r.contract.issuerID)
            ownerIDs.add(r.contract.issuerCorpID)
            ownerIDs.add(r.contract.assigneeID)

        cfg.eveowners.Prime(ownerIDs)
        self.sr.contractlist.sr.id = None
        pathfinderSvc = sm.GetService('clientPathfinderService')
        mapSvc = sm.StartService('map')
        jumpsCache = {}
        routes = {}
        data = []
        for _c in contracts:
            blue.pyos.BeNice()
            items = _c.items
            bids = _c.bids
            c = _c.contract
            typeID = None
            routeLength = 0
            if len(items) == 1:
                typeID = items[0].itemTypeID
            if c.startStationID == session.stationid:
                numJumps = 0
            elif c.startSolarSystemID == session.solarsystemid2:
                numJumps = 0
            elif c.startSolarSystemID not in jumpsCache:
                numJumps = pathfinderSvc.GetAutopilotJumpCount(session.solarsystemid2, c.startSolarSystemID)
                jumpsCache[c.startSolarSystemID] = numJumps
            else:
                numJumps = jumpsCache[c.startSolarSystemID]
            route = None
            if c.type == const.conTypeCourier:
                r = [c.startSolarSystemID, c.endSolarSystemID]
                r.sort()
                route = (r[0], r[1])
                if route not in routes:
                    routes[route] = pathfinderSvc.GetAutopilotJumpCount(c.startSolarSystemID, c.endSolarSystemID)
                routeLength = routes[route]
            startSecurityClass = None
            endSecurityClass = None
            if c.startSolarSystemID != session.solarsystemid2:
                startSecurityClass = int(mapSvc.GetSecurityClass(c.startSolarSystemID))
            if c.endSolarSystemID and c.endSolarSystemID != session.solarsystemid2:
                endSecurityClass = int(mapSvc.GetSecurityClass(c.endSolarSystemID))
            issuer = cfg.eveowners.Get(c.issuerCorpID if c.forCorp else c.issuerID).name
            d = {'contract': c,
             'title': GetContractTitle(c, items),
             'startSolarSystemName': cfg.evelocations.Get(c.startSolarSystemID).name,
             'endSolarSystemName': cfg.evelocations.Get(c.endSolarSystemID).name,
             'issuer': issuer,
             'searchresult': _c,
             'contractItems': items,
             'bids': bids,
             'rec': '',
             'text': '',
             'label': '',
             'typeID': typeID,
             'numJumps': numJumps,
             'routeLength': routeLength,
             'route': route,
             'startSecurityClass': startSecurityClass,
             'endSecurityClass': endSecurityClass,
             'dateIssued': c.dateIssued}
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnCurrentBid')] = (c.price if not bids else bids[0].amount, c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnCollateral')] = (c.collateral, c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation')] = (d['startSolarSystemName'], c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnPrice')] = (int(c.price) or -int(c.reward), c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnReward')] = (c.reward, c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume')] = (c.volume, c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract')] = (d['title'], c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft')] = (c.dateExpired, c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps')] = (d['numJumps'], c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columPickup')] = (d['startSolarSystemName'], c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnDropOff')] = (d['endSolarSystemName'], c.contractID)
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated')] = c.dateIssued
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer')] = issuer.lower()
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnBids')] = d['bids']
            d['sort_%s' % localization.GetByLabel('UI/Contracts/ContractsSearch/columnRoute')] = (d['routeLength'], c.contractID)
            data.append(d)

        self.numFound = numFound
        self.contractType = contractType
        self.pageData[self.currPage] = data
        self.RenderPage(reset)
        self.svc.LogInfo('Found', numFound, 'contracts in %.4f seconds' % (searchTime / float(const.SEC)))

    def RenderPage(self, reset = False):
        try:
            data = self.pageData[self.currPage]
            contractType = self.contractType
            if contractType == cc.CONTYPE_AUCTIONANDITEMECHANGE:
                contractType = const.conTypeItemExchange
            scrolllist = []
            className = {const.conTypeAuction: 'ContractEntrySearchAuction',
             const.conTypeItemExchange: 'ContractEntrySearchItemExchange',
             const.conTypeCourier: 'ContractEntrySearchCourier'}[contractType]
            securityClassMe = sm.GetService('map').GetSecurityClass(session.solarsystemid2)
            ignoreList = set(settings.user.ui.Get('contracts_ignorelist', []))
            for d in data:
                contract = d['contract']
                if settings.user.ui.Get('contracts_search_client_maxjumps', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxjumps_num', 0)
                    if maxNumJumps and d['numJumps'] > maxNumJumps:
                        continue
                if d['route'] and settings.user.ui.Get('contracts_search_client_maxroute', False):
                    maxNumJumps = settings.user.ui.Get('contracts_search_client_maxroute_num', 0)
                    if maxNumJumps and d['routeLength'] > maxNumJumps:
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeunreachable', 0):
                    if d['numJumps'] > cc.NUMJUMPS_UNREACHABLE or d['routeLength'] > cc.NUMJUMPS_UNREACHABLE or self.svc.IsStationInaccessible(contract.startStationID) or self.svc.IsStationInaccessible(contract.endStationID):
                        continue
                if settings.user.ui.Get('contracts_search_client_excludeignore', 1):
                    skipIt = False
                    for ownerID in ignoreList:
                        if ownerID in [contract.issuerID, contract.issuerCorpID]:
                            skipIt = True
                            break

                    if skipIt:
                        continue
                if settings.user.ui.Get('contracts_search_client_currentsecurity', False):
                    if d['startSecurityClass'] is not None and d['startSecurityClass'] != securityClassMe:
                        continue
                    if d['endSecurityClass'] is not None and d['endSecurityClass'] != securityClassMe:
                        continue
                scrolllist.append(listentry.Get(className, d))

            if contractType == const.conTypeItemExchange:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnPrice'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            elif contractType == const.conTypeAuction:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnLocation'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCurrentBid'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnBuyOut'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnBids'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            else:
                columns = [localization.GetByLabel('UI/Contracts/ContractsSearch/columPickup'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnDropOff'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnVolume'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnReward'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCollateral'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnRoute'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnJumps'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnTimeLeft'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnIssuer'),
                 localization.GetByLabel('UI/Contracts/ContractsSearch/columnCreated'),
                 localization.GetByLabel('UI/Contracts/ContractsWindow/InfoByIssuer')]
            self.sr.contractlist.sr.id = 'contractlist'
            self.sr.contractlist.sr.minColumnWidth = {localization.GetByLabel('UI/Contracts/ContractsSearch/columnContract'): 100,
             localization.GetByLabel('UI/Contracts/ContractsSearch/columnBuyOut'): 200}
            reset = False
            self.sr.contractlist.LoadContent(contentList=scrolllist, headers=columns, noContentHint=localization.GetByLabel('UI/Contracts/ContractsSearch/labelNoContractsFound'), ignoreSort=reset, scrolltotop=True)
            if reset:
                if self.sr.contractlist:
                    self.sr.contractlist.HiliteSorted(None, None)
            txt = localization.GetByLabel('UI/Contracts/ContractsSearch/labelNumberContractsFound', num=self.numFound)
            self.sr.foundLabel.SetText(txt)
            self.sr.expanderTextCont.width = self.sr.foundLabel.textwidth + 50
            self.UpdatePaging(self.currPage + 1, self.numPages)
        finally:
            self.IndicateLoading(loading=0)

    def IndicateLoading(self, loading = 0):
        try:
            if loading:
                self.sr.loadingWheel.Show()
                self.sr.contractlist.sr.maincontainer.opacity = 0.5
            else:
                self.sr.loadingWheel.Hide()
                self.sr.contractlist.sr.maincontainer.opacity = 1.0
        except:
            pass

    def DoNothing(self, *args):
        pass
