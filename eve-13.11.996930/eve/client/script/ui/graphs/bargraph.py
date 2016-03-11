#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\graphs\bargraph.py
import carbonui.const as uiconst
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.graphs import PrimeGraphData

class BarGraphBarBase(Container):
    __notifyevents__ = ['OnUIScalingChange']
    default_name = 'BarGraphBarBase'
    default_align = uiconst.TOPLEFT
    default_width = 128
    default_height = 6
    default_state = uiconst.UI_PICKCHILDREN
    default_bgColor = (0.0, 0.0, 0.0, 0.25)
    overlayMarkers = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.segments = []
        self.graphData = None
        sm.RegisterNotify(self)

    def LoadGraphData(self, graphData, animateIn = True):
        self.graphData = PrimeGraphData(graphData)
        self.ReloadGraph(animateIn=animateIn)

    def UpdateGraphData(self, graphData, animate = True):
        self.graphData = PrimeGraphData(graphData)
        for i, segmentParams in enumerate(self.graphData):
            graphSegment = self.segments[i]
            graphSegment.color = segmentParams.color
            graphSegment.hint = segmentParams.tooltip
            graphSegment.pickState = bool(segmentParams.tooltip)
            graphSegment.sizeFactor = segmentParams.sizeFactor
            if segmentParams.showMarker:
                graphSegment.ShowPointer()
            else:
                graphSegment.HidePointer()
            proportion = segmentParams.proportion
            proportion = min(1.0, max(0.0, proportion))
            if animate:
                uicore.animations.MorphScalar(graphSegment, 'segmentSize', startVal=graphSegment.segmentSize, endVal=proportion, curveType=uiconst.ANIM_SMOOTH, duration=0.5)
            else:
                graphSegment.segmentSize = proportion

    def ReloadGraph(self, animateIn = False):
        for each in self.segments:
            each.Close()

        self.segments = []
        if not self.graphData:
            return
        for i, segmentParams in enumerate(self.graphData):
            graphSegment = self.CreateGraphSegment(segmentParams.color)
            self.segments.append(graphSegment)

        self.UpdateGraphData(self.graphData, animateIn)

    def CreateGraphSegment(self, color):
        segment = BarSegmentFill(name='barSegment', parent=self, align=uiconst.NOALIGN, color=color, state=uiconst.UI_NORMAL, segmentAlignment=self.segmentAlignment)
        return segment

    def OnUIScalingChange(self, *args):
        self.ReloadGraph()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        ret = Container.UpdateAlignment(self, budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        self.UpdateSegments()
        return ret

    def UpdateSegments(self):
        displayWidth = self.displayWidth
        displayHeight = self.displayHeight
        p = 0.0
        for each in self.segments:
            if self.segmentAlignment == uiconst.TOLEFT_PROP:
                w = displayWidth * each.width
                each.displayRect = (p,
                 0,
                 w,
                 displayHeight * each.sizeFactor)
                p += w
            else:
                h = displayHeight * each.height
                each.displayRect = (0,
                 p,
                 displayWidth * each.sizeFactor,
                 h)
                p += h


class BarSegmentFill(Fill):
    sizeFactor = 1.0
    pointer = None
    _segmentSize = 0.0

    def ApplyAttributes(self, attributes):
        Fill.ApplyAttributes(self, attributes)
        self.segmentAlignment = attributes.segmentAlignment

    @apply
    def segmentSize():

        def fget(self):
            return self._segmentSize

        def fset(self, value):
            self._segmentSize = value
            if self.segmentAlignment == uiconst.TOLEFT_PROP:
                self.width = value
            elif self.segmentAlignment == uiconst.TOBOTTOM_PROP:
                self.height = value

        return property(**locals())

    def ShowPointer(self):
        if self.pointer is None:
            self.pointer = Sprite(parent=self.parent, texturePath='res:/UI/Texture/classes/Graph/barPointer.png', state=uiconst.UI_DISABLED, pos=(0, 0, 15, 15), idx=0)
            self.pointer.display = False

    def HidePointer(self):
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
            self.pointer = None

    def UpdatePointer(self):
        if not self.pointer:
            return
        displayX, displayY, displayWidth, displayHeight = self.displayRect
        if self.segmentAlignment == uiconst.TOLEFT_PROP:
            self.pointer.left = ReverseScaleDpi(displayX + displayWidth / 2) - self.pointer.width / 2
            self.pointer.top = -self.pointer.height / 2
        else:
            self.pointer.left = ReverseScaleDpi(self.parent.displayWidth) - self.pointer.width / 2
            self.pointer.top = ReverseScaleDpi(displayY + displayHeight / 2) - self.pointer.height / 2
        self.pointer.display = True

    def Close(self, *args):
        Fill.Close(self, *args)
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
            self.pointer = None

    @apply
    def displayRect():

        def fget(self):
            return (self._displayX,
             self._displayY,
             self._displayWidth,
             self._displayHeight)

        def fset(self, value):
            displayX, displayY, displayWidth, displayHeight = value
            self._displayX = displayX
            self._displayY = displayY
            self._displayWidth = displayWidth
            self._displayHeight = displayHeight
            ro = self.renderObject
            if ro:
                ro.displayX = self._displayX
                ro.displayY = self._displayY
                ro.displayWidth = self._displayWidth
                ro.displayHeight = self._displayHeight
            self.UpdatePointer()

        return property(**locals())

    def GetAbsoluteSize(self):
        return (ReverseScaleDpi(self.displayWidth), ReverseScaleDpi(self.displayHeight))


class BarGraphBarHorizontal(BarGraphBarBase):
    segmentAlignment = uiconst.TOLEFT_PROP
    default_width = 128
    default_height = 6


class BarGraphBarVertical(BarGraphBarBase):
    segmentAlignment = uiconst.TOBOTTOM_PROP
    default_width = 6
    default_height = 128


class BarGraphHorizontal(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.barClass = attributes.Get('barClass', BarGraphBarHorizontal)
        self.barPadding = attributes.Get('barPadding', (0, 2, 0, 2))
        self.barSize = attributes.Get('barPadding', 6)
        self.bars = []

    def LoadGraphData(self, graphData, animateIn = True):
        self.graphData = graphData
        self.ReloadGraph(animateIn=animateIn)

    def UpdateGraphData(self, graphData, animate = True):
        self.graphData = graphData
        for i, graphData in enumerate(self.graphData):
            graphBar = self.bars[i]
            graphBar.UpdateGraphData(graphData, animate)

    def ReloadGraph(self, animateIn = False):
        for each in self.bars:
            each.Close()

        self.bars = []
        if not self.graphData:
            return
        if self.barClass is BarGraphBarHorizontal:
            barAlign = uiconst.TOTOP
            width = 0
            height = self.barSize
        else:
            barAlign = uiconst.TOLEFT
            width = self.barSize
            height = 0
        for i, graphData in enumerate(self.graphData):
            graphBar = self.barClass(parent=self, align=barAlign, width=width, height=height, padding=self.barPadding)
            self.bars.append(graphBar)
            graphBar.LoadGraphData(graphData, animateIn)
