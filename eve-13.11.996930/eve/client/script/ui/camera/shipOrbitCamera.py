#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipOrbitCamera.py
import destiny
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance, GetBallRadius
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
import blue
import math
from evecamera.utils import GetARZoomMultiplier
import trinity
import geo2
MAX_SPEED_OFFSET_SPEED = 3000.0
MAX_SPEED_OFFSET_LOGSPEED = math.log(MAX_SPEED_OFFSET_SPEED) ** 2
FOV_MIN = 0.5
FOV_MAX = 1.2

class ShipOrbitCamera(BaseSpaceCamera):
    __notifyevents__ = BaseSpaceCamera.__notifyevents__ + ['OnSessionChangedDoBallsRemove', 'DoBallRemove', 'OnBallparkSetState']
    cameraID = evecamera.CAM_SHIPORBIT
    minZoom = 500000
    isBobbingCamera = True

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self._speedOffsetProportion = 0.0
        self._speedOffsetScale = 1.0
        self.trackBall = None
        self.interestBall = None
        self.orbitFreezeProp = 0.0
        self.speedDir = None
        self.interestScale = 0.0
        self._zoomPropCache = None

    def OnActivated(self, itemID = None, lastCamera = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        if lastCamera and lastCamera.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_SHIPPOV, evecamera.CAM_FARLOOK):
            itemID = itemID or lastCamera.lastLookAtID or self.ego
            self.SetNewTrackBall(itemID)
            atPos1 = self.GetTrackPosition(self.trackBall)
            if self._zoomPropCache is not None:
                dist = self.GetCachedZoomDistance()
            else:
                dist = self.GetLookAtRadius()
            eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(lastCamera.GetLookAtDirection(), dist))
            if lastCamera.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_FARLOOK):
                if lastCamera.cameraID == evecamera.CAM_FARLOOK:
                    self._bobbingAngle = lastCamera._bobbingAngle
                    duration = 1.0
                else:
                    duration = GetDurationByDistance(lastCamera.eyePosition, eyePos1, 0.4, 0.6)
                self.RampUpSpeedOffset(duration)
                self.Transit(lastCamera.atPosition, lastCamera.eyePosition, atPos1, eyePos1, duration=duration, smoothing=0.0)
                self.fov = lastCamera.fov
            else:
                self._atPosition = atPos1
                self._eyePosition = eyePos1
        elif itemID:
            self.SetNewTrackBall(itemID)
        elif not self.trackBall:
            self.SetNewTrackBall(self.ego)

    def GetCachedZoomDistance(self):
        return self.maxZoom + self._zoomPropCache * (self.minZoom - self.maxZoom)

    def GetFov(self):
        if self._transitOffset:
            atPos = geo2.Vec3Subtract(self.atPosition, self._transitOffset)
        else:
            atPos = self.atPosition
        dist = geo2.Vec3Distance(self.eyePosition, atPos)
        return self._GetFov(dist)

    def _GetFov(self, dist):
        prop = max(0.0, min(dist / self.minZoom, 1.0))
        return FOV_MIN + prop ** 0.35 * (FOV_MAX - FOV_MIN)

    def SolveQuadratic(self, a, b, c):
        d = math.sqrt(b ** 2 - 4 * a * c)
        x1 = -2 * c / (b + d)
        x2 = -2 * c / (b - d)
        return max(x1, x2)

    def LookingAt(self):
        return self.GetItemID()

    def LookAt(self, itemID, forceUpdate = False):
        if not self.IsManualControlEnabled():
            return
        self.SetCameraInterest(None)
        if not forceUpdate and self.trackBall and self.trackBall.id == itemID:
            return
        if self.CheckObjectTooFar(itemID):
            sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_FARLOOK, itemID=itemID)
            return
        self.StopUpdateThreads()
        self._speedOffsetProportion = 0.0
        if itemID is None:
            self.trackBall = None
        else:
            self.SetNewTrackBall(itemID)
            if self.trackBall:
                self._LookAtAnimate(itemID)

    def SetNewTrackBall(self, itemID):
        self.trackBall = self.GetBall(itemID)
        self.SetCameraInterest(None)
        if not self.trackBall:
            return
        self.SetMaxZoom(self.GetTrackBallMaxZoom())
        self.UpdateAnchorPos()

    def GetTrackBallMaxZoom(self):
        rad = GetBallRadius(self.trackBall)
        zoomMultiplier = 1.5 * GetARZoomMultiplier(trinity.GetAspectRatio())
        return (rad + self.nearClip) * zoomMultiplier + 2

    def _LookAtAnimate(self, itemID):
        atPos1 = self.GetBallPosition(self.trackBall)
        eyePos1 = self._GetNewLookAtEyePos(atPos1, itemID)
        duration = GetDurationByDistance(self.eyePosition, eyePos1, 0.8, 3.0)
        self.RampUpSpeedOffset(duration)
        self.TransitTo(atPos1, eyePos1, duration=duration)

    def RampUpSpeedOffset(self, duration):
        self._speedOffsetScale = 0.0
        uicore.animations.MorphScalar(self, '_speedOffsetScale', 0.0, 1.0, duration=2.0, timeOffset=duration * 0.8)

    def _GetNewLookAtEyePos(self, atPos1, itemID):
        direction = self.GetLookAtDirectionWithOffset()
        eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(direction, self.GetLookAtRadius()))
        return eyePos1

    def GetLookAtRadius(self):
        kPower = 0.95
        a = 1.0 / self.minZoom ** kPower
        b = FOV_MIN / 2.0
        c = -self.maxZoom
        distance = self.SolveQuadratic(a, b, c)
        return distance

    def _UpdateSpeedOffset(self):
        speedProp = self.GetSpeedOffsetProportion()
        zoomProp = max(0.0, 1.0 - 30 * self.GetZoomProportion())
        speedProp *= zoomProp
        diff = speedProp - self._speedOffsetProportion
        dt = 1.0 / blue.os.fps
        diff *= dt * 0.5
        self._speedOffsetProportion += diff
        maxOffset = self.GetMaxSpeedOffsetScalar()
        if not self.trackBall:
            return
        if getattr(self.trackBall, 'model', None) and hasattr(self.trackBall.model.rotationCurve, 'value'):
            self.speedDir = geo2.QuaternionTransformVector(self.trackBall.model.rotationCurve.value, (0, 0, 1))
        else:
            self.speedDir = geo2.Vec3Normalize(self.GetTrackSpeed())
        speedOffset = geo2.Vec3Scale(self.speedDir, self._speedOffsetProportion * maxOffset * self._speedOffsetScale)
        self._AddToAtOffset(speedOffset)

    def _UpdateInterestOffset(self):
        if self.speedDir:
            interestOffset = geo2.Vec3Scale(self.speedDir, 0.3 * self.GetZoomDistance() * self.interestScale)
            self._AddToEyeOffset(interestOffset)
            if self.IsChasing():
                self._AddToEyeOffset((0, 0.5 * self.maxZoom * self.interestScale, 0))

    def GetSpeedOffsetProportion(self):
        speed = self.GetTrackSpeed()
        velocity = geo2.Vec3Length(speed)
        if velocity <= 1.0:
            return 0.0
        elif velocity < MAX_SPEED_OFFSET_SPEED:
            return math.log(velocity) ** 2 / MAX_SPEED_OFFSET_LOGSPEED
        else:
            return 1.0

    def GetMaxSpeedOffsetScalar(self):
        kMaxSpeedOffset = 0.18
        th = math.radians(90 * self.fov / 2.0)
        maxOffset = 2 * self.GetZoomDistance() * math.tan(th) * kMaxSpeedOffset
        return maxOffset

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.trackBall:
            self._UpdateSpeedOffset()
        if self.interestBall:
            self._UpdateInterestOffset()
        if self.trackBall:
            if getattr(self.trackBall, 'released', False):
                self.LookAt(self.ego)
            newAtPos = self.GetTrackPosition(self.trackBall)
            zoomProp = self.GetZoomProportion()
            atDiff = geo2.Vec3Subtract(newAtPos, self._atPosition)
            zoomDist = self.GetZoomDistance()
            self._atPosition = newAtPos
            if self.IsChasing():
                k = self._GetCameraSpeedMultiplier() ** 3 * 0.5
                self._eyePosition = geo2.Vec3Subtract(self._eyePosition, geo2.Vec3Scale(self.speedDir, k * self.maxZoom))
            elif self.interestBall:
                interestPos = self.GetTrackPosition(self.interestBall)
                trackPos = self.GetTrackPosition(self.trackBall)
                direction = geo2.Vec3Subtract(trackPos, interestPos)
                direction = geo2.Vec3Normalize(direction)
                zoomDist = geo2.Vec3Distance(trackPos, interestPos)
                atDiff = geo2.Vec3Scale(direction, zoomDist * self.interestScale)
                self._eyePosition = geo2.Vec3Add(self._eyePosition, atDiff)
            else:
                prop = self._GetEyePosDriftProporition()
                self._eyePosition = geo2.Vec3Add(self._eyePosition, geo2.Vec3Scale(atDiff, prop))
            if not self.IsInTransit():
                if self.GetItemID() == self.ego or self.interestBall:
                    self.SetZoom(zoomProp)
                elif self.GetZoomProportionUnfiltered() < 0:
                    self.SetZoom(0.0)
            self.SetFovTarget(self.GetFov())
            if self.trackBall.mode == destiny.DSTBALL_WARP:
                self.ResetAnchorPos()
            elif not self._anchorBall:
                self.UpdateAnchorPos()
            if self._anchorBall and geo2.Vec3Length(self.GetBallPosition(self._anchorBall)) > evecamera.LOOKATRANGE_MAX_NEW:
                self.UpdateAnchorPos()

    def SetCameraInterest(self, itemID = None):
        self.StopUpdateThreads()
        self.interestBall = self.GetBall(itemID)
        if self._eyeOffset:
            self._eyePosition = geo2.Vec3Add(self._eyePosition, self._eyeOffset)
            self._eyeOffset = None
        if itemID:
            uicore.animations.MorphScalar(self, 'interestScale', 0.0, 1.0, duration=3.0)
        else:
            self.interestScale = 0.0
            uicore.animations.StopAnimation(self, 'interestScale')

    def _GetEyePosDriftProporition(self):
        if self.GetItemID() == self.ego:
            x = min(0.1, self._speedOffsetProportion)
            return 1.0 - 0.01 * x
        else:
            zoomProp = self.GetZoomProportion()
            k = 0.7
            prop = k * (1.0 - zoomProp)
            prop = max(0.5, prop)
            if prop < 1.0:
                prop += self.orbitFreezeProp * (1.0 - prop)
            prop = min(prop, 1.0)
            return prop

    def IsChasing(self):
        return self.trackBall == self.interestBall

    def GetTrackSpeed(self, offset = 0):
        ball = self.trackBall
        vec = ball.GetVectorDotAt(blue.os.GetSimTime() + int(offset))
        vec = (vec.x, vec.y, vec.z)
        return vec

    def ResetCamera(self):
        self.LookAt(self.ego, forceUpdate=True)

    def ResetCameraPosition(self):
        BaseSpaceCamera.ResetCameraPosition(self)
        self.SetNewTrackBall(self.ego)

    def Orbit(self, *args):
        BaseSpaceCamera.Orbit(self, *args)
        if self.interestBall:
            self.SetCameraInterest(None)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self._zoomPropCache = self.GetZoomProportion()
        self.trackBall = None
        self._speedOffsetProportion = 0.0
        self._speedOffsetScale = 1.0
        self.ResetAnchorPos()

    def GetItemID(self):
        if self.trackBall:
            return self.trackBall.id

    def ClearCameraParent(self):
        self.SetNewTrackBall(self.ego)

    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball == self.trackBall:
            if not self.isActive:
                self.SetNewTrackBall(None)
            if ball.id != self.ego:
                self.SetNewTrackBall(None)
            else:
                self.LookAt(self.ego)

    def OnBallparkSetState(self):
        if self.isActive:
            self.SetNewTrackBall(self.ego)
        else:
            self.SetNewTrackBall(None)

    def OnCurrentShipWarping(self):
        if self.LookingAt() is not None and self.LookingAt() != self.ego:
            self.LookAt(self.ego)

    def OnMouseDown(self, button):
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 1.0, duration=0.5, timeOffset=0.0)

    def OnMouseUp(self, button):
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 0.0, duration=2.0, timeOffset=0.0)
