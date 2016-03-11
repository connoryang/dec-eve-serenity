#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\skinChange.py
from eve.client.script.environment.effects.GenericEffect import ShipRenderEffect

class SkinChange(ShipRenderEffect):
    __guid__ = 'effects.SkinChange'
    __gfxName__ = 'SkinChange'

    def Prepare(self):
        ShipRenderEffect.Prepare(self)
        self.gfx.name = self.__gfxName__
        shipBall = self.GetEffectShipBall()
        for binding in self.gfx.curveSet.bindings:
            if binding.name.startswith('new'):
                binding.destinationObject = self.sourceObject
            if binding.name.startswith('old'):
                binding.destinationObject = shipBall.cachedShip

        self.sourceObject.clipSphereCenter = (0.0, 0.0, 0.0)
        shipBall.cachedShip.clipSphereCenter = (0.0, 0.0, 0.0)

    def Start(self, duration):
        ShipRenderEffect.Start(self, duration)
        if duration < 9000:
            self.SendAudioEvent('ship_skin_change_play')
        else:
            self.SendAudioEvent('ship_skin_change_titan_play')
