#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\capacitorContainer.py
from carbon.common.script.util.mathUtil import DegToRad
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from localization import GetByLabel
from localization.formatters.numericFormatters import FormatNumeric
import uthread
import random
import trinity
import blue
import telemetry
COLOR_ORANGE = (0.9375, 0.3515625, 0.1953125)
COLOR_DARK_ORANGE = (70 / 256.0, 26 / 256.0, 13.0 / 256.0)

class CapacitorContainer(Container):
    default_name = 'CapacitorContainer'
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_pickRadius = 30
    default_width = 60
    default_height = 60

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.powerBlink = None
        self.lastSetCapacitor = None
        self.controller = attributes.controller
        self.InitCapacitor()
        uthread.new(self.UpdateThread)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        tooltipPanel.margin = (6, 4, 8, 4)
        iconObj, labelObj, valueObj = tooltipPanel.AddIconLabelValue('ui_1_64_1', GetByLabel('Tooltips/Hud/Capacitor'), '', iconSize=40)
        valueObj.fontsize = 16
        valueObj.bold = True
        valueObj.top = -2
        setattr(tooltipPanel, 'labelCapacitor', labelObj)
        setattr(tooltipPanel, 'valueLabelCapacitor', valueObj)
        tooltipPanel.AddCell()
        f = Container(align=uiconst.TOPLEFT, width=100, height=1)
        tooltipPanel.AddCell(f, colSpan=2)
        self._UpdateCapacitorTooltip(tooltipPanel)
        self._capacitorTooltipUpdate = AutoTimer(10, self._UpdateCapacitorTooltip, tooltipPanel)

    def _UpdateCapacitorTooltip(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._capacitorTooltipUpdate = None
            return
        maxCap = self.controller.GetCapacitorCapacityMax()
        if maxCap is not None:
            if not self.controller.IsLoaded():
                self._capacitorTooltipUpdate = None
                return
            maxcap = self.controller.GetCapacitorCapacityMax()
            load = self.controller.GetCapacitorCapacity()
            portion = maxCap * max(0.0, min(1.0, maxcap and float(load / maxcap) or maxcap))
            if portion:
                capString = GetByLabel('Tooltips/Hud/Capacitor')
                capString += '<br>'
                capString += '%s / %s' % (FormatNumeric(portion, useGrouping=True, decimalPlaces=0), FormatNumeric(maxCap, useGrouping=True, decimalPlaces=0))
                tooltipPanel.labelCapacitor.text = capString
                value = portion / maxCap
                tooltipPanel.valueLabelCapacitor.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=value * 100)

    @telemetry.ZONE_FUNCTION
    def InitCapacitor(self):
        self.initialized = 0
        self.lastSetCapacitor = None
        self.AnimateCapacitorOut(self.children[:], 0.5)
        self.powerCells = []
        maxCap = self.controller.GetCapacitorCapacityMax()
        numcol = min(18, int(maxCap / 50))
        rotstep = 360.0 / max(1, numcol)
        colWidth = max(12, min(16, numcol and int(192 / numcol)))
        newColumns = []
        for i in range(numcol):
            powerColumn = Transform(parent=self, name='powerColumn', pos=(0,
             0,
             colWidth,
             56), align=uiconst.CENTER, state=uiconst.UI_DISABLED, rotation=DegToRad(i * -rotstep), idx=0)
            newColumns.append(powerColumn)
            for ci in xrange(4):
                newcell = Sprite(parent=powerColumn, name='pmark', pos=(0,
                 ci * 5,
                 10 - ci * 2,
                 7), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCell_2.png', color=(0, 0, 0, 0))
                self.powerCells.insert(0, newcell)

        self.AnimateCapacitorIn(newColumns, 1.0)
        self.initialized = 1

    def AnimateCapacitorOut(self, conts, duration):
        uthread.new(self.AnimateCapacitorOut_Thread, conts, duration)

    def AnimateCapacitorOut_Thread(self, conts, duration):
        for c in conts:
            uicore.animations.FadeOut(c, duration=0.1, timeOffset=random.random() * duration * 0.75)

        blue.synchro.Sleep(duration * 1000)
        for cont in conts:
            cont.Close()

    def AnimateCapacitorIn(self, containers, duration):
        for i, cont in enumerate(containers):
            cont.opacity = 0.0
            pos = float(i) / len(containers)
            uicore.animations.FadeIn(cont, duration=duration, timeOffset=duration + duration * pos, curveType=uiconst.ANIM_OVERSHOT)

    def UpdateThread(self):
        while not self.destroyed:
            blue.synchro.SleepWallclock(500)
            if self.controller.IsLoaded():
                self.Update()

    @telemetry.ZONE_FUNCTION
    def Update(self):
        load = self.controller.GetCapacitorCapacity()
        maxcap = self.controller.GetCapacitorCapacityMax()
        proportion = max(0.0, min(1.0, round(maxcap and load / maxcap or maxcap, 2)))
        if self.lastSetCapacitor == proportion:
            return
        sm.ScatterEvent('OnCapacitorChange', load, maxcap, proportion)
        good = trinity.TriColor(*COLOR_ORANGE)
        bad = trinity.TriColor(*COLOR_DARK_ORANGE)
        bad.Scale(1.0 - proportion)
        good.Scale(proportion)
        maxCap = self.controller.GetCapacitorCapacityMax()
        if maxCap is not None and self.initialized and self.powerCells:
            totalCells = len(self.powerCells)
            visible = max(0, min(totalCells, int(proportion * totalCells)))
            for ci, each in enumerate(self.powerCells):
                if ci >= visible:
                    each.SetRGB(0.5, 0.5, 0.5, 0.5)
                    each.glowColor = (0, 0, 0, 1)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 0)
                else:
                    each.SetRGB(0.125, 0.125, 0.125, 1)
                    each.glowColor = (bad.r + good.r,
                     bad.g + good.g,
                     bad.b + good.b,
                     1.0)
                    each.glowFactor = 0.0
                    each.glowExpand = 0.1
                    each.shadowOffset = (0, 1)

            if self.powerBlink is None:
                self.powerBlink = Sprite(parent=self, name='powerblink', state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/classes/ShipUI/capacitorCellGlow.png', align=uiconst.CENTERTOP, blendMode=trinity.TR2_SBM_ADDX2, color=COLOR_ORANGE)
                r, g, b = COLOR_ORANGE
                uicore.effect.BlinkSpriteRGB(self.powerBlink, r, g, b, 750, None)
            if visible != 0 and visible < totalCells:
                active = self.powerCells[visible - 1]
                self.powerBlink.SetParent(active.parent, 0)
                self.powerBlink.top = active.top
                self.powerBlink.width = active.width + 3
                self.powerBlink.height = active.height
                self.powerBlink.state = uiconst.UI_DISABLED
            else:
                self.powerBlink.state = uiconst.UI_HIDDEN
            self.lastSetCapacitor = proportion

    def GetMenu(self):
        return self.controller.GetMenu()
