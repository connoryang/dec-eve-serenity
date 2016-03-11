#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\dungeonEditorCameraController.py
from eve.client.script.ui.camera.spaceCameraController import SpaceCameraController
import evecamera

class DungeonEditorCameraController(SpaceCameraController):
    cameraID = evecamera.CAM_DUNGEONEDIT
