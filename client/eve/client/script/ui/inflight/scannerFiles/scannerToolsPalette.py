#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerFiles\scannerToolsPalette.py
import weakref
import functools
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.control.menuLabel import MenuLabel
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
from eve.client.script.ui.control.scrollColumnHeader import ScrollColumnHeader
from inventorycommon.const import groupSurveyProbe
import carbonui.const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite, GradientConst
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.buttons import BigButton, ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.primaryButton import PrimaryButton
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.inflight.scannerFiles.scannerToolsUIComponents import FilterBox, IgnoredBox, ProbeTooltipButtonRow, ProbeTooltipCheckboxRow, FormationButton
from eve.client.script.ui.inflight.scannerListEntries import NoScanProbesEntry, ScanResultNew
from eve.client.script.ui.inflight.scannerfiltereditor import ScannerFilterEditor
from eve.client.script.ui.shared.mapView.dockPanelMenu import DockPanelMenuContainer
import evetypes
import localization
from probescanning.const import probeStateIdle, probeStateInactive, probeScanGroupAnomalies
import probescanning.formations as formations
from sensorsuite.overlay.controllers.probescanner import SiteDataFromScanResult
import trinity
import uthread
from eveexceptions import UserError
from utillib import KeyVal
import listentry
import blue

def AddFilter(*args):
    editor = ScannerFilterEditor.Open()
    editor.LoadData(None)


def UserErrorIfScanning(action, *args, **kwargs):

    @functools.wraps(action)
    def wrapper(*args, **kwargs):
        if sm.GetService('scanSvc').IsScanning():
            raise UserError('ScanInProgressGeneric')
        return action(*args, **kwargs)

    return wrapper


