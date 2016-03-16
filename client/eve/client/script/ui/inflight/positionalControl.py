#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\positionalControl.py
import blue
import uthread2
from evegraphics.ui.controlPaths import SinglePointPath

class PositionalControl:
    __notifyevents__ = ['OnBallparkCall']

    def __init__(self):
        self._cameraController = None
        self._currentPath = None
        self._activeIDs = []
        self._finalizeFunction = None
        self._updateRunning = False
        sm.RegisterNotify(self)

    def IsActive(self):
        return self._currentPath is not None

    def SetCameraController(self, cameraController):
        self._cameraController = cameraController
        if self._currentPath is None:
            self.AbortCommand()

    def AbortCommand(self):
        if self._currentPath is not None:
            self._currentPath.Abort()
        self._currentPath = None
        self._activeIDs = []
        self._finalizeFunction = None
        self._EnableUpdate(False)

    def StartFighterMoveCommand(self, fighterIDs):
        if len(fighterIDs) < 1:
            return
        if self._currentPath is not None:
            self._currentPath.Abort()
        self._currentPath = SinglePointPath()
        self._currentPath.Start()
        self._activeIDs = fighterIDs
        self._finalizeFunction = self._MoveFighters
        self._EnableUpdate(True)

    def _EnableUpdate(self, enable):
        if enable and not self._updateRunning:
            uthread2.StartTasklet(self._UpdateThread)
        self._updateRunning = enable

    def _Finalize(self):
        self._finalizeFunction()
        self.AbortCommand()

    def _ConvertPositionToGlobalSpace(self, position):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        egopos = bp.GetCurrentEgoPos()
        destination = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
        return destination

    def _MoveFighters(self):
        fighterSvc = sm.GetService('fighters')
        destination = self._ConvertPositionToGlobalSpace(self._currentPath.GetEndPosition())
        if destination is None:
            return
        for fighterID in self._activeIDs:
            fighterSvc.CmdGotoPoint(fighterID, destination)

    def AddPoint(self):
        if self._currentPath is None or self._cameraController is None:
            return
        self._currentPath.UpdatePosition(self._cameraController)
        self._currentPath.AddPoint()
        if self._currentPath.IsComplete():
            uthread2.StartTasklet(self._Finalize)

    def _UpdateThread(self):
        while self._updateRunning:
            if self._currentPath is not None and self._cameraController is not None:
                self._currentPath.UpdatePosition(self._cameraController)
            blue.synchro.Yield()

    def OnBallparkCall(self, functionName, callArgument, **kwargs):
        if functionName in ('WarpTo',):
            self.AbortCommand()

    def OnSessionChanged(self, isremote, session, change):
        self.AbortCommand()
