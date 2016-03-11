#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerListEntries.py
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.scrollentries import SE_BaseClassCore
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold, EveLabelMedium
from eve.client.script.ui.graphs.bargraph import BarGraphBarHorizontal
import localization
import evetypes
import blue

class NoScanProbesEntry(SE_BaseClassCore):

    def Startup(self, *args):
        self.label = EveLabelMedium(parent=self, text=localization.GetByLabel('UI/Inflight/Scanner/NoProbesDeployed'), bold=True, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=20)

    def Load(self, node):
        pass

    def GetHeight(self, *args):
        node, width = args
        node.height = 22
        return node.height


class ScanProbeEntryNew(SE_BaseClassCore):

    def Startup(self, *args):
        self.icon = Icon(parent=self, pos=(1, 0, 24, 24), align=uiconst.CENTERLEFT)
        self.labelLeft = EveLabelMedium(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=26)
        self.probeExpiry = EveLabelMediumBold(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=66)
        self.probeScanRange = EveLabelMediumBold(parent=self, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, left=6)

    def Load(self, node):
        if node.Get('selectable', 1) and node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        probeName = sm.GetService('scanSvc').GetProbeLabel(node.probe.probeID)
        self.labelLeft.text = probeName
        self.icon.LoadIconByTypeID(node.probe.typeID, ignoreSize=True)
        self.icon.hint = evetypes.GetName(node.probe.typeID)
        self.UpdateProbeState()
        self.updateStateTimer = AutoTimer(500, self.UpdateProbeState)

    def UpdateProbeState(self):
        if self.destroyed:
            self.updateStateTimer = None
            return
        probe = self.sr.node.probe
        if probe.expiry is None:
            expiryText = localization.GetByLabel('UI/Generic/None')
        else:
            expiry = max(0L, long(probe.expiry) - blue.os.GetSimTime())
            if expiry <= 0:
                expiryText = localization.GetByLabel('UI/Inflight/Scanner/Expired')
            elif expiry >= const.MIN:
                expiryText = localization.formatters.FormatTimeIntervalShortWritten(expiry, showFrom='day', showTo='minute')
            else:
                expiryText = localization.formatters.FormatTimeIntervalShortWritten(expiry, showFrom='day', showTo='second')
        self.probeExpiry.text = expiryText
        if probe.state == const.probeStateInactive:
            self.opacity = 0.5
        else:
            self.opacity = 1.0
        if probe.scanRange < const.AU:
            probeScanRangeText = FmtDist(probe.scanRange, maxdemicals=2)
        else:
            probeScanRangeText = FmtDist(probe.scanRange, maxdemicals=0)
        self.probeScanRange.text = probeScanRangeText

    def OnDblClick(self, *args):
        sm.ScatterEvent('OnProbeScanner_FocusOnProbe', self.sr.node.probeID)

    def GetHeight(self, *args):
        node, width = args
        node.height = 26
        return node.height

    def OnMouseEnter(self, *args):
        SE_BaseClassCore.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnProbeScanner_ProbeEntryMouseEnter', self.sr.node.probeID)

    def OnMouseExit(self, *args):
        SE_BaseClassCore.OnMouseExit(self, *args)
        sm.ScatterEvent('OnProbeScanner_ProbeEntryMouseExit', self.sr.node.probeID)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        if getattr(self, 'itemID', None) or getattr(self, 'typeID', None):
            return sm.GetService('menu').GetMenuFormItemIDTypeID(getattr(self, 'itemID', None), getattr(self, 'typeID', None))
        return []


