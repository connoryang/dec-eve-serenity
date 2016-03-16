#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\tacticalCamera.py
import geo2
import math
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance, GetBallPosition, GetBall, GetBallMaxZoom, IsBallWarping, CheckShowModelTurrets
import evecamera
DEFAULT_EYEDIST = 40000
FREE_ORBIT_DIST = 250
LOOKAT_DIST = 50000

class TacticalCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_TACTICAL
    kPanSpeed = 8.0
    kOrbitSpeed = 5.0
    default_fov = 1.2
    default_atPosition = (0, 0, 0)
    default_eyePosition = (-DEFAULT_EYEDIST, DEFAULT_EYEDIST, DEFAULT_EYEDIST)
    minZoom = 250000

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lastLookAtID = None
        self.sceneCursor = (0, 0, 0)
        self.ballPosition = BallPositionAnimator()

    def GetLookAtItemID(self):
        if self.IsAttached():
            return self.GetItemID()
        else:
            return None

    def IsAttached(self):
        return self.ballPosition.IsAttached()

    def LookAt(self, itemID, allowSwitchCamera = True, **kwargs):
        if not self.IsManualControlEnabled():
            return
        if itemID == self.GetItemID():
            return
        if itemID == self.ego:
            sm.ScatterEvent('OnLookAtMyShip', itemID)
        else:
            sm.ScatterEvent('OnLookAtOther', itemID)
        self.StopUpdateThreads()
        ball = GetBall(itemID)
        if ball:
            CheckShowModelTurrets(ball)
        ballPos = GetBallPosition(ball)
        if self.CheckObjectTooFar(itemID):
            self.LookAtFar(ballPos)
            return
        eyePos1 = geo2.Vec3Subtract(self._eyePosition, self._atPosition)
        maxZoom = self.maxZoom
        if geo2.Vec3Length(eyePos1) < self.maxZoom:
            eyePos1 = geo2.Vec3Scale(geo2.Vec3Normalize(eyePos1), self.maxZoom)
        duration = GetDurationByDistance(self.ballPosition.GetPosition(), ballPos, minTime=0.3)
        uicore.animations.MorphVector3(self, '_atPosition', self._atPosition, (0, 0, 0), duration=duration)
        uicore.animations.MorphVector3(self, '_eyePosition', self._eyePosition, eyePos1, duration=duration)
        self._SetLookAtBall(ball, duration=duration)

    def _SetLookAtBall(self, ball, animate = True, duration = 0.6):
        self.ballPosition.SetBall(ball, animate=animate, duration=duration)
        if ball:
            self.UpdateMaxZoom(ball)
            self.lastLookAtID = ball.id
            sm.StartService('state').SetState(ball.id, states.lookingAt, True)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self._eyePosition = geo2.Vec3Subtract(self._eyePosition, self._atPosition)
        self._atPosition = (0, 0, 0)
        self._SetLookAtBall(None)

    def UpdateMaxZoom(self, ball):
        self.SetMaxZoom(GetBallMaxZoom(ball, self.nearClip))

    def LookAtFar(self, ballPos):
        self.Detach()
        ballDir = geo2.Vec3Normalize(ballPos)
        ballDir = geo2.Vec3Direction(ballPos, self.eyePosition)
        atPosition = geo2.Vec3Add(self._eyePosition, geo2.Vec3Scale(ballDir, self.GetZoomDistance()))
        self.Transit(self._atPosition, self._eyePosition, atPosition, self._eyePosition, duration=1.0)

    def Pan(self, dx = None, dy = None, dz = None):
        if not self.IsManualControlEnabled():
            return
        if self.IsActiveOrTrackingShipWarping():
            return
        self.Detach()
        k = 0.5 + 5 * self.GetDistanceToSceneCursor()
        BaseSpaceCamera.Pan(self, k * dx, k * dy, k * dz)

    def Detach(self):
        self.ballPosition.SetAbstractBall()
        if self.lastLookAtID:
            self.lastLookAtID = None
            self.sceneCursor = self.atPosition

    def GetDistanceToSceneCursor(self):
        anchorDist = geo2.Vec3Distance(self.eyePosition, self.sceneCursor)
        zoomProp = anchorDist / (self.minZoom - self.sceneCursor[1])
        zoomProp = max(0.0, min(math.fabs(zoomProp), 2.0))
        return zoomProp

    def ResetCamera(self, *args):
        self.LookAt(self.ego)

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_TACTICAL)
        if lastCamera and lastCamera.cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_JUMP):
            eyePos0 = lastCamera.eyePosition
            atPos0 = lastCamera.atPosition
            self._ResetEyePosition(eyePos0, atPos0)
            self.fov = lastCamera.fov
            self.SetFovTarget(self.default_fov)
            self._SetLookAtBall(GetBall(lastCamera.GetItemID()), animate=False)
        elif itemID:
            self._SetLookAtBall(GetBall(itemID))
        BaseSpaceCamera.OnActivated(self, **kwargs)

    def _GetNewDirection(self, direction):
        y = geo2.Vec2Length((direction[0], direction[2]))
        direction = (direction[0], y, direction[2])
        direction = geo2.Vec3Normalize(direction)
        return direction

    def _ResetEyePosition(self, eyePos0, atPos0):
        direction = self._GetNewDirection(geo2.Vec3Subtract(eyePos0, atPos0))
        eyePos0 = geo2.Vec3Subtract(eyePos0, atPos0)
        eyePos1 = geo2.Vec3Scale(direction, LOOKAT_DIST)
        duration = GetDurationByDistance(eyePos0, eyePos1, 0.4, 0.6)
        self._eyePosition = eyePos0
        self._atPosition = (0, 0, 0)
        self.Transit(self._atPosition, eyePos0, (0, 0, 0), eyePos1, duration=duration, callback=self.EnableManualControl)

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.IsActiveOrTrackingShipWarping():
            self.LookAt(self.ego)
        self._EnforceMaximumDistance()
        if self.ballPosition.GetItemID():
            pos = self.ballPosition.GetPosition()
            self._AddToEyeAndAtOffset(pos)

    def IsActiveOrTrackingShipWarping(self):
        return IsBallWarping(self.GetItemID()) or IsBallWarping(self.ego)

    def GetItemID(self):
        return self.ballPosition.GetItemID()

    def _EnforceMaximumDistance(self):
        maxDist = evecamera.LOOKATRANGE_MAX_NEW
        if geo2.Vec3Length(self.eyePosition) > maxDist:
            direction = geo2.Vec3Normalize(self.eyePosition)
            newEye = geo2.Vec3Scale(direction, maxDist)
            diff = geo2.Vec3Subtract(self.eyePosition, newEye)
            self._eyePosition = newEye
            self._atPosition = geo2.Vec3Subtract(self._atPosition, diff)

    def OnCurrentShipWarping(self):
        self.LookAt(self.ego)

    def Track(self, itemID = None):
        ball = GetBall(itemID)
        if not ball:
            return
        self.LookAtFar(GetBallPosition(ball))


