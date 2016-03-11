#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\layout\mapLayoutHandler.py
import weakref
from eve.client.script.ui.shared.mapView.layout.mapLayoutConstellations import MapLayoutConstellations
from eve.client.script.ui.shared.mapView.layout.mapLayoutRegions import MapLayoutRegions
from eve.client.script.ui.shared.mapView.layout.mapLayoutSolarSystems import MapLayoutSolarSystems
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_LAYOUT_REGIONS, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_SOLARSYSTEM, JUMPBRIDGE_CURVE_SCALE, JUMPBRIDGE_TYPE
from eve.client.script.ui.shared.mapView.mapViewUtil import ScaleSolarSystemValue
import uthread
import blue
import trinity
import geo2
layoutClassMapping = {VIEWMODE_LAYOUT_SOLARSYSTEM: MapLayoutSolarSystems,
 VIEWMODE_LAYOUT_REGIONS: MapLayoutRegions,
 VIEWMODE_LAYOUT_CONSTELLATIONS: MapLayoutConstellations}

class MapViewLayoutNode(object):
    dirty = False

    def __init__(self, particleID, solarSystemID, position):
        self.particleID = particleID
        self.solarSystemID = solarSystemID
        self.lineData = set()
        self.position = position

    def AddLineData(self, lineData):
        self.lineData.add(lineData)

    def SetPosition(self, position):
        self.position = position


