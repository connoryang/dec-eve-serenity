#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\jumpCamera.py
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera
import evecamera

class JumpCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_JUMP
    default_fov = 1.0

    def OnActivated(self, lastCamera = None, itemID = None, **kwargs):
        BaseSpaceCamera.OnActivated(self, **kwargs)
        if lastCamera and lastCamera.cameraID in evecamera.INSPACE_CAMERAS:
            self._atPosition = lastCamera.atPosition
            self._eyePosition = lastCamera.eyePosition
            self.fov = lastCamera.fov
        self.SetFovTarget(self.default_fov)

    def IsLocked(self):
        return True
