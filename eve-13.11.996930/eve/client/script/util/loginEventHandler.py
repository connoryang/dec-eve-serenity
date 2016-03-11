#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\util\loginEventHandler.py
import blue

class LoginEventHandler:
    __notifyevents__ = ['OnClientStageChanged', 'OnNewState']

    def __init__(self):
        self.events = {}
        self.defaults = None
        sm.RegisterNotify(self)

    def OnClientStageChanged(self, what):
        self.events[what] = True

    def OnNewState(self, bp):
        self.events['newstate'] = True

    def WaitForEvent(self, what):
        while what not in self.events or not self.events[what]:
            blue.synchro.Yield()

        self.events[what] = False

    def WaitForEula(self):
        self.WaitForEvent('login')

    def WaitForCharsel(self):
        viewState = sm.GetService('viewState')
        while not viewState.IsViewActive('charsel'):
            blue.synchro.Yield()


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('loginEventHandler', locals())
