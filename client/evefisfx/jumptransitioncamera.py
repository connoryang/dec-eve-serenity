#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evefisfx\jumptransitioncamera.py
import blue
import carbon.common.script.util.mathUtil as mathUtil
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
import evecamera
import evecamera.animation as camanim
import evecamera.utils as camutils
import geo2
import math
import trinity
import uthread2
import eve.client.script.parklife.states as states

class LookAnimation(object):
    __guid__ = 'effects.JumpTransitionLookAnimation'

    def __init__(self, camera, rotation, startFocusID = None, endFocusID = None, startTranslation = None, endTranslation = None):
        self.camera = camera
        self.rotation = rotation
        self.startBall = None
        self.endTranslationFromParent = endTranslation
        self.startTranslation = startTranslation
        self.startFocusID = startFocusID
        self.endFocusID = endFocusID
        self.cameraIntroTime = 2.0
        self.cameraOutroDelay = 1.0
        self.ending = False

    def _GetFocusPosition(self):
        if self.startFocusID is None:
            return (0, 0, 0)
        park = sm.GetService('michelle').GetBallpark()
        if park is None:
            return (0, 0, 0)
        ball = park.GetBall(self.startFocusID)
        if ball is None:
            return (0, 0, 0)
        pos = ball.GetVectorAt(blue.os.GetSimTime())
        return (pos.x, pos.y, pos.z)

    def Stop(self):
        self.ending = True
        if IsNewCameraActive():
            self.camera.EnableManualControl()

    def Start(self):
        self.ending = False
        if IsNewCameraActive():
            self.camera.DisableManualControl()
            uthread2.StartTasklet(self._DoCameraLookAnimation_Thread_New)
        else:
            uthread2.StartTasklet(self._DoCameraLookAnimation_Thread)

    def _DoCameraLookAnimation_Thread_New(self):
        self.camera.targetTracker.TrackItem(None)
        self.camera.SetCameraInterest(None)
        targetTranslation = self.startTranslation
        direction = geo2.Vec3Scale(geo2.QuaternionTransformVector(self.rotation, (0, 0, 1)), -2 * targetTranslation)
        atPosition = self._GetFocusPosition()
        eyePosition = geo2.Vec3Add(atPosition, direction)
        self.camera.TransitTo(atPosition, eyePosition)

    def _DoCameraLookAnimation_Thread(self):
        self.camera.targetTracker.TrackItem(None)
        self.camera.SetCameraInterest(None)
        lookDir = geo2.QuaternionTransformVector(self.rotation, (0, 0, 1))
        lookDir = trinity.TriVector(lookDir[0], lookDir[1], lookDir[2])
        initialTranslation = self.camera.translationFromParent
        targetTranslation = initialTranslation
        if self.startTranslation is not None:
            targetTranslation = self.startTranslation
        startTime = blue.os.GetSimTime()
        endedTime = None
        maxPanSpeed = math.pi / 500
        panCurve = uicore.animations.GetScalar(0, maxPanSpeed, self.cameraIntroTime * 0.9)
        posLerpCurve = uicore.animations.GetScalar(0.0, 1.0, self.cameraIntroTime * 0.9)
        dir = geo2.Vec3Scale(geo2.QuaternionTransformVector(self.rotation, (0, 0, 1)), -targetTranslation)
        self.lookAtAnim = AnimateGateLookAt(self._GetFocusPosition, dir, posLerpCurve)
        self.camera.animationController.Schedule(self.lookAtAnim)
        self.panAnim = AnimateGatePan(initialTranslation, posLerpCurve)
        self.camera.animationController.Schedule(self.panAnim)
        self.panAnimEnd = camutils.PanCamera(targetTranslation, initialTranslation, self.cameraOutroDelay * 0.9)
        while True:
            blue.synchro.Yield()
            curTime = blue.os.GetSimTime()
            if not getattr(self, 'lastTime', None):
                self.lastTime = curTime
                continue
            timeDelta = blue.os.TimeDiffInMs(self.lastTime, curTime)
            self.lastTime = curTime
            t = blue.os.TimeDiffInMs(startTime, curTime) / 1000.0
            panSpeed = maxPanSpeed
            if t < self.cameraIntroTime:
                panSpeed = panCurve.GetValueAt(t)
            self.camera.targetTracker.tracking = None
            self.camera.targetTracker.PointCameraToPos(self.camera, trinity.TriVector(0, 0, 0), lookDir, panSpeed, timeDelta)
            if self.ending and endedTime is None:
                self.lookAtAnim.Stop()
                self.panAnim.Stop()
                self.camera.animationController.Schedule(self.panAnimEnd)
                endedTime = curTime
            elif endedTime is not None:
                if self.endFocusID is None:
                    break
                timeSinceEnd = blue.os.TimeDiffInMs(endedTime, curTime) / 1000.0
                if timeSinceEnd >= self.cameraOutroDelay:
                    itemID = self.GetJumpEndLookAtID()
                    if itemID is not None:
                        sm.GetService('state').SetState(itemID, states.selected, 1)
                        self.camera.targetTracker.SetTemporaryTrackSpeed(itemID, math.pi / 4000)
                    break

    def GetJumpEndLookAtID(self):
        lookatID = self.endFocusID
        autoPilot = sm.GetService('autoPilot')
        starmapSvc = sm.GetService('starmap')
        destinationPath = starmapSvc.GetDestinationPath()
        if destinationPath is not None and len(destinationPath) > 0 and destinationPath[0] is not None:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is not None:
                destID, destItem = autoPilot.GetGateOrStation(bp, destinationPath[0])
                if destID is not None:
                    lookatID = destID
        return lookatID