class ScanResultNew(BaseListEntryCustomColumns):
    redHi = (0.8, 0.0, 0.0, 0.9)
    red = (0.5, 0.0, 0.0, 0.9)
    redLo = (0.3, 0.0, 0.0, 0.9)
    orangeHi = (0.8, 0.5, 0.0, 0.9)
    orange = (0.5, 0.3, 0.0, 0.9)
    orangeLo = (0.3, 0.2, 0.0, 0.9)
    greenHi = (0.0, 0.7, 0.0, 0.9)
    green = (0.0, 0.4, 0.0, 0.9)
    greenLo = (0.0, 0.2, 0.0, 0.9)
    warpButton = None

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.columnContainer = Container(align=uiconst.TOALL, parent=self)
        self.signalColumn = Container(align=uiconst.TORIGHT, parent=self.columnContainer, clipChildren=True, width=50)
        self.signalColumn.label = EveLabelMedium(parent=self.signalColumn, align=uiconst.CENTERRIGHT, left=6)
        self.pushColumnContainer = Container(align=uiconst.TOALL, parent=self.columnContainer, clipChildren=True)
        self.distanceColumn = self.AddColumn(textAlign=uiconst.CENTERRIGHT)
        self.idColumn = self.AddColumn()
        self.nameColumn = self.AddColumn()
        self.groupColumn = self.AddColumn()
        self.groupColumn.align = uiconst.TOALL
        self.columns.append(self.signalColumn)
        self.statusBar = BarGraphBarHorizontal(parent=self, align=uiconst.TOBOTTOM_NOPUSH, pos=(0, 0, 0, 2), bgColor=(0, 0, 0, 0), state=uiconst.UI_DISABLED)

    def AddColumn(self, textAlign = None):
        column = Container(align=uiconst.TOLEFT, parent=self.pushColumnContainer, clipChildren=True, padRight=1)
        self.columns.append(column)
        column.label = EveLabelMedium(parent=column, align=textAlign or uiconst.CENTERLEFT, left=6)
        return column

    def Load(self, node):
        if node.selected:
            self.Select()
        else:
            self.Deselect()
        newResult = False
        if hasattr(node, 'newResult'):
            if node.newResult:
                newResult = True
        normalColor, hiColor, loColor = self.red, self.redHi, self.redLo
        if 0.25 < node.result.certainty <= 0.75:
            normalColor, hiColor, loColor = self.orange, self.orangeHi, self.orangeLo
        if node.result.certainty > 0.75:
            normalColor, hiColor, loColor = self.green, self.greenHi, self.greenLo
        newCert = node.result.certainty
        oldCert = node.result.prevCertainty
        certChange = newCert - oldCert
        signalText = ''
        from eve.client.script.ui.control.entries import IsResultWithinWarpDistance
        if node.result.isPerfect and IsResultWithinWarpDistance(node.result):
            if not self.warpButton:
                self.warpButton = ButtonIcon(name='warpButton', func=self.WarpToAction, parent=self.signalColumn, align=uiconst.CENTERRIGHT, width=22, left=6, iconSize=22, texturePath='res:/UI/Texture/Icons/44_32_18.png', hint=localization.GetByLabel('UI/Commands/WarpTo'))
                if newResult:
                    uicore.animations.SpGlowFadeIn(self.warpButton.icon, glowFactor=1, glowColor=(0.8, 0.8, 0.8, 0.6), glowExpand=0, duration=1, loops=3)
        else:
            signalText = localization.GetByLabel('UI/Common/Percentage', percentage=newCert * 100)
        if newCert or oldCert:
            if certChange > 0:
                baseProportion = oldCert
                changeProportion = certChange
                changeColor = hiColor
            else:
                changeProportion = min(newCert, abs(certChange))
                baseProportion = max(0.0, newCert - changeProportion)
                changeColor = loColor
            graphData = []
            graphData.append(('base', baseProportion, normalColor))
            graphData.append(('change', changeProportion, changeColor))
            self.statusBar.LoadGraphData(graphData, animateIn=True)
        self.distanceColumn.label.text = FmtDist(node.distance)
        self.idColumn.label.text = node.result.id
        self.nameColumn.label.text = node.displayName
        self.groupColumn.label.text = node.groupName
        self.signalColumn.label.text = signalText
        if newResult:
            node.newResult = False
        self.OnColumnResize(node.columnWidths)

    def WarpToAction(self, *args):
        sm.GetService('menu').WarpToScanResult(self.sr.node.result.id)

    def GetHeight(self, *args):
        node, width = args
        node.height = 24
        return node.height

    def OnMouseEnter(self, *args):
        BaseListEntryCustomColumns.OnMouseEnter(self, *args)
        sm.ScatterEvent('OnProbeScanner_ScanResultMouseEnter', self.sr.node.result)

    def OnMouseExit(self, *args):
        BaseListEntryCustomColumns.OnMouseExit(self, *args)
        sm.ScatterEvent('OnProbeScanner_ScanResultMouseExit', self.sr.node.result)

    def OnDblClick(self, *args):
        BaseListEntryCustomColumns.OnDblClick(self, *args)
        sm.ScatterEvent('OnProbeScanner_FocusOnResult', self.sr.node.result)

    def GetMenu(self):
        if self.sr.node and self.sr.node.Get('GetMenu', None):
            return self.sr.node.GetMenu(self)
        return []

    def OnColumnResize(self, newCols):
        for i, width in enumerate(newCols):
            if self.columns[i].align != uiconst.TOALL:
                self.columns[i].width = width - 1

    @classmethod
    def GetCopyData(cls, node):
        return '<t>'.join([node.result.id,
         node.scanGroupName,
         node.groupName,
         node.typeName,
         localization.GetByLabel('UI/Common/Percentage', percentage=node.result.certainty * 100),
         FmtDist(node.distance)])

    @staticmethod
    def GetDefaultColumnAndDirection():
        return (localization.GetByLabel('UI/Common/ID'), True)

    @staticmethod
    def GetFixedColumns():
        return {localization.GetByLabel('UI/Inflight/Scanner/SignalStrength'): 60}

    @staticmethod
    def GetRightAlignedColumns():
        return [localization.GetByLabel('UI/Inflight/Scanner/SignalStrength')]

    @staticmethod
    def GetColumns():
        return [localization.GetByLabel('UI/Common/Distance'),
         localization.GetByLabel('UI/Common/ID'),
         localization.GetByLabel('UI/Common/Name'),
         localization.GetByLabel('UI/Common/Group'),
         localization.GetByLabel('UI/Inflight/Scanner/SignalStrength')]

    @staticmethod
    def GetStretchColumns():
        return [localization.GetByLabel('UI/Common/Group')]

    @staticmethod
    def GetColumnsMinSize():
        return {localization.GetByLabel('UI/Common/Distance'): 70,
         localization.GetByLabel('UI/Common/ID'): 60,
         localization.GetByLabel('UI/Common/Name'): 100,
         localization.GetByLabel('UI/Common/Group'): 100}

    @staticmethod
    def GetColumnsDefaultSize():
        return ScanResultNew.GetColumnsMinSize()
