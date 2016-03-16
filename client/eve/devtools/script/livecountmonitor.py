#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\livecountmonitor.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
import uthread2

class LiveCountMonitor(Window):
    default_caption = 'Live counts'
    default_windowID = 'livecountmonitor'
    default_minSize = (500, 400)
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(8)
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, height=16, padding=8)
        self.filterEdit = SinglelineEdit(parent=self.settingsContainer, align=uiconst.TOLEFT, width=150, label='Filter:')
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.TORIGHT, func=self.Reset, padRight=8)
        self.scroll = Scroll(parent=self.sr.main, id='livecountscroll', align=uiconst.TOALL)
        self.Reset()
        self._ready = True
        uthread2.StartTasklet(self.Refresh)

    def Reset(self, *args):
        self.peakCount = {}
        self.baseCount = {}
        self.lastFilter = None
        self.filterEdit.SetText('')
        self.PopulateScroll()

    def Refresh(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            self.PopulateScroll()

    def GetLabelForEntry(self, key, value):
        peak = self.peakCount.get(key, 0)
        delta = value - self.baseCount.get(key, 0)
        if delta < 0:
            color = '0xffff0000'
        else:
            color = '0xff00ff00'
        label = '%s<t><color=%s>%d</color><t>%d<t>%d' % (key,
         color,
         delta,
         value,
         peak)
        return label

    def RebuildScrollContents(self, objects, filter):
        contentList = []
        for key, value in objects.iteritems():
            if filter and filter not in key.lower():
                continue
            label = self.GetLabelForEntry(key, value)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=key, label=label)
            contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['Name',
         'Delta',
         'Count',
         'Peak'])

    def PopulateScroll(self, *args):
        objects = blue.classes.LiveCount()
        for key, value in objects.iteritems():
            peak = self.peakCount.get(key, 0)
            if value > peak:
                self.peakCount[key] = value
            if key not in self.baseCount:
                self.baseCount[key] = value

        filter = self.filterEdit.text.lower()
        if filter == self.lastFilter:
            for entry in self.scroll.GetNodes():
                key = entry.name
                count = objects[key]
                oldLabel = entry.label
                newLabel = self.GetLabelForEntry(key, count)
                if newLabel != oldLabel:
                    entry.label = newLabel
                    if entry.panel:
                        entry.panel.Load(entry)

        else:
            self.lastFilter = filter
            self.RebuildScrollContents(objects, filter)
