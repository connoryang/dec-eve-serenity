#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\systemMapHandler.py
from carbon.common.script.util.format import FmtDist, FmtAmt
from carbonui.primitives.layoutGrid import LayoutGrid
from eve.client.script.environment.spaceObject.planet import Planet
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.inflight.scannerFiles.directionalScanHandler import MapViewDirectionalScanHandler
from eve.client.script.ui.shared.mapView import mapViewUtil
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_SOLARSYSTEM_CELESTIAL, VIEWMODE_MARKERS_SETTINGS, MARKERID_PROBE
from eve.client.script.ui.shared.mapView.markers.mapMarkerCelestial import MarkerSpaceObject
from eve.client.script.ui.shared.mapView.markers.mapMarkerProbe import MarkerProbe
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos, ScaleSolarSystemValue
from eve.client.script.ui.shared.maps.label import TransformableLabel
from eve.client.script.ui.shared.maps.maputils import GetMyPos
from eve.common.script.util.eveFormat import FmtSystemSecStatus
import evetypes
from localization import GetByLabel
import trinity
import uthread
import evegraphics.settings as gfxsettings
import geo2
import math
import weakref
import inventorycommon.typeHelpers
PLANET_TEXTURE_SIZE = 512

class SystemMapHandler(object):
    scene = None
    probeHandler = None
    directionalScanHandler = None
    localMarkerIDs = None
    cameraTranslationFromParent = None
    solarSystemRadius = None
    sunID = None
    rangeIndicator = None
    _mapView = None

    def __init__(self, mapView, solarsystemID, scaling = 1.0, position = None):
        if mapView:
            self.mapView = mapView
            self.scene = mapView.scene
        self.solarsystemID = solarsystemID
        self.scaling = scaling
        self.systemMapSvc = sm.GetService('systemmap')
        self.localMarkerIDs = set()
        parent = trinity.EveTransform()
        parent.name = 'solarsystem_%s' % solarsystemID
        self.systemMapTransform = parent
        if mapView:
            mapView.mapRoot.children.append(self.systemMapTransform)
        if position:
            self.SetPosition(position)

    def Close(self):
        if self.scene:
            uicore.animations.MorphVector3(self.systemMapTransform, 'scaling', self.systemMapTransform.scaling, (0.0, 0.0, 0.0), duration=0.5, callback=self.RemoveFromScene)
        else:
            self.RemoveFromScene()

    def RemoveFromScene(self):
        mapView = self.mapView
        if mapView and mapView.markersHandler and self.localMarkerIDs:
            for markerID in self.localMarkerIDs:
                mapView.markersHandler.RemoveMarker(markerID)

        self.StopProbeHandler()
        self.StopDirectionalScanHandler()
        if mapView and mapView.mapRoot and self.systemMapTransform in mapView.mapRoot.children:
            mapView.mapRoot.children.remove(self.systemMapTransform)
        self.systemMapTransform = None
        self.scene = None
        self.localMarkerIDs = None

    def OnCameraMoved(self):
        if self.directionalScanHandler:
            self.directionalScanHandler.OnCameraMoved()

    def EnableProbeHandlerStandalone(self):
        self.StopProbeHandler()
        from eve.client.script.ui.shared.mapView.mapViewProbeHandlerStandalone import MapViewProbeHandlerStandalone
        self.probeHandler = MapViewProbeHandlerStandalone(self)
        self.LoadProbeMarkers()

    def StopProbeHandler(self):
        if self.probeHandler:
            self.probeHandler.StopHandler()
        self.probeHandler = None

    def EnableDirectionalScanHandler(self):
        self.StopDirectionalScanHandler()
        self.directionalScanHandler = MapViewDirectionalScanHandler(self)

    def StopDirectionalScanHandler(self):
        if self.directionalScanHandler:
            self.directionalScanHandler.StopHandler()
        self.directionalScanHandler = None

    @apply
    def mapView():

        def fget(self):
            if self._mapView:
                return self._mapView()

        def fset(self, value):
            if value:
                self._mapView = weakref.ref(value)
            else:
                self._mapView = None

        return property(**locals())

    @apply
    def markersHandler():

        def fget(self):
            mapView = self.mapView
            if mapView:
                return mapView.markersHandler

        def fset(self, value):
            pass

        return property(**locals())

    @apply
    def bookmarkHandler():

        def fget(self):
            mapView = self.mapView
            if mapView:
                return mapView.bookmarkHandler

        def fset(self, value):
            pass

        return property(**locals())

    def RegisterCameraTranslationFromParent(self, cameraTranslationFromParent):
        self.cameraTranslationFromParent = cameraTranslationFromParent
        if self.probeHandler and self.solarSystemRadius:
            radius = ScaleSolarSystemValue(self.solarSystemRadius)
            camangle = 0.5
            translationFromParent = radius / math.sin(camangle) * math.cos(camangle) * 16
            if cameraTranslationFromParent > translationFromParent:
                self.probeHandler.Hide()
            else:
                self.probeHandler.Show()

    def SetPosition(self, position):
        self.position = position
        self.systemMapTransform.translation = self.position

    def LoadCelestials(self):
        groups, solarsystemData = self.systemMapSvc.GetSolarsystemHierarchy(self.solarsystemID)
        for transform in self.systemMapTransform.children:
            try:
                itemID = int(transform.name)
                itemData = solarsystemData[itemID]
            except:
                continue

            if itemData.groupID == const.groupPlanet:
                planetTransform = self.LoadPlanet(itemData.typeID, itemID)
                scaling = self.scaling
                planetTransform.scaling = (1 / scaling * 0.1, 1 / scaling * 0.1, 1 / scaling * 0.1)
                planetTransform.translation = transform.translation

    def ShowRangeIndicator(self):
        self.LoadRangeIndicator()

    def HideRangeIndicator(self):
        if self.rangeIndicator:
            uicore.animations.MorphVector3(self.rangeIndicator.rootTransform, 'scaling', startVal=self.rangeIndicator.rootTransform.scaling, endVal=(0, 0, 0), duration=0.2, callback=self._RemoveRangeIndicator)

    def _RemoveRangeIndicator(self):
        if self.rangeIndicator and self.rangeIndicator.rootTransform in self.systemMapTransform.children:
            self.rangeIndicator.systemMapTransform.children.remove(self.rangeIndicator.rootTransform)
        self.rangeIndicator = None

    def LoadRangeIndicator(self):
        self.HideRangeIndicator()
        rangeIndicator = RangeIndicator(self.systemMapTransform, contextScaling=1.0 / const.AU)
        uicore.animations.MorphVector3(rangeIndicator.rootTransform, 'scaling', startVal=(0, 0, 0), endVal=(const.AU, const.AU, const.AU), duration=0.4)
        self.rangeIndicator = rangeIndicator
        self.SetupMyPositionTracker(rangeIndicator.rootTransform)

    def LoadPlanet(self, planetTypeID, planetID):
        planet = Planet()
        graphicFile = inventorycommon.typeHelpers.GetGraphicFile(planetTypeID)
        planet.typeData['graphicFile'] = graphicFile
        planet.typeID = planetTypeID
        planet.LoadPlanet(planetID, forPhotoService=True, rotate=False, hiTextures=True)
        if planet.model is None or planet.model.highDetail is None:
            return
        planetTransform = trinity.EveTransform()
        planetTransform.name = 'planet'
        planetTransform.children.append(planet.model.highDetail)
        renderTarget, size = self.CreateRenderTarget()
        planet.DoPreProcessEffect(size, None, renderTarget)
        trinity.WaitForResourceLoads()
        for t in planet.model.highDetail.children:
            if t.mesh is not None:
                if len(t.mesh.transparentAreas) > 0:
                    t.sortValueMultiplier = 2.0

        self.systemMapTransform.children.append(planetTransform)
        return planetTransform

    def LoadSolarSystemMap(self):
        self.maxRadius = 0.0
        solarsystemID = self.solarsystemID
        parent = self.systemMapTransform
        solarSystemData = self.systemMapSvc.GetSolarsystemData(solarsystemID)
        planets = []
        childrenToParentByID = {}
        sunID = None
        maxRadius = 0.0
        for celestialObject in solarSystemData:
            if celestialObject.groupID == const.groupPlanet:
                planets.append((celestialObject.itemID, geo2.Vector(celestialObject.x, celestialObject.y, celestialObject.z)))
                maxRadius = max(maxRadius, geo2.Vec3Length((celestialObject.x, celestialObject.y, celestialObject.z)))
            elif celestialObject.groupID == const.groupSun:
                sunID = celestialObject.itemID
                sunGraphic = cfg.graphics.Get(evetypes.GetGraphicID(celestialObject.typeID))
                sunGraphicFile = trinity.Load(sunGraphic.graphicFile)
                self.CreateSun(sunGraphicFile)

        self.sunID = sunID
        objectPositions = {}
        for each in solarSystemData:
            objectPositions[each.itemID] = (each.x, each.y, each.z)
            if each.groupID in (const.groupPlanet, const.groupStargate):
                childrenToParentByID[each.itemID] = sunID
                continue
            closest = []
            eachPosition = geo2.Vector(each.x, each.y, each.z)
            maxRadius = max(maxRadius, geo2.Vec3Length(eachPosition))
            for planetID, planetPos in planets:
                diffPos = planetPos - eachPosition
                diffVector = geo2.Vec3Length(diffPos)
                closest.append((diffVector, planetID))

            closest.sort()
            childrenToParentByID[each.itemID] = closest[0][1]

        self.maxRadius = maxRadius
        for each in solarSystemData:
            if each.itemID == each.locationID:
                continue
            if each.groupID == const.groupSecondarySun:
                continue
            if each.groupID == const.groupPlanet:
                self.CreatePlanet((each.x, each.y, each.z))
                OrbitCircle(each.itemID, (each.x, each.y, each.z), objectPositions[sunID], self.systemMapTransform)
            elif each.groupID == const.groupMoon:
                parentID = childrenToParentByID.get(each.itemID, None)
                if parentID:
                    self.CreatePlanet((each.x, each.y, each.z))
                    OrbitCircle(each.itemID, (each.x, each.y, each.z), objectPositions[parentID], self.systemMapTransform)

        self.solarSystemRadius = maxRadius
        cfg.evelocations.Prime(objectPositions.keys(), 0)

    def CreatePlanet(self, planetPosition):
        scaling = 0.01 / mapViewConst.SOLARSYSTEM_SCALE
        planetTransform = trinity.EveTransform()
        planetTransform.name = 'planetTransform'
        planetTransform.scaling = (scaling, scaling, scaling)
        planetTransform.translation = planetPosition
        self.systemMapTransform.children.append(planetTransform)
        planetTransform.useDistanceBasedScale = True
        planetTransform.distanceBasedScaleArg1 = 1.0
        planetTransform.distanceBasedScaleArg2 = 0.0
        planetTransform.mesh = trinity.Tr2Mesh()
        planetTransform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
        planetTransform.modifier = 1
        area = trinity.Tr2MeshArea()
        planetTransform.mesh.additiveAreas.append(area)
        effect = trinity.Tr2Effect()
        effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
        area.effect = effect
        diffuseColor = trinity.Tr2Vector4Parameter()
        diffuseColor.name = 'DiffuseColor'
        effect.parameters.append(diffuseColor)
        diffuseMap = trinity.TriTextureParameter()
        diffuseMap.name = 'DiffuseMap'
        diffuseMap.resourcePath = 'res:/UI/Texture/Classes/MapView/spotSprite.dds'
        effect.resources.append(diffuseMap)

    def CreateSun(self, sunGraphic):

        def GetEffectParameter(effect, parameterName):
            for each in effect.parameters:
                if each.name == parameterName:
                    return each

        scaling = 1.0 / mapViewConst.SOLARSYSTEM_SCALE * 16
        sunTransform = trinity.EveTransform()
        sunTransform.name = 'Sun'
        sunTransform.scaling = (scaling, scaling, scaling)
        sunTransform.useDistanceBasedScale = True
        sunTransform.distanceBasedScaleArg1 = 0.02
        sunTransform.distanceBasedScaleArg2 = 0.1
        self.systemMapTransform.children.append(sunTransform)
        for each in sunGraphic.mesh.additiveAreas:
            if 'flare' not in each.name.lower() and 'rainbow' not in each.name.lower():
                transform = trinity.EveTransform()
                try:
                    size = GetEffectParameter(each.effect, 'Size')
                    transform.scaling = (size.x, size.y, size.z)
                except:
                    continue

                transform.mesh = trinity.Tr2Mesh()
                transform.mesh.geometryResPath = 'res:/Model/Global/zsprite.gr2'
                transform.modifier = 1
                transform.name = each.name
                area = trinity.Tr2MeshArea()
                transform.mesh.additiveAreas.append(area)
                effect = trinity.Tr2Effect()
                effect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/TextureColor.fx'
                area.effect = effect
                diffuseColor = trinity.Tr2Vector4Parameter()
                diffuseColor.name = 'DiffuseColor'
                effect.parameters.append(diffuseColor)
                diffuseColor = diffuseColor
                diffuseMap = trinity.TriTextureParameter()
                diffuseMap.name = 'DiffuseMap'
                diffuseMap.resourcePath = each.effect.resources[0].resourcePath
                effect.resources.append(diffuseMap)
                try:
                    color = GetEffectParameter(each.effect, 'Color')
                    diffuseColor.value = color.value
                except:
                    continue

                sunTransform.children.append(transform)

    def LoadMarkers(self, showChanges = False):
        mapView = self.mapView
        if not mapView or not mapView.markersHandler:
            return
        loadedCelestialMarkers = set()
        loadMarkerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, mapView.mapViewID)
        if self.solarsystemID == session.solarsystemid:
            ballpark = sm.GetService('michelle').GetBallpark()
            for itemID, ball in ballpark.balls.iteritems():
                if ballpark is None:
                    break
                slimItem = ballpark.GetInvItem(itemID)
                if not slimItem:
                    continue
                markerID = (MARKERID_SOLARSYSTEM_CELESTIAL, slimItem.itemID)
                if slimItem.groupID in loadMarkerGroups:
                    markerObject = mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerSpaceObject, celestialData=slimItem, solarSystemID=self.solarsystemID, highlightOnLoad=showChanges, mapPositionLocal=SolarSystemPosToMapPos((ball.x, ball.y, ball.z)), mapPositionSolarSystem=self.position)
                    loadedCelestialMarkers.add(markerID)

        solarSystemData = self.systemMapSvc.GetSolarsystemData(self.solarsystemID)
        for each in solarSystemData:
            markerID = (MARKERID_SOLARSYSTEM_CELESTIAL, each.itemID)
            if markerID in loadedCelestialMarkers:
                continue
            if each.groupID in loadMarkerGroups:
                markerObject = mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerSpaceObject, celestialData=each, solarSystemID=self.solarsystemID, highlightOnLoad=showChanges, mapPositionLocal=SolarSystemPosToMapPos((each.x, each.y, each.z)), mapPositionSolarSystem=self.position)
                loadedCelestialMarkers.add(markerID)

        for markerID in self.localMarkerIDs.copy():
            if markerID[0] != MARKERID_SOLARSYSTEM_CELESTIAL:
                continue
            if markerID not in loadedCelestialMarkers:
                mapView.markersHandler.RemoveMarker(markerID, fadeOut=showChanges)
                self.localMarkerIDs.remove(markerID)

        self.localMarkerIDs.update(loadedCelestialMarkers)
        self.LoadProbeMarkers()
        uthread.new(self.LoadBookmarkMarkers, showChanges)

    def GetMarkerIDs(self):
        return self.localMarkerIDs

    def GetProbeMarkerIDs(self):
        return [ markerID for markerID in self.localMarkerIDs if markerID[0] == MARKERID_PROBE ]

    def LoadBookmarkMarkers(self, showChanges = False):
        loadedMarkerIDs = self.bookmarkHandler.LoadBookmarkMarkers(loadSolarSystemID=self.solarsystemID, showChanges=showChanges)
        self.localMarkerIDs = self.localMarkerIDs.union(loadedMarkerIDs)

    def LoadProbeMarkers(self, *args):
        if not self.probeHandler:
            return
        mapView = self.mapView
        if not mapView:
            return
        currentProbeMarkers = self.GetProbeMarkerIDs()
        scanSvc = sm.GetService('scanSvc')
        probes = scanSvc.GetProbeData()
        loadMarkerGroups = GetMapViewSetting(VIEWMODE_MARKERS_SETTINGS, mapView.mapViewID)
        showProbes = const.groupScannerProbe in loadMarkerGroups
        if showProbes and probes is not None and len(probes) > 0:
            for probe in probes.itervalues():
                markerID = (MARKERID_PROBE, probe.probeID)
                markerObject = mapView.markersHandler.GetMarkerByID(markerID)
                if markerObject:
                    markerObject.UpdateMapPositionLocal(SolarSystemPosToMapPos(probe.pos))
                else:
                    markerObject = mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerProbe, probeData=probe, solarSystemID=self.solarsystemID, mapPositionLocal=SolarSystemPosToMapPos(probe.pos), mapPositionSolarSystem=self.position, trackObjectID=probe.probeID)
                self.localMarkerIDs.add(markerID)
                if markerID in currentProbeMarkers:
                    currentProbeMarkers.remove(markerID)

        for markerID in currentProbeMarkers:
            mapView.markersHandler.RemoveMarker(markerID)
            self.localMarkerIDs.remove(markerID)

    def CreateRenderTarget(self):
        textureQuality = gfxsettings.Get(gfxsettings.GFX_TEXTURE_QUALITY)
        size = PLANET_TEXTURE_SIZE >> textureQuality
        rt = None
        while rt is None or not rt.isValid:
            rt = trinity.Tr2RenderTarget(2 * size, size, 0, trinity.PIXEL_FORMAT.B8G8R8A8_UNORM)
            if not rt.isValid:
                if size < 2:
                    return
                size = size / 2
                rt = None

        return (rt, size)

    def SetupMyPositionTracker(self, transform):
        solarSystemSunID = self.sunID
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None:
            ball = bp.GetBall(solarSystemSunID)
            if ball is not None:
                vectorCurve = trinity.TriVectorCurve()
                vectorCurve.value = (-1.0, -1.0, -1.0)
                vectorSequencer = trinity.TriVectorSequencer()
                vectorSequencer.operator = trinity.TRIOP_MULTIPLY
                vectorSequencer.functions.append(ball)
                vectorSequencer.functions.append(vectorCurve)
                binding = trinity.TriValueBinding()
                binding.sourceAttribute = 'value'
                binding.destinationAttribute = 'translation'
                binding.scale = 1.0
                binding.sourceObject = vectorSequencer
                binding.destinationObject = transform
                curveSet = trinity.TriCurveSet()
                curveSet.name = 'translationCurveSet'
                curveSet.playOnLoad = True
                curveSet.curves.append(vectorSequencer)
                curveSet.bindings.append(binding)
                transform.curveSets.append(curveSet)
                curveSet.Play()


