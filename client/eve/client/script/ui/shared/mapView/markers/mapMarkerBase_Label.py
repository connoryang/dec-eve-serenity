#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\markers\mapMarkerBase_Label.py
from carbon.common.script.util.commonutils import StripTags
from carbonui.primitives.base import ScaleDpi, ReverseScaleDpi
from eve.client.script.ui.shared.mapView.markers.mapMarkerBase import MarkerUniverseBased
import trinity

class MarkerLabelBase(MarkerUniverseBased):
    fontSize = 10
    fontColor = (1.0, 1.0, 1.0, 0.6)
    fontPath = 'res:/UI/Fonts/EveSansNeue-ExpandedBold.otf'
    letterSpace = 0
    textSprite = None
    measurer = None

    def DestroyRenderObject(self):
        if self.textSprite:
            self.textSprite.fontMeasurer = None
        self.textSprite = None
        self.measurer = None
        MarkerUniverseBased.DestroyRenderObject(self)

    def GetLabelText(self):
        return cfg.evelocations.Get(self.markerID).name

    def Load(self):
        self.isLoaded = True
        if self.measurer is None:
            measurer = trinity.Tr2FontMeasurer()
            measurer.limit = 0
            measurer.font = self.fontPath
            measurer.fontSize = ScaleDpi(self.fontSize)
            measurer.letterSpace = ScaleDpi(self.letterSpace)
            measurer.AddText(StripTags(self.GetLabelText()))
            measurer.CommitText(0, measurer.ascender)
            self.measurer = measurer
        textSprite = trinity.Tr2Sprite2dTextObject()
        textSprite.fontMeasurer = self.measurer
        textSprite.color = self.fontColor
        textSprite.blendMode = trinity.TR2_SBM_BLEND
        self.markerContainer.renderObject.children.append(textSprite)
        self.textSprite = textSprite
        height = self.measurer.ascender - self.measurer.descender
        width = self.measurer.cursorX
        self.textSprite.textWidth = width
        self.textSprite.textHeight = height
        self.markerContainer.pos = (0,
         0,
         ReverseScaleDpi(width),
         ReverseScaleDpi(height))
