#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\dockPanelManager.py
from eve.client.script.ui.shared.mapView.dockPanelConst import SETTINGSKEY
from eve.client.script.ui.view.viewStateConst import ViewState
import uthread
import carbonui.const as uiconst

class DockablePanelManager(object):
    __notifyevents__ = ['OnSetDevice',
     'OnShowUI',
     'OnHideUI',
     'OnUIScalingChange']
    panels = {}

    def __init__(self):
        sm.RegisterNotify(self)

    def OnViewStateClosed(self):
        for panel in self.panels.values():
            if panel.IsFullscreen():
                uthread.new(panel.Close)

    def GetPanel(self, panelID):
        panel = self.panels.get(panelID, None)
        if panel and not panel.destroyed:
            return panel

    def GetPanels(self):
        return self.panels

    def HasPanel(self, panelID):
        return bool(self.GetPanel(panelID))

    def RegisterPanel(self, dockPanel):
        if dockPanel.panelID in self.panels:
            prevPanel = self.panels[dockPanel.panelID]
            if not prevPanel.destroyed:
                prevPanel.Close()
        self.panels[dockPanel.panelID] = dockPanel

    def UnregisterPanel(self, dockPanel):
        if dockPanel.panelID in self.panels:
            del self.panels[dockPanel.panelID]
        self.CheckViewState()

    def CheckViewState(self):
        haveFullscreenPanel = bool(self.GetFullScreenView())
        if not haveFullscreenPanel:
            sm.GetService('viewState').CloseSecondaryView(ViewState.DockPanel)
        self.UpdateCameraCenter()

    def GetFullScreenView(self):
        for panel in self.panels.values():
            if panel.IsFullscreen():
                return panel

    def UpdateCameraCenter(self):
        haveDockedPanel = False
        for panel in self.panels.values():
            if panel.IsDockedLeft() or panel.IsDockedRight():
                haveDockedPanel = True
                break

        if haveDockedPanel and eve.hiddenUIState is None:
            pLeft, pRight = uicore.layer.sidePanels.GetSideOffset()
            viewCenter = pLeft + (uicore.desktop.width - pLeft - pRight) / 2
            viewCenterProportion = viewCenter / float(uicore.desktop.width)
            sm.GetService('sceneManager').SetCameraOffsetOverride(-100 + int(200 * viewCenterProportion))
        else:
            sm.GetService('sceneManager').SetCameraOffsetOverride(None)

    def OnSetDevice(self, *args, **kwds):
        for panel in self.panels.values():
            if not panel.IsFullscreen():
                panel.InitDockPanelPosition()

    def OnHideUI(self, *args):
        self.UpdateCameraCenter()

    def OnShowUI(self, *args):
        self.UpdateCameraCenter()

    def UpdatePanelsPushedBySettings(self):
        for panel in self.panels.values():
            if panel.align not in (uiconst.TOLEFT, uiconst.TORIGHT):
                continue
            pushedBy = []
            for each in uicore.layer.sidePanels.children:
                if each is panel:
                    break
                if each.align == panel.align:
                    pushedBy.append(each.name)

            currentSettings = panel.GetPanelSettings()
            currentSettings['pushedBy'] = pushedBy
            settings.char.ui.Set(SETTINGSKEY % panel.panelID, currentSettings)

    def OnUIScalingChange(self, *args):
        for panel in self.panels.values():
            if not panel.IsFullscreen():
                panel.InitDockPanelPosition()
