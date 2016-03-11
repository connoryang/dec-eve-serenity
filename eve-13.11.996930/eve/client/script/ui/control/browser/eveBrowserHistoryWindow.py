#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\eveBrowserHistoryWindow.py
from carbonui.control.browser.browserHistoryWindow import BrowserHistoryWindowCore, BrowserHistoryWindowCoreOverride

class HistoryWindow(BrowserHistoryWindowCore):
    __guid__ = 'uicls.BrowserHistoryWindow'

    def ApplyAttributes(self, attributes):
        BrowserHistoryWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon()
        self.SetTopparentHeight(0)


BrowserHistoryWindowCoreOverride.__bases__ = (HistoryWindow,)