class AnimateGatePan(camanim.BaseCameraAnimation):

    def __init__(self, initialTranslation, progressCurve):
        camanim.BaseCameraAnimation.__init__(self, camanim.PAN_ANIMATION, 0, evecamera.PRIORITY_HIGH, False)
        self.initialTranslation = initialTranslation
        self.progressCurve = progressCurve

    def Tick(self, camera, simTime, clockTime):
        t = blue.os.TimeDiffInMs(self.timeStart, simTime) / 1000.0
        progress = self.progressCurve.GetValueAt(t)
        camera.translationFromParent = mathUtil.Lerp(self.initialTranslation, 0, progress)

    def Stop(self):
        self.isDone = True


class AnimateGateLookAt(camanim.BaseCameraAnimation):

    def __init__(self, endPosFunction, translationOffset, progressCurve):
        camanim.BaseCameraAnimation.__init__(self, camanim.TRANSLATION_ANIMATION, 0, evecamera.PRIORITY_HIGH, False)
        self.startPos = (0.0, 0.0, 0.0)
        self.progressCurve = progressCurve
        self.started = False
        self.translationOffset = translationOffset
        self.endPosFunction = endPosFunction

    def _FirstTick(self, cameraParent, simTime):
        self.started = True
        if cameraParent.translationCurve is not None:
            self.startPos = cameraParent.translationCurve.GetVectorAt(simTime)
            self.startPos = (self.startPos.x, self.startPos.y, self.startPos.z)
            cameraParent.translationCurve = None
        else:
            self.startPos = cameraParent.translation

    def Tick(self, camera, simTime, clockTime):
        if self.isDone:
            return
        t = blue.os.TimeDiffInMs(self.timeStart, simTime) / 1000.0
        progress = self.progressCurve.GetValueAt(t)
        cameraParent = camera.GetCameraParent()
        if not self.started:
            self._FirstTick(cameraParent, simTime)
            self.started = True
        endPos = self.endPosFunction()
        endPos = geo2.Vec3Add(endPos, self.translationOffset)
        cameraParent.translation = geo2.Vec3Lerp(self.startPos, endPos, progress)

    def Stop(self):
        self.isDone = True


class OutFOV(camanim.BaseCameraAnimation):

    def __init__(self, duration):
        camanim.BaseCameraAnimation.__init__(self, camanim.FOV_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.fovStart = 1
        self.fovEnd = 2.2
        self.animationStartsAt = 0.3

    def Start(self, camera, simTime, clockTime):
        camanim.BaseCameraAnimation.Start(self, camera, simTime, clockTime)
        self.fovStart = camera.fov

    def _Tick(self, progress, camera):
        progress = max(0, (progress - self.animationStartsAt) / (1 - self.animationStartsAt))
        camera.fov = mathUtil.Lerp(self.fovStart, self.fovEnd, 1.0 - math.pow(1.0 - progress, 2.0))

    def End(self, camera):
        camera.fov = self.fovEnd


class OutExtraTransl(camanim.BaseCameraAnimation):

    def __init__(self, duration, finalOffset):
        camanim.BaseCameraAnimation.__init__(self, camanim.EXTRA_TRANSLATION_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.finalOffset = finalOffset

    def _Tick(self, progress, camera):
        transl = geo2.Vec3Lerp((0, 0, 0), self.finalOffset, math.pow(progress, 4.0))
        if IsNewCameraActive():
            camera.SetEffectOffset(transl)
        else:
            camera.extraTranslation = transl

    def End(self, camera):
        if IsNewCameraActive():
            camera.SetEffectOffset(self.finalOffset)
        else:
            camera.extraTranslation = self.finalOffset


class InFOV(camanim.BaseCameraAnimation):

    def __init__(self, duration):
        camanim.BaseCameraAnimation.__init__(self, camanim.FOV_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.fovStart = 2.2
        self.fovEnd = 1.0
        self.animationStartsAt = 0.3

    def Start(self, camera, simTime, clockTime):
        camanim.BaseCameraAnimation.Start(self, camera, simTime, clockTime)
        self.fovStart = camera.fov

    def _Tick(self, progress, camera):
        progress = math.pow(progress, 4.0)
        camera.fov = mathUtil.Lerp(self.fovStart, self.fovEnd, progress)

    def End(self, camera):
        camera.fov = self.fovEnd


class InExtraTransl(camanim.BaseCameraAnimation):

    def __init__(self, duration, offset):
        camanim.BaseCameraAnimation.__init__(self, camanim.EXTRA_TRANSLATION_ANIMATION, duration, evecamera.PRIORITY_HIGH, False)
        self.offset = offset

    def _Tick(self, progress, camera):
        offset = geo2.Vec3Lerp(self.offset, (0, 0, 0), math.pow(progress, 2.0))
        if IsNewCameraActive():
            camera.SetEffectOffset(offset)
        else:
            camera.extraTranslation = offset

    def End(self, camera):
        offset = (0, 0, 0)
        if IsNewCameraActive():
            camera.SetEffectOffset(offset)
        else:
            camera.extraTranslation = offset
