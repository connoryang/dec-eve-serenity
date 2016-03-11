#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\tracking.py
import blue
import geo2
import math
import evecamera
import trinity
import trinutils.callbackmanager as cbmanager
import trackingUtils
from evecamera.trackingController import TrackingController

class Tracker(object):

    def __init__(self, cameraSvc):
        self._cameraSvc = cameraSvc
        self.job = None
        self.tracking = None
        self.previousTracking = None
        self.trackerRunning = False
        self.trackPointN = settings.char.ui.Get('tracking_cam_location_n', (0.3, 0.3))
        self.lastTime = blue.os.GetWallclockTime()
        self.trackSwitchTime = blue.os.GetWallclockTime()
        self.tiltX = 0
        self.tiltY = 0
        self.camMaxPitch = 0
        self.camMinPitch = 0
        self.startTrackSpeed = 0.008
        self.trackingController = TrackingController(0, 0)
        self.isCenteredMode = settings.char.ui.Get('track_is_centered', False)
        self.trackingController.isCenteredMode = self.isCenteredMode

    def TrackItem(self, itemID):
        if itemID == self._cameraSvc.LookingAt():
            return
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        if camera is None:
            return
        self.trackSwitchTime = blue.os.GetWallclockTime()
        if itemID is None and self.tracking is not None:
            self.previousTracking = None
            camera.maxPitch = self.trackingController.camMaxPitch
            camera.minPitch = self.trackingController.camMinPitch
            camera.rotationOfInterest = geo2.QuaternionIdentity()
            self.tiltX = 0
            self.tiltY = 0
        if self.trackerRunning and itemID is not None:
            camera.maxPitch = 2 * math.pi
            camera.minPitch = -2 * math.pi
            camera.SetOrbit(camera.yaw, camera.pitch)
        self.tracking = itemID
        if not self.trackerRunning:
            self.camMaxPitch = camera.maxPitch
            self.camMinPitch = camera.minPitch
            self.trackingController.SetPitchLimit(maxPitch=camera.maxPitch, minPitch=camera.minPitch)
            self.lastTime = blue.os.GetWallclockTime()
            cbmanager.CallbackManager.GetGlobal().ScheduleCallback(self._TrackItem, 'trackingCamera')

    def ForceStopTracking(self):
        self.trackerRunning = False
        cbmanager.CallbackManager.GetGlobal().UnscheduleCallbackByTag('trackingCamera')

    def _TrackItem(self):
        self.trackerRunning = True
        if self.tracking is not None:
            trackSpeed = self.startTrackSpeed
            if getattr(self, 'tempTrackSpeedForItem', None) is not None:
                if self.tempTrackSpeedForItem[0] != self.tracking:
                    self.tempTrackSpeedForItem = None
                else:
                    trackSpeed = self.tempTrackSpeedForItem[1]
            self._PointCameraTo(self.tracking, trackSpeed)
        else:
            self.lastTime = blue.os.GetWallclockTime()
            self.ForceStopTracking()

    def SetTemporaryTrackSpeed(self, itemID, trackSpeed):
        self.tempTrackSpeedForItem = (itemID, trackSpeed)

    def SetCenteredTrackingPoint(self):
        self.isCenteredMode = True
        self.trackingController.isCenteredMode = True
        self.trackPointN = None

    def SetTrackingPointNormalized(self, p):
        self.trackPointN = p
        self.isCenteredMode = False
        self.trackingController.isCenteredMode = False

    def _PointCameraTo(self, itemID, panSpeed = math.pi / 500):
        timeDelta = blue.os.TimeDiffInMs(self.lastTime, blue.os.GetWallclockTime())
        self.lastTime = blue.os.GetWallclockTime()
        camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        if camera is None:
            return
        shipBall = sm.GetService('michelle').GetBall(self._cameraSvc.LookingAt())
        if shipBall is None:
            return
        itemBall = sm.GetService('michelle').GetBall(itemID)
        if not itemBall:
            return
        if getattr(itemBall, 'exploded', False):
            explodedTime = getattr(itemBall, 'explodedTime', None)
            if explodedTime is None:
                return
            explosionWatchTime = 3.0
            timeSinceExplosionInSecs = blue.os.TimeDiffInMs(explodedTime, blue.os.GetTime()) / 1000.0
            if timeSinceExplosionInSecs > explosionWatchTime:
                return
            panSpeed *= 1.0 - timeSinceExplosionInSecs / explosionWatchTime
        if hasattr(itemBall, 'IsCloaked') and itemBall.IsCloaked():
            return
        shipPos = shipBall.GetVectorAt(blue.os.GetSimTime())
        itemPos = itemBall.GetVectorAt(blue.os.GetSimTime())
        t = blue.os.GetWallclockTime()
        timeSinceTargetChange = min(float(blue.os.TimeDiffInMs(self.trackSwitchTime, t)), 5000.0)
        rampUp = min(timeSinceTargetChange / 2000.0, 1.0)
        panSpeed *= rampUp
        if self.isCenteredMode:
            self.trackPointN = trackingUtils.GetNormalizedCenter()
        absoluteTrackPoint = trackingUtils.NormalizedPointToAbsoluteInflightNoScaling(self.trackPointN)
        arc = self.PointCameraToPos(camera, shipPos, itemPos, panSpeed, timeDelta, trackingPoint=absoluteTrackPoint)
        self.RotationAdjust(camera, timeSinceTargetChange, arc, itemID, timeDelta, trackingPoint=absoluteTrackPoint)
        self.UpdateInternalTrackingInfo()

    def UpdateInternalTrackingInfo(self):
        if self.previousTracking != self.tracking:
            self.trackSwitchTime = blue.os.GetWallclockTime()
            self.previousTracking = self.tracking

    def GetRotationDeltas(self, dx, dy, arc, timeSinceTargetChange, dt):
        percentOfWay = min(timeSinceTargetChange / 5000.0, 1)
        timeComponent = 1 - percentOfWay
        tiltBrake = 25000 + 1000000 * pow(arc, 2) * timeComponent
        maxMovement = 0.005
        multiplier = dt / 16.6
        dxmod = dx / tiltBrake
        dymod = dy / tiltBrake
        tdx = min(round(dxmod * multiplier, 4), maxMovement)
        tdy = min(round(dymod * multiplier, 4), maxMovement)
        return (tdx, tdy)

    def RotationAdjust(self, camera, timeSinceTargetChange, arc, itemID, timeDelta, trackingPoint):
        br = sm.GetService('bracket')
        itemBracket = br.GetBracket(itemID)
        if itemBracket is None:
            itemBracket = sm.GetService('sensorSuite').GetBracketByBallID(itemID)
        if itemBracket and itemBracket not in br.overlaps:
            bracketRender = itemBracket.renderObject
            if bracketRender is not None and bracketRender.display:
                if itemBracket.IsUnder(uicore.layer.bracket):
                    offset = uicore.layer.inflight.absoluteLeft
                else:
                    offset = 0
                offset = uicore.ScaleDpi(offset)
                trackX, trackY = trackingPoint
                dx = trackX - (bracketRender.displayX + bracketRender.displayWidth / 2) - offset
                dy = trackY - (bracketRender.displayY + bracketRender.displayHeight / 2)
                tdx, tdy = self.GetRotationDeltas(dx, dy, arc, timeSinceTargetChange, timeDelta)
                tiltAngle = geo2.Vec2Length((tdx, tdy))
                multiplier = min(timeDelta / 16.6, 1)
                minMoveAngle = 0.0005 * multiplier
                if tiltAngle > minMoveAngle:
                    self.tiltX += tdx
                    self.tiltY += tdy
                    self.tiltX = math.fmod(self.tiltX, math.pi * 2)
                    self.tiltY = math.fmod(self.tiltY, math.pi * 2)
                    camera.SetRotationOnOrbit(self.tiltX, self.tiltY)

    def clampPitch(self, pitch):
        return min(self.camMaxPitch, max(pitch, self.camMinPitch))

    def PointCameraToPos(self, camera, shipPos, itemPos, panSpeed, timeDelta, trackingPoint = None):
        return self.trackingController.PointCameraToPos(camera, shipPos, itemPos, panSpeed, timeDelta, trackingPoint)
