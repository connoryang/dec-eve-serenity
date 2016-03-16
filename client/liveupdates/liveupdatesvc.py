#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\liveupdates\liveupdatesvc.py
import carbon.common.script.sys.service as service
from . import LiveUpdaterClientMixin

class LiveUpdateSvc(service.Service):
    __guid__ = 'svc.LiveUpdateSvc'
    __notifyevents__ = ['OnLiveClientUpdate']

    def __init__(self):
        self.liveUpdater = LiveUpdaterClientMixin()
        service.Service.__init__(self)

    def Enabled(self):
        return False

    def OnLiveClientUpdate(self, payload):
        if self.Enabled():
            self.liveUpdater.HandlePayload(payload)
