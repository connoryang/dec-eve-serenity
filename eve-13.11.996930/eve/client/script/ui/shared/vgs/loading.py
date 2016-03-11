#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\loading.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.vgs.label import VgsLabelLarge

class VgsLoadingPanel(Container):

    def ApplyAttributes(self, attributes):
        super(VgsLoadingPanel, self).ApplyAttributes(attributes)
        text = attributes.get('text', None)
        mainCont = ContainerAutoSize(parent=self, align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=1)
        wheelWrap = ContainerAutoSize(parent=mainCont, align=uiconst.TOTOP)
        VgsLoadingWheel(parent=wheelWrap, align=uiconst.CENTER)
        labelWrap = ContainerAutoSize(parent=mainCont, align=uiconst.TOTOP)
        VgsLabelLarge(parent=labelWrap, align=uiconst.CENTER, text=text)


class VgsLoadingWheel(Container):
    DEFAULT_SIZE = 72

    def ApplyAttributes(self, attributes):
        super(VgsLoadingWheel, self).ApplyAttributes(attributes)
        size = attributes.get('size') or self.DEFAULT_SIZE
        self.width = size
        self.height = size
        LoadingWheel(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=size, height=size, texturePath='res:/UI/Texture/Vgs/loading-bar-glow.png', color=(0.969, 0.522, 0.463, 1.0))
        Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=size, height=size, texturePath='res:/UI/Texture/Vgs/loading-track-overlay.png')
        LoadingWheel(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=size, height=size, texturePath='res:/UI/Texture/Vgs/loading-bar.png', color=(0.769, 0.322, 0.263, 1.0))
        Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=size, height=size, texturePath='res:/UI/Texture/Vgs/loading-track.png')
