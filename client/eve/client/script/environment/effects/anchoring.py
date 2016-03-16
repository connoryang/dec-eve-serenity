#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\anchoring.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT

class AnchoringEffect(GenericEffect):

    def __init__(self, trigger, *args):
        GenericEffect.__init__(self, trigger, *args)
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None

    def SetState(self, stateName):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if hasattr(ball, 'SetColor'):
            ball.SetColor(stateName)


class AnchorDrop(AnchoringEffect):
    __guid__ = 'effects.AnchorDrop'

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if hasattr(ball, 'BeginStructureAnchoring'):
            self.fxSequencer.LogInfo('AnchorDrop: calling BeginStructureAnchoring')
            ball.BeginStructureAnchoring(self.timeFromStart)
        else:
            self.SetState('yellow')
            AnchoringEffect.Start(self, duration)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if not hasattr(ball, 'BeginStructureAnchoring'):
            self.SetState('red')
            AnchoringEffect.Stop(self)


class AnchorLift(AnchoringEffect):
    __guid__ = 'effects.AnchorLift'

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if hasattr(ball, 'BeginStructureUnAnchoring'):
            self.fxSequencer.LogInfo('AnchorDrop: calling BeginStructureUnAnchoring ')
            ball.BeginStructureUnAnchoring(self.timeFromStart)
        else:
            self.SetState('yellow')
            AnchoringEffect.Start(self, duration)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        if not hasattr(ball, 'SetCapsuleGraphics'):
            self.SetState('green')
            AnchoringEffect.Stop(self)
