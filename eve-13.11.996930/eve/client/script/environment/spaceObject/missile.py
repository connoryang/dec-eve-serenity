#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\missile.py
import math
import random
import audio2
import blue
import trinity
import telemetry
import geo2
import uthread
import evegraphics.settings as gfxsettings
import carbon.common.script.util.logUtil as log
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import inventorycommon.typeHelpers
SECOND = 10000000

class GlobalsGlob(object):

    def GetMissilesEnabled(self):
        missilesDesired = gfxsettings.Get(gfxsettings.UI_MISSILES_ENABLED)
        if missilesDesired:
            scene = self.GetSceneNonBlocking()
            if scene is None:
                return False
            updateTime = scene.updateTime
            now = blue.os.GetSimTime()
            if now < updateTime:
                return False
            delta = blue.os.TimeDiffInMs(updateTime, now)
            return delta < 2000
        return missilesDesired

    def Get_FileName_OwnerID_SourceShipID_SourceModuleIDList(self, missileID):
        bp = sm.StartService('michelle').GetBallpark()
        slimItem = bp.GetInvItem(missileID)
        fileName = inventorycommon.typeHelpers.GetGraphicFile(slimItem.typeID)
        ownerID = slimItem.ownerID
        sourceShipID = slimItem.sourceShipID
        sourceAllModulesID = slimItem.launchModules
        if fileName == '':
            log.LogError('missile::LoadModel failed to get red filename for missile typeID ' + str(slimItem.typeID) + ' missileID : ' + str(missileID) + ' sourceShipID: ' + str(sourceShipID))
            return None
        return (fileName,
         ownerID,
         sourceShipID,
         sourceAllModulesID)

    def GetScene(self):
        return sm.StartService('sceneManager').GetRegisteredScene('default')

    def GetSceneNonBlocking(self):
        return sm.StartService('sceneManager').registeredScenes.get('default', None)

    def GetTargetBall(self, targetId):
        bp = sm.StartService('michelle').GetBallpark()
        if bp is None:
            return
        targetBall = bp.GetBallById(targetId)
        return targetBall

    def GetTransCurveForBall(self, targetBall):
        return targetBall

    def SpawnClientBall(self, position):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        egopos = bp.GetCurrentEgoPos()
        explosionPosition = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
        return bp.AddClientSideBall(explosionPosition)

    def DestroyClientBall(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None and ball.ballpark is not None:
            bp.RemoveBall(ball.id)

    def GetFallbackDuration(self):
        return 8 * SECOND

    def PrepExplosionModel(self, explosionModel):
        pass

    def GetExplosionOverride(self, missileFilename):
        return None

    def GetTargetId(self, missile):
        return missile.followId

    def ShakeCamera(self, shakeMagnitude, explosionPosition):
        camera = sm.GetService('sceneManager').GetActiveCamera()
        camera.ShakeCamera(shakeMagnitude, explosionPosition, 'Missile')


_globalsGlob = GlobalsGlob()

def EstimateTimeToTarget(mslPos, targetPos, targetRadius, velocity):
    offset = mslPos - targetPos
    collisionTime = (offset.Length() - targetRadius) / velocity
    return collisionTime


def GetTransformedDamageLocator(eveship, locatorInd = -1):
    loccnt = eveship.GetDamageLocatorCount()
    if loccnt > 0 and locatorInd == -1:
        locatorInd = random.randint(0, loccnt - 1)
    return eveship.GetTransformedDamageLocator(locatorInd)


class Missile(SpaceObject):
    __guid__ = 'spaceObject.Missile'

    def __init__(self):
        SpaceObject.__init__(self)
        self.exploded = False
        self.collided = False
        self.targetId = None
        self.ownerID = None
        self.sourceShipID = None
        self.sourceModuleIDList = []
        self.delayedBall = None
        self.explosionPath = ''
        self.globalsGlob = _globalsGlob
        self.trinUseNonCached = False
        self.warheadsReleased = 0
        self.totalWarheadCount = 0
        self.delayedBall = None
        self.enabled = self.globalsGlob.GetMissilesEnabled()

    def _GetExplosionPath(self, missileFilename, append = ''):
        override = self.globalsGlob.GetExplosionOverride(missileFilename)
        if override is not None:
            return override
        result = missileFilename.lower().replace('_missile_', '_impact_')
        result = result.replace('_t1.red', append + '.red')
        return result

    @telemetry.ZONE_METHOD
    def LoadModel(self, fileName = None, loadedModel = None):
        if not self.enabled:
            return
        temp = self.globalsGlob.Get_FileName_OwnerID_SourceShipID_SourceModuleIDList(self.id)
        if temp is None:
            return
        self.missileFileName, self.ownerID, self.sourceShipID, self.sourceModuleIDList = temp
        self.targetId = self.globalsGlob.GetTargetId(self)
        self.model = blue.recycler.RecycleOrLoad(self.missileFileName)
        self.explosionPath = self._GetExplosionPath(self.missileFileName)
        if self.model is None:
            self.LogError('missile::LoadModel failed to load a model ' + str(self.missileFileName))
            return
        curves = self._GetModelTransRotCurves()
        self.model.translationCurve, self.model.rotationCurve = curves
        self.model.name = 'Missile in %s' % self.id
        scene = self.globalsGlob.GetScene()
        scene.objects.append(self.model)

    def _GetModelTransRotCurves(self):
        return (self, self)

    def _GetModelTurret(self, moduleIdx):
        if getattr(self, 'sourceModuleIDList', None) is None:
            return
        if len(self.sourceModuleIDList) <= moduleIdx:
            log.LogWarn('moduleIdx: + ' + str(moduleIdx) + ' is too high to index into list!')
            return
        slimItemID = self.sourceModuleIDList[moduleIdx]
        sourceShipBall = self.globalsGlob.GetTargetBall(self.sourceShipID)
        if sourceShipBall is not None:
            if not hasattr(sourceShipBall, 'modules'):
                return
            if sourceShipBall.modules is None:
                return
            if slimItemID in sourceShipBall.modules:
                return sourceShipBall.modules[slimItemID]

    def _GetModelStartTransformAndSpeed(self, muzzleID, moduleIdx):
        if not self.model:
            self.LogError('Missile::_GetModelStart with no model')
            return (None, None)
        now = blue.os.GetSimTime()
        q = self.model.rotationCurve.GetQuaternionAt(now)
        v = self.model.translationCurve.GetVectorAt(now)
        missileBallWorldTransform = geo2.MatrixAffineTransformation(1.0, (0.0, 0.0, 0.0), (q.x,
         q.y,
         q.z,
         q.w), (v.x, v.y, v.z))
        sourceShipBallWorldTransform = missileBallWorldTransform
        firingPosWorldTransform = missileBallWorldTransform
        sourceShipBallSpeed = (0.0, 0.0, 0.0)
        sourceTurretSet = self._GetModelTurret(moduleIdx)
        sourceShipBall = self.globalsGlob.GetTargetBall(self.sourceShipID)
        if sourceShipBall is not None:
            q = sourceShipBall.GetQuaternionAt(now)
            v = sourceShipBall.GetVectorAt(now)
            sourceShipBallWorldTransform = geo2.MatrixAffineTransformation(1.0, (0.0, 0.0, 0.0), (q.x,
             q.y,
             q.z,
             q.w), (v.x, v.y, v.z))
            s = sourceShipBall.GetVectorDotAt(now)
            sourceShipBallSpeed = (s.x, s.y, s.z)
            if sourceTurretSet is not None and len(sourceTurretSet.turretSets) > 0:
                gfxTS = sourceTurretSet.turretSets[0]
                firingPosWorldTransform = gfxTS.GetFiringBoneWorldTransform(gfxTS.currentCyclingFiresPos + muzzleID)
        invMissileBallWorldTransform = geo2.MatrixInverse(missileBallWorldTransform)
        startTransform = geo2.MatrixMultiply(firingPosWorldTransform, invMissileBallWorldTransform)
        startSpeed = geo2.Vec3TransformNormal(sourceShipBallSpeed, invMissileBallWorldTransform)
        return (startTransform, startSpeed)

    @telemetry.ZONE_METHOD
    def Prepare(self):
        if not self.enabled:
            return
        if self.collided:
            return
        SpaceObject.Prepare(self)
        if self.model is None:
            return
        if getattr(self, 'sourceModuleIDList', None) is None:
            self.sourceModuleIDList = [0]
        moduleCount = len(self.sourceModuleIDList)
        moduleCount = max(moduleCount, 1)
        timeToTarget = self.EstimateTimeToTarget()
        doSpread = True
        if timeToTarget < 1.6:
            self.DoCollision(self.targetId, 0, 0, 0)
            doSpread = False
        timeToTargetCenter = max(0.5, self.EstimateTimeToTarget(toCenter=True))
        if timeToTarget > 0:
            timeToTarget = (timeToTarget + timeToTargetCenter) * 0.5
        else:
            timeToTarget = timeToTargetCenter * 0.5
        if len(self.model.warheads) != 1:
            log.LogError('There must be one and only one warhead per missile in: ' + str(self.model.name))
            return
        warheadPrime = self.model.warheads[0]
        curvePrime = None
        bindingPrime = None
        curveSetPrime = None
        for cs in self.model.curveSets:
            for bindingToPrime in cs.bindings:
                if bindingToPrime.destinationObject == warheadPrime:
                    bindingToPrime.destinationObject = None
                    bindingPrime = bindingToPrime.CopyTo()
                    curveSetPrime = cs
                    curvePrime = bindingToPrime.sourceObject
                    cs.curves.remove(curvePrime)
                    cs.bindings.remove(bindingToPrime)
                    break

        del self.model.warheads[:]
        audioService = sm.GetService('audio')
        useWarheadBoosterAudio = audioService.GetMissileBoostersUsage()
        useDopplerEmitters = audioService.GetDopplerEmittersUsage()
        for moduleIdx in range(0, moduleCount):
            turret = self._GetModelTurret(moduleIdx)
            if turret is not None:
                turret.StartShooting()
            turretSet = None
            if turret is not None:
                if len(turret.turretSets) > 0:
                    turretSet = turret.turretSets[0]
            firingDelay = 0.0
            if turretSet is not None:
                firingDelay = turretSet.randomFiringDelay
            firingEffect = None
            if turretSet is not None:
                firingEffect = turretSet.firingEffect
            syncWarheadsCount = 1
            if turretSet is not None:
                if turretSet.maxCyclingFirePos == 1:
                    if turretSet.firingEffect is not None:
                        syncWarheadsCount = turretSet.firingEffect.GetPerMuzzleEffectCount()
            whKey = self.missileFileName + ':warhead'
            for i in range(0, syncWarheadsCount):
                wh = blue.recycler.RecycleOrCopy(whKey, warheadPrime)
                if bindingPrime is not None:
                    bd = bindingPrime.CopyTo()
                    bd.destinationObject = wh
                    curve = curvePrime.CopyTo()
                    bd.sourceObject = curve
                    curveSetPrime.curves.append(curve)
                    curveSetPrime.bindings.append(bd)
                startTransform, startSpeed = self._GetModelStartTransformAndSpeed(i, moduleIdx)
                wh.doSpread = doSpread
                muzzleDelay = getattr(firingEffect, 'firingDelay' + str(i + 1), 0.0)
                wh.PrepareLaunch()
                uthread.new(self._StartWarhead, wh, firingDelay + muzzleDelay, i, moduleIdx)
                wh.id = int(moduleIdx * syncWarheadsCount + i)
                if useWarheadBoosterAudio:
                    self._SetupMissileBoosterAudio(wh, useDopplerEmitters)
                self.model.warheads.append(wh)

            if self.targetId:
                targetBall = self.globalsGlob.GetTargetBall(self.targetId)
                if targetBall is not None:
                    self.model.target = targetBall.model
                    self.model.targetRadius = targetBall.radius
            self.model.explosionCallback = self.ExplosionCallback
            self.model.Start(startSpeed, timeToTarget)
            self.totalWarheadCount = syncWarheadsCount * moduleCount

        self.explosionManager.Preload(self.explosionPath, self.totalWarheadCount)

    @telemetry.ZONE_METHOD
    def RemoveAndClearModel(self, model, scene = None):
        if model is None:
            return
        if type(model) == trinity.EveMissile:
            del model.warheads[1:]
            whPrime = model.warheads[0]
            del whPrime.observers[:]
            for cs in model.curveSets:
                toKeep = []
                for binding in cs.bindings:
                    if type(binding.destinationObject) != trinity.EveMissileWarhead:
                        toKeep.append(binding)
                    elif binding.destinationObject == whPrime:
                        toKeep.append(binding)

                del cs.bindings[:]
                cs.bindings.extend(toKeep)

        SpaceObject.RemoveAndClearModel(self, model, scene=scene)

    def _StartWarhead(self, warhead, delay, warheadIdx, moduleIdx):
        blue.synchro.SleepSim(1000.0 * delay)
        if self.model is None:
            return
        startTransform, startSpeed = self._GetModelStartTransformAndSpeed(warheadIdx, moduleIdx)
        if startTransform is not None:
            warhead.Launch(startTransform)

    def EstimateTimeToTarget(self, toCenter = False):
        targetBall = self.globalsGlob.GetTargetBall(self.targetId)
        if targetBall is None:
            return 5.0
        now = blue.os.GetSimTime()
        myPos = self.model.translationCurve.GetVectorAt(now)
        targetPos = targetBall.GetVectorAt(now)
        if toCenter:
            targetRadius = 0
        else:
            targetRadius = targetBall.radius
        return EstimateTimeToTarget(myPos, targetPos, targetRadius, self.maxVelocity)

    def DoCollision(self, targetId, fx, fy, fz, fake = False):
        if self.collided:
            return
        self.collided = True
        if self.model is None:
            return
        uthread.new(self._DoCollision)

    def _DoCollision(self):
        if self.model is None:
            return
        if self.model.translationCurve is None:
            self.LogError('Missile::_DoCollision no translation curve')
            return
        pos = self.model.translationCurve.GetVectorAt(blue.os.GetSimTime())
        self.delayedBall = self.globalsGlob.SpawnClientBall((pos.x, pos.y, pos.z))
        self.model.translationCurve = self.delayedBall

    def Expire(self):
        self.exploded = True

    def _GetAudioPath(self, missileFilename):
        missileAudio = missileFilename.split('/')[-1:][0][8:-5]
        missileAudio = 'effects_missile_mexplosion_' + missileAudio.lower() + '_play'
        return missileAudio

    def _SetupMissileBoosterAudio(self, wh, useDopplerEmitter):
        del wh.observers[:]
        observer = trinity.TriObserverLocal()
        if useDopplerEmitter:
            emitter = audio2.AudEmitterDoppler('ship_%s_warhead' % id(wh), 'doppler_shift_d', 100)
        else:
            emitter = audio2.AudEmitter('ship_%s_booster' % id(wh))
        observer.observer = emitter
        emitter.SendEvent(u'ship_booster_angel_d_play')
        wh.observers.append(observer)

    def ExplosionCallback(self, warheadIdx):
        uthread.new(self._SpawnExplosion, warheadIdx)

    def _GetExplosionPosition(self, warheadIdx):
        if warheadIdx < len(self.model.warheads):
            warheadPosition = self.model.warheads[warheadIdx].explosionPosition
        else:
            warheadPosition = self.model.worldPosition
        return warheadPosition

    def _GetExplosionTargetLocator(self, warheadIdx):
        if warheadIdx < len(self.model.warheads):
            warheadTargetLocatorID = self.model.warheads[warheadIdx].targetLocatorID
        else:
            warheadTargetLocatorID = -1
        return warheadTargetLocatorID

    @telemetry.ZONE_METHOD
    def _SpawnExplosion(self, warheadIdx):
        if not self.model:
            self.LogWarn('Missile::_SpawnExplosion no model')
            return
        explosionPosition = self._GetExplosionPosition(warheadIdx)
        explosionTargetLocatorID = self._GetExplosionTargetLocator(warheadIdx)
        self.warheadsReleased += 1
        if self.exploded:
            return
        missileRadius = 100
        if self.model:
            missileRadius = self.model.boundingSphereRadius
        if self.warheadsReleased == self.totalWarheadCount:
            if self.model:
                self.model.target = None
                self.model.explosionCallback = None
                self.RemoveAndClearModel(self.model, self.globalsGlob.GetScene())
                self.model = None
            if self.delayedBall:
                self.globalsGlob.DestroyClientBall(self.delayedBall)
                self.delayedBall = None
            self.exploded = True
        actualModel = self.explosionManager.GetExplosion(self.explosionPath, preloaded=True, callback=self.CleanupExplosion)
        if actualModel is None:
            self.LogError('missile::LoadModel failed to get explosion ' + str(self.explosionPath))
            self.explosionManager.Cancel(self.explosionPath, 1)
            return
        explosionBall = None
        if self.enabled:
            explosionBall = self.globalsGlob.SpawnClientBall(explosionPosition)
            actualModel.translationCurve = explosionBall
            rndRotation = geo2.QuaternionRotationSetYawPitchRoll(random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi, random.random() * 2.0 * math.pi)
            actualModel.rotation = rndRotation
            scene = self.globalsGlob.GetScene()
            if scene is not None:
                scene.objects.append(actualModel)
                audio = audio2.AudEmitter('effect_source_%s' % str(id(self)))
                obs = trinity.TriObserverLocal()
                obs.front = (0.0, -1.0, 0.0)
                obs.observer = audio
                del actualModel.observers[:]
                actualModel.observers.append(obs)

                def AudioSetup(*args):
                    for eachSet in actualModel.active.curveSets:
                        for eachCurve in eachSet.curves:
                            if eachCurve.__typename__ == 'TriEventCurve':
                                audio.SendEvent(eachCurve.GetKeyValue(0))
                                break

                loadedEventHandler = blue.BlueEventToPython()
                loadedEventHandler.handler = AudioSetup
                actualModel.loadedCallback = loadedEventHandler
            shakeMagnitude = min(actualModel.boundingSphereRadius, 250)
            shakeMagnitude = max(shakeMagnitude, 50)
            self.globalsGlob.ShakeCamera(shakeMagnitude, explosionPosition)
            self.ApplyImpactTorqueToTarget(explosionTargetLocatorID, missileRadius)

    def ApplyImpactTorqueToTarget(self, targetLocatorID, blastSize):
        targetBall = self.globalsGlob.GetTargetBall(self.targetId)
        if hasattr(targetBall, 'ApplyTorqueAtDamageLocator') and targetLocatorID != -1 and not math.isnan(blastSize):
            velocity = self.GetVectorDotAt(blue.os.GetSimTime())
            targetBall.ApplyTorqueAtDamageLocator(targetLocatorID, (velocity.x, velocity.y, velocity.z), blastSize)

    @telemetry.ZONE_METHOD
    def CleanupExplosion(self, model):
        if model.translationCurve is not None:
            self.globalsGlob.DestroyClientBall(model.translationCurve)
        self.RemoveAndClearModel(model, self.globalsGlob.GetScene())
        if self.warheadsReleased == self.totalWarheadCount:
            self.ReleaseAll()

    def Explode(self):
        return self.collided

    @telemetry.ZONE_METHOD
    def Release(self, origin = None):
        if not self.collided and self.explodeOnRemove and self.enabled:
            self.Expire()
            self.ReleaseAll()

    def DoFinalCleanup(self):
        SpaceObject.DoFinalCleanup(self)
        self.ReleaseAll()

    def ReleaseAll(self):
        if self.model:
            self.model.target = None
            self.model.explosionCallback = None
            SpaceObject.Release(self, 'Missile')
        if self.delayedBall:
            self.globalsGlob.DestroyClientBall(self.delayedBall)
            self.delayedBall = None
        warheadsLeft = self.totalWarheadCount - self.warheadsReleased
        self.warheadsReleased = self.totalWarheadCount
        if warheadsLeft != 0:
            self.explosionManager.Cancel(self.explosionPath, count=warheadsLeft)

    def Display(self, display = 1, canYield = True):
        if self.enabled:
            SpaceObject.Display(self, display, canYield)


class Bomb(Missile):

    def Release(self):
        self._SpawnExplosion(0)
        SpaceObject.Release(self, 'Bomb')

    def EstimateTimeToTarget(self, toCenter = False):
        return 20.0

    def _GetExplosionPosition(self, warheadIdx):
        return self.model.worldPosition
