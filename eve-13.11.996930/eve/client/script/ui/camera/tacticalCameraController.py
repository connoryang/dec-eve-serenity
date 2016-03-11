#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\tacticalCameraController.py
import math
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import evecamera
import geo2
DIST_ORBIT_SWITCH = 20000

class TacticalCameraController(BaseCameraController):
    cameraID = evecamera.CAM_TACTICAL

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            k = 200.0
            camera.Pan(0, 0, -k * uicore.uilib.dy)
        elif uicore.uilib.rightbtn:
            k = 10 * (3.0 + camera.GetZoomDistance() / camera.minZoom)
            camera.Pan(-k * uicore.uilib.dx, k * uicore.uilib.dy, 0)
        elif uicore.uilib.leftbtn:
            k = 0.005
            camera.Orbit(k * uicore.uilib.dx, k * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        dz = GetZoomDz()
        if camera.lastLookAtID:
            k = 0.0005
            camera.Zoom(k * dz)
        else:
            k = 15.0 * dz
            x, y, z = self.GetPanDirection()
            camera.Pan(k * x, k * y, k * z)

    def GetPanDirection(self):
        camera = self.GetCamera()
        th = math.radians(90 * camera.fov / 2.0)
        dist = uicore.desktop.width / (2.0 * math.tan(th))
        x = -(uicore.uilib.x - uicore.desktop.width / 2)
        y = uicore.uilib.y - uicore.desktop.height / 2
        return geo2.Vec3Normalize((x, y, dist))

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())
