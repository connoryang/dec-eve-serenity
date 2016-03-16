#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewProbeHandlerStandalone.py
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.inflight.probeControl_MapView import BaseProbeControl, ProbeControl, BASE_PROBE_COLOR
from eve.client.script.ui.inflight.scanner import FORMATION_CONTROL_ID
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.mapViewConst import SOLARSYSTEM_SCALE, MARKERID_SCANRESULT, MARKERID_PROBE
from eve.client.script.ui.shared.mapView.markers.mapMarkerScanResult import MarkerScanResult
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos, MapPosToSolarSystemPos
from probescanning.util import IsIntersecting
import uthread
from probescanning.const import probeStateIdle, probeStateInactive
import carbonui.const as uiconst
import itertools
import trinity
import blue
import math
import geo2
DISTANCE_RING_RANGES = [1,
 2,
 4,
 8,
 16,
 32,
 64,
 128]
MAX_DIST_RING_RANGE = DISTANCE_RING_RANGES[-1]
r, g, b, a = BASE_PROBE_COLOR
CENTROID_LINE_COLOR = (r * 0.3,
 g * 0.3,
 b * 0.3,
 1.0)
CENTROID_LINE_WIDTH = 2.5
WARP_LINE_COLOR = (r * 0.3,
 g * 0.3,
 b * 0.3,
 1.0)
WARP_LINE_WIDTH = 2.0
CIRCLE_COLOR = (1.0,
 0.0,
 0.0,
 1.0)
INTERSECTION_ACTIVE = 0.6
INTERSECTION_INACTIVE = 0.05
AXIS_Y = geo2.Vector(0.0, 1.0, 0.0)
AXIS_Z = geo2.Vector(0.0, 0.0, 1.0)
MODIFY_POSITION = 1
MODIFY_RANGE = 2
MODIFY_SPREAD = 3

