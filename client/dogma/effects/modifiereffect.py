#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\modifiereffect.py
from dogma.effects import Effect
import dogma.const as dgmconst

def IsPassiveEffect(effectInfo):
    return effectInfo.effectCategory in dgmconst.dgmPassiveEffectCategories


class ModifierEffect(Effect):
    __modifier_only__ = True

    def __init__(self, effectInfo, modifiers):
        self.isPythonEffect = False
        self.__modifies_ship__ = IsPassiveEffect(effectInfo) and any((m.IsShipModifier() for m in modifiers))
        self.__modifies_character__ = IsPassiveEffect(effectInfo) and any((m.IsCharModifier() for m in modifiers))
        self.modifiers = modifiers

    def Start(self, *args):
        for modifier in self.modifiers:
            modifier.Start(*args)

    def Stop(self, *args):
        for modifier in self.modifiers:
            modifier.Stop(*args)

    RestrictedStop = Stop
