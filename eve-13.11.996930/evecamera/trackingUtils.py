#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\trackingUtils.py
import evecamera

def NormalizePoint(absolutePoint, displayRect):
    l, t, w, h = displayRect
    x, y = absolutePoint
    return ((x - l * 1.0) / w, (y - t * 1.0) / h)


def NormalizedPointToAbsolute(normalizedPoint, displayRect):
    x, y = normalizedPoint
    l, t, w, h = displayRect
    return (x * w + l, y * h + t)


def NormalizedPointToAbsoluteInflight(point):
    return NormalizedPointToAbsolute(point, GetRDpiInflight())


def NormalizedPointToAbsoluteInflightNoScaling(point):
    return NormalizedPointToAbsolute(point, uicore.layer.inflight.displayRect)


def NormalizePointToInflight(point):
    return NormalizePoint(point, GetRDpiInflight())


def GetDpiInflight():
    l, t, w, h = uicore.layer.inflight.displayRect
    w = uicore.ScaleDpi(w)
    h = uicore.ScaleDpi(h)
    return (l,
     t,
     w,
     h)


def GetRDpiInflight():
    return map(uicore.ReverseScaleDpi, uicore.layer.inflight.displayRect)


def ClampPoint(boundaries, p):
    x, y = p
    left, top, right, bottom = boundaries
    x = max(left, x)
    x = min(x, right)
    y = max(top, y)
    y = min(y, bottom)
    result = (x, y)
    return result


def GetCameraOffsetDesktopCenter():
    camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
    return GetCameraOffsetDesktopCenterWithOffset(camera.centerOffset)


def GetNormalizedCenter():
    camera = sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
    return GetNormalizedCenterWithOffset(camera.centerOffset)


def GetNormalizedCenterWithOffset(centerOffset):
    return (0.5 - 0.5 * centerOffset, 0.5)


def GetCameraOffsetDesktopCenterWithOffset(centerOffset):
    middle = uicore.desktop.width / 2
    return (uicore.ScaleDpi(middle * (1 - centerOffset)), uicore.ScaleDpi(uicore.desktop.height / 2))
