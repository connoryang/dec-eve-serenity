#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\processingview.py
__author__ = 'ru.Hjalti'
import math
import blue
import uthread
import uicontrols
import uiprimitives
import localization
import taskimages
import carbonui.const as uiconst
from projectdiscovery.client import const
from carbonui.uianimations import animations
from carbon.common.script.util.format import FmtAmt
from projectdiscovery.client.util.eventlistener import eventlistener, on_event

@eventlistener()

class ProcessingView(uiprimitives.Container):
    default_height = 470
    default_width = 843
    default_align = uiconst.CENTER

    def ApplyAttributes(self, attributes):
        super(ProcessingView, self).ApplyAttributes(attributes)
        self.player_selection = None
        self.setup_layout()

    def setup_layout(self):
        self.processing_container = uiprimitives.Container(name='processingContainer', parent=self, width=842, height=70, align=uiconst.CENTER)
        self.expandGradient = uiprimitives.Sprite(name='ExpandGradient', parent=self, align=uiconst.CENTER, width=842, height=48, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandGradient.png')
        self.expandTopContainer = uiprimitives.Container(name='expandTopContainer', parent=self.processing_container, width=842, height=11, align=uiconst.TOTOP)
        uiprimitives.Sprite(name='expandTop', parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERTOP, top=5)
        uiprimitives.Sprite(parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=620, height=3, align=uiconst.CENTERTOP, top=11)
        self.expandBottomContainer = uiprimitives.Transform(name='expandBottomContainer', parent=self.processing_container, width=842, height=11, align=uiconst.TOBOTTOM, rotation=math.pi)
        uiprimitives.Sprite(parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERBOTTOM)
        uiprimitives.Sprite(parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=620, height=3, align=uiconst.CENTERTOP, top=11)
        self.originalTranslationTop = self.expandTopContainer.translation
        self.originalTranslationBot = self.expandBottomContainer.translation

    def setup_busy_indicator(self):
        count = 0
        prevRotation = 0
        delta = 1.04719755
        self.busy_indicator_container = uiprimitives.Container(name='busyIndicatorContainer', parent=self.processing_container, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/busyIndicatorCircle.png', width=36, height=36, align=uiconst.CENTERLEFT, left=120)
        self.busy_indicator_hex = uiprimitives.Transform(name='busyIndicatorHex', parent=self.busy_indicator_container, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/busyIndicatorHex.png', width=10, height=10, align=uiconst.CENTER)
        animations.Tr2DRotateTo(self.busy_indicator_hex, endAngle=self.busy_indicator_hex.rotation - delta, loops=uiconst.ANIM_REPEAT)
        while count < 6:
            count += 1
            triangle = uiprimitives.Transform(name='busyIndicatorTriangle', parent=self.busy_indicator_container, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/busyIndicatorTriangle.png', width=8, height=8, align=uiconst.CENTER, top=12, rotationCenter=(0.5, -1.0), rotation=prevRotation + delta)
            prevRotation = triangle.rotation
            animations.Tr2DRotateTo(triangle, startAngle=triangle.rotation, endAngle=triangle.rotation - delta, loops=uiconst.ANIM_REPEAT)

    @on_event(const.Events.ContinueFromResult)
    def start(self):
        self.reset_processing_screen()
        animations.FadeIn(self, timeOffset=0.2, callback=self.expand_screen)

    @property
    def gradient_height(self):
        return self._gradient_height

    @gradient_height.setter
    def gradient_height(self, value):
        self._gradient_height = value
        self.expandGradient.SetSize(842, self._gradient_height)

    def gradient_height_callback(self):
        self.gradient_height = 440
        self.expandGradient.top = -12
        sm.ScatterEvent(const.Events.ProcessingViewFinished)

    def expand_screen(self):
        translationtop = (self.expandTopContainer.translation[0], -210)
        translationbottom = (self.expandBottomContainer.translation[0], -185)
        animations.MoveTo(self.expandTopContainer, startPos=(0, 0), endPos=translationtop, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.MoveTo(self.expandBottomContainer, startPos=(0, 0), endPos=translationbottom, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.MorphScalar(self, 'gradient_height', startVal=48, endVal=440, curveType=uiconst.ANIM_LINEAR, duration=0.2, callback=self.gradient_height_callback)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowOpenPlay)

    @on_event(const.Events.RewardViewFadeOut)
    def fade_out(self):
        animations.FadeOut(self, duration=0.5, callback=self.reset_processing_screen)

    def reset_processing_screen(self):
        self.expandTopContainer.translation = self.originalTranslationTop
        self.expandBottomContainer.translation = (self.originalTranslationBot[0], 59)
        self.expandGradient.height = 48
        self.expandGradient.top = 0
