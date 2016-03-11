#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\starmapCamera.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from eve.client.script.ui.shared.maps.mapcommon import ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP
import evecamera

class StarmapCamera(CameraOld):
    cameraID = evecamera.CAM_STARMAP
    __notifyevents__ = []

    def _GetMinMaxTranslationFromParent(self):
        return (ZOOM_MIN_STARMAP, ZOOM_MAX_STARMAP)

    def LookAt(self, *args, **kwds):
        print 'LOOOOOOOOOOOOOOOOOK'
