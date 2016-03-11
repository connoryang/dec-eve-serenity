#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewScannerNavigationStandalone.py
from carbon.common.script.util.format import FmtDist
from carbon.common.script.util.timerstuff import AutoTimer
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
from carbonui.primitives.base import ScaleDpi
from carbonui.util.various_unsorted import SortListOfTuples
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation
from eve.client.script.ui.shared.mapView.mapViewProbeHandlerStandalone import MODIFY_POSITION, MODIFY_RANGE, MODIFY_SPREAD
import geo2
import blue
X_AXIS = (1.0, 0.0, 0.0)
Y_AXIS = (0.0, 1.0, 0.0)
Z_AXIS = (0.0, 0.0, 1.0)

class MapViewScannerNavigation(MapViewNavigation):
    movingProbe = None
    rangeProbe = None
    activeManipAxis = None
    modifyHint = None
    borderPickedProbeControl = None
    cursorPickedProbeControl = None
    _keyState = None

    def PickScene(self, mouseX, mouseY):
        if uicore.uilib.mouseOver is self:
            self.mapView.SetHilightItem(None)
        if not (self.movingProbe or self.rangeProbe):
            probeHandler = self.GetProbeHandler()
            if probeHandler:
                picktype, pickobject = self.GetPick()
                if pickobject and pickobject.name.startswith('cursor'):
                    cursorName, side, probeID = pickobject.name.split('_')
                    probeControl = probeHandler.GetProbeControl(probeID)
                    cursorAxis = cursorName[6:]
                    axis = cursorAxis.lower()
                else:
                    probeControl = None
                    axis = None
                probeHandler.HighlightCursors(probeControl, axis)
                self.cursorPickedProbeControl = probeControl
                if not probeControl and probeHandler.GetEditMode() not in (MODIFY_RANGE, MODIFY_SPREAD):
                    borderPickedProbeControl = self.PickProbes(pickBorder=True)
                else:
                    borderPickedProbeControl = None
                probeHandler.HighlightProbeBorder(borderPickedProbeControl)
                self.borderPickedProbeControl = borderPickedProbeControl
                scenePickActive = bool(self.borderPickedProbeControl or self.cursorPickedProbeControl)
                self.mapView.markersHandler.SetScenePickState(scenePickActive)

    def MapMarkerPickingOverride(self, *args, **kwds):
        self.PickScene(uicore.uilib.x, uicore.uilib.y)
        return bool(self.borderPickedProbeControl or self.cursorPickedProbeControl)

    def OnMouseWheel(self, wheelDelta, *args):
        if not uicore.uilib.leftbtn:
            probeHandler = self.GetProbeHandler()
            scanSvc = sm.GetService('scanSvc')
            if probeHandler and probeHandler.HasAvailableProbes():
                if uicore.uilib.Key(uiconst.VK_CONTROL):
                    scaling = 0.9
                    if wheelDelta < 0:
                        scaling = 1.0 / scaling
                    scanSvc.ScaleFormationSpread(scaling)
                    return True
                if uicore.uilib.Key(uiconst.VK_MENU):
                    scaling = 0.5
                    if wheelDelta < 0:
                        scaling = 1.0 / scaling
                    scanSvc.ScaleFormation(scaling)
                    return True
        return MapViewNavigation.OnMouseWheel(self, wheelDelta, *args)

    def OnMouseMove(self, *args):
        if uicore.IsDragging() or self.destroyed:
            return
        camera = self.mapView.camera
        if camera is None:
            return
        lib = uicore.uilib
        if lib.leftbtn and (self.movingProbe or self.rangeProbe):
            return
        return MapViewNavigation.OnMouseMove(self, *args)

    def OnDblClick(self, *args):
        if self.destroyed:
            return
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            picktype, pickobject = self.GetPick()
            if pickobject and pickobject.name.startswith('cursor'):
                cursorName, side, probeID = pickobject.name.split('_')
                probeHandler.FocusOnProbe(probeID)
            else:
                mouseInsideProbes = self.PickProbes()
                if mouseInsideProbes:
                    try:
                        probeHandler.FocusOnProbe(mouseInsideProbes[0].probeID)
                    except KeyError:
                        pass

        self.ClickPickedObject(True, uicore.uilib.x, uicore.uilib.y)

    def GetModifyHint(self):
        if self.modifyHint is None or self.modifyHint.destroyed:
            self.modifyHint = EveLabelMedium(parent=self)
        return self.modifyHint

    def CloseModifyHint(self):
        if self.modifyHint and not self.modifyHint.destroyed:
            self.modifyHint.Close()
            self.modifyHint = None

    def UpdateModifyHintPosition(self):
        if self.modifyHint and not self.modifyHint.destroyed:
            left, top = self.GetAbsolutePosition()
            self.modifyHint.left = uicore.uilib.x + 10 - left
            self.modifyHint.top = uicore.uilib.y + 16 - top

    def OnMouseDown(self, button):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            if button == uiconst.MOUSELEFT:
                picktype, pickobject = self.GetPick()
                rangeProbe = None
                if pickobject and pickobject.name[:6] == 'cursor':
                    cursorName, side, probeID = pickobject.name.split('_')
                    if probeID:
                        pickedProbeControl = probeHandler.GetProbeControl(probeID)
                        if pickedProbeControl and probeHandler.GetEditMode() in (MODIFY_POSITION, MODIFY_SPREAD):
                            cursorAxis = cursorName[6:]
                            self.movingProbe = pickedProbeControl
                            self.activeManipAxis = cursorAxis.lower()
                            self.activeTargetPlaneNormal = self.GetAxisTargetPlaneNormal()
                            self.initProbeScenePosition = pickedProbeControl.GetWorldPosition()
                            self.initCenterScenePosition = probeHandler.GetWorldPositionCenterOfActiveProbes()
                            probeHandler.InitProbeMove(self.initProbeScenePosition, self.initCenterScenePosition, self.GetDotInAxisAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInAxisAlignedPlaneFromPosition(self.initCenterScenePosition))
                            self.scalingOrMoveTimer = AutoTimer(1, self.ScaleOrMoveActiveProbe)
                            return
                        if pickedProbeControl and probeHandler.GetEditMode() == MODIFY_RANGE:
                            rangeProbe = pickedProbeControl
                if not rangeProbe and self.borderPickedProbeControl:
                    pickedProbeControl = self.PickProbes(pickBorder=True)
                    if pickedProbeControl is self.borderPickedProbeControl:
                        rangeProbe = pickedProbeControl
                if rangeProbe:
                    self.rangeProbe = pickedProbeControl
                    self.initProbeScenePosition = pickedProbeControl.GetWorldPosition()
                    self.initCenterScenePosition = probeHandler.GetWorldPositionCenterOfActiveProbes()
                    probeHandler.InitProbeScaling(self.initProbeScenePosition, self.initCenterScenePosition, self.GetDotInCameraAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInCameraAlignedPlaneFromPosition(self.initCenterScenePosition))
                    pickedProbeControl.ShowScanRanges()
                    self.scalingOrMoveTimer = AutoTimer(1, self.ScaleOrMoveActiveProbe)
                    return
            if probeHandler.GetActiveEditMode():
                return
        return MapViewNavigation.OnMouseDown(self, button)

    def OnMouseUp(self, button):
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            if button == uiconst.MOUSERIGHT:
                if uicore.uilib.leftbtn and (self.movingProbe or self.rangeProbe):
                    probeHandler.CancelProbeMoveOrScaling()
                    self.movingProbe = None
                    self.rangeProbe = None
                    self.scalingOrMoveTimer = None
                    self.CloseModifyHint()
                return
            if button == uiconst.MOUSELEFT:
                if self.rangeProbe:
                    probeHandler.RegisterProbeScale(self.rangeProbe)
                    self.scalingOrMoveTimer = None
                    self.rangeProbe = None
                if self.movingProbe:
                    probeHandler.RegisterProbeMove(self.movingProbe)
                    self.scalingOrMoveTimer = None
                    self.movingProbe = None
                self.CloseModifyHint()
        return MapViewNavigation.OnMouseUp(self, button)

    def GetMenu(self, *args):
        mouseInsideProbes = self.PickProbes()
        if mouseInsideProbes:
            return sm.StartService('scanSvc').GetProbeMenu(mouseInsideProbes[0].probeID)

    def GetDotInCameraAlignedPlaneFromPosition(self, targetPlanePos, offsetMouse = (0, 0), debug = False):
        targetPlaneNormal = self.mapView.camera.GetZAxis()
        return self.GetDotOnTargetPlaneFromPosition(targetPlanePos, targetPlaneNormal, offsetMouse)

    def GetDotInAxisAlignedPlaneFromPosition(self, targetPlanePos, offsetMouse = (0, 0)):
        if not self.activeTargetPlaneNormal:
            return None
        return self.GetDotOnTargetPlaneFromPosition(targetPlanePos, self.activeTargetPlaneNormal, offsetMouse)

    def GetDotOnTargetPlaneFromPosition(self, targetPlanePos, targetPlaneNormal, offsetMouse = (0, 0)):
        oX, oY = offsetMouse
        x, y = ScaleDpi(uicore.uilib.x + oX), ScaleDpi(uicore.uilib.y + oY)
        ray, start = self.mapView.camera.GetRayAndPointFromUI(x, y)
        pos = RayToPlaneIntersection(start, ray, targetPlanePos, targetPlaneNormal)
        return pos

    def GetRayToPlaneDenominator(self, targetPlaneNormal, offsetMouse = (0, 0)):
        oX, oY = offsetMouse
        x, y = ScaleDpi(uicore.uilib.x + oX), ScaleDpi(uicore.uilib.y + oY)
        ray, start = self.mapView.camera.GetRayAndPointFromUI(x, y)
        denom = geo2.Vec3Dot(targetPlaneNormal, ray)
        return denom

    def PickProbes(self, pickBorder = False):
        mouseInsideProbes = []
        borderPick = []
        probeHandler = self.GetProbeHandler()
        if probeHandler:
            probeData = sm.StartService('scanSvc').GetProbeData()
            cameraPosition = geo2.Vec3Add(self.mapView.camera.pointOfInterest, self.mapView.camera._eyePosition)
            probes = probeHandler.GetProbeControls()
            for probeID, probeControl in probes.iteritems():
                if probeID not in probeData or probeData[probeID].state != const.probeStateIdle:
                    continue
                targetPlanePos = probeControl.GetWorldPosition()
                cameraDistance = geo2.Vec3Length(geo2.Vec3Subtract(cameraPosition, targetPlanePos))
                rad = probeControl.GetRange() * SOLARSYSTEM_SCALE
                mousePositionOnCameraPlane = self.GetDotInCameraAlignedPlaneFromPosition(targetPlanePos)
                distanceFromCenter = geo2.Vec3Length(geo2.Vec3Subtract(targetPlanePos, mousePositionOnCameraPlane))
                if pickBorder:
                    pickRadiusPos = self.GetDotInCameraAlignedPlaneFromPosition(targetPlanePos, offsetMouse=(-10, 0))
                    pickRadius = geo2.Vec3Length(geo2.Vec3Subtract(pickRadiusPos, mousePositionOnCameraPlane))
                    if rad + pickRadius > distanceFromCenter > rad - pickRadius:
                        borderPick.append((abs(rad - distanceFromCenter), probeControl))
                elif distanceFromCenter <= rad:
                    mouseInsideProbes.append((cameraDistance, probeControl))

        if pickBorder:
            if borderPick:
                return SortListOfTuples(borderPick)[0]
            else:
                return None
        return SortListOfTuples(mouseInsideProbes)

    def GetPick(self):
        scene = self.mapView.scene
        camera = self.mapView.camera
        x, y = ScaleDpi(uicore.uilib.x), ScaleDpi(uicore.uilib.y)
        if scene:
            projection, view, viewport = camera.GetProjectionViewViewPort()
            pick = scene.PickObject(x, y, projection, view, viewport)
            if pick:
                return ('scene', pick)
        return (None, None)

    def GetProbeHandler(self):
        if self.mapView:
            solarSystemHander = self.mapView.currentSolarsystem
            if solarSystemHander and solarSystemHander.solarsystemID == session.solarsystemid2:
                return solarSystemHander.probeHandler

    def ScaleOrMoveActiveProbe(self, *args):
        probeHandler = self.GetProbeHandler()
        if not probeHandler:
            return
        if self.movingProbe:
            probeHandler.MoveProbe(self.movingProbe, self.activeManipAxis, self.GetDotInAxisAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInAxisAlignedPlaneFromPosition(self.initCenterScenePosition))
        elif self.rangeProbe:
            probeHandler.ScaleProbe(self.rangeProbe, self.GetDotInCameraAlignedPlaneFromPosition(self.initProbeScenePosition), self.GetDotInCameraAlignedPlaneFromPosition(self.initCenterScenePosition))

    def GetAxisTargetPlaneNormal(self):
        threshold = 0.15
        if self.activeManipAxis == 'z':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) >= threshold:
                return Y_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= threshold:
                return X_AXIS
            else:
                return Z_AXIS
        elif self.activeManipAxis == 'x':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) >= threshold:
                return Y_AXIS
            elif abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= threshold:
                return Z_AXIS
            else:
                return X_AXIS
        elif self.activeManipAxis == 'y':
            if abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= threshold:
                return Z_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= threshold:
                return X_AXIS
            else:
                return Y_AXIS
        elif self.activeManipAxis == 'xz':
            if abs(self.GetRayToPlaneDenominator(Y_AXIS)) >= threshold:
                return Y_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= threshold:
                return X_AXIS
            else:
                return Z_AXIS
        elif self.activeManipAxis == 'xy':
            if abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= threshold:
                return Z_AXIS
            elif abs(self.GetRayToPlaneDenominator(X_AXIS)) >= threshold:
                return X_AXIS
            else:
                return Y_AXIS
        elif self.activeManipAxis == 'yz':
            if abs(self.GetRayToPlaneDenominator(X_AXIS)) >= threshold:
                return X_AXIS
            elif abs(self.GetRayToPlaneDenominator(Z_AXIS)) >= threshold:
                return Z_AXIS
            else:
                return Y_AXIS
