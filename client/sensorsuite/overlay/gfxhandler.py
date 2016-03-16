#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\gfxhandler.py
import math
from carbon.common.lib.const import SEC
import evecamera
import gametime
from sensorsuite.overlay.const import SUPPRESS_GFX_WARPING, SWEEP_CYCLE_TIME_SEC, SWEEP_START_GRACE_TIME_SEC
import uthread
import logging
from sensorsuite.error import InvalidClientStateError
import blue
import uthread2
logger = logging.getLogger(__name__)

class GfxHandler:

    def __init__(self, sensorSuiteService, sceneManager, michelle):
        self.sensorSuiteService = sensorSuiteService
        self.sceneManager = sceneManager
        self.michelle = michelle
        self.gfxSensorSwipe = None
        self.gfxActiveSensorResults = {}
        self.suppressGfxReasons = set()
        self.gfxSwipeThread = None

    def Reset(self):
        self.gfxSensorSwipe = None
        self.gfxActiveSensorResults = {}
        self.suppressGfxReasons.discard(SUPPRESS_GFX_WARPING)
        self.gfxSwipeThread = None

    def StopGfxSwipe(self):
        if self.gfxSensorSwipe is None:
            return
        uthread.new(self._StopGfxSwipe)

    def _StopGfxSwipe(self):
        if self.gfxSensorSwipe is None:
            return
        fadeOutTime = 0.25
        for cs in self.gfxSensorSwipe.curveSets:
            if cs.name == 'Play':
                fadeOutTime = cs.GetMaxCurveDuration()
                cs.scale = -1.0
                cs.PlayFrom(fadeOutTime)
                break

        uthread2.SleepSim(fadeOutTime)
        if self.gfxSensorSwipe is None:
            return
        self.gfxSensorSwipe.display = False
        scene = self.sceneManager.GetRegisteredScene('default')
        if scene is not None:
            if self.gfxSensorSwipe in scene.objects:
                scene.objects.fremove(self.gfxSensorSwipe)
        self.gfxSensorSwipe = None

    def StopSwipeThread(self):
        if self.gfxSwipeThread is not None:
            self.gfxSwipeThread.kill()
            self.gfxSwipeThread = None

    def StartGfxSwipeThread(self, viewAngleInPlane):
        if self.gfxSwipeThread is not None:
            return
        self.gfxSwipeThread = uthread.worker('sensorSuite::_GfxSwipeThread', self._GfxSwipeThread, viewAngleInPlane)

    def _GfxSwipeThread(self, viewAngleInPlane):
        try:
            uthread2.SleepSim(SWEEP_START_GRACE_TIME_SEC)
            if self.sensorSuiteService.IsOverlayActive() or self.sensorSuiteService.sensorSweepActive:
                logger.debug('triggering a gfx swipe')
                self.StartGfxSwipe(viewAngleInPlane)
                uthread2.SleepSim(SWEEP_CYCLE_TIME_SEC)
                self.StopGfxSwipe()
        except InvalidClientStateError:
            pass
        finally:
            logger.debug('exiting gfx swipe thread')
            self.gfxSwipeThread = None

    def StartGfxSwipe(self, viewAngleInPlane):
        if self.suppressGfxReasons:
            return
        if self.gfxSensorSwipe is None:
            self.gfxSensorSwipe = blue.recycler.RecycleOrLoad('res:/fisfx/scanner/background.red')
        adjustedViewAngleInPlane = viewAngleInPlane + math.pi
        for child in self.gfxSensorSwipe.children:
            if child.mesh is not None:
                for area in list(child.mesh.transparentAreas) + list(child.mesh.additiveAreas):
                    if area.effect is not None:
                        for param in area.effect.parameters:
                            if param.name == 'SwipeData':
                                param.value = (param.value[0],
                                 adjustedViewAngleInPlane / (2.0 * math.pi),
                                 param.value[2],
                                 param.value[3])

        self.gfxSensorSwipe.display = True
        scene = self.sceneManager.GetRegisteredScene('default')
        if scene is not None:
            if self.gfxSensorSwipe not in scene.objects:
                scene.objects.append(self.gfxSensorSwipe)
            for cs in self.gfxSensorSwipe.curveSets:
                if cs.name == 'Rotater':
                    for c in cs.curves:
                        if c.name == 'Speed':
                            c.length = SWEEP_CYCLE_TIME_SEC

                    cs.scale = 1.0
                    cs.Play()
                elif cs.name == 'Play':
                    cs.scale = 1.0
                    cs.Play()

    def GetViewAngleInPlane(self):
        camera = self.sceneManager.GetActiveCamera()
        if camera is None:
            raise InvalidClientStateError('No camera found')
        viewVec = camera.GetLookAtDirection()
        viewAngleInPlane = math.atan2(viewVec[0], viewVec[2])
        return viewAngleInPlane

    def DisableGfx(self, reason):
        self.suppressGfxReasons.add(reason)
        self.StopGfxSwipe()

    def EnableGfx(self, reason):
        self.suppressGfxReasons.discard(reason)
        if not self.sensorSuiteService.IsOverlayActive():
            return
        if self.sensorSuiteService.sensorSweepActive:
            return
        if self.suppressGfxReasons:
            return

    def WaitForSceneReady(self):
        scene = self.sceneManager.GetRegisteredScene('default')
        startTime = gametime.GetSimTime()
        while scene is None and startTime + SEC * 15 < gametime.GetSimTime():
            uthread2.Sleep(0.25)
            if session.solarsystemid is None:
                raise InvalidClientStateError('Solarsystemid is None in session')
            scene = self.sceneManager.GetRegisteredScene('default')

        if scene is None:
            raise InvalidClientStateError('Failed to find the default space scene')
