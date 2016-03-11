#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\dockPanelUtil.py
from eve.client.script.ui.shared.mapView.dockPanelManager import DockablePanelManager

def GetDockPanelManager():
    if getattr(uicore, 'dockablePanelManager', None) is None:
        uicore.dockablePanelManager = DockablePanelManager()
    return uicore.dockablePanelManager
