#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerProbe.py
from carbon.common.script.util.format import FmtDist
from eve.client.script.ui.shared.mapView import mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase_Icon import MarkerIconBase

class MarkerProbe(MarkerIconBase):
    distanceFadeAlphaNearFar = (0.0, mapViewConst.MAX_MARKER_DISTANCE * 0.1)
    backgroundTexturePath = None

    def __init__(self, *args, **kwds):
        bracketData = sm.GetService('bracket').GetBracketDataByGroupID(const.groupScannerProbe)
        if bracketData:
            kwds['texturePath'] = bracketData.texturePath
        MarkerIconBase.__init__(self, *args, **kwds)
        self.probeData = kwds['probeData']
        self.projectBracket.offsetY = 0

    def GetLabelText(self):
        labelText = sm.GetService('scanSvc').GetProbeLabel(self.probeData.probeID)
        distance = self.GetDistance()
        if distance is not None:
            labelText += ' ' + FmtDist(distance)
        return labelText

    def GetMenu(self):
        return sm.GetService('scanSvc').GetProbeMenu(self.probeData.probeID)
