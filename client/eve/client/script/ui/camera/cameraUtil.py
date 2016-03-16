#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\cameraUtil.py
import math
from eve.client.script.ui.shared.systemMenu import betaOptions
from evecamera import LOOKATRANGE_MAX, LOOKATRANGE_MAX_NEW
from evegraphics import settings as gfxsettings
import geo2
import evespacescene

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
    if gfxsettings.Get(gfxsettings.UI_INVERT_CAMERA_ZOOM):
        dz = -uicore.uilib.dz
    else:
        dz = uicore.uilib.dz
    return GetPowerOfWithSign(dz)


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
