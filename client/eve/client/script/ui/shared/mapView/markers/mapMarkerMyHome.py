#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerMyHome.py
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_MYHOME_OVERLAP_SORT_ORDER
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from localization import GetByLabel

class MarkerMyHome(MarkerIconBase):
    distanceFadeAlphaNearFar = None
    texturePath = 'res:/UI/Texture/classes/MapView/homeIcon.png'

    def __init__(self, *args, **kwds):
        MarkerIconBase.__init__(self, *args, **kwds)
        self.stationInfo = kwds['stationInfo']
        self.typeID = self.stationInfo.stationTypeID
        self.itemID = self.stationInfo.stationID

    def GetMenu(self):
        if self.stationInfo:
            return sm.GetService('menu').GetMenuFormItemIDTypeID(self.stationInfo.stationID, self.stationInfo.stationTypeID, noTrace=1)

    def GetLabelText(self):
        return GetByLabel('UI/Map/HomeStationLabel')

    def GetDragText(self):
        return cfg.evelocations.Get(self.stationInfo.stationID).name
