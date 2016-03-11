#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewCameraHandler.py
from carbon.common.script.util.mathCommon import GetYawAndPitchAnglesRad, GetLesserAngleBetweenYaws
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
import uthread
import blue
import geo2
import math
import trinity
import weakref

class MapViewCamera(object):
    fieldOfView = 0.7
    frontClip = 1.0
    backClip = mapViewConst.MAX_CAMERA_DISTANCE
    minDistance = mapViewConst.MIN_CAMERA_DISTANCE
    maxDistance = mapViewConst.MAX_CAMERA_DISTANCE
    cameraCenter = (0.5, 0.5)
    cameraCapture = None
    _pointOfInterest = (0, 0, 0)
    _pointOfInterestCurrent = _pointOfInterest
    _pointOfInterestOverrideHandler = None
    _eyePosition = geo2.Vec3Scale(geo2.Vec3Normalize((0, 1.0, -1.0)), mapViewConst.MAX_CAMERA_DISTANCE)
    _eyePositionCurrent = _eyePosition
    _yawSpeed = 0.0
    _pitchSpeed = 0.0
    callback = None
    followMarker = None
    upVector = (0, 1, 0)
    debugRenderer = None

    def __init__(self, *args, **kwds):
        self.viewport = None
        self.viewMatrix = trinity.TriView()
        self.projectionMatrix = trinity.TriProjection()
        self.enabled = True
        uthread.new(self.UpdateTick)

    def SetCapture(self, uiObject):
        self.cameraCapture = weakref.ref(uiObject)

    def ReleaseCapture(self, uiObject):
        capture = self.GetCapture()
        if capture is uiObject:
            self.cameraCapture = None

    def GetCapture(self):
        if self.cameraCapture:
            cameraCapture = self.cameraCapture()
            if cameraCapture and not cameraCapture.destroyed:
                return cameraCapture

    def SetDebugRenderer(self, debugRenderer):
        self.debugRenderer = debugRenderer

    def GetProjectionViewViewPort(self):
        return (self.projectionMatrix, self.viewMatrix, self.viewport)

    def GetRayAndPointFromUI(self, x, y, projection2view = None, view2world = None):
        viewport = self.viewport
        mx = x - viewport.x
        my = y - viewport.y
        w = viewport.width
        h = viewport.height
        fx = float(mx * 2) / w - 1.0
        fy = float(my * 2) / h - 1.0
        fy *= -1
        projection2view = projection2view or geo2.MatrixInverse(self.projectionMatrix.transform)
        view2world = view2world or geo2.MatrixInverse(self.viewMatrix.transform)
        rayStart = (fx, fy, 0.0)
        rayStart = geo2.Vec3TransformCoord(rayStart, projection2view)
        rayStart = geo2.Vec3TransformCoord(rayStart, view2world)
        rayEnd = (fx, fy, 1.0)
        rayEnd = geo2.Vec3TransformCoord(rayEnd, projection2view)
        rayEnd = geo2.Vec3TransformCoord(rayEnd, view2world)
        rayDir = geo2.Vec3SubtractD(rayEnd, rayStart)
        return (geo2.Vec3NormalizeD(rayDir), rayStart)

    def GetUIPositionFromWorldPosition(self, worldPosition):
        worldPosition = geo2.Vec3TransformCoord(worldPosition, self.viewMatrix.transform)
        worldPosition = geo2.Vec3TransformCoord(worldPosition, self.projectionMatrix.transform)
        worldPosition = geo2.Vector(*worldPosition)
        x = 0.5 + worldPosition.x * 0.5
        y = 1.0 - (0.5 + worldPosition.y * 0.5)
        return (x * self.viewport.width, y * self.viewport.height)

    def GetLocalMousePosition(self):
        projection, view, viewport = self.GetProjectionViewViewPort()
        return (uicore.uilib.x - viewport.x, uicore.uilib.y - viewport.y)

    def Close(self):
        self.enabled = False
        self.callback = None

    def SetCallback(self, callback):
        self.callback = callback

    def SetViewPort(self, viewport):
        self.viewport = viewport

    def UpdateTick(self):
        while self.enabled:
            self.Update()
            blue.synchro.Sleep(15)

    @apply
    def pointOfInterest():

        def fget(self):
            return self._pointOfInterestCurrent

        def fset(self, value):
            self._pointOfInterest = value
            self._pointOfInterestCurrent = value

        return property(**locals())

    @apply
    def rotationAroundInterest():

        def fget(self):
            viewVectorNormalized = geo2.Vec3Normalize(self._eyePositionCurrent)
            rotation = geo2.QuaternionRotationArc((1.0, 0.0, 0.0), viewVectorNormalized)
            return rotation

        def fset(self, rotationQuaternion):
            rotationMatrix = geo2.MatrixRotationQuaternion(rotationQuaternion)
            transformedVec = geo2.Vec3Transform((1.0, 0.0, 0.0), rotationMatrix)
            cameraDistance = geo2.Vec3Length(self._eyePositionCurrent)
            self._eyePositionCurrent = geo2.Vec3Scale(transformedVec, cameraDistance)
            self._eyePosition = self._eyePositionCurrent

        return property(**locals())

    def Update(self):
        pointOfInterestOverrideValue = self.GetPointOfInterestOverrideValue()
        if pointOfInterestOverrideValue is not None:
            self._pointOfInterest = pointOfInterestOverrideValue
        elif self.followMarker:
            followMarker = self.followMarker()
            if followMarker:
                markerPosition = followMarker.GetDisplayPosition()
                if markerPosition is not None:
                    self._pointOfInterest = markerPosition
        speedFactor = 0.4
        diff = geo2.Vec3Subtract(self._pointOfInterest, self._pointOfInterestCurrent)
        diffLength = geo2.Vec3Length(diff)
        if diffLength > 0.001:
            addVector = geo2.Vec3ScaleD(diff, speedFactor)
            newPosition = geo2.Vec3Add(self._pointOfInterestCurrent, addVector)
            if geo2.Vec3Equal(newPosition, self._pointOfInterestCurrent):
                newPosition = self._pointOfInterest
            self._pointOfInterestCurrent = newPosition
        else:
            self._pointOfInterestCurrent = self._pointOfInterest
        if abs(self._yawSpeed) > 0.0001:
            yawChange = self._yawSpeed * speedFactor
            rotYaw = geo2.MatrixRotationAxis(self.upVector, yawChange)
            self._eyePositionCurrent = geo2.Vec3Transform(self._eyePositionCurrent, rotYaw)
            currentPositionN = geo2.Vec3Normalize(self._eyePositionCurrent)
            self._eyePosition = geo2.Vec3Scale(currentPositionN, geo2.Vec3Length(self._eyePosition))
            self._yawSpeed -= yawChange
        else:
            self._yawSpeed = 0.0
        if abs(self._pitchSpeed) > 0.0001:
            pitchChange = self._pitchSpeed * speedFactor
            viewVectorNormalized = geo2.Vec3Normalize(self._eyePositionCurrent)
            axis = geo2.Vec3Cross(viewVectorNormalized, self.upVector)
            rotPitch = geo2.MatrixRotationAxis(axis, pitchChange)
            self._eyePositionCurrent = geo2.Vec3Transform(self._eyePositionCurrent, rotPitch)
            currentPositionN = geo2.Vec3NormalizeD(self._eyePositionCurrent)
            self._eyePosition = geo2.Vec3ScaleD(currentPositionN, geo2.Vec3Length(self._eyePosition))
            self._pitchSpeed -= pitchChange
        else:
            self._pitchSpeed = 0.0
        setCameraDistance = geo2.Vec3Length(self._eyePosition)
        currentCameraDistance = geo2.Vec3Length(self._eyePositionCurrent)
        cameraDistanceDiff = setCameraDistance - currentCameraDistance
        if math.fabs(cameraDistanceDiff) > 0.001:
            usedDist = cameraDistanceDiff * speedFactor * 0.5
            viewVectorNormalized = geo2.Vec3NormalizeD(self._eyePositionCurrent)
            newDistance = min(self.maxDistance, max(self.minDistance, currentCameraDistance + usedDist))
            self._eyePositionCurrent = geo2.Vec3ScaleD(viewVectorNormalized, newDistance)
        self.UpdateProjection()
        self.UpdateView()
        if self.callback:
            self.callback()

    def UpdateProjection(self):
        if self.viewport:
            aspectRatio = self.viewport.GetAspectRatio()
        else:
            aspectRatio = uicore.uilib.desktop.width / float(uicore.uilib.desktop.height)
        centerX, centerY = self.cameraCenter
        dX = aspectRatio * self.frontClip * math.tan(self.fieldOfView / 2)
        dY = self.frontClip * math.tan(self.fieldOfView / 2)
        offsetX = (1.0 - centerX) * 2 - 1.0
        offsetY = centerY * 2 - 1.0
        left = -dX + dX * offsetX
        right = dX + dX * offsetX
        top = dY + dY * offsetY
        bottom = -dY + dY * offsetY
        self.projectionMatrix.PerspectiveOffCenter(left, right, bottom, top, self.frontClip, self.backClip)

    def UpdateView(self):
        self.viewMatrix.SetLookAtPosition(geo2.Vec3Add(self._eyePositionCurrent, self._pointOfInterestCurrent), self._pointOfInterestCurrent, self.upVector)

    def GetEyePosition(self):
        return geo2.Vec3Add(self._eyePositionCurrent, self._pointOfInterestCurrent)

    def GetPointOfInterest(self):
        return self._pointOfInterestCurrent

    def GetXAxis(self):
        t = self.viewMatrix.transform
        return geo2.Vec3NormalizeD((t[0][0], t[1][0], t[2][0]))

    def GetYAxis(self):
        t = self.viewMatrix.transform
        return geo2.Vec3NormalizeD((t[0][1], t[1][1], t[2][1]))

    def GetZAxis(self):
        t = self.viewMatrix.transform
        return geo2.Vec3NormalizeD((t[0][2], t[1][2], t[2][2]))

    def GetViewVector(self):
        t = geo2.MatrixInverse(self.viewMatrix.transform)
        ret = geo2.Vec3NormalizeD((t[2][0], t[2][1], t[2][2]))
        return ret

    def GetYawPitch(self):
        rotMatrix = geo2.MatrixTranspose(self.viewMatrix.transform)
        quat = geo2.QuaternionRotationMatrix(rotMatrix)
        yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(quat)
        yaw = math.pi / 2 - yaw
        pitch = math.pi / 2 - pitch
        return (yaw, pitch)

    def OrbitMouseDelta(self, dx = 0, dy = 0):
        yaw, pitch = self.GetYawPitch()
        self._yawSpeed -= dx * self.fieldOfView * 0.005
        pitchSpeed = self._pitchSpeed + dy * self.fieldOfView * 0.005
        endPitch = max(0.01, min(pitchSpeed + pitch, math.pi - 0.01))
        pitchSpeed -= pitchSpeed + pitch - endPitch
        self._pitchSpeed = pitchSpeed

    def SetPointOfInterest(self, pointOfInterest, duration = None, callback = None, sleep = False):
        if duration:
            uicore.animations.MorphVector3(self, 'pointOfInterest', startVal=self.pointOfInterest, endVal=pointOfInterest, duration=duration, callback=callback, sleep=sleep)
        else:
            self.pointOfInterest = pointOfInterest

    def SetViewVector(self, viewVector, duration = None, callback = None, sleep = False):
        endRotation = geo2.QuaternionRotationArc((1.0, 0.0, 0.0), viewVector)
        if duration:
            curveSet = uicore.animations.MorphQuaternion(self, 'rotationAroundInterest', startVal=self.rotationAroundInterest, endVal=endRotation, duration=duration, callback=callback, sleep=sleep)
        else:
            uicore.animations.StopAnimation(self, 'rotationAroundInterest')
            self.rotationAroundInterest = endRotation

    def SetPointOfInterestOverrideHandler(self, handler):
        if handler:
            self._pointOfInterestOverrideHandler = weakref.ref(handler)
        else:
            self._pointOfInterestOverrideHandler = None

    def GetPointOfInterestOverrideValue(self):
        if self._pointOfInterestOverrideHandler:
            handler = self._pointOfInterestOverrideHandler()
            if handler:
                return handler.GetPointOfInterestOverride()

    def ZoomMouseWheelDelta(self, dz, immediate = True):
        dz = dz / 500.0
        setCameraDistance = max(self.minDistance, geo2.Vec3Length(self._eyePosition))
        self.ZoomToDistance(setCameraDistance + dz * setCameraDistance, immediate)

    def ZoomMouseDelta(self, dx, dy, immediate = True):
        dz = -dy / 100.0
        setCameraDistance = geo2.Vec3Length(self._eyePosition)
        self.ZoomToDistance(setCameraDistance + dz * setCameraDistance, immediate)

    def SetMinCameraDistanceFromInterest(self, minDistance):
        setCameraDistance = geo2.Vec3Length(self._eyePosition)
        refresh = setCameraDistance < minDistance
        self.minDistance = minDistance
        if refresh:
            self.ZoomToDistance(minDistance)

    def ZoomToDistance(self, endCameraDistance, immediate = True):
        endCameraDistance = min(self.maxDistance, max(self.minDistance, endCameraDistance))
        eyePositionNorm = geo2.Vec3NormalizeD(self._eyePosition)
        self._eyePosition = geo2.Vec3ScaleD(eyePositionNorm, endCameraDistance)
        if immediate:
            self._eyePositionCurrent = self._eyePosition

    def GetCameraDistanceFromInterest(self):
        return geo2.Vec3Length(self._eyePositionCurrent)

    def FollowMarker(self, markerObject):
        if markerObject:
            self.followMarker = weakref.ref(markerObject)
        else:
            self.followMarker = None

    def ClampAngle(self, angle):
        while angle < 0:
            angle += 2 * math.pi

        while angle >= 2 * math.pi:
            angle -= 2 * math.pi

        return angle

    def RegisterCameraSettings(self, settingsID):
        cameraSettings = self.GetCameraSettings()
        all = settings.char.ui.Get(mapViewConst.MAPVIEW_CAMERA_SETTINGS, {})
        all[settingsID] = cameraSettings
        settings.char.ui.Set(mapViewConst.MAPVIEW_CAMERA_SETTINGS, all)

    def LoadRegisteredCameraSettings(self, settingsID):
        all = settings.char.ui.Get(mapViewConst.MAPVIEW_CAMERA_SETTINGS, {})
        if settingsID in all and all[settingsID]:
            cameraSettings = all[settingsID]
            self._pointOfInterest = cameraSettings['pointOfInterest']
            self._pointOfInterestCurrent = self._pointOfInterest
            self._eyePosition = cameraSettings['eyePosition']
            if geo2.Vec3Length(self._eyePosition) == 0:
                self._eyePosition = geo2.Vec3Scale(geo2.Vec3Normalize((0, 1.0, -1.0)), self.maxDistance)
            self._eyePositionCurrent = self._eyePosition
            return True
        return False

    def GetCameraSettings(self):
        cameraSettings = {}
        cameraSettings['fieldOfView'] = self.fieldOfView
        cameraSettings['frontClip'] = self.frontClip
        cameraSettings['backClip'] = self.backClip
        cameraSettings['pointOfInterest'] = self._pointOfInterest
        cameraSettings['eyePosition'] = self._eyePosition
        return cameraSettings
