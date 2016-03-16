#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\dungeonhack.py
import blue
import geo2
import trinity
import carbonui.const as uiconst
import uthread

class DungeonHack(object):

    def __init__(self):
        self._Reset()
        self.InitAxisLines()

    def _Reset(self):
        self._clientToolsScene = None
        self._drawAxis = True
        self._gridEnabled = True
        self._gridSpacing = 10000.0
        self._gridLength = 200000.0

    def RemoveAxisLines(self):
        try:
            self._clientToolsScene.primitives.remove(self.axisLines)
        except ValueError:
            pass

        self.axisLines = None

    def InitAxisLines(self):
        self.axisLines = trinity.Tr2LineSet()
        self.axisLines.effect = trinity.Tr2Effect()
        self.axisLines.effect.effectFilePath = 'res:/Graphics/Effect/Managed/Utility/LinesWithZ.fx'
        self._clientToolsScene = self._GetClientToolsScene()
        self._clientToolsScene.primitives.append(self.axisLines)
        self._BuildGridAndAxes()

    def IsDrawingAxis(self):
        return self._drawAxis

    def SetDrawAxis(self, enabled = True):
        self._drawAxis = enabled
        self._BuildGridAndAxes()

    def IsGridEnabled(self):
        return self._gridEnabled

    def SetGridState(self, enabled = True):
        self._gridEnabled = enabled
        self._BuildGridAndAxes()

    def GetGridSpacing(self):
        return self._gridSpacing

    def SetGridSpacing(self, spacing = 100.0):
        if self._gridLength / spacing > 200:
            spacing = self._gridLength / 200
        elif self._gridLength / spacing <= 1:
            spacing = self._gridLength / 20
        if spacing < 1.0:
            spacing = 1.0
        self._gridSpacing = spacing
        self._BuildGridAndAxes()

    def GetGridLength(self):
        return self._gridLength

    def SetGridLength(self, length = 100.0):
        if length / self._gridSpacing > 200:
            self._gridSpacing = length / 200
        elif length / self._gridSpacing <= 1:
            self._gridSpacing = length / 20
        if length < 1.0:
            length = 1.0
        self._gridLength = length
        self._BuildGridAndAxes()

    def _BuildGridAndAxes(self):
        if self.axisLines is None:
            return
        self.axisLines.ClearLines()
        self.axisLines.SubmitChanges()
        red = (1, 0, 0, 1)
        green = (0, 1, 0, 1)
        blue = (0, 0, 1, 1)
        xAxis = (100.0, 0.0, 0.0)
        yAxis = (0.0, 100.0, 0.0)
        zAxis = (0.0, 0.0, 100.0)
        origin = (0.0, 0.0, 0.0)
        if self.IsDrawingAxis():
            self.axisLines.AddLine(origin, red, xAxis, red)
            self.axisLines.AddLine(origin, green, yAxis, green)
            self.axisLines.AddLine(origin, blue, zAxis, blue)
        if self.IsGridEnabled():
            grey = (0.4, 0.4, 0.4, 0.5)
            lightGrey = (0.5, 0.5, 0.5, 0.5)
            offWhite = (1, 1, 1, 0.8)
            minGridPos = -self._gridLength / 2.0
            maxGridPos = self._gridLength / 2.0
            halfNumSquares = int(self._gridLength / self._gridSpacing) / 2
            for i in xrange(-halfNumSquares, halfNumSquares + 1):
                color = grey
                if i % 10 == 0:
                    color = lightGrey
                if i % 20 == 0:
                    color = offWhite
                gridPos = i * self._gridSpacing
                startZ = (gridPos, 0.0, minGridPos)
                endZ = (gridPos, 0.0, maxGridPos)
                startX = (minGridPos, 0.0, gridPos)
                endX = (maxGridPos, 0.0, gridPos)
                if i != 0 or not self._drawAxis:
                    self.axisLines.AddLine(startZ, color, endZ, color)
                    self.axisLines.AddLine(startX, color, endX, color)
                else:
                    self.axisLines.AddLine(startZ, color, origin, color)
                    self.axisLines.AddLine(zAxis, color, endZ, color)
                    self.axisLines.AddLine(startX, color, origin, color)
                    self.axisLines.AddLine(xAxis, color, endX, color)

            color = offWhite
            startZ = (minGridPos, 0.0, minGridPos)
            endZ = (minGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, minGridPos)
            endX = (maxGridPos, 0.0, minGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
            startZ = (maxGridPos, 0.0, minGridPos)
            endZ = (maxGridPos, 0.0, maxGridPos)
            startX = (minGridPos, 0.0, maxGridPos)
            endX = (maxGridPos, 0.0, maxGridPos)
            self.axisLines.AddLine(startZ, color, endZ, color)
            self.axisLines.AddLine(startX, color, endX, color)
        self.axisLines.SubmitChanges()

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActivePrimaryCamera()

    def _GetClientToolsScene(self):
        if self._clientToolsScene is not None:
            return self._clientToolsScene
        renderManager = sm.GetService('sceneManager')
        rj = renderManager.fisRenderJob
        scene = rj.GetClientToolsScene()
        if scene is not None:
            self._clientToolsScene = scene
            return self._clientToolsScene
        self._clientToolsScene = trinity.Tr2PrimitiveScene()
        rj.SetClientToolsScene(self._clientToolsScene)
        return self._clientToolsScene
