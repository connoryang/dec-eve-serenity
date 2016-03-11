#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerBookmark.py
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewUtil import MapPosToSolarSystemPos
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from localization import GetByLabel
import localization
import state
import carbonui.const as uiconst

class MarkerBookmarkUniverseLevel(MarkerIconBase):
    texturePath = 'res:/UI/Texture/Icons/38_16_150.png'
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.2, mapViewConst.MAX_MARKER_DISTANCE)
    overlapEnabled = False
    distanceSortEnabled = False

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.bookmarksData = kwds['bookmarksData']
        self.showChanges = kwds.get('showChanges', False)

    def GetLabelText(self):
        return GetByLabel('UI/Map/LocationsInSolarSystem', locationName=cfg.evelocations.Get(self.solarSystemID).name, amount=len(self.bookmarksData))

    def GetMenu(self):
        pass


class MarkerBookmark(MarkerIconBase):
    texturePath = 'res:/UI/Texture/Icons/38_16_150.png'
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE * 0.1)

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.bookmarkData = kwds['bookmarkData']
        if self.bookmarkData.ownerID == session.corpid:
            self.texturePath = 'res:/UI/Texture/Icons/38_16_257.png'
        self.itemID = self.bookmarkData.itemID or self.bookmarkData.locationID
        self.typeID = self.bookmarkData.typeID
        self.CreateClientBall()

    def GetDisplayText(self):
        caption, note = sm.GetService('bookmarkSvc').UnzipMemo(self.bookmarkData.memo)
        return localization.GetByLabel('UI/Map/StarMap/hintSystemBookmark', memo=caption)

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.itemID, typeID=self.typeID, bookmark=self.bookmarkData)

    def OnClick(self, *args):
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            markerPosition = self.position
            directionalScanner = DirectionalScanner.GetIfOpen()
            if directionalScanner:
                directionalScanner.ScanTowardsItem(self.itemID, mapPosition=markerPosition)
        else:
            sm.GetService('state').SetState(self.itemID, state.selected, 1)
            MarkerIconBase.OnClick(self, *args)

    def OnMouseDown(self, *args):
        bookMarkInfo = self.bookmarkData
        if bookMarkInfo is None:
            return
        if self.clientBall:
            sm.GetService('menu').TryExpandActionMenu(itemID=self.clientBall.id, clickedObject=self, bookmarkInfo=self.bookmarkData, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)
