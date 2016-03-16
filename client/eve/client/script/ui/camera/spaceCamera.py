#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\spaceCamera.py
from math import sin, cos
from eve.client.script.ui.camera.cameraBase import CameraBase
from eve.client.script.ui.camera.cameraUtil import GetCameraMaxLookAtRange
import evecamera
import audio2
import blue
import trinity
import uthread
import state
import destiny
import localization
import telemetry
import evecamera.shaker as shaker
import evecamera.utils as camutils
import evecamera.cameratarget as camtarget
import evecamera.tracking
import evecamera.animation as camanim
import evegraphics.settings as gfxsettings
import evespacescene
SIZEFACTOR = 1e-07
TRANSLATION_MAX = 1000000.0

class SpaceCamera(CameraBase):
    cameraID = evecamera.CAM_SPACE_PRIMARY
    __notifyevents__ = ['OnSpecialFX',
     'DoBallClear',
     'DoBallRemove',
     'OnSessionChanged',
     'OnSetDevice',
     'OnGraphicSettingsChanged',
     'DoBallsRemove',
     'DoSimClockRebase',
     'OnBallparkSetState']

    def __init__(self):
        CameraBase.__init__(self)
        sm.RegisterNotify(self)
        self.ResetConfiguration()
        self.noise = gfxsettings.Get(gfxsettings.UI_CAMERA_SHAKE_ENABLED)
        self.UpdateCameraBobbing()
        self.checkDistToEgoThread = None
        self.cachedCameraTranslation = -1
        self.targetTracker = evecamera.tracking.Tracker(self)
        self.shakeController = shaker.ShakeController(self)
        self.animationController = camanim.AnimationController(self)
        self.lookingAt = None

    def UpdateCameraBobbing(self):
        self.idleMove = gfxsettings.Get(gfxsettings.UI_CAMERA_BOBBING_ENABLED)

    def ResetConfiguration(self):
        self.fieldOfView = evecamera.FOV_MAX
        self.friction = evecamera.DEFAULT_FRICTION
        self.maxSpeed = evecamera.DEFAULT_MAX_SPEED
        self.frontClip = evecamera.DEFAULT_FRONT_CLIP
        self.backClip = evecamera.DEFAULT_BACK_CLIP
        self.idleScale = evecamera.DEFAULT_IDLE_SCALE
        self.translationFromParent = -30.0
        self.idleSpeed = 0.5
        self.noiseScale = -2.010956
        self.noiseScaleCurve = trinity.TriScalarCurve()
        self.noiseScaleCurve.start = 126750659610511812L
        self.noiseScaleCurve.value = -2.010956
        self.noiseScaleCurve.extrapolation = 1
        self.noiseScaleCurve.AddKey(0.0, 0.0, 0.0, 0.0, 2)
        self.noiseScaleCurve.AddKey(0.5, -2.2945609, 0.0, 0.0, 2)
        self.noiseScaleCurve.AddKey(5.0, 0.0, 0.0, 0.0, 2)
        self.zoomCurve = trinity.TriScalarCurve()
        self.zoomCurve.start = 4644652442024148992L
        self.zoomCurve.value = 1.2
        self.zoomCurve.AddKey(0.0, evecamera.FOV_MAX, 0.0, 1.0, 3)
        self.zoomCurve.AddKey(0.224, evecamera.FOV_MAX, 0.0, -7.0, 3)
        self.zoomCurve.AddKey(0.45, evecamera.FOV_MAX, 0.0, -9.0, 3)
        self.zoomCurve.AddKey(0.6, evecamera.FOV_MAX, 0.0, 20.0, 3)
        self.zoomCurve.AddKey(0.0, evecamera.FOV_MAX, 0.0, 1.0, 3)

    def DoBallClear(self, solitem):
        cameraParent = self.GetCameraParent()
        if cameraParent is not None:
            cameraParent.parent = None

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if session.shipid is not None:
            lookingAtID = self.GetLookAtItemID()
            if lookingAtID is not None and ball.id == lookingAtID:
                if ball.explodeOnRemove and ball.id != session.shipid:
                    uthread.new(self._HandleTargetKilled, ball)
                else:
                    uthread.new(self._AdjustLookAtTarget, ball)
            elif self.cameraInterestID == ball.id and ball.explodeOnRemove:
                uthread.new(self._HandleTargetKilled, ball)

    def DoSimClockRebase(self, times):
        self.animationController.DoSimClockRebase(times)

    def _HandleTargetKilled(self, ball):
        delay = ball.GetExplosionLookAtDelay()
        blue.synchro.SleepSim(delay)
        lookingAtID = self.GetLookAtItemID()
        if lookingAtID == ball.id:
            self.LookAt(session.shipid)
        if self.cameraInterestID == ball.id:
            self.Track(None)

    def _AdjustLookAtTarget(self, ball):
        if session.shipid is None:
            return
        cameraParent = self.GetCameraParent()
        lookingAtID = self.GetLookAtItemID()
        if cameraParent and cameraParent.parent and cameraParent.parent == ball.model:
            cameraParent.parent = None
        if lookingAtID and ball.id == lookingAtID and lookingAtID != session.shipid:
            self.LookAt(session.shipid)

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration = -1, repeat = None, startTime = None, timeFromStart = 0, graphicInfo = None):
        if guid == 'effects.Warping':
            if shipID == session.shipid:
                if self.GetLookAtItemID() is not None and self.GetLookAtItemID() != session.shipid:
                    self.LookAt(session.shipid)

    def OnSetDevice(self, *args):
        if session.stationid:
            return
        blue.synchro.Yield()
        self.translationFromParent = self.CheckTranslationFromParent(self.translationFromParent)

    def OnBallparkSetState(self, *args):
        self.LookAt(session.shipid, self.cachedCameraTranslation, smooth=False)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'shipid' in change:
            oldID = change['shipid'][0]
            newID = change['shipid'][1]
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return
            if newID is not None and newID not in bp.slimItems and oldID is not None:
                self.lookingAt = newID
            else:
                self.LookAt(newID, self.cachedCameraTranslation)

    def _GetTrackableCurve(self, itemID):
        item = sm.StartService('michelle').GetBall(itemID)
        if item is None or getattr(item, 'model', None) is None:
            return
        if item.model.__bluetype__ in evespacescene.EVESPACE_TRINITY_CLASSES:
            behavior = trinity.EveLocalPositionBehavior.centerBounds
            tracker = trinity.EveLocalPositionCurve(behavior)
            tracker.parent = item.model
            return tracker
        return item

    def Track(self, itemID):
        self.cameraInterestID = itemID
        cameraInterest = self.GetCameraInterest()
        if itemID is None:
            cameraInterest.translationCurve = None
        trackable = self._GetTrackableCurve(itemID)
        cameraInterest.translationCurve = trackable

    def GetTrackItemID(self):
        return self.cameraInterestID

    def _AbortLookAtOther(self):
        self.ResetCamera()
        self.checkDistToEgoThread = None

    def _CheckDistanceToEgo(self):
        while self.checkDistToEgoThread is not None:
            if self.lookingAt is not None:
                lookingAtItem = sm.GetService('michelle').GetBall(self.lookingAt)
                if lookingAtItem is None or lookingAtItem.surfaceDist > GetCameraMaxLookAtRange():
                    self._AbortLookAtOther()
            blue.synchro.Yield()

    def _LookingAtSelf(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is not None and scene.dustfield is not None:
            scene.dustfield.display = True
        self.checkDistToEgoThread = None

    def _IsLookingAtOtherOK(self, item):
        obs = sm.GetService('target').IsObserving()
        if item is None:
            return False
        if item.mode == destiny.DSTBALL_WARP:
            return False
        if not obs and item.surfaceDist > GetCameraMaxLookAtRange():
            sm.GetService('gameui').Say(localization.GetByLabel('UI/Camera/OutsideLookingRange'))
            return False
        return True

    def _LookingAtOther(self):
        scene = sm.GetService('sceneManager').GetRegisteredScene('default')
        if scene is not None:
            if scene.dustfield is not None:
                scene.dustfield.display = False
        if self.checkDistToEgoThread is None:
            self.checkDistToEgoThread = uthread.pool('MenuSvc>checkDistToEgoThread', self._CheckDistanceToEgo)
        return True

    def _WaitForTech3Model(self, item):
        if item is None or getattr(item, 'model', None) is None:
            if hasattr(item, 'loadingModel'):
                while item.loadingModel:
                    blue.synchro.Yield()

    def LookAt(self, itemID, setZ = None, resetCamera = False, smooth = True, **kwargs):
        item = sm.StartService('michelle').GetBall(itemID)
        if not hasattr(item, 'GetModel') or item.GetModel() is None:
            return
        self._WaitForTech3Model(item)
        itemIdIsMyShip = itemID == session.shipid
        if itemIdIsMyShip:
            self._LookingAtSelf()
        elif self._IsLookingAtOtherOK(item):
            self._LookingAtOther()
        else:
            return
        cameraParent = self.GetCameraParent()
        if cameraParent is None:
            return
        self.GetCameraInterest().translationCurve = None
        sm.StartService('state').SetState(itemID, state.lookingAt, 1)
        self.lookingAt = itemID
        cache = itemIdIsMyShip
        item.LookAtMe()
        if itemIdIsMyShip is False:
            sm.ScatterEvent('OnLookAtOther', itemID)
        trackableItem = self._GetTrackableCurve(itemID)
        if not smooth:
            self.animationController.Schedule(camutils.SetTranslationCurve(trackableItem))
            self.animationController.Schedule(camutils.LookAt_Pan(setZ, 0.0, cache=cache))
        else:
            self._DoAnimatedLookAt(item, setZ, resetCamera, trackableItem, cache=cache)

    def _DoAnimatedLookAt(self, item, setZ = None, resetCamera = False, trackableItem = None, cache = False):
        if item.model.__bluetype__ not in evespacescene.EVESPACE_TRINITY_CLASSES:
            self.animationController.Schedule(camutils.SetTranslationCurve(trackableItem))
            return
        behavior = trinity.EveLocalPositionBehavior.centerBounds
        tracker = trinity.EveLocalPositionCurve(behavior)
        tracker.parent = item.model
        self.animationController.Schedule(camutils.LookAt_Translation(tracker))
        self.animationController.Schedule(camutils.LookAt_FOV(resetCamera))
        self.animationController.Schedule(camutils.LookAt_Pan(setZ, cache=cache))

    def PanCameraBy(self, percentage, time = 0.0, cache = False):
        beg = self.translationFromParent
        end = beg + beg * percentage
        self.PanCamera(beg, end, time, cache)

    def PanCamera(self, cambeg = None, camend = None, time = 0.5, cache = False, source = None):
        cacheTranslation = cache and self.GetLookAtItemID() == session.shipid
        self.animationController.Schedule(camutils.PanCamera(cambeg, camend, time, cacheTranslation, source))

    def TranslateFromParentAccelerated(self, begin, end, durationSec, accelerationPower = 2.0):
        self.animationController.Schedule(camutils.PanCameraAccelerated(begin, end, durationSec, accelerationPower))

    def ClearAnimations(self):
        self.animationController.ClearAll()

    def CacheCameraTranslation(self):
        self.cachedCameraTranslation = self.translationFromParent

    def ClearCameraParent(self):
        if self.cameraParent:
            self.cameraParent.translationCurve = None
            self.cameraParent = None

    def GetCameraParent(self):
        if self.cameraParent is None:
            self.cameraParent = camtarget.CameraTarget(self)
        return self.cameraParent

    def GetCameraInterest(self):
        if self.cameraInterest is None:
            self.cameraInterest = camtarget.CameraTarget(self, 'interest')
        return self.cameraInterest

    def ResetCamera(self, *args):
        sm.ScatterEvent('OnLookAtMyShip', session.shipid)
        self.LookAt(session.shipid, resetCamera=True)

    def GetLookAtItemID(self):
        return self.lookingAt

    def _GetTranslationFromParentForItem(self, itemID):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        ball = ballpark.GetBall(itemID)
        ball, model, ballRadius = ball, getattr(ball, 'model', None), getattr(ball, 'radius', None)
        if model is None:
            return
        rad = None
        if model.__bluetype__ in evespacescene.EVESPACE_TRINITY_CLASSES:
            rad = model.GetBoundingSphereRadius()
            zoomMultiplier = 1.1 * camutils.GetARZoomMultiplier(trinity.GetAspectRatio())
            return (rad + self.frontClip) * zoomMultiplier + 2
        if len(getattr(model, 'children', [])) > 0:
            rad = ball.model.children[0].GetBoundingSphereRadius()
        if rad is None or rad <= 0.0:
            rad = ballRadius
        camangle = self.fieldOfView * 0.5
        return max(15.0, rad / sin(camangle) * cos(camangle))

    def CheckTranslationFromParent(self, distance, distanceIsScale = False):
        mn, mx = self._GetMinMaxTranslationFromParent()
        if distanceIsScale:
            distance = mn * distance
        retval = max(mn, min(distance, mx))
        return retval

    def _GetMinMaxTranslationFromParent(self):
        lookingAt = self.GetLookAtItemID() or session.shipid
        mn = self._GetTranslationFromParentForItem(lookingAt)
        mx = TRANSLATION_MAX
        return (mn, mx)

    def ShakeCamera(self, magnitude, position, key = None):
        behavior = camutils.CreateBehaviorFromMagnitudeAndPosition(magnitude, position, self)
        if behavior is None:
            return
        behavior.key = key
        self.shakeController.DoCameraShake(behavior)

    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.UI_CAMERA_SHAKE_ENABLED in changes:
            self.shakeController.Enable(gfxsettings.Get(gfxsettings.UI_CAMERA_SHAKE_ENABLED))
        if gfxsettings.UI_CAMERA_BOBBING_ENABLED in changes:
            self.UpdateCameraBobbing()

    def OnActivated(self, *args, **kwargs):
        self.audio2Listener = audio2.GetListener(0)

    def OnDeactivated(self, *args, **kwargs):
        self.audio2Listener = None
