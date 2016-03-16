#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\fittingLayout.py
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor, GetBaseShapeSize
import mathUtil
from localization import GetByLabel
import trinity
import uiprimitives
import telemetry

class FittingLayoutGhost(uiprimitives.Container):
    default_name = 'fittingBase'
    default_width = 640
    default_height = 640
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.scaleFactor = GetScaleFactor()
        self.baseShapeSize = GetBaseShapeSize()
        self.width = self.baseShapeSize
        self.height = self.baseShapeSize
        overlay = uiprimitives.Sprite(parent=self, name='overlay', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_overlay.png', color=(1.0, 1.0, 1.0, 0.39))
        radius = int(self.baseShapeSize * 0.885 / 2)
        self.calibrationGauge = CalibrationGauge(parent=self, radius=radius)
        self.powerGauge = PowergridGauge(parent=self, radius=radius)
        self.cpuGauge = CPUGauge(parent=self, radius=radius)
        baseDOT = uiprimitives.Sprite(parent=self, name='baseDOT', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_dotproduct.png', spriteEffect=trinity.TR2_SFX_DOT, blendMode=trinity.TR2_SBM_ADD)
        self.sr.baseColor = SpriteThemeColored(parent=self, name='baseColor', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase_basecircle.png', colorType=uiconst.COLORTYPE_UIBASE)
        self.sr.baseShape = uiprimitives.Sprite(parent=self, name='baseShape', align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Fitting/fittingbase.png', color=(0.0, 0.0, 0.0, 0.86))


class FittingGauge(GaugeCircular):
    gaugeRange = 45
    default_align = uiconst.CENTER
    default_state = uiconst.UI_PICKCHILDREN
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_colorBg = (1.0, 1.0, 1.0, 0.0)
    default_lineWidth = 11.0
    hintPath = ''

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        GaugeCircular.ApplyAttributes(self, attributes)
        self.gauge.OnMouseMove = self.OnMouseMove
        self.bgGauge.OnMouseMove = self.OnMouseMove
        self.gauge.GetTooltipPosition = self.GetTooltipPosition
        self.bgGauge.GetTooltipPosition = self.GetTooltipPosition
        self.currentValue = 0

    def SetValue(self, value, animate = True):
        if value > 1.0:
            uicore.animations.FadeTo(self, 0.25, 1.0, duration=0.5, loops=uiconst.ANIM_REPEAT)
        else:
            uicore.animations.FadeIn(self, duration=0.5)
        value = min(1.0, max(0.0, value))
        self.currentValue = 100 * value
        value *= self.gaugeRange / 360.0
        GaugeCircular.SetValue(self, value)

    def OnMouseMove(self, *args):
        value = FmtAmt(self.currentValue, showFraction=2)
        hintText = GetByLabel(self.hintPath, state=value)
        self.gauge.hint = hintText
        self.bgGauge.hint = hintText

    def GetTooltipPosition(self):
        return (uicore.uilib.x - 5,
         uicore.uilib.y - 5,
         10,
         10)


class PowergridGauge(FittingGauge):
    gaugeRange = 45
    default_name = 'powergridGauge'
    default_colorStart = (0.40625, 0.078125, 0.03125, 0.8)
    default_colorEnd = (0.40625, 0.078125, 0.03125, 0.8)
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_startAngle = mathUtil.DegToRad(45)
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/PowerGridState'


class CPUGauge(FittingGauge):
    gaugeRange = 45
    default_name = 'cpuGauge'
    default_colorStart = (0.203125, 0.3828125, 0.37890625, 0.8)
    default_colorEnd = (0.203125, 0.3828125, 0.37890625, 0.8)
    default_colorMarker = (1.0, 1.0, 1.0, 0.0)
    default_startAngle = mathUtil.DegToRad(135)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/CpuState'


class CalibrationGauge(FittingGauge):
    gaugeRange = 31
    default_name = 'calibrationGauge'
    default_colorStart = (0.29296875, 0.328125, 0.33984375, 0.8)
    default_colorEnd = (0.29296875, 0.328125, 0.33984375, 0.8)
    default_startAngle = mathUtil.DegToRad(317)
    default_clockwise = False
    default_bgPortion = gaugeRange / 360.0
    hintPath = 'UI/Fitting/FittingWindow/CalibrationState'
