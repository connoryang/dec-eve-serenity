#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\graphswindow.py
import blue
import carbonui.const as uiconst
import uthread
from carbonui.control.buttons import ButtonCoreOverride as Button
from carbonui.control.checkbox import CheckboxCoreOverride as Checkbox
from carbonui.control.scroll import ScrollCoreOverride as Scroll
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveWindow import Window
from trinity.GraphManager import GraphManager
from nicenum import FormatMemory, Format

class GraphsWindow(Window):
    default_caption = 'Blue stats graphs'
    default_minSize = (700, 500)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.graphs = GraphManager()
        self.graphs.SetEnabled(True)
        if hasattr(self, 'SetTopparentHeight'):
            self.SetTopparentHeight(0)
            self.container = Container(parent=self.sr.main, align=uiconst.TOALL)
        else:
            self.container = Container(parent=self.sr.content, align=uiconst.TOALL)
        self.settingsContainer = Container(parent=self.container, align=uiconst.TOTOP, height=30, padding=10)
        self.showTimersChk = Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Timers', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showMemoryChk = Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Memory counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showLowCountersChk = Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Low counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.showHighCountersChk = Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='High counters', checked=True, width=120, height=30, callback=self.PopulateScroll)
        self.taskletTimersChk = Checkbox(parent=self.settingsContainer, align=uiconst.TOLEFT, text='Tasklet timers', width=120, checked=blue.pyos.taskletTimer.active, callback=self.OnTaskletTimersChk)
        self.resetBtn = Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Reset peaks', fixedwidth=80, padRight=8, func=self.PopulateScroll)
        self.refreshBtn = Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Refresh', fixedwidth=80, padRight=8, func=self.PopulateScroll)
        self.scroll = Scroll(parent=self.container, id='blueGraphsScroll', align=uiconst.TOTOP, height=200)
        self.graphsContainer = Container(parent=self.container, align=uiconst.TOALL)
        self._ready = True
        self.PopulateScroll()

    def Close(self, *args, **kwargs):
        self.graphs.SetEnabled(False)
        Window.Close(self, *args, **kwargs)

    def DelayedRefresh_thread(self):
        blue.synchro.SleepWallclock(600)
        self.PopulateScroll()

    def DelayedRefresh(self):
        uthread.new(self.DelayedRefresh_thread)

    def ResetPeaks(self, *args):
        blue.statistics.ResetPeaks()
        self.DelayedRefresh()

    def PopulateScroll(self, *args):
        typesIncluded = []
        if self.showTimersChk.GetValue():
            typesIncluded.append('time')
        if self.showMemoryChk.GetValue():
            typesIncluded.append('memory')
        if self.showLowCountersChk.GetValue():
            typesIncluded.append('counterLow')
        if self.showHighCountersChk.GetValue():
            typesIncluded.append('counterHigh')
        stats = blue.statistics.GetValues()
        desc = blue.statistics.GetDescriptions()
        contentList = []
        for key, value in desc.iteritems():
            type = value[1]
            if type in typesIncluded:
                peak = stats[key][1]
                if type == 'memory':
                    label = '%s<t>%s<t>%s' % (key, FormatMemory(peak), value[0])
                elif type.startswith('counter'):
                    label = '%s<t>%s<t>%s' % (key, Format(peak, 1), value[0])
                elif type == 'time':
                    label = '%s<t>%s<t>%s' % (key, Format(peak, 1e-10), value[0])
                listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=key, peak=peak, desc=value[0], label=label, GetMenu=self.GetListEntryMenu, OnDblClick=self.OnListEntryDoubleClicked)
                contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['Name', 'Peak', 'Description'], noContentHint='No Data available')

    def GetListEntryMenu(self, listEntry):
        return (('Right-click action 1', None), ('Right-click action 2', None))

    def OnListEntryDoubleClicked(self, listEntry):
        node = listEntry.sr.node
        if self.graphs.HasGraph(node.name):
            self.graphs.RemoveGraph(node.name)
        else:
            self.graphs.AddGraph(node.name)

    def OnTaskletTimersChk(self, checkbox):
        blue.pyos.taskletTimer.active = checkbox.GetValue()
        self.PopulateScroll()

    def _OnResize(self):
        if self._ready:
            l, t, w, h = self.graphsContainer.GetAbsolute()
            scaledAbs = (uicore.ScaleDpi(l),
             uicore.ScaleDpi(t),
             uicore.ScaleDpi(w),
             uicore.ScaleDpi(h))
            self.graphs.AdjustViewports(scaledAbs)
