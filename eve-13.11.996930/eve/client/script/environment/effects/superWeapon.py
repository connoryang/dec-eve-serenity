#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\superWeapon.py
import random
import geo2
import blue
import trinity
import uthread
import log
from eve.client.script.environment.effects.GenericEffect import StretchEffect, GetBoundingBox, GenericEffect, STOP_REASON_DEFAULT
effectData = {'effects.SuperWeaponCaldari': {'count': 32,
                                'maxDelay': 2600,
                                'delayUntilShipHit': 10000},
 'effects.SuperWeaponMinmatar': {'count': 32,
                                 'maxDelay': 3000,
                                 'delayUntilShipHit': 1000},
 'effects.SuperWeaponAmarr': {'count': 1,
                              'maxDelay': 0,
                              'delayUntilShipHit': 6208},
 'effects.SuperWeaponGallente': {'count': 1,
                                 'maxDelay': 0,
                                 'delayUntilShipHit': 4833}}

class SuperWeapon(StretchEffect):
    scene = trinity.device.scene

    def __init__(self, trigger, effect = None, graphicFile = None):
        StretchEffect.__init__(self, trigger, effect, graphicFile)
        data = effectData[trigger.guid]
        self.projectileCount = data['count']
        self.maxDelay = data['maxDelay']
        self.delayUntilShipHit = data['delayUntilShipHit']

    def Prepare(self):
        pass

    def StartIndividual(self, duration, sourceBall, targetBall, rotation, direction):
        effect = self.RecycleOrLoad(self.graphicFile)
        effect.source = trinity.TriVectorSequencer()
        effect.source.operator = 1
        sourceLocation = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.damageLocator)
        sourceLocation.parent = sourceBall.model
        sourceLocation.alignPositionCurve = targetBall
        effect.source.functions.append(sourceLocation)
        sourceOffsetCurve = trinity.TriVectorCurve()
        if self.projectileCount > 1:
            offset = (random.gauss(0.0, 1000.0), random.gauss(0.0, 1000.0), random.gauss(0.0, 700.0) - 2000.0)
        else:
            offset = (0, 0, -self.sourceOffset)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        sourceOffsetCurve.value = offset
        effect.source.functions.append(sourceOffsetCurve)
        effect.dest = trinity.TriVectorSequencer()
        effect.dest.operator = 1
        destLocation = trinity.EveLocalPositionCurve(trinity.EveLocalPositionBehavior.damageLocator)
        destLocation.parent = targetBall.model
        destLocation.alignPositionCurve = sourceBall
        effect.dest.functions.append(destLocation)
        destOffsetCurve = trinity.TriVectorCurve()
        if self.projectileCount > 1:
            offset = (random.gauss(0.0, 1000.0), random.gauss(0.0, 1000.0), random.gauss(0.0, 700.0) + 500.0)
        else:
            offset = (0, 0, self.destinationOffset)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        destOffsetCurve.value = offset
        effect.dest.functions.append(destOffsetCurve)
        delay = random.random() * self.maxDelay
        blue.synchro.SleepSim(delay)
        self.AddToScene(effect)
        effect.Start()
        blue.synchro.SleepSim(self.delayUntilShipHit)
        if targetBall.model is not None:
            impactMass = targetBall.mass * targetBall.model.boundingSphereRadius * 2.0 / (250.0 * self.projectileCount)
            targetShip = sm.GetService('michelle').GetBall(targetBall.id)
            targetShip.ApplyTorqueAtPosition(effect.dest.value, direction, impactMass)
        blue.synchro.SleepSim(duration * 3)
        self.RemoveFromScene(effect)
        sourceLocation.parent = None
        sourceLocation.alignPositionCurve = None
        destLocation.parent = None
        destLocation.alignPositionCurve = None

    def Start(self, duration):
        sourceBall = self.GetEffectShipBall()
        targetBall = self.GetEffectTargetBall()
        sourcePos = sourceBall.GetVectorAt(blue.os.GetSimTime())
        sourcePos = (sourcePos.x, sourcePos.y, sourcePos.z)
        targetPos = targetBall.GetVectorAt(blue.os.GetSimTime())
        targetPos = (targetPos.x, targetPos.y, targetPos.z)
        direction = geo2.Vec3Direction(sourcePos, targetPos)
        rotation = geo2.QuaternionRotationArc((0, 0, 1), direction)
        direction = geo2.Vec3Scale(direction, -1.0)
        for x in range(self.projectileCount):
            uthread.new(self.StartIndividual, duration, sourceBall, targetBall, rotation, direction)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        pass

    def ScaleEffectAudioEmitters(self):
        pass


class SlashWeapon(StretchEffect):

    def __init__(self, trigger, *args):
        StretchEffect.__init__(self, trigger, *args)
        self.startTargetOffset = trigger.graphicInfo.startTargetOffset
        self.endTargetOffset = trigger.graphicInfo.endTargetOffset

    def Prepare(self):
        shipBall = self.GetEffectShipBall()
        self.gfx = self.RecycleOrLoad(self.graphicFile)
        if self.gfx is None:
            log.LogError('effect not found: ' + str(self.graphicFile))
            return
        self.gfx.dest = trinity.EveRemotePositionCurve()
        self.gfx.dest.startPositionCurve = shipBall
        self.gfx.dest.offsetDir1 = self.startTargetOffset
        self.gfx.dest.offsetDir2 = self.endTargetOffset
        self.gfx.dest.delayTime = 10.0
        self.gfx.dest.sweepTime = 10.0
        sourceBehavior = trinity.EveLocalPositionBehavior.nearestBounds
        self.gfx.source = trinity.EveLocalPositionCurve(sourceBehavior)
        self.gfx.source.offset = self.sourceOffset
        self.gfx.source.parentPositionCurve = shipBall
        self.gfx.source.parentRotationCurve = shipBall
        self.gfx.source.alignPositionCurve = self.gfx.dest
        self.gfx.source.boundingSize = GetBoundingBox(shipBall, scale=1.2)
        self.AddToScene(self.gfx)

    def Start(self, duration):
        StretchEffect.Start(self, duration)

    def Stop(self, reason = STOP_REASON_DEFAULT):
        if self.gfx is None:
            return
        self.RemoveFromScene(self.gfx)
        self.gfx.source.parentPositionCurve = None
        self.gfx.source.parentRotationCurve = None
        self.gfx.source.alignPositionCurve = None
        self.gfx.dest.startPositionCurve = None
        self.gfx = None
        self.gfxModel = None
