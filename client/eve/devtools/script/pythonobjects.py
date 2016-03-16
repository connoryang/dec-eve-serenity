#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\pythonobjects.py
import blue
import gc
import weakref
import sys
import stackless
import carbonui.const as uiconst
from util import FmtDate
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.control import entries as listentry
from htmlwriter import MultipleReplacer
from copy import deepcopy
from copy import deepcopy
import log

class PythonObjectsMonitor(Window):
    default_caption = 'Python objects'
    default_windowID = 'pythonobjectsmonitor'
    default_minSize = (500, 400)

    def ApplyAttributes(self, attributes):
        self._ready = False
        self.detailsWindow = None
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(8)
        self.settingsContainer = Container(parent=self.sr.main, align=uiconst.TOTOP, height=16, padding=8)
        self.filterEdit = SinglelineEdit(parent=self.settingsContainer, align=uiconst.TOLEFT, width=150, label='Filter:', OnReturn=self.PopulateScroll)
        Button(parent=self.settingsContainer, label='Reset', align=uiconst.TORIGHT, func=self.Reset, padRight=8)
        Button(parent=self.settingsContainer, label='Refresh', align=uiconst.TORIGHT, func=self.PopulateScroll, padRight=8)
        self.scroll = Scroll(parent=self.sr.main, id='pythonobjectscroll', align=uiconst.TOALL)
        self.Reset()
        self._ready = True

    def Reset(self, *args):
        if self.detailsWindow:
            self.detailsWindow.Close()
            self.detailsWindow = None
        self.peakCount = {}
        self.baseCount = {}
        self.filterEdit.SetText('')
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
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=key, label=label, OnDblClick=self.ClassEntryDetails)
            contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['Name',
         'Delta',
         'Count',
         'Peak'])

    def ClassEntryDetails(self, entry, *args):
        if not session.role and service.ROLE_QA:
            return
        if self.detailsWindow and self.detailsWindow.IsOpen():
            self.detailsWindow.SwitchItemClass(entry.name)
        else:
            self.detailsWindow = PythonObjectClassDetails.Open(itemClass=entry.name)

    def PopulateScroll(self, *args):
        objectsByType = {}
        for object in gc.get_objects():
            tp = type(object)
            if not isinstance(object, weakref.ProxyType):
                try:
                    tp = object.__class__
                except AttributeError:
                    sys.exc_clear()

            objectsByType[tp] = objectsByType.get(tp, 0) + 1

        objectsByModuleAndType = {}
        for k, v in objectsByType.iteritems():
            name = k.__module__ + '.' + k.__name__
            objectsByModuleAndType[name] = objectsByModuleAndType.get(name, 0) + v

        for key, value in objectsByModuleAndType.iteritems():
            peak = self.peakCount.get(key, 0)
            if value > peak:
                self.peakCount[key] = value
            if key not in self.baseCount:
                self.baseCount[key] = value

        filter = self.filterEdit.text.lower()
        self.RebuildScrollContents(objectsByModuleAndType, filter)


class PythonObjectClassDetails(Window):
    default_caption = 'Python Object Class Details'
    default_windowID = 'pythonobjectclassdetails'
    default_minSize = (500, 400)

    def ApplyAttributes(self, attributes):
        self._ready = False
        Window.ApplyAttributes(self, attributes)
        self.collectTimestamp = None
        self.itemClass = attributes.itemClass
        self.classDetailsContainer = Container(parent=self.sr.topParent, align=uiconst.TOTOP, height=32, padding=16)
        self.scroll = Scroll(parent=self.sr.main, id='pythonobjectclassdetailscroll', align=uiconst.TOALL)
        self.ShowObjectDetail()
        self._ready = True

    def Close(self, setClosed = False, *args, **kwds):
        self.scroll = None
        self.classDetailsContainer = None
        gc.collect()
        Window.Close(self, setClosed, *args, **kwds)

    def Refresh(self):
        self.scroll.Clear()
        self.classDetailsContainer.Flush()
        self.ShowObjectDetail()

    def SwitchItemClass(self, itemClass):
        if not self._ready:
            return
        self.itemClass = itemClass
        self._ready = False
        self.Refresh()
        self._ready = True

    def ShowObjectDetail(self):
        objectDetails = self.GetObjectDetails()
        classLabel = EveLabelMedium(name='classLabel', parent=self.classDetailsContainer, text='module.class: %s' % self.itemClass, align=uiconst.TOPLEFT)
        timeStamp = EveLabelMedium(name='timestamp', parent=self.classDetailsContainer, text='Collected at %s' % FmtDate(self.collectTimestamp), align=uiconst.BOTTOMLEFT)
        oCount = len(objectDetails)
        objectCount = EveLabelMedium(name='oCount', parent=self.classDetailsContainer, text='%s Object%s' % (oCount, ['', 's'][oCount > 1]), align=uiconst.BOTTOMRIGHT)
        self.PopulateScroll(objectDetails)

    def PopulateScroll(self, objectData):
        contentList = []
        for object in objectData:
            objectName = self.GetObjectName(object)
            data = {'GetSubContent': self.GetReferees,
             'label': objectName,
             'id': objectName,
             'instanceData': object,
             'sublevel': 0,
             'showlen': 0}
            contentList.append(listentry.Get('Group', data))

        self.scroll.Load(contentList=contentList)

    def GetReferees(self, data, *args):
        refList = []
        object = data.instanceData
        referrers = gc.get_referrers(object)
        myref = stackless.getcurrent().frame
        known = [gc.garbage,
         stackless.getcurrent().frame,
         object,
         data,
         self.scroll]
        for ref in referrers:
            if ref not in known:
                try:
                    objectName = self.GetObjectName(ref)
                    listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, name=objectName, label=objectName, sublevel=1)
                    refList.append(listEntry)
                except Exception as e:
                    log.LogError('Failed naming reference! Need to do something about this error')

        return refList

    def GetObjectDetails(self):
        self.collectTimestamp = startTime = blue.os.GetWallclockTimeNow()
        activeObjects = gc.get_objects()
        objectDetails = []
        for activeObject in activeObjects:
            typeOrClass = type(activeObject)
            if not isinstance(activeObject, weakref.ProxyType):
                try:
                    typeOrClass = activeObject.__class__
                except AttributeError:
                    sys.exc_clear()

            objectName = '%s.%s' % (typeOrClass.__module__, typeOrClass.__name__)
            if objectName == self.itemClass:
                objectDetails.append(activeObject)

        endTime = blue.os.GetWallclockTimeNow()
        log.LogInfo('Finished fetching object details in %s Ms' % blue.os.TimeDiffInMs(startTime, endTime))
        return objectDetails

    def GetObjectName(self, object):
        Swing = MultipleReplacer({'&': '&amp;',
         '<': '&lt;',
         '>': '&gt;',
         '\n': '<br>',
         '    ': '&nbsp;&nbsp;&nbsp;'})
        objectName = '%s at 0x%.8x: %s' % (object.__class__, id(object), repr(object))
        objectName = '%s - Ref Count = %s' % (objectName, sys.getrefcount(object) - 4)
        objectName = Swing(objectName)
        return objectName
