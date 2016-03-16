#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\baseCamera.py
import math
import trinity
import geo2
import uthread
import blue
import logmodule as log

class Camera(object):
    __typename__ = None
    __notifyevents__ = ['OnSetDevice']
    name = 'util.Camera'
    default_fov = 1.0
    default_nearClip = 6.0
    default_farClip = 10000000.0
    default_eyePosition = (0, 500, 1000)
    default_atPosition = (0, 0, 0)
    default_upDirection = (0, 1, 0)
    maxFov = 1.5
    minFov = 0.2
    kZoomSpeed = 20.0
    kZoomStopDist = 0.0001
    maxZoom = 100
    minZoom = 10000
    kFovSpeed = 4.0
    kFovStopDist = 0.001
    kOrbitSpeed = 5.0
    kOrbitStopAngle = 0.0001
    kMinPitch = 0.05
    kMaxPitch = math.pi - kMinPitch
    kPanSpeed = 5.0
    kPanStopDist = 50

    def __init__(self):
        sm.RegisterNotify(self)
        self._fov = self.default_fov
        self._nearClip = self.default_nearClip
        self._farClip = self.default_farClip
        self._eyePosition = self.default_eyePosition
        self._atPosition = self.default_atPosition
        self._upDirection = self.default_upDirection
        self.panTarget = None
        self.panUpdateThread = None
        self.zoomTarget = None
        self.zoomUpdateThread = None
        self.orbitTarget = None
        self.orbitUpdateThread = None
        self.fovTarget = None
        self.fovUpdateThread = None
        self._fovOffset = 0.0
        self._eyeOffset = None
        self._atOffset = None
        self._eyeAndAtOffset = None
        self._transitOffset = None
        self._effectOffset = None
        self.centerOffset = None
        self.isActive = False
        self.viewMatrix = trinity.TriView()
        self.projectionMatrix = trinity.TriProjection()
        self.updateThread = uthread.new(self.UpdateThread)

    def UpdateThread(self):
        while self.isActive:
            self._Update()
            blue.synchro.Yield()

        self.updateThread = None

    def _Update(self):
        self._eyeOffset = None
        self._atOffset = None
        self._eyeAndAtOffset = None
        self.Update()
        self.UpdateProjection()
        self.UpdateView()

    def Update(self):
        self._UpdateTransitOffset()
        self._UpdateEffectOffset()

    def _UpdateTransitOffset(self):
        if self._transitOffset:
            self._AddToAtOffset(self._transitOffset)

    def OnSetDevice(self, *args):
        if self.isActive:
            self.UpdateProjection()

    def OnActivated(self, **kwargs):
        self.isActive = True
        self.Update()
        if not self.updateThread:
            self.updateThread = uthread.new(self.UpdateThread)

    def OnDeactivated(self):
        self.isActive = False
        self.StopAnimations()
        self.StopUpdateThreads()
        if self.updateThread:
            self.updateThread.kill()
            self.updateThread = None
        self._transitOffset = None
        self._eyeAndAtOffset = None
        self._atOffset = None
        self._eyeOffset = None

    def UpdateProjection(self):
        aspectRatio = uicore.uilib.desktop.width / float(uicore.uilib.desktop.height)
        fov = self._fov - self._fovOffset
        if fov <= 0.0:
            fov = 1.0
            self.ResetCameraPosition()
            log.LogException('Camera: FOV Set to <= 0.0')
        if self.centerOffset:
            self._UpdateProjectionOffset(aspectRatio, fov)
        else:
            self._UpdateProjectionFov(aspectRatio, fov)

    def _UpdateProjectionFov(self, aspectRatio, fov):
        self.projectionMatrix.PerspectiveFov(fov, aspectRatio, self._nearClip, self._farClip)

    def _UpdateProjectionOffset(self, aspectRatio, fov):
        dX = aspectRatio * self._nearClip * math.tan(fov / 2)
        dY = self._nearClip * math.tan(fov / 2.0)
        left = -dX + dX * self.centerOffset
        right = dX + dX * self.centerOffset
        top = dY
        bottom = -dY
        self.projectionMatrix.PerspectiveOffCenter(left, right, bottom, top, self._nearClip, self._farClip)

    def UpdateView(self):
        self.viewMatrix.SetLookAtPosition(self.eyePosition, self.atPosition, self._upDirection)

    def OffsetAtPosition(self, atPosition):
        if self._atOffset:
            atPosition = geo2.Vec3Add(atPosition, self._atOffset)
        if self._eyeAndAtOffset:
            atPosition = geo2.Vec3Add(atPosition, self._eyeAndAtOffset)
        return atPosition

    def OffsetEyePosition(self, eyePosition):
        if self._eyeOffset:
            eyePosition = geo2.Vec3Add(eyePosition, self._eyeOffset)
        if self._eyeAndAtOffset:
            eyePosition = geo2.Vec3Add(eyePosition, self._eyeAndAtOffset)
        return eyePosition

    def _AddToEyeOffset(self, offset):
        if not self._eyeOffset:
            self._eyeOffset = offset
        else:
            self._eyeOffset = geo2.Vec3Add(self._eyeOffset, offset)

    def _AddToAtOffset(self, offset):
        if not self._atOffset:
            self._atOffset = offset
        else:
            self._atOffset = geo2.Vec3Add(self._atOffset, offset)

    def SetEffectOffset(self, offset):
        self._effectOffset = offset

    def _UpdateEffectOffset(self):
        if self._effectOffset:
            self._AddToEyeAndAtOffset(self._effectOffset)

    def _AddToEyeAndAtOffset(self, offset):
        if not self._eyeAndAtOffset:
            self._eyeAndAtOffset = offset
        else:
            self._eyeAndAtOffset = geo2.Vec3Add(self._eyeAndAtOffset, offset)

    def GetXAxis(self):
        t = self.viewMatrix.transform
        return (t[0][0], t[1][0], t[2][0])

    def GetYAxis(self):
        t = self.viewMatrix.transform
        return (t[0][1], t[1][1], t[2][1])

    def GetZAxis(self):
        t = self.viewMatrix.transform
        return (t[0][2], t[1][2], t[2][2])

    def SetViewVector(self, viewVector):
        self.StopUpdateThreads()
        atPosition = self.GetAtPosition()
        eyePosition = self.GetEyePosition()
        eyePositionLocal = geo2.Subtract(atPosition, eyePosition)
        eyeDistance = geo2.Vec3Length(eyePositionLocal)
        newEyePosition = geo2.Vec3Scale(viewVector, eyeDistance)
        self.eyePosition = geo2.Vec3Add(newEyePosition, atPosition)
        if not self.isActive:
            self.Update()

    def GetViewVector(self):
        return self.GetLookAtDirection()

    def GetYaw(self):
        x, y, z = self.GetLookAtDirection()
        return -(math.atan2(z, x) + math.pi / 2)

    def GetPitch(self):
        x, y, z = self.GetLookAtDirection()
        return math.atan2(math.sqrt(z ** 2 + x ** 2), -y) + math.pi / 2

    def GetRotationQuat(self):
        yaw = self.GetYaw()
        pitch = self.GetPitch()
        return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0.0)

    def GetLookAtDirection(self):
        return geo2.Vec3Direction(self._eyePosition, self._atPosition)

    def GetLookAtDirectionWithOffset(self):
        return geo2.Vec3Direction(self.eyePosition, self.atPosition)

    def Pan(self, dx = 0, dy = 0, dz = 0):
        if self.panTarget is None:
            self.panTarget = geo2.Vector(0, 0, 0)
        if dx:
            self.panTarget += geo2.Scale(self.GetXAxis(), dx)
        if dy:
            self.panTarget += geo2.Scale(self.GetYAxis(), dy)
        if dz:
            self.panTarget += geo2.Scale(self.GetZAxis(), dz)
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)

    def PanTo(self, diff):
        self.panTarget = geo2.Vector(*diff)
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)

    def PanAxis(self, axis, amount):
        if self.panTarget is None:
            self.panTarget = geo2.Vector(0, 0, 0)
        self.panTarget += geo2.Scale(axis, amount)
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)

    def PanUpdateThread(self):
        while True:
            if self.panTarget is None:
                break
            distLeft = geo2.Vec3Length(self.panTarget)
            if distLeft == 0:
                break
            dist = self._GetPanSpeed() / blue.os.fps
            if distLeft < self.kPanStopDist:
                dist *= self.kPanStopDist / distLeft
            dist = min(dist, 1.0)
            toMove = geo2.Vec3Scale(self.panTarget, dist)
            self.eyePosition = geo2.Add(self._eyePosition, toMove)
            self.atPosition = geo2.Add(self._atPosition, toMove)
            self.panTarget -= toMove
            if dist == 1.0:
                break
            blue.synchro.Yield()

        self.panUpdateThread = None
        self.panTarget = None

    def IsZoomedOutCompletely(self):
        zoomValue = self.GetZoomValue()
        return zoomValue > 1.0 - self.kZoomStopDist

    def IsZoomedInCompletely(self):
        zoomValue = self.GetZoomValue()
        return zoomValue == 0.0

    def GetZoomValue(self):
        if self.zoomTarget is not None:
            zoomValue = self.zoomTarget
        else:
            zoomValue = self.GetZoomProportion()
        return zoomValue

    def Zoom(self, dz):
        if dz < 0 and self.IsZoomedInCompletely():
            return
        if dz > 0 and self.IsZoomedOutCompletely():
            return
        if self.zoomTarget is None:
            self.zoomTarget = self.GetZoomProportion()
        distProp = self.GetZoomDistance() / self.minZoom
        self.zoomTarget += distProp ** 0.8 * dz
        self.zoomTarget = max(0.0, min(self.zoomTarget, 1.0))
        if not self.zoomUpdateThread:
            self.zoomUpdateThread = uthread.new(self.ZoomUpdateThread)

    def ZoomUpdateThread(self):
        try:
            while True:
                if self.zoomTarget is None:
                    break
                zoomProporition = self.GetZoomProportion()
                distLeft = self.zoomTarget - zoomProporition
                if not distLeft:
                    break
                distProp = self.GetZoomDistance() / self.minZoom
                zoomSpeed = (0.2 + 0.8 * distProp ** 0.6) * self._GetZoomSpeed()
                moveProp = zoomSpeed / blue.os.fps
                if math.fabs(distLeft) < self.kZoomStopDist:
                    moveProp *= self.kZoomStopDist / math.fabs(distLeft)
                moveProp = min(moveProp, 1.0)
                self._ApplyZoom(moveProp * distLeft)
                if moveProp == 1.0:
                    break
                blue.synchro.Yield()

        finally:
            self.zoomUpdateThread = None
            self.zoomTarget = None

    def _ApplyZoom(self, toMove):
        toMove *= self.minZoom - self.maxZoom
        toMove = geo2.Vec3Scale(self.GetLookAtDirection(), toMove)
        self._eyePosition = geo2.Add(self._eyePosition, toMove)

    def GetZoom(self):
        return 1.0 - self.GetZoomProportion()

    def SetZoom(self, proportion):
        vec = self.GetLookAtDirection()
        zoomVec = geo2.Vec3Scale(vec, self.maxZoom + (self.minZoom - self.maxZoom) * proportion)
        self._eyePosition = geo2.Vec3Add(self._atPosition, zoomVec)

    zoom = property(GetZoom, SetZoom)

    def FovZoom(self, dz):
        if self.fovTarget is not None:
            self.SetFovTarget(self.fovTarget + dz)
        else:
            self.SetFovTarget(self.fov + dz)

    def SetFovTarget(self, value):
        if self.fov == value:
            return
        self.fovTarget = self._EnforceMinMaxFov(value)
        if not self.fovUpdateThread:
            self.fovUpdateThread = uthread.new(self.FovUpdateThread)

    def FovUpdateThread(self):
        try:
            while True:
                if self.fovTarget is None:
                    break
                distLeft = self.fovTarget - self.fov
                if not distLeft:
                    break
                moveProp = self.kFovSpeed / blue.os.fps
                if math.fabs(distLeft) < self.kFovStopDist:
                    moveProp *= self.kFovStopDist / math.fabs(distLeft)
                moveProp = min(moveProp, 1.0)
                fov = self.fov + moveProp * distLeft
                self.fov = self._EnforceMinMaxFov(fov)
                if fov != self.fov:
                    break
                if moveProp == 1.0:
                    break
                blue.synchro.Yield()

        finally:
            self.fovUpdateThread = None
            self.fovTarget = None

    def _EnforceMinMaxFov(self, value):
        if value >= self.maxFov:
            return self.maxFov
        if value <= self.minFov:
            return self.minFov
        return value

    def StopUpdateThreads(self):
        self.zoomTarget = None
        self.panTarget = None
        self.orbitTarget = None
        self.fovTarget = None

    def GetZoomDistance(self):
        dist = geo2.Vec3Distance(self._eyePosition, self._atPosition)
        if math.isinf(dist):
            log.LogException('Error: Infinite camera distance:%s, %s, %s' % (repr(self.atPosition), repr(self.eyePosition), repr(dist)))
            self.ResetCameraPosition()
            return 1.0
        return dist

    def GetZoomProportion(self):
        ret = self.GetZoomProportionUnfiltered()
        return max(0.0, min(ret, 1.0))

    def GetZoomProportionUnfiltered(self):
        dist = self.GetZoomDistance()
        ret = (dist - self.maxZoom) / (self.minZoom - self.maxZoom)
        if math.isinf(ret):
            ret = 1.0
        return ret

    def SetMaxZoom(self, value):
        self.maxZoom = value

    def SetMinZoom(self, value):
        self.minZoom = value

    def Orbit(self, dx = 0, dy = 0):
        diff = geo2.Subtract(self.eyePosition, self.atPosition)
        if not self.orbitTarget:
            self.orbitTarget = (0, self.GetAngleLookAtToUpDirection())
        yaw = self.orbitTarget[0] - dx
        pitch = self.orbitTarget[1] - dy / 2.0
        pitch = max(self.kMinPitch, min(pitch, self.kMaxPitch))
        self.orbitTarget = [yaw, pitch]
        if not self.orbitUpdateThread:
            self.orbitUpdateThread = uthread.new(self.OrbitUpdateThread)

    def OrbitUpdateThread(self):
        try:
            while True:
                if self.orbitTarget is None:
                    break
                vLookAt = self.GetLookAtDirectionWithOffset()
                currPitch = self.GetAngleLookAtToUpDirection()
                if self._atOffset:
                    offset = geo2.Vec3Add(self._atPosition, self._atOffset)
                else:
                    offset = self._atPosition
                self.eyePosition = geo2.Subtract(self._eyePosition, offset)
                yawRemaining = self._UpdateYaw()
                pitchRemaining = self._UpdatePitch(currPitch, vLookAt)
                self.eyePosition = geo2.Add(self._eyePosition, offset)
                if not pitchRemaining and not yawRemaining:
                    break
                blue.synchro.Yield()

        finally:
            self.orbitUpdateThread = None
            self.orbitTarget = None

    def _UpdatePitch(self, currPitch, vLookAt):
        targetPitch = self.orbitTarget[1]
        pitchRemaining = currPitch - targetPitch
        if pitchRemaining:
            if math.fabs(pitchRemaining) < self.kOrbitStopAngle:
                pitch = pitchRemaining
                pitchRemaining = None
            else:
                pitch = self._GetOrbitSpeed() * pitchRemaining / blue.os.fps
            axis = geo2.Vec3Cross(vLookAt, self.upDirection)
            rotPitch = geo2.MatrixRotationAxis(axis, pitch)
            self.eyePosition = geo2.Vec3Transform(self._eyePosition, rotPitch)
        return pitchRemaining

    def _GetOrbitSpeed(self):
        multiplier = self._GetCameraSpeedMultiplier()
        return self.kOrbitSpeed * multiplier

    def _GetCameraSpeedMultiplier(self):
        multiplier = settings.user.ui.Get('cameraMouseLookSpeedSlider', 0.0)
        if multiplier < 0:
            multiplier = 1.0 / (1.0 - multiplier)
        else:
            multiplier = 1.0 + multiplier
        return multiplier

    def _GetZoomSpeed(self):
        multiplier = self._GetCameraSpeedMultiplier()
        return self.kZoomSpeed * multiplier

    def _GetPanSpeed(self):
        multiplier = self._GetCameraSpeedMultiplier()
        return self.kPanSpeed * multiplier

    def _UpdateYaw(self):
        yawRemaining = self.orbitTarget[0]
        if yawRemaining:
            if math.fabs(yawRemaining) < self.kOrbitStopAngle:
                yaw = yawRemaining
                yawRemaining = None
            else:
                yaw = self._GetOrbitSpeed() * yawRemaining / blue.os.fps
            rotYaw = geo2.MatrixRotationAxis(self.upDirection, yaw)
            self.eyePosition = geo2.Vec3Transform(self._eyePosition, rotYaw)
            self.orbitTarget[0] -= yaw
        return yawRemaining

    def GetAngleLookAtToUpDirection(self):
        try:
            vLookAt = self.GetLookAtDirectionWithOffset()
            return math.acos(geo2.Vec3Dot(vLookAt, self.upDirection) / (geo2.Vec3Length(vLookAt) * geo2.Vec3Length(self.upDirection)))
        except ValueError:
            return 0.0

    def GetActiveThreads(self):
        return (self.panTarget, self.orbitTarget, self.zoomTarget)

    def Rotate(self, x = 0, y = 0):
        xAxis = self.GetXAxis()
        yAxis = self.GetYAxis()
        self.atPosition = geo2.Subtract(self._atPosition, self._eyePosition)
        rotY = geo2.MatrixRotationAxis(xAxis, y)
        self.atPosition = geo2.Vec3Transform(self._atPosition, rotY)
        rotX = geo2.MatrixRotationAxis(yAxis, x)
        self.atPosition = geo2.Vec3Transform(self._atPosition, rotX)
        self.atPosition = geo2.Add(self._atPosition, self.eyePosition)

    def GetDistanceFromLookAt(self):
        return geo2.Vec3Distance(self.eyePosition, self.atPosition)

    def LookAt(self, position, duration = None, followWithEye = True, eyePos = None):
        if duration:
            uicore.animations.MorphVector3(self, 'atPosition', self.atPosition, position, duration=duration)
        else:
            self.atPosition = position
        if followWithEye:
            if not eyePos:
                eyePos = geo2.Subtract(self.eyePosition, self.atPosition)
                eyePos = geo2.Add(eyePos, position)
            if duration:
                uicore.animations.MorphVector3(self, 'eyePosition', self.eyePosition, eyePos, duration=duration)
            else:
                self.eyePosition = eyePos

    def TransitTo(self, atPosition = None, eyePosition = None, duration = 1.0, smoothing = 0.1, numPoints = 1000, timeOffset = 0.0):
        self.Transit(self.atPosition, self.eyePosition, atPosition, eyePosition, duration, smoothing, numPoints, timeOffset)

    def Transit(self, atPos0, eyePos0, atPos1, eyePos1, duration = 1.0, smoothing = 0.1, numPoints = 1000, timeOffset = 0.0, callback = None):
        newDir = geo2.Vec3Direction(eyePos1, atPos1)
        self.StopEyeAndAtAnimation()
        if self._transitOffset:
            atPos0 = geo2.Vec3Add(atPos0, self._transitOffset)
        self._ConstructScalarCurve(duration)
        atPoints = self.GetTransitAtCurve(eyePos0, atPos0, atPos1, newDir, smoothing, numPoints=numPoints)
        eyePoints = self.GetTransitEyeCurve(eyePos0, atPos0, eyePos1, atPos1, newDir, atPoints)
        atPoints = [ geo2.Vec3Subtract(p, atPoints[-1]) for p in atPoints ]
        self._transitOffset = atPoints[0]
        self._atPosition = atPos1
        self._eyePosition = eyePos0
        uicore.animations.MorphVector3(self, '_transitOffset', curveType=atPoints, duration=duration, timeOffset=timeOffset, callback=self.OnTransitEnd)
        uicore.animations.MorphVector3(self, 'eyePosition', curveType=eyePoints, duration=duration, timeOffset=timeOffset, callback=callback)

    def StopEyeAndAtAnimation(self):
        uicore.animations.StopAnimation(self, 'atPosition')
        uicore.animations.StopAnimation(self, 'eyePosition')
        uicore.animations.StopAnimation(self, '_transitOffset')
        self._transitOffset = None
        self.panTarget = None
        self.orbitTarget = None
        self.zoomTarget = None

    def IsInTransit(self):
        return self._transitOffset is not None

    def OnTransitEnd(self):
        self._transitOffset = None

    def GetTransitAtCurve(self, eyePos0, atPos0, atPos1, newDir, smoothing, numPoints):
        currDir = geo2.Vec3Direction(eyePos0, atPos0)
        angle = math.acos(geo2.Vec3Dot((currDir[0], 0, currDir[2]), (newDir[1], 0, newDir[2])))
        if smoothing and angle:
            offset = geo2.Vec3Normalize(geo2.Vec3Negate(newDir))
            dist = geo2.Vec3Distance(atPos0, atPos1)
            offset = geo2.Vec3Scale(offset, dist * angle * smoothing)
        else:
            offset = (0, 0, 0)
        points = []
        for i in xrange(numPoints + 1):
            t = self._GetTimeValue(float(i) / numPoints)
            offsetDist = 2 * (t - t ** 2)
            point = geo2.Vec3Lerp(atPos0, atPos1, t)
            point = geo2.Add(point, geo2.Vec3Scale(offset, offsetDist))
            points.append(point)

        return points

    def GetTransitEyeCurve(self, eyePos0, atPos0, eyePos1, atPos1, newDir, atCurve):
        currDir = geo2.Vec3Direction(eyePos0, atPos0)
        try:
            angle = math.acos(geo2.Vec3Dot(currDir, newDir))
        except ValueError:
            angle = 0

        th0 = math.atan2(currDir[2], currDir[0])
        th0 = self.ClampAngle(th0)
        th1 = math.atan2(newDir[2], newDir[0])
        th1 = self.ClampAngle(th1)
        if th0 - th1 > math.pi:
            th0 -= 2 * math.pi
        elif th1 - th0 > math.pi:
            th1 -= 2 * math.pi
        r0 = geo2.Vec3Distance((eyePos0[0], 0, eyePos0[2]), (atPos0[0], 0, atPos0[2]))
        r1 = geo2.Vec3Distance((eyePos1[0], 0, eyePos1[2]), (atPos1[0], 0, atPos1[2]))
        y0 = eyePos0[1] - atPos0[1]
        y1 = eyePos1[1] - atPos1[1]
        points = []
        for i, atPoint in enumerate(atCurve):
            t = self._GetTimeValue(float(i) / len(atCurve))
            r = r0 + t * (r1 - r0)
            th = th0 + t * (th1 - th0)
            y = y0 + t * (y1 - y0)
            point = (r * math.cos(th), y, r * math.sin(th))
            point = geo2.Vec3Add(point, atCurve[i])
            points.append(point)

        return points

    def _GetTimeValue(self, t):
        return self._transitCurve.GetValueAt(t)

    def _ConstructScalarCurve(self, duration):
        self._transitCurve = trinity.Tr2ScalarBezierCurve()
        self._transitCurve.length = 1.0
        self._transitCurve.endValue = 1.0
        x = max(0.0, min(-0.3 + 0.6 * duration, 1.0))
        self._transitCurve.controlPointA = (0.2 + 0.2 * (1.0 - x), 0.0)
        self._transitCurve.controlPointB = (-(0.2 + x * 0.7), 0.0)

    def ClampAngle(self, angle):
        while angle < 0:
            angle += 2 * math.pi

        while angle >= 2 * math.pi:
            angle -= 2 * math.pi

        return angle

    def StopAnimations(self):
        uicore.animations.StopAllAnimations(self)

    def GetFov(self):
        return self._fov

    def SetFov(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._fov = value

    fov = property(GetFov, SetFov)

    def GetFovOffset(self):
        return self._fovOffset

    def SetFovOffset(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._fovOffset = value

    fovOffset = property(GetFovOffset, SetFovOffset)

    def GetNearClip(self):
        return self._nearClip

    def SetNearClip(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._nearClip = value

    nearClip = property(GetNearClip, SetNearClip)

    def GetFarClip(self):
        return self._farClip

    def SetFarClip(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._farClip = value

    farClip = property(GetFarClip, SetFarClip)

    def GetEyePosition(self):
        return self.OffsetEyePosition(self._eyePosition)

    def SetEyePosition(self, value):
        if self.IsNanVector3(value) or self.IsInfVector3(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign an invalid eyePosition value: %s' % repr(value))
        self._eyePosition = value

    eyePosition = property(GetEyePosition, SetEyePosition)

    def GetAtPosition(self):
        return self.OffsetAtPosition(self._atPosition)

    def SetAtPosition(self, value):
        if self.IsNanVector3(value) or self.IsInfVector3(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign an invalid atPosition value: %s' % repr(value))
        self._atPosition = value

    atPosition = property(GetAtPosition, SetAtPosition)

    def GetUpDirection(self):
        return self._upDirection

    def SetUpDirection(self, value):

        def IsNanValue(self, value):
            return math.isnan(value[0] or math.isnan(value[1]) or math.isnan(value[2]))

        self._upDirection = geo2.Vec3Normalize(value)

    upDirection = property(GetUpDirection, SetUpDirection)

    def IsNanVector3(self, values):
        for value in values:
            if math.isnan(value):
                return True

        return False

    def IsInfVector3(self, values):
        for value in values:
            if value > math.fabs(1e+38):
                return True

        return False

    def GetCameraInterestID(self):
        return None

    def ResetCamera(self):
        pass

    def ResetCameraPosition(self):
        self.atPosition = self.default_atPosition
        self.eyePosition = self.default_eyePosition
        self.fov = self.default_fov
        self.trackTarget = None
