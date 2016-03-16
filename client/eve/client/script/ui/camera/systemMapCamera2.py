#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\systemMapCamera2.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP
import evecamera
from evecamera.utils import GetARZoomMultiplier
import trinity

class SystemMapCamera2(CameraOld):
    cameraID = evecamera.CAM_SYSTEMMAP

    def _GetMinMaxTranslationFromParent(self):
        mn, mx = ZOOM_NEAR_SYSTEMMAP, ZOOM_FAR_SYSTEMMAP
        mx *= GetARZoomMultiplier(trinity.device.viewport.GetAspectRatio())
        return (mn, mx)
