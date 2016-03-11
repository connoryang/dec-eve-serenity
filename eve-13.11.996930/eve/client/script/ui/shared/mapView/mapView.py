#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapView.py
import itertools
import logging
import math
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.fill import Fill
from carbonui.util.bunch import Bunch
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.colorModes.colorModeInfoBase import ColorModeInfoBase
from eve.client.script.ui.shared.mapView.dockPanelSubFrame import DockablePanelContentFrame
from eve.client.script.ui.shared.mapView.layout.mapLayoutHandler import MapViewLayoutHandler
from eve.client.script.ui.shared.mapView.mapViewBookmarkHandler import MapViewBookmarkHandler
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData
from eve.client.script.ui.shared.mapView.mapViewNavigation import MapViewNavigation
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyHome import MarkerMyHome
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyLocation import MarkerMyLocation
from eve.client.script.ui.shared.mapView.markers.mapMarkersHandler import MapViewMarkersHandler
from eve.client.script.ui.shared.mapView.mapViewSceneContainer import MapViewSceneContainer
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting, SetMapViewSetting
from eve.client.script.ui.shared.mapView.mapViewSolarSystem import MapViewSolarSystem
from eve.client.script.ui.shared.mapView import mapViewUtil
from eve.client.script.ui.shared.mapView.systemMapHandler import SystemMapHandler
from eve.common.script.sys.idCheckers import IsStation
from eve.common.script.util.eveFormat import FmtSystemSecStatus
import blue
from inventorycommon.util import IsWormholeSystem, IsWormholeRegion, IsWormholeConstellation
import trinity
import uthread
import fleetbr
import nodemanager
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
import eve.client.script.ui.shared.mapView.mapViewColorHandler as colorHandler
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_COLOR_SETTINGS, VIEWMODE_LAYOUT_SETTINGS, VIEWMODE_LAYOUT_REGIONS, VIEWMODE_LAYOUT_CONSTELLATIONS, VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS, VIEWMODE_LINES_SETTINGS, VIEWMODE_LINES_NONE, VIEWMODE_LINES_ALL, VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS, VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS, MARKERID_MYPOS, MARKERID_SOLARSYSTEM_CELESTIAL, MARKERID_MYHOME, VIEWMODE_MARKERS_SETTINGS, JUMPBRIDGE_COLOR, VIEWMODE_FOCUS_SELF, MAPVIEW_OVERLAY_PADDING_FULLSCREEN, MAPVIEW_OVERLAY_PADDING_NONFULLSCREEN, UNIVERSE_SCALE, JUMPBRIDGE_TYPE, SETTING_PREFIX, STAR_SIZE, MAPVIEW_PRIMARY_OVERLAY_ID
import eve.client.script.ui.shared.maps.mapcommon as mapcommon
from eve.common.script.sys.eveCfg import IsSolarSystem, IsConstellation, IsRegion, GetActiveShip
import geo2
import carbonui.const as uiconst
import localization
from utillib import KeyVal
log = logging.getLogger(__name__)
LINE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines3DStarMapNew.fx'
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/mapStarNew5.dds'
PARTICLE_SPRITE_HEAT_TEXTURE = 'res:/Texture/Particle/mapStarNewHeat.dds'
PARTICLE_SPRITE_DATA_TEXTURE = 'res:/Texture/Particle/mapStatData_Circle.dds'
DISTANCE_RANGE = 'distanceRange'
NEUTRAL_COLOR = (0.5, 0.5, 0.5, 1.0)
HEX_TILE_SIZE = 60

