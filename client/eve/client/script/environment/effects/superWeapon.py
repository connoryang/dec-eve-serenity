#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\superWeapon.py
import random
import geo2
import blue
from dogma.const import attributeDamageDelayDuration
import trinity
import uthread
import log
from eve.client.script.environment.effects.GenericEffect import StretchEffect, GetBoundingBox, STOP_REASON_DEFAULT
effectData = {'effects.SuperWeaponCaldari': {'count': 32,
                                'maxDelay': 2600,
                                'delayUntilShipHit': 10000},
 'effects.SuperWeaponMinmatar': {'count': 32,
                                 'maxDelay': 4000,
                                 'delayUntilShipHit': 1000,
                                 'delayBeforeEffect': 3000},
 'effects.SuperWeaponAmarr': {'count': 1,
                              'maxDelay': 0,
                              'delayUntilShipHit': 6208},
 'effects.SuperWeaponGallente': {'count': 1,
                                 'maxDelay': 0,
                                 'delayUntilShipHit': 4833},
 'effects.TurboLaser': {'count': 1,
                        'maxDelay': 0,
                        'delayUntilShipHit': 2500,
                        'impactMassFraction': 0.5,
                        'startLocation': trinity.EveLocalPositionBehavior.nearestBounds,
                        'destLocation': trinity.EveLocalPositionBehavior.nearestBounds}}

class SuperWeapon(StretchEffect):
    scene = trinity.device.scene

    def __init__(self, trigger, effect = None, graphicFile = None):
        StretchEffect.__init__(self, trigger, effect, graphicFile)
        data = effectData[trigger.guid]
        self.projectileCount = data['count']
        self.maxDelay = data['maxDelay']
        self.delayUntilShipHit = data['delayUntilShipHit']
        self.delayBeforeEffect = data.get('delayBeforeEffect', 0)
        self.delayUntilDamageApplied = self.fxSequencer.GetTypeAttribute(trigger.moduleTypeID, attributeDamageDelayDuration)
        self.impactMassFraction = data.get('impactMassFraction', 1.0)
        self.startLocation = data.get('startLocation', trinity.EveLocalPositionBehavior.damageLocator)
        self.destLocation = data.get('destLocation', trinity.EveLocalPositionBehavior.damageLocator)

    def IsTargetStillValid(self):
        targetBall = self.GetEffectTargetBall()
        return targetBall is not None and targetBall.model is not None

    def Prepare(self):
        pass

    def StartIndividual(self, duration, sourceBall, targetBall, rotation, direction):
        effect = self.RecycleOrLoad(self.graphicFile)
        effect.source = trinity.TriVectorSequencer()
        effect.source.operator = 1
        sourceLocation = trinity.EveLocalPositionCurve(self.startLocation)
        sourceLocation.parent = sourceBall.model
        sourceLocation.parentPositionCurve = sourceBall
        sourceLocation.parentRotationCurve = sourceBall
        sourceLocation.alignPositionCurve = targetBall
        sourceScale = GetBoundingBox(sourceBall, scale=1.2)
        sourceLocation.boundingSize = sourceScale
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
        destLocation = trinity.EveLocalPositionCurve(self.destLocation)
        destLocation.parent = targetBall.model
        destLocation.alignPositionCurve = sourceBall
        destLocation.parentPositionCurve = targetBall
        destLocation.parentRotationCurve = targetBall
        targetScale = GetBoundingBox(targetBall, scale=1.2)
        destLocation.boundingSize = targetScale
        effect.dest.functions.append(destLocation)
        destOffsetCurve = trinity.TriVectorCurve()
        if self.projectileCount > 1:
            offset = (random.gauss(0.0, 1000.0), random.gauss(0.0, 1000.0), random.gauss(0.0, 700.0) + 500.0)
        else:
            offset = (0, 0, self.destinationOffset)
        offset = geo2.QuaternionTransformVector(rotation, offset)
        destOffsetCurve.value = offset
        effect.dest.functions.append(destOffsetCurve)
        blue.synchro.SleepSim(self.delayBeforeEffect)
        delay = random.random() * self.maxDelay
        blue.synchro.SleepSim(delay)
        self.AddToScene(effect)
        effect.Start()
        blue.synchro.SleepSim(self.delayUntilShipHit)
        if self.IsTargetStillValid() and self.delayUntilDamageApplied is not None:
            impactMass = targetBall.mass * targetBall.model.boundingSphereRadius * self.impactMassFraction / (250.0 * self.projectileCount)
            targetShip = self.GetEffectTargetBall()
            targetShip.ApplyTorqueAtPosition(effect.dest.value, direction, impactMass)
            impactDirection = geo2.Vec3Scale(direction, -1.0)
            if self.projectileCount == 1:
                impactScale = 16.0 * self.impactMassFraction
            else:
                impactScale = 8.0 * self.impactMassFraction
            damageDuration = self.delayUntilDamageApplied - self.delayUntilShipHit + 500
            targetBall.model.CreateImpact(destLocation.damageLocatorIndex, impactDirection, damageDuration * 0.001, impactScale)
            blue.synchro.SleepSim(damageDuration)
            if self.projectileCount == 1 and self.IsTargetStillValid() and self.delayUntilDamageApplied is not None:
                targetBall.model.CreateImpact(destLocation.damageLocatorIndex, impactDirection, 3, impactScale)
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
        self.warmupDurationSeconds = trigger.graphicInfo.warmupDuration / 1000
        self.damageDurationSeconds = trigger.graphicInfo.damageDuration / 1000

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
        self.gfx.dest.delayTime = self.warmupDurationSeconds
        self.gfx.dest.sweepTime = self.damageDurationSeconds
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