class OrbitCircle(object):
    lineSetScaling = 1000000.0

    def __init__(self, orbitID, position, parentPosition, parentTransform):
        self.orbitID = orbitID
        dirVec = geo2.Vec3Subtract(position, parentPosition)
        radius = geo2.Vec3Length(dirVec)
        dirVec = geo2.Vec3Normalize(dirVec)
        fwdVec = (-1.0, 0.0, 0.0)
        rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
        radius = radius / self.lineSetScaling
        lineSet = mapViewUtil.CreateLineSet()
        lineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
        lineSet.translation = parentPosition
        lineSet.rotation = rotation
        parentTransform.children.append(lineSet)
        self.pixelLineSet = lineSet
        mapViewUtil.DrawCircle(lineSet, (0, 0, 0), radius, startColor=(0.25, 0.25, 0.25, 1.0), endColor=(0.25, 0.25, 0.25, 1.0), lineWidth=2.5)
        lineSet.SubmitChanges()
        lineSet = mapViewUtil.CreatePlanarLineSet(texturePath='res:/dx9/texture/ui/linePlanarSmoothAdditive.dds')
        lineSet.scaling = (self.lineSetScaling, self.lineSetScaling, self.lineSetScaling)
        lineSet.translation = parentPosition
        lineSet.rotation = rotation
        lineSet.additive = True
        parentTransform.children.append(lineSet)
        self.planarLineSet = lineSet
        orbitLineColor = (0.2, 0.2, 0.2, 0.5)
        self.planarLineIDs = mapViewUtil.DrawCircle(lineSet, (0, 0, 0), radius, startColor=orbitLineColor, endColor=orbitLineColor, lineWidth=radius / 150.0)
        lineSet.SubmitChanges()


