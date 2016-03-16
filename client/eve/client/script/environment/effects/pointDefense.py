#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\pointDefense.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect

class PointDefense(GenericEffect):
    __guid__ = 'effects.PointDefense'

    def __init__(self, trigger, *args):
        GenericEffect.__init__(self, trigger, *args)
        self.ballpark = sm.GetService('michelle').GetBallpark()
        self.trigger = trigger

    def Prepare(self):
        pass

    def Start(self, duration):
        self.PlayDamageEffect()

    def Repeat(self, duration):
        self.PlayDamageEffect()

    def Stop(self, reason = None):
        pass

    def PlayDamageEffect(self):
        print 'PlayDamageEffect: ', self.GetTargets()

    def GetTargets(self):
        radius = self.fxSequencer.GetTypeAttribute(self.trigger.moduleTypeID, const.attributeEmpFieldRange)
        balls = self.ballpark.GetBallsInRange(self.trigger.shipID, radius)
        return balls
