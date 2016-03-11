#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\locatorStretchEffect.py
import trinity
from eve.client.script.environment.effects.GenericEffect import StretchEffect, GetBoundingBox, STOP_REASON_DEFAULT

class LocatorStretchEffect(StretchEffect):
    __guid__ = 'effects.StretchEffect'

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        if shipBall is None:
            raise RuntimeError('LocatorStretchEffect: no ball found')
        if not getattr(shipBall, 'model', None):
            raise RuntimeError('LocatorStretchEffect: no model found')
        if targetBall is None:
            raise RuntimeError('LocatorStretchEffect: no target ball found')
        if not getattr(targetBall, 'model', None):
            raise RuntimeError('LocatorStretchEffect: no target model found')
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            raise RuntimeError('StretchEffect: no effect found: ' + str(getattr(self, 'graphicFile', 'None')))
        self.ScaleEffectAudioEmitters()
        self.gfxModel = self.gfx
        sourceBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.source = trinity.EveLocalPositionCurve(sourceBehavior)
        destBehavior = trinity.EveLocalPositionBehavior.damageLocator
        self.gfx.dest = trinity.EveLocalPositionCurve(destBehavior)
        self.gfx.source.parentPositionCurve = shipBall
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = self.gfx.dest
        self.gfx.dest.parent = targetBall.model
        self.gfx.dest.alignPositionCurve = shipBall
        sourceScale = GetBoundingBox(shipBall, scale=1.2)
        self.gfx.source.boundingSize = sourceScale
        self.AddToScene(self.gfxModel)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            raise RuntimeError('ShipEffect: no effect defined: ' + str(getattr(self, 'graphicFile', 'None')))
        if self.gfx.curveSets is not None and len(self.gfx.curveSets) > 0:
            self.FadeOutAudio()
        self.RemoveFromScene(self.gfxModel)
        self.gfx.source.parentPositionCurve = None
        self.gfx.source.parentRotationCurve = None
        self.gfx.source.alignPositionCurve = None
        self.gfx.source = None
        self.gfx.dest.parent = None
        self.gfx.dest.alignPositionCurve = None
        self.gfx.dest = None
        self.gfx = None
        self.gfxModel = None
