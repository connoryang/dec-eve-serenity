#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\shipPOVCameraController.py
from eve.client.script.ui.camera.cameraUtil import SetShipDirection, GetZoomDz
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
import carbonui.const as uiconst
import evecamera
FOV_LEVELS = [1.3, 0.775, 0.25]

class ShipPOVCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SHIPPOV

    def __init__(self):
        BaseCameraController.__init__(self)
        self.fovLevel = 0
        self.GetCamera().fov = FOV_LEVELS[self.fovLevel]

    def OnMouseMove(self, *args):
        pass

    def OnMouseWheel(self, *args):
        camera = self.GetCamera()
        dz = GetZoomDz()
        if dz < 0:
            if self.fovLevel == len(FOV_LEVELS) - 1:
                return
            self.fovLevel += 1
        elif self.fovLevel > 0:
            self.fovLevel -= 1
        sm.GetService('audio').SendUIEvent('ship_interior_cam_zoom_play')
        fov = FOV_LEVELS[self.fovLevel]
        uicore.animations.MorphScalar(camera, 'fov', camera.fov, fov, duration=0.35, curveType=uiconst.ANIM_OVERSHOT)

    def OnDblClick(self, *args):
        if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
            return
        SetShipDirection(self.GetCamera())
