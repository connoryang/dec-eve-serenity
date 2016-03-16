#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\scannerFiles\directionalScanHandler.py
from carbon.common.script.util.mathCommon import GetLesserAngleBetweenYaws
from carbon.common.script.util.mathUtil import RadToDeg
from eve.client.script.ui.camera.baseCamera import Camera
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
from eve.client.script.ui.inflight.scannerFiles.directionalScanUtil import GetActiveScanMode, SCANMODE_CAMERA, GetScanConeDisplayState
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.mapViewUtil import CreatePlanarLineSet
from eve.common.lib.appConst import AU
import blue
import math
import trinity
import weakref
import geo2
import uthread
import state
import nodemanager
MAX_SCANRANGE = 14.3 * const.AU
CONE_ROTATION_SPEED = math.pi / 2
CAMERAUPDATE_MAP_TO_SPACE = 1
CAMERAUPDATE_SPACE_TO_MAP = 2
TR2TM_NONE = 0
TR2TM_LOOK_AT_CAMERA = 3

class MapViewDirectionalScanHandler(object):
    __notifyevents__ = ['OnDirectionalScannerRangeChanged',
     'OnDirectionalScannerAngleChanged',
     'OnDirectionalScannerScanModeChanged',
     'OnDirectionalScannerShowCone']
    _systemMapHandler = None
    lineSetScaling = 1000000.0
    debugLineSet = None
    dScanTransform = None
    dScanSubTransform = None
    dScanLineSet = None

    def __init__(self, systemMapHandler):
        self.systemMapHandler = systemMapHandler
        sm.RegisterNotify(self)
        self.viewStateService = sm.GetService('viewState')
        self.sceneManager = sm.GetService('sceneManager')
        self.scanRange = settings.user.ui.Get('dir_scanrange', MAX_SCANRANGE / 1000.0) * 1000.0
        self.scanMode = None
        self.scanAngle = settings.user.ui.Get('scan_angleSlider', 360)
        self.coneLineSets = []
        uthread.new(self.DrawDirectionalScanCone)

    def StopHandler(self):
        sm.UnregisterNotify(self)
        if self.dScanTransform:
            uicore.animations.MorphVector3(self.dScanTransform, 'scaling', startVal=self.dScanTransform.scaling, endVal=(0, 0, 0), duration=0.2, callback=self._RemoveFromScene)
        else:
            self._RemoveFromScene()

    def ScanEffect(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectReturn)
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeHalfTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectHalfReturn)
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeFullTransform, 'ScanPart_01', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            duration = scanLinesCurveSet.GetMaxCurveDuration()
            scanLinesCurveSet.Play()
            scanLinesCurveSet.StopAfterWithCallback(duration, self._ScanEffectFullReturn)

    def _ScanEffectReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def _ScanEffectHalfReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeHalfTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def _ScanEffectFullReturn(self):
        scanLinesCurveSet = nodemanager.FindNode(self.scanConeFullTransform, 'ScanPart_02', 'trinity.TriCurveSet')
        if scanLinesCurveSet:
            scanLinesCurveSet.Play()

    def ChangeCircleLineAlpha(self, lineset, alpha, linequart1, linequart2, linequart3, linequart4, linebasecolor):
        if alpha is not None:
            r, g, b, a = linebasecolor
            newcolor = (r,
             g,
             b,
             alpha)
        else:
            newcolor = linebasecolor
        lineset.ChangeLineColor(linequart1, newcolor, newcolor)
        lineset.ChangeLineColor(linequart2, newcolor, newcolor)
        lineset.ChangeLineColor(linequart3, newcolor, newcolor)
        lineset.ChangeLineColor(linequart4, newcolor, newcolor)

    def _RemoveFromScene(self):
        if self.dScanTransform in self.systemMapHandler.systemMapTransform.children:
            self.systemMapHandler.systemMapTransform.children.remove(self.dScanTransform)
        self.dScanTransform = None
        self.dScanSubTransform = None
        self.dScanUpdateTimer = None
        self.systemMapHandler = None

    def GetPosition(self):
        if self.dScanTransform:
            return self.dScanTransform.translation

    def OnDirectionalScannerRangeChanged(self, scanRange):
        self.scanRange = scanRange
        self.DrawDirectionalScanCone()

    def OnDirectionalScannerAngleChanged(self, scanAngle):
        self.scanAngle = RadToDeg(scanAngle)
        self.DrawDirectionalScanCone()

    def OnDirectionalScannerScanModeChanged(self, newScanMode):
        if newScanMode != self.scanMode:
            uthread.new(self.SwitchToScanMode, newScanMode)

    def OnDirectionalScannerShowCone(self, displayState):
        if self.dScanSubTransform:
            self.dScanSubTransform.display = displayState

    def SwitchToScanMode(self, scanMode, initing = False):
        if scanMode == SCANMODE_CAMERA:
            camera = self.systemMapHandler.mapView.camera
            endRotation = self.GetSpaceCameraRotation()
            viewVector = self.GetSpaceCameraViewVector()
            if initing:
                duration = None
            else:
                cameraDuration = self.GetRotationDurationFromVectors(camera.GetViewVector(), viewVector)
                coneDuration = self.GetRotationDurationFromQuaternions(self.dScanTransform.rotation, endRotation)
                duration = max(cameraDuration, coneDuration)
            conePosition = self.dScanTransform.worldTransform[3][:3]
            camera.SetPointOfInterest(conePosition, duration=duration)
            if duration:
                uicore.animations.MorphQuaternion(self.dScanTransform, 'rotation', startVal=self.dScanTransform.rotation, endVal=endRotation, duration=duration, callback=self._OnConeAligned)
            else:
                uicore.animations.StopAnimation(self.dScanTransform, 'rotation')
                self.dScanTransform.rotation = endRotation
                self.dScanTransform.modifier = TR2TM_LOOK_AT_CAMERA
            camera.SetViewVector(viewVector, duration=duration, sleep=not initing)
            camera.SetPointOfInterestOverrideHandler(self)
            self.scanMode = scanMode
        else:
            self.scanMode = scanMode
            self.dScanTransform.modifier = TR2TM_NONE
            camera = self.systemMapHandler.mapView.camera
            camera.SetPointOfInterestOverrideHandler(None)

    def _OnConeAligned(self):
        self.dScanTransform.modifier = TR2TM_LOOK_AT_CAMERA

    def GetSpaceCameraRotation(self):
        yaw, pitch = self.spaceCameraOrbit
        return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0.0)

    def GetSpaceCameraViewVector(self):
        spaceCameraRotation = self.GetSpaceCameraRotation()
        viewVector = geo2.QuaternionTransformVector(spaceCameraRotation, (0, 0, 1))
        return viewVector

    def GetPointOfInterestOverride(self):
        return self.dScanTransform.worldTransform[3][:3]

    def SetScanTarget(self, itemID, mapPosition, callback = None):
        conePosition = self.dScanTransform.worldTransform[3][:3]
        ball = sm.GetService('michelle').GetBall(itemID)
        if not ball:
            return
        vec = ball.GetVectorAt(blue.os.GetSimTime())
        scanVector = geo2.Vec3Normalize((-vec.x, -vec.y, -vec.z))
        oldScanVector = self.GetSpaceCameraViewVector()
        try:
            uicore.animations.StopAnimation(self.dScanTransform, 'rotation')
            duration = self.GetRotationDurationFromVectors(oldScanVector, scanVector)
            self.AlignSpaceCameraToViewVector(scanVector, duration, sleep=True)
        finally:
            if callback:
                callback()

    @apply
    def spaceCameraOrbit():

        def fget(self):
            spaceCamera = self.GetSpaceCamera()
            if IsNewCameraActive():
                viewVector = spaceCamera.GetViewVector()
                rotation = geo2.QuaternionRotationArc((0, 0, 1), viewVector)
                yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(rotation)
                return (yaw, pitch)
            else:
                return (spaceCamera.yaw, spaceCamera.pitch)

        def fset(self, yaw_pitch):
            spaceCamera = self.GetSpaceCamera()
            if IsNewCameraActive():
                y, p = yaw_pitch
                rotation = geo2.QuaternionRotationSetYawPitchRoll(y, p, 0.0)
                viewVector = geo2.QuaternionTransformVector(rotation, (0, 0, 1))
                spaceCamera.SetViewVector(viewVector)
            else:
                spaceCamera.SetOrbit(*yaw_pitch)

        return property(**locals())

    def IsNewCamera(self, camera):
        return isinstance(camera, Camera)

    @apply
    def systemMapHandler():

        def fget(self):
            if self._systemMapHandler:
                return self._systemMapHandler()

        def fset(self, value):
            if value:
                self._systemMapHandler = weakref.ref(value)
            else:
                self._systemMapHandler = None

        return property(**locals())

    def DrawDirectionalScanCone(self):
        scanAngle = self.scanAngle
        scanRange = float(self.scanRange)
        systemMapHandler = self.systemMapHandler
        if not systemMapHandler:
            return
        if self.dScanLineSet is None:
            self.dScanTransform = trinity.EveTransform()
            self.dScanTransform.name = 'dScanTransform'
            systemMapHandler.systemMapTransform.children.append(self.dScanTransform)
            systemMapHandler.SetupMyPositionTracker(self.dScanTransform)
            self.dScanSubTransform = trinity.EveTransform()
            self.dScanSubTransform.name = 'dScanSubTransform'
            self.dScanSubTransform.display = GetScanConeDisplayState()
            self.dScanTransform.children.append(self.dScanSubTransform)
            scanCone = trinity.Load('res:/dx9/model/UI/scancone.red')
            scanCone.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, -math.pi / 2, 0.0)
            self.dScanSubTransform.children.append(scanCone)
            self.scanConeTransform = scanCone
            scanConeHalf = trinity.Load('res:/dx9/model/UI/scanconehalfsphere.red')
            self.dScanSubTransform.children.append(scanConeHalf)
            self.scanConeHalfTransform = scanConeHalf
            scanConeFull = trinity.Load('res:/dx9/model/UI/scanconesphere.red')
            self.dScanSubTransform.children.append(scanConeFull)
            self.scanConeFullTransform = scanConeFull
            lineSet = CreatePlanarLineSet(texturePath='res:/dx9/texture/ui/linePlanarSmoothAdditive.dds')
            lineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
            lineSet.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, -math.pi / 2, 0.0)
            lineSet.additive = True
            self.dScanSubTransform.children.append(lineSet)
            self.dScanLineSet = lineSet
            blue.synchro.Yield()
            self.SwitchToScanMode(GetActiveScanMode(), initing=True)
        else:
            lineSet = self.dScanLineSet
        lineSet.ClearLines()
        if scanAngle < 180.0:
            scanAngleRad = math.radians(scanAngle)
            scanAngleCos = math.cos(scanAngleRad * 0.5)
            lineWidth = 5000.0
            color = (0.1, 0.4, 0.6, 0.125)
            centerLineDistance = AU
            while centerLineDistance < scanRange:
                step = centerLineDistance * scanAngleCos
                radius = math.tan(scanAngleRad * 0.5) * step
                lineIDs = mapViewUtil.DrawCircle(lineSet, (0, step / self.lineSetScaling, 0), radius / self.lineSetScaling, lineWidth=lineWidth, startColor=color, endColor=color)
                centerLineDistance += const.AU

            self.scanConeHalfTransform.display = False
            self.scanConeFullTransform.display = False
            z = scanRange * scanAngleCos
            endCapAngle = scanAngleRad * 0.5
            radius = scanRange * math.sin(endCapAngle)
            self.scanConeTransform.scaling = (radius * 2, z, radius * 2)
            self.scanConeTransform.display = True
        elif scanAngle < 360.0:
            self.scanConeTransform.display = False
            self.scanConeFullTransform.display = False
            self.scanConeHalfTransform.scaling = (-scanRange, -scanRange, -scanRange)
            self.scanConeHalfTransform.display = True
        else:
            self.scanConeTransform.display = False
            self.scanConeHalfTransform.display = False
            self.scanConeFullTransform.scaling = (-scanRange, -scanRange, -scanRange)
            self.scanConeFullTransform.display = True
        lineSet.SubmitChanges()

    def GetSpaceCamera(self):
        return self.sceneManager.GetActiveSpaceCamera()

    def OnCameraMoved(self):
        if not self.dScanTransform or not self.GetSpaceCamera():
            return
        self.dScanTransform.rotation = self.GetSpaceCameraRotation()
        camera = self.systemMapHandler.mapView.camera
        if self.scanMode == SCANMODE_CAMERA:
            followSpaceCamera = not bool(camera.GetCapture())
            if followSpaceCamera:
                viewVector = self.GetSpaceCameraViewVector()
                camera.SetViewVector(viewVector)
            else:
                viewVector = camera.GetViewVector()
                self.AlignSpaceCameraToViewVector(viewVector)

    def AlignSpaceCameraToViewVector(self, viewVector, duration = None, callback = None, sleep = False):
        rotation = geo2.QuaternionRotationArc((0, 0, 1), viewVector)
        y, p, r = geo2.QuaternionRotationGetYawPitchRoll(rotation)
        if duration:
            currentYaw, currentPitch = self.spaceCameraOrbit
            yawDiff = GetLesserAngleBetweenYaws(currentYaw, y)
            pitchDiff = GetLesserAngleBetweenYaws(currentPitch, p)
            endVal = (currentYaw + yawDiff, currentPitch + pitchDiff)
            uicore.animations.MorphVector2(self, 'spaceCameraOrbit', startVal=(currentYaw, currentPitch), endVal=endVal, duration=duration, callback=callback, sleep=sleep)
        else:
            uicore.animations.StopAnimation(self, 'spaceCameraOrbit')
            self.spaceCameraOrbit = (y, p)

    def GetRotationDurationFromVectors(self, startVec, endVec):
        dotProduct = geo2.Vec3Dot(startVec, endVec)
        try:
            angle = math.acos(dotProduct)
        except ValueError:
            angle = 0.5

        return max(0.01, angle / CONE_ROTATION_SPEED)

    def GetRotationDurationFromQuaternions(self, startRotation, endRotation):
        startVec = geo2.QuaternionTransformVector(startRotation, (0, 0, 1))
        endVec = geo2.QuaternionTransformVector(endRotation, (0, 0, 1))
        return self.GetRotationDurationFromVectors(startVec, endVec)
