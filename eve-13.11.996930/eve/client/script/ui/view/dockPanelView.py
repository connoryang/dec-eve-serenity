#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\dockPanelView.py
from viewstate import View
from eve.client.script.ui.view.viewStateConst import ViewState

class DockPanelView(View):
    __guid__ = 'viewstate.DockPanelView'
    __layerClass__ = None

    def LoadView(self, **kwargs):
        import trinity
        sm.GetService('sceneManager').RegisterScene(trinity.EveSpaceScene(), ViewState.DockPanel)
        sm.GetService('sceneManager').SetRegisteredScenes(ViewState.DockPanel)

    def UnloadView(self):
        uicore.dockablePanelManager.OnViewStateClosed()
        sm.GetService('sceneManager').SetRegisteredScenes('default')
        sm.GetService('sceneManager').UnregisterScene(ViewState.DockPanel)

    def CheckShouldReopen(self, newKwargs, cachedKwargs):
        return True
