#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\dockPanelUtil.py
from carbonui import const as uiconst

def GetDockPanelManager():
    if getattr(uicore, 'dockablePanelManager', None) is None:
        from eve.client.script.ui.shared.mapView.dockPanelManager import DockablePanelManager
        uicore.dockablePanelManager = DockablePanelManager()
    return uicore.dockablePanelManager


def GetPanelSettings(panelID):
    defaultSettings = {'align': uiconst.TOPLEFT,
     'dblToggleFullScreenAlign': uiconst.TOPLEFT,
     'positionX': 0.5,
     'positionY': 0.5,
     'widthProportion': 0.8,
     'heightProportion': 0.8,
     'widthProportion_docked': 0.5,
     'heightProportion_docked': 1.0,
     'pushedBy': []}
    if panelID:
        registered = settings.char.dockPanels.Get(panelID, {})
        defaultSettings.update(registered)
    return defaultSettings


def RegisterPanelSettings(panelID, panelSettings):
    settings.char.dockPanels.Set(panelID, panelSettings)
