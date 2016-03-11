#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\spewContainer.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import evegraphics.settings as gfxsettings
import hackingcommon.hackingConstants as hackingConst

class SpewContainer(SpaceObject):

    def __init__(self):
        super(SpewContainer, self).__init__()
        self.explodeOnRemove = True

    def Assemble(self):
        self.UnSync()
        if self.model is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        slimItem = self.typeData.get('slimItem')
        if slimItem.hackingSecurityState is not None:
            state = slimItem.hackingSecurityState
        else:
            state = hackingConst.hackingStateSecure
        self.SetSecurityState(state)
        self.SetupSharedAmbientAudio()
        self.SetStaticRotation()

    def SetSecurityState(self, securityState):
        if securityState == hackingConst.hackingStateBeingHacked:
            self.TriggerAnimation('hacking')
        elif securityState == hackingConst.hackingStateHacked:
            self.TriggerAnimation('empty')
        elif securityState == hackingConst.hackingStateSecure:
            self.TriggerAnimation('idle')

    def Explode(self):
        if not gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            return False
        explosionURL, (delay, scaling) = self.GetExplosionInfo()
        return SpaceObject.Explode(self, explosionURL=explosionURL, managed=True, delay=delay, scaling=scaling)
