#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerCelestial.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.inflight.scannerFiles.directionalScannerWindow import DirectionalScanner
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import VIEWMODE_MARKERS_OVERLAP_SORT_ORDER
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from eve.client.script.ui.shared.mapView.markers.mapMarkerSpaceObjectRadialMenu import MapMarkerSpaceObjectRadialMenu
from eve.client.script.ui.util.uix import EditStationName, GetBallparkRecord
import evetypes
import state
import carbonui.const as uiconst

class MarkerSpaceObject(MarkerIconBase):
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE * 0.1)
    backgroundTexturePath = None

    def __init__(self, *args, **kwds):
        celestialData = kwds['celestialData']
        bracketIconPath = sm.GetService('bracket').GetBracketIcon(celestialData.typeID)
        if bracketIconPath:
            kwds['texturePath'] = bracketIconPath
        MarkerIconBase.__init__(self, *args, **kwds)
        self.projectBracket.offsetY = 0
        self.celestialData = celestialData
        self.typeID = self.celestialData.typeID
        self.itemID = self.celestialData.itemID

    def GetMenu(self):
        return sm.GetService('menu').CelestialMenu(self.celestialData.itemID, typeID=self.celestialData.typeID, noTrace=1)

    def GetOverlapSortValue(self):
        if self.overlapSortValue:
            return self.overlapSortValue
        displayText = (self.GetDisplayText() or '').lower()
        groupID = self.celestialData.groupID
        if groupID in VIEWMODE_MARKERS_OVERLAP_SORT_ORDER:
            overlapSortValue = (self.markerID[0], VIEWMODE_MARKERS_OVERLAP_SORT_ORDER.index(groupID), displayText)
        else:
            overlapSortValue = (self.markerID[0], len(VIEWMODE_MARKERS_OVERLAP_SORT_ORDER) + self.celestialData.groupID, displayText)
        self.overlapSortValue = overlapSortValue
        return self.overlapSortValue

    def GetDisplayText(self):
        displayName = ''
        locationName = cfg.evelocations.Get(self.celestialData.itemID).name
        if locationName:
            displayName = locationName
            if evetypes.GetGroupID(self.typeID) == const.groupStation:
                displayName = EditStationName(displayName, usename=1)
        elif self.celestialData.typeID:
            displayName = evetypes.GetName(self.celestialData.typeID)
        return displayName

    def GetLabelText(self):
        displayName = self.GetDisplayText()
        distance = self.GetDistance()
        if distance is not None:
            displayName += ' ' + FmtDist(distance)
        return displayName

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
        if not GetBallparkRecord(self.itemID):
            return
        sm.GetService('radialmenu').TryExpandActionMenu(self.itemID, self.markerContainer, radialMenuClass=MapMarkerSpaceObjectRadialMenu, markerObject=self)

    def OnMouseEnter(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 1)
        MarkerIconBase.OnMouseEnter(self, *args)

    def OnMouseExit(self, *args):
        sm.GetService('state').SetState(self.itemID, state.mouseOver, 0)
        MarkerIconBase.OnMouseExit(self, *args)
