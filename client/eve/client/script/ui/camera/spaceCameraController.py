#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\spaceCameraController.py
import math
from achievements.common.achievementConst import AchievementConsts
from achievements.common.eventExceptionEater import AchievementEventExceptionEater
from carbon.common.script.util import mathCommon
from carbonui import const as uiconst
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.dungeonEditorCamera import DungeonEditorCamera
import evecamera
from evecamera import FOV_MAX, FOV_MIN
import mathUtil
import service
import uthread
import geo2
import blue
from evegraphics import settings as gfxsettings

class SpaceCameraController(BaseCameraController):
    cameraID = evecamera.CAM_SPACE_PRIMARY

    def __init__(self):
        BaseCameraController.__init__(self)
        self.fovCached = None
        self.ignoreNextDblClick = False
        self.isPicked = False
        self.isRotating = False
        self.dungeonEditorSelectionEnabled = False
        self.fovResetPending = False
        self.isDragEventScattered = False
        self.zoomAchievementCompleted = False
        self.rotateAchievementCompleted = False
        self.cameraStillSpinning = False

    def OnMouseDown(self, *args):
        self.mouseDownPos = (uicore.uilib.x, uicore.uilib.y)
        self.isPicked = True
        self.ignoreNextDblClick = 0
        _, pickobject = self.GetPick()
        if uicore.uilib.leftbtn:
            if sm.IsServiceRunning('scenario') and sm.GetService('scenario').IsActive():
                self.isMovingSceneCursor = sm.GetService('scenario').GetPickAxis()
            if pickobject:
                self.CheckInSceneCursorPicked(pickobject)
                if session.role & service.ROLE_CONTENT and self.dungeonEditorSelectionEnabled and not self.isMovingSceneCursor:
                    self.OnDungeonEditClick(pickobject)
        if uicore.uilib.rightbtn:
            sm.GetService('target').CancelTargetOrder()
            if self.fovCached is None:
                camera = self.GetCamera()
                self.fovCached = camera.fieldOfView
            self.ignoreNextDblClick = 1
        return pickobject

    def OnDungeonEditClick(self, pickobject):
        scenario = sm.GetService('scenario')
        michelle = sm.GetService('michelle')
        item = michelle.GetItem(pickobject.translationCurve.id)
        if getattr(item, 'dunObjectID', None) != None and hasattr(pickobject, 'translationCurve') and hasattr(pickobject.translationCurve, 'id'):
            shift = uicore.uilib.Key(uiconst.VK_SHIFT)
            if not shift:
                slimItem = michelle.GetItem(item.itemID)
                scenario.SetSelectionByID([slimItem.dunObjectID])
            elif not scenario.IsSelected(item.itemID):
                scenario.AddSelected(item.itemID)
            else:
                scenario.RemoveSelected(item.itemID)

    def OnDblClick(self, *args):
        solarsystemID = session.solarsystemid
        uthread.Lock(self)
        try:
            if solarsystemID != session.solarsystemid:
                return
            if self.ignoreNextDblClick:
                return
            if uicore.uilib.Key(uiconst.VK_SHIFT) and session.role & service.ROLE_CONTENT:
                return
            if uicore.uilib.rightbtn or uicore.uilib.mouseTravel > 6:
                return
            camera = self.GetCamera()
            isFreeLook = self.IsFreeLookCamera(camera)
            if isFreeLook:
                picktype, pickobject = self.GetPick()
                if pickobject:
                    camera.LookAt(pickobject.translationCurve.id)
                return
            self.SetShipDirection(solarsystemID)
        finally:
            uthread.UnLock(self)

    def SetShipDirection(self, solarsystemID):
        camera = self.GetCamera()
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if camera is not None:
            proj = camera.projectionMatrix.transform
            view = camera.viewMatrix.transform
            pickDir = scene.PickInfinity(uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y), proj, view)
            if pickDir:
                bp = sm.GetService('michelle').GetRemotePark()
                if bp is not None:
                    if solarsystemID == session.solarsystemid:
                        try:
                            bp.CmdGotoDirection(pickDir[0], pickDir[1], pickDir[2])
                            sm.ScatterEvent('OnClientEvent_MoveWithDoubleClick')
                            sm.GetService('menu').ClearAlignTargets()
                            sm.GetService('flightPredictionSvc').GotoDirection(pickDir)
                        except RuntimeError as what:
                            if what.args[0] != 'MonikerSessionCheckFailure':
                                raise what

    def IsFreeLookCamera(self, camera):
        return isinstance(camera, DungeonEditorCamera) and camera.dungeonHack.IsFreeLook()

    def OnMouseUp(self, button, *args):
        self.mouseDownPos = None
        sm.ScatterEvent('OnCameraDragEnd')
        self.isDragEventScattered = False
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self.isPicked = False
        camera = self.GetCamera()
        if not uicore.uilib.rightbtn:
            if self.isRotating and self.fovResetPending and camera.fieldOfView != self.fovCached:
                uthread.new(self.ResetFov)
            camera = self.GetCamera()
            if not camera.targetTracker.tracking:
                camera.rotationOfInterest = geo2.QuaternionIdentity()
            self.isRotating = 0
        if button == 0 and not uicore.uilib.rightbtn:
            self.cameraStillSpinning = False
            camera = self.GetCamera()
            freeLookMove = self.IsFreeLookCamera(camera) and uicore.uilib.Key(uiconst.VK_MENU)
            mt = self.GetMouseTravel()
            if not (mt and mt > 5 or freeLookMove):
                if not self.TryClickSceneObject():
                    if uicore.uilib.Key(uiconst.VK_MENU):
                        sm.GetService('menu').TryLookAt(session.shipid)
        if self.CheckReleaseSceneCursor():
            return
        if session.role & service.ROLE_CONTENT:
            if self.isMovingSceneCursor:
                self.isMovingSceneCursor = None

    def ZoomBy(self, amount):
        self.GetCamera().PanCameraBy(amount * 0.001, time=0, cache=True)
        self.RecordZoomForAchievements(amount)

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        dz = uicore.uilib.dz
        self.ZoomBy(modifier * dz)
        return 1

    def OnMouseMove(self, *args):
        if not self.isPicked:
            return
        leftbtn = uicore.uilib.leftbtn
        rightbtn = uicore.uilib.rightbtn
        dx = uicore.uilib.dx
        dy = uicore.uilib.dy
        camera = self.GetCamera()
        fov = camera.fieldOfView
        if self.CheckMoveSceneCursor():
            return
        if uicore.uilib.Key(uiconst.VK_MENU) and self.IsFreeLookCamera(camera):
            self.MoveDungeonCamera()
            return
        if rightbtn and not leftbtn:
            camera.RotateOnOrbit(-dx * fov * 0.2, dy * fov * 0.2)
            self.isRotating = True
        elif leftbtn and not rightbtn:
            camera.OrbitParent(-dx * fov * 0.2, dy * fov * 0.2)
            self.RecordOrbitForAchievements()
        elif leftbtn and rightbtn:
            if self.isRotating:
                self.FOVZoom()
            else:
                self.ZoomAndOrbit()
        if leftbtn ^ rightbtn:
            if abs(dx) + abs(dy) > 1:
                sm.GetService('targetTrackingService').MouseTrackInterrupt()
        if not self.isDragEventScattered:
            sm.ScatterEvent('OnCameraDragStart')
        self.isDragEventScattered = True

    def ZoomAndOrbit(self):
        camera = self.GetCamera()
        dx = uicore.uilib.dx
        dy = uicore.uilib.dy
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        camera.PanCameraBy(modifier * -0.01 * dy, time=0, cache=True)
        self.RecordZoomForAchievements(dy)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            camera.fieldOfView = -dx * 0.01 + camera.fieldOfView
            if camera.fieldOfView > FOV_MAX:
                camera.fieldOfView = FOV_MAX
            if camera.fieldOfView < FOV_MIN:
                camera.fieldOfView = FOV_MIN
        else:
            camera.OrbitParent(-dx * camera.fieldOfView * 0.2, 0.0)

    def FOVZoom(self):
        camera = self.GetCamera()
        dy = uicore.uilib.dy
        camera.fieldOfView += dy * 0.01
        if camera.fieldOfView > FOV_MAX:
            camera.fieldOfView = FOV_MAX
        if camera.fieldOfView < FOV_MIN:
            camera.fieldOfView = FOV_MIN
        self.fovResetPending = True

    def CheckMoveSceneCursor(self):
        isMoving = BaseCameraController.CheckMoveSceneCursor(self)
        if isMoving:
            return True
        if not self.isMovingSceneCursor or not uicore.uilib.leftbtn:
            return False
        if session.role & service.ROLE_CONTENT:
            sm.GetService('scenario').MoveCursor(self.isMovingSceneCursor, uicore.uilib.dx, uicore.uilib.dy, self.GetCamera())
            return True
        return False

    def MoveDungeonCamera(self):
        camera = self.GetCamera()
        lib = uicore.uilib
        leftBtn = lib.leftbtn and not lib.rightbtn and not lib.midbtn
        rightBtn = lib.rightbtn and not lib.leftbtn and not lib.midbtn
        midBtn = lib.rightbtn and lib.leftbtn or lib.midbtn
        if leftBtn:
            camera.OrbitParent(-lib.dx * camera.fieldOfView * 0.2, -lib.dy * camera.fieldOfView * 0.2)
        if rightBtn:
            modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
            camera.PanCameraBy(modifier * -0.01 * lib.dy, time=0)
        if midBtn:
            vertMovement = geo2.Vec3Scale(camera.upVec, lib.dy * camera.translationFromParent / uicore.uilib.desktop.height)
            horizMovement = geo2.Vec3Scale(camera.rightVec, -lib.dx * camera.translationFromParent / uicore.uilib.desktop.height)
            camera.dungeonHack._ChangeCamPos(geo2.Vec3Add(vertMovement, horizMovement))

    def ResetFov(self):
        if self.fovCached is not None:
            camera = self.GetCamera()
            if camera is None:
                return
            to = FOV_MAX
            fr = camera.fieldOfView
            start, ndt = blue.os.GetSimTime(), 0.0
            while ndt != 1.0:
                ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetSimTime()) / 1000.0, 1.0)
                camera.fieldOfView = mathUtil.Lerp(fr, to, ndt)
                blue.pyos.synchro.Yield()

            self.fovCached = None
        self.fovResetPending = False

    def RecordZoomForAchievements(self, amount):
        with AchievementEventExceptionEater():
            if self.zoomAchievementCompleted:
                return
            isCompleted = sm.GetService('achievementSvc').IsAchievementCompleted(AchievementConsts.UI_ZOOM_IN_SPACE)
            if isCompleted:
                self.zoomAchievementCompleted = True
            else:
                sm.ScatterEvent('OnClientMouseZoomInSpace', amount)

    def CameraMove_thread(self):
        try:
            camera = self.GetCamera()
            lastYawRad, _, _ = geo2.QuaternionRotationGetYawPitchRoll(camera.rotationAroundParent)
            radDelta = 0
            while self.cameraStillSpinning:
                blue.pyos.synchro.Yield()
                if self.mouseDownPos is None or camera is None:
                    self.cameraStillSpinning = False
                    return
                curYaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(camera.rotationAroundParent)
                angleBtwYaws = mathCommon.GetLesserAngleBetweenYaws(lastYawRad, curYaw)
                radDelta += angleBtwYaws
                lastYawRad = curYaw
                if abs(radDelta) > math.pi / 2:
                    sm.ScatterEvent('OnClientMouseSpinInSpace')
                    return

        except Exception as e:
            pass

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

    def ResetAchievementVariables(self):
        self.zoomAchievementCompleted = False
        self.rotateAchievementCompleted = False
