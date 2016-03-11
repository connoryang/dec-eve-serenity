#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\accelerationGate.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect

class AccelerationGate(GenericEffect):
    __guid__ = 'effects.WarpGateEffect'

    def Start(self, duration):
        gateID = self.GetEffectShipID()
        targetID = self.GetEffectTargetID()
        gateBall = self.GetEffectShipBall()
        slimItem = self.fxSequencer.GetItem(gateID)
        sm.GetService('dungeonChecker').enteringDungeon = True
        if slimItem.dunMusicUrl is not None and targetID == eve.session.shipid:
            sm.GetService('audio').SendUIEvent(slimItem.dunMusicUrl.lower())
        self.PlayNamedAnimations(gateBall.model, 'Activation')
