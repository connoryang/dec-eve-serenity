#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\graphs\circulargraph.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
import math
import geo2
import blue
from eve.client.script.ui.graphs import PrimeGraphData

class CircularGraph(Container):
    __notifyevents__ = ['OnUIScalingChange']
    default_name = 'CircularGraph'
    default_radius = 32
    default_lineWidth = 4.0
    default_bgLineWidth = default_lineWidth + 1.0
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_PICKCHILDREN
    default_colorBg = (0.0, 0.0, 0.0, 0.25)
    default_startAngle = -math.pi / 2
    backgroundLine = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.radius = attributes.Get('radius', self.default_radius)
        self.lineWidth = attributes.Get('lineWidth', self.default_lineWidth)
        self.bgLineWidth = attributes.Get('bgLineWidth', self.default_bgLineWidth)
        self.startAngle = attributes.Get('startAngle', self.default_startAngle)
        self.colorBg = attributes.Get('colorBg', self.default_colorBg)
        self.width = self.height = self.radius * 2
        self.pickRadius = self.radius
        self.segments = []
        self.pointers = set()
        self.graphData = None
        sm.RegisterNotify(self)

    def LoadGraphData(self, graphData, animateIn = True):
        self.graphData = PrimeGraphData(graphData)
        self.ReloadGraph(animateIn=animateIn)

    def UpdateGraphData(self, graphData, animate = True):
        self.graphData = PrimeGraphData(graphData)
        position = 0.0
        for i, segmentParams in enumerate(self.graphData):
            segmentLine = self.segments[i]
            segmentLine.color = segmentParams.color
            segmentLine.hint = segmentParams.tooltip
            if segmentParams.showMarker:
                segmentLine.ShowPointer()
                self.pointers.add(segmentLine.pointer)
            else:
                pointer = getattr(segmentLine, 'pointer', None)
                if pointer and pointer in self.pointers:
                    self.pointers.remove(pointer)
                segmentLine.HidePointer()
            proportion = segmentParams.proportion
            proportion = max(0.0, proportion)
            endPosition = min(1.0, position + proportion)
            if animate:
                uicore.animations.MorphScalar(segmentLine, 'start', startVal=segmentLine.start, endVal=position, curveType=uiconst.ANIM_SMOOTH, duration=0.5)
                uicore.animations.MorphScalar(segmentLine, 'end', startVal=segmentLine.end, endVal=endPosition, curveType=uiconst.ANIM_SMOOTH, duration=0.5)
            else:
                segmentLine.start = position
                segmentLine.end = endPosition
            position = endPosition

    def ReloadGraph(self, animateIn = False):
        for each in self.segments:
            each.Close()

        for each in self.pointers:
            each.Close()

        if self.backgroundLine:
            self.backgroundLine.Close()
        self.backgroundLine = None
        self.segments = []
        self.pointers = set()
        if not self.graphData:
            return
        for i, segmentParams in enumerate(self.graphData):
            segmentLine = self.CreateLineTrace(segmentParams.color, self.lineWidth * segmentParams.sizeFactor)
            self.segments.append(segmentLine)

        self.UpdateGraphData(self.graphData, animateIn)
        self.width = self.radius * 2
        self.height = self.radius * 2
        if self.colorBg:
            bgLine = self.CreateLineTrace(self.colorBg, self.bgLineWidth)
            bgLine.end = 1.0
            bgLine.state = uiconst.UI_DISABLED
            self.backgroundLine = bgLine

    def CreateLineTrace(self, color, lineWidth):
        graphSize = self.radius * 2
        line = CircularGraphSegment(name='segmentline', parent=self, lineWidth=lineWidth, width=graphSize, height=graphSize, color=color, state=uiconst.UI_NORMAL)
        line.end = 0.0
        halfLine = lineWidth / 2.0
        plotRadius = self.radius - halfLine
        numPoints = min(256, max(32, int(math.pi * plotRadius)))
        stepSize = 2 * math.pi / numPoints
        angle = self.startAngle
        for i in xrange(numPoints + 1):
            x = plotRadius * math.cos(angle) + self.radius
            y = plotRadius * math.sin(angle) + self.radius
            line.AddPoint((x, y), (1.0, 1.0, 1.0, 1.0))
            angle += stepSize

        return line

    def OnUIScalingChange(self, *args):
        self.ReloadGraph()


class CircularGraphSegment(VectorLineTrace):
    sizeFactor = 1.0
    pointer = None

    def ShowPointer(self):
        if self.pointer is None:
            self.pointer = Sprite(parent=self.parent, texturePath='res:/UI/Texture/classes/Graph/barPointer.png', pos=(0, 0, 15, 15), state=uiconst.UI_DISABLED, idx=0)
            self.UpdatePointer()

    def HidePointer(self):
        if self.pointer and not self.pointer.destroyed:
            self.pointer.Close()
            self.pointer = None

    def UpdatePointer(self):
        if not self.pointer:
            return
        x, y, angle = self.GetOuterCenterPointAndAngle()
        self.pointer.left = x - self.pointer.width / 2
        self.pointer.top = y - self.pointer.height / 2
        self.pointer.rotation = math.pi * 2 - angle

    def GetOuterCenterPointAndAngle(self):
        centerProportion = self.start + (self.end - self.start) / 2
        angle = centerProportion * math.pi * 2
        radius = self.width / 2
        x = radius * (1.0 + math.cos(angle + math.pi / 2))
        y = radius * (1.0 + math.sin(angle + math.pi / 2))
        return (self.width - x, self.height - y, angle)

    @apply
    def start():
        doc = '\n        Where to start drawing the line, as a proportion of the length of\n        the line path. Defaults to 0 to start at the start of the path.\n        '
        fget = VectorLineTrace.start.fget

        def fset(self, value):
            VectorLineTrace.start.fset(self, value)
            self.UpdatePointer()

        return property(**locals())

    @apply
    def end():
        doc = '\n        Where to stop drawing the line, as a proportion of the length of\n        the line path. Defaults to 1 to stop at the end of the path.\n        '
        fget = VectorLineTrace.end.fget

        def fset(self, value):
            VectorLineTrace.end.fset(self, value)
            self.UpdatePointer()

        return property(**locals())

    def GetTooltipPosition(self):
        xp, yp = self.GetAbsolutePosition()
        x, y, angle = self.GetOuterCenterPointAndAngle()
        return (x + xp,
         y + yp,
         0,
         0)

    def GetTooltipPointer(self):
        x, y, angle = self.GetOuterCenterPointAndAngle()
        x = x - self.width / 2
        y = y - self.height / 2
        if y > 0:
            if x > 0:
                return uiconst.POINT_TOPLEFT
            else:
                return uiconst.POINT_TOPRIGHT
        else:
            if x > 0:
                return uiconst.POINT_BOTTOMLEFT
            return uiconst.POINT_BOTTOMRIGHT
        return uiconst.POINT_TOP_2
