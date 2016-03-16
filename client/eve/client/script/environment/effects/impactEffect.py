#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\impactEffect.py
__author__ = 'stevem'
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class ImpactEffect(GenericEffect):
    __guid__ = 'effects.ImpactEffect'

    def Start(self, duration):
        shipBall = self.GetEffectShipBall()
        model = getattr(shipBall, 'model', None)
        if model is not None:
            if self.animationName is not None:
                self.AddSoundToEffect(scaler=4.0, model=model)
                model.SetImpactAnimation(self.animationName, True, self.duration / 1000.0)
                event = 'ship_effect_%s_play' % self.animationName
                self.SendAudioEvent(event)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        shipBall = self.GetEffectShipBall()
        model = getattr(shipBall, 'model', None)
        if model is not None:
            if self.animationName is not None:
                model.SetImpactAnimation(self.animationName, False, self.duration / 1000.0)
                if self.animationName not in ('shieldboost', 'shieldhardening'):
                    event = 'ship_effect_%s_stop' % self.animationName
                    self.SendAudioEvent(event)

    def Repeat(self, duration):
        shipBall = self.GetEffectShipBall()
        model = getattr(shipBall, 'model', None)
        if model is not None:
            if self.animationName is not None:
                model.SetImpactAnimation(self.animationName, True, self.duration / 1000.0)
                event = 'ship_effect_%s_play' % self.animationName
                self.SendAudioEvent(event)