class MapViewProbeHandlerStandalone(object):
    __notifyevents__ = ['OnProbeScanner_ProbeEntryMouseEnter',
     'OnProbeScanner_ProbeEntryMouseExit',
     'OnProbeScanner_FocusOnProbe',
     'OnProbeScanner_FocusOnResult',
     'OnProbeScanner_ScanResultMouseEnter',
     'OnProbeScanner_ScanResultMouseExit',
     'OnProbeAdded',
     'OnProbeRemoved',
     'OnProbeWarpStart',
     'OnProbeWarpEnd',
     'OnProbeStateUpdated',
     'OnProbeRangeUpdated',
     'OnProbePositionsUpdated',
     'OnSystemScanBegun',
     'OnSystemScanDone',
     'OnSystemScanFilterChanged',
     'OnScannerDisconnected',
     'OnRefreshScanResults']
    _keyState = None
    _editMode = MODIFY_POSITION
    _activeEditMode = None
    _filterResults = None
    highlightCursorData = None

    def __init__(self, systemMapHandler):
        self.systemMapHandler = systemMapHandler
        self.Cleanup()
        parentTransform = trinity.EveTransform()
        parentTransform.name = 'probes_%d' % systemMapHandler.solarsystemID
        self.parentTransform = parentTransform
        systemMapHandler.systemMapTransform.children.append(self.parentTransform)
        self.scanSvc = sm.GetService('scanSvc')
        sm.RegisterNotify(self)
        self.keyDownCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYDOWN, self.OnGlobalKeyCallback)
        self.keyUpCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_KEYUP, self.OnGlobalKeyCallback)
        self.updateTick = AutoTimer(500, self.UpdateInputState)
        self.UpdateProbeSpheres()
        self.UpdateScanResult()

    def StopHandler(self):
        uicore.event.UnregisterForTriuiEvents(self.keyDownCookie)
        uicore.event.UnregisterForTriuiEvents(self.keyUpCookie)
        self.updateTick = None
        sm.UnregisterNotify(self)
        self.Cleanup()
        self.systemMapHandler.systemMapTransform.children.remove(self.parentTransform)
        self.systemMapHandler = None

    def Cleanup(self):
        if getattr(self, 'parentTransform', None):
            for each in self.parentTransform.children[:]:
                self.parentTransform.children.remove(each)

        resultMarkers = self.systemMapHandler.markersHandler.GetMarkersByType(MARKERID_SCANRESULT)
        for markerObject in resultMarkers:
            self.systemMapHandler.markersHandler.RemoveMarker(markerObject.markerID)

        self.centerProbeControl = None
        self.probeIntersectionsByPair = {}
        self.centroidLines = None
        self.lastProbeIDs = None
        self.probeControlsByID = {}
        self.resultObjectsByID = {}
        self.resultMarkers = set()

    def UpdateInputState(self):
        self.CheckKeyState()

    def OnGlobalKeyCallback(self, wnd, eventID, (vkey, flag)):
        if vkey not in (uiconst.VK_CONTROL, uiconst.VK_MENU, uiconst.VK_SHIFT):
            return True
        if eventID == uiconst.UI_KEYDOWN and flag & 1073741824:
            return True
        try:
            self.CheckKeyState()
        finally:
            return True

    def CheckKeyState(self):
        CTRL = uicore.uilib.Key(uiconst.VK_CONTROL)
        ALT = uicore.uilib.Key(uiconst.VK_MENU)
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        if CTRL:
            self._editMode = MODIFY_SPREAD
        elif ALT:
            self._editMode = MODIFY_RANGE
        else:
            self._editMode = MODIFY_POSITION
        keyState = (CTRL, ALT, SHIFT)
        if self._keyState != keyState:
            self._keyState = keyState
            self.UpdateProbeControlDisplay()

    def GetEditMode(self):
        return self._editMode

    def GetActiveEditMode(self):
        return self._activeEditMode

    def OnProbeWarpStart(self, probeID, fromPos, toPos, startTime, duration):
        uthread.worker('MapViewProbeHandler::OnProbeWarpStart_Thread', self.OnProbeWarpStart_Thread, probeID, fromPos, toPos, startTime, duration)

    def OnProbeWarpStart_Thread(self, probeID, fromPos, toPos, startTime, duration):
        if not hasattr(self, 'probeRoutes'):
            self.probeRoutes = {}
        data = self.probeTracker.GetProbeData()
        if probeID not in data:
            return
        probe = data[probeID]
        lineSet = mapViewUtil.CreateLineSet()
        lineSet.name = 'probeRoute_' + str(probeID)
        lineID = lineSet.AddStraightLine(probe.pos, WARP_LINE_COLOR, probe.destination, WARP_LINE_COLOR, WARP_LINE_WIDTH)
        lineSet.ChangeLineAnimation(lineID, WARP_LINE_COLOR, -0.125, 20.0)
        lineSet.SubmitChanges()
        self.parentTransform.children.append(lineSet)
        self.probeRoutes[probeID] = lineSet

    def OnProbeWarpEnd(self, probeID):
        uthread.worker('MapViewProbeHandler::OnProbeWarpEnd_Thread', self.OnProbeWarpEnd_Thread, probeID)

    def OnProbeWarpEnd_Thread(self, probeID):
        if hasattr(self, 'probeRoutes') and probeID in self.probeRoutes:
            routeLineSet = self.probeRoutes[probeID]
            if routeLineSet in self.parentTransform.children:
                self.parentTransform.children.remove(routeLineSet)
            del self.probeRoutes[probeID]
            scanSvc = sm.GetService('scanSvc')
            probes = scanSvc.GetProbeData()
            if probes and probeID in probes:
                probe = probes[probeID]
                markerID = (MARKERID_PROBE, probeID)
                markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
                if markerObject:
                    markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(probe.destination))

    def OnProbeAdded(self, probe):
        uthread.new(self._OnProbeAdded, probe)

    def _OnProbeAdded(self, probe):
        self.UpdateProbeSpheres()

    def OnProbeRemoved(self, probeID):
        uthread.new(self._OnProbeRemove, probeID)

    def _OnProbeRemove(self, probeID):
        self.UpdateProbeSpheres()

    def OnSystemScanBegun(self):
        self.SetScanDronesState(1)

    def OnSystemScanDone(self):
        self.SetScanDronesState(0)
        self.SetResultFilter([])
        self.UpdateScanResult()

    def OnSystemScanFilterChanged(self, *args):
        self.UpdateScanResult()

    def OnProbeStateUpdated(self, probeID, state):
        self.updateProbeSpheresTimer = AutoTimer(200, self.UpdateProbeSpheres)

    def OnProbeRangeUpdated(self, probeID, scanRange):
        probe = self.GetProbeControl(probeID)
        if probe:
            probe.SetRange(scanRange)

    def OnScannerDisconnected(self):
        self.UpdateProbeSpheres()
        self.UpdateScanResult()

    def OnRefreshScanResults(self):
        self.UpdateProbeSpheres()
        self.UpdateScanResult()

    def OnProbePositionsUpdated(self):
        self.UpdateProbeSpheres()

    def OnProbeScanner_ProbeEntryMouseEnter(self, probeID):
        probeControl = self.GetProbeControl(probeID)
        if probeControl:
            probeControl.HighlightProbe()

    def OnProbeScanner_ProbeEntryMouseExit(self, probeID):
        probeControl = self.GetProbeControl(probeID)
        if probeControl:
            probeControl.StopHighlightProbe()

    def OnProbeScanner_ScanResultMouseEnter(self, result):
        if isinstance(result.data, float):
            markerIDs = [(MARKERID_SCANRESULT, result.id)]
        elif isinstance(result.data, (tuple, list)):
            if isinstance(result.data, list):
                positions = result.data
            else:
                positions = [result.data]
            markerIDs = [ (MARKERID_SCANRESULT, (result.id, i)) for i, position in enumerate(positions) ]
        else:
            markerIDs = [(MARKERID_SCANRESULT, result.id)]
        self.systemMapHandler.markersHandler.HilightMarkers(markerIDs)
        resultMarkers = self.systemMapHandler.markersHandler.GetMarkersByType(MARKERID_SCANRESULT)
        for markerObject in resultMarkers:
            markerObject.UpdateActiveAndHilightState()

    def OnProbeScanner_ScanResultMouseExit(self, result):
        self.systemMapHandler.markersHandler.HilightMarkers([])
        resultMarkers = self.systemMapHandler.markersHandler.GetMarkersByType(MARKERID_SCANRESULT)
        for markerObject in resultMarkers:
            markerObject.UpdateActiveAndHilightState()

    def OnProbeScanner_FocusOnProbe(self, probeID, *args):
        self.FocusOnProbe(probeID)

    def OnProbeScanner_FocusOnResult(self, result, *args):
        if isinstance(result.data, float):
            self.systemMapHandler.markersHandler.mapView.SetCameraPointOfInterestSolarSystemPosition(self.systemMapHandler.solarsystemID, result.pos)
        elif isinstance(result.data, (tuple, list)):
            if isinstance(result.data, list):
                positions = result.data
            else:
                positions = [result.data]
            centerPosition = self.GetCenterPosition(positions)
            self.systemMapHandler.markersHandler.mapView.SetCameraPointOfInterestSolarSystemPosition(self.systemMapHandler.solarsystemID, centerPosition)
        else:
            self.systemMapHandler.markersHandler.mapView.SetCameraPointOfInterestSolarSystemPosition(self.systemMapHandler.solarsystemID, result.data.point)

    def UpdateProbeControlDisplay(self):
        editMode = self.GetActiveEditMode() or self.GetEditMode()
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        probesAvailable = self.HasAvailableProbes()
        if self.centerProbeControl:
            self.centerProbeControl.cursor.display = editMode == MODIFY_POSITION and not SHIFT and probesAvailable
        for probeID, probeControl in self.probeControlsByID.iteritems():
            if self.probeTracker.GetProbeState(probeID) != probeStateIdle:
                continue
            probeControl.spreadCursor.display = editMode == MODIFY_SPREAD
            probeControl.cursor.display = editMode == MODIFY_POSITION and SHIFT
            probeControl.rangeCursor.display = editMode == MODIFY_RANGE
            if editMode in (MODIFY_SPREAD, MODIFY_RANGE):
                self.ShowCentroidLines()
            else:
                self.RemoveCentroidLines()

        if self.highlightCursorData:
            self.HighlightCursors(*self.highlightCursorData)

    def HasAvailableProbes(self):
        return self.probeTracker.HasAvailableProbes()

    def SetScanDronesState(self, value):
        for probe in self.probeControlsByID.values():
            probe.SetScanDronesState(value)

    def SetResultFilter(self, showResults, update = False):
        self._filterResults = showResults
        if update:
            self.UpdateScanResult()

    def UpdateScanResult(self):
        if not self.systemMapHandler or self.systemMapHandler.solarsystemID != session.solarsystemid2:
            return
        if not self.systemMapHandler.markersHandler:
            return
        previousMarkerIDs = self.resultMarkers.copy()
        self.resultMarkers = set()
        previousSpheresAndCircles = self.resultObjectsByID.copy()
        self.resultObjectsByID = {}
        results, ignored, filtered, filteredAnomalies = self.scanSvc.GetResults(useFilterSet=True)
        for result in results:
            if self._filterResults and result.id not in self._filterResults:
                continue
            if result.id in previousSpheresAndCircles:
                for obj in previousSpheresAndCircles[result.id]:
                    self.parentTransform.children.remove(obj)

                del previousSpheresAndCircles[result.id]
            if isinstance(result.data, float):
                self.CreateSphereResult(result)
            elif isinstance(result.data, (tuple, list)):
                self.CreatePointResult(result)
            else:
                self.CreateCircleResult(result)

        oldMarkerIDs = previousMarkerIDs.difference(self.resultMarkers)
        for each in oldMarkerIDs:
            self.systemMapHandler.markersHandler.RemoveMarker(each)

        previousSpheresAndCirclesIDs = set(previousSpheresAndCircles.keys())
        spheresAndCirclesIDs = set(self.resultObjectsByID.keys())
        oldSpheresAndCirclesIDs = previousSpheresAndCirclesIDs.difference(spheresAndCirclesIDs)
        for oldResultID in oldSpheresAndCirclesIDs:
            for obj in previousSpheresAndCircles[oldResultID]:
                self.parentTransform.children.remove(obj)

    def UpdateProbeSpheres(self):
        uthread.Lock('MapViewProbeHandler::UpdateProbeSpheres')
        try:
            bp = sm.GetService('michelle').GetBallpark()
            if not bp or eve.session.shipid not in bp.balls:
                self.Cleanup()
                return
            probeData = self.probeTracker.GetProbeData()
            probeIDs = self.probeControlsByID.keys()[:]
            for probeID in probeIDs:
                if probeID not in probeData or probeData[probeID].state == probeStateInactive:
                    probeControl = self.probeControlsByID[probeID]
                    if probeControl.locator in self.parentTransform.children:
                        self.parentTransform.children.remove(probeControl.locator)
                    del self.probeControlsByID[probeID]

            if probeData and self.centerProbeControl is None:
                self.centerProbeControl = BaseProbeControl(FORMATION_CONTROL_ID, self.parentTransform)
            for probeID, probe in probeData.items():
                if probe.state == probeStateInactive:
                    continue
                if probeID not in self.probeControlsByID:
                    probeControl = ProbeControl(probeID, probe, self.parentTransform)
                    self.probeControlsByID[probeID] = probeControl
                else:
                    probeControl = self.probeControlsByID[probeID]
                probeControl.SetRange(probe.scanRange)
                probeControl.SetPosition(probe.destination)

            self.HighlightProbeIntersections()
            self.HighlightMarkersInProbeRange()
            self.UpdateProbeControlDisplay()
        finally:
            uthread.UnLock('MapViewProbeHandler::UpdateProbeSpheres')
            self.updateProbeSpheresTimer = None

        centerPosition = self.probeTracker.GetCenterOfActiveProbes()
        for probeID, probeControl in self.probeControlsByID.iteritems():
            probeControl.SetFormationCenter(centerPosition)

        if self.centerProbeControl:
            self.centerProbeControl.SetPosition(self.probeTracker.GetCenterOfActiveProbes())
        if self.systemMapHandler:
            self.systemMapHandler.LoadProbeMarkers()

    def HighlightCursors(self, activeProbeControl = None, axis = None):
        SHIFT = uicore.uilib.Key(uiconst.VK_SHIFT)
        self.highlightCursorData = (activeProbeControl, axis)
        if self.centerProbeControl:
            if self.centerProbeControl is activeProbeControl or not SHIFT and axis:
                self.centerProbeControl.SetCursorState(self.centerProbeControl.STATE_ACTIVE, axis)
            else:
                self.centerProbeControl.SetCursorState(self.centerProbeControl.STATE_IDLE, axis)
        for probeID, probeControl in self.probeControlsByID.iteritems():
            if self.probeTracker.GetProbeState(probeID) != probeStateIdle:
                continue
            if activeProbeControl is None:
                probeControl.SetCursorState(probeControl.STATE_IDLE, axis)
            elif probeControl is activeProbeControl or not SHIFT:
                probeControl.SetCursorState(probeControl.STATE_ACTIVE, axis)
            else:
                probeControl.SetCursorState(probeControl.STATE_IDLE, axis)

    def HighlightProbeIntersections(self, showAll = False):
        probeIDs = self.probeTracker.GetActiveProbes()
        probeIDs.sort()
        possiblePairs = [ pair for pair in itertools.combinations(probeIDs, 2) ]
        activePairs = []
        for pair in possiblePairs:
            id1, id2 = pair
            probe1 = self.GetProbeControl(id1)
            probe2 = self.GetProbeControl(id2)
            if not probe1 or not probe2:
                self.RemoveIntersection(pair)
                continue
            pos1 = probe1.GetPosition()
            radius1 = probe1.GetRange()
            pos2 = probe2.GetPosition()
            radius2 = probe2.GetRange()
            if (showAll or not self.probeTracker.IsInFormation()) and IsIntersecting(pos1, radius1, pos2, radius2):
                if pair not in self.probeIntersectionsByPair:
                    intersection = ProbesIntersection(pair)
                    self.parentTransform.children.append(intersection.transform)
                    self.probeIntersectionsByPair[pair] = intersection
                changed = self.SetIntersectionHighlight(pair, (pos1,
                 pos2,
                 radius1,
                 radius2))
                if changed:
                    activePairs.append(pair)
            else:
                self.RemoveIntersection(pair)

        for pair in self.probeIntersectionsByPair.keys():
            if pair not in possiblePairs:
                self.RemoveIntersection(pair)

        if not getattr(self, 'fadeActiveIntersectionsTimers', {}):
            self.fadeActiveIntersectionsTimers = {}
        for each in activePairs:
            intersection = self.probeIntersectionsByPair.get(each)
            if intersection:
                uicore.animations.MorphScalar(intersection, 'opacity', startVal=intersection.opacity, endVal=INTERSECTION_ACTIVE, duration=0.1)
                self.fadeActiveIntersectionsTimers[each] = AutoTimer(500, self.FadeOutIntersection, each)

    def ComputeHighlightCircle(self, distance, pos1, pos2, rad1, rad2):
        if not distance:
            return None
        rad1_sq = rad1 ** 2
        rad2_sq = rad2 ** 2
        dist_sq = distance ** 2
        distToPoint = (rad1_sq - rad2_sq + dist_sq) / (2 * distance)
        radius_sq = rad1_sq - distToPoint ** 2
        if radius_sq < 0.0:
            return None
        radius = math.sqrt(radius_sq)
        normal = geo2.Vec3Normalize(pos2 - pos1)
        normal = geo2.Vector(*normal)
        point = pos1 + normal * distToPoint
        rotation = geo2.QuaternionRotationArc(AXIS_Z, normal)
        return (point, rotation, radius)

    def SetIntersectionHighlight(self, pair, config):
        intersection = self.probeIntersectionsByPair[pair]
        if repr(config) != repr(intersection.lastConfig):
            intersection.lastConfig = config
            intersection.opacity = INTERSECTION_ACTIVE
            pos1, pos2, radius1, radius2 = config
            newDistance = geo2.Vec3Length(geo2.Vec3Subtract(pos1, pos2))
            self.UpdateIntersection(pair, newDistance)
            return True
        return False

    def RemoveIntersection(self, pair):
        if pair in self.probeIntersectionsByPair:
            intersection = self.probeIntersectionsByPair[pair]
            if intersection.transform in self.parentTransform.children:
                self.parentTransform.children.remove(intersection.transform)
            del self.probeIntersectionsByPair[pair]
        try:
            del self.fadeActiveIntersectionsTimers[pair]
        except:
            pass

    def UpdateIntersection(self, pair, distance):
        intersection = self.probeIntersectionsByPair[pair]
        data = self.ComputeHighlightCircle(distance, *intersection.lastConfig)
        if data:
            point, rotation, radius = data
            tr = intersection.transform
            tr.translation = point
            tr.rotation = rotation
            tr.scaling = (radius * 2.0, radius * 2.0, radius * 2.0)
            changed = True
        else:
            self.RemoveIntersection(pair)
            changed = False
        return changed

    def FadeOutIntersection(self, pairID):
        del self.fadeActiveIntersectionsTimers[pairID]
        intersection = self.probeIntersectionsByPair.get(pairID, None)
        if not intersection:
            return
        uicore.animations.MorphScalar(intersection, 'opacity', startVal=intersection.opacity, endVal=INTERSECTION_INACTIVE, duration=1.5)

    def ShowCentroidLines(self):
        if self.centroidLines is None:
            self.centroidLines = mapViewUtil.CreateLineSet()
            self.centroidLines.name = 'centroidLines'
            self.parentTransform.children.append(self.centroidLines)
        self.centroidLines.display = True
        probes = self.probeTracker.GetProbeData()
        probeIDs = [ probeID for probeID, probe in probes.iteritems() if probe.state == probeStateIdle ]
        if probeIDs:
            probeIDs.sort()
            update = self.lastProbeIDs == probeIDs
            if not update:
                self.lastProbeIDs = probeIDs
                self.centroidLines.ClearLines()
            centroid = geo2.Vector(0, 0, 0)
            probePositions = []
            scanRanges = []
            for probeID in probeIDs:
                probeControl = self.GetProbeControl(probeID)
                if probeControl:
                    p = probeControl.GetPosition()
                    centroid += p
                    probePositions.append((p.x, p.y, p.z))
                    scanRanges.append(probeControl.GetRange())

            editMode = self.GetActiveEditMode() or self.GetEditMode()
            centroid /= len(probeIDs)
            c = (centroid.x, centroid.y, centroid.z)
            for index, position in enumerate(probePositions):
                startPosition = c
                if editMode == MODIFY_RANGE:
                    v = geo2.Vec3Subtract(position, c)
                    l = geo2.Vec3Length(v)
                    vN = geo2.Vec3Normalize(v)
                    if uicore.uilib.Key(uiconst.VK_SHIFT):
                        startPosition = position
                    position = geo2.Vec3Add(c, geo2.Vec3Scale(vN, l + scanRanges[index]))
                if update:
                    self.centroidLines.ChangeLinePositionCrt(index, startPosition, position)
                    self.centroidLines.ChangeLineAnimation(index, CENTROID_LINE_COLOR, -0.25, 10.0)
                else:
                    self.centroidLines.AddStraightLine(startPosition, CENTROID_LINE_COLOR, position, CENTROID_LINE_COLOR, CENTROID_LINE_WIDTH)

            self.centroidLines.SubmitChanges()

    def RemoveCentroidLines(self):
        if self.centroidLines and self.centroidLines in self.parentTransform.children:
            self.parentTransform.children.remove(self.centroidLines)
        self.centroidLines = None
        self.centroidTimer = None
        self.lastProbeIDs = None

    @property
    def probeTracker(self):
        return self.scanSvc.GetProbeTracker()

    def GetProbeControl(self, probeID):
        if probeID == FORMATION_CONTROL_ID:
            return self.centerProbeControl
        else:
            return self.probeControlsByID.get(int(probeID), None)

    def GetProbeControls(self):
        return self.probeControlsByID

    def GetCenterPosition(self, positions):
        accPos = geo2.Vector((0, 0, 0))
        for pos in positions:
            if isinstance(pos, (tuple, list)):
                accPos += geo2.Vector(pos)
            else:
                accPos += pos

        return geo2.Vec3Scale(accPos, 1.0 / len(positions))

    def GetWorldPositionCenterOfActiveProbes(self):
        probes = self.probeTracker.GetProbeData()
        return self.GetCenterPosition([ self.GetProbeControl(probeID).GetWorldPosition() for probeID, probe in probes.iteritems() if probe.state == probeStateIdle ])

    def InitProbeScaling(self, probeScenePosition, centerScenePosition, mousePositionInProbePlane, mousePositionInCenterPlane):
        self.initProbeScaleData = (probeScenePosition,
         centerScenePosition,
         mousePositionInProbePlane,
         mousePositionInCenterPlane)
        self._activeEditMode = MODIFY_RANGE

    def InitProbeMove(self, probeScenePosition, centerScenePosition, mousePositionInProbeAxisPlane, mousePositionInCenterAxisPlane):
        self.probeTracker.StartMoveMode()
        self.initProbeMoveData = (probeScenePosition,
         centerScenePosition,
         mousePositionInProbeAxisPlane,
         mousePositionInCenterAxisPlane)
        self._activeEditMode = self.GetEditMode()

    def RegisterProbeScale(self, probeControl):
        self.HighlightMarkersInProbeRange()
        probeControl.HideScanRanges()
        self.probeTracker.UnsetAsScaling()
        probeID = probeControl.uniqueID
        probe = self.probeTracker.GetProbe(probeID)
        currentSize = probe.scanRange
        desiredSize = self.probeControlsByID[probeID].GetRange()
        rangeStep, desiredSize = self.probeTracker.GetRangeStepForType(probe.typeID, desiredSize)
        if not uicore.uilib.Key(uiconst.VK_SHIFT):
            scale = desiredSize / currentSize
            self.probeTracker.ScaleAllProbes(scale)
        else:
            self.probeTracker.SetProbeRangeStep(probeID, rangeStep)
        self.probeTracker.PersistProbeFormation()
        self.probeTracker.PurgeBackupData()
        self.UpdateProbeSpheres()
        self.UpdateProbeControlDisplay()
        self._activeEditMode = None

    def RegisterProbeMove(self, *args):
        probes = self.probeTracker.GetProbeData()
        for probeID, probe in probes.iteritems():
            if probe.state != probeStateIdle:
                continue
            probeControl = self.GetProbeControl(probeID)
            if probeControl:
                cachedPos = probes[probeID].destination
                currentPos = probeControl.locator.translation
                if geo2.Vec3DistanceD(cachedPos, currentPos):
                    self.probeTracker.SetProbeDestination(probeID, currentPos)

        self.probeTracker.PersistProbeFormation()
        self.probeTracker.PurgeBackupData()
        self.UpdateProbeSpheres()
        self.UpdateProbeControlDisplay()
        self.HighlightMarkersInProbeRange()
        self._activeEditMode = None

    def ScaleProbe(self, probeControl, currentCursorPosInProbePlane, currentCursorPosInCenterPlane):
        probeScenePosition, centerScenePosition, mousePositionInProbePlane, mousePositionInCenterPlane = self.initProbeScaleData
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            initDistance = geo2.Vec3Length(geo2.Vec3Subtract(probeScenePosition, mousePositionInProbePlane))
            distanceToFocusPoint = geo2.Vec3Length(geo2.Vec3Subtract(probeScenePosition, currentCursorPosInProbePlane))
            scale = distanceToFocusPoint / initDistance
            scaleOthers = 1.0
        else:
            initDistance = geo2.Vec3Length(geo2.Vec3Subtract(centerScenePosition, mousePositionInCenterPlane))
            distanceToFocusPoint = geo2.Vec3Length(geo2.Vec3Subtract(centerScenePosition, currentCursorPosInCenterPlane))
            scale = distanceToFocusPoint / initDistance
            scaleOthers = scale
        probeIDs = [ probeID for probeID in self.probeTracker.GetProbeData() ]
        probe = self.probeTracker.GetProbe(probeControl.uniqueID)
        probeControl.SetRange(probe.scanRange * scale)
        probesInfo = self.probeTracker.GetScaledProbesData(probeIDs, scaleOthers)
        positions = []
        for probeID, probePos, scanRange in probesInfo:
            _probeControl = self.probeControlsByID[probeID]
            if probeID != probeControl.uniqueID:
                _probeControl.SetRange(scanRange)
            _probeControl.SetPosition(probePos)
            positions.append(probePos)

        if self.centerProbeControl:
            centerPosition = self.GetCenterPosition(positions)
            self.centerProbeControl.SetPosition(centerPosition)
        self.HighlightMarkersInProbeRange()
        self.HighlightCursors(probeControl)
        self.UpdateProbeControlDisplay()

    def MoveProbe(self, probeControl, moveAxis, currentCursorPosInProbeAxisPlane, currentCursorPosInCenterAxisPlane):
        alt = uicore.uilib.Key(uiconst.VK_MENU)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        probeIDs = [ probeID for probeID in self.probeTracker.GetProbeData() ]
        allPositionDiff = (0, 0, 0)
        probePositionDiff = (0, 0, 0)
        positionOverride = {}
        probesInfo = self.probeTracker.GetScaledProbesData(probeIDs, 1.0)
        probeScenePosition, centerScenePosition, mousePositionInProbeAxisPlane, mousePositionInCenterAxisPlane = self.initProbeMoveData
        if self._activeEditMode == MODIFY_SPREAD:
            initDistance = geo2.Vec3Length(geo2.Vec3Subtract(centerScenePosition, mousePositionInCenterAxisPlane))
            distanceToFocusPoint = geo2.Vec3Length(geo2.Vec3Subtract(centerScenePosition, currentCursorPosInCenterAxisPlane))
            scale = distanceToFocusPoint / initDistance
            if shift:
                modProbesInfo = self.probeTracker.GetScaledProbesData([probeControl.uniqueID], scale)
                positionOverride[probeControl.uniqueID] = modProbesInfo[0][1]
            else:
                probesInfo = self.probeTracker.GetScaledProbesData(probeIDs, scale)
        elif self._activeEditMode == MODIFY_POSITION:
            initPosition = geo2.Vec3Subtract(probeScenePosition, mousePositionInProbeAxisPlane)
            currentPosition = geo2.Vec3Subtract(probeScenePosition, currentCursorPosInProbeAxisPlane)
            positionDiff = geo2.Vec3Scale(geo2.Vec3Subtract(initPosition, currentPosition), 1 / SOLARSYSTEM_SCALE)
            if shift:
                probePositionDiff = self.ClampVector(positionDiff, moveAxis)
            else:
                allPositionDiff = self.ClampVector(positionDiff, moveAxis)
        else:
            return
        positions = []
        for probeID, probePos, scanRange in probesInfo:
            _probeControl = self.probeControlsByID[probeID]
            newPosition = positionOverride.get(probeID, geo2.Vec3Add(probePos, allPositionDiff))
            if probeID == probeControl.uniqueID:
                newPosition = geo2.Vec3Add(newPosition, probePositionDiff)
            _probeControl.SetPosition(newPosition)
            positions.append(newPosition)

        centerPosition = self.GetCenterPosition(positions)
        for probeID, probePos, scanRange in probesInfo:
            _probeControl = self.probeControlsByID[probeID]
            _probeControl.SetFormationCenter(centerPosition)

        if self.centerProbeControl:
            self.centerProbeControl.SetPosition(centerPosition)
        self.HighlightCursors(probeControl, moveAxis)
        if shift or self._activeEditMode == MODIFY_SPREAD:
            self.HighlightProbeIntersections(showAll=True)
        else:
            self.HighlightProbeIntersections()
        self.UpdateProbeControlDisplay()

    def ClampVector(self, vec, axis):
        if axis == 'xz':
            x, y, z = vec
            return (x, 0.0, z)
        if axis == 'xy':
            x, y, z = vec
            return (x, y, 0.0)
        if axis == 'yz':
            x, y, z = vec
            return (0.0, y, z)
        if axis == 'x':
            scaledDir = (1.0, 0.0, 0.0)
        elif axis == 'y':
            scaledDir = (0.0, 1.0, 0.0)
        elif axis == 'z':
            scaledDir = (0.0, 0.0, 1.0)
        dot = geo2.Vec3Dot(vec, scaledDir)
        scaledDir = geo2.Vec3Scale(scaledDir, dot)
        return scaledDir

    def CancelProbeMoveOrScaling(self, *args):
        self.RemoveCentroidLines()
        self.probeTracker.RestoreProbesFromBackup()
        self.UpdateProbeSpheres()
        for probeControl in self.probeControlsByID.itervalues():
            probeControl.HideScanRanges()

        self.HighlightMarkersInProbeRange()
        self._activeEditMode = None

    def FocusOnProbe(self, probeID):
        try:
            probeID = int(probeID)
        except ValueError:
            focusPoint = self.probeTracker.GetCenterOfActiveProbes()
        else:
            focusPoint = self.probeTracker.GetProbe(probeID).destination

        self.systemMapHandler.markersHandler.mapView.SetCameraPointOfInterestSolarSystemPosition(self.systemMapHandler.solarsystemID, focusPoint)

    def CreateSphereResult(self, result):
        sphereSize = result.data
        sphere = trinity.Load('res:/dx9/model/UI/scanbubblehitsphere.red')
        sphere.name = 'Result sphere'
        sphere.scaling = (sphereSize / 4, sphereSize / 4, sphereSize / 4)
        locator = trinity.EveTransform()
        locator.name = 'scanResult_%s' % result.id
        locator.translation = result.pos
        locator.children.append(sphere)
        self.parentTransform.children.append(locator)
        if result.id not in self.resultObjectsByID:
            self.resultObjectsByID[result.id] = []
        self.resultObjectsByID[result.id].append(locator)
        markerID = (MARKERID_SCANRESULT, result.id)
        markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
        if markerObject:
            markerObject.UpdateResultData(result)
            markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(result.pos))
        else:
            self.systemMapHandler.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerScanResult, resultData=result, solarSystemID=self.systemMapHandler.solarsystemID, mapPositionLocal=SolarSystemPosToMapPos(result.pos), mapPositionSolarSystem=self.systemMapHandler.position)
        self.resultMarkers.add(markerID)

    def CreateCircleResult(self, result):
        lineSet = mapViewUtil.CreateLineSet()
        self.parentTransform.children.append(lineSet)
        if result.id not in self.resultObjectsByID:
            self.resultObjectsByID[result.id] = []
        self.resultObjectsByID[result.id].append(lineSet)
        lineSet.scaling = (1000000.0, 1000000.0, 1000000.0)
        lineSet.translation = result.data.point
        lineSet.rotation = geo2.QuaternionRotationArc((0.0, 1.0, 0.0), result.data.normal)
        lineIDs = mapViewUtil.DrawCircle(lineSet, centerPosition=(0, 0, 0), radius=result.data.radius / 1000000.0, startColor=CIRCLE_COLOR, endColor=CIRCLE_COLOR, lineWidth=2.5)
        for lineID in lineIDs:
            lineSet.ChangeLineAnimation(lineID, CIRCLE_COLOR, 0.05, 12)

        lineSet.SubmitChanges()
        markerID = (MARKERID_SCANRESULT, result.id)
        markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
        if markerObject:
            markerObject.UpdateResultData(result)
            markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(result.data.point))
        else:
            self.systemMapHandler.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerScanResult, resultData=result, solarSystemID=self.systemMapHandler.solarsystemID, mapPositionLocal=SolarSystemPosToMapPos(result.data.point), mapPositionSolarSystem=self.systemMapHandler.position)
        self.resultMarkers.add(markerID)

    def CreatePointResult(self, result):
        if isinstance(result.data, list):
            positions = result.data
        else:
            positions = [result.data]
        for i, position in enumerate(positions):
            markerID = (MARKERID_SCANRESULT, (result.id, i))
            markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
            if markerObject:
                markerObject.UpdateResultData(result)
                markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(position))
            else:
                self.systemMapHandler.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerScanResult, resultData=result, solarSystemID=self.systemMapHandler.solarsystemID, mapPositionLocal=SolarSystemPosToMapPos(position), mapPositionSolarSystem=self.systemMapHandler.position)
            self.resultMarkers.add(markerID)

    def HighlightProbeBorder(self, probeControl = None):
        probeControls = self.GetProbeControls()
        for _probeID, _probeControl in probeControls.iteritems():
            if probeControl and _probeControl is probeControl:
                probeControl.HighlightBorder(True)
            else:
                _probeControl.HighlightBorder(False)

    def HighlightMarkersInProbeRange(self):
        if getattr(self, 'lastHighlightItemsWithinProbeRange', None):
            timeDiff = blue.os.TimeDiffInMs(self.lastHighlightItemsWithinProbeRange, blue.os.GetWallclockTime())
            if timeDiff < 200.0:
                return
        self.lastHighlightItemsWithinProbeRange = blue.os.GetWallclockTime()
        probeData = self.probeTracker.GetProbeData()
        validProbes = [ probeID for probeID, probe in probeData.iteritems() if probe.state != const.probeStateInactive ]
        markerID_position = {}
        solarsystemMarkerIDs = self.systemMapHandler.GetMarkerIDs()
        for markerID in solarsystemMarkerIDs:
            markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
            if markerObject:
                solarSystemPosition = MapPosToSolarSystemPos(markerObject.mapPositionLocal)
                markerID_position[markerID] = solarSystemPosition

        inRangeOfProbe = []
        probeControls = self.GetProbeControls()
        for probeID in validProbes:
            if probeID not in probeControls:
                continue
            probeControl = probeControls[probeID]
            pPos = probeControl.GetPosition()
            pRange = probeControl.GetRange()
            for markerID, position in markerID_position.items():
                if pRange > geo2.Vec3Length(geo2.Vec3Subtract(pPos, position)):
                    inRangeOfProbe.append(markerID)
                    markerID_position.pop(markerID, None)

            if not markerID_position:
                break

        for markerID in solarsystemMarkerIDs:
            markerObject = self.systemMapHandler.markersHandler.GetMarkerByID(markerID)
            if not markerObject or not hasattr(markerObject, 'SetInRangeIndicatorState'):
                continue
            markerObject.SetInRangeIndicatorState(markerID in inRangeOfProbe)