class BallPositionAnimator(object):

    def __init__(self):
        self.ball = None
        self.oldPos = None
        self.offset = None
        self._isAttached = False

    def GetPosition(self):
        if not self.ball:
            return (0, 0, 0)
        pos = GetBallPosition(self.ball)
        if self.offset:
            pos = geo2.Vec3Add(pos, self.offset)
        return pos

    def SetBall(self, ball, animate = True, duration = 0.6):
        self._isAttached = True
        self._SetBall(ball, animate, duration)

    def _SetBall(self, ball, animate, duration):
        if ball and self.ball:
            oldPos = GetBallPosition(self.ball)
            if animate:
                self.offset = geo2.Vec3Subtract(oldPos, GetBallPosition(ball))
                uicore.animations.MorphVector3(self, 'offset', self.offset, (0, 0, 0), duration=duration, callback=self._ResetOffset)
            else:
                self.offset = None
        self.ball = ball

    def SetAbstractBall(self, animate = True, duration = 0.6):
        if not self._isAttached:
            return
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        self._isAttached = False
        pos = bp.GetCurrentEgoPos()
        if self.ball:
            pos = geo2.Vec3AddD(pos, GetBallPosition(self.ball))
        ball = bp.AddClientSideBall(pos)
        self._SetBall(ball, animate, duration)

    def IsAttached(self):
        return self._isAttached

    def _ResetOffset(self):
        self.offset = None

    def GetItemID(self):
        if self.ball:
            return self.ball.id
