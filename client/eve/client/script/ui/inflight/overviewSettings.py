#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\overviewSettings.py
import operator
from carbon.common.script.util.format import FmtDate
from carbonui import const as uiconst
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.util.various_unsorted import ParanoidDecoMethod, SortListOfTuples
from eve.client.script.parklife import tacticalConst
from eve.client.script.parklife.state import GetNPCGroups
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.buttonGroup import ButtonGroup
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveCombo import Combo
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveIcon import MenuIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveHeaderSmall, EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveTabgroupUtil import FixedTabName
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.tabGroup import TabGroup
from eve.client.script.ui.inflight.overview import StatesPanel, DraggableShareContainer, OverView
from eve.client.script.ui.quickFilter import QuickFilterEdit
import evetypes
import localization
import blue
from overviewPresets.overviewPresetUtil import MAX_TAB_NUM
from utillib import KeyVal

class OverviewSettings(Window):
    __guid__ = 'form.OverviewSettings'
    __notifyevents__ = ['OnTacticalPresetChange',
     'OnOverviewPresetSaved',
     'OnRefreshOverviewTab',
     'OnReloadingOverviewProfile']
    default_windowID = 'overviewsettings'
    default_captionLabelPath = 'UI/Overview/OverviewSettings'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.currentKey = None
        self.specialGroups = GetNPCGroups()
        self.scope = 'inflight'
        self.minWidth = 430
        self.SetWndIcon()
        self.SetHeaderIcon()
        settingsIcon = self.sr.headerIcon
        settingsIcon.state = uiconst.UI_NORMAL
        settingsIcon.GetMenu = self.GetPresetsMenu
        settingsIcon.expandOnLeft = 1
        settingsIcon.hint = ''
        self.sr.main = self.GetChild('main')
        self.AddDraggableCont()
        self.settingCheckboxes = []
        self.statetop = statetop = Container(name='statetop', parent=self.sr.main, align=uiconst.TOTOP)
        topText = EveLabelMedium(text=localization.GetByLabel('UI/Overview/HintToggleDisplayState'), parent=statetop, align=uiconst.TOTOP, padding=(10, 3, 10, 0), state=uiconst.UI_NORMAL)
        topText.color.SetRGBA(1, 1, 1, 0.8)
        cb = Checkbox(text=localization.GetByLabel('UI/Overview/ApplyToShipsAndDronesOnly'), parent=statetop, configName='applyOnlyToShips', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('applyOnlyToShips', True), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        self.settingCheckboxes.append(cb)
        self.sr.applyOnlyToShips = cb
        cb = Checkbox(text=localization.GetByLabel('UI/Overview/UseSmallColortags'), parent=statetop, configName='useSmallColorTags', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('useSmallColorTags', False), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        self.settingCheckboxes.append(cb)
        self.sr.useSmallColorTags = cb
        self.sr.useSmallText = Checkbox(text=localization.GetByLabel('UI/Overview/UseSmallFont'), parent=statetop, configName='useSmallText', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('useSmallText', False), callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, padding=(9, 0, 0, 0))
        self.settingCheckboxes.append(self.sr.useSmallText)
        statebtns = ButtonGroup(btns=[[localization.GetByLabel('UI/Commands/ResetAll'),
          self.ResetStateSettings,
          (),
          None]], parent=self.sr.main, idx=0)
        colLabel = EveLabelMedium(text=localization.GetByLabel('UI/Overview/HintToggleDisplayStateAndOrder'), parent=self.sr.main, align=uiconst.TOTOP, padding=(10, 3, 10, 2), state=uiconst.UI_DISABLED)
        colLabel.color.SetRGBA(1, 1, 1, 0.8)
        colbtns = ButtonGroup(btns=[[localization.GetByLabel('UI/Overview/ResetColumns'),
          self.ResetColumns,
          (),
          None]], parent=self.sr.main, idx=0)
        filtertop = Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP)
        Container(name='push', parent=filtertop, align=uiconst.TOTOP, height=36, state=uiconst.UI_DISABLED)
        shiptop = Container(name='filtertop', parent=self.sr.main, align=uiconst.TOTOP, height=57)
        presetMenu = MenuIcon()
        presetMenu.GetMenu = self.GetShipLabelMenu
        presetMenu.left = 6
        presetMenu.top = 10
        presetMenu.hint = ''
        shiptop.children.append(presetMenu)
        cb = Checkbox(text=localization.GetByLabel('UI/Overview/HideTickerIfInAlliance'), parent=shiptop, configName='hideCorpTicker', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('hideCorpTicker', False), groupname=None, callback=self.CheckBoxChange, prefstype=('user', 'overview'), align=uiconst.TOTOP, pos=(0, 30, 0, 16))
        cb.padLeft = 8
        self.settingCheckboxes.append(cb)
        self.sr.hideTickerIfInAlliance = cb
        historyCont = self.GetHistoryTab()
        misctop = Container(name='misctop', parent=self.sr.main, align=uiconst.TOALL, left=const.defaultPadding, width=const.defaultPadding, top=const.defaultPadding)
        miscPadding = 4
        overviewBroadcastsToTop = Checkbox(text=localization.GetByLabel('UI/Overview/MoveBroadcastersToTop'), parent=misctop, configName='overviewBroadcastsToTop', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('overviewBroadcastsToTop', False), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, padLeft=miscPadding)
        self.settingCheckboxes.append(overviewBroadcastsToTop)
        self.targetRangeSubCheckboxes = []
        btnCont = Container(parent=misctop, height=20, align=uiconst.TOTOP)
        Button(parent=btnCont, label=localization.GetByLabel('UI/Overview/ResetOverview'), func=self.ResetAllOverviewSettings, left=miscPadding)
        EveHeaderSmall(text=localization.GetByLabel('UI/Overview/BracketAndTargetsHeader'), parent=misctop, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, top=14, padLeft=miscPadding + 2)
        targetCrosshairCb = Checkbox(text=localization.GetByLabel('UI/SystemMenu/GeneralSettings/Inflight/ShowTargettingCrosshair'), parent=misctop, configName='targetCrosshair', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('targetCrosshair', True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        self.settingCheckboxes.append(targetCrosshairCb)
        dmgIndicatorCb = Checkbox(text=localization.GetByLabel('UI/Overview/DisplayDamageIndications'), parent=misctop, configName='showBiggestDamageDealers', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('showBiggestDamageDealers', True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        self.settingCheckboxes.append(dmgIndicatorCb)
        moduleHairlineCb = Checkbox(text=localization.GetByLabel('UI/Overview/DisplayModuleLinks'), parent=misctop, configName='showModuleHairlines', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('showModuleHairlines', True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, padLeft=miscPadding)
        self.settingCheckboxes.append(moduleHairlineCb)
        targetRangeCb = Checkbox(text=localization.GetByLabel('UI/Overview/DisplayRangeBrackets'), parent=misctop, configName='showInTargetRange', retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName('showInTargetRange', True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=miscPadding)
        self.settingCheckboxes.append(targetRangeCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryShip
        targetRangeShipsCb = Checkbox(text=localization.GetByLabel('UI/Overview/Ships'), parent=misctop, configName=configName, retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        self.settingCheckboxes.append(targetRangeShipsCb)
        self.targetRangeSubCheckboxes.append(targetRangeShipsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryEntity
        targetRangeNPCsCb = Checkbox(text=localization.GetByLabel('UI/Overview/NPCs'), parent=misctop, configName=configName, retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        self.settingCheckboxes.append(targetRangeNPCsCb)
        self.targetRangeSubCheckboxes.append(targetRangeNPCsCb)
        configName = 'showCategoryInTargetRange_%s' % const.categoryDrone
        targetRangeDronesCb = Checkbox(text=localization.GetByLabel('UI/Overview/Drones'), parent=misctop, configName=configName, retval=None, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, True), groupname=None, prefstype=('user', 'overview'), align=uiconst.TOTOP, callback=self.MiscCheckboxChange, padLeft=3 * miscPadding)
        parentGrid = LayoutGrid(parent=misctop, columns=1, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP, top=10)
        Button(parent=parentGrid, label=localization.GetByLabel('UI/Overview/ImportOverviewSettings'), func=sm.GetService('tactical').ImportOverviewSettings, left=miscPadding)
        Button(parent=parentGrid, label=localization.GetByLabel('UI/Commands/ExportOverviewSettings'), func=sm.GetService('tactical').ExportOverviewSettings, left=miscPadding, top=4)
        self.settingCheckboxes.append(targetRangeDronesCb)
        self.targetRangeSubCheckboxes.append(targetRangeDronesCb)
        self.ChangeStateOfSubCheckboxes(targetRangeCb)
        overviewtabtop = self.AddTabForOverviewProfile()
        btns = ButtonGroup(btns=[[localization.GetByLabel('UI/Common/SelectAll'),
          self.SelectAll,
          (),
          None], [localization.GetByLabel('UI/Common/DeselectAll'),
          self.DeselectAll,
          (),
          None]], parent=self.sr.main, idx=0)
        parentGrid = LayoutGrid(parent=filtertop, columns=2, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT, left=10, top=3)
        l = EveLabelMedium(text=localization.GetByLabel('UI/Overview/CurrentPreset'))
        l.color.SetRGBA(1, 1, 1, 0.8)
        parentGrid.AddCell(cellObject=l, colSpan=2)
        currentPreset = self.overviewPresetSvc.GetActiveOverviewPresetName()
        currentPresetName = self.overviewPresetSvc.GetPresetDisplayName(currentPreset)
        self.sr.presetText = EveLabelSmall(text=currentPresetName, align=uiconst.CENTERLEFT)
        parentGrid.AddCell(cellObject=self.sr.presetText)
        self.savePresetButton = Button(label=localization.GetByLabel('UI/Common/Buttons/Save'), func=sm.GetService('overviewPresetSvc').SavePreset, align=uiconst.BOTTOMLEFT)
        parentGrid.AddCell(cellObject=self.savePresetButton, cellPadding=(20, 0, 0, 0))
        parentGrid.RefreshGridLayout()
        top = parentGrid.height + parentGrid.top
        self.groupQuickFilterCont = Container(parent=self.sr.main, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP)
        self.groupQuickFilter = QuickFilterEdit(parent=self.groupQuickFilterCont, pos=(5, 0, 150, 0), align=uiconst.TOPRIGHT)
        self.groupQuickFilter.ReloadFunction = self.LoadFilteredTypes
        self.groupQuickFilterCont.height = self.groupQuickFilter.height
        self.sr.scroll = Scroll(name='scroll', parent=self.sr.main, padding=const.defaultPadding)
        self.sr.scroll.multiSelect = 0
        self.sr.scroll.SelectAll = self.SelectAll
        self.sr.scroll.sr.content.OnDropData = self.MoveStuff
        self.Maximize()
        self.state = uiconst.UI_NORMAL
        stateTabs = [[localization.GetByLabel('UI/Overview/Colortag'),
          statebtns,
          self,
          'flag'], [localization.GetByLabel('UI/Overview/Background'),
          statebtns,
          self,
          'background']]
        self.sr.statetabs = TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=statetop, idx=0, tabs=stateTabs, groupID='overviewstatesTab', autoselecttab=0)
        self.statesPanel = StatesPanel(parent=self.sr.main, onChangeFunc=self.OnFilteredStatesChange)
        filterTabs = [[localization.GetByLabel('UI/Generic/Types'),
          btns,
          self,
          'filtertypes'], [localization.GetByLabel('UI/Generic/States'),
          self.statesPanel,
          self,
          'filterstates']]
        self.sr.filtertabs = TabGroup(name='overviewstatesTab', height=18, align=uiconst.TOBOTTOM, parent=filtertop, tabs=filterTabs, groupID='overviewfilterTab', autoselecttab=0)
        filtertop.height = top + self.sr.filtertabs.height
        settingsTabs = [[localization.GetByLabel('UI/Overview/OverviewTabs'),
          [],
          self,
          'overviewTabs',
          overviewtabtop],
         [FixedTabName('UI/Overview/TabPresetsTabName'),
          btns,
          self,
          'filters',
          filtertop],
         [FixedTabName('UI/Generic/Appearance'),
          statebtns,
          self,
          'appearance',
          statetop],
         [FixedTabName('UI/Generic/Columns'),
          colbtns,
          self,
          'columns',
          colLabel],
         [FixedTabName('UI/Common/ItemTypes/Ships'),
          [],
          self,
          'ships',
          shiptop],
         [FixedTabName('UI/Generic/Misc'),
          [],
          self,
          'misc',
          misctop],
         [FixedTabName('UI/Overview/ProfileHistory'),
          [],
          self,
          'history',
          historyCont]]
        self.sr.tabs = TabGroup(name='overviewsettingsTab', height=18, align=uiconst.TOTOP, parent=self.sr.main, idx=0, tabs=settingsTabs, groupID='overviewsettingsTab', UIIDPrefix='overviewSettingsTab')
        self.sr.statetabs.align = uiconst.TOBOTTOM
        self.minHeight = top + self.sr.tabs.height + const.defaultPadding * 2 + self.sr.topParent.height + 10
        self.minHeight += sum([ c.height for c in misctop.children ])
        self.ResetMinSize()
        self.UpdateStateTopHeight()

    def GetHistoryTab(self):
        historyCont = Container(name='historyCont', parent=self.sr.main, align=uiconst.TOALL)
        self.restoreCont = ContainerAutoSize(name='historyCont', parent=historyCont, align=uiconst.TOBOTTOM, left=const.defaultPadding, width=const.defaultPadding, alignMode=uiconst.TOTOP)
        Line(parent=historyCont, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.1))
        restoreButton = Button(parent=self.restoreCont, label=localization.GetByLabel('UI/Overview/RestoreProfile'), func=self.RestoreOldOverview, left=10, align=uiconst.CENTERRIGHT)
        restoreLabel = EveLabelMedium(text=localization.GetByLabel('UI/Overview/AutomaticallyStoredOverviewHeader'), parent=self.restoreCont, align=uiconst.TOTOP, padding=(10,
         3,
         restoreButton.width + 10,
         0), state=uiconst.UI_DISABLED)
        self.restoreOverviewNameLabel = EveLabelSmall(text='', parent=self.restoreCont, align=uiconst.TOTOP, padding=(10,
         0,
         restoreButton.width + 10,
         2), state=uiconst.UI_DISABLED)
        historyText = EveLabelMedium(text=localization.GetByLabel('UI/Overview/HistoryText'), parent=historyCont, align=uiconst.TOTOP, padding=(10, 3, 10, 0), state=uiconst.UI_DISABLED)
        historyText.color.SetRGBA(1, 1, 1, 0.8)
        self.historyEdit = EditPlainText(setvalue='', parent=historyCont, align=uiconst.TOALL, readonly=True, pos=(10, -2, 10, 0))
        self.historyEdit.HideBackground()
        self.historyEdit.RemoveActiveFrame()
        return historyCont

    def RestoreOldOverview(self, *args):
        restoreData = settings.user.overview.Get('restoreData', {})
        if not restoreData:
            return
        data = restoreData['data']
        overviewName = restoreData['name']
        self.overviewPresetSvc.LoadSettingsFromDict(data, overviewName)
        settings.user.overview.Set('restoreData', {})
        self.LoadRestoreData()

    def AddDraggableCont(self):
        currentText = self.overviewPresetSvc.GetOverviewName()
        defaultText = localization.GetByLabel('UI/Overview/DefaultOverviewName', charID=session.charid)
        configName = 'overviewProfileName'
        shareContainer = DraggableShareContainer(parent=self.sr.topParent, currentText=currentText, defaultText=defaultText, configName=configName, getDragDataFunc=self.overviewPresetSvc.GetShareData, hintText=localization.GetByLabel('UI/Overview/SharableOverviewIconHint'))
        self.overviewNameEdit = shareContainer.sharedNameLabel
        self.SetTopparentHeight(self.overviewNameEdit.height + 10)

    def RefreshOverviewName(self):
        currentText = self.overviewPresetSvc.GetOverviewName()
        self.overviewNameEdit.SetValue(currentText)
        self.overviewNameEdit.OnEditFieldChanged()

    def AddTabForOverviewProfile(self):
        overviewtabtop = Container(name='overviewtabtop', parent=self.sr.main, align=uiconst.TOALL, pos=(4, 0, 0, 0))
        parentGrid = LayoutGrid(parent=overviewtabtop, columns=3, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOPLEFT, left=10, top=0, cellSpacing=(15, 8))
        bracketOptions, overviewOptions = self.GetBracketAndOverviewOptions()
        for i in xrange(parentGrid.columns):
            container = Container(pos=(0, 0, 115, 0), name='spacer', align=uiconst.TOPLEFT)
            parentGrid.AddCell(cellObject=container)

        nameText = EveLabelMedium(parent=parentGrid, text=localization.GetByLabel('UI/Overview/TabName'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        overviewText = EveLabelMedium(parent=parentGrid, text=localization.GetByLabel('UI/Overview/OverviewPreset'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        bracketText = EveLabelMedium(parent=parentGrid, text=localization.GetByLabel('UI/Overview/BracketPreset'), state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.75), width=120)
        self.tabedit = {}
        self.comboTabOverview = {}
        self.comboTabBracket = {}
        tabsettings = self.overviewPresetSvc.GetTabSettingsForOverview()
        for i in range(MAX_TAB_NUM):
            comboTabBracketVal, comboTabOverviewVal, newOverviewOptions, tabeditVal = self.GetTabInfoForCombos(i, overviewOptions, tabsettings)
            tabedit = SinglelineEdit(name='edit' + str(i), align=uiconst.TOPLEFT, pos=(0, 0, 120, 0), setvalue=tabeditVal, OnFocusLost=self.ChangeTabText, OnReturn=self.UpdateOverviewTab)
            tabedit.originalValue = tabeditVal
            parentGrid.AddCell(cellObject=tabedit)
            self.tabedit[i] = tabedit
            comboTabOverview = Combo(label='', options=newOverviewOptions or overviewOptions, name='comboTabOverview', select=comboTabOverviewVal, align=uiconst.TOPLEFT, width=120, callback=self.OnProfileInTabChanged)
            self.comboTabOverview[i] = comboTabOverview
            parentGrid.AddCell(cellObject=comboTabOverview)
            comboTabBracket = Combo(label='', options=bracketOptions, name='comboTabBracket', select=comboTabBracketVal, width=120, align=uiconst.TOPLEFT, callback=self.OnProfileInTabChanged)
            self.comboTabBracket[i] = comboTabBracket
            parentGrid.AddCell(cellObject=comboTabBracket)

        return overviewtabtop

    def GetTabInfoForCombos(self, i, overviewOptions, tabsettings):
        tabeditVal = ''
        comboTabOverviewVal = None
        comboTabBracketVal = None
        newOverviewOptions = None
        if i in tabsettings:
            tabeditVal = tabsettings[i].get('name', None)
            comboTabBracketVal = tabsettings[i].get('bracket', None) or None
            comboTabOverviewVal = tabsettings[i].get('overview', None)
            if self.overviewPresetSvc.IsTempName(comboTabOverviewVal):
                displayName = self.overviewPresetSvc.GetPresetDisplayName(comboTabOverviewVal)
                newOverviewOptions = overviewOptions[:]
                newOverviewOptions.append((displayName, comboTabOverviewVal))
        return (comboTabBracketVal,
         comboTabOverviewVal,
         newOverviewOptions,
         tabeditVal)

    def OnProfileInTabChanged(self, *args):
        self.UpdateOverviewTab()

    def ChangeTabText(self, editField):
        currentValue = editField.GetValue()
        if currentValue != editField.originalValue:
            self.UpdateOverviewTab()

    def GetBracketAndOverviewOptions(self, includeEmpty = True):
        overviewOptions = []
        bracketOptions = []
        if includeEmpty:
            overviewOptions = [(' ', [' ', None])]
            bracketOptions = [('  ', [localization.GetByLabel('UI/Overview/ShowAllBrackets'), None])]
        presets = self.overviewPresetSvc.GetAllPresets()
        bothOptions = []
        for label in presets.keys():
            if self.overviewPresetSvc.IsTempName(label):
                continue
            elif label == 'ccp_notsaved':
                bothOptions.append(('   ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                overviewName = self.overviewPresetSvc.GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if overviewName is not None:
                    bothOptions.append((lowerLabel, [overviewName, label]))
                else:
                    bothOptions.append((lowerLabel, [label, label]))

        overviewOptions = [ x[1] for x in localization.util.Sort(overviewOptions + bothOptions, key=operator.itemgetter(0)) ]
        bracketOptions = [ x[1] for x in localization.util.Sort(bracketOptions + bothOptions, key=operator.itemgetter(0)) ]
        return (bracketOptions, overviewOptions)

    def UpdateStateTopHeight(self):
        self.statetop.height = sum((c.height for c in self.statetop.children))

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        if self.currentKey is None:
            return
        if self.currentKey == 'columns':
            self.MoveColumn(idx)
        elif self.currentKey in ('flag', 'background'):
            self.Move(idx)
        elif self.currentKey == 'ships':
            self.MoveShipLabel(idx)

    def OnTacticalPresetChange(self, label, preset):
        presetName = self.overviewPresetSvc.GetPresetDisplayName(label)
        self.sr.presetText.text = presetName
        self.RefreshOverviewTab()
        if self.sr.filtertabs.IsVisible() and self.sr.filtertabs.GetSelectedArgs() in ('filtertypes', 'filterstates'):
            self.sr.filtertabs.ReloadVisible()

    def OnOverviewPresetSaved(self):
        overviewOptions = [(' ', [' ', None])]
        bracketOptions = [(' ', [localization.GetByLabel('UI/Overview/ShowAllBrackets'), None])]
        tabsettings = self.overviewPresetSvc.GetTabSettingsForOverview()
        presets = self.overviewPresetSvc.GetAllPresets()
        for label in presets.keys():
            if label == 'ccp_notsaved':
                overviewOptions.append(('  ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
                bracketOptions.append(('  ', [localization.GetByLabel('UI/Overview/NotSaved'), label]))
            else:
                presetName = self.overviewPresetSvc.GetDefaultOverviewName(label)
                lowerLabel = label.lower()
                if presetName is not None:
                    overviewOptions.append((lowerLabel, [presetName, label]))
                    bracketOptions.append((lowerLabel, [presetName, label]))
                else:
                    overviewOptions.append((lowerLabel, [label, label]))
                    bracketOptions.append((lowerLabel, [label, label]))

        overviewOptions = [ x[1] for x in localization.util.Sort(overviewOptions, key=lambda x: x[0]) ]
        bracketOptions = [ x[1] for x in localization.util.Sort(bracketOptions, key=lambda x: x[0]) ]
        for i in range(MAX_TAB_NUM):
            comboTabOverviewVal = None
            comboTabBracketVal = None
            editFieldText = None
            if tabsettings.has_key(i):
                comboTabOverviewVal = tabsettings[i].get('overview', None)
                comboTabBracketVal = tabsettings[i].get('bracket', None)
                editFieldText = tabsettings[i].get('name', None)
            self.comboTabOverview[i].LoadOptions(overviewOptions, comboTabOverviewVal)
            self.comboTabBracket[i].LoadOptions(bracketOptions, comboTabBracketVal)
            if editFieldText:
                self.tabedit[i].SetText(editFieldText)
                self.tabedit[i].originalValue = editFieldText

    def ExportSettings(self, *args):
        pass

    def ResetAllOverviewSettings(self, *args):
        if eve.Message('ResetAllOverviewSettings', {}, uiconst.YESNO) != uiconst.ID_YES:
            return
        settings.user.overview.Set('presetHistoryKeys', {})
        self.overviewPresetSvc.ResetPresetsToDefault()
        self.overviewPresetSvc.ResetActivePresets()
        oldTabs = self.overviewPresetSvc.GetTabSettingsForOverview()
        values = settings.user.overview.GetValues()
        keys = values.keys()
        for key in keys:
            settings.user.overview.Delete(key)

        overviewWindow = OverView.GetIfOpen()
        if overviewWindow:
            newTabs = self.overviewPresetSvc.GetTabSettingsForOverview()
            overviewWindow.OnOverviewTabChanged(newTabs, oldTabs)
        stateSvc = sm.StartService('state')
        stateSvc.SetDefaultShipLabel('default')
        stateSvc.ResetColors()
        default = self.overviewPresetSvc.GetDefaultOverviewGroups('default')
        settings.user.overview.Set('overviewProfilePresets', {'default': default})
        sm.GetService('bracket').Reload()
        self.CloseByUser()

    def DoFontChange(self):
        self.ResetMinSize()

    def ResetMinSize(self):
        maxBtnWidth = max([ wnd.GetChild('btns').width for wnd in self.sr.main.children if wnd.name == 'btnsmainparent' ])
        margin = 12
        minWidth = max(self.minWidth, maxBtnWidth + margin * 2)
        self.SetMinSize((minWidth, self.minHeight))

    ResetMinSize = ParanoidDecoMethod(ResetMinSize, ('sr', 'main'))

    def SelectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        groups = []
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 1
                if entry.panel:
                    entry.panel.Load(entry)
            if entry.__guid__ == 'listentry.Group':
                for item in entry.groupItems:
                    if type(item[0]) == list:
                        groups += item[0]
                    else:
                        groups.append(item[0])

        if groups:
            self.overviewPresetSvc.SetSettings('groups', groups)

    def DeselectAll(self, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        for entry in self.sr.scroll.GetNodes():
            if entry.__guid__ == 'listentry.Checkbox':
                entry.checked = 0
                if entry.panel:
                    entry.panel.Load(entry)

        self.overviewPresetSvc.SetSettings('groups', [])

    def GetPresetsMenu(self):
        p = self.overviewPresetSvc.GetAllPresets().keys()
        p.sort()
        for name in self.overviewPresetSvc.GetDefaultOverviewNameList():
            if name in p:
                p.remove(name)

        m = []
        m += [None, (MenuLabel('UI/Commands/ExportOverviewSettings'), sm.GetService('tactical').ExportOverviewSettings), (MenuLabel('UI/Overview/ImportOverviewSettings'), sm.GetService('tactical').ImportOverviewSettings)]
        dm = []
        for label in p:
            if self.overviewPresetSvc.IsTempName(label):
                continue
            dm.append((label.lower(), (label, self.overviewPresetSvc.DeletePreset, (label,))))

        if dm:
            m.append(None)
            dm = SortListOfTuples(dm)
            m.append((MenuLabel('UI/Common/Delete'), dm))
        return m

    def GetShipLabelMenu(self):
        return [(localization.GetByLabel('UI/Overview/ShipLabelFormatPilotCC'), self.SetDefaultShipLabel, ('default',)), (localization.GetByLabel('UI/Overview/ShipLabelFormatPilotCCAA'), self.SetDefaultShipLabel, ('ally',)), (localization.GetByLabel('UI/Overview/ShipLabelFormatCCPilotAA'), self.SetDefaultShipLabel, ('corpally',))]

    def SetDefaultShipLabel(self, setting):
        sm.GetService('state').SetDefaultShipLabel(setting)
        self.LoadShips()

    def Load(self, key):
        if self.currentKey is None or self.currentKey != key:
            self.cachedScrollPos = 0
        self.currentKey = key
        self.sr.scroll.state = uiconst.UI_NORMAL
        self.statesPanel.display = False
        self.groupQuickFilterCont.display = False
        if key == 'filtertypes':
            self.groupQuickFilterCont.display = True
            self.LoadTypes()
        elif key == 'filterstates':
            self.statesPanel.display = True
            self.sr.scroll.state = uiconst.UI_HIDDEN
            self.statesPanel.Load()
        elif key == 'columns':
            self.LoadColumns()
        elif key == 'appearance':
            self.sr.statetabs.AutoSelect()
        elif key == 'filters':
            self.sr.filtertabs.AutoSelect()
        elif key == 'ships':
            self.LoadShips()
        elif key == 'misc':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'overviewTabs':
            self.sr.scroll.state = uiconst.UI_HIDDEN
        elif key == 'history':
            self.sr.scroll.state = uiconst.UI_HIDDEN
            self.LoadHistory()
        else:
            self.LoadFlags()

    def LoadFlags(self, selected = None):
        where = self.sr.statetabs.GetSelectedArgs()
        flagOrder = sm.GetService('state').GetStateOrder(where)
        scrolllist = []
        i = 0
        for flag in flagOrder:
            props = sm.GetService('state').GetStateProps(flag)
            data = KeyVal()
            data.label = props.text
            data.props = props
            data.checked = sm.GetService('state').GetStateState(where, flag)
            data.cfgname = where
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = props.hint
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('FlagEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadShips(self, selected = None):
        shipLabels = sm.GetService('state').GetShipLabels()
        allLabels = sm.GetService('state').GetAllShipLabels()
        corpTickerHidden = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName('hideCorpTicker', False)
        self.sr.hideTickerIfInAlliance.SetChecked(corpTickerHidden)
        hints = {None: '',
         'corporation': localization.GetByLabel('UI/Common/CorpTicker'),
         'alliance': localization.GetByLabel('UI/Shared/AllianceTicker'),
         'pilot name': localization.GetByLabel('UI/Common/PilotName'),
         'ship name': localization.GetByLabel('UI/Common/ShipName'),
         'ship type': localization.GetByLabel('UI/Common/ShipType')}
        comments = {None: localization.GetByLabel('UI/Overview/AdditionalTextForCorpTicker'),
         'corporation': localization.GetByLabel('UI/Overview/OnlyShownForPlayerCorps'),
         'alliance': localization.GetByLabel('UI/Overview/OnlyShownWhenAvailable')}
        newlabels = [ label for label in allLabels if label['type'] not in [ alabel['type'] for alabel in shipLabels ] ]
        shipLabels += newlabels
        scrolllist = []
        for i, flag in enumerate(shipLabels):
            data = KeyVal()
            data.label = hints[flag['type']]
            data.checked = flag['state']
            data.cfgname = 'shiplabels'
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = hints[flag['type']]
            data.comment = comments.get(flag['type'], '')
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(listentry.Get('ShipEntry', data=data))

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))
        maxLeft = 140
        for shipEntry in self.sr.scroll.GetNodes():
            if shipEntry.panel:
                postLeft = shipEntry.panel.sr.label.left + shipEntry.panel.sr.label.textwidth + 4
                maxLeft = max(maxLeft, postLeft)

        for shipEntry in self.sr.scroll.GetNodes():
            if shipEntry.panel:
                shipEntry.panel.postCont.left = maxLeft

    def Move(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeStateOrder(self.GetWhere(), selected.flag, newIdx)
            self.LoadFlags(newIdx)

    def GetWhere(self):
        where = self.sr.statetabs.GetSelectedArgs()
        return where

    def ResetStateSettings(self, *args):
        where = self.sr.statetabs.GetSelectedArgs()
        settings.user.overview.Set('flagOrder', None)
        settings.user.overview.Set('iconOrder', None)
        settings.user.overview.Set('backgroundOrder', None)
        settings.user.overview.Set('flagStates', None)
        settings.user.overview.Set('iconStates', None)
        settings.user.overview.Set('backgroundStates', None)
        settings.user.overview.Set('stateColors', {})
        sm.GetService('state').InitColors(1)
        settings.user.overview.Set('stateBlinks', {})
        defaultApplyOnlyToShips = sm.GetService('overviewPresetSvc').GetDefaultSettingValueFromName('applyOnlyToShips', True)
        settings.user.overview.Set('applyOnlyToShips', defaultApplyOnlyToShips)
        self.sr.applyOnlyToShips.SetChecked(defaultApplyOnlyToShips, 0)
        defaultUseSmallColorTags = sm.GetService('overviewPresetSvc').GetDefaultSettingValueFromName('useSmallColorTags', False)
        settings.user.overview.Set('useSmallColorTags', defaultUseSmallColorTags)
        self.sr.useSmallColorTags.SetChecked(defaultUseSmallColorTags, 0)
        self.LoadFlags()
        sm.GetService('state').NotifyOnStateSetupChange('reset')

    def LoadColumns(self, selected = None):
        userSet = sm.GetService('tactical').GetColumns()
        userSetOrder = sm.GetService('tactical').GetColumnOrder()
        missingColumns = [ col for col in sm.GetService('tactical').GetAllColumns() if col not in userSetOrder ]
        userSetOrder += missingColumns
        i = 0
        scrolllist = []
        for columnID in userSetOrder:
            data = KeyVal()
            data.label = sm.GetService('tactical').GetColumnLabel(columnID)
            data.checked = columnID in userSet
            data.cfgname = 'columns'
            data.retval = columnID
            data.canDrag = True
            data.isSelected = selected == i
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('ColumnEntry', data=data))
            i += 1

        self.sr.scroll.Load(contentList=scrolllist, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def LoadFilteredTypes(self, *args):
        self.LoadTypes()

    def LoadTypes(self):
        filterText = self.groupQuickFilter.GetValue()
        categoryList = self.GetListOfCategories(filterText=filterText.lower())
        sortCat = categoryList.keys()
        sortCat.sort()
        presetName = self.overviewPresetSvc.GetActiveOverviewPresetName()
        scrolllist = []
        userSettings = self.overviewPresetSvc.GetPresetGroupsFromKey(presetName)
        for catName in sortCat:
            checkedCounter = 0
            groupItems = categoryList[catName]
            for groupID, name in groupItems:
                if isinstance(groupID, list):
                    for each in groupID:
                        if each in userSettings:
                            checkedCounter += 1
                            break

                else:
                    checkedCounter += int(groupID in userSettings)

            posttext = '[%s/%s]' % (checkedCounter, len(groupItems))
            data = {'GetSubContent': self.GetCatSubContent,
             'label': catName,
             'MenuFunction': self.GetSubFolderMenu,
             'id': ('GroupSel', catName),
             'groupItems': groupItems,
             'showlen': 0,
             'sublevel': 0,
             'state': 'locked',
             'presetName': presetName,
             'showicon': 'hide',
             'posttext': posttext}
            scrolllist.append(listentry.Get('Group', data))

        self.sr.scroll.Load(contentList=scrolllist, scrolltotop=0, scrollTo=getattr(self, 'cachedScrollPos', 0.0))

    def GetListOfCategories(self, filterText = ''):
        categoryList = {}
        for _, groupid_name_tuple in tacticalConst.groups:
            groupID, name = groupid_name_tuple
            if filterText and name.lower().find(filterText) < 0:
                continue
            for cat, groupdict in self.specialGroups.iteritems():
                for group, groupIDs in groupdict.iteritems():
                    if groupID in groupIDs:
                        catName = cat
                        groupID = groupIDs
                        name = group
                        break
                else:
                    continue

                break
            else:
                catName = evetypes.GetCategoryNameByGroup(groupID)

            if catName not in categoryList:
                categoryList[catName] = [(groupID, name)]
            elif (groupID, name) not in categoryList[catName]:
                categoryList[catName].append((groupID, name))

        return categoryList

    def GetSubFolderMenu(self, node):
        m = [None, (localization.GetByLabel('UI/Common/SelectAll'), self.SelectGroup, (node, True)), (localization.GetByLabel('UI/Common/DeselectAll'), self.SelectGroup, (node, False))]
        return m

    def SelectGroup(self, node, isSelect):
        groups = []
        for entry in node.groupItems:
            if type(entry[0]) == list:
                for entry1 in entry[0]:
                    groups.append(entry1)

            else:
                groups.append(entry[0])

        chageList = [('groups', groups, isSelect)]
        sm.StartService('overviewPresetSvc').ChangeSettings(changeList=chageList)

    def GetCatSubContent(self, nodedata, newitems = 0):
        presetName = nodedata.presetName
        userSettings = self.overviewPresetSvc.GetPresetGroupsFromKey(presetName)
        scrolllist = []
        for groupID, name in nodedata.groupItems:
            if type(groupID) == list:
                for each in groupID:
                    if each in userSettings:
                        checked = 1
                        break
                else:
                    checked = 0

            else:
                name = evetypes.GetGroupNameByGroup(groupID)
                checked = groupID in userSettings
            data = KeyVal()
            data.label = name
            data.sublevel = 1
            data.checked = checked
            data.cfgname = 'groups'
            data.retval = groupID
            data.OnChange = self.CheckBoxChange
            scrolllist.append(listentry.Get('Checkbox', data=data))

        return scrolllist

    def LoadHistory(self):
        presetHistoryKeys = settings.user.overview.Get('presetHistoryKeys', {})
        textList = []
        for eachKey, eachValue in presetHistoryKeys.iteritems():
            overviewName = eachValue.get('overviewName', 'overview_name')
            presetKey = eachValue.get('presetKey')
            timestamp = eachValue.get('timestamp')
            overviewLink = '<a href="overviewPreset:%s//%s">%s</a>' % (presetKey[0], presetKey[1], overviewName)
            text = localization.GetByLabel('UI/Overview/ProfileLinkWithTimestamp', profileLink=overviewLink, timestamp=FmtDate(timestamp))
            textList.append((timestamp, text))

        textList = SortListOfTuples(textList, reverse=True)
        allText = '<br>'.join(textList[:15])
        self.historyEdit.SetValue(allText)
        self.LoadRestoreData()

    def LoadRestoreData(self):
        restoreData = settings.user.overview.Get('restoreData', {})
        if not restoreData:
            self.restoreCont.display = False
            return
        self.restoreCont.display = True
        overviewName = restoreData['name']
        timestamp = restoreData['timestamp']
        self.restoreOverviewNameLabel.text = localization.GetByLabel('UI/Overview/StoredOverviewBasedOn', overviewName=overviewName, timestamp=FmtDate(timestamp))

    def MoveColumn(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            column = selected.retval
            current = sm.GetService('tactical').GetColumnOrder()[:]
            while column in current:
                current.remove(column)

            if idx == -1:
                idx = len(current)
            current.insert(idx, column)
            settings.user.overview.Set('overviewColumnOrder', current)
            self.LoadColumns(newIdx)
            self.DoFullOverviewReload()

    def ResetColumns(self, *args):
        settings.user.overview.Set('overviewColumnOrder', None)
        settings.user.overview.Set('overviewColumns', None)
        self.LoadColumns()
        sm.GetService('state').NotifyOnStateSetupChange('column reset')

    def DoFullOverviewReload(self):
        overview = OverView.GetIfOpen()
        if overview:
            overview.FullReload()

    def CheckBoxChange(self, checkbox):
        if self and not self.destroyed:
            self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        if checkbox.data.has_key('config'):
            config = checkbox.data['config']
            if config == 'applyOnlyToShips':
                sm.GetService('tactical').SetNPCGroups()
                sm.GetService('state').InitFilter()
                sm.GetService('state').NotifyOnStateSetupChange('filter')
                self.DoFullOverviewReload()
                sm.GetService('bracket').Reload()
            elif config == 'hideCorpTicker':
                sm.GetService('bracket').UpdateLabels()
            elif config == 'useSmallColorTags':
                sm.GetService('state').NotifyOnStateSetupChange('filter')
            elif config == 'useSmallText':
                if checkbox.checked:
                    settings.user.overview.Set('useSmallText', 1)
                else:
                    settings.user.overview.Set('useSmallText', 0)
                self.DoFullOverviewReload()
        if checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'groups':
                changeList = [(key, checkbox.data['retval'], checkbox.checked)]
                self.overviewPresetSvc.ChangeSettings(changeList=changeList)
            elif key == 'columns':
                checked = checkbox.checked
                column = checkbox.data['retval']
                current = sm.GetService('tactical').GetColumns()[:]
                while column in current:
                    current.remove(column)

                if checked:
                    current.append(column)
                settings.user.overview.Set('overviewColumns', current)
                self.DoFullOverviewReload()
            elif key == self.GetWhere():
                sm.GetService('state').ChangeStateState(self.GetWhere(), checkbox.data['retval'], checkbox.checked)
            elif key == 'shiplabels':
                sm.GetService('state').ChangeShipLabels(checkbox.data['retval'], checkbox.checked)
                return
        blue.pyos.synchro.Yield()
        uicore.registry.SetFocus(self.sr.scroll)

    def OnFilteredStatesChange(self, node, configToChange, *args):
        if node:
            selected = self.statesPanel.statesScroll.GetSelectedNodes(node)
        else:
            selected = self.statesPanel.statesScroll.GetSelected()
        flags = [ x.flag for x in selected ]
        addAlwaysShow = False
        addFilterOut = False
        if configToChange == 'alwaysShow':
            addAlwaysShow = True
        elif configToChange == 'filterOut':
            addFilterOut = True
        changeList = [('filteredStates', flags, addFilterOut), ('alwaysShownStates', flags, addAlwaysShow)]
        self.overviewPresetSvc.ChangeSettings(changeList=changeList)

    def MoveShipLabel(self, idx = None, *args):
        self.cachedScrollPos = self.sr.scroll.GetScrollProportion()
        selected = self.sr.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            sm.GetService('state').ChangeLabelOrder(selected.idx, newIdx)
            self.LoadShips(newIdx)

    def OnRefreshOverviewTab(self):
        sm.GetService('bracket').UpdateLabels()
        self.RefreshOverviewTab()

    def OnReloadingOverviewProfile(self):
        self.RefreshOverviewName()
        self.LoadHistory()
        self.sr.tabs.AutoSelect()
        defaultSettings = self.overviewPresetSvc.GetSettingsNamesAndDefaults()
        for eachCb in self.settingCheckboxes:
            configName = eachCb.data['config']
            defaultValue = defaultSettings.get(configName, True)
            newValue = self.overviewPresetSvc.GetSettingValueOrDefaultFromName(configName, defaultValue)
            eachCb.SetChecked(newValue, report=0)

    def RefreshOverviewTab(self):
        tabSettings = self.overviewPresetSvc.GetTabSettingsForOverview()
        for key, editContainer in self.tabedit.iteritems():
            tSetting = tabSettings.get(key, {})
            if tSetting is None:
                continue
            comboTabOverviewContainer = self.comboTabOverview.get(key, None)
            comboTabBracketContainer = self.comboTabBracket.get(key, None)
            editField = self.tabedit.get(key, None)
            if None in (comboTabOverviewContainer, comboTabBracketContainer, editField):
                continue
            overviewSetting = tSetting.get('overview', None)
            bracketSetting = tSetting.get('bracket', None)
            tabName = tSetting.get('name', '')
            bracketOptions, overviewOptions = self.GetBracketAndOverviewOptions()
            newOverviewOptions = None
            if self.overviewPresetSvc.IsTempName(overviewSetting):
                currBracket, currOverview, newOverviewOptions, tabName = self.GetTabInfoForCombos(key, overviewOptions, tabSettings)
            comboTabOverviewContainer.LoadOptions(newOverviewOptions or overviewOptions)
            comboTabOverviewContainer.SelectItemByValue(overviewSetting)
            comboTabBracketContainer.SelectItemByValue(bracketSetting)
            editField.SetText(tabName)
            editField.originalValue = tabName

    def UpdateOverviewTab(self, *args):
        tabSettings = {}
        for key in self.tabedit.keys():
            editContainer = self.tabedit.get(key, None)
            comboTabBracketContainer = self.comboTabBracket.get(key, None)
            comboTabOverviewContainer = self.comboTabOverview.get(key, None)
            if not (editContainer and comboTabOverviewContainer and comboTabBracketContainer):
                continue
            if not editContainer.text:
                continue
            tabSettings[key] = {'name': editContainer.text,
             'bracket': comboTabBracketContainer.selectedValue,
             'overview': comboTabOverviewContainer.selectedValue}

        oldtabsettings = self.overviewPresetSvc.GetTabSettingsForOverview()
        sm.ScatterEvent('OnOverviewTabChanged', tabSettings, oldtabsettings)

    def _OnResize(self, *args):
        self.UpdateStateTopHeight()

    def MiscCheckboxChange(self, cb, *args):
        configName = cb.data.get('config', '')
        if configName == 'showInTargetRange':
            self.ChangeStateOfSubCheckboxes(cb)
        elif configName == 'showBiggestDamageDealers':
            if cb.checked:
                sm.GetService('bracket').EnableShowingDamageDealers()
            else:
                sm.GetService('bracket').DisableShowingDamageDealers()
        elif configName in ('targetCrosshair',):
            sm.GetService('bracket').Reload()
        elif cb in self.targetRangeSubCheckboxes:
            sm.GetService('bracket').ShowInTargetRange()

    def ChangeStateOfSubCheckboxes(self, cb):
        if cb.checked:
            sm.GetService('bracket').EnableInTargetRange()
            for subCb in self.targetRangeSubCheckboxes:
                subCb.Enable()
                subCb.opacity = 1.0

        else:
            sm.GetService('bracket').DisableInTargetRange()
            for subCb in self.targetRangeSubCheckboxes:
                subCb.Disable()
                subCb.opacity = 0.3
