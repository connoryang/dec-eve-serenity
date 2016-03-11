#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\devtools\script\memorymonitor.py
from carbon.common.script.util.format import GetTimeParts
from carbonui import const as uiconst
from carbonui.graphs import graphsutil
from carbonui.graphs.axislabels import HorizontalAxisLabels, VerticalAxisLabels
from carbonui.graphs.grid import Grid
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.util.color import Color
from eve.devtools.script.engineinfopanel import EngineInfoPanel
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveSinglelineEdit import SinglelineEdit
import blue
import trinity
import uicontrols
import uthread2

def _OnMouseExitLegend(graph):
    graph.lineWidth = 1


def _OnMouseEnterLegend(graph):
    graph.SetOrder(0)
    graph.lineWidth = 2


def OnRefreshRateEdit(value):
    if value:
        value = max(0.1, float(value))
        value = min(10.0, value)
        refreshRate = int(10000000.0 * value)
        blue.pyos.performanceUpdateFrequency = refreshRate


def _TimeLabel(t):
    year, month, wd, day, hour, minutes, sec, ms = GetTimeParts(long(t))
    return '%2.2d:%2.2d' % (hour, minutes)


class MemoryGraph(Container):
    horizontalLabelWidth = 64

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isBuilding = True
        info = Container(parent=self, align=uiconst.TOTOP, height=64)
        EngineInfoPanel(parent=info, align=uiconst.TOLEFT_PROP, width=0.8)
        infoRight = Container(parent=info, align=uiconst.TOALL)
        refreshRate = blue.pyos.performanceUpdateFrequency / 10000000.0
        self.refreshRateEdit = SinglelineEdit(parent=infoRight, align=uiconst.TOTOP, label='Refresh rate (seconds):', setvalue=refreshRate, floats=(0.1, 10.0), OnChange=OnRefreshRateEdit)
        self.legend = Container(parent=self, align=uiconst.TOBOTTOM, height=16)
        self.graph = Container(parent=self, align=uiconst.TOALL)
        self.data = None
        self.graphs = []
        self.isBuilding = False
        self.isResizing = False

    def UpdateGraph(self):
        while not self.destroyed:
            if not self.isResizing:
                self.Build()
            uthread2.Sleep(0.5)

    def AddLegend(self, color, text, graph):
        fill = Fill(parent=self.legend, color=color, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=16)
        fill.OnMouseEnter = lambda : _OnMouseEnterLegend(graph)
        fill.OnMouseExit = lambda : _OnMouseExitLegend(graph)
        Label(parent=self.legend, text=text, align=uiconst.TOLEFT, padLeft=8, padRight=16)

    def Build(self):
        self.minGridLineHeight = 32
        self.graph.Flush()
        self.legend.Flush()
        self.isBuilding = True
        minutes = 60
        self.data = blue.pyos.cpuUsage[-minutes * 60 / 10:]
        memData = []
        pymemData = []
        bluememData = []
        othermemData = []
        workingsetData = []
        startTime = self.data[0][0]
        endTime = startTime
        for t, cpu, mem, sched in self.data:
            mem, pymem, workingset, pagefaults, bluemem = mem
            memData.append(mem)
            pymemData.append(pymem)
            bluememData.append(bluemem)
            othermem = mem - bluemem
            othermemData.append(othermem)
            workingsetData.append(workingset)
            endTime = t

        maxValues = []
        for each in [memData,
         pymemData,
         bluememData,
         othermemData,
         workingsetData]:
            maxValues.append(max(each))

        self.overallMaxValue = max(maxValues)
        bottom = Container(parent=self.graph, align=uiconst.TOBOTTOM, height=24)
        Fill(parent=bottom, align=uiconst.TOLEFT, width=80, spriteEffect=trinity.TR2_SFX_NONE)
        self.horizontalAxisLabels = HorizontalAxisLabels(parent=bottom, align=uiconst.TOBOTTOM, height=24, padRight=8, labelClass=Label, fontsize=12, minValue=startTime, maxValue=endTime, step=64, formatter=_TimeLabel)
        self.axisLabels = VerticalAxisLabels(parent=self.graph, align=uiconst.TOLEFT, width=80, padRight=8, labelClass=Label, fontsize=16, formatter=lambda x: str(int(x * 1e-06)))
        self.grid = Grid(parent=self.graph)
        self.graphContainer = Container(parent=self.graph, align=uiconst.TOALL)
        Fill(parent=self.graph, color=(0, 0, 0, 0.25))
        Fill(parent=self.legend, align=uiconst.TOLEFT, width=80, spriteEffect=trinity.TR2_SFX_NONE)
        self.graphs = []
        graphSources = [(memData, Color.RED, 'Total memory'),
         (pymemData, Color.GREEN, 'Python memory'),
         (bluememData, Color.BLUE, 'Blue memory'),
         (othermemData, Color.YELLOW, 'Other memory'),
         (workingsetData, Color.AQUA, 'Working set')]
        for source, color, text in graphSources:
            graph = LineGraph(parent=self.graphContainer, color=color, lineWidth=1, data=source, spriteEffect=trinity.TR2_SFX_FILL)
            self.graphs.append(graph)
            self.AddLegend(color, text, graph)

        self.AdjustForSize()
        self.isBuilding = False

    def AdjustForSize(self):
        width, height = self.graphContainer.GetAbsoluteSize()
        adjustedMaxValue, numGridLines = graphsutil.AdjustMaxValue(height, self.overallMaxValue, self.minGridLineHeight)
        for graph in self.graphs:
            graph.maxValue = adjustedMaxValue
            graph.Rebuild()

        gridLineStep = height / numGridLines
        self.axisLabels.maxValue = adjustedMaxValue
        self.axisLabels.count = numGridLines
        self.axisLabels.step = gridLineStep
        self.axisLabels.Rebuild()
        self.horizontalAxisLabels.count = width / self.horizontalLabelWidth
        self.horizontalAxisLabels.Rebuild()
        self.grid.count = numGridLines
        self.grid.step = gridLineStep
        self.grid.Rebuild()

    def ResizeGraphs(self):
        if self.isBuilding:
            return
        if not self.data:
            return
        self.isResizing = True
        self.AdjustForSize()
        self.isResizing = False

    def _OnSizeChange_NoBlock(self, width, height):
        self.ResizeGraphs()


class MemoryMonitor(uicontrols.Window):
    default_caption = 'Memory Monitor'
    default_minSize = (700, 400)
    default_windowID = 'MemoryMonitor'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.graph = MemoryGraph(parent=self.sr.main, align=uiconst.TOALL, padding=16)
        uthread2.StartTasklet(self.graph.UpdateGraph)
