#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipOrbitCamera.py
import destiny
from eve.client.script.parklife import states
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance, GetBallPosition, GetBall, GetBallMaxZoom, Vector3Chaser, VectorLerper, IsAutoTrackingEnabled, CheckShowModelTurrets
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera
import blue
import math
import geo2
import uthread
import evegraphics.settings as gfxsettings
MAX_SPEED_OFFSET_SPEED = 3000.0
MAX_SPEED_OFFSET_LOGSPEED = math.log(MAX_SPEED_OFFSET_SPEED) ** 2
FOV_MIN = 0.55
FOV_MAX = 1.1

class ShipOrbitCamera(BaseSpaceCamera):
    __notifyevents__ = BaseSpaceCamera.__notifyevents__[:] + ['DoBallsRemove',
     'DoBallRemove',
     'OnBallparkSetState',
     'OnStateChange']
    cameraID = evecamera.CAM_SHIPORBIT
    minZoom = 500000
    isBobbingCamera = True
    minFov = 0.3
    maxFov = 1.2

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self._speedOffsetProportion = 0.0
        self.lookAtBall = None
        self.trackBall = None
        self.orbitFreezeProp = 0.0
        self.speedDir = None
        self._zoomPropCache = None
        self._eyeOffsetChaser = Vector3Chaser()
        self._atOffsetChaser = Vector3Chaser()
        self.trackLerper = None
        self.isManualFovEnabled = False
        self._trackSpeed = 1.0

    def OnActivated(self, itemID = None, lastCamera = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPORBIT)
        if lastCamera and lastCamera.cameraID in (evecamera.CAM_TACTICAL,
         evecamera.CAM_SHIPPOV,
         evecamera.CAM_FARLOOK,
         evecamera.CAM_JUMP):
            itemID = itemID or getattr(lastCamera, 'lastLookAtID', None) or self.ego
            self._SetLookAtBall(itemID)
            atPos1 = self.GetTrackPosition(self.lookAtBall)
            if self._zoomPropCache is not None:
                dist = self.GetZoomDistanceByZoomProportion(self._zoomPropCache)
            else:
                dist = self.GetLookAtRadius()
            eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(lastCamera.GetLookAtDirection(), dist))
            if lastCamera.cameraID in (evecamera.CAM_TACTICAL, evecamera.CAM_FARLOOK, evecamera.CAM_JUMP):
                if lastCamera.cameraID == evecamera.CAM_JUMP:
                    duration = 0.1
                if lastCamera.cameraID == evecamera.CAM_FARLOOK:
                    self._bobbingAngle = lastCamera._bobbingAngle
                    duration = 1.0
                else:
                    duration = GetDurationByDistance(lastCamera.eyePosition, eyePos1, 0.4, 0.6)
                self.Transit(lastCamera.atPosition, lastCamera.eyePosition, atPos1, eyePos1, duration=duration, smoothing=0.0)
                self.fov = lastCamera.fov
            else:
                self._atPosition = atPos1
                self._eyePosition = eyePos1
        elif itemID:
            self._SetLookAtBall(itemID)
        elif not self.lookAtBall:
            self._SetLookAtBall(self.ego)

    def GetFov(self):
        if not self.IsDynamicFovEnabled():
            return 1.0
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

    def GetLookAtItemID(self):
        return self.GetItemID()

    def LookAt(self, itemID, forceUpdate = False, radius = None):
        if not self.IsManualControlEnabled():
            return
        if self.IsBallWarping(itemID) and itemID != self.ego:
            return
        self.Track(None)
        self.DisableManualFov()
        if not forceUpdate and self.lookAtBall and self.lookAtBall.id == itemID:
            if radius is None:
                return
        if itemID == self.ego:
            sm.ScatterEvent('OnLookAtMyShip', itemID)
        else:
            sm.ScatterEvent('OnLookAtOther', itemID)
        if self.CheckObjectTooFar(itemID):
            self.Track(itemID)
            return
        self._speedOffsetProportion = 0.0
        if itemID is None:
            self.lookAtBall = None
        else:
            self._SetLookAtBall(itemID)
            if self.lookAtBall:
                self._LookAtAnimate(itemID, radius)

    def IsBallWarping(self, itemID):
        trackBall = GetBall(itemID)
        return trackBall is None or trackBall.mode == destiny.DSTBALL_WARP

    def DisableManualFov(self):
        self.isManualFovEnabled = False

    def _SetLookAtBall(self, itemID):
        self.lookAtBall = GetBall(itemID)
        if self.lookAtBall:
            sm.StartService('state').SetState(self.lookAtBall.id, states.lookingAt, True)
            CheckShowModelTurrets(self.lookAtBall)
        self.Track(None)
        if not self.lookAtBall:
            self.ResetAnchorPos()
            return
        self.UpdateMaxZoom()
        self.UpdateAnchorPos()

    def UpdateMaxZoom(self):
        ball = self.lookAtBall
        nearClip = self.nearClip
        self.SetMaxZoom(GetBallMaxZoom(ball, nearClip))

    def _LookAtAnimate(self, itemID, radius):
        atPos1 = GetBallPosition(self.lookAtBall)
        eyePos1 = self._GetNewLookAtEyePos(atPos1, itemID, radius)
        duration = GetDurationByDistance(self.eyePosition, eyePos1, 0.4, 1.5)
        self.TransitTo(atPos1, eyePos1, duration=duration)

    def _GetNewLookAtEyePos(self, atPos1, itemID, radius):
        direction = self.GetLookAtDirectionWithOffset()
        eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(direction, self.GetLookAtRadius(radius)))
        return eyePos1

    def GetLookAtRadius(self, objRadius = None):
        kPower = 0.95
        a = 1.0 / self.minZoom ** kPower
        b = FOV_MIN / 2.0
        r = objRadius or self.maxZoom
        r = max(objRadius, self.maxZoom)
        c = -r
        radius = self.SolveQuadratic(a, b, c)
        return radius

    def _UpdateAtOffset(self):
        if not self.lookAtBall:
            self._atOffsetChaser.ResetValue()
            return
        self.speedDir = self.GetSpeedDirection()
        if self.IsSpeedOffsetEnabled():
            offsetAmount = self._GetSpeedOffset()
            atOffset = geo2.Vec3Scale(self.speedDir, offsetAmount)
        else:
            atOffset = None
        if self.IsTracking():
            offsetDir = geo2.Vec3Cross(self.upDirection, geo2.Vec3Direction(self._atPosition, self.GetTrackPosition(self.trackBall)))
            trackOffset = geo2.Vec3Subtract(self.GetTrackPosition(self.trackBall), self._atPosition)
            length = geo2.Vec3Length(trackOffset)
            maxLen = 25000
            if length > maxLen:
                trackOffset = geo2.Vec3Scale(trackOffset, maxLen / length)
            if atOffset:
                atOffset = geo2.Vec3Add(atOffset, trackOffset)
            else:
                atOffset = trackOffset
            speed = 30.0
        else:
            isChasingSelf = self.IsChasing() and self.lookAtBall.id == self.ego
            if isChasingSelf:
                speed = 1.2
            else:
                speed = 60.0
        if atOffset:
            self._atOffsetChaser.SetValue(atOffset, speed * self._trackSpeed)
        else:
            self._atOffsetChaser.ResetValue(30.0)
        self._atOffsetChaser.Update()
        self._AddToAtOffset(self._atOffsetChaser.GetValue())

    def IsSpeedOffsetEnabled(self):
        return gfxsettings.Get(gfxsettings.UI_CAMERA_SPEED_OFFSET)

    def IsDynamicFovEnabled(self):
        return gfxsettings.Get(gfxsettings.UI_CAMERA_DYNAMIC_FOV)

    def _GetSpeedOffset(self):
        speedProp = self.GetSpeedOffsetProportion()
        zoomProp = max(0.0, 1.0 - 30 * self.GetZoomProportion())
        speedProp *= zoomProp
        diff = speedProp - self._speedOffsetProportion
        dt = 1.0 / blue.os.fps
        diff *= dt * 0.5
        self._speedOffsetProportion += diff
        maxOffset = self.GetMaxSpeedOffsetScalar()
        offsetAmount = self._speedOffsetProportion * maxOffset
        return offsetAmount

    def GetSpeedDirection(self):
        if getattr(self.lookAtBall, 'model', None) and hasattr(self.lookAtBall.model.rotationCurve, 'value'):
            return geo2.QuaternionTransformVector(self.lookAtBall.model.rotationCurve.value, (0, 0, 1))
        else:
            return geo2.Vec3Normalize(self.GetLookAtBallSpeed())

    def _UpdateEyeOffset(self):
        if self.IsChasing() and self.speedDir:
            offset = (0, 0.5 * self.maxZoom, 0)
            eyeOffset = self.GetChaseEyeOffset()
            offset = geo2.Vec3Subtract(offset, eyeOffset)
            self._eyeOffsetChaser.SetValue(offset, 1.0)
        elif self.IsTracking():
            offsetAmount = (1.0 - self.GetZoomProportion()) * 1.0 * self.maxZoom
            upDir = self.GetYAxis()
            offsetDir = geo2.Vec3Cross(upDir, geo2.Vec3Direction(self._atPosition, self.GetTrackPosition(self.trackBall)))
            offset = geo2.Vec3Scale(offsetDir, offsetAmount)
            offset = geo2.Vec3Add(offset, geo2.Vec3Scale(self.GetZAxis(), -2 * self.maxZoom))
            self._eyeOffsetChaser.SetValue(offset, self._trackSpeed * 0.7)
        else:
            self._eyeOffsetChaser.ResetValue(5.0)
        self._eyeOffsetChaser.Update()
        self._AddToEyeOffset(self._eyeOffsetChaser.GetValue())

    def GetSpeedOffsetProportion(self):
        speed = self.GetLookAtBallSpeed()
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
        zoomProp = self.GetZoomProportion()
        if self.lookAtBall:
            self._UpdateAtOffset()
        self._UpdateEyeOffset()
        if self.lookAtBall:
            newAtPos = self.GetTrackPosition(self.lookAtBall)
            atDiff = geo2.Vec3Subtract(newAtPos, self._atPosition)
            zoomDist = self.GetZoomDistance()
            self._atPosition = newAtPos
            if self.IsChasing():
                self._eyePosition = self.trackLerper.GetValue(self._eyePosition, self.GetChaseEyePosition())
            elif self.IsTracking():
                self._eyePosition = self.trackLerper.GetValue(self._eyePosition, self.GetTrackingEyePosition())
            else:
                prop = self._GetEyePosDriftProporition()
                eyeOffset = geo2.Vec3Scale(atDiff, prop)
                self._eyePosition = geo2.Vec3Add(self._eyePosition, eyeOffset)
            if not self.IsInTransit():
                if self.GetItemID() == self.ego or self.IsTracking():
                    self.SetZoom(zoomProp)
                elif self.GetZoomProportionUnfiltered() < self.GetMinZoomProp():
                    self.SetZoom(0.0)
            if not self.isManualFovEnabled:
                self.SetFovTarget(self.GetFov())
            if self.lookAtBall.mode == destiny.DSTBALL_WARP:
                self.ResetAnchorPos()
            elif not self._anchorBall:
                self.UpdateAnchorPos()
            if self._anchorBall and geo2.Vec3Length(GetBallPosition(self._anchorBall)) > evecamera.LOOKATRANGE_MAX_NEW:
                self.UpdateAnchorPos()

    def GetTrackingEyePosition(self):
        trackPos = self.GetTrackPosition(self.trackBall)
        lookAtPos = self.GetTrackPosition(self.lookAtBall)
        lookAtPos = self._atPosition
        direction = geo2.Vec3Subtract(lookAtPos, trackPos)
        direction = geo2.Vec3Normalize(direction)
        offset = geo2.Vec3Scale(direction, self.GetZoomDistance())
        return geo2.Vec3Add(self._atPosition, offset)

    def GetChaseEyePosition(self):
        offset = geo2.Vec3Scale(self.speedDir, -self.GetZoomDistance())
        return geo2.Vec3Add(self._atPosition, offset)

    def IsTracking(self):
        return self.trackBall is not None and self.trackBall != self.lookAtBall

    def GetChaseEyeOffset(self):
        k = self._GetCameraSpeedMultiplier() ** 3 * 0.5
        eyeOffset = geo2.Vec3Scale(self.speedDir, k * self.maxZoom)
        return eyeOffset

    def Track(self, itemID = None):
        if self.trackBall and self.trackBall.id == itemID:
            return
        if not self.trackBall and itemID is None:
            return
        self.StopUpdateThreads()
        self.trackBall = GetBall(itemID)
        self._trackSpeed = 0.0
        uicore.animations.MorphScalar(self, '_trackSpeed', self._trackSpeed, 1.0, duration=2.0)
        if self.trackBall:
            self.trackLerper = VectorLerper(duration=3.0)
        else:
            self.trackLerper = None

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
        return self.lookAtBall == self.trackBall

    def GetLookAtBallSpeed(self, offset = 0):
        ball = self.lookAtBall
        vec = ball.GetVectorDotAt(blue.os.GetSimTime() + int(offset))
        vec = (vec.x, vec.y, vec.z)
        return vec

    def GetTrackItemID(self):
        if self.IsTracking():
            return self.trackBall.id

    def ResetCamera(self, *args):
        self.LookAt(self.ego, forceUpdate=True)

    def ResetCameraPosition(self):
        BaseSpaceCamera.ResetCameraPosition(self)
        self._SetLookAtBall(self.ego)

    def Orbit(self, *args):
        BaseSpaceCamera.Orbit(self, *args)
        if self.IsTracking() or self.IsChasing():
            self.Track(None)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self._zoomPropCache = self.GetZoomProportion()
        self.lookAtBall = None
        self._speedOffsetProportion = 0.0
        self._atOffsetChaser.ResetValue()
        self.ResetAnchorPos()
        self.DisableManualFov()

    def GetItemID(self):
        if self.lookAtBall:
            return self.lookAtBall.id

    def ClearCameraParent(self):
        self._SetLookAtBall(self.ego)

    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if ball == self.lookAtBall:
            if not self.isActive or ball.id == self.ego:
                self._SetLookAtBall(None)
            elif ball.id != self.ego and ball.explodeOnRemove:
                uthread.new(self._HandleTargetKilled, ball)
            else:
                self.LookAt(self.ego)
        if ball == self.trackBall:
            self.Track(None)

    def _HandleTargetKilled(self, ball):
        delay = ball.GetExplosionLookAtDelay()
        blue.synchro.SleepSim(delay)
        self.LookAt(self.ego)

    def OnBallparkSetState(self):
        if self.isActive:
            self._SetLookAtBall(self.ego)
        else:
            self._SetLookAtBall(None)

    def OnCurrentShipWarping(self):
        if self.GetLookAtItemID() is not None and self.GetLookAtItemID() != self.ego:
            self.LookAt(self.ego)

    def OnMouseDown(self, button):
        if self.IsTracking() or self.IsChasing():
            return
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 1.0, duration=0.5, timeOffset=0.0)

    def OnMouseUp(self, button):
        if button == 0:
            uicore.animations.MorphScalar(self, 'orbitFreezeProp', self.orbitFreezeProp, 0.0, duration=2.0, timeOffset=0.0)

    def FovZoom(self, dz):
        BaseSpaceCamera.FovZoom(self, dz)
        self.isManualFovEnabled = True

    def OnStateChange(self, itemID, flag, flagState, *args):
        if flag == states.selected and IsAutoTrackingEnabled():
            self.Track(itemID)
