#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewNavigation.py
from carbon.common.script.util.mathUtil import RayToPlaneIntersection
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
import carbonui.const as uiconst
import geo2
import trinity

class MapViewNavigation(Container):
    default_cursor = uiconst.UICURSOR_POINTER
    lastPickInfo = None
    isTabStop = True
    pickInfo = None
    pickPosition = None
    cameraUpdateTimer = None
    doLeftMouseUp = False
    doRightMouseUp = False
    rightMouseDownPosition = None

    def Close(self, *args):
        Container.Close(self, *args)
        self.mapView = None
        self.pickTimer = None
        self.cameraUpdateTimer = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapView = attributes.mapView
        self.pickTimer = AutoTimer(20, self.CheckPick)

    def UpdateCamera(self, *args):
        if self.destroyed:
            self.cameraUpdateTimer = None
            return
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self.cameraUpdateTimer = None
            return
        if uicore.registry.GetFocus() is not self:
            self.cameraUpdateTimer = None
            return
        camera = self.mapView.camera
        mouseX, mouseY = trinity.GetCursorPos()
        if uicore.uilib.leftbtn:
            if (mouseX, mouseY) != self.leftMouseDownPosition or self.doLeftMouseUp is False:
                self.doLeftMouseUp = False
                oldX, oldY = self.leftMouseDownPosition
                dx = mouseX - oldX
                dy = mouseY - oldY
                self.leftMouseDownPosition = (mouseX, mouseY)
                if uicore.uilib.rightbtn:
                    self.doRightMouseUp = False
                    modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
                    camera.ZoomMouseDelta(dx, modifier * dy)
                else:
                    camera.OrbitMouseDelta(dx, dy)
        elif uicore.uilib.rightbtn:
            if (mouseX, mouseY) != self.rightMouseDownPosition or self.doRightMouseUp is False:
                self.doRightMouseUp = False
                initRayToPlaneIntersection, initPointOfInterest, initTargetPlaneNormal, projection2view, view2world = self.rightButtonCameraData
                x, y = ScaleDpi(uicore.uilib.x), ScaleDpi(uicore.uilib.y)
                ray, start = self.mapView.camera.GetRayAndPointFromUI(x, y, projection2view, view2world)
                rayToPlaneIntersection = RayToPlaneIntersection(start, ray, initPointOfInterest, initTargetPlaneNormal)
                rayToPlaneIntersectionDiff = geo2.Vec3Subtract(initRayToPlaneIntersection, rayToPlaneIntersection)
                newPointOfInterest = geo2.Vec3Add(initPointOfInterest, rayToPlaneIntersectionDiff)
                camera.SetPointOfInterest(newPointOfInterest)
                self.mapView.DisableAutoFocus()

    def CheckPick(self):
        if uicore.uilib.mouseOver is not self or uicore.uilib.leftbtn or uicore.uilib.rightbtn:
            return
        mx, my = uicore.uilib.x, uicore.uilib.y
        if self.pickPosition:
            dX = abs(mx - self.pickPosition[0])
            dY = abs(my - self.pickPosition[1])
            picked = self.pickPosition[-1]
            if dX == 0 and dY == 0:
                if not picked:
                    self.PickScene(mx, my)
                    self.pickPosition = (mx, my, True)
                return
        self.pickPosition = (mx, my, False)

    def PickScene(self, mouseX, mouseY):
        pickInfo = self.mapView.GetPickObjects(mouseX, mouseY, getMarkers=False)
        if pickInfo:
            self.mapView.SetHilightItem(pickInfo[0])
        else:
            self.mapView.SetHilightItem(None)

    def MapMarkerPickingOverride(self, *args, **kwds):
        return False

    def PickRegionID(self):
        return None

    def OnDblClick(self, *args):
        if self.destroyed:
            return
        self.ClickPickedObject(True, uicore.uilib.x, uicore.uilib.y)

    def OnClick(self, *args):
        if not self.doLeftMouseUp:
            return
        self.clickTimer = AutoTimer(250, self.ClickPickedObject, uicore.uilib.Key(uiconst.VK_CONTROL), uicore.uilib.x, uicore.uilib.y)

    def ClickPickedObject(self, zoomTo, mouseX, mouseY):
        self.clickTimer = None
        if self.destroyed:
            return
        pickInfo = self.mapView.GetPickObjects(mouseX, mouseY, getMarkers=True)
        if pickInfo:
            self.mapView.SetActiveMarker(pickInfo[0][1], zoomToItem=zoomTo)

    def _PrimeForCameraPanning(self):
        projection2view = geo2.MatrixInverse(self.mapView.camera.projectionMatrix.transform)
        view2world = geo2.MatrixInverse(self.mapView.camera.viewMatrix.transform)
        x, y = ScaleDpi(uicore.uilib.x), ScaleDpi(uicore.uilib.y)
        ray, start = self.mapView.camera.GetRayAndPointFromUI(x, y, projection2view, view2world)
        targetPlaneNormal = self.mapView.camera.GetViewVector()
        initPointOfInterest = self.mapView.camera._pointOfInterestCurrent
        initRayToPlaneIntersection = RayToPlaneIntersection(start, ray, initPointOfInterest, targetPlaneNormal)
        return (initRayToPlaneIntersection,
         initPointOfInterest,
         targetPlaneNormal,
         projection2view,
         view2world)

    def OnMouseDown(self, button):
        mousePos = trinity.GetCursorPos()
        if button == uiconst.MOUSERIGHT:
            self.doRightMouseUp = True
            self.rightMouseDownPosition = mousePos
            self.rightButtonCameraData = self._PrimeForCameraPanning()
        elif button == uiconst.MOUSELEFT:
            self.doLeftMouseUp = True
            self.leftMouseDownPosition = mousePos
            self.leftButtonCameraData = self._PrimeForCameraPanning()
            self.mapView.camera.SetCapture(self)
        updateCamera = button in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT)
        if updateCamera and not self.cameraUpdateTimer:
            self.cameraUpdateTimer = AutoTimer(1, self.UpdateCamera)

    def OnMouseUp(self, button):
        if button == uiconst.MOUSELEFT and uicore.uilib.rightbtn:
            self.rightButtonCameraData = self._PrimeForCameraPanning()
        if button == uiconst.MOUSERIGHT and uicore.uilib.leftbtn:
            self.leftButtonCameraData = self._PrimeForCameraPanning()
        if not (uicore.uilib.leftbtn or uicore.uilib.rightbtn):
            self.mapView.camera.ReleaseCapture(self)

    def OnMouseWheel(self, *args):
        camera = self.mapView.camera
        if camera:
            modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
            camera.ZoomMouseWheelDelta(modifier * uicore.uilib.dz)
        return 1

    def OnMouseMove(self, *args):
        pass

    def GetMenuForObjectID(self, objectID):
        return self.mapView.GetItemMenu(objectID)

    def GetMenu(self):
        if not self.doRightMouseUp:
            return
        pickInfo = self.mapView.GetPickObjects(uicore.uilib.x, uicore.uilib.y)
        if pickInfo and len(pickInfo) == 1:
            return self.GetMenuForObjectID(pickInfo[0][0])
        locations = [(MenuLabel('UI/Map/Navigation/menuSolarSystem'), self.mapView.SetActiveItemID, (session.solarsystemid2,)), (MenuLabel('UI/Map/Navigation/menuConstellation'), self.mapView.SetActiveItemID, (session.constellationid,)), (MenuLabel('UI/Map/Navigation/menuRegion'), self.mapView.SetActiveItemID, (session.regionid,))]
        m = [(MenuLabel('UI/Map/Navigation/menuSelectCurrent'), locations)]
        mapSvc = sm.GetService('map')
        waypoints = sm.StartService('starmap').GetWaypoints()
        if len(waypoints):
            waypointList = []
            wpCount = 1
            for waypointID in waypoints:
                waypointItem = mapSvc.GetItem(waypointID)
                caption = MenuLabel('UI/Map/Navigation/menuWaypointEntry', {'itemName': waypointItem.itemName,
                 'wpCount': wpCount})
                waypointList += [(caption, self.mapView.SetActiveItemID, (waypointID,))]
                wpCount += 1

            m.append((MenuLabel('UI/Map/Navigation/menuSelectWaypoint'), waypointList))
            m.append(None)
            m.append((MenuLabel('UI/Map/Navigation/menuClearWaypoints'), sm.StartService('starmap').ClearWaypoints, (None,)))
        return m
