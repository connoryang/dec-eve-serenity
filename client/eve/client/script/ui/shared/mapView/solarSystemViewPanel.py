#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\solarSystemViewPanel.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.inflight.probeScannerWindow import ProbeScannerWindow
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import SCANMODE_CAMERA, GetActiveScanMode, ToggleScanMode, GetScanConeDisplayState, SetScanConeDisplayState
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.shared.mapView.dockPanelConst import DOCKPANELID_SOLARSYSTEMMAP
from eve.client.script.ui.shared.mapView.mapViewConst import MAPVIEW_SOLARSYSTEM_ID
from eve.client.script.ui.shared.mapView.mapViewScannerNavigationStandalone import MapViewScannerNavigation
from eve.client.script.ui.shared.mapView.mapViewSolarSystem import MapViewSolarSystem
import carbonui.const as uiconst
from eve.common.script.sys.idCheckers import IsSolarSystem
import localization
import uthread

class SolarSystemViewPanel(DockablePanel):
    __notifyevents__ = ['OnBallparkSetState',
     'OnTacticalOverlayChange',
     'OnSessionChanged',
     'OnSetCameraOffset',
     'OnHideUI',
     'OnShowUI']
    default_captionLabelPath = None
    default_caption = None
    default_windowID = DOCKPANELID_SOLARSYSTEMMAP
    default_iconNum = 'res:/UI/Texture/classes/ProbeScanner/solarsystemMapButton.png'
    panelID = default_windowID
    mapView = None
    overlayTools = None
    mapViewID = MAPVIEW_SOLARSYSTEM_ID

    def ApplyAttributes(self, attributes):
        DockablePanel.ApplyAttributes(self, attributes)
        self.showRangeIndicator = sm.GetService('tactical').IsTacticalOverlayActive()
        self.mapView = MapViewSolarSystem(parent=self.GetMainArea(), showInfobox=False, navigationPadding=(0, 0, 0, 0), navigationClass=MapViewScannerNavigation, mapViewID=self.mapViewID, showSolarSystemNebula=False, showStarfield=False, showDebugInfo=False, sceneBlendMode=None, stackMarkers=True)
        sceneOptionsContainer = Container(parent=self.toolbarContainer, align=uiconst.CENTERLEFT, width=100, height=32, left=4, idx=0)
        from eve.client.script.ui.shared.mapView.mapViewSettings import MapViewMarkersSettingButton
        self.markersSettingButton = MapViewMarkersSettingButton(parent=sceneOptionsContainer, callback=self.OnMarkersSettingChanged, mapViewID=self.mapViewID, align=uiconst.TOPLEFT, left=2, top=2)
        focusSelf = ButtonIcon(parent=sceneOptionsContainer, pos=(26, 2, 26, 26), iconSize=16, func=self.OnFocusSelf, hint=localization.GetByLabel('UI/Map/FocusCurrentLocation'), texturePath='res:/UI/Texture/classes/MapView/focusIcon.png', align=uiconst.TOPLEFT)
        focusSelf.tooltipPointer = uiconst.POINT_TOP_1
        self.dScanOptions = ButtonIcon(parent=sceneOptionsContainer, pos=(50, 2, 26, 26), iconSize=16, texturePath='res:/UI/Texture/classes/MapView/dScanIcon.png', align=uiconst.TOPLEFT)
        self.dScanOptions.tooltipPointer = uiconst.POINT_TOP_1
        self.dScanOptions.LoadTooltipPanel = self.LoadDScanTooltipPanel
        uthread.new(self.LoadSolarSystem)
        if uicore.cmd.IsUIHidden():
            self.OnHideUI()

    def OnShowUI(self):
        self.toolbarContainer.display = True

    def OnHideUI(self):
        if self.IsFullscreen():
            self.toolbarContainer.display = False

    def StartDirectionalScanHandler(self):
        self.mapView.currentSolarsystem.EnableDirectionalScanHandler()
        self.dScanOptions.Enable()

    def StopDirectionalScanHandler(self):
        self.mapView.currentSolarsystem.StopDirectionalScanHandler()
        self.dScanOptions.Disable()

    def GetDirectionalScanHandler(self):
        return self.mapView.currentSolarsystem.directionalScanHandler

    def StartProbeHandler(self):
        self.mapView.currentSolarsystem.EnableProbeHandlerStandalone()

    def StopProbeHandler(self):
        self.mapView.currentSolarsystem.StopProbeHandler()

    def OnFocusSelf(self, *args, **kwds):
        self.mapView.FocusSelf()

    def OnMarkersSettingChanged(self, *args, **kwds):
        self.mapView.OnMapViewSettingChanged(*args, **kwds)

    def OnDockModeChanged(self, *args):
        pass

    def OnTacticalOverlayChange(self):
        visible = sm.GetService('tactical').IsTacticalOverlayActive()
        self.showRangeIndicator = visible
        if visible:
            self.mapView.currentSolarsystem.ShowRangeIndicator()
        else:
            self.mapView.currentSolarsystem.HideRangeIndicator()

    def OnBallparkSetState(self):
        if not self.destroyed:
            uthread.new(self.LoadSolarSystem)

    def OnSetCameraOffset(self, camera, cameraOffset):
        if self.IsFullscreen():
            cameraOffset = sm.GetService('sceneManager').GetCameraOffset('default')
            x = -(cameraOffset * 0.5 - 0.5)
            self.mapView.camera.cameraCenter = (x, 0.5)
        else:
            self.mapView.camera.cameraCenter = (0.5, 0.5)

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change and not IsSolarSystem(change['locationid'][1]):
            uthread.new(self.LoadSolarSystem)

    def LoadSolarSystem(self):
        if self.destroyed:
            return
        self.mapView.LoadSolarSystemDetails(session.solarsystemid2)
        lastloaded = settings.char.ui.Get('solarSystemView_loaded_%s' % self.mapViewID, None)
        settings.char.ui.Set('solarSystemView_loaded_%s' % self.mapViewID, session.solarsystemid2)
        resetCamera = lastloaded != session.solarsystemid2
        if resetCamera:
            self.mapView.FrameSolarSystem()
        self.mapView.sceneContainer.display = True
        self.SetCaption(cfg.evelocations.Get(session.solarsystemid2).name)
        if self.showRangeIndicator:
            self.mapView.currentSolarsystem.ShowRangeIndicator()
        probeScanner = ProbeScannerWindow.GetIfOpen()
        if probeScanner:
            self.StartProbeHandler()
        directionalScanner = DirectionalScanner.GetIfOpen()
        if directionalScanner:
            self.StartDirectionalScanHandler()

    def LoadDScanTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.leftbtn:
            return
        tooltipPanel.columns = 2
        tooltipPanel.AddLabelSmall(text=localization.GetByLabel('UI/Inflight/Scanner/DirectionalScan'), bold=True, cellPadding=(8, 4, 4, 2), colSpan=tooltipPanel.columns)
        divider = LineThemeColored(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=1, padding=(1, 1, 1, 0), opacity=0.3)
        tooltipPanel.AddCell(divider, cellPadding=(0, 0, 0, 2), colSpan=tooltipPanel.columns)
        for optionName, optionID, checked in ((localization.GetByLabel('UI/Inflight/Scanner/ShowScanCone'), 'showScanCone', GetScanConeDisplayState() == True), (localization.GetByLabel('UI/Inflight/Scanner/AlignWithCamera'), 'cameraAligned', GetActiveScanMode() == SCANMODE_CAMERA)):
            checkBox = Checkbox(align=uiconst.TOPLEFT, text=optionName, checked=checked, wrapLabel=False, callback=self.OnSettingButtonCheckBoxChange, retval=optionID, prefstype=None)
            tooltipPanel.AddCell(cellObject=checkBox, colSpan=tooltipPanel.columns, cellPadding=(5, 0, 5, 0))

        tooltipPanel.AddSpacer(width=2, height=2, colSpan=tooltipPanel.columns)
        tooltipPanel.state = uiconst.UI_NORMAL

    def OnSettingButtonCheckBoxChange(self, checkbox, *args, **kwds):
        optionID = checkbox.data['value']
        enabled = checkbox.GetValue()
        if optionID == 'cameraAligned':
            ToggleScanMode()
        elif optionID == 'showScanCone':
            SetScanConeDisplayState(enabled)

    def CmdZoomInOut(self, zoomDelta):
        if self.mapView:
            self.mapView.camera.ZoomMouseWheelDelta(zoomDelta, immediate=False)
