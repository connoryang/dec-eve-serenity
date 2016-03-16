#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\speedGauge.py
import sys
import math
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.mathUtil import DegToRad
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from localization import GetByLabel
import uthread
import telemetry
import blue
import log

class SpeedGauge(Container):
    default_name = 'SpeedGauge'
    default_width = 124
    default_height = 36
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.wantedspeed = None
        self.speedTimer = None
        self.speedInited = 0
        self.speedCircularPickParent = Container(name='speedCircularPickParent', parent=self, align=uiconst.CENTERBOTTOM, pos=(0, 0, 144, 144), pickRadius=72)
        self.speedGaugeParent = Container(parent=self.speedCircularPickParent, name='speedGaugeParent', pos=(0, 0, 124, 36), align=uiconst.CENTERBOTTOM, state=uiconst.UI_DISABLED, clipChildren=True)
        self.speedLabel = EveLabelSmall(name='speedLabel', parent=self.speedGaugeParent, color=Color.BLACK, align=uiconst.CENTER)
        Sprite(parent=self.speedCircularPickParent, name='speedoUnderlay', pos=(0, 48, 104, 44), align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/speedoUnderlay.png')
        self.speedNeedle = Transform(parent=self.speedGaugeParent, name='speedNeedle', pos=(-5, -38, 134, 12), align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN, rotationCenter=(0.5, 0.5))
        Sprite(parent=self.speedNeedle, name='needle', pos=(0, 0, 24, 12), align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ShipUI/heatGaugeNeedle.png')
        Sprite(parent=self.speedNeedle, name='speedGaugeSprite', texturePath='res:/UI/Texture/classes/ShipUI/speedoOverlay.png', pos=(-8, -73, 79, 79), state=uiconst.UI_DISABLED)
        self.speedTimer = uthread.new(self.UpdateSpeedThread)

    def OnClick(self, *args):
        uthread.new(self.controller.SetSpeed, self.GetCurrMouseSpeedPortion())

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric3ColumnTemplate()
        iconObj, labelObj, valueObj = tooltipPanel.AddIconLabelValue('ui_22_32_13', GetByLabel('Tooltips/Hud/CurrentSpeed'), '', iconSize=24)
        setattr(tooltipPanel, '_valueLabelSpeed', valueObj)
        tooltipPanel.AddSpacer(width=2, height=2)
        tooltipPanel._setSpeedValue = tooltipPanel.AddLabelMedium(colSpan=tooltipPanel.columns - 1, width=180)
        self._UpdateSpeedTooltip(tooltipPanel)
        self._speedTooltipUpdate = AutoTimer(10, self._UpdateSpeedTooltip, tooltipPanel)

    def _UpdateSpeedTooltip(self, tooltipPanel):
        if tooltipPanel.destroyed:
            self._speedTooltipUpdate = None
            return
        if not self.controller.IsLoaded():
            self._speedTooltipUpdate = None
            return
        if self.controller.IsInWarp():
            fmtSpeed = FmtDist(self.controller.GetSpeed(), 2)
            tooltipPanel._valueLabelSpeed.text = '%s/s' % fmtSpeed
            tooltipPanel._setSpeedValue.text = GetByLabel('UI/Inflight/CanNotChangeSpeedWhileWarping')
        else:
            fmtSpeed = self.controller.GetSpeedFormatted()
            tooltipPanel._valueLabelSpeed.text = fmtSpeed
            portion = self.GetCurrMouseSpeedPortion()
            speed = self.controller.GetSpeedAtFormatted(portion)
            tooltipPanel._setSpeedValue.text = GetByLabel('UI/Inflight/ClickToSetSpeedTo', speed=speed)

    def StopShip(self):
        self.controller.StopShip()

    @telemetry.ZONE_FUNCTION
    def UpdateSpeedThread(self):
        while not self.destroyed:
            blue.synchro.Sleep(20)
            try:
                if not self.controller.IsLoaded():
                    continue
                if not (self.controller.GetBall() and self.controller.GetBall().ballpark):
                    continue
                speedPortion = self.controller.GetSpeedPortion()
                self.speedNeedle.SetRotation(DegToRad(45.0 + 90.0 * speedPortion))
                if self.controller.IsInWarp():
                    fmtSpeed = GetByLabel('UI/Inflight/WarpSpeedNotification', warpingMessage=GetByLabel('UI/Inflight/Scanner/Warping'))
                else:
                    fmtSpeed = self.controller.GetSpeedFormatted()
                self.speedLabel.text = fmtSpeed
            except Exception as e:
                log.LogException(e)
                sys.exc_clear()

    def GetCurrMouseSpeedPortion(self):
        l, t, w, h = self.speedCircularPickParent.GetAbsolute()
        centerX = l + w / 2
        centerY = t + h / 2
        y = float(uicore.uilib.y - centerY)
        x = float(uicore.uilib.x - centerX)
        if x and y:
            angle = math.atan(x / y)
            deg = angle / math.pi * 180.0
            factor = (45.0 + deg) / 90.0
            if factor < 0.05:
                return 0.0
            elif factor > 0.95:
                return 1.0
            else:
                return factor
        return 0.5
