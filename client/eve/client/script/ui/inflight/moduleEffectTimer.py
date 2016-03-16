#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\moduleEffectTimer.py
import carbonui.const as uiconst
import math
import trinity
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations

class ModuleEffectTimer(Container):
    default_blink = False
    default_timeIncreases = True
    default_timerColor = (0.5, 0.5, 0.5)
    default_timerOpacity = 0.5
    default_timerRightCounterTexturePath = None
    default_timerLeftCounterTexturePath = None
    default_timerCounterGaugeTexturePath = None
    BLINK_MIN_DURATION = 2
    BLINK_MAX_DURATION = 5
    BLINK_LOOP_DURATION = 1.0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.blink = attributes.get('blink', self.default_blink)
        self.timeIncreases = attributes.get('timeIncreases', self.default_timeIncreases)
        self.timerColor = attributes.get('timerColor', self.default_timerColor)
        self.timerOpacity = attributes.get('timerOpacity', self.default_timerOpacity)
        self.timerRightCounterTexturePath = attributes.get('timerRightCounterTexturePath', self.default_timerRightCounterTexturePath)
        self.timerLeftCounterTexturePath = attributes.get('timerLeftCounterTexturePath', self.default_timerLeftCounterTexturePath)
        self.timerCounterGaugeTexturePath = attributes.get('timerCounterGaugeTexturePath', self.default_timerCounterGaugeTexturePath)

    def StartTimer(self, duration):
        if self.destroyed:
            return
        leftTimer, rightTimer = self._GetTimers()
        if leftTimer and rightTimer:
            durationInSec = duration / 1000
            curveSet = animations.CreateCurveSet(useRealTime=False)
            if self.timeIncreases:
                curvePoints = ([0, math.pi], [0.5, 0], [1, 0])
            else:
                curvePoints = ([0, 0], [0.5, -math.pi], [1, -math.pi])
            animations.MorphScalar(rightTimer, 'rotationSecondary', duration=durationInSec, curveType=curvePoints, curveSet=curveSet)
            if self.timeIncreases:
                curvePoints = ([0, 0], [0.5, 0], [1, -math.pi])
            else:
                curvePoints = ([0, math.pi], [0.5, math.pi], [1, 0])
            animations.MorphScalar(leftTimer, 'rotationSecondary', duration=durationInSec, curveType=curvePoints, curveSet=curveSet)
            if self.blink:
                blinkIn = max(self.BLINK_MIN_DURATION, durationInSec - self.BLINK_MAX_DURATION)
                self.blinkTimer = AutoTimer(blinkIn * 1000, self._BlinkModule)

    def RemoveTimer(self):
        if self.destroyed:
            return
        for sideName in ('leftSide', 'rightSide'):
            side = getattr(self, sideName, None)
            if side:
                side.Close()
                setattr(self, sideName, None)

    def SetTimerOpacity(self, timerOpacity):
        self.timerOpacity = timerOpacity
        right = getattr(self, 'rightSide', None)
        left = getattr(self, 'leftSide', None)
        timerRGB = self.timerColor + (self.timerOpacity,)
        if right and not right.destroyed:
            right.SetRGB(*timerRGB)
        if left and not left.destroyed:
            left.SetRGB(*timerRGB)

    def _GetTimers(self):
        right = getattr(self, 'rightSide', None)
        left = getattr(self, 'leftSide', None)
        if not right or right.destroyed:
            timerName = 'rightSide'
            rotation = 0
            texturePath = self.timerRightCounterTexturePath
            textureSecondaryPath = self.timerCounterGaugeTexturePath
            color = self.timerColor + (self.timerOpacity,)
            rightSide = self._CreateTimer(timerName, rotation, texturePath, textureSecondaryPath, color)
        else:
            rightSide = right
        if not left or left.destroyed:
            timerName = 'leftSide'
            rotation = math.pi
            texturePath = self.timerLeftCounterTexturePath
            textureSecondaryPath = self.timerCounterGaugeTexturePath
            color = self.timerColor + (self.timerOpacity,)
            leftSide = self._CreateTimer(timerName, rotation, texturePath, textureSecondaryPath, color)
        else:
            leftSide = left
        self.rightSide = rightSide
        self.leftSide = leftSide
        return (leftSide, rightSide)

    def _CreateTimer(self, timerName = 'timer', rotation = 0, texturePath = None, textureSecondaryPath = None, color = None):
        if not texturePath or not textureSecondaryPath:
            return None
        timer = Sprite(name=timerName, parent=self, align=uiconst.TOALL, texturePath=texturePath, textureSecondaryPath=textureSecondaryPath, blendMode=1, spriteEffect=trinity.TR2_SFX_MODULATE, state=uiconst.UI_DISABLED)
        if color:
            timer.SetRGB(*color)
        timer.baseRotation = rotation
        timer.rotationSecondary = rotation
        return timer

    def _BlinkModule(self):
        self.blinkTimer = None
        if self.parent and not self.parent.destroyed:
            numLoops = self.BLINK_MAX_DURATION / self.BLINK_LOOP_DURATION
            animations.BlinkIn(self.parent, startVal=0.0, endVal=1.0, duration=self.BLINK_LOOP_DURATION, loops=numLoops)

    def _AreTimerTexturePathsSet(self):
        return self.timerRightCounterTexturePath and self.timerLeftCounterTexturePath and self.timerCounterGaugeTexturePath
