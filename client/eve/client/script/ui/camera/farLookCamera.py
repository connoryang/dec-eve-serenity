#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\farLookCamera.py
from eve.client.script.parklife import states
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
from eve.client.script.ui.camera.cameraUtil import GetBallPosition, GetBall
import evecamera
import geo2

class FarLookCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_FARLOOK
    default_fov = 0.75
    isBobbingCamera = True

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.lastCamera = None
        self.itemID = None
        self.lastLookAtID = None
        self.dist = 0.0

    def OnActivated(self, itemID = None, lastCamera = None, **kwargs):
        self.itemID = itemID
        self.lastCamera = lastCamera
        self.lastLookAtID = lastCamera.GetItemID()
        self.eyePosition = lastCamera.eyePosition
        self.atPosition = lastCamera.atPosition
        self.dist = lastCamera.GetZoomDistance()
        self.fov = self.lastCamera.fov
        self.SetFovTarget(self.default_fov)
        self.LookAt(itemID)
        if lastCamera.cameraID == evecamera.CAM_SHIPORBIT:
            self._bobbingAngle = lastCamera._bobbingAngle
            self._UpdateBobbingOffset()
        BaseSpaceCamera.OnActivated(self)

    def GetLookAtItemID(self):
        return GetBall(self.itemID)

    def LookAt(self, itemID = None, **kwargs):
        ball = GetBall(itemID)
        if not ball:
            return
        if not self.CheckObjectTooFar(itemID):
            self.SwitchToLastCamera(itemID=itemID)
            return
        sm.StartService('state').SetState(itemID, states.lookingAt, True)
        ballPos = GetBallPosition(ball)
        ballDir = geo2.Vec3Normalize(ballPos)
        atPosition = geo2.Vec3Add(self.eyePosition, geo2.Vec3Scale(ballDir, self.dist))
        self.TransitTo(atPosition, self.eyePosition, duration=1.0)

    def SwitchToLastCamera(self, itemID = None):
        cameraID = self.lastCamera.cameraID
        itemID = itemID or self.lastLookAtID
        sm.GetService('sceneManager').SetActiveCameraByID(cameraID, itemID=itemID)

    def GetLookAtItemID(self):
        return self.itemID

    def ResetCamera(self, *args):
        self.SwitchToLastCamera()
