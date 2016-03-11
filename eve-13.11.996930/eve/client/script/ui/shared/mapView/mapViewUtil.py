#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewUtil.py
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import MARKER_TYPES, UNIVERSE_SCALE, SOLARSYSTEM_SCALE, VIEWMODE_COLOR_SETTINGS
import sys
import geo2
from math import sin, cos
from eve.client.script.ui.shared.maps import mapcommon
from eve.client.script.ui.shared.systemMenu.betaOptions import BETA_MAP_SETTING_KEY, BetaFeatureEnabled, IsBetaScannersEnabled
import uthread
import trinity
import math
colorModeLogName = {mapcommon.STARMODE_SERVICE_Paintshop: 'STARMODE_SERVICE_Paintshop',
 mapcommon.STARMODE_ASSETS: 'STARMODE_ASSETS',
 mapcommon.STARMODE_JUMPS1HR: 'STARMODE_JUMPS1HR',
 mapcommon.STARMODE_SERVICE_AssassinationMissions: 'STARMODE_SERVICE_AssassinationMissions',
 mapcommon.STARMODE_SETTLED_SYSTEMS_BY_CORP: 'STARMODE_SETTLED_SYSTEMS_BY_CORP',
 mapcommon.STARMODE_STATION_SERVICE_STORAGE: 'STARMODE_STATION_SERVICE_STORAGE',
 mapcommon.STARMODE_PLANETTYPE: 'STARMODE_PLANETTYPE',
 mapcommon.STARMODE_SERVICE_NavyOffices: 'STARMODE_SERVICE_NavyOffices',
 mapcommon.STARMODE_SERVICE_Factory: 'STARMODE_SERVICE_Factory',
 mapcommon.STARMODE_INCURSIONGM: 'STARMODE_INCURSIONGM',
 mapcommon.STARMODE_STATION_SERVICE_INSURANCE: 'STARMODE_STATION_SERVICE_INSURANCE',
 mapcommon.STARMODE_STATION_SERVICE_NAVYOFFICES: 'STARMODE_STATION_SERVICE_NAVYOFFICES',
 mapcommon.STARMODE_PODKILLS24HR: 'STARMODE_PODKILLS24HR',
 mapcommon.STARMODE_SOV_CHANGE: 'STARMODE_SOV_CHANGE',
 mapcommon.STARMODE_SERVICE_RepairFacilities: 'STARMODE_SERVICE_RepairFacilities',
 mapcommon.STARMODE_BOOKMARKED: 'STARMODE_BOOKMARKED',
 mapcommon.STARMODE_CORPDELIVERIES: 'STARMODE_CORPDELIVERIES',
 mapcommon.STARMODE_SOV_STANDINGS: 'STARMODE_SOV_STANDINGS',
 mapcommon.STARMODE_FILTER_EMPIRE: 'STARMODE_FILTER_EMPIRE',
 mapcommon.STARMODE_FRIENDS_AGENT: 'STARMODE_FRIENDS_AGENT',
 mapcommon.STARMODE_FRIENDS_CONTACTS: 'STARMODE_FRIENDS_CONTACTS',
 mapcommon.STARMODE_COPY_JOBS24HOUR: 'STARMODE_COPY_JOBS24HOUR',
 mapcommon.STARMODE_MILITIAKILLS1HR: 'STARMODE_MILITIAKILLS1HR',
 mapcommon.STARMODE_INDEX_INDUSTRY: 'STARMODE_INDEX_INDUSTRY',
 mapcommon.STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX: 'STARMODE_INDUSTRY_RESEARCHMATERIAL_COST_INDEX',
 mapcommon.STARMODE_STATION_SERVICE_CLONING: 'STARMODE_STATION_SERVICE_CLONING',
 mapcommon.STARMODE_MANUFACTURING_JOBS24HOUR: 'STARMODE_MANUFACTURING_JOBS24HOUR',
 mapcommon.STARMODE_VISITED: 'STARMODE_VISITED',
 mapcommon.STARMODE_STATION_SERVICE_BLACKMARKET: 'STARMODE_STATION_SERVICE_BLACKMARKET',
 mapcommon.STARMODE_PLAYERDOCKED: 'STARMODE_PLAYERDOCKED',
 mapcommon.STARMODE_STATION_SERVICE_REPROCESSINGPLANT: 'STARMODE_STATION_SERVICE_REPROCESSINGPLANT',
 mapcommon.STARMODE_SERVICE_DNATherapy: 'STARMODE_SERVICE_DNATherapy',
 mapcommon.STARMODE_PODKILLS1HR: 'STARMODE_PODKILLS1HR',
 mapcommon.STARMODE_REAL: 'STARMODE_REAL',
 mapcommon.STARMODE_SERVICE_Storage: 'STARMODE_SERVICE_Storage',
 mapcommon.STARMODE_STATION_SERVICE_ASSASSINATIONMISSIONS: 'STARMODE_STATION_SERVICE_ASSASSINATIONMISSIONS',
 mapcommon.STARMODE_PISCANRANGE: 'STARMODE_PISCANRANGE',
 mapcommon.STARMODE_SECURITY: 'STARMODE_SECURITY',
 mapcommon.STARMODE_STATIONCOUNT: 'STARMODE_STATIONCOUNT',
 mapcommon.STARMODE_INDEX_MILITARY: 'STARMODE_INDEX_MILITARY',
 mapcommon.STARMODE_SERVICE_Laboratory: 'STARMODE_SERVICE_Laboratory',
 mapcommon.STARMODE_SERVICE_Cloning: 'STARMODE_SERVICE_Cloning',
 mapcommon.STARMODE_OUTPOST_GAIN: 'STARMODE_OUTPOST_GAIN',
 mapcommon.STARMODE_CONSTSOVEREIGNTY: 'STARMODE_CONSTSOVEREIGNTY',
 mapcommon.STARMODE_FACTION: 'STARMODE_FACTION',
 mapcommon.STARMODE_STATION_SERVICE_NEWS: 'STARMODE_STATION_SERVICE_NEWS',
 mapcommon.STARMODE_SERVICE_Insurance: 'STARMODE_SERVICE_Insurance',
 mapcommon.STARMODE_FRIENDS_FLEET: 'STARMODE_FRIENDS_FLEET',
 mapcommon.STARMODE_CORPIMPOUNDED: 'STARMODE_CORPIMPOUNDED',
 mapcommon.STARMODE_STATION_SERVICE_FITTING: 'STARMODE_STATION_SERVICE_FITTING',
 mapcommon.STARMODE_SERVICE_Gambling: 'STARMODE_SERVICE_Gambling',
 mapcommon.STARMODE_MYCOLONIES: 'STARMODE_MYCOLONIES',
 mapcommon.STARMODE_SERVICE: 'STARMODE_SERVICE',
 mapcommon.STARMODE_STATION_SERVICE_GAMBLING: 'STARMODE_STATION_SERVICE_GAMBLING',
 mapcommon.STARMODE_SERVICE_SecurityOffice: 'STARMODE_SERVICE_SecurityOffice',
 mapcommon.STARMODE_SERVICE_BlackMarket: 'STARMODE_SERVICE_BlackMarket',
 mapcommon.STARMODE_STATION_SERVICE_REPAIRFACILITIES: 'STARMODE_STATION_SERVICE_REPAIRFACILITIES',
 mapcommon.STARMODE_SERVICE_ReprocessingPlant: 'STARMODE_SERVICE_ReprocessingPlant',
 mapcommon.STARMODE_STATION_SERVICE_INTERBUS: 'STARMODE_STATION_SERVICE_INTERBUS',
 mapcommon.STARMODE_STATION_SERVICE_SURGERY: 'STARMODE_STATION_SERVICE_SURGERY',
 mapcommon.STARMODE_SHIPKILLS1HR: 'STARMODE_SHIPKILLS1HR',
 mapcommon.STARMODE_MILITIA: 'STARMODE_MILITIA',
 mapcommon.STARMODE_CYNOSURALFIELDS: 'STARMODE_CYNOSURALFIELDS',
 mapcommon.STARMODE_STATION_SERVICE_MARKET: 'STARMODE_STATION_SERVICE_MARKET',
 mapcommon.STARMODE_CORPOFFICES: 'STARMODE_CORPOFFICES',
 mapcommon.STARMODE_JOBS24HOUR: 'STARMODE_JOBS24HOUR',
 mapcommon.STARMODE_STATION_SERVICE_DNATHERAPY: 'STARMODE_STATION_SERVICE_DNATHERAPY',
 mapcommon.STARMODE_SERVICE_Market: 'STARMODE_SERVICE_Market',
 mapcommon.STARMODE_AVOIDANCE: 'STARMODE_AVOIDANCE',
 mapcommon.STARMODE_RESEARCHMATERIAL_JOBS24HOUR: 'STARMODE_RESEARCHMATERIAL_JOBS24HOUR',
 mapcommon.STARMODE_REGION: 'STARMODE_REGION',
 mapcommon.STARMODE_SERVICE_Refinery: 'STARMODE_SERVICE_Refinery',
 mapcommon.STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX: 'STARMODE_INDUSTRY_RESEARCHTIME_COST_INDEX',
 mapcommon.STARMODE_DUNGEONS: 'STARMODE_DUNGEONS',
 mapcommon.STARMODE_STATION_SERVICE_PAINTSHOP: 'STARMODE_STATION_SERVICE_PAINTSHOP',
 mapcommon.STARMODE_FACTIONKILLS1HR: 'STARMODE_FACTIONKILLS1HR',
 mapcommon.STARMODE_FRIENDS_CORP: 'STARMODE_FRIENDS_CORP',
 mapcommon.STARMODE_INCURSION: 'STARMODE_INCURSION',
 mapcommon.STARMODE_INDUSTRY_INVENTION_COST_INDEX: 'STARMODE_INDUSTRY_INVENTION_COST_INDEX',
 mapcommon.STARMODE_PLAYERCOUNT: 'STARMODE_PLAYERCOUNT',
 mapcommon.STARMODE_INDUSTRY_COPY_COST_INDEX: 'STARMODE_INDUSTRY_COPY_COST_INDEX',
 mapcommon.STARMODE_STATION_SERVICE_LABORATORY: 'STARMODE_STATION_SERVICE_LABORATORY',
 mapcommon.STARMODE_FACTIONEMPIRE: 'STARMODE_FACTIONEMPIRE',
 mapcommon.STARMODE_FILTER_FACWAR_MINE: 'STARMODE_FILTER_FACWAR_MINE',
 mapcommon.STARMODE_RESEARCHTIME_JOBS24HOUR: 'STARMODE_RESEARCHTIME_JOBS24HOUR',
 mapcommon.STARMODE_STATION_SERVICE_SECURITYOFFICE: 'STARMODE_STATION_SERVICE_SECURITYOFFICE',
 mapcommon.STARMODE_SHIPKILLS24HR: 'STARMODE_SHIPKILLS24HR',
 mapcommon.STARMODE_SERVICE_Interbus: 'STARMODE_SERVICE_Interbus',
 mapcommon.STARMODE_SERVICE_News: 'STARMODE_SERVICE_News',
 mapcommon.STARMODE_SERVICE_StockExchange: 'STARMODE_SERVICE_StockExchange',
 mapcommon.STARMODE_INVENTION_JOBS24HOUR: 'STARMODE_INVENTION_JOBS24HOUR',
 mapcommon.STARMODE_SERVICE_Fitting: 'STARMODE_SERVICE_Fitting',
 mapcommon.STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX: 'STARMODE_INDUSTRY_MANUFACTURING_COST_INDEX',
 mapcommon.STARMODE_STATION_SERVICE_STOCKEXCHANGE: 'STARMODE_STATION_SERVICE_STOCKEXCHANGE',
 mapcommon.STARMODE_OUTPOST_LOSS: 'STARMODE_OUTPOST_LOSS',
 mapcommon.STARMODE_SOV_LOSS: 'STARMODE_SOV_LOSS',
 mapcommon.STARMODE_FILTER_FACWAR_ENEMY: 'STARMODE_FILTER_FACWAR_ENEMY',
 mapcommon.STARMODE_STATION_SERVICE_REFINERY: 'STARMODE_STATION_SERVICE_REFINERY',
 mapcommon.STARMODE_MILITIAKILLS24HR: 'STARMODE_MILITIAKILLS24HR',
 mapcommon.STARMODE_SERVICE_Surgery: 'STARMODE_SERVICE_Surgery',
 mapcommon.STARMODE_SERVICE_CourierMissions: 'STARMODE_SERVICE_CourierMissions',
 mapcommon.STARMODE_STATION_SERVICE_COURIERMISSIONS: 'STARMODE_STATION_SERVICE_COURIERMISSIONS',
 mapcommon.STARMODE_DUNGEONSAGENTS: 'STARMODE_DUNGEONSAGENTS',
 mapcommon.STARMODE_INDEX_STRATEGIC: 'STARMODE_INDEX_STRATEGIC',
 mapcommon.STARMODE_CARGOILLEGALITY: 'STARMODE_CARGOILLEGALITY',
 mapcommon.STARMODE_STATION_SERVICE_FACTORY: 'STARMODE_STATION_SERVICE_FACTORY',
 mapcommon.STARMODE_CORPPROPERTY: 'STARMODE_CORPPROPERTY',
 mapcommon.STARMODE_SOV_GAIN: 'STARMODE_SOV_GAIN'}

