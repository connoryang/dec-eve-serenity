#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewSolarSystem.py
import logging
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared.mapView.mapViewBookmarkHandler import MapViewBookmarkHandler
from eve.client.script.ui.shared.mapView.mapViewScannerNavigationStandalone import MapViewScannerNavigation
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyHome import MarkerMyHome
from eve.client.script.ui.shared.mapView.markers.mapMarkerMyLocation import MarkerMyLocation
from eve.client.script.ui.shared.mapView.markers.mapMarkersHandler import MapViewMarkersHandler
from eve.client.script.ui.shared.mapView.mapViewSceneContainer import MapViewSceneContainer
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos, ScaleSolarSystemValue, GetTranslationFromParentWithRadius, UpdateDebugOutput
from eve.client.script.ui.shared.mapView.systemMapHandler import SystemMapHandler, SolarSystemInfoBox
import blue
from eve.common.script.sys.idCheckers import IsSolarSystem
from inventorycommon.util import IsWormholeSystem
import trinity
import uthread
import fleetbr
import nodemanager
from carbonui.control.menuLabel import MenuLabel
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_MYPOS, MARKERID_MYHOME, VIEWMODE_MARKERS_SETTINGS, SETTING_PREFIX
import geo2
import carbonui.const as uiconst
import localization
log = logging.getLogger(__name__)
SUNBASE = 7.5
LINE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines3DStarMapNew.fx'
PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/mapStarNew5.dds'
PARTICLE_SPRITE_HEAT_TEXTURE = 'res:/Texture/Particle/mapStarNewHeat.dds'
DISTANCE_RANGE = 'distanceRange'
NEUTRAL_COLOR = (0.25, 0.25, 0.25, 1.0)
HEX_TILE_SIZE = 60

