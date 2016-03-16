#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\probeScannerWindow.py
import carbonui.const as uiconst
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.inflight.scannerFiles.scannerToolsPalette import ScannerToolsPalette
MIN_WINDOW_WIDTH = 320
MIN_WINDOW_HEIGHT = 250

class ProbeScannerWindow(Window):
    default_windowID = 'probeScannerWindow'
    default_width = 400
    default_height = 400
    default_minSize = (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    default_captionLabelPath = 'UI/Inflight/Scanner/ProbeScanner'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.scope = 'inflight'
        self.SetWndIcon(None)
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        self.scannerTools = ScannerToolsPalette(parent=self.GetMainArea(), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, padding=const.defaultPadding, idx=0)

    def Confirm(self, *args):
        self.scannerTools.Confirm()
