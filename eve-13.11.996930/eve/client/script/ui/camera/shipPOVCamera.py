#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipPOVCamera.py
import math
import blue
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
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
        self.atPosition = geo2.Vec3Add(trackPos, geo2.Vec3Scale(lookDir, -self.trackBall.radius))
        self.eyePosition = geo2.Vec3Add(self.atPosition, lookDir)

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
            self.ShowModel()
            self.trackBall = None

    def ShowModel(self):
        if self.trackBall and self.trackBall.model:
            self.trackBall.model.display = True

    def HideModel(self):
        if self.trackBall and self.trackBall.model:
            self.trackBall.model.display = False

    def OnActivated(self, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        bp = sm.GetService('michelle').GetBallpark()
        self.trackBall = bp.GetBall(self.ego)
        self.HideModel()

    def LookingAt(self):
        return self.trackBall

    def LookAt(self, itemID, *args):
        if not self.CheckObjectTooFar(itemID):
            sm.GetService('sceneManager').SetActiveCameraByID(evecamera.CAM_SHIPORBIT, itemID=itemID)

    def ResetCamera(self):
        self.LookAt(session.shipid)
