#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\trackingController.py
import trinity
import math
import geo2

class TrackingController:

    def __init__(self, maxPitch, minPitch):
        self.camMaxPitch = maxPitch
        self.camMinPitch = minPitch
        self.isCenteredMode = False

    def SetCenteredMode(self, mode):
        self.isCenteredMode = mode

    def SetPitchLimit(self, maxPitch, minPitch):
        self.camMaxPitch = maxPitch
        self.camMinPitch = minPitch

    def clampPitch(self, pitch):
        return min(self.camMaxPitch, max(pitch, self.camMinPitch))

    def CalcAngle(self, x, y):
        angle = 0
        if x != 0:
            angle = math.atan(y / x)
            if x < 0 and y >= 0:
                angle = math.atan(y / x) + math.pi
            if x < 0 and y < 0:
                angle = math.atan(y / x) - math.pi
        else:
            if y > 0:
                angle = math.pi / 2
            if y < 0:
                angle = -math.pi / 2
        return angle

    def GetAlphasDesktop(self, camera, trackingPoint):
        m, h = uicore.desktop.width / 2, uicore.desktop.height
        center = trinity.TriVector(uicore.ScaleDpi(m * (1 - camera.centerOffset)), uicore.ScaleDpi(h / 2), 0)
        dx2 = center.x - trackingPoint[0]
        dy2 = center.y - trackingPoint[1]
        alphaX = math.pi * dx2 * camera.fieldOfView / uicore.ScaleDpi(uicore.desktop.width)
        alphaY = math.pi * dy2 * camera.fieldOfView / uicore.ScaleDpi(uicore.desktop.width)
        alphaX75 = alphaX * 0.75
        alphaY75 = alphaY * 0.75
        return (alphaX75, alphaY75)

    def PointCameraToPos(self, camera, shipPos, itemPos, panSpeed, timeDelta, trackingPoint = None):
        v2 = shipPos - itemPos
        v2.Normalize()
        yzProj = trinity.TriVector(0, v2.y, v2.z)
        zxProj = trinity.TriVector(v2.x, 0, v2.z)
        yaw = self.CalcAngle(zxProj.z, zxProj.x)
        pitch = -math.asin(min(1.0, max(-1.0, yzProj.y)))
        oldYaw = camera.yaw
        oldPitch = self.clampPitch(camera.pitch)
        alphaX75 = 0
        alphaY75 = 0
        if not self.isCenteredMode and trackingPoint is not None:
            alphaX75, alphaY75 = self.GetAlphasDesktop(camera, trackingPoint)
        dPitchTotal = pitch - oldPitch
        dYawTotal = (yaw - camera.yaw) % (2 * math.pi) - alphaX75
        clampedPitchTotal = min(2 * math.pi - dPitchTotal, dPitchTotal) - alphaY75
        if dYawTotal > math.pi:
            dYawTotal = -(2 * math.pi - dYawTotal)
        arc = geo2.Vec2Length((dYawTotal, clampedPitchTotal))
        part = min(1, timeDelta * panSpeed)
        dYawPart = dYawTotal * part
        dPitchPart = clampedPitchTotal * part
        Yaw = oldYaw + dYawPart
        Pitch = oldPitch + dPitchPart
        camera.SetOrbit(Yaw, Pitch)
        return arc
