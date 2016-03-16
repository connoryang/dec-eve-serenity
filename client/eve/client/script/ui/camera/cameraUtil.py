#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\cameraUtil.py
import math
from eve.client.script.ui.shared.systemMenu import betaOptions
from evecamera import LOOKATRANGE_MAX, LOOKATRANGE_MAX_NEW
from evegraphics import settings as gfxsettings
import geo2
import evespacescene
import trinity
import blue
import destiny
from evecamera.utils import GetARZoomMultiplier
import uthread

def IsNewCameraActive():
    return betaOptions.BetaFeatureEnabled(betaOptions.BETA_NEWCAM_SETTING_KEY)


def SetNewCameraActive():
    settings.char.ui.Set('isNewCameraActive', True)


def SetNewCameraInactive():
    settings.char.ui.Set('isNewCameraActive', False)


def IsBobbingEnabled():
    return gfxsettings.Get(gfxsettings.UI_CAMERA_BOBBING_ENABLED)


def GetCameraMaxLookAtRange():
    if IsNewCameraActive():
        return LOOKATRANGE_MAX_NEW
    else:
        return LOOKATRANGE_MAX


def SetShipDirection(camera):
    scene = sm.GetService('sceneManager').GetRegisteredScene('default')
    proj = camera.projectionMatrix.transform
    view = camera.viewMatrix.transform
    pickDir = scene.PickInfinity(uicore.ScaleDpi(uicore.uilib.x), uicore.ScaleDpi(uicore.uilib.y), proj, view)
    if pickDir:
        bp = sm.GetService('michelle').GetRemotePark()
        if bp is not None:
            try:
                bp.CmdGotoDirection(pickDir[0], pickDir[1], pickDir[2])
                sm.ScatterEvent('OnClientEvent_MoveWithDoubleClick')
                sm.GetService('menu').ClearAlignTargets()
                sm.GetService('flightPredictionSvc').GotoDirection(pickDir)
            except RuntimeError as e:
                if e.args[0] != 'MonikerSessionCheckFailure':
                    raise e


def GetZoomDz():
    dz = CheckInvertZoom(uicore.uilib.dz)
    return GetPowerOfWithSign(dz)


def CheckInvertZoom(dz):
    if gfxsettings.Get(gfxsettings.UI_INVERT_CAMERA_ZOOM):
        return -dz
    return dz


def GetPowerOfWithSign(value, power = 1.1):
    return math.copysign(math.fabs(value) ** power, value)


def GetDurationByDistance(pos0, pos1, minTime = 0.3, maxTime = 1.0):
    dist = geo2.Vec3Distance(pos0, pos1)
    duration = max(minTime, min(minTime + (maxTime - minTime) * dist / 100000.0, maxTime))
    return duration


def GetBallRadius(ball):
    model = getattr(ball, 'model', None)
    rad = None
    if model and model.__bluetype__ in evespacescene.EVESPACE_TRINITY_CLASSES:
        rad = model.GetBoundingSphereRadius()
    elif model and len(getattr(model, 'children', [])) > 0:
        rad = model.children[0].GetBoundingSphereRadius()
    if rad is None or rad <= 0.0:
        rad = ball.radius
    return rad


def GetBallPosition(ball):
    if hasattr(ball, 'model') and not isinstance(ball.model, trinity.EvePlanet):
        elpc = trinity.EveLocalPositionCurve()
        elpc.parent = ball.model
        elpc.behavior = trinity.EveLocalPositionBehavior.centerBounds
        vec = elpc.GetVectorAt(blue.os.GetSimTime())
    else:
        vec = ball.GetVectorAt(blue.os.GetSimTime())
    return (vec.x, vec.y, vec.z)


def GetBall(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if not bp:
        return None
    return bp.GetBall(itemID)


def GetBallMaxZoom(ball, nearClip):
    rad = GetBallRadius(ball)
    zoomMultiplier = 1.5 * GetARZoomMultiplier(trinity.GetAspectRatio())
    return (rad + nearClip) * zoomMultiplier + 2


def IsBallWarping(itemID):
    ball = GetBall(itemID)
    if not ball:
        return False
    return ball.mode == destiny.DSTBALL_WARP


def IsAutoTrackingEnabled():
    return settings.char.ui.Get('orbitCameraAutoTracking', False)


def CheckShowModelTurrets(ball):
    if hasattr(ball, 'LookAtMe'):
        uthread.new(ball.LookAtMe)


class Vector3Chaser(object):

    def __init__(self, speed = 1.0):
        self._value = (0, 0, 0)
        self._targetValue = None
        self._speed = speed

    def GetValue(self):
        return self._value

    def SetValue(self, value, speed = None):
        self._targetValue = value
        if speed is not None:
            self._speed = speed

    def Update(self):
        if not self._targetValue or self._targetValue == self._value:
            return
        if self._speed == 0.0:
            return
        dt = 1.0 / blue.os.fps
        diff = geo2.Vec3Subtract(self._targetValue, self._value)
        prop = dt * (1.0 * self._speed)
        prop = min(1.0, prop)
        dV = geo2.Vec3Scale(diff, prop)
        self._value = geo2.Vec3Add(self._value, dV)
        if prop == 1.0:
            self._targetValue = None

    def ResetValue(self, speed = None):
        self.SetValue((0, 0, 0), speed)


class VectorLerper(object):

    def __init__(self, duration = 1.0):
        self.duration = duration
        self.startTime = blue.os.GetSimTime()

    def GetValue(self, v0, v1):
        t = (blue.os.GetSimTime() - self.startTime) / float(SEC)
        if t >= self.duration:
            return v1
        elif hasattr(v0, '__iter__'):
            return geo2.Lerp(v0, v1, t / self.duration)
        else:
            return v0 + (v1 - v0) * t
