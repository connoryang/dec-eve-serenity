#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerSolarSystem.py
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerSolarSystemBased
import carbonui.const as uiconst
import math
from carbonui.uianimations import animations

class MarkerLabelSolarSystem(MarkerSolarSystemBased):
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.005, mapViewConst.MAX_MARKER_DISTANCE * 0.075)
    hilightContainer = None
    positionPickable = True
    extraInfo = None
    _cachedLabel = None
    CIRCLESIZE = 14
    LABEL_LEFT_MARGIN = 6

    def __init__(self, *args, **kwds):
        MarkerSolarSystemBased.__init__(self, *args, **kwds)
        self.typeID = const.typeSolarSystem
        self.itemID = self.markerID
        self.solarSystemID = self.markerID

    def Load(self):
        self.isLoaded = True
        self.textLabel = EveLabelSmall(parent=self.markerContainer, text=self.GetLabelText(), bold=True, state=uiconst.UI_DISABLED, left=self.CIRCLESIZE + self.LABEL_LEFT_MARGIN)
        self.markerContainer.width = self.textLabel.textwidth
        self.markerContainer.height = self.textLabel.textheight
        self.projectBracket.offsetX = ScaleDpi(self.markerContainer.width * 0.5 - self.CIRCLESIZE / 2)
        self.UpdateActiveAndHilightState()

    def DestroyRenderObject(self):
        MarkerSolarSystemBased.DestroyRenderObject(self)
        self.hilightContainer = None

    def UpdateSolarSystemPosition(self, solarSystemPosition):
        self.mapPositionSolarSystem = solarSystemPosition
        self.SetPosition(solarSystemPosition)

    def GetLabelText(self):
        if self._cachedLabel is None:
            securityStatus, color = sm.GetService('map').GetSecurityStatus(self.markerID, True)
            self._cachedLabel = '%s <color=%s>%s</color>' % (cfg.evelocations.Get(self.markerID).name, Color.RGBtoHex(color.r, color.g, color.b), securityStatus)
        return self._cachedLabel

    def GetDragText(self):
        return cfg.evelocations.Get(self.markerID).name

    def UpdateActiveAndHilightState(self):
        if self.hilightState or self.activeState:
            self.projectBracket.maxDispRange = 1e+32
            if self.markerContainer:
                if not self.hilightContainer:
                    hilightContainer = Container(parent=self.markerContainer, align=uiconst.CENTERLEFT, pos=(0,
                     0,
                     self.CIRCLESIZE,
                     self.CIRCLESIZE), state=uiconst.UI_DISABLED)
                    DashedCircle(parent=hilightContainer, dashCount=4, lineWidth=0.8, radius=self.CIRCLESIZE / 2, range=math.pi * 2)
                    self.hilightContainer = hilightContainer
                if self.hilightState:
                    if not self.extraInfo:
                        self.extraInfo = ExtraInfoContainer(parent=self.markerContainer.parent, text=self.GetExtraMouseOverInfo(), top=self.textLabel.textheight, idx=0)
                        self.extraContainer = self.extraInfo
                        self.UpdateExtraContainer()
                    else:
                        self.extraInfo.SetText(self.GetExtraMouseOverInfo())
                elif self.extraInfo:
                    self.extraContainer = None
                    self.extraInfo.Close()
                    self.extraInfo = None
        else:
            if self.distanceFadeAlphaNearFar:
                self.projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]
            if self.hilightContainer:
                self.hilightContainer.Close()
                self.hilightContainer = None
            if self.extraInfo:
                self.extraContainer = None
                self.extraInfo.Close()
                self.extraInfo = None
        self.lastUpdateCameraValues = None

    def GetExtraContainerDisplayOffset(self):
        return (ScaleDpi(self.CIRCLESIZE + self.LABEL_LEFT_MARGIN), self.markerContainer.renderObject.displayHeight)


class ExtraInfoContainer(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_clipChildren = True
    default_cursor = uiconst.UICURSOR_POINTER

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.label = EveLabelSmall(parent=self, text=attributes.text, bold=True, state=uiconst.UI_NORMAL, opacity=0.8, cursor=uiconst.UICURSOR_POINTER)
        self.height = self.label.textheight
        self.width = self.label.textwidth
        animations.FadeTo(self, startVal=0.0, endVal=1.0, duration=0.1)
        animations.MorphScalar(self, 'displayWidth', 0, self.label.actualTextWidth, duration=0.2)

    def SetText(self, text):
        self.label.text = text
