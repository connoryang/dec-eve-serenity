#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\moonscan.py
import service
from eve.client.script.ui.inflight.scannerFiles.moonScanner import MoonScanner

class MoonScanSvc(service.Service):
    __guid__ = 'svc.moonScan'
    __update_on_reload__ = 1
    __exportedcalls__ = {'Clear': [],
     'ClearEntry': [],
     'Refresh': []}
    __notifyevents__ = ['OnMoonScanComplete']

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.scans = {}
        self.wnd = None

    def OnMoonScanComplete(self, moonID, results):
        self.scans[moonID] = results
        self.Refresh()

    def GetWnd(self, create):
        wnd = MoonScanner.GetIfOpen()
        if not wnd and create:
            MoonScanner.Open()
            return self.GetWnd(0)
        return wnd

    def Refresh(self):
        self.GetWnd(1).SetEntries(self.scans)

    def Clear(self):
        self.scans = {}
        if self.GetWnd(0):
            self.GetWnd(1).ClearMoons()

    def ClearEntry(self, celestialID):
        if celestialID in self.scans:
            del self.scans[celestialID]
        self.Refresh()