def LogColorModeUsage(useCase = ''):
    colorMode = settings.char.ui.Get('%s_%s' % (VIEWMODE_COLOR_SETTINGS, mapViewConst.MAPVIEW_PRIMARY_ID), mapViewConst.DEFAULT_MAPVIEW_SETTINGS[VIEWMODE_COLOR_SETTINGS])
    if isinstance(colorMode, tuple):
        colorMode, _colorModeArgs = colorMode
    if colorMode in colorModeLogName:
        logValue = '%s (%s)' % (colorModeLogName[colorMode], useCase)
        uthread.new(sm.GetService('experimentClientSvc').LogMapColorModeLoadedCounter, logValue)


def GetBoundingSphereRadiusCenter(vectors, isFlatten = False):
    minX = sys.maxint
    minY = sys.maxint
    minZ = sys.maxint
    maxX = -sys.maxint
    maxY = -sys.maxint
    maxZ = -sys.maxint
    for x, y, z in vectors:
        minX = min(minX, x)
        minY = min(minY, y)
        minZ = min(minZ, z)
        maxX = max(maxX, x)
        maxY = max(maxY, y)
        maxZ = max(maxZ, z)

    if isFlatten:
        minY = maxY = 0.0
    maxBound = (maxX, maxY, maxZ)
    minBound = (minX, minY, minZ)
    center = geo2.Vec3Scale(geo2.Vec3Add(minBound, maxBound), 0.5)
    offset = geo2.Vec3Scale(geo2.Vec3Subtract(minBound, maxBound), 0.5)
    return (center, geo2.Vec3Length(offset))


