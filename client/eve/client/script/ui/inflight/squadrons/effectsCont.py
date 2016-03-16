#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\effectsCont.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.squadrons.effectController import EffectController
from eve.client.script.ui.inflight.squadrons.effectIcon import EffectIcon

class EffectsCont(ContainerAutoSize):
    default_width = 16
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.effectController = EffectController()
        self.DrawEffects()

    def DrawEffects(self):
        effects = self.controller.GetEffects()
        for effect in effects:
            self.AddEffect(effect)

    def AddEffect(self, effect):
        EffectIcon(parent=self, name=effect, controller=self.effectController, align=uiconst.TOBOTTOM)
