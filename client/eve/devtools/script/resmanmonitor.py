#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\resmanmonitor.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore, SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.checkbox import Checkbox
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveWindow import Window
import uthread2

class NumberAttribute(SE_BaseClassCore):
    refreshDelay = 0.5

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        left = Container(parent=self, align=uiconst.TOLEFT_PROP, width=0.5)
        right = Container(parent=self, align=uiconst.TOALL)
        self.label = Label(parent=left)
        self.value = Label(parent=right, autoUpdate=True)
        self.GetValue = None

    def Load(self, node):
        self.GetValue = node.getvalue
        self.label.SetText(node.text)
        self.UpdateValue()

    def UpdateValue(self):
        if self.GetValue:
            self.value.text = self.GetValue()


def FormatTime(value):
    if value < 1:
        return '%.2fms' % (value * 1000)
    if value < 10:
        return '%.3fs' % value
    return '%.1fs' % value


class ResManMonitor(Window):
    default_caption = 'Resource Manager Monitor'
    default_windowID = 'resmanmonitor'
    default_minSize = (500, 400)
    refreshDelay = 0.5

    def PopulateAttributes(self):
        resManAttrs = [('Pending loads', lambda : blue.resMan.pendingLoads),
         ('Pending prepares', lambda : blue.resMan.pendingPrepares),
         ('Prepares handled last tick', lambda : blue.resMan.preparesHandledLastTick),
         ('Maximum prepares handled per tick', lambda : blue.resMan.preparesHandledPerTickMax),
         ('Maximum time on main thread per tick', lambda : FormatTime(blue.resMan.mainThreadMaxTime)),
         ('Average time in load queue', lambda : FormatTime(blue.resMan.loadQueueTimeAverage)),
         ('Maximum time in load queue', lambda : FormatTime(blue.resMan.loadQueueTimeMax)),
         ('Average time in prepare queue', lambda : FormatTime(blue.resMan.prepareQueueTimeAverage)),
         ('Maximum time in prepare queue', lambda : FormatTime(blue.resMan.prepareQueueTimeMax))]
        contentList = []
        for attrDesc in resManAttrs:
            text, getvalue = attrDesc
            node = ScrollEntryNode(decoClass=NumberAttribute, text=text, getvalue=getvalue)
            contentList.append(node)

        self.attributes.Load(contentList=contentList)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(8)
        top = Container(parent=self.sr.main, align=uiconst.TOTOP, height=128, padding=8)
        self.loadObjectCacheEnabledChk = Checkbox(parent=top, align=uiconst.TOTOP, text='Load Object Cache Enabled', width=120, checked=blue.resMan.loadObjectCacheEnabled, callback=self._OnLoadObjectCacheEnabledChk)
        self.attributes = Scroll(parent=top, align=uiconst.TOALL)
        bottom = LayoutGrid(parent=self.sr.main, align=uiconst.TOBOTTOM, height=100, columns=4, cellPadding=5)
        self.filterEdit = SinglelineEdit(parent=bottom, width=150, label='Filter:', OnReturn=self._OnRefresh)
        Button(parent=bottom, label='Refresh', func=self._OnRefresh, fixedwidth=80)
        Button(parent=bottom, label='Reload', func=self._OnReload, fixedwidth=80)
        Button(parent=bottom, label='Clear cache', func=self._OnClear, fixedwidth=80)
        Label(parent=self.sr.main, align=uiconst.TOTOP, text='<b>Resources', padLeft=8)
        self.scroll = Scroll(parent=self.sr.main, id='resmanmonitorscroll', align=uiconst.TOALL, padding=2)
        self.PopulateAttributes()
        self.PopulateScroll()
        uthread2.StartTasklet(self.RefreshAttributes)

    def RefreshAttributes(self):
        while not self.destroyed:
            uthread2.Sleep(self.refreshDelay)
            for each in self.attributes.GetNodes():
                if each.panel:
                    each.panel.UpdateValue()

    def _OnLoadObjectCacheEnabledChk(self, checkbox):
        blue.resMan.loadObjectCacheEnabled = checkbox.GetValue()

    def GetEntryForObject(self, wr, filename, isCachedStr):
        typename = type(wr.object).__name__
        memory = 0
        if hasattr(wr.object, 'GetMemoryUsage'):
            memory = wr.object.GetMemoryUsage()
        pyRC, blueRC = wr.object.GetRefCounts()
        label = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (filename,
         typename,
         memory,
         isCachedStr,
         blueRC,
         pyRC)
        listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, label=label, object_ref=wr)
        return listEntry

    def AddKeys(self, contentList, keys, isCachedStr, filter = None):
        for each in keys:
            wr = blue.motherLode.LookupAsWeakRef(each)
            if wr.object is not None:
                filename = str(each)
                if not filter or filter.lower() in filename.lower():
                    listEntry = self.GetEntryForObject(wr, filename, isCachedStr)
                    contentList.append(listEntry)

    def PopulateScroll(self):
        contentList = []
        self.AddKeys(contentList, blue.motherLode.GetCachedKeys(), 'Y', self.filterEdit.text)
        self.AddKeys(contentList, blue.motherLode.GetNonCachedKeys(), 'N', self.filterEdit.text)
        self.scroll.LoadContent(contentList=contentList, headers=['Filename',
         'Type',
         'Memory usage',
         'Cached?',
         'Blue Refs',
         'Python Refs'])

    def _OnRefresh(self, *args):
        self.PopulateScroll()

    def _OnReload(self, *args):
        selected = self.scroll.GetSelected()
        for each in selected:
            if each.object_ref.object:
                each.object_ref.object.Reload()

    def _OnClear(self, *args):
        blue.motherLode.ClearCached()
        self.PopulateScroll()
