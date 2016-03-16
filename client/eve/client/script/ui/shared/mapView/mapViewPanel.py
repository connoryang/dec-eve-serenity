#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewPanel.py
from eve.client.script.ui.shared.mapView.dockPanelConst import DOCKPANELID_MAP
from eve.client.script.ui.shared.mapView.mapView import MapView
from eve.client.script.ui.shared.mapView.mapViewConst import MAPVIEW_PRIMARY_ID
from eve.client.script.ui.shared.mapView.mapViewSearch import MapViewSearchControl
from eve.client.script.ui.shared.mapView.mapViewSettings import MapViewSettingButtons
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
import carbonui.const as uiconst
import logging
log = logging.getLogger(__name__)
OVERLAY_LEFT_PADDING_FULLSCREEN = 360
OVERLAY_RIGHT_PADDING_FULLSCREEN = 280
OVERLAY_SIDE_PADDING_NONFULLSCREEN = 6

class MapViewPanel(DockablePanel):
    __notifyevents__ = ['OnSetCameraOffset', 'OnHideUI', 'OnShowUI']
    default_captionLabelPath = 'UI/Neocom/MapBtn'
    default_windowID = DOCKPANELID_MAP
    default_iconNum = 'res:/UI/Texture/windowIcons/map.png'
    panelID = default_windowID
    mapViewID = MAPVIEW_PRIMARY_ID
    mapView = None
    overlayTools = None

    def OnSetCameraOffset(self, camera, cameraOffset):
        if self.mapView and not self.mapView.destroyed:
            if self.IsFullscreen():
                cameraOffset = sm.GetService('sceneManager').GetCameraOffset('default')
                x = -(cameraOffset * 0.5 - 0.5)
                self.mapView.camera.cameraCenter = (x, 0.5)
            else:
                self.mapView.camera.cameraCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        DockablePanel.ApplyAttributes(self, attributes)
        if uicore.cmd.IsUIHidden():
            self.toolbarContainer.display = False
        self.mapView = MapView(parent=self.GetMainArea(), isFullScreen=self.IsFullscreen(), mapViewID=self.mapViewID, interestID=attributes.interestID, starColorMode=attributes.starColorMode)
        if self.IsFullscreen():
            self.mapView.overlayTools.padding = (OVERLAY_LEFT_PADDING_FULLSCREEN,
             self.toolbarContainer.height + 6,
             OVERLAY_RIGHT_PADDING_FULLSCREEN,
             6)
        else:
            self.mapView.overlayTools.padding = (OVERLAY_SIDE_PADDING_NONFULLSCREEN,
             self.toolbarContainer.height + 6,
             OVERLAY_SIDE_PADDING_NONFULLSCREEN,
             6)
        MapViewSettingButtons(parent=self.toolbarContainer, align=uiconst.CENTERLEFT, onSettingsChangedCallback=self.mapView.OnMapViewSettingChanged, mapViewID=self.mapViewID, left=4, idx=0)
        MapViewSearchControl(parent=self.mapView.overlayTools, mapView=self.mapView, align=uiconst.TOPRIGHT, idx=0)

    def Close(self, *args, **kwds):
        DockablePanel.Close(self, *args, **kwds)
        self.mapView = None

    def OnShowUI(self):
        self.mapView.overlayTools.display = True
        self.toolbarContainer.display = True

    def OnHideUI(self):
        if self.IsFullscreen():
            self.mapView.overlayTools.display = False
            self.toolbarContainer.display = False

    def SetActiveItemID(self, *args, **kwds):
        if self.mapView:
            return self.mapView.SetActiveItemID(*args, **kwds)

    def SetViewColorMode(self, *args, **kwds):
        if self.mapView:
            return self.mapView.SetViewColorMode(*args, **kwds)

    def OnDockModeChanged(self, *args, **kwds):
        if self.mapView:
            if self.mapView.overlayTools and not self.mapView.overlayTools.destroyed:
                if self.IsFullscreen():
                    self.mapView.overlayTools.padLeft = OVERLAY_LEFT_PADDING_FULLSCREEN
                    self.mapView.overlayTools.padRight = OVERLAY_RIGHT_PADDING_FULLSCREEN
                else:
                    self.mapView.overlayTools.padLeft = OVERLAY_SIDE_PADDING_NONFULLSCREEN
                    self.mapView.overlayTools.padRight = OVERLAY_SIDE_PADDING_NONFULLSCREEN
            self.mapView.OnDockModeChanged(self.IsFullscreen())

    def _OnResize(self, *args):
        DockablePanel._OnResize(self, *args)
        if self.mapView:
            self.mapView.UpdateViewPort()

    def SetActive(self, *args, **kwds):
        DockablePanel.SetActive(self, *args, **kwds)
        if self.mapView:
            self.mapView.SetFocusState(True)

    def OnSetInactive(self, *args, **kwds):
        DockablePanel.OnSetInactive(self, *args, **kwds)
        if self.mapView:
            self.mapView.SetFocusState(False)

    def CmdZoomInOut(self, zoomDelta):
        if self.mapView:
            self.mapView.camera.ZoomMouseWheelDelta(zoomDelta, immediate=False)
