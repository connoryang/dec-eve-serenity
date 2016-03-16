#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\siegeMode.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class SiegeMode(GenericEffect):
    __guid__ = 'effects.SiegeMode'

    def Stop(self, reason = STOP_REASON_DEFAULT):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.TriggerAnimation('normal')

    def Prepare(self):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        graphicsID = shipBall.typeData['graphicID']

    def Start(self, duration):
        shipID = self.ballIDs[0]
        shipBall = self.fxSequencer.GetBall(shipID)
        shipBall.TriggerAnimation('siege')

    def Repeat(self, duration):
        pass
