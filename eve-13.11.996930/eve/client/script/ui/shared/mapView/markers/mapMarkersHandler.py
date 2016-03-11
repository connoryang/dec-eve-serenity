#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkersHandler.py
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from eve.client.script.ui.shared.mapView.markers.mapMarkerContellation import MarkerLabelConstellation
from eve.client.script.ui.shared.mapView.markers.mapMarkerLandmark import MarkerLabelLandmark
from eve.client.script.ui.shared.mapView.markers.mapMarkerRegion import MarkerLabelRegion
from eve.client.script.ui.shared.mapView.markers.mapMarkerSolarSystem import MarkerLabelSolarSystem
from eve.client.script.ui.shared.mapView.mapViewUtil import IsDynamicMarkerType
import geo2
import telemetry

@telemetry.ZONE_METHOD
def DoMarkersIntersect(marker1Bound, marker2Bound):
    l1, t1, r1, b1 = marker1Bound
    l2, t2, r2, b2 = marker2Bound
    overlapX = not (r1 <= l2 or l1 >= r2)
    if overlapX:
        overlapY = not (b1 <= t2 or t1 >= b2)
        if overlapY:
            return True
    return False


@telemetry.ZONE_METHOD
def FindOverlaps(markers):
    isOverlapped = set()
    isOverlapping = {}
    for _sortVal, (bound1, marker1) in markers:
        if marker1.markerID in isOverlapped:
            continue
        for _sortVal, (bound2, marker2) in markers:
            if marker1 is marker2:
                continue
            if marker2.markerID in isOverlapped:
                continue
            intersect = DoMarkersIntersect(bound1, bound2)
            if intersect:
                isOverlapping.setdefault(marker1.markerID, []).append(marker2)
                isOverlapped.add(marker2.markerID)

    return (isOverlapping, isOverlapped)


