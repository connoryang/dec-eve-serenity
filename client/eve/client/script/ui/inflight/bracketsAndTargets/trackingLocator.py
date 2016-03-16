#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\bracketsAndTargets\trackingLocator.py
import uiprimitives
import carbonui.const as uiconst
import uicontrols
import uix
import uthread
import blue
import evecamera.trackingUtils as trackingUtils
import trinity

class TrackingLocator(uiprimitives.Container):
    default_width = 64
    default_height = 64

    def ApplyAttributes(self, attributes):
        self.mouseCookie = None
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.isInteractive = attributes.get('interactive', True)
        self.positionCallback = attributes.get('positionCallback', None)
        self.boundary = attributes.get('boundary', None)
        normalizedPoint = attributes.get('desiredPosition', (0, 0))
        sx, sy = trackingUtils.NormalizedPointToAbsoluteInflight(normalizedPoint)
        self.left = sx - self.width / 2
        self.top = sy - self.height / 2
        if self.isInteractive:
            icon = uiprimitives.Sprite(state=uiconst.UI_DISABLED, parent=self, pos=(0, 0, 64, 64), texturePath='res:/UI/Texture/classes/Bracket/customTrackerIndicator.png')
            uicore.animations.BlinkIn(self, startVal=1.0, endVal=0.0, duration=0.2, loops=3, curveType=uiconst.ANIM_WAVE, callback=self.StartFadeSlow)
        else:
            icon = uiprimitives.Sprite(state=uiconst.UI_DISABLED, parent=self, pos=(0, 0, 64, 64), texturePath='res:/UI/Texture/classes/Bracket/centerTrackerIndicator.png')
            uicore.animations.BlinkIn(self, startVal=1.0, endVal=0.0, duration=0.2, loops=3, curveType=uiconst.ANIM_WAVE, callback=self.StartFade)
        self.UpdateTrackingData(persist=False)

    def StartFadeSlow(self):
        uicore.animations.FadeOut(obj=self, duration=2.0, callback=self.Close)

    def StartFade(self):
        uicore.animations.FadeOut(obj=self, duration=1.0, callback=self.Close)

    def SetBoundaries(self, boundaries):
        self.boundary = boundaries

    def OnMouseDown(self, *args):
        if not self.isInteractive:
            return
        self.StopAnimations()
        uicore.animations.FadeIn(obj=self, duration=0.1)
        absX, absY = self.GetAbsolutePosition()
        mouseX, mouseY = self.GetMousePosition()
        diffX = absX - mouseX
        diffY = absY - mouseY
        self.dragPositionOffset = (diffX, diffY)
        self.dragging = 1
        uthread.new(self.BeginDrag, diffX, diffY)
        self.mouseCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEUP, self.OnGlobalMouseUp)

    def GetMousePosition(self):
        mouseX, mouseY = trinity.GetCursorPos()
        mouseX = uicore.ReverseScaleDpi(mouseX)
        mouseY = uicore.ReverseScaleDpi(mouseY)
        return (mouseX, mouseY)

    def GetCenterPoint(self):
        return (self.left + self.width / 2, self.top + self.height / 2)

    def UpdateTrackingData(self, persist):
        if self.positionCallback:
            x, y = self.GetCenterPoint()
            self.positionCallback(x, y, persist=persist)

    def BeginDrag(self, diffX, diffY, *args):
        while not self.destroyed and getattr(self, 'dragging', 0):
            mouseX, mouseY = self.GetMousePosition()
            left = mouseX + diffX
            top = mouseY + diffY
            normalized = trackingUtils.NormalizePointToInflight((left, top))
            if self.boundary:
                normalized = trackingUtils.ClampPoint(self.boundary, normalized)
                left, top = trackingUtils.NormalizedPointToAbsoluteInflight(normalized)
            self.left = left
            self.top = top
            self.UpdateTrackingData(persist=False)
            blue.synchro.SleepWallclock(1)

    def OnGlobalMouseUp(self, *args):
        self.UpdateTrackingData(persist=True)
        self.StopDragging()
        uicore.animations.FadeOut(obj=self, callback=self.Close)

    def StopDragging(self):
        self.dragging = 0
        if self.mouseCookie:
            uicore.event.UnregisterForTriuiEvents(self.mouseCookie)
        self.mouseCookie = None

    def Close(self):
        self.StopDragging()
        super(TrackingLocator, self).Close()
