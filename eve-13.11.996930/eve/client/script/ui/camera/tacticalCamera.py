#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\tacticalCamera.py
import blue
import geo2
import math
import destiny
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetDurationByDistance
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
        self.lastLookAtTime = None
        self.lastLookAtID = None
        self.sceneCursor = (0, 0, 0)

    def SetFixedAtPosition(self):
        vec = geo2.Vec3Direction(self.atPosition, self.eyePosition)
        zoomVec = geo2.Vec3Scale(vec, FREE_ORBIT_DIST)
        self.atPosition = geo2.Vec3Add(self.eyePosition, zoomVec)
        self.lastLookAtID = None

    def LookingAt(self):
        return None

    def GetCameraInterestID(self):
        return None

    def LookAt(self, itemID, allowSwitchCamera = True):
        if not self.IsManualControlEnabled():
            return
        ball = self.GetBall(itemID)
        if not ball:
            return
        ballPos = self.GetBallPosition(ball)
        if self._eyeAndAtOffset:
            ballPos = geo2.Vec3Subtract(ballPos, self._eyeAndAtOffset)
        if self.CheckObjectTooFar(itemID):
            self.LookAtFar(ballPos)
            return
        if itemID == self.lastLookAtID and self.lastLookAtTime and allowSwitchCamera:
            if blue.os.GetWallclockTime() - self.lastLookAtTime < 5 * SEC:
                sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_SHIPORBIT, itemID=itemID)
                return
        self.lastLookAtID = itemID
        self.lastLookAtTime = blue.os.GetWallclockTime()
        lookDir = self.GetLookAtDirectionWithOffset()
        atPos1 = ballPos
        currDist = geo2.Vec3Distance(self.eyePosition, ballPos)
        eyePos1 = geo2.Vec3Add(ballPos, geo2.Vec3Scale(lookDir, min(currDist, LOOKAT_DIST)))
        self.StopEyeAndAtAnimation()
        duration = GetDurationByDistance(self.eyePosition, eyePos1, minTime=0.4)
        uicore.animations.MorphVector3(self, 'atPosition', self._atPosition, atPos1, duration=duration)
        uicore.animations.MorphVector3(self, 'eyePosition', self._eyePosition, eyePos1, duration=duration)

    def LookAtFar(self, ballPos):
        ballDir = geo2.Vec3Normalize(ballPos)
        atPosition = geo2.Vec3Add(self._eyePosition, geo2.Vec3Scale(ballDir, self.GetZoomDistance()))
        self.Transit(self._atPosition, self._eyePosition, atPosition, self._eyePosition, duration=1.0)

    def Pan(self, dx = None, dy = None, dz = None):
        if not self.IsManualControlEnabled():
            return
        if self.lastLookAtID:
            self.lastLookAtID = None
            self.sceneCursor = self.atPosition
        k = 0.5 + 5 * self.GetDistanceToSceneCursor()
        BaseSpaceCamera.Pan(self, k * dx, k * dy, k * dz)

    def GetDistanceToSceneCursor(self):
        anchorDist = geo2.Vec3Distance(self.eyePosition, self.sceneCursor)
        zoomProp = anchorDist / (self.minZoom - self.sceneCursor[1])
        zoomProp = max(0.0, min(math.fabs(zoomProp), 2.0))
        return zoomProp

    def ResetCamera(self):
        self.LookAt(self.ego)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        self.ResetAnchorPos()

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        if lastCamera and lastCamera.cameraID == evecamera.CAM_SHIPORBIT:
            eyePos0 = lastCamera.eyePosition
            atPos0 = lastCamera.atPosition
            self._ResetEyePosition(atPos0, eyePos0, atPos0)
            self.fov = lastCamera.fov
            self.SetFovTarget(self.default_fov)
            self.lastLookAtID = lastCamera.GetItemID()
        BaseSpaceCamera.OnActivated(self, **kwargs)
        self.UpdateAnchorPos()

    def _GetNewDirection(self, direction):
        y = geo2.Vec2Length((direction[0], direction[2]))
        direction = (direction[0], y, direction[2])
        direction = geo2.Vec3Normalize(direction)
        return direction

    def _ResetEyePosition(self, atPos0, eyePos0, atPos1):
        direction = self._GetNewDirection(geo2.Vec3Subtract(eyePos0, atPos0))
        eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(direction, LOOKAT_DIST))
        duration = GetDurationByDistance(eyePos0, eyePos1, 0.4, 0.6)
        self.Transit(atPos0, eyePos0, atPos1, eyePos1, duration=duration)

    def Update(self):
        self.CheckWarping()
        BaseSpaceCamera.Update(self)
        self._EnforceMaximumDistance()

    def CheckWarping(self):
        ball = self.GetBall(session.shipid)
        if ball is None:
            return
        if ball.mode == destiny.DSTBALL_WARP:
            self.ResetAnchorPos()
        elif not self._anchorBall:
            self.UpdateAnchorPos()

    def _EnforceMaximumDistance(self):
        maxDist = evecamera.LOOKATRANGE_MAX_NEW
        if geo2.Vec3Length(self.eyePosition) > maxDist:
            direction = geo2.Vec3Normalize(self.eyePosition)
            newEye = geo2.Vec3Scale(direction, maxDist)
            diff = geo2.Vec3Subtract(self.eyePosition, newEye)
            self._eyePosition = newEye
            self._atPosition = geo2.Vec3Subtract(self._atPosition, diff)
            self.UpdateAnchorPos()