class MapViewMarkersHandler(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    projectBrackets = None
    markerCurveSet = None
    markerLayer = None
    mapView = None
    disabledMarkers = None
    eventHandler = None
    clickTimer = None
    cameraTranslationFromParent = 1.0

    def __init__(self, mapView, markerCurveSet, markerLayer, eventHandler = None, stackMarkers = True):
        self.mapView = mapView
        self.projectBrackets = {}
        self.hilightMarkers = set()
        self.activeMarkers = set()
        self.overlapMarkers = set()
        self.distanceSortedMarkers = set()
        self.markerCurveSet = markerCurveSet
        self.markerLayer = markerLayer
        self.eventHandler = eventHandler
        self.stackMarkers = stackMarkers
        self.updateTimer = AutoTimer(500, self.UpdateMarkers)

    def __del__(self):
        self.StopHandler()

    def SetScenePickState(self, scenePickActive):
        if scenePickActive:
            self.markerLayer.opacity = 0.5
            self.markerLayer.state = uiconst.UI_DISABLED
        else:
            self.markerLayer.opacity = 1.0
            self.markerLayer.state = uiconst.UI_PICKCHILDREN

    def IsMarkerPickOverridden(self):
        if self.eventHandler:
            return self.eventHandler.MapMarkerPickingOverride()
        return False

    def GetIntersectingMarkersForMarker(self, checkMarkerObject):
        intersectingMarkers = []
        for markerID, markerObject in self.projectBrackets.iteritems():
            if markerObject and markerObject.markerContainer and not markerObject.markerContainer.destroyed:
                intersect = DoMarkersIntersect(checkMarkerObject.GetBoundaries(), markerObject.GetBoundaries())
                if intersect:
                    intersectingMarkers.append(markerObject)

        return intersectingMarkers

    def UpdateMarkers(self):
        distance_markers = []
        stack_markers = []
        for markerID in self.distanceSortedMarkers:
            markerObject = self.projectBrackets.get(markerID, None)
            if markerObject and markerObject.markerContainer and not markerObject.markerContainer.destroyed:
                markerDistance = markerObject.GetCameraDistance()
                distance_markers.append((markerDistance, markerObject))
                markerBoundaries = markerObject.GetBoundaries()
                stack_markers.append(((markerObject.GetOverlapSortValue(), markerDistance), (markerBoundaries, markerObject)))

        distanceSortedMarkers = sorted(distance_markers, reverse=True)
        for markerDistance, markerObject in distanceSortedMarkers:
            markerObject.MoveToFront()

        if self.stackMarkers:
            markersSorted = sorted(stack_markers)
            isOverlapping, isOverlapped = FindOverlaps(markersSorted)
            for sortOrderValue, (bound, markerObject) in reversed(markersSorted):
                markerID = markerObject.markerID
                if markerID in isOverlapping:
                    markerObject.RegisterOverlapMarkers(isOverlapping[markerID])
                elif markerID in isOverlapped:
                    markerObject.SetOverlappedState(True)
                else:
                    markerObject.SetOverlappedState(False)

        for marker in self.GetActiveAndHilightedMarkers():
            marker.MoveToFront()

    def GetExtraMouseOverInfoForMarker(self, markerID):
        if self.mapView:
            return self.mapView.GetExtraMouseOverInfoForItemID(markerID)

    def ReloadAll(self):
        for markerID, markerObject in self.projectBrackets.iteritems():
            if markerObject:
                markerObject.Reload()

    def SetDisplayStateOverrideFilter(self, markersToShow):
        filtering = bool(markersToShow)
        for markerID, markerObject in self.projectBrackets.iteritems():
            if IsDynamicMarkerType(markerObject.markerID):
                continue
            if not filtering or markerID in markersToShow:
                markerObject.displayStateOverride = None
            else:
                markerObject.displayStateOverride = False

    def UpdateMarkerPositions(self, changedSolarSystemPositions, yScaleFactor):
        for markerID, markerObject in self.projectBrackets.iteritems():
            if hasattr(markerObject, 'UpdateSolarSystemPosition') and markerObject.solarSystemID in changedSolarSystemPositions:
                mapNode = changedSolarSystemPositions[markerObject.solarSystemID]
                markerObject.UpdateSolarSystemPosition(mapNode.position)
            elif hasattr(markerObject, 'SetYScaleFactor'):
                markerObject.SetYScaleFactor(yScaleFactor)

    def StopHandler(self):
        self.updateTimer = None
        if self.projectBrackets:
            for markerID, markerObject in self.projectBrackets.iteritems():
                markerObject.Close()

        self.projectBrackets = None
        self.mapView = None
        self.markerLayer = None
        self.markerCurveSet = None
        self.eventHandler = None

    def OnMarkerHilighted(self, marker):
        self.mapView.SetHilightItem(marker.markerID)

    def OnMarkerSelected(self, marker, zoomTo = False):
        self.mapView.SetActiveMarker(marker, zoomToItem=zoomTo)

    def HilightMarkers(self, markerIDs):
        hilightMarkers = markerIDs
        for oldMarkerID in self.hilightMarkers:
            if oldMarkerID not in hilightMarkers:
                oldMarker = self.GetMarkerByID(oldMarkerID)
                if oldMarker:
                    oldMarker.SetHilightState(False)

        for newMarkerID in hilightMarkers:
            newMarker = self.GetMarkerByID(newMarkerID)
            if newMarker:
                newMarker.SetHilightState(True)

        self.hilightMarkers = set(hilightMarkers)

    def ActivateMarkers(self, markerIDs):
        activeMarkers = markerIDs
        for oldMarkerID in self.activeMarkers:
            if oldMarkerID not in activeMarkers:
                oldMarker = self.GetMarkerByID(oldMarkerID)
                if oldMarker:
                    oldMarker.SetActiveState(False)

        for newMarkerID in activeMarkers:
            newMarker = self.GetMarkerByID(newMarkerID)
            if newMarker:
                newMarker.SetActiveState(True)

        self.activeMarkers = set(activeMarkers)

    def RefreshActiveAndHilightedMarkers(self):
        for marker in self.GetActiveAndHilightedMarkers():
            marker.UpdateActiveAndHilightState()

    def GetActiveAndHilightedMarkers(self):
        ret = set()
        for markerID in self.hilightMarkers.union(self.activeMarkers):
            marker = self.GetMarkerByID(markerID)
            if marker:
                ret.add(marker)

        return ret

    def IsActiveOfHilighted(self, markerID):
        return markerID in self.activeMarkers or markerID in self.hilightMarkers

    def RemoveMarker(self, markerID, fadeOut = False):
        try:
            self.overlapMarkers.remove(markerID)
        except:
            pass

        try:
            self.distanceSortedMarkers.remove(markerID)
        except:
            pass

        markerObject = self.projectBrackets.pop(markerID, None)
        if markerObject:
            if fadeOut:
                markerObject.FadeOutAndClose()
            else:
                markerObject.Close()

    def GetMarkerByID(self, markerID):
        return self.projectBrackets.get(markerID, None)

    def GetMarkersByType(self, markerType):
        return [ markerObject for markerID, markerObject in self.projectBrackets.iteritems() if isinstance(markerID, tuple) and markerID[0] == markerType ]

    def _AddPositionMarker(self, **kwds):
        markerID = kwds.get('markerID', None)
        if markerID in self.projectBrackets:
            return self.projectBrackets[markerID]
        kwds['parentContainer'] = self.markerLayer
        kwds['curveSet'] = self.markerCurveSet
        kwds['markerHandler'] = self
        kwds['eventHandler'] = self.eventHandler
        markerClass = kwds.get('markerClass', None)
        markerObject = markerClass(**kwds)
        self.projectBrackets[markerID] = markerObject
        return markerObject

    def RegisterMarker(self, markerObject):
        self.projectBrackets[markerObject.markerID] = markerObject

    def AddSolarSystemMarker(self, markerID, position):
        return self.AddSolarSystemBasedMarker(markerID=markerID, solarSystemID=markerID, mapPositionSolarSystem=position, mapPositionLocal=(0, 0, 0), markerClass=MarkerLabelSolarSystem)

    def AddConstellationMarker(self, markerID, position):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelConstellation)

    def AddRegionMarker(self, markerID, position):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelRegion)

    def AddLandmarkMarker(self, markerID, position, **kwds):
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=MarkerLabelLandmark, **kwds)

    def AddSolarSystemBasedMarker(self, markerID, markerClass, **kwds):
        if getattr(markerClass, 'distanceSortEnabled', False):
            self.distanceSortedMarkers.add(markerID)
            if getattr(markerClass, 'overlapEnabled', False):
                self.overlapMarkers.add(markerID)
        position = geo2.Vec3Add(kwds['mapPositionSolarSystem'], kwds['mapPositionLocal'])
        return self._AddPositionMarker(markerID=markerID, position=position, markerClass=markerClass, **kwds)

    def RegisterCameraTranslationFromParent(self, cameraTranslationFromParent):
        self.cameraTranslationFromParent = cameraTranslationFromParent
