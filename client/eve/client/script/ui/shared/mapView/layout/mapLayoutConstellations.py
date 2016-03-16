#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\layout\mapLayoutConstellations.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutConstellations(MapLayoutBase):

    def PrimeLayout(self, expandedItems = None, flatten = False):
        if (expandedItems, flatten) == self.cacheKey:
            return
        self.cacheKey = (expandedItems, flatten)
        showMarkers = mapViewData.GetKnownUniverseRegions().keys()
        showMarkers += mapViewData.GetKnownUniverseConstellations().keys()
        solarSystemID_position = {}
        for constellationID, constellationItem in mapViewData.GetKnownUniverseConstellations().iteritems():
            if expandedItems and constellationID in expandedItems:
                for solarSystemID in constellationItem.solarSystemIDs:
                    solarSystemItem = mapViewData.GetKnownSolarSystem(solarSystemID)
                    x, y, z = solarSystemItem.mapPosition
                    if flatten:
                        y = 0.0
                    solarSystemID_position[solarSystemID] = (x, y, z)

                showMarkers += constellationItem.solarSystemIDs
            else:
                x, y, z = constellationItem.mapPosition
                if flatten:
                    y = 0.0
                for solarSystemID in constellationItem.solarSystemIDs:
                    solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
        self.visibleMarkers = showMarkers
