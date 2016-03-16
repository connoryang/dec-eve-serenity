#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\methodcallsmonitor.py
import carbonui.const as uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
import base
import blue
import uthread2
import util

class MethodCallsMonitor(Window):
    default_caption = 'Method Calls'
    default_windowID = 'methodcalls'
    default_minSize = (400, 300)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(4)
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, height=16, padding=8)
        self.filterEdit = SinglelineEdit(parent=self.settingsContainer, align=uiconst.TOLEFT, width=150, label='Filter:')
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.TORIGHT, func=self.Reset)
        self.scroll = Scroll(parent=self.sr.main, id='methodcallsscroll', align=uiconst.TOALL)
        self.Reset()
        self._ready = True
        uthread2.StartTasklet(self.Refresh)

    def Reset(self, *args):
        self.filterEdit.SetText('')
        self.PopulateScroll()

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            self.PopulateScroll()

    def PopulateScroll(self, *args):
        contentList = []
        history = list(base.methodCallHistory)
        history.reverse()
        filter = self.filterEdit.text
        count = 0
        for ct in history:
            method = ct[0]
            if filter and filter not in method.lower():
                continue
            t = ct[1]
            label = '%s<t>%s<t>%s' % (method, util.FmtDate(t, 'nl'), ct[2] / const.MSEC)
            contentList.append(ScrollEntryNode(decoClass=SE_GenericCore, label=label))
            count += 1
            if count == 100:
                break

        self.scroll.Load(contentList=contentList, headers=['method', 'time', 'ms'])
