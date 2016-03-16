#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerScanResult.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from eve.client.script.ui.util.uix import GetBallparkRecord
from eve.common.lib.appConst import minWarpDistance
from inventorycommon.const import groupCosmicAnomaly, groupCosmicSignature
from probescanning.const import probeResultInformative, probeResultGood
from sensorsuite.overlay.controllers.probescanner import SiteDataFromScanResult
import evetypes
import geo2
POINT_COLOR_RED = (1.0, 0.0, 0.0, 1.0)
POINT_COLOR_YELLOW = (1.0, 1.0, 0.0, 1.0)
POINT_COLOR_GREEN = (0.0, 1.0, 0.0, 1.0)
MIN_WARP_DISTANCE_SQUARED = minWarpDistance ** 2

def IsResultWithinWarpDistance(result):
    ballpark = sm.GetService('michelle').GetBallpark()
    egoBall = ballpark.GetBall(ballpark.ego)
    egoPos = geo2.Vector(egoBall.x, egoBall.y, egoBall.z)
    resultPos = geo2.Vector(*result.data)
    distanceSquared = geo2.Vec3LengthSq(egoPos - resultPos)
    return distanceSquared > MIN_WARP_DISTANCE_SQUARED


class MarkerScanResult(MarkerIconBase):
    backgroundTexturePath = None
    graph = None
    highlightFrame = None
    label = None
    redHi = (0.9, 0.0, 0.0, 0.9)
    red = (0.6, 0.0, 0.0, 0.9)
    redLo = (0.4, 0.0, 0.0, 0.9)
    orangeHi = (0.9, 0.5, 0.0, 0.9)
    orange = (0.6, 0.3, 0.0, 0.9)
    orangeLo = (0.4, 0.2, 0.0, 0.9)
    greenHi = (0.0, 0.8, 0.0, 0.9)
    green = (0.0, 0.5, 0.0, 0.9)
    greenLo = (0.0, 0.3, 0.0, 0.9)

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.resultData = resultData = kwds['resultData']
        if isinstance(resultData.data, float) or not isinstance(resultData.data, (tuple, list)):
            texturePath = 'res:/UI/Texture/classes/MapView/scanResultLocation.png'
        else:
            typeID, groupID, categoryID = self.GetTypeGroupCategoryID()
            texturePath = self.GetIconBasedOnQuality(categoryID, groupID, typeID, resultData.certainty)
        self.texturePath = texturePath
        self.projectBracket.offsetY = 0
        self.CreateClientBall()

    def UpdateResultData(self, resultData):
        self.resultData = resultData
        if self.isLoaded:
            self.UpdateScanResult()

    def SetOverlappedState(self, overlapState):
        self.overlapMarkers = None
        if self.overlapStackContainer:
            overlapStackContainer = self.overlapStackContainer
            self.overlapStackContainer = None
            overlapStackContainer.Close()

    def Load(self):
        if self.isLoaded:
            return
        MarkerIconBase.Load(self)
        self.UpdateScanResult()

    def GetResultColors(self):
        result = self.resultData
        if 0.25 < result.certainty <= 0.75:
            baseColor, hiColor, loColor = self.orange, self.orangeHi, self.orangeLo
        elif result.certainty > 0.75:
            baseColor, hiColor, loColor = self.green, self.greenHi, self.greenLo
        else:
            baseColor, hiColor, loColor = self.red, self.redHi, self.redLo
        return (baseColor, hiColor, loColor)

    def UpdateScanResult(self):
        baseColor, hiColor, loColor = self.GetResultColors()
        self.iconColor = self.iconSprite.color = hiColor

    def GetTypeGroupCategoryID(self):
        resultData = self.resultData
        if resultData.certainty >= probeResultInformative:
            typeID = resultData.Get('typeID', None)
            groupID = resultData.groupID
            categoryID = None
        elif resultData.certainty >= probeResultGood:
            typeID = None
            groupID = resultData.Get('groupID', None)
            categoryID = evetypes.GetCategoryIDByGroup(resultData.groupID)
        else:
            typeID = None
            groupID = None
            categoryID = None
        return (typeID, groupID, categoryID)

    def GetLabelText(self):
        scanSvc = sm.GetService('scanSvc')
        displayName = scanSvc.GetDisplayName(self.resultData)
        labelText = '%s %s' % (self.resultData.id, displayName)
        distance = self.GetDistance()
        if distance is not None:
            labelText += ' ' + FmtDist(distance)
        return labelText

    def GetIconBasedOnQuality(self, categoryID, groupID, typeID, certainty):
        if groupID in (groupCosmicAnomaly, groupCosmicSignature):
            bracketData = sm.GetService('bracket').GetBracketDataByGroupID(const.groupBeacon)
        elif categoryID == const.categoryShip and groupID is None:
            bracketData = sm.GetService('bracket').GetBracketDataByGroupID(const.groupFrigate)
        elif typeID:
            bracketIconPath = sm.GetService('bracket').GetBracketIcon(typeID)
            if bracketIconPath:
                return bracketIconPath
        elif groupID:
            bracketData = sm.GetService('bracket').GetBracketDataByGroupID(groupID)
        else:
            bracketData = None
        if bracketData:
            texturePath = bracketData.texturePath
        else:
            texturePath = 'res:/UI/Texture/Shared/Brackets/planet.png'
        return texturePath

    def GetMenu(self):
        scanSvc = sm.GetService('scanSvc')
        scanResult = SiteDataFromScanResult(self.resultData)
        return scanSvc.GetScanResultMenuWithIgnore(scanResult, self.resultData.groupID)

    def GetDistance(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        if not bp.ego:
            return
        ego = bp.balls[bp.ego]
        myPos = (ego.x, ego.y, ego.z)
        return self.resultData.GetDistance(myPos)

    def OnMouseDown(self, *args):
        siteData = SiteDataFromScanResult(self.resultData)
        if self.clientBall:
            sm.GetService('menu').TryExpandActionMenu(itemID=self.clientBall.id, clickedObject=self, siteData=siteData, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)
