#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\ui\lineController.py
import trinity
LINE_CONNECTOR_ATTACKING = 'attacking'
LINE_CONNECTOR_LOCKING = 'locking'
LINE_CONNECTOR_MOVING = 'moving'
_LINE_CONNECTORS = {LINE_CONNECTOR_ATTACKING: 'res:/dx9/model/ui/lineConnectorAttacking.red',
 LINE_CONNECTOR_LOCKING: 'res:/dx9/model/ui/lineConnectorLocking.red',
 LINE_CONNECTOR_MOVING: 'res:/dx9/model/ui/lineConnectorMoving.red'}

class LineSet:

    def __init__(self, lineSet):
        self.lines = {}
        self.lineSet = lineSet

    def RebuildLine(self, lineID):
        line = self.lines[lineID]
        del self.lines[lineID]
        self.lineSet.RemoveLine(lineID)
        line.lineID = self.lineSet.AddStraightLine(line.startPos, line.color, line.endPos, line.color, line.width)
        self.lineSet.SubmitChanges()
        self.lines[line.lineID] = line

    def AddLine(self, p0, p1, color):
        line = Line(self, p0, p1, color)
        line.lineID = self.lineSet.AddStraightLine(line.startPos, line.color, line.endPos, line.color, line.width)
        self.lineSet.SubmitChanges()
        self.lines[line.lineID] = line
        return line

    def RemoveLine(self, lineID):
        del self.lines[lineID]
        self.lineSet.RemoveLine(lineID)
        self.lineSet.SubmitChanges()

    def Clear(self):
        for key in self.lines:
            self.lineSet.RemoveLine(key)

        self.lineSet.SubmitChanges()
        self.lines.clear()

    def Destroy(self):
        self.Clear()
        self.lineSet = None


class Line:

    def __init__(self, lineSet, p0, p1, color, width = 1.0):
        self.lineID = None
        self.lineSet = lineSet
        self.width = width
        self.color = color
        self.startPos = p0
        self.endPos = p1

    def SetStartPosition(self, p):
        self.startPos = p
        self.lineSet.RebuildLine(self.lineID)

    def SetEndPosition(self, p):
        self.endPos = p
        self.lineSet.RebuildLine(self.lineID)

    def SetColor(self, color):
        self.color = color
        self.lineSet.RebuildLine(self.lineID)


class LinePath:

    def __init__(self, lineSet, color = (1, 1, 1, 1)):
        self.lines = []
        self.lineSet = lineSet
        self.activePosition = (0, 0, 0)
        self.activeLine = None
        self.color = color

    def BeginPath(self, position = (0, 0, 0)):
        self.lines.append(self.lineSet.AddLine(position, self.activePosition, self.color))

    def SetPosition(self, position):
        self.lines[-1].SetEndPosition(position)
        self.activePosition = position

    def ConfirmPoint(self):
        self.BeginPath(self.activePosition)

    def UndoPoint(self):
        if len(self.lines) <= 1:
            return
        self.lineSet.RemoveLine(self.lines[-1].lineID)
        self.lines = self.lines[:-1]
        self.activeLine = self.lines[-1]
        self.SetPosition(self.activePosition)

    def EndPath(self):
        self.lineSet.Clear()
        self.lines = []

    def GetPath(self):
        if len(self.lines) == 0:
            return ((0, 0, 0), (0, 0, 0))
        return (self.lines[0].startPos, self.lines[-1].endPos)

    def GetStartPosition(self):
        if len(self.lines) == 0:
            return None
        return self.lines[0].startPos

    def GetEndPosition(self):
        if len(self.lines) == 0:
            return None
        return self.lines[-1].endPos


class LineController:
    _singletonInstance = None
    _CONNECTOR_CONTAINER_PATH = 'res:/dx9/model/ui/lineContainer.red'
    _FREEFORM_LINESET_PATH = 'res:/dx9/model/ui/lineSetTransparent.red'
    __notifyevents__ = ['OnLoadScene']

    def __init__(self, scene = None):
        self._connectorContainer = trinity.Load(self._CONNECTOR_CONTAINER_PATH)
        self._freeformLineSet = trinity.Load(self._FREEFORM_LINESET_PATH)
        sm.RegisterNotify(self)
        if scene is None:
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        scene.objects.fremove(self._connectorContainer)
        scene.objects.append(self._connectorContainer)
        scene.objects.fremove(self._freeformLineSet)
        scene.objects.append(self._freeformLineSet)

    def AddSpaceObjectConnector(self, source, dest, lineType):
        if lineType not in _LINE_CONNECTORS:
            return
        redFile = _LINE_CONNECTORS[lineType]
        connector = trinity.Load(redFile)
        connector.sourceObject.parentPositionCurve = source
        connector.sourceObject.parentRotationCurve = source
        connector.sourceObject.alignPositionCurve = dest
        connector.destObject.parentPositionCurve = dest
        connector.destObject.parentRotationCurve = dest
        connector.destObject.alignPositionCurve = source
        self._connectorContainer.connectors.append(connector)
        return id(connector)

    def CreateLinePath(self, color = (1, 1, 1, 1)):
        return LinePath(self.CreateLineSet(), color)

    def CreateLineSet(self):
        return LineSet(self._freeformLineSet)

    def OnLoadScene(self, scene, key):
        scene.objects.fremove(self._connectorContainer)
        scene.objects.append(self._connectorContainer)
        scene.objects.fremove(self._freeformLineSet)
        scene.objects.append(self._freeformLineSet)

    @staticmethod
    def GetGlobalInstance(scene = None):
        if LineController._singletonInstance is None:
            LineController._singletonInstance = LineController(scene)
        return LineController._singletonInstance
