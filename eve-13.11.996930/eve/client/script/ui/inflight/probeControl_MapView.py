#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\probeControl_MapView.py
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
import trinity
import carbonui.const as uiconst
import geo2
import random
import math
import nodemanager
BASE_PROBE_COLOR = (0.45098039215686275, 0.9411764705882353, 1.0, 0)
CURSOR_COLOR_PARAMETER_INDEX = 2
CURSOR_IDLE_COLOR = BASE_PROBE_COLOR
CURSOR_ACTIVE_COLOR = (0.5, 0.0, 0.0, 1.0)
TR2TM_LOOK_AT_CAMERA = 3

class BaseProbeControl(object):
    formationCenter = None
    STATE_IDLE = 0
    STATE_ACTIVE = 1
    STATE_ACTIVE_SINGLE = 2
    spreadCursor = None
    rangeCursor = None
    _cursorState = None

    def __init__(self, uniqueID, parent):
        locator = trinity.EveTransform()
        locator.name = 'spherePar_%s' % uniqueID
        try:
            parent.children.append(locator)
        except:
            parent.objects.append(locator)

        CURSOR_SCALE_ARG_1 = 2000000.0
        CURSOR_SCALE = SOLARSYSTEM_SCALE * 250000000000.0
        cursor = trinity.Load('res:/Model/UI/probeCursor.red')
        cursor.scaling = (CURSOR_SCALE, CURSOR_SCALE, CURSOR_SCALE)
        cursor.useDistanceBasedScale = True
        cursor.distanceBasedScaleArg1 = CURSOR_SCALE_ARG_1
        cursor.distanceBasedScaleArg2 = 0.0
        cursor.translation = (0.0, 0.0, 0.0)
        for c in cursor.children:
            c.name += '_' + str(uniqueID)

        locator.children.append(cursor)
        self.uniqueID = uniqueID
        self.cursor = cursor
        self.locator = locator

    def SetFormationCenter(self, centerPosition):
        self.formationCenter = centerPosition
        q = geo2.QuaternionRotationArc((0.0, 0.0, 1.0), geo2.Vec3Normalize(geo2.Vec3Subtract(self.formationCenter, self.locator.translation)))
        if self.spreadCursor:
            self.spreadCursor.rotation = q
        if self.rangeCursor:
            self.rangeCursor.rotation = q

    def SetPosition(self, position):
        position = geo2.Vector(*position)
        self.locator.translation = position

    def GetPosition(self):
        return geo2.Vector(self.locator.translation)

    def GetWorldPosition(self):
        return geo2.Vector(self.locator.worldTransform[3][:3])

    def SetCursorState(self, cursorState, hiliteAxis = None):
        if self._cursorState == (cursorState, hiliteAxis):
            return
        self._cursorState = (cursorState, hiliteAxis)
        if cursorState == self.STATE_ACTIVE:
            color = CURSOR_ACTIVE_COLOR
        else:
            color = CURSOR_IDLE_COLOR
        for each in self.cursor.children:
            if hiliteAxis and cursorState == self.STATE_ACTIVE:
                cursorName, side, probeID = each.name.split('_')
                cursorAxis = cursorName[6:].lower()
                if hiliteAxis == cursorAxis:
                    each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = CURSOR_ACTIVE_COLOR
                else:
                    each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = CURSOR_IDLE_COLOR
            else:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color

        if self.spreadCursor:
            for each in self.spreadCursor.children:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color

        if self.rangeCursor:
            for each in self.rangeCursor.children:
                each.mesh.opaqueAreas[0].effect.parameters[CURSOR_COLOR_PARAMETER_INDEX].value = color