class MapView(Container):
    __notifyevents__ = ['OnAvoidanceItemsChanged',
     'OnUIScalingChange',
     'OnAutopilotUpdated',
     'OnDestinationSet',
     'OnHomeStationChanged',
     'OnBallparkSetState',
     'OnSessionChanged',
     'DoBallClear',
     'DoBallsAdded']
    mapRoot = None
    curveSet = None
    systemMap = None
    markersHandler = None
    bookmarkHandler = None
    layoutHandler = None
    markersAlwaysVisible = set()
    markersLoaded = False
    extraLineMapping = None
    dirtyLineIDs = set()
    inFocus = False
    solarSystemStandalone = None
    overlayContainer = None
    isFullScreen = False
    currentSolarsystem = None
    hilightID = None
    jumpRouteHighlightID = None
    mapViewID = None
    showDebugInfo = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.isFullScreen = attributes.isFullScreen
        self.mapViewID = attributes.mapViewID
        self.autoFocusEnabled = settings.char.ui.Get('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        self.Reset()
        self.mapSvc = sm.GetService('map')
        self.clientPathfinderService = sm.GetService('clientPathfinderService')
        self.overlayTools = Container(parent=self, name='overlayTools')
        self.colorModeInfoPanel = ColorModeInfoBase(parent=self.overlayTools, mapView=self)
        self.infoLayer = Container(parent=self, clipChildren=True, name='infoLayer', opacity=0.0)
        self.mapNavigation = MapViewNavigation(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, mapView=self)
        sceneContainer = MapViewSceneContainer(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        sceneContainer.Startup()
        self.sceneContainer = sceneContainer
        self.camera.SetCallback(self.OnCameraMoved)
        if attributes.starColorMode:
            self.SetViewColorMode(attributes.starColorMode, updateColorMode=False)
        uthread.new(self.InitMap, interestID=attributes.interestID)
        sm.RegisterNotify(self)
        uthread.new(uicore.registry.SetFocus, self)
        self.showDebugInfo = attributes.Get('showDebugInfo', self.showDebugInfo)
        if self.showDebugInfo:
            self.debugOutput = EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT, left=6, top=6, idx=0)
            self.debugOutputTimer = AutoTimer(5, self.UpdateDebugOutput)
        sm.ScatterEvent('OnClientEvent_OpenMap')
        mapViewUtil.LogColorModeUsage(useCase='open')

    def Close(self, *args, **kwds):
        if self.mapViewID:
            self.camera.RegisterCameraSettings(self.mapViewID)
        sm.GetService('audio').SendUIEvent('map_stop_all')
        if self.currentSolarsystem:
            self.currentSolarsystem.RemoveFromScene()
        self.currentSolarsystem = None
        if self.camera:
            self.camera.Close()
        if self.markersHandler:
            self.markersHandler.StopHandler()
        self.markersHandler = None
        if self.bookmarkHandler:
            self.bookmarkHandler.StopHandler()
        self.bookmarkHandler = None
        if self.layoutHandler:
            self.layoutHandler.StopHandler()
        self.layoutHandler = None
        self.mapNavigation = None
        self.Reset()
        Container.Close(self, *args, **kwds)

    def UpdateDebugOutput(self):
        if self.destroyed:
            return
        mapViewUtil.UpdateDebugOutput(self.debugOutput, camera=self.camera, mapView=self)

    def SetFocusState(self, focusState):
        self.inFocus = focusState

    def Reset(self):
        self.LogInfo('MapViewPanel Reset')
        self.destinationPath = [None]
        self.currentSolarsystem = None
        self.activeState = None
        self.autoFocusEnabled = True
        self.mapMode = None
        self.lineMode = None
        if self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        self.abstractMode = False
        self.mapStars = None
        self.starParticles = None
        self.solarSystemJumpLineSet = None
        self.overlayContentFrame = None
        self.starData = {}
        self.starColorByID = {}
        self.activeObjects = Bunch()

    def LoadSearchResult(self, searchResult):
        if searchResult:
            self.SetActiveItemID(searchResult[0].itemID, zoomToItem=True)

    def OnDockModeChanged(self, isFullScreen):
        self.isFullScreen = isFullScreen
        if self.overlayContentFrame and not self.overlayContentFrame.destroyed:
            if isFullScreen:
                self.overlayContentFrame.padding = MAPVIEW_OVERLAY_PADDING_FULLSCREEN
            else:
                self.overlayContentFrame.padding = MAPVIEW_OVERLAY_PADDING_NONFULLSCREEN

    def OnMapViewSettingChanged(self, settingKey, settingValue, *args, **kwds):
        if self.solarSystemStandalone:
            if settingKey == VIEWMODE_MARKERS_SETTINGS:
                SetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, settingValue, MAPVIEW_PRIMARY_OVERLAY_ID)
            self.solarSystemStandalone.OnMapViewSettingChanged(settingKey, settingValue, *args, **kwds)
        if settingKey == VIEWMODE_FOCUS_SELF:
            self.EnableAutoFocus()
            self.SetActiveState(primaryItemID=session.solarsystemid2, localID=(MARKERID_MYPOS, session.charid), zoomToItem=False)
            return
        if settingKey == VIEWMODE_MARKERS_SETTINGS:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers(showChanges=True)
            else:
                self.bookmarkHandler.LoadBookmarkMarkers()
            return
        if settingKey == VIEWMODE_COLOR_SETTINGS:
            mapViewUtil.LogColorModeUsage(useCase='change')
        self.UpdateMapLayout()

    def LoadOverlaySolarSystemMap(self, solarSystemID):
        settings.char.ui.Set('%s_overlayActiveState_%s' % (SETTING_PREFIX, self.mapViewID), solarSystemID)
        if self.solarSystemStandalone and not self.solarSystemStandalone.destroyed:
            if self.solarSystemStandalone.solarSystemID != solarSystemID:
                self.solarSystemStandalone.LoadSolarSystemDetails(solarSystemID)
                self.solarSystemStandalone.FrameSolarSystem()
            return
        overlayContainer = Container(parent=self, state=uiconst.UI_NORMAL, idx=0)
        fadeFill = Fill(bgParent=overlayContainer, color=(0, 0, 0, 0))
        uicore.animations.FadeTo(fadeFill, startVal=0.0, endVal=0.75, duration=1.0)
        self.overlayContainer = overlayContainer
        if self.isFullScreen:
            padding = MAPVIEW_OVERLAY_PADDING_FULLSCREEN
            self.sceneContainer.renderJob.enabled = False
        else:
            padding = MAPVIEW_OVERLAY_PADDING_NONFULLSCREEN
            self.sceneContainer.renderJob.enabled = True
        contentFrame = DockablePanelContentFrame(parent=overlayContainer, padding=padding)
        markerSettings = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, self.mapViewID)
        SetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, markerSettings, MAPVIEW_PRIMARY_OVERLAY_ID)
        self.solarSystemStandalone = MapViewSolarSystem(parent=contentFrame.content, showCloseButton=True, showInfobox=True, closeFunction=self.CloseOverlayContainer, mapViewID=MAPVIEW_PRIMARY_OVERLAY_ID)
        contentFrame.AnimateContentIn(animationOffset=0.1)
        self.solarSystemStandalone.LoadSolarSystemDetails(solarSystemID)
        self.solarSystemStandalone.FrameSolarSystem()
        self.overlayContentFrame = contentFrame

    def UpdateMapLayout(self):
        self.UpdateMapViewColorMode()
        if self.destroyed:
            return
        currentViewModeGroup = GetMapViewSetting(VIEWMODE_LAYOUT_SETTINGS, self.mapViewID)
        currentAbstract = GetMapViewSetting(VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS, self.mapViewID)
        if currentViewModeGroup != self.mapMode or currentAbstract != self.abstractMode:
            self.mapMode = currentViewModeGroup
            self.abstractMode = currentAbstract
            self.RefreshActiveState()
        currentLineMode = GetMapViewSetting(VIEWMODE_LINES_SETTINGS, self.mapViewID)
        if currentLineMode != self.lineMode:
            self.UpdateLines(hint='OnMapViewSettingChanged')

    def CloseOverlayContainer(self, *args, **kwds):
        self.sceneContainer.renderJob.enabled = True
        if self.overlayContainer and not self.overlayContainer.destroyed:
            self.overlayContainer.Close()
        self.solarSystemStandalone = None
        self.overlayContainer = None
        settings.char.ui.Set('%s_overlayActiveState_%s' % (SETTING_PREFIX, self.mapViewID), None)

    def InitMap(self, interestID = None):
        if self.destroyed:
            return
        self.LogInfo('MapView: InitMap')
        scene = trinity.EveSpaceScene()
        scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
        scene.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        scene.backgroundRenderingEnabled = True
        node = nodemanager.FindNode(scene.backgroundEffect.resources, 'NebulaMap', 'trinity.TriTextureParameter')
        if node is not None:
            node.resourcePath = 'res:/UI/Texture/classes/MapView/backdrop_cube.dds'
        node = nodemanager.FindNode(scene.backgroundEffect.resources, 'StarMap', 'trinity.TriTextureParameter')
        if node is not None:
            node.resourcePath = 'res:/dx9/scene/starfield/Stars01_Tile2_dim.dds'
        self.sceneContainer.scene = scene
        self.sceneContainer.DisplaySpaceScene()
        self.mapRoot = trinity.EveRootTransform()
        self.mapRoot.name = 'mapRoot'
        self.mapRoot.display = False
        scene.objects.append(self.mapRoot)
        self.layoutHandler = MapViewLayoutHandler(self)
        self.markersHandler = MapViewMarkersHandler(self, self.sceneContainer.bracketCurveSet, self.infoLayer, eventHandler=self.mapNavigation)
        self.bookmarkHandler = MapViewBookmarkHandler(self, loadUniverseBookmarks=True)
        self.CreateStarParticles()
        lineSet = self.CreateJumpLineSet()
        self.solarSystemJumpLineSet = lineSet
        self.layoutHandler.RegisterJumpLineSet(lineSet)
        lineSet = self.CreateJumpLineSet()
        self.extraJumpLineSet = lineSet
        self.layoutHandler.RegisterExtraJumpLineSet(lineSet)
        self.LoadJumpLines()
        self.LoadAllianceJumpLines()
        self.UpdateMapLayout()
        if self.destroyed:
            return
        if self.destroyed:
            return
        self.starLegend = []
        self.tileLegend = []
        self.ShowMyLocation()
        if self.destroyed:
            return
        self.ShowMyHomeStation()
        if self.destroyed:
            return
        if self.destroyed:
            return
        if interestID:
            self.SetActiveItemID(interestID, zoomToItem=True)
        else:
            if self.mapViewID:
                self.camera.LoadRegisteredCameraSettings(self.mapViewID)
            activeOverlaySolarSystemID = settings.char.ui.Get('%s_overlayActiveState_%s' % (SETTING_PREFIX, self.mapViewID), None)
            if IsWormholeSystem(session.solarsystemid2):
                defaultActiveState = {'primaryItemID': const.locationUniverse}
            else:
                defaultActiveState = {'primaryItemID': session.solarsystemid2,
                 'localID': (MARKERID_MYPOS, session.charid)}
            activeState = settings.char.ui.Get('%s_activeState_%s' % (SETTING_PREFIX, self.mapViewID), defaultActiveState)
            self.SetActiveState(**activeState)
            if activeOverlaySolarSystemID:
                self.SetActiveItemID(activeOverlaySolarSystemID)
        self.OnCameraMoved()
        self.StopLoadingBar('starmap_init')

    @apply
    def camera():

        def fget(self):
            if self.sceneContainer:
                return self.sceneContainer.camera

        return property(**locals())

    @apply
    def scene():

        def fget(self):
            return self.sceneContainer.scene

        return property(**locals())

    def LogError(self, *args, **kwds):
        log.error('MAPVIEW ' + repr(args))

    def LogInfo(self, *args, **kwds):
        log.info('MAPVIEW ' + repr(args))

    def LogWarn(self, *args, **kwds):
        log.warning('MAPVIEW ' + repr(args))

    def OnAvoidanceItemsChanged(self):
        colorMode = GetMapViewSetting(VIEWMODE_COLOR_SETTINGS, self.mapViewID)
        if colorMode == mapcommon.STARMODE_AVOIDANCE:
            self.UpdateMapViewColorMode()

    def OnUIScalingChange(self, *args):
        self.markersHandler.ReloadAll()

    def GetPickObjects(self, mouseX, mouseY, getMarkers = True):
        if not self.markersHandler:
            return
        x, y = ScaleDpi(mouseX), ScaleDpi(mouseY)
        vx, vy = self.sceneContainer.viewport.x, self.sceneContainer.viewport.y
        lastDistance = None
        picked = []
        for markerID, marker in self.markersHandler.projectBrackets.iteritems():
            if not marker.projectBracket.isInFront or not marker.positionPickable:
                continue
            mx, my = marker.projectBracket.rawProjectedPosition
            if x - 7 < vx + mx < x + 8 and y - 7 < vy + my < y + 8:
                distance = marker.projectBracket.cameraDistance
                if distance < self.camera.backClip and (lastDistance is None or distance < lastDistance):
                    if getMarkers:
                        picked = [(markerID, marker)]
                    else:
                        picked = [markerID]
                    lastDistance = distance

        return picked

    def GetItemMenu(self, itemID):
        item = self.mapSvc.GetItem(itemID, retall=True)
        if not item:
            return []
        m = []
        m.append(None)
        filterFunc = [MenuLabel('UI/Commands/ShowLocationOnMap')]
        m += sm.GetService('menu').CelestialMenu(itemID, noTrace=1, mapItem=item, filterFunc=filterFunc)
        return m

    def ShowJumpDriveRange(self):
        if getattr(self, 'mylocation', None):
            for each in self.mylocation.trackerTransform.children[:]:
                if each.name == 'jumpDriveRange':
                    self.mylocation.trackerTransform.children.remove(each)

        else:
            return
        if session.regionid > const.mapWormholeRegionMin:
            return
        shipID = GetActiveShip()
        if shipID is None:
            return
        dogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
        driveRange = dogmaLM.GetAttributeValue(shipID, const.attributeJumpDriveRange)
        if driveRange is None or driveRange == 0:
            return
        scale = 2.0 * driveRange * const.LIGHTYEAR * UNIVERSE_SCALE
        sphere = trinity.Load('res:/dx9/model/UI/JumpRangeBubble.red')
        sphere.scaling = (scale, scale, scale)
        sphere.name = 'jumpDriveRange'
        if self.abstractMode():
            sphere.display = False
        self.mylocation.trackerTransform.children.append(sphere)

    def ShowMyHomeStation(self):
        if self.destroyed:
            return
        markerID = (MARKERID_MYHOME, session.charid)
        self.markersHandler.RemoveMarker(markerID)
        try:
            self.markersAlwaysVisible.remove(markerID)
        except:
            pass

        homeStationID = sm.RemoteSvc('charMgr').GetHomeStation()
        if not homeStationID or self.destroyed:
            return
        stationInfo = self.mapSvc.GetStation(homeStationID)
        if IsWormholeRegion(stationInfo.regionID):
            return
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(stationInfo.solarSystemID)
        solarSystemPosition = mapNode.position
        localPosition = mapViewUtil.SolarSystemPosToMapPos((stationInfo.x, stationInfo.y, stationInfo.z))
        markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyHome, stationInfo=stationInfo, solarSystemID=stationInfo.solarSystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)
        self.markersAlwaysVisible.add(markerID)

    def RemoveMyLocation(self):
        markerID = (MARKERID_MYPOS, session.charid)
        self.markersHandler.RemoveMarker(markerID, fadeOut=False)

    def ShowMyLocation(self):
        if self.destroyed:
            return
        if self.mapRoot is None:
            return
        self.RemoveMyLocation()
        markerID = (MARKERID_MYPOS, session.charid)
        try:
            self.markersAlwaysVisible.remove(markerID)
        except:
            pass

        if not IsWormholeRegion(session.regionid):
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(session.solarsystemid2)
            solarSystemPosition = mapNode.position
            if session.stationid:
                stationInfo = self.mapSvc.GetStation(session.stationid)
                if self.destroyed:
                    return
                localPosition = mapViewUtil.SolarSystemPosToMapPos((stationInfo.x, stationInfo.y, stationInfo.z))
                markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, solarSystemID=stationInfo.solarSystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)
            else:
                bp = sm.GetService('michelle').GetBallpark()
                if bp and bp.ego and bp.ego in bp.balls:
                    ego = bp.balls[bp.ego]
                    localPosition = mapViewUtil.SolarSystemPosToMapPos((ego.x, ego.y, ego.z))
                else:
                    localPosition = (0.0, 0.0, 0.0)
                markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, trackObjectID=session.shipid or session.stationid, solarSystemID=session.solarsystemid2, mapPositionLocal=localPosition, mapPositionSolarSystem=solarSystemPosition)
            self.markersAlwaysVisible.add(markerID)

    def IsFlat(self):
        return self.abstractMode

    def LayoutChangeStarting(self, changedSolarSystems):
        if changedSolarSystems:
            uicore.animations.FadeTo(self.infoLayer, startVal=self.infoLayer.opacity, endVal=0.0, duration=0.1, sleep=True)

    def LayoutChanging(self, progress, changedSolarSystems):
        if self.currentSolarsystem and self.currentSolarsystem.solarsystemID in changedSolarSystems:
            mapNode = changedSolarSystems[self.currentSolarsystem.solarsystemID]
            newPosition = geo2.Vec3Lerp(mapNode.oldPosition, mapNode.position, progress)
            self.currentSolarsystem.SetPosition(newPosition)

    def LayoutChangeCompleted(self, changedSolarSystems):
        self.starParticles.UpdateBoundingBox()
        self.mapStars.mesh.minBounds = self.starParticles.aabbMin
        self.mapStars.mesh.maxBounds = self.starParticles.aabbMax
        yScaleFactor = 0.0 if self.abstractMode else 1.0
        self.markersHandler.UpdateMarkerPositions(changedSolarSystems, yScaleFactor)
        self.UpdateLines(hint='LayoutChangeCompleted')
        self.mapRoot.display = True
        uicore.animations.FadeTo(self.infoLayer, startVal=self.infoLayer.opacity, endVal=1.0, duration=1.0)

    def SetMarkersFilter(self, showMarkers):
        if showMarkers:
            showMarkers += list(self.markersAlwaysVisible)
        self.markersHandler.SetDisplayStateOverrideFilter(showMarkers)

    def CreateStarParticles(self):
        self.mapStars = trinity.EveTransform()
        self.mapStars.name = 'mapStars'
        self.mapStars.sortValueMultiplier = 1000000.0
        self.mapRoot.children.append(self.mapStars)
        tex = trinity.TriTextureParameter()
        tex.name = 'TexMap'
        tex.resourcePath = PARTICLE_SPRITE_TEXTURE
        heattex = trinity.TriTextureParameter()
        heattex.name = 'HeatTexture'
        heattex.resourcePath = PARTICLE_SPRITE_HEAT_TEXTURE
        self.starDataTexture = heattex
        distanceRangeStars = trinity.Tr2Vector4Parameter()
        distanceRangeStars.name = DISTANCE_RANGE
        distanceRangeStars.value = (0, 1, 0, 0)
        self.distanceRangeStars = distanceRangeStars
        self.starParticles = trinity.Tr2RuntimeInstanceData()
        self.starParticles.SetElementLayout([(trinity.PARTICLE_ELEMENT_TYPE.POSITION, 0, 3),
         (trinity.PARTICLE_ELEMENT_TYPE.POSITION, 1, 3),
         (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 0, 1),
         (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 1, 4)])
        mesh = trinity.Tr2InstancedMesh()
        mesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
        mesh.instanceGeometryResource = self.starParticles
        self.mapStars.mesh = mesh
        area = trinity.Tr2MeshArea()
        area.effect = trinity.Tr2Effect()
        area.effect.effectFilePath = PARTICLE_EFFECT
        area.effect.resources.append(tex)
        area.effect.resources.append(heattex)
        area.effect.parameters.append(distanceRangeStars)
        mesh.transparentAreas.append(area)
        particleCounter = itertools.count()
        starParticleData = []
        initPos = (0.0, 0.0, 0.0)
        for systemID, system in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            particleID = particleCounter.next()
            starParticleData.append((initPos,
             initPos,
             0.0,
             (0.0, 0.0, 0.0, 0.0)))
            self.layoutHandler.CreateSolarSystemNode(particleID, systemID, initPos)

        vs = trinity.GetVariableStore()
        vs.RegisterVariable('StarmapMorphValue', 0.0)
        self.starParticles.SetData(starParticleData)
        self.layoutHandler.RegisterStarParticles(self.starParticles)

    def CreateJumpLineSet(self):
        lineSet = mapViewUtil.CreateLineSet()
        lineSet.lineEffect.effectFilePath = LINE_EFFECT
        lineSet.name = 'JumpLines'
        self.mapRoot.children.append(lineSet)
        if getattr(self, 'distanceRangeLines', None) is None:
            distanceRangeLines = trinity.Tr2Vector4Parameter()
            distanceRangeLines.name = DISTANCE_RANGE
            distanceRangeLines.value = (0, 1, 0, 0)
            self.distanceRangeLines = distanceRangeLines
        lineSet.lineEffect.parameters.append(self.distanceRangeLines)
        return lineSet

    def OnCameraMoved(self):
        self._OnCameraMoved()

    def _OnCameraMoved(self):
        camera = self.camera
        if camera is None:
            return
        if not self.starParticles:
            return
        cameraDistance = self.camera.GetCameraDistanceFromInterest()
        if cameraDistance < mapViewConst.AUDIO_SOLARSYSTEM_DISTANCE:
            if self.inFocus:
                self.ChangeAmbientAudioLoop('map_system_loop_play')
            else:
                self.ChangeAmbientAudioLoop('map_system_loop_window_play')
        elif cameraDistance < mapViewConst.AUDIO_CONSTELLATION_DISTANCE:
            if self.inFocus:
                self.ChangeAmbientAudioLoop('map_constellation_loop_play')
            else:
                self.ChangeAmbientAudioLoop('map_constellation_loop_window_play')
        elif self.inFocus:
            self.ChangeAmbientAudioLoop('map_region_loop_play')
        else:
            self.ChangeAmbientAudioLoop('map_region_loop_window_play')
        aabbMin = self.starParticles.aabbMin
        aabbMax = self.starParticles.aabbMax
        bbSize = geo2.Vec3Add(geo2.Vec3Negate(aabbMin), aabbMax)
        maxLength = geo2.Vec3Length(bbSize)
        self.camera.frontClip = 0.1
        self.camera.backClip = cameraDistance + maxLength
        fadeOutFar = max(100.0, cameraDistance * 4)
        self.distanceRangeStars.value = (cameraDistance,
         fadeOutFar,
         0,
         0)
        self.distanceRangeLines.value = (cameraDistance,
         fadeOutFar,
         0,
         0)
        if self.markersHandler:
            self.markersHandler.RegisterCameraTranslationFromParent(cameraDistance)
        if self.currentSolarsystem:
            self.currentSolarsystem.RegisterCameraTranslationFromParent(cameraDistance)

    def ChangeAmbientAudioLoop(self, audioPath):
        if getattr(self, 'ambientAudioPath', None) != audioPath:
            self.ambientAudioPath = audioPath
            sm.GetService('audio').SendUIEvent('map_stop_all')
            sm.GetService('audio').SendUIEvent(audioPath)

    def GetStarData(self):
        return getattr(self, 'starData', {})

    def GetDistance(self, fromVector, toVector):
        return geo2.Vec3Length(geo2.Vec3Subtract(fromVector, toVector))

    def GetExtraMouseOverInfoForItemID(self, itemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(itemID)
        if mapNode and mapNode.particleID in self.starData:
            hintFunc, hintArgs = self.starData[mapNode.particleID]
            particleHint = hintFunc(*hintArgs)
            return particleHint

    def SetHilightItem(self, itemID):
        hilightID = itemID
        if self.hilightID != hilightID:
            self.hilightID = hilightID
            self.UpdateLines(hint='SetHilightItem')
            if hilightID:
                self.markersHandler.HilightMarkers([hilightID])
            else:
                self.markersHandler.HilightMarkers([])

    def SetCameraPointOfInterestSolarSystemPosition(self, solarSystemID, position):
        mapInfo = mapViewData.GetKnownSolarSystem(solarSystemID)
        if not mapInfo:
            return
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        self.camera.pointOfInterest = geo2.Vec3Add(mapNode.position, mapViewUtil.SolarSystemPosToMapPos(position))

    def EnableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        self.autoFocusEnabled = True

    def DisableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), False)
        self.autoFocusEnabled = False
        self.camera.FollowMarker(None)

    def SetActiveItemID(self, itemID, **kwds):
        self.EnableAutoFocus()
        if IsStation(itemID):
            stationData = cfg.stations.Get(itemID)
            markerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, self.mapViewID)
            if const.groupStation not in markerGroups:
                markerGroups.append(const.groupStation)
                SetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, markerGroups, self.mapViewID)
            self.SetActiveState(primaryItemID=stationData.solarSystemID, localID=(MARKERID_SOLARSYSTEM_CELESTIAL, itemID), **kwds)
        else:
            self.SetActiveState(primaryItemID=itemID, **kwds)

    def SetActiveMarker(self, markerObject, **kwds):
        self.EnableAutoFocus()
        if mapViewUtil.IsDynamicMarkerType(markerObject.markerID):
            self.SetActiveState(primaryItemID=markerObject.solarSystemID, localID=markerObject.markerID, **kwds)
        else:
            self.SetActiveState(primaryItemID=markerObject.markerID, **kwds)

    def RefreshActiveState(self):
        if self.activeState:
            self.SetActiveState(**self.activeState)

    def SetActiveState(self, primaryItemID, localID = None, updateCamera = True, zoomToItem = False, *args, **kwds):
        if localID == (MARKERID_MYPOS, session.charid):
            primaryItemID = session.solarsystemid2
        itemID = primaryItemID
        if IsWormholeSystem(itemID):
            if self.solarSystemStandalone and not self.solarSystemStandalone.destroyed:
                if self.solarSystemStandalone.solarSystemID == itemID:
                    self.CloseOverlayContainer()
                    return
            self.LoadOverlaySolarSystemMap(itemID)
            return
        self.CloseOverlayContainer()
        if IsWormholeConstellation(itemID):
            return
        if IsWormholeRegion(itemID):
            return
        self.activeState = {'primaryItemID': primaryItemID,
         'localID': localID}
        settings.char.ui.Set('%s_activeState_%s' % (SETTING_PREFIX, self.mapViewID), self.activeState)
        keywords = {'flatten': self.abstractMode}
        if self.mapMode == VIEWMODE_LAYOUT_REGIONS:
            if IsRegion(itemID):
                keywords['expandedItems'] = [itemID]
            elif IsConstellation(itemID):
                mapInfo = mapViewData.GetKnownConstellation(itemID)
                keywords['expandedItems'] = [mapInfo.regionID]
            elif IsSolarSystem(itemID):
                mapInfo = mapViewData.GetKnownSolarSystem(itemID)
                keywords['expandedItems'] = [mapInfo.regionID]
        elif self.mapMode == VIEWMODE_LAYOUT_CONSTELLATIONS:
            if IsConstellation(itemID):
                keywords['expandedItems'] = [itemID]
            elif IsSolarSystem(itemID):
                mapInfo = mapViewData.GetKnownSolarSystem(itemID)
                keywords['expandedItems'] = [mapInfo.constellationID]
        self.layoutHandler.LoadLayout(self.mapMode, **keywords)
        cameraPointOfInterest = None
        cameraDistanceFromInterest = None
        minCameraDistanceFromInterest = None
        activeMarkers = []
        activeObjects = Bunch()
        self.jumpRouteHighlightID = None
        if IsSolarSystem(itemID):
            self.jumpRouteHighlightID = itemID
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(itemID)
            mapData = mapViewData.GetKnownSolarSystem(itemID)
            self.LoadSolarSystemDetails(itemID)
            radius = mapViewUtil.ScaleSolarSystemValue(self.currentSolarsystem.solarSystemRadius)
            cameraDistanceFromInterest = mapViewUtil.GetTranslationFromParentWithRadius(radius, self.camera)
            minCameraDistanceFromInterest = mapViewConst.MIN_CAMERA_DISTANCE
            sm.GetService('audio').SendUIEvent('map_system_zoom_play')
            activeMarkers.append(itemID)
            activeObjects.solarSystemID = itemID
            activeObjects.constellationID = mapData.constellationID
            activeObjects.regionID = mapData.regionID
        elif IsConstellation(itemID):
            mapData = mapViewData.GetKnownConstellation(itemID)
            self.CloseCurrentSolarSystemIfAny()
            positions = [ self.layoutHandler.GetNodeBySolarSystemID(solarSystemID).position for solarSystemID in mapData.solarSystemIDs ]
            cameraPointOfInterest, radius = mapViewUtil.GetBoundingSphereRadiusCenter(positions, self.abstractMode)
            cameraDistanceFromInterest = mapViewUtil.GetTranslationFromParentWithRadius(radius, self.camera)
            minCameraDistanceFromInterest = cameraDistanceFromInterest * 0.5
            sm.GetService('audio').SendUIEvent('map_constellation_zoom_play')
            activeObjects.constellationID = itemID
            activeObjects.regionID = mapData.regionID
        elif IsRegion(itemID):
            mapInfo = mapViewData.GetKnownRegion(itemID)
            self.CloseCurrentSolarSystemIfAny()
            positions = [ self.layoutHandler.GetNodeBySolarSystemID(solarSystemID).position for solarSystemID in mapInfo.solarSystemIDs ]
            cameraPointOfInterest, radius = mapViewUtil.GetBoundingSphereRadiusCenter(positions, self.abstractMode)
            cameraDistanceFromInterest = mapViewUtil.GetTranslationFromParentWithRadius(radius, self.camera)
            minCameraDistanceFromInterest = cameraDistanceFromInterest * 0.25
            sm.GetService('audio').SendUIEvent('map_region_zoom_play')
            activeObjects.regionID = itemID
        elif mapViewUtil.IsLandmark(itemID):
            lm = self.mapSvc.GetLandmark(itemID * -1)
            cameraPointOfInterest = mapViewUtil.WorldPosToMapPos(lm.position)
            if self.abstractMode:
                x, y, z = cameraPointOfInterest
                cameraPointOfInterest = (x, 0.0, z)
        elif itemID == const.locationUniverse:
            cameraPointOfInterest = (0.0, 0.0, 0.0)
            cameraDistanceFromInterest = self.camera.maxDistance
            zoomToItem = True
        else:
            updateCamera = False
        if self.destroyed:
            return
        if not self.markersLoaded:
            self.markersLoaded = True
            self.LoadRegionMarkers()
            self.LoadConstellationMarkers()
            self.LoadSolarSystemMarkers()
            self.LoadLandmarkMarkers()
        if self.destroyed or not self.markersHandler:
            return
        markerObject = None
        if localID:
            markerObject = self.markersHandler.GetMarkerByID(localID)
        if not markerObject:
            markerObject = self.markersHandler.GetMarkerByID(itemID)
        self.activeObjects = activeObjects
        self.markersHandler.ActivateMarkers(activeMarkers)
        if updateCamera:
            if minCameraDistanceFromInterest:
                self.camera.SetMinCameraDistanceFromInterest(minCameraDistanceFromInterest)
            if zoomToItem and cameraDistanceFromInterest:
                self.camera.ZoomToDistance(cameraDistanceFromInterest)
            if markerObject and self.autoFocusEnabled:
                self.camera.FollowMarker(markerObject)
            elif cameraPointOfInterest:
                self.camera.FollowMarker(None)
                self.camera.pointOfInterest = cameraPointOfInterest

    def CloseCurrentSolarSystemIfAny(self):
        if self.currentSolarsystem:
            self.currentSolarsystem.Close()
        self.currentSolarsystem = None

    def LoadSolarSystemDetails(self, solarSystemID):
        current = self.currentSolarsystem
        if current:
            resetSolarsystemID = current.solarsystemID
        else:
            resetSolarsystemID = None
        self.layoutHandler.AdjustStargateLinesForSolarSystem(solarSystemID)
        if resetSolarsystemID != solarSystemID:
            if current:
                current.Close()
            self.currentSolarsystem = None
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            solarSystemPosition = mapNode.position
            self.currentSolarsystem = SystemMapHandler(self, solarSystemID, scaling=mapViewUtil.ScaleSolarSystemValue(1.0), position=solarSystemPosition)
            self.currentSolarsystem.LoadSolarSystemMap()
            if self.destroyed:
                return
            self.currentSolarsystem.LoadMarkers()
            if self.destroyed:
                return
            scaling = mapViewUtil.ScaleSolarSystemValue(1.0)
            cameraParentTravel = self.GetDistance(self.camera.pointOfInterest, solarSystemPosition)
            if cameraParentTravel:
                uicore.animations.MorphVector3(self.currentSolarsystem.systemMapTransform, 'scaling', (0.0, 0.0, 0.0), (scaling, scaling, scaling), duration=max(0.1, min(1500.0, cameraParentTravel) / 2000.0))
            else:
                self.currentSolarsystem.systemMapTransform.scaling = (scaling, scaling, scaling)

    def LoadBookmarkMarkers(self):
        if not self.destroyed and self.bookmarkHandler:
            self.bookmarkHandler.LoadBookmarkMarkers()

    def LoadLandmarkMarkers(self):
        for landmarkID, landmark in self.mapSvc.GetLandmarks().iteritems():
            if self.destroyed or not self.markersHandler:
                return
            markerObject = self.markersHandler.AddLandmarkMarker(-landmarkID, mapViewUtil.ScaledPosToMapPos(geo2.Vec3Scale(landmark.position, UNIVERSE_SCALE)), landmarkData=landmark)

    def LoadRegionMarkers(self):
        self.LogInfo('LoadRegionMarkers')
        for regionID, regionItem in mapViewData.GetKnownUniverseRegions().iteritems():
            if IsWormholeRegion(regionID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            self.markersHandler.AddRegionMarker(regionID, regionItem.mapPosition)
            blue.pyos.BeNice(100)

    def LoadConstellationMarkers(self):
        for constellationID, constellationItem in mapViewData.GetKnownUniverseConstellations().iteritems():
            if IsWormholeConstellation(constellationID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            self.markersHandler.AddConstellationMarker(constellationID, constellationItem.mapPosition)
            blue.pyos.BeNice(100)

    def LoadSolarSystemMarkers(self):
        for solarSystemID, solarSystemItem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            if IsWormholeConstellation(solarSystemID):
                continue
            if self.destroyed or not self.markersHandler:
                return
            mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
            self.markersHandler.AddSolarSystemMarker(solarSystemID, mapNode.position)
            blue.pyos.BeNice(100)

    def GetLineIDForJumpBetweenSystems(self, fromSystemID, toSystemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(fromSystemID)
        if mapNode:
            for lineData in mapNode.lineData:
                if lineData.fromSolarSystemID == toSystemID or lineData.toSolarSystemID == toSystemID:
                    return lineData.lineID

    def GetLineIDsForSolarSystemID(self, solarSystemID):
        mapNode = self.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
        if mapNode:
            return [ lineData.lineID for lineData in mapNode.lineData ]
        return []

    def GetLineIDsForSolarSystemIDs(self, solarSystemIDs):
        result = []
        for solarSystemID in solarSystemIDs:
            result.extend(self.GetLineIDsForSolarSystemID(solarSystemID))

        return result

    def LoadJumpLines(self):
        self.allianceJumpLines = []
        self.jumpLineInfoByLineID = {}
        lineSet = self.solarSystemJumpLineSet
        defaultColor = (0, 0, 0, 0)
        defaultPos = (0, 0, 0)
        for lineData in mapViewData.IterateJumps():
            lineID = lineSet.AddStraightLine(defaultPos, defaultColor, defaultPos, defaultColor, mapViewConst.JUMPLINE_BASE_WIDTH)
            lineData.lineID = lineID
            self.jumpLineInfoByLineID[lineID] = lineData
            fromNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.fromSolarSystemID)
            fromNode.AddLineData(lineData)
            toNode = self.layoutHandler.GetNodeBySolarSystemID(lineData.toSolarSystemID)
            toNode.AddLineData(lineData)

    def LoadAllianceJumpLines(self):
        if not hasattr(session, 'allianceid') or session.allianceid is None:
            return
        mapRemoteSvc = sm.RemoteSvc('map')
        bridgesByLocation = mapRemoteSvc.GetAllianceJumpBridges()
        jumpBridgeColor = JUMPBRIDGE_COLOR
        defaultPos = (0, 0, 0)
        lineSet = self.solarSystemJumpLineSet
        for jumpFromSystemID, jumpToSystemID in bridgesByLocation:
            if not IsSolarSystem(jumpToSystemID) or not IsSolarSystem(jumpFromSystemID):
                self.LogWarn("DrawAllianceJumpLines had entry that wasn't a solarsystem:", jumpToSystemID, jumpFromSystemID)
                continue
            lineID = lineSet.AddCurvedLineCrt(defaultPos, jumpBridgeColor, defaultPos, jumpBridgeColor, defaultPos, 3)
            lineData = mapViewData.PrimeJumpData(jumpFromSystemID, jumpToSystemID, JUMPBRIDGE_TYPE)
            lineData.lineID = lineID
            self.allianceJumpLines.append(lineID)
            self.jumpLineInfoByLineID[lineID] = lineData
            fromNode = self.layoutHandler.GetNodeBySolarSystemID(jumpFromSystemID)
            fromNode.AddLineData(lineData)
            toNode = self.layoutHandler.GetNodeBySolarSystemID(jumpToSystemID)
            toNode.AddLineData(lineData)

    def SetExtraLineMapping(self, lineMapping):
        self.extraLineMapping = lineMapping

    def RefreshLines(self):
        self.dirtyLineIDs = set()
        self._UpdateLines(hint='RefreshLines')

    def UpdateLines(self, hint = '', **kwds):
        self.linesUpdateTimer = AutoTimer(100, self._UpdateLines, hint)

    def _UpdateLines(self, hint = '', **kwds):
        if self.destroyed:
            return
        self.linesUpdateTimer = None
        self.LogInfo('MapView UpdateLines ' + hint)
        lineMode = GetMapViewSetting(VIEWMODE_LINES_SETTINGS, self.mapViewID)
        if lineMode != self.lineMode:
            self.dirtyLineIDs = set()
            self.lineMode = lineMode
        active = self.activeObjects
        maxAlpha = 0.9
        lineAlpha = {}
        if lineMode == VIEWMODE_LINES_NONE:
            baseLineAlphaModulate = 0.0
        else:
            hiliteID = self.hilightID
            if hiliteID is None:
                hiliteID = active.solarSystemID or active.constellationID or active.regionID
            if lineMode == VIEWMODE_LINES_ALL:
                baseLineAlphaModulate = maxAlpha * 0.25
            else:
                baseLineAlphaModulate = 0.0
                if active.regionID and lineMode in (VIEWMODE_LINES_SELECTION_REGION, VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS) and not IsWormholeRegion(active.regionID):
                    regionsToShow = [active.regionID]
                    if lineMode == VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS:
                        regionsToShow = regionsToShow + mapViewData.GetKnownRegion(active.regionID).neighbours
                    solarSystemIDs = self.mapSvc.ExpandItems(regionsToShow)
                    lineIDs = self.GetLineIDsForSolarSystemIDs(solarSystemIDs)
                    for each in lineIDs:
                        lineAlpha[each] = maxAlpha / 2

            if IsSolarSystem(hiliteID) and not IsWormholeSystem(hiliteID):
                lineIDs = self.GetLineIDsForSolarSystemID(hiliteID)
                for each in lineIDs:
                    lineAlpha[each] = maxAlpha

                hiliteItem = mapViewData.GetKnownSolarSystem(hiliteID)
                lineIDs = self.GetLineIDsForSolarSystemIDs(hiliteItem.neighbours)
                for each in lineIDs:
                    lineAlpha[each] = maxAlpha

            elif IsConstellation(hiliteID) and not IsWormholeConstellation(hiliteID):
                hiliteItem = mapViewData.GetKnownConstellation(hiliteID)
                lineIDs = self.GetLineIDsForSolarSystemIDs(hiliteItem.solarSystemIDs)
                for each in lineIDs:
                    lineAlpha[each] = maxAlpha

            elif IsRegion(hiliteID) and not IsWormholeRegion(hiliteID):
                hiliteItem = mapViewData.GetKnownRegion(hiliteID)
                lineIDs = self.GetLineIDsForSolarSystemIDs(hiliteItem.solarSystemIDs)
                for each in lineIDs:
                    lineAlpha[each] = maxAlpha

        showAllianceLines = GetMapViewSetting(VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS, self.mapViewID)
        for lineID in self.allianceJumpLines:
            lineAlpha[lineID] = maxAlpha if showAllianceLines else 0.0

        self.UpdateLineColorData(lineAlpha, baseLineAlphaModulate)
        if self.jumpRouteHighlightID:
            self.UpdateHighlightJumpRoute()
        self.UpdateAutopilotJumpRoute()
        self.solarSystemJumpLineSet.SubmitChanges()
        self.extraJumpLineSet.SubmitChanges()

    def ChangeLineColor(self, lineSet, lineID, color, opacity = 1.0):
        if len(color) == 2:
            fromColor = self.ModulateAlpha(color[0], opacity)
            toColor = self.ModulateAlpha(color[1], opacity)
        else:
            fromColor = toColor = self.ModulateAlpha(color, opacity)
        lineSet.ChangeLineColor(lineID, fromColor, toColor)

    def ModulateAlpha(self, color, alphaModulate):
        if len(color) == 3:
            r, g, b = color
            return (r,
             g,
             b,
             alphaModulate)
        r, g, b, a = color
        return (r,
         g,
         b,
         a * alphaModulate)

    def UpdateLineColorData(self, lineAlphaByLineID, baseLineAlphaModulate):
        lineSet = self.solarSystemJumpLineSet
        newLines = set(lineAlphaByLineID.keys())
        if not self.dirtyLineIDs:
            updateLinesIDs = self.jumpLineInfoByLineID.keys()
        else:
            updateLinesIDs = newLines.union(self.dirtyLineIDs)
        self.dirtyLineIDs = newLines
        ModulateAlpha = self.ModulateAlpha
        for lineID in updateLinesIDs:
            lineData = self.jumpLineInfoByLineID[lineID]
            if lineID in self.allianceJumpLines:
                fromColor = toColor = JUMPBRIDGE_COLOR
            else:
                fromColor = self.starColorByID.get(lineData.fromSolarSystemID, NEUTRAL_COLOR)
                toColor = self.starColorByID.get(lineData.toSolarSystemID, NEUTRAL_COLOR)
            lineOpacity = lineAlphaByLineID.get(lineID, baseLineAlphaModulate)
            fromColor = ModulateAlpha(fromColor, lineOpacity)
            toColor = ModulateAlpha(toColor, lineOpacity)
            if self.extraLineMapping and lineID in self.extraLineMapping:
                extraLineData = self.extraLineMapping[lineID]
                self.extraJumpLineSet.ChangeLineColor(extraLineData.startLineID, fromColor, fromColor)
                self.extraJumpLineSet.ChangeLineColor(extraLineData.arcLineID, fromColor, toColor)
                self.extraJumpLineSet.ChangeLineColor(extraLineData.endLineID, toColor, toColor)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.startLineID, mapViewConst.JUMPLINE_BASE_WIDTH)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.arcLineID, mapViewConst.JUMPLINE_BASE_WIDTH)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.endLineID, mapViewConst.JUMPLINE_BASE_WIDTH)
                if lineData.jumpType == mapcommon.REGION_JUMP:
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.startLineID, (0, 0, 0, 1), 0.0, extraLineData.startLineLength / mapViewConst.REGION_LINE_TICKSIZE)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.arcLineID, (0, 0, 0, 1), 0.0, extraLineData.arcLineLength / mapViewConst.REGION_LINE_TICKSIZE)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.endLineID, (0, 0, 0, 1), 0.0, extraLineData.endLineLength / mapViewConst.REGION_LINE_TICKSIZE)
                elif lineData.jumpType == mapcommon.CONSTELLATION_JUMP:
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.startLineID, (0, 0, 0, 1), 0.0, extraLineData.startLineLength / mapViewConst.CONSTELLATION_LINE_TICKSIZE)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.arcLineID, (0, 0, 0, 1), 0.0, extraLineData.arcLineLength / mapViewConst.CONSTELLATION_LINE_TICKSIZE)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.endLineID, (0, 0, 0, 1), 0.0, extraLineData.endLineLength / mapViewConst.CONSTELLATION_LINE_TICKSIZE)
                else:
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.startLineID, (0, 0, 0, 0), 0.0, 1.0)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.arcLineID, (0, 0, 0, 0), 0.0, 1.0)
                    self.extraJumpLineSet.ChangeLineAnimation(extraLineData.endLineID, (0, 0, 0, 0), 0.0, 1.0)
                fromColor = toColor = (0, 0, 0, 0)
            lineSet.ChangeLineColor(lineID, fromColor, toColor)
            lineSet.ChangeLineWidth(lineID, mapViewConst.JUMPLINE_BASE_WIDTH)
            if lineData.jumpType == mapcommon.REGION_JUMP:
                lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(lineData.fromSolarSystemID, lineData.toSolarSystemID)
                lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1), 0.0, lineLength / mapViewConst.REGION_LINE_TICKSIZE)
            elif lineData.jumpType == mapcommon.CONSTELLATION_JUMP:
                lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(lineData.fromSolarSystemID, lineData.toSolarSystemID)
                lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1), 0.0, lineLength / mapViewConst.CONSTELLATION_LINE_TICKSIZE)
            else:
                lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 0), 0.0, 1.0)

    def GetSystemColorBasedOnSecRating(self, ssID, alpha = 2.0):
        ss = self.mapSvc.GetSecurityStatus(ssID)
        c = FmtSystemSecStatus(ss, 1)[1]
        return (c.r,
         c.g,
         c.b,
         alpha)

    def UpdateHighlightJumpRoute(self):
        targetID = self.jumpRouteHighlightID
        self.LogInfo('MapView.UpdateHighlightJumpRoute', targetID)
        if targetID in [session.solarsystemid2, session.constellationid, session.regionid]:
            return []
        routeList = sm.GetService('starmap').ShortestGeneralPath(targetID)
        if not len(routeList):
            return
        GetSystemColorBasedOnSecRating = self.GetSystemColorBasedOnSecRating
        lineSet = self.solarSystemJumpLineSet
        for i in xrange(len(routeList) - 1):
            fromID = routeList[i]
            toID = routeList[i + 1]
            lineID = self.GetLineIDForJumpBetweenSystems(fromID, toID)
            if lineID is None:
                continue
            jumpLineInfo = self.jumpLineInfoByLineID[lineID]
            self.dirtyLineIDs.add(lineID)
            if fromID == jumpLineInfo.fromSolarSystemID:
                fromColor = GetSystemColorBasedOnSecRating(fromID)
                toColor = GetSystemColorBasedOnSecRating(toID)
            else:
                fromColor = GetSystemColorBasedOnSecRating(toID)
                toColor = GetSystemColorBasedOnSecRating(fromID)
            lineSet.ChangeLineColor(lineID, fromColor, toColor)
            lineSet.ChangeLineWidth(lineID, mapViewConst.AUTOPILOT_LINE_WIDTH)
            lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(fromID, toID)
            if lineLength:
                segmentScale = lineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
                lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 1.0), 0.0, segmentScale)

    def UpdateAutopilotJumpRoute(self):
        GetSystemColorBasedOnSecRating = self.GetSystemColorBasedOnSecRating
        starmapSvc = sm.GetService('starmap')
        destinationPath = starmapSvc.GetDestinationPath()
        if destinationPath and destinationPath[0] != session.solarsystemid2:
            destinationPath = [session.solarsystemid2] + destinationPath
        lineSet = self.solarSystemJumpLineSet
        for i in xrange(len(destinationPath) - 1):
            fromID = destinationPath[i]
            toID = destinationPath[i + 1]
            lineID = self.GetLineIDForJumpBetweenSystems(fromID, toID)
            if lineID is None:
                continue
            jumpLineInfo = self.jumpLineInfoByLineID[lineID]
            self.dirtyLineIDs.add(lineID)
            if fromID == jumpLineInfo.fromSolarSystemID:
                fromColor = GetSystemColorBasedOnSecRating(fromID)
                toColor = GetSystemColorBasedOnSecRating(toID)
                animationDirection = -1
            else:
                fromColor = GetSystemColorBasedOnSecRating(toID)
                toColor = GetSystemColorBasedOnSecRating(fromID)
                animationDirection = 1
            if self.extraLineMapping and lineID in self.extraLineMapping:
                extraLineData = self.extraLineMapping[lineID]
                self.extraJumpLineSet.ChangeLineColor(extraLineData.startLineID, fromColor, fromColor)
                self.extraJumpLineSet.ChangeLineColor(extraLineData.arcLineID, fromColor, toColor)
                self.extraJumpLineSet.ChangeLineColor(extraLineData.endLineID, toColor, toColor)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.startLineID, mapViewConst.AUTOPILOT_LINE_WIDTH)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.arcLineID, mapViewConst.AUTOPILOT_LINE_WIDTH)
                self.extraJumpLineSet.ChangeLineWidth(extraLineData.endLineID, mapViewConst.AUTOPILOT_LINE_WIDTH)
                segmentScale = extraLineData.startLineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
                animationSpeed = mapViewConst.AUTOPILOT_LINE_ANIM_SPEED / segmentScale * animationDirection
                self.extraJumpLineSet.ChangeLineAnimation(extraLineData.startLineID, (0, 0, 0, 0.75), animationSpeed, segmentScale)
                segmentScale = extraLineData.arcLineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
                animationSpeed = mapViewConst.AUTOPILOT_LINE_ANIM_SPEED / segmentScale * animationDirection
                self.extraJumpLineSet.ChangeLineAnimation(extraLineData.arcLineID, (0, 0, 0, 0.75), animationSpeed, segmentScale)
                segmentScale = extraLineData.endLineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
                animationSpeed = mapViewConst.AUTOPILOT_LINE_ANIM_SPEED / segmentScale * animationDirection
                self.extraJumpLineSet.ChangeLineAnimation(extraLineData.endLineID, (0, 0, 0, 0.75), animationSpeed, segmentScale)
                continue
            lineSet.ChangeLineColor(lineID, fromColor, toColor)
            lineSet.ChangeLineWidth(lineID, mapViewConst.AUTOPILOT_LINE_WIDTH)
            lineLength = self.layoutHandler.GetDistanceBetweenSolarSystems(fromID, toID)
            if lineLength:
                segmentScale = lineLength / mapViewConst.AUTOPILOT_LINE_TICKSIZE
                animationSpeed = mapViewConst.AUTOPILOT_LINE_ANIM_SPEED / segmentScale * animationDirection
                lineSet.ChangeLineAnimation(lineID, (0, 0, 0, 0.75), animationSpeed, segmentScale)

    def SetViewColorMode(self, colorMode, updateColorMode = True):
        if colorMode in mapcommon.oldColorModeToNewColorMode:
            colorMode = mapcommon.oldColorModeToNewColorMode[colorMode]
        SetMapViewSetting(VIEWMODE_COLOR_SETTINGS, colorMode, self.mapViewID)
        if updateColorMode:
            self.UpdateMapViewColorMode()

    def UpdateMapViewColorMode(self):
        colorMode = GetMapViewSetting(VIEWMODE_COLOR_SETTINGS, self.mapViewID)
        self.starLegend = []
        mode = colorMode[0] if isinstance(colorMode, tuple) else colorMode
        definition = colorHandler.GetFormatFunction(mode)
        if not definition:
            self.LogWarn('MapView.UpdateMapViewColorMode, format function not found for colorMode', colorMode)
            return
        colorInfo = KeyVal(solarSystemDict={}, colorList=None, legend=set(), colorType=colorHandler.STAR_COLORTYPE_PASSIVE)
        loadArguments = definition.loadArguments or ()
        definition.loadFunction(colorInfo, colorMode, *loadArguments)
        if self.destroyed:
            return
        self.colorModeInfoPanel.LoadColorModeInfo(colorMode, definition, colorInfo)
        self.starLegend = list(colorInfo.legend)
        self.ApplyStarColors(colorInfo)
        self.RefreshLines()
        self.markersHandler.RefreshActiveAndHilightedMarkers()

    def GetColorCurve(self, colorList):
        colorCurve = trinity.TriColorCurve()
        black = trinity.TriColor()
        colorListDivisor = float(len(colorList) - 1)
        for colorID, colorValue in enumerate(colorList):
            time = float(colorID) / colorListDivisor
            colorCurve.AddKey(time, colorValue, black, black, trinity.TRIINT_LINEAR)

        colorCurve.Sort()
        colorCurve.extrapolation = trinity.TRIEXT_CONSTANT
        colorCurve.start = 0L
        return colorCurve

    def GetColorCurveValue(self, colorCurve, time):
        return colorCurve.GetColorAt(long(const.SEC * time))

    def ApplyStarColors(self, colorInfo):
        self.starData = {}
        self.starColorByID = {}
        solarSystemDict = colorInfo.solarSystemDict
        colorList = colorInfo.colorList
        colorCurve = self.GetColorCurve(colorList or self.GetDefaultColorList())
        if colorInfo.colorType == colorHandler.STAR_COLORTYPE_DATA:
            self.starDataTexture.resourcePath = PARTICLE_SPRITE_DATA_TEXTURE
        else:
            self.starDataTexture.resourcePath = PARTICLE_SPRITE_HEAT_TEXTURE
        neutralStarSize = STAR_SIZE / 8
        particleSystem = self.starParticles
        for particleID, mapNode in self.layoutHandler.GetNodesByParticleID().iteritems():
            solarSystemID = mapNode.solarSystemID
            if solarSystemID in solarSystemDict:
                sizeNormalized, colorPositionNormalized, commentCallback, uniqueColor = solarSystemDict[solarSystemID]
                if colorInfo.colorType == colorHandler.STAR_COLORTYPE_DATA:
                    starSize = STAR_SIZE * sizeNormalized * 8.0
                else:
                    starSize = STAR_SIZE * sizeNormalized
                if uniqueColor is None and colorPositionNormalized is not None:
                    col = self.GetColorCurveValue(colorCurve, colorPositionNormalized)
                else:
                    col = uniqueColor
                if commentCallback:
                    self.starData[particleID] = commentCallback
                try:
                    starColor = (col.r,
                     col.g,
                     col.b,
                     col.a)
                except:
                    starColor = col

            else:
                starColor = NEUTRAL_COLOR
                starSize = neutralStarSize
            self.starColorByID[solarSystemID] = starColor
            particleSystem.SetItemElement(particleID, 2, starSize)
            particleSystem.SetItemElement(particleID, 3, starColor)

        particleSystem.UpdateData()
        self.mapStars.display = 1

    def GetDefaultColorList(self):
        return [trinity.TriColor(1.0, 0.0, 0.0, 1.0), trinity.TriColor(1.0, 1.0, 0.0, 1.0), trinity.TriColor(0.0, 1.0, 0.0, 1.0)]

    def GetLegend(self, name):
        return getattr(self, name + 'Legend', [])

    def StartLoadingBar(self, key, tile, action, total):
        pass

    def UpdateLoadingBar(self, key, tile, action, part, total):
        pass

    def StopLoadingBar(self, key):
        pass

    def OnAutopilotUpdated(self):
        self.UpdateLines(hint='OnAutopilotUpdated')

    def OnDestinationSet(self, *args, **kwds):
        self.UpdateLines(hint='OnDestinationSet')

    def OnHomeStationChanged(self, *args, **kwds):
        self.ShowMyHomeStation()

    def OnBallparkSetState(self, *args):
        if session.solarsystemid2:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers()
            self.layoutHandler.ClearCache()
            self.RefreshActiveState()

    def OnSessionChanged(self, isRemote, session, change):
        if 'locationid' in change and not IsSolarSystem(change['locationid'][1]):
            uthread.new(self.ShowMyLocation)

    def DoBallClear(self, solitem):
        self.RemoveMyLocation()

    def DoBallsAdded(self, balls_slimItems, *args, **kw):
        for ball, slimItem in balls_slimItems:
            if ball.id == session.shipid:
                uthread.new(self.ShowMyLocation)
                break

    def UpdateViewPort(self):
        if self.sceneContainer:
            self.sceneContainer.UpdateViewPort()
        if self.solarSystemStandalone:
            self.solarSystemStandalone.UpdateViewPort()
