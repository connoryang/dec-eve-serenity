#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\dungeonEditorCamera.py
from eve.client.script.ui.camera.cameraOld import CameraOld
from evecamera import dungeonhack
import blue
import evecamera

class DungeonEditorCamera(CameraOld):
    cameraID = evecamera.CAM_DUNGEONEDIT

    def __init__(self):
        CameraOld.__init__(self)
        self.dungeonHack = dungeonhack.DungeonHack(self)

    def _DisableFreeLook(self):
        if self.dungeonHack.IsFreeLook():
            self.dungeonHack.SetFreeLook(False)

    def DoBallClear(self, solitem):
        self._DisableFreeLook()
        CameraOld.DoBallClear(solitem)

    def _AdjustLookAtTarget(self, ball):
        CameraOld._AdjustLookAtTarget(self, ball)
        cameraParent = self.GetCameraParent()
        lookingAtID = self.LookingAt()
        if cameraParent and cameraParent.parent and cameraParent.parent == ball.model:
            self._DisableFreeLook()

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        CameraOld.OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration, repeat, startTime, timeFromStart, graphicInfo)
        if guid == 'effects.Warping':
            if shipID == session.shipid:
                self._DisableFreeLook()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'locationid' in change.iterkeys():
            self._DisableFreeLook()
        CameraOld.OnSessionChanged(self, isRemote, sess, change)

    def PanCamera(self, cambeg = None, camend = None, time = 0.5, cache = False, source = None):
        if self.dungeonHack.IsFreeLook():
            return
        CameraOld.PanCamera(self, cambeg, camend, time, cache, source)

    def SetCameraInterest(self, itemID):
        if self.dungeonHack.IsFreeLook():
            return
        CameraOld.SetCameraInterest(self, itemID)

    def LookAt(self, itemID, setZ = None, resetCamera = False, smooth = True):
        item = sm.StartService('michelle').GetBall(itemID)
        if not hasattr(item, 'GetModel') or item.GetModel() is None:
            return
        self._WaitForTech3Model(item)
        if self.dungeonHack.IsFreeLook():
            vec = item.GetVectorAt(blue.os.GetSimTime())
            self.GetCameraParent().translation = (vec.x, vec.y, vec.z)
            return
        CameraOld.LookAt(self, itemID, setZ, resetCamera, smooth)