class ProbeControl(BaseProbeControl):

    def __init__(self, probeID, probe, parent):
        scanSvc = sm.GetService('scanSvc')
        BaseProbeControl.__init__(self, probeID, parent)
        sphere = trinity.Load('res:/dx9/model/UI/Scanbubbledoteffect.red')
        self.locator.children.append(sphere)
        self.sphere = sphere
        scanbubble = nodemanager.FindNode(sphere, 'Scanbubble', 'trinity.EveTransform')
        for each in scanbubble.children:
            each.scaling = tuple([ (100 if scaling > 0 else -100) for scaling in each.scaling ])

        CURSOR_SCALE_ARG_1 = 2000000.0
        CURSOR_SCALE = SOLARSYSTEM_SCALE * 250000000000.0
        cursor = trinity.Load('res:/Model/UI/probeSpreadCursor.red')
        cursor.scaling = (CURSOR_SCALE, CURSOR_SCALE, CURSOR_SCALE)
        cursor.useDistanceBasedScale = True
        cursor.distanceBasedScaleArg1 = CURSOR_SCALE_ARG_1
        cursor.distanceBasedScaleArg2 = 0.0
        cursor.translation = (0.0, 0.0, 0.0)
        for c in cursor.children:
            c.name += '_' + str(probeID)

        self.locator.children.append(cursor)
        self.spreadCursor = cursor
        cursor = trinity.Load('res:/Model/UI/probeRangeCursor.red')
        for c in cursor.children:
            c.scaling = (250.0, 250.0, 250.0)
            c.name += '_' + str(probeID)
            c.mesh.geometryResPath = 'res:/Graphics/generic/vortex/Cone2.gr2'
            c.rotation = geo2.QuaternionRotationSetYawPitchRoll(0.0, math.pi * 0.5, 0.0)

        self.locator.children.append(cursor)
        self.rangeCursor = cursor
        self.scanRanges = scanSvc.GetScanRangeStepsByTypeID(probe.typeID)
        self.probeID = probeID
        self.scanrangeCircles = None
        self._highlighted = True
        self.HighlightBorder(0)
        uicore.animations.MorphVector3(self.locator, 'scaling', startVal=(0.0, 0.0, 0.0), endVal=(1.0, 1.0, 1.0), duration=0.5, curveType=uiconst.ANIM_OVERSHOT, timeOffset=random.random() * 0.5)

    def SetScanDronesState(self, state):
        scanEffectTf = nodemanager.FindNode(self.sphere, 'scanLines', 'trinity.EveTransform')
        if scanEffectTf:
            scanEffectTf.display = state
            if state:
                scanLinesCurveSet = nodemanager.FindNode(scanEffectTf, 'ScanCurveSet', 'trinity.TriCurveSet')
                if scanLinesCurveSet:
                    scanLinesCurveSet.Play()

    def SetRange(self, probeRange):
        self.sphere.scaling = (probeRange, probeRange, probeRange)
        self.rangeCursor.children[0].translation = (0.0, 0.0, -probeRange + 250.0)

    def ScaleRange(self, scale):
        scale = self.sphere.scaling[0] * scale
        self.SetRange((scale, scale, scale))

    def GetRange(self):
        return self.sphere.scaling[0]

    def HighlightBorder(self, on = 1):
        if bool(on) == self._highlighted:
            return
        self._highlighted = bool(on)
        curveSets = self.sphere.Find('trinity.TriCurveSet')
        curveSet = None
        for each in curveSets:
            if getattr(each, 'name', None) == 'Highlight':
                curveSet = each
                break

        if curveSet:
            curveSet.Stop()
            if on:
                curveSet.scale = 10.0
                curveSet.Play()
            else:
                curveSet.scale = -1.0
                curveSet.PlayFrom(curveSet.GetMaxCurveDuration())

    def HideScanRanges(self):
        if self.scanrangeCircles is not None:
            self.scanrangeCircles.display = False

    def ShowScanRanges(self):
        if self.scanrangeCircles is None:
            par = trinity.EveTransform()
            self.scanrangeCircles = par
            par.modifier = TR2TM_LOOK_AT_CAMERA
            self.locator.children.append(par)
            for r in self.scanRanges:
                r *= 100.0
                sr = trinity.Load('res:/Model/UI/probeRange.red')
                sr.scaling = (r, r, r)
                par.children.append(sr)

        self.scanrangeCircles.display = True

    def HighlightProbe(self):
        self.HighlightBorder(1)

    def StopHighlightProbe(self):
        self.HighlightBorder(0)