def GetTranslationFromParentWithRadius(radius, camera):
    camangle = camera.fieldOfView * 0.5
    translationFromParent = max(mapViewConst.MIN_CAMERA_DISTANCE, min(mapViewConst.MAX_CAMERA_DISTANCE, radius / sin(camangle) * cos(camangle)))
    return translationFromParent


def SolarSystemPosToMapPos(position):
    x, y, z = position
    return (ScaleSolarSystemValue(x), ScaleSolarSystemValue(y), ScaleSolarSystemValue(z))


def MapPosToSolarSystemPos(position):
    x, y, z = position
    return (x / SOLARSYSTEM_SCALE, y / SOLARSYSTEM_SCALE, z / SOLARSYSTEM_SCALE)


def WorldPosToMapPos(position):
    x, y, z = position
    return (x * -UNIVERSE_SCALE, y * -UNIVERSE_SCALE, z * UNIVERSE_SCALE)


def ScaledPosToMapPos(pos):
    x, y, z = pos
    return (x * -1, y * -1, z)


def ScaleSolarSystemValue(value):
    return value * SOLARSYSTEM_SCALE


def IsDynamicMarkerType(itemID):
    try:
        if itemID[0] in MARKER_TYPES:
            return True
    except:
        return False


def IsLandmark(itemID):
    return itemID and itemID < 0


