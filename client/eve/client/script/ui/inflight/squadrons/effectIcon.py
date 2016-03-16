#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\effectIcon.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.frame import Frame

class EffectIcon(Container):
    default_width = 16
    default_height = 16
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        Frame(parent=self, color=(0.8, 0.2, 0.8, 0.2))
