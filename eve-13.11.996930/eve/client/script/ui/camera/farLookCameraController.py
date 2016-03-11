#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\farLookCameraController.py
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera

class FarLookCameraController(BaseCameraController):
    cameraID = evecamera.CAM_FARLOOK

    def OnMouseMove(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.leftbtn:
            self.SwitchToLastCamera()

    def SwitchToLastCamera(self):
        self.GetCamera().SwitchToLastCamera()

    def OnMouseUp(self, *args):
        if self.GetMouseTravel() < 5:
            self.SwitchToLastCamera()
        BaseCameraController.OnMouseUp(self, *args)

    def OnMouseWheel(self, *args):
        self.SwitchToLastCamera()