def IsMapBetaEnabled():
    map_beta_enabled = BetaFeatureEnabled(BETA_MAP_SETTING_KEY)
    return map_beta_enabled


def IsMapBetaExplicit():
    return False


def IsMapBetaPrimary():
    return IsMapBetaEnabled()


def ToggleSolarSystemMap():
    if IsBetaScannersEnabled():
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if not SolarSystemViewPanel.ClosePanel() and session.solarsystemid2:
            SolarSystemViewPanel.OpenPanel()
    else:
        sm.GetService('viewState').ToggleSecondaryView('systemmap')


def OpenSolarSystemMap():
    if IsBetaScannersEnabled():
        if session.solarsystemid2:
            from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
            SolarSystemViewPanel.OpenPanel()
    else:
        sm.GetService('viewState').ActivateView('systemmap')


def ToggleMap(*args, **kwds):
    if IsMapBetaPrimary():
        from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
        if not MapViewPanel.ClosePanel():
            return OpenMap(*args, **kwds)
    else:
        viewSvc = sm.GetService('viewState')
        if viewSvc.IsViewActive('starmap', 'systemmap'):
            viewSvc.CloseSecondaryView()
        else:
            viewSvc.ActivateView('starmap', **kwds)


def OpenMap(interestID = None, hightlightedSolarSystems = None, drawRoute = None, starColorMode = None, **kwds):
    if IsMapBetaPrimary():
        from eve.client.script.ui.shared.mapView.mapViewPanel import MapViewPanel
        mapPanel = MapViewPanel.GetPanel()
        if mapPanel:
            if interestID:
                mapPanel.SetActiveItemID(interestID, zoomToItem=True)
            if starColorMode:
                mapPanel.SetViewColorMode(starColorMode)
        else:
            mapView = MapViewPanel.OpenPanel(parent=uicore.layer.main, interestID=interestID, starColorMode=starColorMode)
    else:
        sm.GetService('viewState').ActivateView('starmap', interestID=interestID, hightlightedSolarSystems=hightlightedSolarSystems, drawRoute=drawRoute, starColorMode=starColorMode)


