#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\layout\mapLayoutRegions.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutRegions(MapLayoutBase):

    def PrimeLayout(self, expandedItems = None, flatten = False):
        if (expandedItems, flatten) == self.cacheKey:
            return
        self.cacheKey = (expandedItems, flatten)
        showMarkers = mapViewData.GetKnownUniverseRegions().keys()
        solarSystemID_position = {}
        for regionID, regionItem in mapViewData.GetKnownUniverseRegions().iteritems():
            if expandedItems and regionID in expandedItems:
                for solarSystemID in regionItem.solarSystemIDs:
                    solarSystemItem = mapViewData.GetKnownSolarSystem(solarSystemID)
                    x, y, z = solarSystemItem.mapPosition
                    if flatten:
                        y = 0.0
                    solarSystemID_position[solarSystemID] = (x, y, z)

                showMarkers += regionItem.constellationIDs
                showMarkers += regionItem.solarSystemIDs
            else:
                x, y, z = regionItem.mapPosition
                if flatten:
                    y = 0.0
                for solarSystemID in regionItem.solarSystemIDs:
                    solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
        self.visibleMarkers = showMarkers
