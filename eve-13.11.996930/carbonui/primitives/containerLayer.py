#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\primitives\containerLayer.py
import trinity
from carbonui.primitives.container import Container
import carbonui.const as uiconst

class ContainerLayer(Container):
    __renderObject__ = trinity.Tr2Sprite2dLayer

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
