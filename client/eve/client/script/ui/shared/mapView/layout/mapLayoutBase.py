#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\layout\mapLayoutBase.py
import weakref

class MapLayoutBase(object):
    cacheKey = None
    positionsBySolarSystemID = None
    visibleMarkers = None
    extraLineMapping = None

    def __init__(self, layoutHandler):
        self.layoutHandler = weakref.ref(layoutHandler)

    def LoadExtraLines(self, lineSet):
        lineSet.ClearLines()

    def ClearCache(self):
        self.cacheKey = None
        self.positionsBySolarSystemID = None
        self.visibleMarkers = None
        self.extraLineMapping = None
