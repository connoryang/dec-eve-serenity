#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\baseCameraController.py
import trinity
import carbonui.const as uiconst
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.client.script.parklife import states

class BaseCameraController(object):

    def __init__(self):
        self.mouseDownPos = None
        self.isMovingSceneCursor = None

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
            mt = self.GetMouseTravel()
            if mt is None or mt < 5:
                self.TryClickSceneObject()
        self.CheckReleaseSceneCursor()
        self.mouseDownPos = None

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
        elif uicore.cmd.IsCombatCommandLoaded('CmdToggleCameraInterest'):
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
        if not pickobject:
            return False
        if sm.GetService('posAnchor').IsActive() and pickobject.name[:6] == 'cursor':
            self.isMovingSceneCursor = pickobject

    def CheckReleaseSceneCursor(self):
        if self.isMovingSceneCursor:
            if sm.GetService('posAnchor').IsActive():
                sm.GetService('posAnchor').StopMovingCursor()
                self.isMovingSceneCursor = None
                return True
        return False

    def CheckMoveSceneCursor(self):
        if not self.isMovingSceneCursor or not uicore.uilib.leftbtn:
            return False
        if sm.GetService('posAnchor').IsActive():
            sm.GetService('posAnchor').MoveCursor(self.isMovingSceneCursor, uicore.uilib.dx, uicore.uilib.dy, self.GetCamera())
            return True
        return False
