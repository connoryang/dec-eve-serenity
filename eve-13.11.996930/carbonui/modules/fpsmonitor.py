#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\modules\fpsmonitor.py
import blue
import trinity
import uthread
import carbonui.const as uiconst
from carbonui.primitives.gridcontainer import GridContainer
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.control.window import WindowCoreOverride as Window
from carbonui.control.label import LabelOverride as Label

class GraphRenderer(Base):
    __renderObject__ = trinity.Tr2Sprite2dRenderJob

    def ApplyAttributes(self, attributes):
        Base.ApplyAttributes(self, attributes)
        self.viewport = trinity.TriViewport()
        self.linegraph = trinity.Tr2LineGraph()
        self.linegraphSize = 0
        self.linegraph.name = 'FPS'
        self.linegraph.color = (0.9, 0.9, 0.9, 1)
        blue.statistics.SetAccumulator(self.linegraph.name, self.linegraph)
        self.renderJob = trinity.CreateRenderJob('Graphs')
        self.renderObject.renderJob = self.renderJob
        self.renderJob.PythonCB(self.AdjustViewport)
        self.renderJob.SetViewport(self.viewport)
        self.renderJob.SetStdRndStates(trinity.RM_SPRITE2D)
        self.renderer = self.renderJob.RenderLineGraph()
        self.renderer.showLegend = False
        self.renderer.lineGraphs.append(self.linegraph)

    def Close(self):
        Base.Close(self)
        self.renderer.scaleChangeCallback = None

    def AdjustViewport(self):
        l, t = self.displayX, self.displayY
        parent = self.GetParent()
        while parent:
            l += parent.displayX
            t += parent.displayY
            parent = parent.GetParent()

        self.viewport.x = l
        self.viewport.y = t
        self.viewport.width = self._displayWidth
        self.viewport.height = self._displayHeight
        if self.linegraphSize != self._displayWidth:
            self.linegraph.SetSize(self._displayWidth)
            self.linegraphSize = self._displayWidth


class FpsMonitor(Window):
    __guid__ = 'uicls.FpsMonitor'
    default_caption = 'FPS Monitor'
    default_windowID = 'fpsMonitor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(4)
        self.fpsStat = blue.statistics.Find('FPS')
        self.frameTimeStat = blue.statistics.Find('Trinity/SmoothedFrameTime')
        self.fpsLabel = Label(parent=self.sr.main, left=4, width=160, fontsize=18)
        adapterInfo = trinity.adapters.GetAdapterInfo(trinity.device.adapter)
        info = '%s / %s / %s' % (trinity.platform, adapterInfo.description, trinity.GetShaderModel())
        self.platformLabel = Label(parent=self.sr.main, align=uiconst.TOBOTTOM, padding=4, fontsize=12, text=info)
        self.toggleDisplayResults = False
        self.legendContainer = GridContainer(parent=self.sr.main, align=uiconst.TORIGHT, width=28, columns=1, padRight=4, padBottom=4)
        self.labels = []
        for i in xrange(4):
            label = Label(parent=self.legendContainer, align=uiconst.TOTOP, width=20, top=-4)
            self.labels.append(label)

        graphContainer = Container(parent=self.sr.main, align=uiconst.TOALL, padLeft=4, padRight=4, padBottom=4)
        gr = GraphRenderer(parent=graphContainer, align=uiconst.TOALL)
        self.renderer = gr.renderer
        self.renderer.scaleChangeCallback = self.ScaleChangeHandler
        uthread.new(self.UpdateFpsLabel)

    def ScaleChangeHandler(self):
        numLabels = len(self.labels)
        label = 1.0
        labelStep = 1.0 / float(numLabels)
        for i in xrange(numLabels):
            labelValue = int((label / self.renderer.scale * self.renderer.legendScale + 0.5) / 100)
            self.labels[i].SetText(str(labelValue))
            label -= labelStep

    def UpdateFpsLabel(self):
        while not self.destroyed:
            self.fpsLabel.text = '%6.2f (%5.1fms)' % (self.fpsStat.value / 100.0, self.frameTimeStat.value * 1000.0)
            blue.synchro.SleepWallclock(500)
