#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewBookmarkHandler.py
from carbonui.util.bunch import Bunch
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_BOOKMARK, MARKERS_OPTION_PERSONAL_LOCATION, MARKERS_OPTION_CORPORATION_LOCATION
from eve.client.script.ui.shared.mapView.markers.mapMarkerBookmark import MarkerBookmark, MarkerBookmarkUniverseLevel
from eve.client.script.ui.shared.mapView.mapViewSettings import GetMapViewSetting, IsMarkerGroupEnabled
from eve.client.script.ui.shared.mapView.mapViewUtil import SolarSystemPosToMapPos
import weakref
import geo2
from eve.common.script.sys.idCheckers import IsSolarSystem, IsConstellation
import evetypes
import uthread
import blue
import telemetry
import logging
log = logging.getLogger(__name__)

class MapViewBookmarkHandler(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __notifyevents__ = ['OnBookmarkCreated', 'OnBookmarksDeleted']
    _mapView = None

    def __init__(self, mapView, loadUniverseBookmarks = False):
        self.bookmarkSvc = sm.GetService('bookmarkSvc')
        self.mapView = mapView
        self.loadedSolarSystemID = None
        self.loadUniverseBookmarks = loadUniverseBookmarks
        sm.RegisterNotify(self)

    def StopHandler(self):
        sm.UnregisterNotify(self)

    @apply
    def mapView():

        def fget(self):
            if self._mapView:
                return self._mapView()

        def fset(self, value):
            self._mapView = weakref.ref(value)

        return property(**locals())

    def OnBookmarkCreated(self, bookmarkID, comment, itemTypeID = None):
        bookmark = self.bookmarkSvc.GetBookmark(bookmarkID)
        if not bookmark:
            return
        self.LoadBookmarkMarkers(loadSolarSystemID=self.loadedSolarSystemID, showChanges=True)

    def OnBookmarksDeleted(self, bookmarkIDs):
        self.LoadBookmarkMarkers(loadSolarSystemID=self.loadedSolarSystemID)

    def LoadBookmarkMarkers(self, loadSolarSystemID = None, showChanges = False):
        self.loadedSolarSystemID = loadSolarSystemID
        loadPersonal = IsMarkerGroupEnabled(MARKERS_OPTION_PERSONAL_LOCATION, self.mapView.mapViewID)
        loadCorporation = IsMarkerGroupEnabled(MARKERS_OPTION_CORPORATION_LOCATION, self.mapView.mapViewID)
        bookmarks = []
        if loadPersonal:
            bookmarks += self.bookmarkSvc.GetMyBookmarks().values()[:const.maxCharBookmarkCount]
        if loadCorporation:
            bookmarks += self.bookmarkSvc.GetCorpBookmarks().values()[:const.maxCorpBookmarkCount]
        bookmarksBySolarSystemID = {}
        for bookmark in bookmarks:
            if IsSolarSystem(bookmark.locationID):
                solarSystemID = bookmark.locationID
            elif IsConstellation(bookmark.locationID):
                solarSystemID = bookmark.itemID
            else:
                continue
            bookmarksBySolarSystemID.setdefault(solarSystemID, []).append(bookmark)

        bookmarkMarkers = self.mapView.markersHandler.GetMarkersByType(MARKERID_BOOKMARK)
        bookmarkMarkerIDs = set([ markerObject.markerID for markerObject in bookmarkMarkers ])
        markerIDs = set()
        for solarSystemID, bookmarks in bookmarksBySolarSystemID.iteritems():
            if self.loadUniverseBookmarks:
                if not (self.mapView and self.mapView.layoutHandler):
                    return
                mapNode = self.mapView.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
                if not mapNode:
                    continue
                solarSystemPosition = mapNode.position
                markerID = (MARKERID_BOOKMARK, solarSystemID)
                markerObject = self.mapView.markersHandler.GetMarkerByID(markerID)
                if markerObject:
                    markerObject.bookmarksData = bookmarks
                else:
                    self.mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerBookmarkUniverseLevel, bookmarksData=bookmarks, solarSystemID=solarSystemID, highlightOnLoad=showChanges, mapPositionLocal=(0, 0, 0), mapPositionSolarSystem=solarSystemPosition)
                markerIDs.add(markerID)
            if loadSolarSystemID and solarSystemID != loadSolarSystemID:
                continue
            for bookmark in bookmarks:
                markerID = (MARKERID_BOOKMARK, bookmark.bookmarkID)
                if markerID in bookmarkMarkerIDs:
                    markerIDs.add(markerID)
                    continue
                try:
                    localBookmarkPosition = self.GetBookmarkPosition(bookmark)
                except RuntimeError:
                    log.warn('Failed to get bookmark position, bookmark.bookmarkID, bookmark.itemID: %s, %s' % (bookmark.bookmarkID, bookmark.itemID))
                    continue

                try:
                    mapPositionLocal = SolarSystemPosToMapPos(localBookmarkPosition)
                except TypeError:
                    log.warn('Failed to get bookmark position, localBookmarkPosition: %s' % repr(localBookmarkPosition))
                    continue

                solarSystemPosition = (0, 0, 0)
                if hasattr(self.mapView, 'layoutHandler'):
                    mapNode = self.mapView.layoutHandler.GetNodeBySolarSystemID(solarSystemID)
                    if mapNode:
                        solarSystemPosition = mapNode.position
                self.mapView.markersHandler.AddSolarSystemBasedMarker(markerID, MarkerBookmark, bookmarkData=bookmark, solarSystemID=solarSystemID, highlightOnLoad=showChanges, mapPositionLocal=mapPositionLocal, mapPositionSolarSystem=solarSystemPosition)
                markerIDs.add(markerID)

            blue.pyos.BeNice(10)

        for removeMarkerID in bookmarkMarkerIDs.difference(markerIDs):
            self.mapView.markersHandler.RemoveMarker(removeMarkerID)

        return markerIDs

    def GetBookmarkPosition(self, bookmark):
        localPosition = None
        if bookmark and (bookmark.itemID == bookmark.locationID or bookmark.typeID == const.typeSolarSystem) and bookmark.x is not None:
            localPosition = (bookmark.x, bookmark.y, bookmark.z)
        else:
            mapSvc = sm.GetService('map')
            try:
                itemStarMapData = mapSvc.GetItem(bookmark.itemID)
            except KeyError:
                log.error('Map data not found for bookmark.itemID: %s' % bookmark.itemID)
                return

            if itemStarMapData:
                localPosition = (itemStarMapData.x, itemStarMapData.y, itemStarMapData.z)
            elif evetypes.GetGroupID(bookmark.typeID) == const.groupStargate:
                try:
                    solarSystemData = cfg.mapSolarSystemContentCache[bookmark.locationID]
                except KeyError:
                    log.error('Stargate data not found for bookmark.locationID: %s' % bookmark.locationID)
                    return

                starGateInfo = solarSystemData.stargates.get(bookmark.itemID, None)
                if starGateInfo:
                    position = starGateInfo.position
                    localPosition = (position.x, position.y, position.z)
        if localPosition is None:
            localPosition = (0, 0, 0)
        return localPosition
