#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\eveBrowserSourceWindow.py
from carbonui.control.browser.browserSourceWindow import BrowserSourceWindowCore, BrowserSourceWindowCoreOverride

class BrowserSourceWindow(BrowserSourceWindowCore):
    __guid__ = 'uicls.BrowserSourceWindow'

    def ApplyAttributes(self, attributes):
        BrowserSourceWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon()
        self.SetTopparentHeight(0)


BrowserSourceWindowCoreOverride.__bases__ = (BrowserSourceWindow,)