class MapViewSolarSystem(Container):
    __notifyevents__ = ['OnUIScalingChange',
     'OnAutopilotUpdated',
     'OnDestinationSet',
     'OnSessionChanged',
     'OnBallparkSetState',
     'DoBallClear',
     'DoBallsAdded']
    curveSet = None
    systemMap = None
    mapRoot = None
    infoBox = None
    markersHandler = None
    bookmarkHandler = None
    markersAlwaysVisible = set()
    inFocus = False
    currentSolarsystem = None
    hilightID = None
    mapViewID = None
    sceneBlendMode = None
    showSolarSystemNebula = True
    showStarfield = True
    showDebugInfo = False
    showInfobox = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.mapSvc = sm.GetService('map')
        self.mapViewID = attributes.mapViewID
        self.autoFocusEnabled = settings.char.ui.Get('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        innerPadding = attributes.innerPadding or 0
        self.infoLayer = Container(parent=self, clipChildren=True, name='infoLayer', padding=innerPadding)
        if attributes.showCloseButton:
            ButtonIcon(parent=self.infoLayer, hint=localization.GetByLabel('UI/Generic/Close'), texturePath='res:/UI/Texture/classes/DockPanel/closeButton.png', func=attributes.closeFunction or self.Close, align=uiconst.TOPRIGHT)
        self.showInfobox = attributes.Get('showInfobox', self.showInfobox)
        if self.showInfobox:
            self.infoBox = SolarSystemInfoBox(parent=self.infoLayer, align=uiconst.TOPLEFT, left=32, top=32)
        navigationClass = attributes.Get('navigationClass', MapViewScannerNavigation)
        navigationPadding = attributes.Get('navigationPadding', (0, 32, 0, 0))
        self.mapNavigation = navigationClass(parent=self, align=uiconst.TOALL, state=uiconst.UI_NORMAL, mapView=self, padding=navigationPadding)
        sceneContainer = MapViewSceneContainer(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=innerPadding)
        sceneContainer.Startup()
        self.sceneContainer = sceneContainer
        self.sceneContainer.display = False
        scene = trinity.EveSpaceScene()
        self.showSolarSystemNebula = attributes.Get('showSolarSystemNebula', self.showSolarSystemNebula)
        if self.showSolarSystemNebula:
            scene.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
            scene.backgroundRenderingEnabled = True
        self.showStarfield = attributes.Get('showStarfield', self.showStarfield)
        if self.showStarfield:
            scene.starfield = trinity.Load('res:/dx9/scene/starfield/spritestars.red')
            scene.backgroundRenderingEnabled = True
        self.mapRoot = trinity.EveRootTransform()
        self.mapRoot.name = 'mapRoot'
        scene.objects.append(self.mapRoot)
        self.sceneBlendMode = attributes.Get('sceneBlendMode', self.sceneBlendMode)
        self.sceneContainer.scene = scene
        self.sceneContainer.DisplaySpaceScene(blendMode=self.sceneBlendMode)
        self.markersHandler = MapViewMarkersHandler(self, self.sceneContainer.bracketCurveSet, self.infoLayer, eventHandler=self.mapNavigation, stackMarkers=attributes.Get('stackMarkers', True))
        self.bookmarkHandler = MapViewBookmarkHandler(self)
        self.showDebugInfo = attributes.Get('showDebugInfo', self.showDebugInfo)
        if self.showDebugInfo:
            self.debugOutput = EveLabelSmall(parent=self, align=uiconst.BOTTOMLEFT, left=6, top=6, idx=0)
            self.debugOutputTimer = AutoTimer(5, self.UpdateDebugOutput)
        self.camera.fieldOfView = 0.7
        self.camera.minDistance = 0.5
        self.camera.maxDistance = 8000.0
        self.camera.frontClip = 0.1
        self.camera.backClip = 50000.0
        self.camera.LoadRegisteredCameraSettings(self.mapViewID)
        self.camera.SetCallback(self.OnCameraMoved)
        sm.RegisterNotify(self)
        uthread.new(uicore.registry.SetFocus, self)

    def Close(self, *args, **kwds):
        self.camera.RegisterCameraSettings(self.mapViewID)
        if hasattr(self, 'mapRoot') and self.mapRoot is not None:
            del self.mapRoot.children[:]
        self.mapRoot = None
        if self.currentSolarsystem:
            self.currentSolarsystem.RemoveFromScene()
        self.currentSolarsystem = None
        if self.camera:
            self.camera.Close()
        self.camera = None
        if self.markersHandler:
            self.markersHandler.StopHandler()
        self.markersHandler = None
        if self.bookmarkHandler:
            self.bookmarkHandler.StopHandler()
        self.bookmarkHandler = None
        self.mapNavigation = None
        self.debugOutputTimer = None
        Container.Close(self, *args, **kwds)

    def UpdateDebugOutput(self):
        if self.destroyed:
            return
        UpdateDebugOutput(self.debugOutput, camera=self.camera, mapView=self)

    def SetFocusState(self, focusState):
        self.inFocus = focusState

    def SetHilightItem(self, itemID):
        hilightID = itemID
        if self.hilightID != hilightID:
            self.hilightID = hilightID
            if hilightID:
                self.markersHandler.HilightMarkers([hilightID])
            else:
                self.markersHandler.HilightMarkers([])

    def OnMapViewSettingChanged(self, settingKey, *args, **kwds):
        if settingKey == VIEWMODE_MARKERS_SETTINGS:
            if self.currentSolarsystem:
                self.currentSolarsystem.LoadMarkers(showChanges=True)

    def FocusSelf(self, *args, **kwds):
        self.EnableAutoFocus()
        self.SetActiveItemID((MARKERID_MYPOS, session.charid))

    def EnableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), True)
        self.autoFocusEnabled = True

    def DisableAutoFocus(self):
        settings.char.ui.Set('%s_autoFocusEnabled_%s' % (SETTING_PREFIX, self.mapViewID), False)
        self.autoFocusEnabled = False
        self.camera.FollowMarker(None)

    @apply
    def solarSystemTransform():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.systemMapTransform

        return property(**locals())

    @apply
    def solarSystemSunID():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.sunID

        return property(**locals())

    @apply
    def camera():

        def fget(self):
            if self.sceneContainer:
                return self.sceneContainer.camera

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def scene():

        def fget(self):
            return self.sceneContainer.scene

        return property(**locals())

    @apply
    def solarSystemID():

        def fget(self):
            if self.currentSolarsystem:
                return self.currentSolarsystem.solarsystemID

        def fset(self, value):
            pass

        return property(**locals())

    def LogError(self, *args, **kwds):
        log.error('MAPVIEW ' + repr(args))

    def LogInfo(self, *args, **kwds):
        log.info('MAPVIEW ' + repr(args))

    def LogWarn(self, *args, **kwds):
        log.warning('MAPVIEW ' + repr(args))

    def OnUIScalingChange(self, *args):
        self.markersHandler.ReloadAll()

    def GetItemMenu(self, itemID):
        item = self.mapSvc.GetItem(itemID, retall=True)
        if not item:
            return []
        m = []
        m.append(None)
        filterFunc = [MenuLabel('UI/Commands/ShowLocationOnMap')]
        m += sm.GetService('menu').CelestialMenu(itemID, noTrace=1, mapItem=item, filterFunc=filterFunc)
        return m

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
        if self.destroyed:
            return
        if stationInfo.solarSystemID != self.currentSolarsystem.solarsystemID:
            return
        localPosition = SolarSystemPosToMapPos((stationInfo.x, stationInfo.y, stationInfo.z))
        markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyHome, stationInfo=stationInfo, solarSystemID=stationInfo.solarSystemID, mapPositionLocal=localPosition, mapPositionSolarSystem=(0, 0, 0))
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

        if self.solarSystemID == session.solarsystemid2:
            if session.stationid:
                stationInfo = self.mapSvc.GetStation(session.stationid)
                if self.destroyed:
                    return
                localPosition = SolarSystemPosToMapPos((stationInfo.x, stationInfo.y, stationInfo.z))
                markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, solarSystemID=session.solarsystemid2, mapPositionLocal=localPosition, mapPositionSolarSystem=(0, 0, 0))
            else:
                markerObject = self.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerMyLocation, trackObjectID=session.shipid or session.stationid, solarSystemID=session.solarsystemid2, mapPositionLocal=(0, 0, 0), mapPositionSolarSystem=(0, 0, 0))
            self.markersAlwaysVisible.add(markerID)
            if self.autoFocusEnabled:
                self.FocusSelf()

    def OnCameraMoved(self):
        camera = self.camera
        if camera is None:
            return
        if self.currentSolarsystem:
            self.currentSolarsystem.OnCameraMoved()
        cameraDistance = camera.GetCameraDistanceFromInterest()
        if self.markersHandler:
            self.markersHandler.RegisterCameraTranslationFromParent(cameraDistance)

    def SetCameraPointOfInterestSolarSystemPosition(self, solarSystemID, position):
        if solarSystemID != self.solarSystemID:
            return
        self.DisableAutoFocus()
        self.camera.pointOfInterest = SolarSystemPosToMapPos(position)

    def SetActiveItemID(self, itemID, *args, **kwds):
        markerObject = self.markersHandler.GetMarkerByID(itemID)
        if markerObject:
            self.SetActiveMarker(markerObject)

    def SetActiveMarker(self, markerObject, *args, **kwds):
        self.camera.FollowMarker(markerObject)

    def LoadGenericBackdrop(self):
        scene = self.scene
        scene.backgroundEffect = trinity.Load('res:/dx9/scene/starfield/starfieldNebula.red')
        scene.backgroundRenderingEnabled = True
        node = nodemanager.FindNode(scene.backgroundEffect.resources, 'NebulaMap', 'trinity.TriTextureParameter')
        if node is not None:
            node.resourcePath = 'res:/UI/Texture/classes/MapView/backdrop_cube.dds'
        node = nodemanager.FindNode(scene.backgroundEffect.resources, 'StarMap', 'trinity.TriTextureParameter')
        if node is not None:
            node.resourcePath = 'res:/dx9/scene/starfield/Stars01_Tile2_dim.dds'

    def LoadSolarSystemDetails(self, solarSystemID):
        current = getattr(self, 'currentSolarsystem', None)
        if current:
            resetSolarsystemID = current.solarsystemID
        else:
            resetSolarsystemID = None
        if resetSolarsystemID != solarSystemID:
            if current:
                current.Close()
            self.currentSolarsystem = None
            self.currentSolarsystem = SystemMapHandler(self, solarSystemID, scaling=ScaleSolarSystemValue(1.0), position=(0, 0, 0))
            self.currentSolarsystem.LoadSolarSystemMap()
            if self.destroyed:
                return
            self.currentSolarsystem.LoadMarkers()
            if self.destroyed:
                return
            scaling = ScaleSolarSystemValue(1.0)
            self.currentSolarsystem.systemMapTransform.scaling = (scaling, scaling, scaling)
            if self.showSolarSystemNebula:
                node = nodemanager.FindNode(self.scene.backgroundEffect.resources, 'NebulaMap', 'trinity.TriTextureParameter')
                if node is not None:
                    sceneCube = sm.GetService('sceneManager').GetNebulaPathForSystem(solarSystemID)
                    node.resourcePath = sceneCube or 'res:/UI/Texture/classes/MapView/backdrop_cube.dds'
            if IsWormholeSystem(solarSystemID) and self.scene.starfield:
                self.scene.starfield.numStars = 0
            uthread.new(self.ShowMyHomeStation)
            uthread.new(self.ShowMyLocation)
            if self.infoBox:
                self.infoBox.LoadSolarSystemID(solarSystemID)

    def FrameSolarSystem(self):
        radius = ScaleSolarSystemValue(self.currentSolarsystem.solarSystemRadius)
        cameraDistanceFromInterest = GetTranslationFromParentWithRadius(radius, self.camera)
        if cameraDistanceFromInterest:
            self.camera.ZoomToDistance(cameraDistanceFromInterest)
        if not self.autoFocusEnabled:
            self.SetCameraPointOfInterestSolarSystemPosition(session.solarsystemid2, (0, 0, 0))
        self.sceneContainer.display = True

    def GetPickObjects(self, *args, **kwds):
        return None

    def OnAutopilotUpdated(self):
        pass

    def OnDestinationSet(self, *args, **kwds):
        self.ShowMyLocation()

    def OnBallparkSetState(self, *args):
        if self.currentSolarsystem:
            self.currentSolarsystem.LoadMarkers()
            self.ShowMyHomeStation()

    def OnSessionChanged(self, isRemote, session, change):
        if self.currentSolarsystem and not self.destroyed:
            if 'locationid' in change and not IsSolarSystem(change['locationid'][1]):
                self.currentSolarsystem.StopDirectionalScanHandler()
                self.currentSolarsystem.StopProbeHandler()
                self.currentSolarsystem.HideRangeIndicator()
                self.currentSolarsystem.LoadMarkers()
                self.ShowMyHomeStation()
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