def UpdateDebugOutput(debugOutput, camera = None, mapView = None, **kwds):
    debugText = ''
    if mapView:
        debugText += '<br>MapViewID %s' % mapView.mapViewID
    if camera:
        debugText += '<br>field of view %s' % camera.fieldOfView
        debugText += '<br>min/max distance %s/%s' % (camera.minDistance, camera.maxDistance)
        debugText += '<br>front/back clip %s/%s' % (camera.frontClip, camera.backClip)
        debugText += '<br>translationFromParent %s' % camera.GetCameraDistanceFromInterest()
        debugText += '<br>viewAngle %.3f, %.3f, %.3f' % camera.GetViewVector()
    debugOutput.text = debugText


def CreateLineSet(pickEnabled = False, texturePath = None):
    lineSet = trinity.EveCurveLineSet()
    tex2D = trinity.TriTextureParameter()
    tex2D.name = 'TexMap'
    tex2D.resourcePath = texturePath or 'res:/UI/Texture/classes/MapView/lineSegment.dds'
    lineSet.lineEffect.resources.append(tex2D)
    overlayTex2D = trinity.TriTextureParameter()
    overlayTex2D.name = 'OverlayTexMap'
    overlayTex2D.resourcePath = 'res:/UI/Texture/classes/MapView/lineSegmentConstellation.dds'
    lineSet.lineEffect.resources.append(overlayTex2D)
    if not pickEnabled:
        lineSet.pickEffect = None
    return lineSet


def CreatePlanarLineSet(pickEnabled = False, texturePath = None):
    lineSet = trinity.EveCurveLineSet()
    lineSet.lineEffect = trinity.Tr2Effect()
    lineSet.lineEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines/Lines3DPlanar.fx'
    tex2D = trinity.TriTextureParameter()
    tex2D.name = 'TexMap'
    tex2D.resourcePath = texturePath or 'res:/dx9/texture/ui/linePlanarBase.dds'
    lineSet.lineEffect.resources.append(tex2D)
    if pickEnabled:
        lineSet.pickEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Lines/Lines3DPlanarPicking.fx'
    else:
        lineSet.pickEffect = None
    return lineSet


PARTICLE_EFFECT = 'res:/Graphics/Effect/Managed/Space/SpecialFX/Particles/StarmapNew.fx'
PARTICLE_SPRITE_TEXTURE = 'res:/Texture/Particle/mapStarNew5.dds'
PARTICLE_SPRITE_HEAT_TEXTURE = 'res:/Texture/Particle/mapStarNewHeat.dds'
PARTICLE_SPRITE_DATA_TEXTURE = 'res:/Texture/Particle/mapStatData_Circle.dds'
DISTANCE_RANGE = 'distanceRange'