class ProbesIntersection(object):
    _opacity = 0.0
    lastConfig = None

    def __init__(self, probePair):
        eff = trinity.Tr2Effect()
        eff.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        sampler = list(eff.samplerOverrides.GetDefaultValue())
        sampler[0] = 'DiffuseMapSampler'
        sampler[1] = trinity.TRITADDRESS_CLAMP
        sampler[2] = trinity.TRITADDRESS_CLAMP
        eff.samplerOverrides.append(tuple(sampler))
        diffuseColor = trinity.Tr2Vector4Parameter()
        diffuseColor.name = 'DiffuseColor'
        eff.parameters.append(diffuseColor)
        self.diffuseColor = diffuseColor
        diffuseMap = trinity.TriTextureParameter()
        diffuseMap.name = 'DiffuseMap'
        diffuseMap.resourcePath = 'res:/UI/Texture/classes/ProbeScanner/intersectionCircle.png'
        eff.resources.append(diffuseMap)
        mesha = trinity.Tr2MeshArea()
        mesha.effect = eff
        mesh = trinity.Tr2Mesh()
        mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        mesh.additiveAreas.append(mesha)
        transform = trinity.EveTransform()
        transform.scaling = (10000.0, 10000.0, 10000.0)
        transform.mesh = mesh
        self.transform = transform
        self.opacity = INTERSECTION_INACTIVE

    @apply
    def opacity():

        def fget(self):
            return self._opacity

        def fset(self, value):
            self._opacity = value
            r, g, b, a = BASE_PROBE_COLOR
            self.diffuseColor.value = (r * value,
             g * value,
             b * value,
             1.0)

        return property(**locals())
