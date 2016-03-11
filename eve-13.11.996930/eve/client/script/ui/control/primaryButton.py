#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\primaryButton.py
import math
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import Button
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
import localization
import trinity
import uthread

class PrimaryButton(Button):

    def ApplyAttributes(self, attributes):
        Button.ApplyAttributes(self, attributes)
        self.isStopPending = False
        self.isArrowsAnimating = False
        self.sr.label.uppercase = True
        self.sr.label.fontsize = 13
        self.sr.label.bold = True
        self.pattern = Sprite(name='bgGradient', bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/buttonPattern.png', color=Color.GRAY2, idx=0)
        self.bg = Sprite(name='bg', bgParent=self, opacity=0.0, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/buttonBg.png', color=Color.GRAY2, idx=0, state=uiconst.UI_HIDDEN)
        self.arrows = Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, idx=0)
        self.arrows.translationSecondary = (-0.16, 0)
        self.errorFrame = ErrorFrame(bgParent=self)
        self.errorFrame.Hide()
        color = attributes.color
        if color is None:
            color = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        self.SetColor(color)

    def Update_Size_(self):
        if self.iconPath is None:
            self.width = self.fixedwidth or max(64, self.sr.label.width + 60)
            self.height = self.fixedheight or max(32, self.sr.label.textheight + 12)

    def AnimateArrows(self):
        if self.destroyed:
            return
        self.arrows.Show()
        if self.isArrowsAnimating:
            return
        diff = math.fabs(-0.16 - self.arrows.translationSecondary[0])
        duration = diff / 0.16
        if diff > 0.001:
            uicore.animations.MorphVector2(self.arrows, 'translationSecondary', self.arrows.translationSecondary, (-0.16, 0.0), duration=duration, curveType=uiconst.ANIM_LINEAR, callback=self._LoopArrowAnimation)
        else:
            self._LoopArrowAnimation()
        self.isArrowsAnimating = True

    def _LoopArrowAnimation(self):
        uicore.animations.MorphVector2(self.arrows, 'translationSecondary', (0.16, 0.0), (-0.16, 0.0), duration=2.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)

    def StopAnimateArrows(self):
        if self.destroyed:
            return
        diff = math.fabs(-0.16 - self.arrows.translationSecondary[0])
        duration = diff / 0.16
        if diff:
            uicore.animations.MorphVector2(self.arrows, 'translationSecondary', self.arrows.translationSecondary, (-0.16, 0.0), duration=duration, curveType=uiconst.ANIM_LINEAR)
        self.isArrowsAnimating = False

    def HideArrows(self):
        self.StopAnimateArrows()
        self.arrows.Hide()

    def UpdateLabel(self):
        label = self.GetLabel()
        if label:
            text = localization.GetByLabel(label)
            if self.text != text:
                self.SetLabelAnimated(text)
        else:
            self.SetLabel('')

    def SetColor(self, color):
        underlayColor = Color(*color).SetBrightness(0.4).GetRGBA()
        self.underlay.SetFixedColor(underlayColor)
        blinkColor = Color(*color).SetSaturation(0.5).SetBrightness(0.9).GetRGBA()
        self.sr.hilite.SetRGBA(*blinkColor)
        for obj in (self.pattern, self.bg, self.arrows):
            uicore.animations.SpColorMorphTo(obj, obj.GetRGBA(), color, duration=0.3)

    def SetLabelAnimated(self, text):
        uthread.new(self._SetLabelAnimated, text)

    def _SetLabelAnimated(self, text):
        uicore.animations.FadeOut(self.sr.label, duration=0.15, sleep=True)
        self.SetLabel(text)
        uicore.animations.FadeIn(self.sr.label, duration=0.3)
