#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerFiles\directionalScannerWindow.py
import math
import weakref
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.mathUtil import DegToRad
import carbonui.const as uiconst
from carbonui.control.editPlainText import EditPlainTextCore
from carbonui.control.scrollentries import ScrollEntryNode
from carbonui.control.singlelineedit import SinglelineEditCore
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive, GetBallPosition, GetBall
from eve.client.script.ui.control.primaryButton import PrimaryButton
from eve.client.script.ui.control.themeColored import FillThemeColored, LineThemeColored
from eve.client.script.ui.control.tooltips import ShortcutHint
from eve.client.script.ui.inflight.scannerFiles.scannerToolsUIComponents import FilterBox, ProbeTooltipCheckboxRow
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelHeaderBackground
from eve.client.script.ui.shared.mapView.mapViewSettings import MapViewCheckbox
import evetypes
import uthread
import blue
import service
import state
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.buttons import Button, BigButton, ToggleButtonGroup
from eve.client.script.ui.control.eveLabel import EveLabelSmall, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
import geo2
from localization import GetByLabel
from eve.client.script.ui.shared.maps.browserwindow import MapBrowserWnd
from utillib import KeyVal

def ConvertKmToAu(kmValue):
    auValue = kmValue * 1000 / const.AU
    return auValue


def ConvertAuToKm(auValue):
    kmValue = int(auValue * const.AU / 1000)
    return kmValue


MIN_WINDOW_WIDTH = 320
MIN_WINDOW_HEIGHT = 200
RANGEMODE_AU = 1
RANGEMODE_KM = 2
MIN_RANGE_KM = 10
MIN_RANGE_AU = ConvertKmToAu(MIN_RANGE_KM)
MAX_RANGE_AU = 14.3
MAX_RANGE_KM = ConvertAuToKm(MAX_RANGE_AU)

