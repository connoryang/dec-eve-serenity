#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerTooltip.py
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.sprite import Sprite
from carbonui.util.mouseTargetObject import MouseTargetObject
from eve.client.script.ui.control.eveBaseLink import BaseLink
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
import carbonui.const as uiconst
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracketTooltip import BracketTooltipSidePanel
import blue
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
import uthread
from carbonui.primitives.layoutGrid import LayoutGridRow, LayoutGrid
TOOLTIP_OPACITY = 0.8
MINENTRYHEIGHT = 26
SCROLL_THRESHOLD = 10

class MarkerTooltipWrapperBase(TooltipBaseWrapper):

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = MarkerTooltipBase(parent=parent, owner=owner, idx=idx)
        return self.tooltipPanel


class MarkerTooltipRowBase(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    mainLabel = None
    dynamicsUpdateTimer = None
    highlight = None
    isDragObject = True

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.markerObject = attributes.markerObject
        self.iconParent = Container(align=uiconst.CENTER, pos=(0,
         0,
         26,
         MINENTRYHEIGHT), parent=self)
        self.iconObj = self.CreateIcon()
        self.mainLabel = attributes.sideContainer.CreateBracketEntry()
        self.mainLabel.DelegateEvents(self)
        self.StartDynamicUpdates()

    def UpdateDynamicValues(self):
        self.mainLabel.text = self.markerObject.GetLabelText()
        self.iconParent.height = max(MINENTRYHEIGHT, self.mainLabel.height)

    def StartDynamicUpdates(self):
        self.UpdateDynamicValues()
        self.dynamicsUpdateTimer = AutoTimer(500, self.UpdateDynamicValues)

    def CreateIcon(self):
        return self.LoadIconFromMarkerObject()

    def LoadIconFromMarkerObject(self):
        self.iconObj = Sprite(state=uiconst.UI_DISABLED, pos=(0, 0, 16, 16), align=uiconst.CENTER, parent=self.iconParent, texturePath=self.markerObject.texturePath, color=self.markerObject.iconColor)
        return self.iconObj

    def Close(self, *args):
        LayoutGridRow.Close(self, *args)
        self.bracket = None
        self.mainLabel = None
        self.dynamicsUpdateTimer = None

    def SetHilited(self, hiliteState):
        if hiliteState:
            if self.highlight is None or self.highlight.destroyed:
                self.highlight = Fill(bgParent=self, color=(1, 1, 1, 0.0))
            self.highlight.opacity = 0.2
            if self.mainLabel:
                self.mainLabel.opacity = 1.5
        else:
            if self.highlight and not self.highlight.destroyed:
                self.highlight.opacity = 0.0
            if self.mainLabel:
                self.mainLabel.opacity = 0.8

    def OnClick(self, *args):
        return self.markerObject.OnClick(*args)

    def OnMouseDown(self, *args):
        return self.markerObject.OnMouseDown(self, *args)

    def OnMouseEnter(self, *args):
        self.SetHilited(True)
        uthread.new(self.WhileMouseOver)
        return self.markerObject.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        return self.markerObject.OnMouseExit(self, *args)

    def GetDragData(self, *args):
        return self.markerObject.GetDragData(self, *args)

    @classmethod
    def PrepareDrag(cls, *args):
        return BaseLink.PrepareDrag(*args)

    def WhileMouseOver(self):
        while uicore.uilib.mouseOver is self or uicore.uilib.mouseOver is self.mainLabel:
            blue.pyos.synchro.SleepWallclock(10)
            if self.destroyed:
                break

        self.SetHilited(False)

    def AlignContent(self, align = uiconst.TOLEFT):
        if align == uiconst.TOLEFT:
            self.mainLabel.align = uiconst.CENTERLEFT
        else:
            self.mainLabel.align = uiconst.CENTERRIGHT

    def GetMenu(self, *args):
        return self.markerObject.GetMenu()


class MarkerTooltipBase(TooltipPersistentPanel):
    sideContainer = None
    scroll = None
    loaded = False
    picktestEnabled = False

    def ApplyAttributes(self, attributes):
        TooltipPersistentPanel.ApplyAttributes(self, attributes)
        self.align = uiconst.ABSOLUTE
        self.rowsByItemIDs = {}
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEDOWN, self.OnGlobalMouseDown)
        MouseTargetObject(self)

    def Close(self, *args):
        TooltipPersistentPanel.Close(self, *args)
        self.overlappingMarkers = None
        self.rowsByItemIDs = None
        if self.sideContainer:
            self.sideContainer.Close()

    def CloseWithFade(self, *args):
        self.Close()

    def OnGlobalMouseDown(self, uiObject, *args, **kwds):
        if self.destroyed:
            return False
        if uiObject.IsUnder(self) or uiObject.IsUnder(uicore.layer.menu):
            return True
        if self.sideContainer and uiObject.IsUnder(self.sideContainer):
            return True
        self.CloseWithFade()
        return False

    def OnMouseEnter(self, *args):
        self.LoadEntries()

    def LoadTooltip(self, *args, **kwds):
        if self.owner.markerObject.markerHandler.IsMarkerPickOverridden():
            return
        sortList = []
        overlapMarkers = self.owner.markerObject.markerHandler.GetIntersectingMarkersForMarker(self.owner.markerObject)
        if overlapMarkers:
            for markerObject in overlapMarkers:
                if not markerObject.tooltipRowClass:
                    continue
                sortList.append((markerObject.GetOverlapSortValue(), markerObject))

        if len(sortList) == 1:
            return
        self.overlappingMarkers = sortList
        self.SetBackgroundAlpha(TOOLTIP_OPACITY)
        self.margin = 3
        scroll = ScrollContainer(align=uiconst.TOPLEFT, parent=self)
        scroll.isTabStop = False
        scroll.verticalScrollBar.align = uiconst.TORIGHT_NOPUSH
        scroll.verticalScrollBar.width = 3
        self.scroll = scroll
        subGrid = LayoutGrid(parent=scroll, align=uiconst.TOPLEFT, columns=1, name='markersTooltipSubGrid')
        self.subGrid = subGrid
        self.sideContainer = BracketTooltipSidePanel(align=uiconst.TOPLEFT, parent=self.parent, idx=self.parent.children.index(self))
        self.sideContainer.display = False
        uthread.new(self.UpdateSideContainer)
        self.LoadEntries()

    def LoadEntries(self):
        if self.loaded:
            return
        self.loaded = True
        self.subGrid.Flush()
        rowOrder = []
        for _sortValue, markerObject in sorted(self.overlappingMarkers, reverse=True):
            row = self.subGrid.AddRow(rowClass=markerObject.tooltipRowClass, markerObject=markerObject, sideContainer=self.sideContainer)
            self.rowsByItemIDs[markerObject.itemID] = row
            rowOrder.append(row)

        self.subGrid.RefreshGridLayout()
        self.scroll.width = self.subGrid.width + (5 if len(rowOrder) > SCROLL_THRESHOLD else 0)
        totalHeight = 0
        for row in rowOrder[:SCROLL_THRESHOLD]:
            totalHeight += row.height

        self.scroll.height = totalHeight
        self.state = uiconst.UI_NORMAL

    def UpdateSideContainer(self):
        rightAligned = (uiconst.POINT_RIGHT_1, uiconst.POINT_RIGHT_2, uiconst.POINT_RIGHT_3)
        while not self.destroyed:
            if not hasattr(self, 'menuPointFlag'):
                blue.pyos.synchro.SleepWallclock(1)
                self.scroll.ScrollToVertical(1.0)
                continue
            if self.menuPointFlag in rightAligned or self.left + self.width + self.sideContainer.width > uicore.desktop.width:
                self.sideContainer.SetContentAlign(uiconst.TORIGHT)
                self.sideContainer.left = self.left - self.sideContainer.width
                for row in self.rowsByItemIDs.values():
                    row.UpdateDynamicValues()

            else:
                self.sideContainer.SetContentAlign(uiconst.TOLEFT)
                self.sideContainer.left = self.left + self.width
            self.sideContainer.top = self.top
            self.sideContainer.height = self.height
            self.sideContainer.grid.top = self.scroll.mainCont.top
            self.sideContainer.opacity = self.opacity
            if self.beingDestroyed:
                self.sideContainer.display = False
            else:
                self.sideContainer.display = True
            blue.pyos.synchro.SleepWallclock(1)
