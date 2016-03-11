#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\ui\entosisTimer.py
import math
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
import carbonui.const as uiconst
import trinity
ARROW_TEXTURE_WIDTH = 15
LINE_WIDTH = 3
WHITE_COLOR = (1.0, 1.0, 1.0, 1.0)
NO_COLOR = (0.0, 0.0, 0.0, 0.0)

class EntosisTimer(GaugeCircular):
    default_radius = 20
    default_lineWidth = LINE_WIDTH
    default_align = uiconst.CENTER
    default_state = uiconst.UI_DISABLED
    default_colorStart = WHITE_COLOR
    default_colorEnd = WHITE_COLOR
    default_colorBg = WHITE_COLOR
    default_autoUpdate = False
    default_moveMarker = True
    default_name = 'entosisTimer'
    stalemateTextureWidth = 18
    gaugeArrowRightTexturePath = 'res:/UI/Texture/classes/Sov/gauge_arrow_right.png'
    gaugeArrowLeftTexturePath = 'res:/UI/Texture/classes/Sov/gauge_arrow_left.png'
    gaugeStalemateTexturePath = 'res:/UI/Texture/classes/Sov/gauge_arrow_stop.png'

    def ApplyAttributes(self, attributes):
        attributes['useRealTime'] = False
        GaugeCircular.ApplyAttributes(self, attributes)
        radius = attributes.get('radius', self.default_radius)
        self.animatedGauge = GaugeCircular(parent=self, name='animatedGauge', radius=radius, lineWidth=LINE_WIDTH, showMarker=False, colorStart=WHITE_COLOR, colorEnd=WHITE_COLOR, colorBg=NO_COLOR, state=uiconst.UI_DISABLED, idx=0, useRealTime=False)
        self.stalemateTextureWidth = 2 * math.pi * radius / 7
        self.SetAnimatedGaugeTexture(self.gaugeArrowRightTexturePath, ARROW_TEXTURE_WIDTH)
        self.animatedGauge.gauge.spriteEffect = trinity.TR2_SFX_COPY
        self.animatedGauge.gauge.texture.useTransform = True

    def SetAnimatedGaugeTexture(self, gaugeTexturePath, textureWidth):
        self.animatedGauge.gauge.texturePath = gaugeTexturePath
        self.animatedGauge.gauge.textureWidth = textureWidth

    def SetEntosisValueImmediate(self, currentValue):
        self.StopGaugeAnimations()
        self.animatedGauge.StopGaugeAnimations()
        self.animatedGauge.display = False
        self.SetValueAndMarker(currentValue, False)
        self.animatedGauge.SetValueAndMarker(currentValue, False)

    def SetStalemate(self, currentValue):
        self.StopGaugeAnimations()
        self.animatedGauge.StopGaugeAnimations()
        self.animatedGauge.display = True
        uicore.animations.StopAnimation(self.animatedGauge.gauge.texture, 'translation')
        self.SetAnimatedGaugeTexture(self.gaugeStalemateTexturePath, self.stalemateTextureWidth)
        self.SetValueAndMarker(currentValue, False)
        self.animatedGauge.SetValueAndMarker(currentValue, False)

    def SetEntosisValueTimed(self, currentValue, targetValue, duration):
        self.SetValueAndMarker(currentValue, False)
        self.animatedGauge.SetValueAndMarker(currentValue, False)
        self.SetValueAndMarkerTimed(targetValue, duration)
        self.animatedGauge.SetValueAndMarkerTimed(targetValue, duration)
        self.animatedGauge.display = True
        if targetValue == 0.0:
            self.SetAnimatedGaugeTexture(self.gaugeArrowLeftTexturePath, ARROW_TEXTURE_WIDTH)
            uicore.animations.MorphVector2(self.animatedGauge.gauge.texture, 'translation', startVal=(0.0, 0.0), endVal=(1.0, 0.0), duration=1.5, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        else:
            self.SetAnimatedGaugeTexture(self.gaugeArrowRightTexturePath, ARROW_TEXTURE_WIDTH)
            uicore.animations.MorphVector2(self.animatedGauge.gauge.texture, 'translation', startVal=(0.0, 0.0), endVal=(-1.0, 0.0), duration=1.5, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def SetTimerColor(self, foregroundColor, backgroundColor, arrowColor):
        self.SetColorMarker(foregroundColor)
        self.gauge.color = foregroundColor
        self.bgGauge.color = backgroundColor
        self.animatedGauge.gauge.color = arrowColor

    def Close(self):
        uicore.animations.StopAnimation(self.animatedGauge.gauge.texture, 'translation')
        GaugeCircular.Close(self)

    def SetDisplayValue(self, displayValue):
        self.display = displayValue
