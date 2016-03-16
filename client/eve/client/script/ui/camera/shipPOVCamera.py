#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipPOVCamera.py
import math
import blue
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetBallPosition
import evecamera
import geo2

class ShipPOVCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_SHIPPOV
    minZoom = 100000
    kOrbitSpeed = 5.0
    kPanSpeed = 8.0
    default_fov = 1.5

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lastLookAtID = None
        self.trackBall = None

    def Update(self):
        BaseSpaceCamera.Update(self)
        if self.trackBall and getattr(self.trackBall, 'model', None) and hasattr(self.trackBall.model.rotationCurve, 'value'):
            self.UpdateUpDirection()
            self.UpdateAtEyePositions()
            self.UpdateCrosshairPosition()

    def UpdateAtEyePositions(self):
        trackPos = self.GetTrackPosition()
        lookDir = self.GetLookDirection()
        ballPos = GetBallPosition(self.trackBall)
        if self.trackBall.model:
            radius = self.trackBall.model.GetBoundingSphereRadius()
        else:
            radius = self.trackBall.radius * 1.2
        self.eyePosition = geo2.Vec3Add(ballPos, geo2.Vec3Scale(lookDir, -radius))
        self.atPosition = geo2.Vec3Add(ballPos, geo2.Vec3Scale(lookDir, -2 * radius))

    def GetTrackPosition(self):
        trackPos = self.trackBall.GetVectorAt(blue.os.GetSimTime())
        return (trackPos.x, trackPos.y, trackPos.z)

    def GetLookDirection(self):
        lookDir = geo2.QuaternionTransformVector(self.trackBall.model.rotationCurve.value, (0.0, 0.0, -1.0))
        lookDir = geo2.Vec3Normalize(lookDir)
        return lookDir

    def UpdateUpDirection(self):
        model = self.trackBall.model
        upDirection = geo2.QuaternionTransformVector(model.rotationCurve.value, (0.0, 1.0, 0.0))
        self.upDirection = geo2.Vec3Normalize(upDirection)

    def UpdateCrosshairPosition(self):
        lookAtDir = self.GetLookAtDirection()
        pitch = math.acos(geo2.Vec3Dot(lookAtDir, (0, -1, 0)))
        rightDir = geo2.Vec3Cross(self.GetUpDirection(), lookAtDir)
        roll = math.acos(geo2.Vec3Dot(rightDir, (0, 1, 0)))
        sm.ChainEvent('ProcessPOVCameraOrientation', pitch, roll)

    def OnDeactivated(self):
        BaseSpaceCamera.OnDeactivated(self)
        if self.trackBall:
            self.trackBall = None

    def OnActivated(self, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        sm.StartService('state').SetState(self.ego, states.lookingAt, True)
        settings.char.ui.Set('spaceCameraID', evecamera.CAM_SHIPPOV)
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            self.trackBall = bp.GetBall(self.ego)

    def GetLookAtItemID(self):
        return self.trackBall

    def LookAt(self, itemID, *args, **kwargs):
        if itemID == self.ego:
            return
        if not self.CheckObjectTooFar(itemID):
            sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_SHIPORBIT, itemID=itemID)

    def ResetCamera(self, *args):
        pass
