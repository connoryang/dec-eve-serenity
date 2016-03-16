#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipOrbitCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz, CheckInvertZoom
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
import carbonui.const as uiconst

class ShipOrbitCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SHIPORBIT

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-CheckInvertZoom(uicore.uilib.dy), kZoom)
            if math.fabs(uicore.uilib.dx) > 1:
                camera.Orbit(0.01 * uicore.uilib.dx, 0.0)
                self.RecordOrbitForAchievements()
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * uicore.uilib.dx, kOrbit * uicore.uilib.dy)
            self.RecordOrbitForAchievements()

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
        k = 0.0005
        dz = GetZoomDz()
        self._Zoom(dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        self.RecordZoomForAchievements(dz)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            camera.Zoom(0.35 * k * dz)
            camera.FovZoom(-0.5 * k * dz)
        elif uicore.uilib.Key(uiconst.VK_MENU):
            camera.FovZoom(k * dz)
        elif camera.lookAtBall:
            camera.Zoom(k * dz)
