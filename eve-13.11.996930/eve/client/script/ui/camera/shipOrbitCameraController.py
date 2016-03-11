#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipOrbitCameraController.py
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera

class ShipOrbitCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SHIPORBIT

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = 0.012
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.001
            camera.Zoom(-kZoom * uicore.uilib.dy)
            camera.Orbit(kOrbit * uicore.uilib.dx, 0.0)
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * uicore.uilib.dx, kOrbit * uicore.uilib.dy)

    def OnMouseDown(self, button, *args):
        ret = BaseCameraController.OnMouseDown(self, button, *args)
        self.GetCamera().OnMouseDown(button)
        return ret

    def OnMouseUp(self, button, *args):
        BaseCameraController.OnMouseUp(self, button, *args)
        self.GetCamera().OnMouseUp(button)

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        if camera.trackBall:
            k = 0.0005
            camera.Zoom(k * GetZoomDz())
