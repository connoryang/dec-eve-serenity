#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\outstandingmonitor.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
import base
import util
import uthread2

class OutstandingMonitor(Window):
    default_caption = 'Outstanding Calls'
    default_windowID = 'outstandingcalls'
    default_minSize = (400, 300)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(4)
        self.scroll = Scroll(parent=self.sr.main, id='outstandingscroll', align=uiconst.TOALL)
        uthread2.StartTasklet(self.Refresh)

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            self.PopulateScroll()

    def PopulateScroll(self, *args):
        scrolllist = []
        for ct in base.outstandingCallTimers:
            method = ct[0]
            t = ct[1]
            label = '%s<t>%s<t>%s' % (method, util.FmtDate(t, 'nl'), util.FmtTime(blue.os.GetWallclockTimeNow() - t))
            scrolllist.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label))

        self.scroll.Load(contentList=scrolllist, headers=['method', 'time', 'dt'])