class RangeIndicator(object):
    circleColor = (0.065, 0.065, 0.065, 0.7)
    labelColor = (0.5, 0.5, 0.5, 0.7)
    defaultRangeSteps = [ each * const.AU for each in (30, 25, 20, 15, 10, 5) ]

    def __init__(self, parentTransform = None, rangeSteps = None, contextScaling = 1.0):
        rangeCircles = trinity.EveTransform()
        rangeCircles.name = 'RangeIndicator'
        if parentTransform:
            parentTransform.children.append(rangeCircles)
        self.rootTransform = rangeCircles
        self.contextScaling = contextScaling
        rangeSteps = rangeSteps or self.defaultRangeSteps
        prevRadius = None
        color = self.circleColor
        for i, radius in enumerate(rangeSteps):
            drawRadius = radius * self.contextScaling
            if i == 0:
                label = GetByLabel('UI/Inflight/Scanner/UnitAU')
            else:
                if radius >= const.AU:
                    label = FmtAmt(radius / const.AU)
                else:
                    label = FmtDist(radius, maxdemicals=0)
                baseAngle = math.pi / 2
                circum = drawRadius * baseAngle
                gapSize = 0.8 / circum
                gapAngle = gapSize * baseAngle
                for startAngle in (0.0,
                 math.pi * 0.5,
                 math.pi,
                 math.pi * 1.5):
                    lineSet = mapViewUtil.CreatePlanarLineSet()
                    rangeCircles.children.append(lineSet)
                    lineIDs = mapViewUtil.DrawCircularArc(lineSet, (0.0, 0.0, 0.0), drawRadius, startAngle=startAngle + gapAngle, angle=baseAngle - gapAngle * 2, lineWidth=0.1, startColor=color, endColor=color)
                    if prevRadius:
                        cos = math.cos(startAngle)
                        sin = math.sin(startAngle)
                        p1 = ((prevRadius - 0.5) * sin, 0.0, (prevRadius - 0.5) * cos)
                        p2 = ((drawRadius + 0.5) * sin, 0.0, (drawRadius + 0.5) * cos)
                        lineID = lineSet.AddStraightLine(p1, color, p2, color, 0.02)
                    lineSet.SubmitChanges()

                prevRadius = drawRadius
            self.AddRangeLabel(label, drawRadius)

        lineSet.SubmitChanges()

    def AddRangeLabel(self, text, radius):
        for x, z in [(0.0, radius),
         (radius, 0.0),
         (0.0, -radius),
         (-radius, 0.0)]:
            label = TransformableLabel(text, self.rootTransform, size=64, shadow=0, hspace=0)
            label.transform.translation = (x, 0.0, z)
            sx, sy, sz = label.transform.scaling
            label.transform.scaling = (sx / sy, 1.0, 0.0)
            label.SetDiffuseColor(self.labelColor)
            label.transform.useDistanceBasedScale = False
            label.transform.modifier = 0
            label.transform.rotation = geo2.QuaternionRotationArc((0, -1, 0), (0, 0, 1))


class SolarSystemInfoBox(LayoutGrid):
    default_columns = 2
    default_cellPadding = (0, 1, 6, 1)

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        self.nameLabel = EveLabelLarge(bold=True)
        self.AddCell(cellObject=self.nameLabel, colSpan=self.columns)
        EveLabelMedium(parent=self, text=GetByLabel('UI/Map/StarMap/SecurityStatus'))
        self.securityValue = EveLabelMedium(parent=self, bold=True, color=(1, 0, 0, 1))

    def LoadSolarSystemID(self, solarSystemID):
        self.nameLabel.text = cfg.evelocations.Get(solarSystemID).name
        securityStatus, color = FmtSystemSecStatus(sm.GetService('map').GetSecurityStatus(solarSystemID), True)
        self.securityValue.color = (color.r,
         color.g,
         color.b,
         1.0)
        self.securityValue.text = securityStatus