class MapViewLayoutHandler(object):
    starParticles = None
    jumpLineSet = None
    layoutDirty = False
    extraJumpLineSet = None
    starGateAdjusted = None
    adjustStargateLinesForSolarSystem = None
    lineAdjustmentOffset = {}
    morph_to_index = 0
    transformTime = 1.0
    currentLayout = None

    def StopHandler(self):
        try:
            self.updateThread.kill()
        except:
            pass

    def __init__(self, mapView):
        self.mapViewWR = weakref.ref(mapView)
        self.nodesByParticleID = {}
        self.nodesBySolarSystemID = {}
        self.dirtyNodesBySolarSystemID = {}
        self.layouts = {}
        self.updateThread = uthread.new(self.Tick)

    def __del__(self):
        self.nodesByParticleID = None
        self.nodesBySolarSystemID = None
        self.dirtyNodesBySolarSystemID = None
        self.layouts = None

    def __len__(self):
        return len(self.nodesByParticleID)

    def ClearCache(self):
        for layoutType, mapLayout in self.layouts.iteritems():
            mapLayout.ClearCache()

        self.currentLayout = None

    def LoadLayout(self, layoutType, *args, **kwds):
        if self.currentLayout == (layoutType, args, kwds):
            return
        self.currentLayout = (layoutType, args, kwds)
        if layoutType not in self.layouts:
            self.layouts[layoutType] = layoutClassMapping[layoutType](self)
        mapLayout = self.layouts[layoutType]
        mapLayout.PrimeLayout(*args, **kwds)
        self.mapLayout = mapLayout
        for solarSystemID, position in mapLayout.positionsBySolarSystemID.iteritems():
            mapNode = self.nodesBySolarSystemID[solarSystemID]
            if not mapNode.position or not geo2.Vec3Equal(mapNode.position, position):
                mapNode.oldPosition = mapNode.position or position
                mapNode.SetPosition(position)
                self.dirtyNodesBySolarSystemID[solarSystemID] = mapNode

        if self.dirtyNodesBySolarSystemID:
            self.layoutDirty = True

    def Tick(self):
        while True:
            self._Tick()
            blue.synchro.SleepWallclock(500)

    def _Tick(self):
        if not self.layoutDirty:
            return
        self.layoutDirty = False
        mapView = self.mapViewWR()
        if not mapView or mapView.destroyed:
            return
        lineSet = self.jumpLineSet()
        extraLineSet = self.extraJumpLineSet()
        starParticles = self.starParticles()
        if not (lineSet and extraLineSet and starParticles):
            return
        mapView.LayoutChangeStarting(self.dirtyNodesBySolarSystemID)
        mapView.SetMarkersFilter(self.mapLayout.visibleMarkers)
        adjustLines, dirtyNodes = self.AdjustStarGateLines()
        for mapNode in dirtyNodes:
            if mapNode.solarSystemID not in self.dirtyNodesBySolarSystemID:
                mapNode.oldPosition = mapNode.position
                self.dirtyNodesBySolarSystemID[mapNode.solarSystemID] = mapNode

        extraLineSet.ClearLines()
        extraLineSet.SubmitChanges()
        worldUp = geo2.Vector(0.0, -1.0, 0.0)
        GetNodeBySolarSystemID = self.GetNodeBySolarSystemID
        changeLinePositions = {}
        start = blue.os.GetWallclockTime()
        ndt = 0.0
        duration = self.transformTime

        def update_mapNode_position(mapNode):
            newPosition = geo2.Vec3Lerp(mapNode.oldPosition, mapNode.position, ndt)
            starParticles.SetItemElement(mapNode.particleID, 0, newPosition)
            for lineData in mapNode.lineData:
                if mapNode.solarSystemID == lineData.fromSolarSystemID:
                    if lineData.lineID in changeLinePositions:
                        changeLinePositions[lineData.lineID][0] = newPosition
                    else:
                        changeLinePositions[lineData.lineID] = [newPosition, None, lineData]
                elif lineData.lineID in changeLinePositions:
                    changeLinePositions[lineData.lineID][1] = newPosition
                else:
                    changeLinePositions[lineData.lineID] = [None, newPosition, lineData]

        def update_line_position(posInfo):
            lineData = posInfo[2]
            lineID = lineData.lineID
            fromPosition = posInfo[0]
            if fromPosition is None:
                fromMapNode = GetNodeBySolarSystemID(lineData.fromSolarSystemID)
                fromPosition = fromMapNode.position
                posInfo[0] = fromPosition
            toPosition = posInfo[1]
            if toPosition is None:
                toMapNode = GetNodeBySolarSystemID(lineData.toSolarSystemID)
                toPosition = toMapNode.position
                posInfo[1] = toPosition
            if lineID in adjustLines:
                fromPosition = geo2.Vec3Add(fromPosition, adjustLines[lineID][0])
                toPosition = geo2.Vec3Add(toPosition, adjustLines[lineID][2])
            lineSet.ChangeLinePositionCrt(lineID, fromPosition, toPosition)
            if lineData.jumpType == JUMPBRIDGE_TYPE:
                linkVec = geo2.Vec3Subtract(toPosition, fromPosition)
                normLinkVec = geo2.Vec3Normalize(linkVec)
                rightVec = geo2.Vec3Cross(worldUp, normLinkVec)
                upVec = geo2.Vec3Cross(rightVec, normLinkVec)
                offsetVec = geo2.Vec3Scale(geo2.Vec3Normalize(upVec), geo2.Vec3Length(linkVec) * 1.0)
                midPos = geo2.Vec3Scale(geo2.Vec3Add(toPosition, fromPosition), 0.5)
                splinePos = geo2.Vec3Add(midPos, offsetVec)
                lineSet.ChangeLineIntermediateCrt(lineID, splinePos)

        while ndt != 1.0:
            ndt = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / duration, 1.0)
            map(update_mapNode_position, self.dirtyNodesBySolarSystemID.itervalues())
            map(update_line_position, changeLinePositions.itervalues())
            starParticles.UpdateData()
            lineSet.SubmitChanges()
            mapView.LayoutChanging(ndt, self.dirtyNodesBySolarSystemID)
            blue.pyos.synchro.Yield()
            if not mapView or mapView.destroyed:
                return

        self.mapLayout.LoadExtraLines(extraLineSet)
        mapView.SetExtraLineMapping(self.mapLayout.extraLineMapping)
        mapView.LayoutChangeCompleted(self.dirtyNodesBySolarSystemID)
        self.transformTime = 500.0
        self.dirtyNodesBySolarSystemID = {}

    def AdjustStargateLinesForSolarSystem(self, solarSystemID):
        self.adjustStargateLinesForSolarSystem = solarSystemID
        self.layoutDirty = True

    def RegisterStarParticles(self, starParticles):
        self.starParticles = weakref.ref(starParticles)

    def RegisterJumpLineSet(self, jumpLineSet):
        self.jumpLineSet = weakref.ref(jumpLineSet)

    def RegisterExtraJumpLineSet(self, jumpLineSet):
        self.extraJumpLineSet = weakref.ref(jumpLineSet)

    def CreateSolarSystemNode(self, particleID, solarSystemID, position):
        node = MapViewLayoutNode(particleID, solarSystemID, position)
        self.nodesByParticleID[particleID] = node
        self.nodesBySolarSystemID[solarSystemID] = node
        return node

    def GetNodesIter(self):
        return self.nodesByParticleID.itervalues()

    def GetNodesByParticleID(self):
        return self.nodesByParticleID

    def GetNodeByParticleID(self, particleID):
        return self.nodesByParticleID.get(particleID, None)

    def GetNodeBySolarSystemID(self, solarSystemID):
        return self.nodesBySolarSystemID.get(solarSystemID, None)

    def GetLineData(self):
        lineIDs = set()
        for solarSystemID, mapNode in self.nodesBySolarSystemID.iteritems():
            for lineData in mapNode.lineData:
                if lineData.lineID in lineIDs:
                    continue
                lineIDs.add(lineData.lineID)
                yield lineData

    def AdjustStarGateLines(self):
        adjustLines = {}
        dirtyNodes = set()
        if self.starGateAdjusted != self.adjustStargateLinesForSolarSystem and self.lineAdjustmentOffset:
            self.starGateAdjusted = None
            for lineID, (fromSolarSystemID, toSolarSystemID, offsetFromPosition, offsetToPosition, jumpType) in self.lineAdjustmentOffset.iteritems():
                fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
                toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
                adjustLines[lineID] = ((0, 0, 0),
                 offsetFromPosition,
                 (0, 0, 0),
                 offsetToPosition)
                dirtyNodes.add(fromMapNode)
                dirtyNodes.add(toMapNode)

        if self.adjustStargateLinesForSolarSystem:
            applyOffset = self.GetStarGateLineOffsets(self.adjustStargateLinesForSolarSystem)
            self.starGateAdjusted = self.adjustStargateLinesForSolarSystem
            for lineID, (fromSolarSystemID, toSolarSystemID, offsetFromPosition, offsetToPosition, jumpType) in applyOffset.iteritems():
                if lineID in self.lineAdjustmentOffset:
                    oldOffsetFromPosition = self.lineAdjustmentOffset[lineID][2]
                    oldOffsetToPosition = self.lineAdjustmentOffset[lineID][3]
                else:
                    oldOffsetFromPosition = oldOffsetToPosition = (0, 0, 0)
                fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
                toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
                adjustLines[lineID] = (offsetFromPosition,
                 oldOffsetFromPosition,
                 offsetToPosition,
                 oldOffsetToPosition)
                dirtyNodes.add(fromMapNode)
                dirtyNodes.add(toMapNode)

            self.lineAdjustmentOffset = applyOffset
        return (adjustLines, dirtyNodes)

    def GetStarGateLineOffsets(self, solarSystemID):
        fromSystemInfo = cfg.mapSolarSystemContentCache[solarSystemID]
        mapNode = self.GetNodeBySolarSystemID(solarSystemID)
        adjustLines = {}
        for lineData in mapNode.lineData:
            if solarSystemID == lineData.fromSolarSystemID:
                otherSystemInfo = cfg.mapSolarSystemContentCache[lineData.toSolarSystemID]
            else:
                otherSystemInfo = cfg.mapSolarSystemContentCache[lineData.fromSolarSystemID]
            fromStargateVector = None
            for each in fromSystemInfo.stargates:
                if fromSystemInfo.stargates[each].destination in otherSystemInfo.stargates:
                    fromStargate = fromSystemInfo.stargates[each]
                    fromStargateVector = (fromStargate.position.x, fromStargate.position.y, fromStargate.position.z)
                    break

            if fromStargateVector:
                stargateOffset = geo2.Vec3Scale(fromStargateVector, ScaleSolarSystemValue(1.0))
                if solarSystemID == lineData.fromSolarSystemID:
                    adjustLines[lineData.lineID] = (lineData.fromSolarSystemID,
                     lineData.toSolarSystemID,
                     stargateOffset,
                     (0, 0, 0),
                     lineData.jumpType)
                else:
                    adjustLines[lineData.lineID] = (lineData.fromSolarSystemID,
                     lineData.toSolarSystemID,
                     (0, 0, 0),
                     stargateOffset,
                     lineData.jumpType)

        return adjustLines

    def GetDistanceBetweenSolarSystems(self, fromSolarSystemID, toSolarSystemID):
        fromMapNode = self.GetNodeBySolarSystemID(fromSolarSystemID)
        toMapNode = self.GetNodeBySolarSystemID(toSolarSystemID)
        if fromMapNode and toMapNode:
            return geo2.Vec3Length(geo2.Vec3Subtract(fromMapNode.position, toMapNode.position))
