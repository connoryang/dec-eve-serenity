#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\enginetools.py
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.control.eveWindow import Window
from eve.devtools.script.bdqmonitor import BackgroundDownloadQueueMonitor
from eve.devtools.script.engineinfopanel import EngineInfoPanel
from eve.devtools.script.graphswindow import GraphsWindow
from eve.devtools.script.livecountmonitor import LiveCountMonitor
from eve.devtools.script.logviewer import LogViewer
from eve.devtools.script.memorymonitor import MemoryMonitor
from eve.devtools.script.methodcallsmonitor import MethodCallsMonitor
from eve.devtools.script.networkdatamonitor import NetworkDataMonitor
from eve.devtools.script.outstandingmonitor import OutstandingMonitor
from eve.devtools.script.pythonobjects import PythonObjectsMonitor
from eve.devtools.script.resmanmonitor import ResManMonitor
from eve.devtools.script.taskletMonitor import TaskletMonitor
from eve.devtools.script.telemetrypanel import TelemetryPanel
from eve.devtools.script.threadmonitor import ThreadMonitor
import blue
import service
TOOLS = [['Memory', MemoryMonitor, 0],
 ['LiveCount', LiveCountMonitor, 0],
 ['Python objects', PythonObjectsMonitor, 0],
 ['Log viewer', LogViewer, 0],
 ['Method Calls', MethodCallsMonitor, 0],
 ['Outstanding Calls', OutstandingMonitor, 0],
 ['Network', NetworkDataMonitor, 0],
 ['Background download queue monitor', BackgroundDownloadQueueMonitor, service.ROLE_QA],
 ['Threads', ThreadMonitor, service.ROLE_QA],
 ['Tasklets', TaskletMonitor, service.ROLE_QA],
 ['Blue statistics graphs', GraphsWindow, service.ROLE_QA],
 ['Telemetry panel', TelemetryPanel, service.ROLE_QA],
 ['Resource Manager', ResManMonitor, service.ROLE_QA]]

class EngineToolsLauncher(Window):
    default_caption = 'Engine Tools'
    default_minSize = (500, 300)
    default_windowID = 'EngineTools'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        EngineInfoPanel(parent=self.sr.main, align=uiconst.TOTOP, height=48, padding=14)
        scroll = ScrollContainer(parent=self.sr.main, align=uiconst.TOALL, padding=10)
        for name, obj, roleRequired in TOOLS:
            if roleRequired and session.role & roleRequired == 0:
                continue

            def OnClick(wnd):
                wnd.Open()

            Button(parent=scroll, label=name, align=uiconst.TOTOP, padding=4, func=OnClick, args=obj)
