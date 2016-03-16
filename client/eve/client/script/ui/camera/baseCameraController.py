#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\baseCameraController.py
import math
from achievements.common.achievementConst import AchievementConsts
from achievements.common.eventExceptionEater import AchievementEventExceptionEater
from carbon.common.script.sys import service
from carbon.common.script.util import mathCommon
from logmodule import LogException
import trinity
import carbonui.const as uiconst
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.client.script.parklife import states
import geo2
import uthread
import blue

class BaseCameraController(object):

    def __init__(self):
        self.mouseDownPos = None
        self.isMovingSceneCursor = None
        self.zoomAchievementCompleted = False
        self.rotateAchievementCompleted = False
        self.cameraStillSpinning = False

    def OnMouseEnter(self, *args):
        pass

    def OnMouseExit(self, *args):
        pass

    def OnMouseDown(self, *args):
        _, pickobject = self.GetPick()
        self.mouseDownPos = (uicore.uilib.x, uicore.uilib.y)
        self.CheckInSceneCursorPicked(pickobject)
        return pickobject

    def OnMouseUp(self, button, *args):
        isLeftBtn = button == 0
        if isLeftBtn and not uicore.uilib.rightbtn:
            self.cameraStillSpinning = False
            if not self.IsMouseDragged():
                self.TryClickSceneObject()
        self.CheckReleaseSceneCursor()
        isRightBtn = button == 1
        if isRightBtn:
            uthread.new(sm.GetService('target').CancelTargetOrder)
        self.mouseDownPos = None

    def IsMouseDragged(self):
        mt = self.GetMouseTravel()
        return mt is not None and mt >= 5

    def OnMouseMove(self, *args):
        pass

    def OnDblClick(self, *args):
        pass

    def OnMouseWheel(self, *args):
        pass

    def GetCamera(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(self.cameraID)

    def GetPick(self, x = None, y = None):
        if not trinity.app.IsActive():
            return (None, None)
        sceneMan = sm.GetService('sceneManager')
        if sceneMan.IsLoadingScene('default'):
            return (None, None)
        x = x or uicore.uilib.x
        y = y or uicore.uilib.y
        scene = sceneMan.GetRegisteredScene('default')
        x, y = uicore.ScaleDpi(x), uicore.ScaleDpi(y)
        if scene:
            camera = self.GetCamera()
            pick = scene.PickObject(x, y, camera.projectionMatrix, camera.viewMatrix, trinity.device.viewport)
            if pick:
                return ('scene', pick)
        return (None, None)

    def GetPickVector(self):
        x = int(uicore.uilib.x * uicore.desktop.dpiScaling)
        y = int(uicore.uilib.y * uicore.desktop.dpiScaling)
        camera = self.GetCamera()
        viewport = trinity.device.viewport
        view = camera.viewMatrix.transform
        projection = camera.projectionMatrix.transform
        direction, startPos = trinity.device.GetPickRayFromViewport(x, y, viewport, view, projection)
        return (direction, startPos)

    def ProjectWorldToScreen(self, vec3):
        cam = self.GetCamera()
        viewport = (trinity.device.viewport.x,
         trinity.device.viewport.y,
         trinity.device.viewport.width,
         trinity.device.viewport.height,
         trinity.device.viewport.minZ,
         trinity.device.viewport.maxZ)
        x, y, z, w = geo2.Vec3Project(vec3, viewport, cam.projectionMatrix.transform, cam.viewMatrix.transform, geo2.MatrixIdentity())
        return (x, y)

    def TryClickSceneObject(self):
        _, pickobject = self.GetPick()
        if pickobject and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            slimItem = GetBallparkRecord(pickobject.translationCurve.id)
            if slimItem and slimItem.groupID not in const.nonTargetableGroups:
                itemID = pickobject.translationCurve.id
                sm.GetService('state').SetState(itemID, states.selected, 1)
                sm.GetService('menu').TacticalItemClicked(itemID)
                return True
        elif uicore.cmd.IsCombatCommandLoaded('CmdToggleLookAtItem'):
            uicore.cmd.ExecuteCombatCommand(session.shipid, uiconst.UI_KEYUP)
        elif uicore.cmd.IsCombatCommandLoaded('CmdToggleCameraTracking'):
            uicore.cmd.ExecuteCombatCommand(session.shipid, uiconst.UI_KEYUP)
        return False

    def GetMouseTravel(self):
        if self.mouseDownPos:
            x, y = uicore.uilib.x, uicore.uilib.y
            v = trinity.TriVector(float(x - self.mouseDownPos[0]), float(y - self.mouseDownPos[1]), 0.0)
            return int(v.Length())
        else:
            return None

    def CheckInSceneCursorPicked(self, pickobject):
        if sm.IsServiceRunning('scenario') and sm.GetService('scenario').IsActive():
            self.isMovingSceneCursor = sm.GetService('scenario').GetPickAxis()
        elif pickobject and sm.GetService('posAnchor').IsActive() and pickobject.name[:6] == 'cursor':
            self.isMovingSceneCursor = pickobject

    def CheckReleaseSceneCursor(self):
        if self.isMovingSceneCursor:
            self.isMovingSceneCursor = None
            if sm.GetService('posAnchor').IsActive():
                sm.GetService('posAnchor').StopMovingCursor()
            return True
        return False

    def CheckMoveSceneCursor(self):
        if not self.isMovingSceneCursor or not uicore.uilib.leftbtn:
            return False
        if sm.GetService('posAnchor').IsActive():
            sm.GetService('posAnchor').MoveCursor(self.isMovingSceneCursor, uicore.uilib.dx, uicore.uilib.dy, self.GetCamera())
            return True
        if session.role & service.ROLE_CONTENT:
            sm.GetService('scenario').MoveCursor(self.isMovingSceneCursor, uicore.uilib.dx, uicore.uilib.dy, self.GetCamera())
            return True
        return False

    def RecordZoomForAchievements(self, amount):
        with AchievementEventExceptionEater():
            if self.zoomAchievementCompleted:
                return
            isCompleted = sm.GetService('achievementSvc').IsAchievementCompleted(AchievementConsts.UI_ZOOM_IN_SPACE)
            if isCompleted:
                self.zoomAchievementCompleted = True
            else:
                sm.ScatterEvent('OnClientMouseZoomInSpace', amount)

    def ResetAchievementVariables(self):
        self.zoomAchievementCompleted = False
        self.rotateAchievementCompleted = False

    def CameraMove_thread(self):
        try:
            camera = self.GetCamera()
            lastYawRad, _, _ = geo2.QuaternionRotationGetYawPitchRoll(camera.GetRotationQuat())
            radDelta = 0
            while self.cameraStillSpinning:
                blue.pyos.synchro.Yield()
                if self.mouseDownPos is None or camera is None:
                    self.cameraStillSpinning = False
                    return
                curYaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(camera.GetRotationQuat())
                angleBtwYaws = mathCommon.GetLesserAngleBetweenYaws(lastYawRad, curYaw)
                radDelta += angleBtwYaws
                lastYawRad = curYaw
                if abs(radDelta) > math.pi / 2:
                    sm.ScatterEvent('OnClientMouseSpinInSpace')
                    return

        except Exception as e:
            LogException(e)

    def RecordOrbitForAchievements(self):
        with AchievementEventExceptionEater():
            if self.rotateAchievementCompleted or self.cameraStillSpinning:
                return
            isCompleted = sm.GetService('achievementSvc').IsAchievementCompleted(AchievementConsts.UI_ROTATE_IN_SPACE)
            if isCompleted:
                self.rotateAchievementCompleted = True
            else:
                self.cameraStillSpinning = True
                uthread.new(self.CameraMove_thread)
