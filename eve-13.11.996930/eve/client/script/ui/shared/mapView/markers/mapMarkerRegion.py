#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerRegion.py
from carbonui.primitives.base import ScaleDpi
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Label import MarkerLabelBase

class MarkerLabelRegion(MarkerLabelBase):
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.015, mapViewConst.MAX_MARKER_DISTANCE * 0.75)
    fontSize = 10
    letterSpace = 3

    def __init__(self, *args, **kwds):
        MarkerLabelBase.__init__(self, *args, **kwds)
        self.typeID = const.typeRegion
        self.itemID = self.markerID

    def GetLabelText(self):
        return cfg.evelocations.Get(self.markerID).name.upper()

    def GetDragText(self):
        return cfg.evelocations.Get(self.markerID).name

    def Load(self):
        MarkerLabelBase.Load(self)
        self.projectBracket.offsetY = -ScaleDpi(self.markerContainer.height + 20)