class DirectionalScanner(Window):
    __notifyevents__ = ['OnOverviewPresetSaved', 'OnBallparkSetState']
    default_windowID = 'directionalScannerWindow'
    default_width = 400
    default_height = 350
    default_minSize = (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    default_captionLabelPath = 'UI/Inflight/Scanner/DirectionalScan'
    dScanDirty = False
    filteredBoxTooltip = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        scanOnOpen = attributes.Get('scanOnOpen', True)
        self.scanSvc = sm.GetService('scanSvc')
        self.busy = False
        self.scanresult = []
        self.scanangle = DegToRad(90)
        self.rangeEditMode = settings.user.ui.Get('scanner_rangeEditMode', RANGEMODE_AU)
        self.hasAnalyzeExecutedDuringKeyPress = None
        self.scope = 'inflight'
        self.SetTopparentHeight(0)
        self.SetWndIcon(None)
        self.HideMainIcon()
        content = Container(name='content', parent=self.GetMainArea(), align=uiconst.TOALL, padding=const.defaultPadding)
        self.SetupDScanUI(content)
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            solarSystemView.StartDirectionalScanHandler()
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyUpCallback)
        if scanOnOpen:
            self.Analyze()

    def OnCmdDirectionalScanUnload(self, cmdWasExecuted):
        if not cmdWasExecuted:
            self.Analyze()
        self.hasAnalyzeExecutedDuringKeyPress = None

    def OnCmdDirectionalScanLoad(self):
        self.hasAnalyzeExecutedDuringKeyPress = False

    def Close(self, *args, **kwds):
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            solarSystemView.StopDirectionalScanHandler()
        self.SetMapAngle(0)
        Window.Close(self, *args, **kwds)

    def Confirm(self, *args):
        if not self.analyzeButton.disabled:
            self.Analyze()

    def OnGlobalKeyUpCallback(self, wnd, eventID, (vkey, flag), *args):
        if self.destroyed:
            return False
        localShortCuts = [uiconst.VK_1,
         uiconst.VK_2,
         uiconst.VK_3,
         uiconst.VK_4,
         uiconst.VK_5,
         uiconst.VK_6,
         uiconst.VK_7,
         uiconst.VK_8,
         uiconst.VK_9,
         uiconst.VK_0]
        if vkey not in localShortCuts:
            return True
        focus = uicore.registry.GetFocus()
        editFieldHasFocus = focus and isinstance(focus, (SinglelineEditCore, EditPlainTextCore))
        if editFieldHasFocus:
            return True
        activeToplevel = uicore.registry.GetActive()
        if activeToplevel is not self:
            return True
        shortCutIndex = localShortCuts.index(vkey)
        presetOptions = self.GetPresetOptions()
        try:
            filterName, filterID = presetOptions[shortCutIndex]
            uthread.new(self.OnFilterChange, filterID, True)
        except IndexError:
            pass

        return True

    def ToggleSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if not SolarSystemViewPanel.ClosePanel():
            SolarSystemViewPanel.OpenPanel()

    def GetSolarSystemView(self):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        solarSystemView = SolarSystemViewPanel.GetPanel()
        if solarSystemView and not solarSystemView.destroyed:
            return solarSystemView

    def GetDirectionalScanHandler(self):
        solarSystemView = self.GetSolarSystemView()
        if solarSystemView:
            return solarSystemView.GetDirectionalScanHandler()

    def SetupDScanUI(self, directionBox):
        self.analyzeButton = AnalyzeButton(label=GetByLabel('UI/Inflight/Scanner/Scan'), func=self.OnAnalyzeButton, parent=directionBox)
        mapButton = BigButton(parent=directionBox, width=32, height=32, hint=GetByLabel('UI/Map/MapPallet/btnSolarsystemMap'), align=uiconst.TOPRIGHT)
        mapButton.Startup(32, 32)
        mapButton.sr.icon.SetTexturePath('res:/UI/Texture/classes/ProbeScanner/solarsystemMapButton.png')
        mapButton.OnClick = self.ToggleSolarSystemView
        rangeText = GetByLabel('UI/Inflight/Scanner/Range')
        rangeLabel = EveLabelSmall(text=rangeText, parent=directionBox, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, left=self.analyzeButton.width + 6)
        flowContainer = FlowContainer(parent=directionBox, padding=(rangeLabel.left + rangeLabel.width + 6,
         0,
         mapButton.width + 2,
         0), align=uiconst.TOTOP, contentSpacing=(4, 2))
        startingKmValue = settings.user.ui.Get('dir_scanrange', const.AU * MAX_RANGE_AU)
        startingAuValue = ConvertKmToAu(startingKmValue)
        self.distanceSlider = Slider(name='distanceSlider', parent=flowContainer, sliderID='distanceSlider', minValue=0, maxValue=MAX_RANGE_AU, endsliderfunc=self.EndSetDistanceSliderValue, onsetvaluefunc=self.OnSetDistanceSliderValue, increments=[MIN_RANGE_AU,
         1,
         5,
         10,
         MAX_RANGE_AU], width=90, align=uiconst.NOALIGN, barHeight=10)
        self.distanceSlider.label.display = False
        self.distanceSlider.SetValue(startingAuValue, updateHandle=True, useIncrements=False)
        subGrid = LayoutGrid(columns=2, align=uiconst.NOALIGN)
        maxAuRangeInKm = ConvertAuToKm(MAX_RANGE_AU)
        self.dir_rangeinput = SinglelineEdit(name='dir_rangeinput', parent=subGrid, align=uiconst.CENTERLEFT, width=90, top=0, maxLength=len(str(maxAuRangeInKm)) + 1, OnReturn=self.OnAnalyzeButton)
        self.unitToggleButton = Button(parent=subGrid, align=uiconst.CENTERLEFT, func=self.ToggleRangeUnits, left=4)
        flowContainer.children.append(subGrid)
        startingKmValue = settings.user.ui.Get('dir_scanrange', const.AU * MAX_RANGE_AU)
        startingKmValue = min(MAX_RANGE_KM, max(MIN_RANGE_KM, startingKmValue))
        self.scanRangeKM = startingKmValue
        self.UpdateRangeInput(startingKmValue)
        self.dir_rangeinput.OnChar = self.OnCharRangeInput
        self.dir_rangeinput.OnMouseWheel = self.OnMouseWheelRangeInput
        self.dir_rangeinput.ChangeNumericValue = self.ChangeNumericValueRangeInput
        flowContainer2 = FlowContainer(parent=directionBox, padding=(self.analyzeButton.width + 6,
         0,
         mapButton.width + 2,
         0), align=uiconst.TOTOP, contentSpacing=(4, 2))
        angleLabelParent = Container(parent=flowContainer2, align=uiconst.NOALIGN, width=32, height=20)
        angleText = GetByLabel('UI/Inflight/Scanner/Angle')
        angleLabel = EveLabelSmall(text=angleText, parent=angleLabelParent, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        startingAngle = settings.user.ui.Get('scan_angleSlider', 360)
        startingAngle = max(0, min(startingAngle, 360))
        self.scanangle = DegToRad(startingAngle)
        subGrid = LayoutGrid(parent=flowContainer2, columns=2, align=uiconst.NOALIGN)
        angleSlider = Slider(name='angleSlider', parent=subGrid, sliderID='angleSlider', startVal=startingAngle, minValue=5, maxValue=360, increments=[5,
         15,
         30,
         60,
         90,
         180,
         360], isEvenIncrementsSlider=True, endsliderfunc=self.EndSetAngleSliderValue, setlabelfunc=self.UpdateAngleSliderLabel, width=90, height=20, align=uiconst.CENTERLEFT, barHeight=10)
        self.angleSliderLabel = EveLabelSmall(text=GetByLabel('UI/Inflight/Scanner/AngleDegrees', value=startingAngle), parent=subGrid, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=4)
        rangeLabel.width = angleLabel.width = max(rangeLabel.width, angleLabel.width)
        flowContainer.padLeft = rangeLabel.left + rangeLabel.width + 6
        angleLabelParent.width = rangeLabel.width + 2
        self.headerParent = Container(parent=directionBox, name='headerParent', align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, height=24)
        FillThemeColored(bgParent=self.headerParent, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
        InfoPanelHeaderBackground(bgParent=self.headerParent)
        self.headerLabel = EveLabelMedium(text=GetByLabel('UI/Inflight/Scanner/ScanResults'), parent=self.headerParent, bold=True, state=uiconst.UI_DISABLED, left=7, align=uiconst.CENTERLEFT)
        self.headerParent.height = max(20, self.headerLabel.textheight + 2)
        self.sr.dirscroll = Scroll(name='dirscroll', parent=directionBox)
        self.sr.dirscroll.sr.id = 'scanner_dirscroll'
        self.sr.dirscroll.OnChar = None
        self.filteredBox = FilterBox(parent=self.headerParent, text='-', state=uiconst.UI_NORMAL, align=uiconst.CENTERRIGHT)
        self.filteredBox.LoadTooltipPanel = self.LoadFilterTooltipPanel

    def LoadFilterTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.Flush()
        tooltipPanel.columns = 1
        tooltipPanel.cellPadding = 2
        tooltipPanel.state = uiconst.UI_NORMAL
        header = EveLabelSmall(text=GetByLabel('UI/Inflight/Scanner/ShowResultsFor'), align=uiconst.CENTERLEFT, bold=True)
        tooltipPanel.AddCell(header, colSpan=tooltipPanel.columns, cellPadding=(7, 3, 5, 3))
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 0, 1, 0), opacity=0.4)
        tooltipPanel.AddCell(divider, cellPadding=0, colSpan=tooltipPanel.columns)
        tooltipPanel.scroll = Scroll(parent=tooltipPanel, align=uiconst.TOPLEFT, width=200, height=200)
        tooltipPanel.scroll.OnUpdatePosition = self.OnScrollPositionChanged
        self.filteredBoxTooltip = weakref.ref(tooltipPanel)
        self.LoadFilters()

    def LoadFilters(self):
        filteredBoxTooltip = self.filteredBoxTooltip()
        if not filteredBoxTooltip:
            return
        scrollPosition = settings.char.ui.Get('directionalScanFilterPos', 0.0)
        presetSelected = settings.user.ui.Get('scanner_presetInUse', None)
        presetOptions = self.GetPresetOptions()
        scrollEntries = []
        for i, (filterName, filterID) in enumerate(presetOptions):
            if i < 10:
                filterIndex = (i + 1) % 10
            else:
                filterIndex = None
            scrollNode = ScrollEntryNode(label=filterName, checked=filterID == presetSelected, cfgname=filterID, OnChange=self.OnFilterCheckBoxChange, entryWidth=190, decoClass=FilterOptionEntry, filterIndex=filterIndex)
            scrollEntries.append(scrollNode)

        filteredBoxTooltip.scroll.Load(contentList=scrollEntries, scrollTo=scrollPosition)
        filteredBoxTooltip.scroll.height = min(200, filteredBoxTooltip.scroll.GetContentHeight() + 2)

    def OnScrollPositionChanged(self, *args, **kwargs):
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip:
            settings.char.ui.Set('directionalScanFilterPos', filteredBoxTooltip.scroll.GetScrollProportion())

    def OnFilterCheckBoxChange(self, checkbox, *args):
        settingKey = checkbox.data['key']
        self.OnFilterChange(settingKey, True)

    def OnFilterChange(self, settingKey, settingState, *args):
        settings.user.ui.Set('scanner_presetInUse', settingKey)
        if self.scanresult:
            uthread.new(self.ShowDirectionalSearchResult)
        else:
            self.Analyze()
        self.ReloadFilteredBoxTooltip()

    def ReloadFilteredBoxTooltip(self):
        if not self.filteredBoxTooltip or self.destroyed:
            return
        filteredBoxTooltip = self.filteredBoxTooltip()
        if filteredBoxTooltip is not None:
            self.LoadFilters()

    def UpdateRangeInput(self, scanRangeKM):
        if self.rangeEditMode == RANGEMODE_AU:
            scanRangeAU = ConvertKmToAu(scanRangeKM)
            self.dir_rangeinput.FloatMode(minfloat=MIN_RANGE_AU, maxfloat=MAX_RANGE_AU, digits=1)
            self.dir_rangeinput.SetValue(scanRangeAU)
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitAU'))
        else:
            self.dir_rangeinput.IntMode(minint=ConvertAuToKm(MIN_RANGE_AU), maxint=ConvertAuToKm(MAX_RANGE_AU))
            self.dir_rangeinput.SetValue(scanRangeKM)
            self.unitToggleButton.SetLabel(GetByLabel('UI/Inflight/Scanner/UnitKm'))

    def ToggleRangeUnits(self, *args):
        if self.rangeEditMode == RANGEMODE_AU:
            self.rangeEditMode = RANGEMODE_KM
        else:
            self.rangeEditMode = RANGEMODE_AU
        settings.user.ui.Set('scanner_rangeEditMode', self.rangeEditMode)
        self.UpdateRangeInput(self.scanRangeKM)

    def GetPresetOptions(self):
        p = sm.GetService('overviewPresetSvc').GetAllPresets().keys()
        options = []
        for name in p:
            defaultName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(name)
            if defaultName:
                options.append((' ' + defaultName.lower(), (defaultName, name)))
            else:
                displayName = sm.GetService('overviewPresetSvc').GetPresetDisplayName(name)
                options.append((displayName.lower(), (displayName, name)))

        options = SortListOfTuples(options)
        options.insert(0, (GetByLabel('UI/Inflight/Scanner/UseActiveOverviewSettings'), None))
        return options

    def ScanTowardsItem(self, itemID, mapPosition = None):
        if self.busy:
            return
        ball = GetBall(itemID)
        if not ball:
            return
        uthread.new(self._Analyze, GetBallPosition(ball))
        directionalScanHandler = self.GetDirectionalScanHandler()
        if directionalScanHandler:
            directionalScanHandler.SetScanTarget(itemID, mapPosition)
        else:
            camera = sm.GetService('sceneManager').GetActiveSpaceCamera()
            camera.Track(itemID)

    def OnScanConeAligned(self):
        self.Analyze()

    def OnBallparkSetState(self):
        if not self.destroyed:
            self.Analyze()

    def OnOverviewPresetSaved(self):
        uthread.new(self.ShowDirectionalSearchResult)

    def UpdateAngleSliderLabel(self, label, sliderID, displayName, value):
        if getattr(self, 'angleSliderLabel', None):
            self.angleSliderLabel.text = GetByLabel('UI/Inflight/Scanner/AngleDegrees', value=value)

    def OnCharRangeInput(self, char, flag):
        returnValue = SinglelineEdit.OnChar(self.dir_rangeinput, char, flag)
        self.OnScanRangeValueChanged()
        return returnValue

    def OnMouseWheelRangeInput(self, *args):
        SinglelineEdit.MouseWheel(self.dir_rangeinput, *args)
        self.OnScanRangeValueChanged()

    def ChangeNumericValueRangeInput(self, *args):
        SinglelineEdit.ChangeNumericValue(self.dir_rangeinput, *args)
        self.OnScanRangeValueChanged()

    def OnScanRangeValueChanged(self):
        scanRange = self.dir_rangeinput.GetValue()
        if self.rangeEditMode == RANGEMODE_KM:
            scanRangeAU = ConvertKmToAu(scanRange)
            self.scanRangeKM = scanRange
        else:
            scanRangeAU = scanRange
            self.scanRangeKM = max(MIN_RANGE_KM, ConvertAuToKm(scanRange))
        self.distanceSlider.SetValue(scanRangeAU, updateHandle=True, useIncrements=False)
        sm.ScatterEvent('OnDirectionalScannerRangeChanged', self.scanRangeKM * 1000)
        self.Analyze()

    def UpdateDistanceFromSlider(self):
        scanRangeAU = self.distanceSlider.GetValue()
        kmValue = ConvertAuToKm(scanRangeAU)
        if self.rangeEditMode == RANGEMODE_KM:
            self.dir_rangeinput.SetValue(kmValue)
        else:
            self.dir_rangeinput.SetValue(scanRangeAU)

    def EndSetDistanceSliderValue(self, *args):
        self.UpdateDistanceFromSlider()
        scanRange = self.dir_rangeinput.GetValue()
        if self.rangeEditMode == RANGEMODE_AU:
            scanRange = ConvertAuToKm(scanRange)
        self.scanRangeKM = max(MIN_RANGE_KM, scanRange)
        sm.ScatterEvent('OnDirectionalScannerRangeChanged', self.scanRangeKM * 1000)
        self.Analyze()

    def OnSetDistanceSliderValue(self, slider, *args):
        if not slider.dragging:
            return
        self.UpdateDistanceFromSlider()

    def EndSetAngleSliderValue(self, slider):
        angleValue = slider.GetValue()
        self.SetMapAngle(DegToRad(angleValue))
        settings.user.ui.Set('scan_angleSlider', angleValue)
        sm.ScatterEvent('OnDirectionalScannerAngleChanged', self.scanangle)
        self.Analyze()

    def OnAnalyzeButton(self, *args):
        self.Analyze()

    def Analyze(self, direction = None):
        uthread.new(self._Analyze, direction)

    def _Analyze(self, direction = None, *args):
        if self.hasAnalyzeExecutedDuringKeyPress is not None:
            self.hasAnalyzeExecutedDuringKeyPress = True
        if self.destroyed:
            return
        if self.busy:
            self.dScanDirty = True
            return
        self.busy = True
        self.analyzeButton.AnimateArrows()
        self.analyzeButton.Disable()
        try:
            self._DirectionSearch(direction)
        finally:
            self.analyzeButton.StopAnimateArrows()
            self.busy = False
            self.analyzeButton.Enable()

        if self.dScanDirty:
            self.dScanDirty = False
            self.Analyze()

    def _DirectionSearch(self, direction = None, *args, **kwds):
        self.scanresult = []
        spaceCamera = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if not spaceCamera:
            return
        updateStartTime = blue.os.GetWallclockTimeNow()
        if not direction:
            direction = self.GetScanDirection(spaceCamera)
        settings.user.ui.Set('dir_scanrange', self.scanRangeKM)
        try:
            result = self.scanSvc.ConeScan(self.scanangle, (self.scanRangeKM * 1000), *direction)
        except (UserError, RuntimeError) as err:
            raise err

        directionalScanHandler = self.GetDirectionalScanHandler()
        if directionalScanHandler:
            directionalScanHandler.ScanEffect()
        self.scanresult = result
        self.ShowDirectionalSearchResult()
        diff = blue.os.TimeDiffInMs(updateStartTime, blue.os.GetWallclockTimeNow())
        sleep = max(1, 1500 - diff)
        blue.pyos.synchro.SleepWallclock(sleep)

    def GetScanDirection(self, spaceCamera):
        if IsNewCameraActive():
            direction = spaceCamera.GetViewVector()
        else:
            spaceCameraRotation = geo2.QuaternionRotationSetYawPitchRoll(spaceCamera.yaw, spaceCamera.pitch, 0.0)
            direction = geo2.QuaternionTransformVector(spaceCameraRotation, (0, 0, 1))
        direction = geo2.Vec3Negate(direction)
        return direction

    def ShowDirectionalSearchResult(self, *args):
        selectedValue = settings.user.ui.Get('scanner_presetInUse', None)
        if selectedValue is None:
            selectedValue = sm.GetService('overviewPresetSvc').GetActiveOverviewPresetName()
        filters = sm.GetService('overviewPresetSvc').GetValidGroups(presetName=selectedValue)
        ballpark = sm.GetService('michelle').GetBallpark()
        filtered = 0
        scrolllist = []
        if self.scanresult and ballpark:
            scanresult = self.scanresult[:]
            prime = []
            for celestialRec in scanresult:
                if celestialRec.id not in ballpark.balls:
                    prime.append(celestialRec.id)

            if prime:
                cfg.evelocations.Prime(prime)
            for celestialRec in scanresult:
                if self.destroyed:
                    return
                if celestialRec.groupID not in filters:
                    filtered += 1
                    continue
                typeName = evetypes.GetName(celestialRec.typeID)
                if evetypes.GetGroupID(celestialRec.typeID) == const.groupHarvestableCloud:
                    entryname = GetByLabel('UI/Inventory/SlimItemNames/SlimHarvestableCloud', typeName)
                elif evetypes.GetCategoryID(celestialRec.typeID) == const.categoryAsteroid:
                    entryname = GetByLabel('UI/Inventory/SlimItemNames/SlimAsteroid', typeName)
                else:
                    entryname = cfg.evelocations.Get(celestialRec.id).name
                if not entryname:
                    entryname = typeName
                itemID = celestialRec.id
                typeID = celestialRec.typeID
                ball = ballpark.GetBall(celestialRec.id)
                if ball is not None:
                    dist = ball.surfaceDist
                    diststr = FmtDist(dist, maxdemicals=1)
                else:
                    dist = 0
                    diststr = '-'
                groupID = evetypes.GetGroupID(typeID)
                if not eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
                    if groupID == const.groupCloud:
                        continue
                data = KeyVal()
                data.label = '%s<t>%s<t>%s' % (entryname, typeName, diststr)
                data.entryName = entryname
                data.typeName = typeName
                data.Set('sort_%s' % GetByLabel('UI/Common/Distance'), dist)
                data.columnID = 'directionalResultGroupColumn'
                data.itemID = itemID
                data.typeID = typeID
                data.GetMenu = self.DirectionalResultMenu
                scrolllist.append(listentry.Get(decoClass=DirectionalScanResults, data=data))
                blue.pyos.BeNice()

        filteredText = GetByLabel('UI/Inflight/Scanner/Filtered', noFiltered=filtered)
        activeFilterName = sm.GetService('overviewPresetSvc').GetDefaultOverviewName(selectedValue)
        self.filteredBox.SetText('%s (%s)' % (filteredText, activeFilterName))
        if not len(scrolllist):
            data = KeyVal()
            data.label = GetByLabel('UI/Inflight/Scanner/DirectionalNoResult')
            data.hideLines = 1
            scrolllist.append(listentry.Get('Generic', data=data))
            headers = []
        else:
            headers = [GetByLabel('UI/Common/Name'), GetByLabel('UI/Common/Type'), GetByLabel('UI/Common/Distance')]
        self.sr.dirscroll.Load(contentList=scrolllist, headers=headers)

    def DirectionalResultMenu(self, entry, *args):
        if entry.sr.node.itemID:
            return sm.GetService('menu').CelestialMenu(entry.sr.node.itemID, typeID=entry.sr.node.typeID)
        return []

    def SetMapAngle(self, angle):
        if angle is not None:
            self.scanangle = angle
        wnd = MapBrowserWnd.GetIfOpen()
        if wnd:
            wnd.SetTempAngle(angle)

    def EndSetSliderValue(self, *args):
        self.Analyze()


class DirectionalScanResults(listentry.Generic):
    __guid__ = 'listentry.DirectionalScanResults'
    isDragObject = True

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)


class FilterOptionEntry(MapViewCheckbox):

    def Startup(self, *args):
        MapViewCheckbox.Startup(self, *args)
        if self.sr.node.filterIndex is not None:
            shortcutObj = ShortcutHint(parent=self, text=str(self.sr.node.filterIndex), left=2, top=2)
            self.TEXTRIGHT = shortcutObj.width + 4


class AnalyzeButton(PrimaryButton):

    def StopAnimateArrows(self):
        PrimaryButton.StopAnimateArrows(self)
        uicore.animations.BlinkIn(self.underlay, loops=2)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        cmd = uicore.cmd.commandMap.GetCommandByName('CmdRefreshDirectionalScan')
        tooltipPanel.AddCommandTooltip(cmd)
