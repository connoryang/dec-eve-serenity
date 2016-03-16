#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\ui\controlPaths.py
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
import geo2
import lineController
_PATH_STATE_PICK_XZ = 0
_PATH_STATE_PICK_Y = 1
_PATH_STATE_INACTIVE = 2
_PATH_STATE_DONE = 3

class SinglePointPath:

    def __init__(self):
        self.pathColor = (1, 1, 1, 0.5)
        self.movementColor = (1, 1, 1, 1)
        self.linePath = None
        self.movementLine = None
        self.mouseDown = False
        self.state = _PATH_STATE_INACTIVE
        self.planarPosition = (0, 0, 0)
        self.finalPosition = (0, 0, 0)

    def Start(self):
        lc = lineController.LineController.GetGlobalInstance()
        self.linePath = lc.CreateLinePath(self.pathColor)
        self.linePath.BeginPath()
        self.state = _PATH_STATE_PICK_XZ
        self.planarPosition = (0, 0, 0)
        self.finalPosition = (0, 0, 0)
        self.movementLine = self.linePath.lineSet.AddLine((0, 0, 0), (0, 0, 0), self.movementColor)

    def Abort(self):
        self.linePath.EndPath()
        self.state = _PATH_STATE_INACTIVE
        self.movementLine = None

    def AddPoint(self):
        if self.state == _PATH_STATE_PICK_XZ:
            self.state = _PATH_STATE_PICK_Y
            self.linePath.ConfirmPoint()
        elif self.state == _PATH_STATE_PICK_Y:
            self.state = _PATH_STATE_DONE
            self.linePath.EndPath()

    def UpdatePosition(self, cameraController):
        if self.state == _PATH_STATE_PICK_XZ:
            ray_dir, ray_start = cameraController.GetPickVector()
            multiplier = ray_start[1] / -ray_dir[1]
            self.planarPosition = geo2.Vec3Add(ray_start, geo2.Vec3Scale(ray_dir, multiplier))
            self.linePath.SetPosition(self.planarPosition)
            self.movementLine.SetEndPosition(self.planarPosition)
        elif self.state == _PATH_STATE_PICK_Y:
            viewTransform = cameraController.GetCamera().viewMatrix.transform
            plane_dir = (viewTransform[0][2], 0, viewTransform[2][2])
            ray_dir, start = cameraController.GetPickVector()
            plane_position = RayToPlaneIntersection(start, ray_dir, self.planarPosition, plane_dir)
            self.finalPosition = (self.planarPosition[0], plane_position[1], self.planarPosition[2])
            self.linePath.SetPosition(self.finalPosition)
            self.movementLine.SetEndPosition(self.finalPosition)

    def IsComplete(self):
        return self.state == _PATH_STATE_DONE

    def GetEndPosition(self):
        if self.state == _PATH_STATE_DONE:
            return self.finalPosition
        return self.linePath.GetEndPosition()
