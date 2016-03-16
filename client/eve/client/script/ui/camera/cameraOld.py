#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\cameraOld.py
from eve.client.script.ui.camera.spaceCamera import SpaceCamera

class CameraOld(SpaceCamera):

    def UpdateCameraBobbing(self, *args):
        self.idleMove = 0
