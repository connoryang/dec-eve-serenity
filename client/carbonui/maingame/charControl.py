#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\maingame\charControl.py
import carbonui.const as uiconst
from carbonui.control.layer import LayerCore

class CoreCharControl(LayerCore):
    __guid__ = 'uicls.CharControlCore'

    def ApplyAttributes(self, *args, **kw):
        LayerCore.ApplyAttributes(self, *args, **kw)
        self.opened = 0
        self.cursor = uiconst.UICURSOR_POINTER

    def GetConfigValue(self, data, name, default):
        return default

    def OnOpenView(self):
        self.isTabStop = True
        self.state = uiconst.UI_NORMAL
        self.OnSetFocus()

    def OnCloseView(self):
        self.OnKillFocus()
        self.isTabStop = False

    def OnKillFocus(self, *args):
        nav = sm.GetService('navigation')
        nav.controlLayer = None
        nav.hasFocus = False
        nav.RecreatePlayerMovement()

    def OnSetFocus(self, *args):
        nav = sm.GetService('navigation')
        nav.controlLayer = self
        nav.hasFocus = True
        nav.RecreatePlayerMovement()