class ScannerToolsPalette(Container):
    __notifyevents__ = ['OnProbeAdded',
     'OnProbeRemoved',
     'OnSystemScanFilterChanged',
     'OnSystemScanBegun',
     'OnSystemScanDone',
     'OnNewScannerFilterSet',
     'OnProbeStateUpdated',
     'OnProbePositionsUpdated',
     'OnScannerDisconnected',
     'OnRefreshScanResults',
     'OnBallparkSetState',
     'OnReconnectToProbesAvailable']
    __disallowanalysisgroups = [groupSurveyProbe]
    filteredBoxTooltip = None
    isBeingTransformed = False
    solarSystemView = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.scanSvc = sm.GetService('scanSvc')
        toolbar = Container(parent=self, align=uiconst.TOTOP, height=36, padBottom=4)
        buttonGrid = LayoutGrid(parent=toolbar, align=uiconst.TOPLEFT, columns=8, cellPadding=(0, 0, 4, 0))
        self.analyzeButton = PrimaryButton(parent=buttonGrid, label=localization.GetByLabel('UI/Inflight/Scanner/Analyze'), func=self.Analyze)
        self.scanAnimator = Container(parent=self.analyzeButton, name='scanAnimator', align=uiconst.TOLEFT_PROP, clipChildren=True)
        GradientSprite(parent=self.scanAnimator, align=uiconst.TORIGHT, pos=(0, 0, 200, 0), rgbData=[(0, (0.3, 0.5, 0.9)), (1, (0.3, 0.8, 0.7))], alphaData=[(0, 0),
         (0.95, 0.3),
         (0.99, 0.5),
         (1, 1)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR)
        menuParent = DockPanelMenuContainer(parent=self, state=uiconst.UI_PICKCHILDREN, clipChildren=True)
        self.menuParent = menuParent
        probesMenu = self.menuParent.CreateMenu(settingsID='probeScanner_probesMenu', headerLabel=localization.GetByLabel('UI/Inflight/Scanner/Probes'), minExpandedHeight=52, expandedByDefault=True)
        self.probesMenu = probesMenu
        self.probesScroll = Scroll(name='probesScroll', parent=probesMenu.content, padding=2)
        self.probesScroll.HideBackground()
        self.probesHeaderContent = LayoutGrid(parent=probesMenu.headerParent, align=uiconst.CENTERRIGHT, columns=8, cellPadding=(2, 1, 2, 1), left=4, idx=0)
        BumpedUnderlay(bgParent=probesMenu.content, name='background')
        resultMenu = self.menuParent.CreateMenu(settingsID='probeScanner_resultMenu', headerLabel=localization.GetByLabel('UI/Inflight/Scanner/ScanResults'), minExpandedHeight=120, fillParent=True, resizeable=False, expandedByDefault=True)
        self.resultMenu = resultMenu
        self.resultScroll = BasicDynamicScroll(name='resultscroll', parent=resultMenu.content, id='probescannerwindow_resultScrollList', padding=(2, 0, 2, 2))
        self.resultScroll.HideBackground()
        self.resultScroll.OnSelectionChange = self.OnSelectionChange
        self.sortHeaders = ScrollColumnHeader(parent=self.resultScroll, settingsID='probescannerwindow_resultScrollList', idx=0, scroll=self.resultScroll, entryClass=ScanResultNew)
        self.resultHeaderContent = LayoutGrid(parent=resultMenu.headerParent, align=uiconst.CENTERRIGHT, columns=2, cellPadding=(0, 0, 3, 0), left=1)
        BumpedUnderlay(bgParent=resultMenu.content, name='background')
        self.formationButtonsByID = {}
        btn = BigButton(parent=buttonGrid, width=32, height=32, hint=localization.GetByLabel('UI/Inflight/Scanner/LaunchPinpointFormation'))
        btn.Startup(32, 32)
        btn.sr.icon.SetTexturePath('res:/UI/Texture/classes/ProbeScanner/pinpointFormation.png')
        btn.OnClick = (lambda *args: self.LaunchFormation(formations.PINPOINT_FORMATION, 4),)
        self.formationButtonsByID[formations.PINPOINT_FORMATION] = btn
        btn = BigButton(parent=buttonGrid, width=32, height=32, hint=localization.GetByLabel('UI/Inflight/Scanner/LaunchSpreadFormation'))
        btn.Startup(32, 32)
        btn.sr.icon.SetTexturePath('res:/UI/Texture/classes/ProbeScanner/spreadFormation.png')
        btn.OnClick = (lambda *args: self.LaunchFormation(formations.SPREAD_FORMATION, 32),)
        self.formationButtonsByID[formations.SPREAD_FORMATION] = btn
        self.customFormationButton = FormationButton(parent=buttonGrid, width=32, height=32)
        self.recoverButton = BigButton(parent=buttonGrid, hint=localization.GetByLabel('UI/Inflight/Scanner/RecoverActiveProbes'), width=32, height=32)
        self.recoverButton.Startup(32, 32)
        self.recoverButton.sr.icon.SetTexturePath('res:/UI/Texture/Classes/ProbeScanner/recoverProbesIcon.png')
        self.recoverButton.OnClick = self.RecoverActiveProbes
        btn = BigButton(parent=toolbar, width=32, height=32, hint=localization.GetByLabel('UI/Map/MapPallet/btnSolarsystemMap'), align=uiconst.TOPRIGHT)
        btn.Startup(32, 32)
        btn.sr.icon.SetTexturePath('res:/UI/Texture/classes/ProbeScanner/solarsystemMapButton.png')
        btn.OnClick = self.ToggleSolarSystemView
        self.reconnectButton = ButtonIcon(hint=localization.GetByLabel('UI/Inflight/Scanner/ReconnectActiveProbes'), func=self.ReconnectToLostProbes, texturePath='res:/UI/Texture/Classes/ProbeScanner/reconnectProbesIcon.png', parent=self.probesHeaderContent, iconSize=17, width=17, height=17)
        filtered = localization.GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=0)
        self.filteredBox = FilterBox(parent=self.resultHeaderContent, text=filtered, state=uiconst.UI_NORMAL)
        self.filteredBox.LoadTooltipPanel = self.LoadFilterTooltipPanel
        ignored = localization.GetByLabel('UI/Inflight/Scanner/Ignored', noIgnored=0)
        self.ignoredBox = IgnoredBox(parent=self.resultHeaderContent, text=ignored, state=uiconst.UI_NORMAL)
        self.ignoredBox.LoadTooltipPanel = self.LoadIgnoredTooltipPanel
        if settings.user.ui.Get('scannerShowAnomalies', True):
            self.scanSvc.ShowAnomalies()
        else:
            self.scanSvc.StopShowingAnomalies()
        self.LoadProbeList()
        if self.destroyed:
            return
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is not None:
            uthread.new(self.LoadResultList)
        self.Refresh()
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            solarSystemView.StartProbeHandler()
        sm.RegisterNotify(self)

    def Close(self, *args):
        sm.UnregisterNotify(self)
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            solarSystemView.StopProbeHandler()
        Container.Close(self, *args)

    def ToggleSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if not SolarSystemViewPanel.ClosePanel():
            SolarSystemViewPanel.OpenPanel()

    def GetSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        solarSystemView = SolarSystemViewPanel.GetPanel()
        if solarSystemView and not solarSystemView.destroyed:
            return solarSystemView

    def OnGlobalKeyUpCallback(self, wnd, eventID, (vkey, flag), *args):
        if self.destroyed:
            return False
        activeToplevel = uicore.registry.GetActive()
        isWindow = isinstance(activeToplevel, Window)
        isUnderActiveWindow = isWindow and self.IsUnder(activeToplevel)
        mouseInside = uicore.uilib.mouseOver.IsUnder(self)
        if not any((isUnderActiveWindow, mouseInside)):
            return True
        if vkey == uiconst.VK_1:
            toggleState = not settings.user.ui.Get('scannerShowAnomalies', True)
            settings.user.ui.Set('scannerShowAnomalies', toggleState)
            if toggleState:
                self.scanSvc.ShowAnomalies()
            else:
                self.scanSvc.StopShowingAnomalies()
            uthread.new(self.ReloadFilteredBoxTooltip)
        elif vkey in (uiconst.VK_2,
         uiconst.VK_3,
         uiconst.VK_4,
         uiconst.VK_5):
            filterOptions = self.scanSvc.GetFilterOptions()
            filterOptionIDs = [ filterID for filterName, filterID in filterOptions if filterID < 0 ]
            filterIndex = [uiconst.VK_2,
             uiconst.VK_3,
             uiconst.VK_4,
             uiconst.VK_5].index(vkey)
            filterID = filterOptionIDs[filterIndex]
            activeFilters = self.scanSvc.GetActiveFilterSet()
            if filterID in activeFilters:
                self.scanSvc.RemoveFromActiveFilterSet(filterID)
            else:
                self.scanSvc.AddToActiveFilterSet(filterID)
            uthread.new(self.ReloadFilteredBoxTooltip)
        return True

    def ClearIgnoredResults(self, *args, **kwds):
        self.scanSvc.ClearIgnoredResults()

    def ClearFilteredResults(self):
        self.scanSvc.SetActiveFilter(0)
        self.LoadResultList()

    def OnSystemScanFilterChanged(self, *args):
        self.LoadResultList()

    def OnSystemScanBegun(self):
        self.Refresh()
        uicore.animations.FadeTo(self.resultScroll, duration=0.5, startVal=1.0, endVal=0.5)
        scanSvc = sm.GetService('scanSvc')
        currentScan = scanSvc.GetCurrentScan()
        self.scanAnimator.state = uiconst.UI_NORMAL
        uicore.animations.FadeIn(self.scanAnimator, duration=0.5)
        uicore.animations.MorphScalar(self.scanAnimator, 'width', 0, 1, duration=currentScan.duration / 1000 + 0.5, callback=self.FadeOutScanAnimator)

    def FadeOutScanAnimator(self):
        uicore.animations.FadeOut(self.scanAnimator, duration=0.5, callback=self.HideScanAnimator)

    def HideScanAnimator(self):
        self.scanAnimator.state = uiconst.UI_HIDDEN
        self.scanAnimator.width = 0

    def OnSystemScanDone(self):
        self.Refresh()
        uicore.animations.FadeTo(self.resultScroll, duration=0.2, startVal=self.resultScroll.opacity, endVal=1.0)

    def GetProbesTooltipPointer(self):
        return uiconst.POINT_TOP_3

    def LoadHelpTooltip(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.margin = (12, 4, 4, 4)
        tooltipPanel.cellPadding = (1, 1, 1, 1)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/HelpToModify'), wrapWidth=120)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/HelpHold'), align=uiconst.CENTERRIGHT)
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/FormationProbeRange'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_MENU), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/FormationSpread'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_CONTROL), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))
        tooltipPanel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/OneProbe'), wrapWidth=120)
        tooltipPanel.AddCell(ShortcutHint(text=trinity.app.GetKeyNameText(uiconst.VK_SHIFT), align=uiconst.TOPRIGHT), cellPadding=(6, 1, 1, 1))

    def LoadFilterTooltipPanel(self, tooltipPanel, *args):
        return self._LoadFilterTooltipPanel(tooltipPanel, *args)

    def _LoadFilterTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.columns = 4
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.cellPadding = (5, 2, 5, 2)
        tooltipPanel.margin = (0, 1, 0, 1)
        header = EveLabelSmall(text=localization.GetByLabel('UI/Inflight/Scanner/ShowResultsFor'), align=uiconst.CENTERLEFT, bold=True)
        tooltipPanel.AddCell(header, colSpan=tooltipPanel.columns, cellPadding=(7, 3, 5, 3))
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 0, 1, 0), opacity=0.4)
        tooltipPanel.AddCell(divider, cellPadding=0, colSpan=tooltipPanel.columns)
        tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=localization.GetByLabel('UI/Inflight/Scanner/AnomalySiteFilterLabel'), checked=settings.user.ui.Get('scannerShowAnomalies', True), func=self.OnShowAnomaliesCheckBoxChange, filterIndex=1)
        filterOptions = self.scanSvc.GetFilterOptions()
        activeFilters = self.scanSvc.GetActiveFilterSet()
        standardFilters = [ (filterName, filterID) for filterName, filterID in filterOptions if filterID < 0 ]
        for i, (filterName, filterID) in enumerate(standardFilters):
            if filterID < 0:
                tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=filterName, checked=filterID in activeFilters, retval=filterID, func=self.OnFilterCheckBoxChange, filterIndex=i + 2)

        customFilters = [ (filterName, filterID) for filterName, filterID in filterOptions if filterID > 0 ]
        if customFilters:
            divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 0, 1, 0), opacity=0.4)
            tooltipPanel.AddCell(divider, cellPadding=0, colSpan=tooltipPanel.columns)
            for filterName, filterID in customFilters:
                if filterID > 0:
                    tooltipPanel.AddRow(rowClass=ProbeTooltipCheckboxRow, text=filterName, checked=filterID in activeFilters, retval=filterID, func=self.OnFilterCheckBoxChange, deleteFunc=(self.DeleteFilter, (filterID,)), editFunc=(self.EditFilter, (filterID,)))

        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 0, 1, 0), opacity=0.4)
        tooltipPanel.AddCell(divider, cellPadding=0, colSpan=tooltipPanel.columns)
        buttonRow = tooltipPanel.AddRow(rowClass=ProbeTooltipButtonRow, text=localization.GetByLabel('UI/Inflight/Scanner/CreateNewFilter'), texturePath='res:/UI/Texture/Classes/ProbeScanner/saveformationProbesIcon.png', func=AddFilter)
        self.filteredBoxTooltip = weakref.ref(tooltipPanel)

    def ReloadFilteredBoxTooltip(self):
        if not self.filteredBoxTooltip or self.destroyed:
            return
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip is not None:
            self._LoadFilterTooltipPanel(filteredBoxTooltip)

    def LoadIgnoredTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.margin = 3
        resultsIgnored = self.scanSvc.GetIgnoredResultsDesc()
        if not resultsIgnored:
            return
        scroll = ScrollContainer(align=uiconst.TOPLEFT, parent=tooltipPanel)
        scroll.verticalScrollBar.align = uiconst.TORIGHT_NOPUSH
        scroll.verticalScrollBar.width = 3
        scroll.isTabStop = False
        subGrid = LayoutGrid(parent=scroll, align=uiconst.TOPLEFT, columns=4)
        rowOrder = []
        if len(resultsIgnored) > 1:
            row = subGrid.AddRow(rowClass=ProbeTooltipButtonRow, text=localization.GetByLabel('UI/Inflight/Scanner/ClearAllIgnoredResults'), texturePath='res:/UI/Texture/Classes/ProbeScanner/clearIgnoredMenu.png', func=self.ClearIgnoredResults, width=200)
            rowOrder.append(row)
        ids = sorted(resultsIgnored)
        for id, desc in ids:
            if desc:
                displayDesc = localization.GetByLabel('UI/Inflight/Scanner/ResultIdAndDesc', id=id, desc=desc)
            else:
                displayDesc = id
            row = subGrid.AddRow(rowClass=ProbeTooltipButtonRow, text=displayDesc, texturePath='res:/UI/Texture/Classes/ProbeScanner/clearIgnoredMenu.png', func=self.UnIgnoreResult, funcArgs=(id,), width=200)
            rowOrder.append(row)

        subGrid.RefreshGridLayout()
        scroll.width = subGrid.width + (5 if len(rowOrder) > 10 else 0)
        totalHeight = 0
        for row in rowOrder[:10]:
            totalHeight += row.height

        scroll.height = totalHeight
        tooltipPanel.state = uiconst.UI_NORMAL
        self.ignoredTooltip = weakref.ref(tooltipPanel)

    def ClearIgnoredResults(self, *args):
        self.scanSvc.ClearIgnoredResults()
        ignoredTooltip = self.ignoredTooltip()
        if ignoredTooltip is not None:
            self.LoadIgnoredTooltipPanel(ignoredTooltip)

    def UnIgnoreResult(self, resultID, *args):
        self.scanSvc.ShowIgnoredResult(resultID)
        ignoredTooltip = self.ignoredTooltip()
        if ignoredTooltip is not None:
            self.LoadIgnoredTooltipPanel(ignoredTooltip)

    def OnShowAnomaliesCheckBoxChange(self, settingKey, settingState, *args):
        settings.user.ui.Set('scannerShowAnomalies', settingState)
        if settingState:
            self.scanSvc.ShowAnomalies()
        else:
            self.scanSvc.StopShowingAnomalies()
        self.LoadResultList()

    def DeleteFilter(self, settingsKey):
        self.scanSvc.DeleteFilter(settingsKey)
        self.scanSvc.RemoveFromActiveFilterSet(settingsKey)
        uthread.new(self.ReloadFilteredBoxTooltip)

    def OnFilterCheckBoxChange(self, settingKey, settingState, *args):
        if settingState:
            self.scanSvc.AddToActiveFilterSet(settingKey)
        else:
            self.scanSvc.RemoveFromActiveFilterSet(settingKey)

    def ValidateProbesState(self, probeIDs, isEntryButton = False):
        probeData = self.scanSvc.GetProbeData()
        for probeID in probeIDs:
            if probeID in probeData:
                probe = probeData[probeID]
                if isEntryButton:
                    if probe.state not in (probeStateIdle, probeStateInactive):
                        return False
                elif probe.state != probeStateIdle:
                    return False

        return True

    def LoadCurrentSolarSystem(self):
        self.ReloadSolarSystem()
        self.LoadProbeList()
        self.LoadResultList()

    def OnNewScannerFilterSet(self, *args):
        self.LoadResultList()

    def OnProbeStateUpdated(self, probeID, state):
        self.sr.loadProbeList = AutoTimer(200, self.LoadProbeList)

    def OnProbePositionsUpdated(self):
        self.CheckButtonStates()

    def OnScannerDisconnected(self):
        self.LoadProbeList()
        self.LoadResultList()
        self.CheckButtonStates()

    def OnProbeRemoved(self, probeID):
        uthread.new(self._OnProbeRemove, probeID)

    def _OnProbeRemove(self, probeID):
        rm = []
        cnt = 0
        for entry in self.probesScroll.GetNodes():
            if entry.Get('probe', None) is None:
                continue
            if entry.probe.probeID == probeID:
                rm.append(entry)
            cnt += 1

        if rm:
            self.probesScroll.RemoveEntries(rm)
        if cnt <= 1:
            uthread.new(self.LoadProbeList)
        self.CheckButtonStates()

    def OnProbeAdded(self, probe):
        uthread.new(self.LoadProbeList)

    def LaunchFormation(self, formationID, size):
        self.scanSvc.MoveProbesToFormation(formationID)

    def EditFilter(self, filterID, *args):
        editor = ScannerFilterEditor.Open()
        editor.LoadData(filterID)

    def EditCurrentFilter(self, *args):
        activeFilter = self.scanSvc.GetActiveFilterID()
        editor = ScannerFilterEditor.Open()
        editor.LoadData(activeFilter)

    def DeleteCurrentFilter(self, *args):
        self.scanSvc.DeleteCurrentFilter()
        self.LoadResultList()

    def LoadResultList(self):
        if self.destroyed:
            return
        currentScan = self.scanSvc.GetCurrentScan()
        scanningProbes = self.scanSvc.GetScanningProbes()
        bp = sm.GetService('michelle').GetBallpark(doWait=True)
        if bp is None:
            return
        if not bp.ego:
            return
        ego = bp.balls[bp.ego]
        myPos = (ego.x, ego.y, ego.z)
        results, ignored, filtered, filteredAnomalies = self.scanSvc.GetResults(useFilterSet=True)
        columnWidths = self.sortHeaders.GetColumnWidths()
        resultList = []
        if currentScan and blue.os.TimeDiffInMs(currentScan.startTime, blue.os.GetSimTime()) < currentScan.duration:
            return
        if scanningProbes and session.shipid not in scanningProbes:
            return
        if results:
            for result in results:
                displayName = self.scanSvc.GetDisplayName(result)
                scanGroupName = self.scanSvc.GetScanGroupName(result)
                groupName = self.scanSvc.GetGroupName(result)
                typeName = self.scanSvc.GetTypeName(result)
                distance = result.GetDistance(myPos)
                sortValues = [distance,
                 result.id,
                 displayName,
                 groupName,
                 min(1.0, result.certainty)]
                data = KeyVal()
                data.sortValues = sortValues
                data.columnID = 'probeResultColumn'
                data.displayName = displayName
                data.scanGroupName = scanGroupName
                data.groupName = groupName
                data.typeName = typeName
                data.result = result
                data.GetMenu = self.ResultMenu
                data.distance = distance
                data.newResult = True
                data.columnWidths = columnWidths
                resultList.append(listentry.Get(decoClass=ScanResultNew, data=data))

        scrollPosition = self.resultScroll.GetScrollProportion()
        self.resultScroll.Clear()
        columns = ScanResultNew.GetColumns()
        activeColumn, columnDirection = self.sortHeaders.GetActiveColumnAndDirection()
        activeColumnIndex = columns.index(activeColumn)

        def GetSortValue(_node):
            return _node.sortValues[activeColumnIndex]

        sortedScrollNodes = sorted(resultList, key=GetSortValue, reverse=not columnDirection)
        self.resultScroll.AddNodes(0, sortedScrollNodes)
        if scrollPosition:
            self.resultScroll.ScrollToProportion(scrollPosition)
        if sortedScrollNodes:
            self.resultScroll.ShowHint()
            self.sortHeaders.Show()
        else:
            self.resultScroll.ShowHint(localization.GetByLabel('UI/Inflight/Scanner/NoScanResult'))
            self.sortHeaders.Hide()
        self.ShowFilteredAndIgnored(filtered, ignored, filteredAnomalies)
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            probeHandler.SetResultFilter([], update=True)

    def GetProbeEntry(self, probe, selectedIDs = None):
        from eve.client.script.ui.inflight.scannerListEntries import ScanProbeEntryNew
        selectedIDs = selectedIDs or []
        data = KeyVal()
        data.probe = probe
        data.probeID = probe.probeID
        data.isSelected = probe.probeID in selectedIDs
        data.GetMenu = self.GetProbeMenu
        data.scanRangeSteps = self.scanSvc.GetScanRangeStepsByTypeID(probe.typeID)
        entry = listentry.Get(decoClass=ScanProbeEntryNew, data=data)
        return entry

    def LoadProbeList(self):
        selectedIDs = self.GetSelectedProbes(asIds=1)
        scrolllist = []
        for probeID, probe in self.scanSvc.GetProbeData().items():
            if evetypes.GetGroupID(probe.typeID) in self.__disallowanalysisgroups:
                continue
            entry = self.GetProbeEntry(probe, selectedIDs)
            scrolllist.append(entry)

        if not scrolllist:
            scrolllist.append(listentry.Get(decoClass=NoScanProbesEntry))
        self.probesScroll.Load(contentList=scrolllist)
        self.CheckButtonStates()
        self.sr.loadProbeList = None

    def CheckButtonStates(self):
        if self.destroyed:
            return
        hasProbes = self.scanSvc.HasAvailableProbes()
        scanningProbes = self.scanSvc.GetScanningProbes()
        if scanningProbes:
            self.analyzeButton.Disable()
            self.analyzeButton.AnimateArrows()
        elif hasProbes:
            self.analyzeButton.Enable()
            self.analyzeButton.StopAnimateArrows()
        else:
            self.analyzeButton.Disable()
            self.analyzeButton.StopAnimateArrows()
        canClaim = self.scanSvc.CanClaimProbes()
        if canClaim:
            self.reconnectButton.Enable()
        else:
            self.reconnectButton.Disable()
        probes = self.scanSvc.GetActiveProbes()
        allIdle = self.ValidateProbesState(probes)
        if probes and allIdle:
            self.recoverButton.Enable()
        else:
            self.recoverButton.Disable()
        for formationID, button in self.formationButtonsByID.iteritems():
            try:
                canLaunch = self.scanSvc.CanLaunchFormation(formationID)
            except KeyError:
                continue

            if canLaunch:
                button.Enable()
            else:
                button.Disable()

        self.customFormationButton.UpdateButton()
        self.buttonRefreshTimer = AutoTimer(1000, self.CheckButtonStates)

    def GetProbeMenu(self, entry, *args):
        probeIDs = self.GetSelectedProbes(asIds=1)
        return self.scanSvc.GetProbeMenu(entry.sr.node.probeID, probeIDs)

    def GetProbeHandler(self):
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            solarSystemHandler = solarSystemView.mapView.currentSolarsystem
            if solarSystemHandler and solarSystemHandler.solarsystemID == session.solarsystemid2:
                return solarSystemHandler.probeHandler

    @UserErrorIfScanning
    def ReconnectToLostProbes(self, *args):
        self.scanSvc.ReconnectToLostProbes()
        self.LoadProbeList()

    @UserErrorIfScanning
    def RecoverActiveProbes(self, *args):
        probes = self.scanSvc.GetActiveProbes()
        self.scanSvc.RecoverProbes(probes)

    @UserErrorIfScanning
    def DestroyActiveProbes(self, *args):
        probeIDs = self.scanSvc.GetActiveProbes()
        if probeIDs:
            allIdle = True
            probeData = self.scanSvc.GetProbeData()
            for probeID in probeIDs:
                if probeID in probeData:
                    probe = probeData[probeID]
                    if probe.state != probeStateIdle:
                        allIdle = False

            if allIdle and eve.Message('DestroyProbes', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
                for _probeID in probeIDs:
                    self.scanSvc.DestroyProbe(_probeID)

    def GetSelectedProbes(self, asIds = 0):
        selected = self.probesScroll.GetSelected()
        returnVal = []
        for each in selected:
            if each.Get('probe', None) is not None:
                if asIds:
                    returnVal.append(each.probe.probeID)
                else:
                    returnVal.append(each)

        return returnVal

    @UserErrorIfScanning
    def Analyze(self, *args):
        self.analyzeButton.Disable()
        self.analyzeButton.AnimateArrows()
        try:
            self.scanSvc.RequestScans()
        except UserError as e:
            self.CheckButtonStates()
            raise e

        self.LoadResultList()

    def Confirm(self, *args):
        if not self.analyzeButton.disabled:
            uthread.new(self.Analyze)

    def ResultMenu(self, panel, *args):
        result = panel.sr.node.result
        menu = []
        siteData = SiteDataFromScanResult(result)
        menu.extend(self.scanSvc.GetScanResultMenuWithoutIgnore(siteData))
        nodes = self.resultScroll.GetSelected() or [panel.sr.node]
        idList = []
        nonAnomalyIdList = []
        for node in nodes:
            if hasattr(node.result, 'id'):
                idList.append(node.result.id)
                if node.result.scanGroupID != probeScanGroupAnomalies:
                    nonAnomalyIdList.append(node.result.id)

        menu.append((MenuLabel('UI/Inflight/Scanner/IngoreResult'), self.scanSvc.IgnoreResult, idList))
        menu.append((MenuLabel('UI/Inflight/Scanner/IgnoreOtherResults'), self.scanSvc.IgnoreOtherResults, idList))
        if len(nonAnomalyIdList) > 0:
            menu.append((MenuLabel('UI/Inflight/Scanner/ClearResult'), self.scanSvc.ClearResults, nonAnomalyIdList))
        return menu

    def OnSelectionChange(self, entries):
        selectedNodes = self.resultScroll.GetSelected()
        showResults = []
        if selectedNodes:
            for entry in self.resultScroll.GetNodes():
                if entry.result and entry in selectedNodes:
                    showResults.append(entry.result.id)

        probeHandler = self.GetProbeHandler()
        if probeHandler:
            probeHandler.SetResultFilter(showResults, update=True)

    def Refresh(self):
        self.refreshTimer = AutoTimer(200, self.DoRefresh)

    def DoRefresh(self):
        self.refreshTimer = None
        if self.destroyed:
            return
        self.CheckButtonStates()
        self.LoadProbeList()
        self.LoadResultList()

    def OnRefreshScanResults(self):
        self.Refresh()

    def OnBallparkSetState(self):
        self.Refresh()

    def ShowFilteredAndIgnored(self, filtered, ignored, filteredAnomalies):
        self.filteredBox.SetText(localization.GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=filtered + filteredAnomalies))
        self.ignoredBox.UpdateIgnoredAmount(ignored)

    def OnReconnectToProbesAvailable(self):
        self.CheckButtonStates()
