#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\layout\mapLayoutSolarSystems.py
from eve.client.script.ui.shared.mapView.layout.mapLayoutBase import MapLayoutBase
from eve.client.script.ui.shared.mapView.mapViewData import mapViewData

class MapLayoutSolarSystems(MapLayoutBase):

    def PrimeLayout(self, flatten = False, **kwds):
        if flatten == self.cacheKey:
            return
        self.cacheKey = flatten
        solarSystemID_position = {}
        for solarSystemID, solarSystemItem in mapViewData.GetKnownUniverseSolarSystems().iteritems():
            x, y, z = solarSystemItem.mapPosition
            if flatten:
                y = 0.0
            solarSystemID_position[solarSystemID] = (x, y, z)

        self.positionsBySolarSystemID = solarSystemID_position
