#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\__init__.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from eve.client.script.ui.camera.dungeonEditorCamera import DungeonEditorCamera
from eve.client.script.ui.camera.farLookCamera import FarLookCamera
from eve.client.script.ui.camera.shipOrbitCamera import ShipOrbitCamera
from eve.client.script.ui.camera.shipPOVCamera import ShipPOVCamera
from eve.client.script.ui.camera.spaceCamera import SpaceCamera
from eve.client.script.ui.camera.starmapCamera import StarmapCamera
from eve.client.script.ui.camera.systemMapCamera2 import SystemMapCamera2
from eve.client.script.ui.camera.tacticalCamera import TacticalCamera
import evecamera
cameraClsByCameraID = {evecamera.CAM_SPACE_PRIMARY: SpaceCamera,
 evecamera.CAM_SHIPORBIT: ShipOrbitCamera,
 evecamera.CAM_DUNGEONEDIT: DungeonEditorCamera,
 evecamera.CAM_HANGAR: CameraOld,
 evecamera.CAM_PLANET: CameraOld,
 evecamera.CAM_STARMAP: StarmapCamera,
 evecamera.CAM_SYSTEMMAP: SystemMapCamera2,
 evecamera.CAM_TACTICAL: TacticalCamera,
 evecamera.CAM_SHIPPOV: ShipPOVCamera,
 evecamera.CAM_FARLOOK: FarLookCamera}