def CreateParticles():
    particleTransform = trinity.EveTransform()
    particleTransform.name = 'particleTransform'
    tex = trinity.TriTextureParameter()
    tex.name = 'TexMap'
    tex.resourcePath = PARTICLE_SPRITE_TEXTURE
    heattex = trinity.TriTextureParameter()
    heattex.name = 'HeatTexture'
    heattex.resourcePath = PARTICLE_SPRITE_HEAT_TEXTURE
    distanceFadeControl = trinity.Tr2Vector4Parameter()
    distanceFadeControl.name = DISTANCE_RANGE
    distanceFadeControl.value = (0, 1, 0, 0)
    particles = trinity.Tr2RuntimeInstanceData()
    particles.SetElementLayout([(trinity.PARTICLE_ELEMENT_TYPE.POSITION, 0, 3),
     (trinity.PARTICLE_ELEMENT_TYPE.POSITION, 1, 3),
     (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 0, 1),
     (trinity.PARTICLE_ELEMENT_TYPE.CUSTOM, 1, 4)])
    mesh = trinity.Tr2InstancedMesh()
    mesh.geometryResPath = 'res:/Graphics/Generic/UnitPlane/UnitPlane.gr2'
    mesh.instanceGeometryResource = particles
    particleTransform.mesh = mesh
    area = trinity.Tr2MeshArea()
    area.effect = trinity.Tr2Effect()
    area.effect.effectFilePath = PARTICLE_EFFECT
    area.effect.resources.append(tex)
    area.effect.resources.append(heattex)
    area.effect.parameters.append(distanceFadeControl)
    mesh.additiveAreas.append(area)
    return (particleTransform, particles, distanceFadeControl)


def DrawLineSetCircle(lineSet, centerPosition, outerPosition, segmentSize, lineColor = (0.3, 0.3, 0.3, 0.5), lineWeight = 2.0, animationSpeed = 0.0, dashSegments = 0, dashColor = None):
    orbitPos = geo2.Vector(*outerPosition)
    parentPos = geo2.Vector(*centerPosition)
    dirVec = orbitPos - parentPos
    radius = geo2.Vec3Length(dirVec)
    fwdVec = (1.0, 0.0, 0.0)
    dirVec = geo2.Vec3Normalize(dirVec)
    rotation = geo2.QuaternionRotationArc(fwdVec, dirVec)
    matrix = geo2.MatrixAffineTransformation(1.0, (0.0, 0.0, 0.0), rotation, centerPosition)
    circum = math.pi * 2 * radius
    steps = min(256, max(16, int(circum / segmentSize)))
    coordinates = []
    stepSize = math.pi * 2 / steps
    for step in range(steps):
        angle = step * stepSize
        x = math.cos(angle) * radius
        z = math.sin(angle) * radius
        pos = geo2.Vector(x, 0.0, z)
        pos = geo2.Vec3TransformCoord(pos, matrix)
        coordinates.append(pos)

    lineIDs = set()
    dashColor = dashColor or lineColor
    for start in xrange(steps):
        end = (start + 1) % steps
        lineID = lineSet.AddStraightLine(coordinates[start], lineColor, coordinates[end], lineColor, lineWeight)
        lineIDs.add(lineID)
        if dashSegments:
            lineSet.ChangeLineAnimation(lineID, dashColor, animationSpeed, dashSegments)

    return lineIDs


def DrawCircle(lineSet, centerPosition, radius, arcSegments = 4, startColor = (0.3, 0.3, 0.3, 0.5), endColor = (0.3, 0.3, 0.3, 0.5), **kwds):
    lineIDs = set()
    arcAngle = math.pi * 2 / float(arcSegments)
    stepSize = 1.0 / float(arcSegments)
    for i in xrange(arcSegments):
        step = i / float(arcSegments)
        startAngle = math.pi * 2 * step
        color1 = geo2.Vec4Lerp(startColor, endColor, step)
        color2 = geo2.Vec4Lerp(startColor, endColor, step + stepSize)
        lineID = DrawCircularArc(lineSet, centerPosition, radius, angle=arcAngle, startAngle=startAngle, startColor=color1, endColor=color2, **kwds)
        lineIDs.add(lineID)

    return lineIDs


def DrawCircularArc(lineSet, centerPosition, radius, angle, startAngle = 0.0, lineWidth = 1.0, startColor = (0.3, 0.3, 0.3, 0.5), endColor = (0.3, 0.3, 0.3, 0.5)):
    cos = math.cos(startAngle)
    sin = math.sin(startAngle)
    p1 = geo2.Vec3Add(centerPosition, (-radius * cos, 0.0, -radius * sin))
    cos = math.cos(startAngle + angle)
    sin = math.sin(startAngle + angle)
    p2 = geo2.Vec3Add(centerPosition, (-radius * cos, 0.0, -radius * sin))
    lineID = lineSet.AddSpheredLineCrt(p1, startColor, p2, endColor, centerPosition, lineWidth)
    lineSet.ChangeLineSegmentation(lineID, int(math.degrees(angle)))
    return lineID
