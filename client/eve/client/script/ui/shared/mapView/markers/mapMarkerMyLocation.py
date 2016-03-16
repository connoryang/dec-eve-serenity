#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerMyLocation.py
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.mapViewConst import MARKERID_MYPOS_OVERLAP_SORT_ORDER
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase
from localization import GetByLabel

class MarkerMyLocation(MarkerIconBase):
    solarSystemID = None
    distanceFadeAlphaNearFar = None
    texturePath = 'res:/UI/Texture/classes/MapView/focusIcon.png'

    def GetMenu(self):
        pass

    def GetLabelText(self):
        return GetByLabel('UI/Map/StarMap/lblYouAreHere')
