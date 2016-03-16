#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerSolarSystem.py
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.vectorlinetrace import DashedCircle
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import eve.client.script.ui.shared.mapView.mapViewConst as mapViewConst
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerSolarSystemBased
import carbonui.const as uiconst
import math
from carbonui.uianimations import animations
import localization
CIRCLESIZE = 14
LABEL_LEFT_MARGIN = 6

class MarkerLabelSolarSystem(MarkerSolarSystemBased):
    distanceFadeAlphaNearFar = (mapViewConst.MAX_MARKER_DISTANCE * 0.005, mapViewConst.MAX_MARKER_DISTANCE * 0.075)
    hilightContainer = None
    positionPickable = True
    extraInfo = None
    _cachedLabel = None

    def __init__(self, *args, **kwds):
        MarkerSolarSystemBased.__init__(self, *args, **kwds)
        self.typeID = const.typeSolarSystem
        self.itemID = self.markerID
        self.solarSystemID = self.markerID

    def Load(self):
        self.isLoaded = True
        labelLeft = CIRCLESIZE + LABEL_LEFT_MARGIN
        self.textLabel = EveLabelSmall(parent=self.markerContainer, text=self.GetLabelText(), bold=True, state=uiconst.UI_DISABLED, left=labelLeft)
        self.markerContainer.width = labelLeft + self.textLabel.textwidth
        self.markerContainer.height = self.textLabel.textheight
        Fill(bgParent=self.markerContainer, padding=(labelLeft - 2,
         0,
         -2,
         0), color=(0, 0, 0, 0.5))
        self.projectBracket.offsetX = ScaleDpi(self.markerContainer.width * 0.5 - CIRCLESIZE / 2)
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
                if self.hilightState:
                    if not self.hilightContainer:
                        hilightContainer = Container(parent=self.markerContainer, align=uiconst.CENTERLEFT, pos=(0,
                         0,
                         CIRCLESIZE,
                         CIRCLESIZE), state=uiconst.UI_DISABLED)
                        DashedCircle(parent=hilightContainer, dashCount=4, lineWidth=0.8, radius=CIRCLESIZE / 2, range=math.pi * 2)
                        self.hilightContainer = hilightContainer
                elif self.hilightContainer:
                    self.hilightContainer.Close()
                    self.hilightContainer = None
                if self.hilightState or self.activeState:
                    extraInfoText = self.GetExtraMouseOverInfo() or ''
                    lines = extraInfoText.split('<br>')
                    if len(lines) > 1 and not self.hilightState:
                        showExtraInfoText = localization.GetByLabel('UI/Map/ColorModeHandler/NumRecordsFound', count=len(lines))
                    else:
                        showExtraInfoText = extraInfoText
                    if not self.extraContainer:
                        self.extraContainer = ExtraInfoContainer(parent=self.markerContainer.parent, text=showExtraInfoText, top=self.textLabel.textheight, markerObject=self, idx=0)
                    else:
                        self.extraContainer.SetText(showExtraInfoText)
                    self.UpdateExtraContainer()
                elif self.extraContainer:
                    self.extraContainer.Close()
                    self.extraContainer = None
        else:
            if self.distanceFadeAlphaNearFar:
                self.projectBracket.maxDispRange = self.distanceFadeAlphaNearFar[1]
            if self.hilightContainer:
                self.hilightContainer.Close()
                self.hilightContainer = None
            if self.extraContainer:
                self.extraContainer.Close()
                self.extraContainer = None
        self.lastUpdateCameraValues = None

    def GetExtraContainerDisplayOffset(self):
        return (ScaleDpi(CIRCLESIZE + LABEL_LEFT_MARGIN), self.markerContainer.renderObject.displayHeight)


class ExtraInfoLabel(EveLabelSmall):

    def OnMouseEnter(self, *args):
        EveLabelSmall.OnMouseEnter(self, *args)
        self.parent.markerObject.markerHandler.HilightMarkers([self.parent.markerObject.markerID], add=True)


class ExtraInfoContainer(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_opacity = 0.0
    default_clipChildren = False
    default_cursor = uiconst.UICURSOR_POINTER

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.markerObject = attributes.markerObject
        self.label = ExtraInfoLabel(parent=self, text=attributes.text, bold=True, state=uiconst.UI_NORMAL, opacity=0.8, cursor=uiconst.UICURSOR_POINTER)
        self.UpdateSize()
        Fill(bgParent=self, padding=(-3, 0, -2, 0), color=(0, 0, 0, 0.4))
        animations.FadeTo(self, startVal=0.0, endVal=1.0, duration=0.1)
        animations.MorphScalar(self, 'displayWidth', 0, self.label.actualTextWidth, duration=0.2)

    def UpdateSize(self):
        self.height = self.label.textheight
        self.width = self.label.textwidth

    def Close(self, *args):
        Container.Close(self, *args)
        self.markerObject = None

    def SetText(self, text):
        self.label.text = text
        self.UpdateSize()
