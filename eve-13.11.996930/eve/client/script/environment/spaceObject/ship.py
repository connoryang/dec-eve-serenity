#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\ship.py
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
from eveexceptions.exceptionEater import ExceptionEater
import evetypes
from inventorycommon.util import IsModularShip
import blue
import trinity
import uthread2
import uthread
import eve.common.lib.appConst as const
from eve.client.script.environment.model.turretSet import TurretSet
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.spaceObject.spaceObject import BOOSTER_GFX_SND_RESPATHS
from eveSpaceObject import spaceobjanimation
import eveSpaceObject.spaceobjaudio as spaceobjaudio
from uthread2.callthrottlers import CallCombiner
import locks
import destiny
import evegraphics.settings as gfxsettings
import evegraphics.utils as gfxutils
import geo2

class Ship(SpaceObject):
    __notifyevents__ = []

    def __init__(self):
        SpaceObject.__init__(self)
        self.activeTargetID = None
        self.fitted = False
        self.cachedShip = None
        self._skinChangeTasklet = None
        self.fittingThread = None
        self.turrets = []
        self.modules = {}
        self.stanceID = None
        self.lastStanceID = None
        self.isT3LoadingLockHeld = False
        self.burning = True
        self.loadingModel = False
        self.LoadT3ShipWithThrottle = CallCombiner(self.LoadT3Ship, 1.0)
        self._SkinLock = locks.RLock()
        self._modelChangeCallbacks = []

    def _LockT3Loading(self):
        uthread.Lock(self, 'LoadT3Model')
        self.isT3LoadingLockHeld = True

    def _UnlockT3Loading(self):
        if self.isT3LoadingLockHeld:
            uthread.UnLock(self, 'LoadT3Model')
            self.isT3LoadingLockHeld = False

    def LoadT3Ship(self):
        modules = self.typeData.get('slimItem').modules
        subsystems = {}
        self._LockT3Loading()
        self.loadingModel = True
        oldModel = self.model
        try:
            for _, typeID, _ in modules:
                if evetypes.GetCategoryID(typeID) == const.categorySubSystem:
                    subsystems[evetypes.GetGroupID(typeID)] = typeID

            t3ShipSvc = self.sm.GetService('t3ShipSvc')
            model = t3ShipSvc.GetTech3ShipFromDict(self.typeID, subsystems, self.typeData.get('sofRaceName', None))
            if model is not None:
                SpaceObject.LoadModel(self, None, loadedModel=model)
                self.Assemble()
            self.Display(1)
        finally:
            self.loadingModel = False
            self._UnlockT3Loading()

        if oldModel is not None:
            self.RemoveAndClearModel(oldModel)

    def IsModularShip(self):
        return IsModularShip(self.typeID)

    def LoadModel(self, fileName = None, loadedModel = None):
        if self.IsModularShip():
            self.LoadT3Ship()
        else:
            SpaceObject.LoadModel(self, fileName, loadedModel)
            self.Display(1)

    def OnSubSystemChanged(self, newSlim):
        self.typeData['slimItem'] = newSlim
        if self.model is None:
            self.LogError('OnSlimItemUpdated - no model to remove')
            return
        self.fitted = False
        uthread2.StartTasklet(self.LoadT3ShipWithThrottle)

    def GetStanceIDFromSlimItem(self, slimItem):
        if slimItem.shipStance is None:
            return
        _, _, stanceID = slimItem.shipStance
        return stanceID

    def OnDamageState(self, damageState):
        SpaceObject.OnDamageState(self, damageState)
        if self.model is not None and damageState is not None:
            states = [ (d if d is not None else 0.0) for d in damageState ]
            self.model.SetImpactDamageState(states[0], states[1], states[2], False)

    def OnSlimItemUpdated(self, slimItem):
        with ExceptionEater('ship::OnSlimItemUpdated failed'):
            oldSlim = self.typeData['slimItem']
            self.typeData['slimItem'] = slimItem
            stanceID = self.GetStanceIDFromSlimItem(self.typeData['slimItem'])
            if stanceID != self.stanceID:
                self.lastStanceID = self.stanceID
                self.stanceID = stanceID
                spaceobjanimation.SetShipAnimationStance(self.model, stanceID)
            if getattr(oldSlim, 'skinMaterialSetID') != getattr(slimItem, 'skinMaterialSetID'):
                uthread.new(self.ChangeSkin)

    def _SetInitialState(self):
        stanceID = self.GetStanceIDFromSlimItem(self.typeData['slimItem'])
        if stanceID is not None:
            self.stanceID = stanceID
            spaceobjanimation.SetShipAnimationStance(self.model, self.stanceID)
        if self.mode == destiny.DSTBALL_WARP:
            self.TriggerAnimation('warping')
            try:
                self.model.boosters.warpIntensity = 1
            except AttributeError:
                pass

            if session.shipid != self.id:
                self.sm.GetService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, 'effects.WarpIn', 0, 1, 0)
        elif self.GetCurrentAnimationState(spaceobjanimation.STATE_MACHINE_SHIP_STANDARD) is None:
            self.TriggerAnimation('normal')

    def _UpdateImpacts(self):
        states = self.GetDamageState()
        if states is not None and self.model is not None:
            damageState = [ (d if d is not None else 0.0) for d in states ]
            self.model.SetImpactDamageState(damageState[0], damageState[1], damageState[2], True)

    def Assemble(self):
        if self.model is None:
            return
        self.UnSync()
        if self.id == eve.session.shipid:
            self.FitHardpoints()
        self._SetInitialState()
        self._UpdateImpacts()

    def Release(self):
        self._UnlockT3Loading()
        if self.released:
            return
        if self.model is None:
            return
        self.modules = {}
        self.LoadT3ShipWithThrottle = None
        SpaceObject.Release(self, 'Ship')
        self._modelChangeCallbacks = []

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()
        audsvc = self.sm.GetServiceIfRunning('audio')
        if audsvc.active:
            lookedAt = audsvc.lastLookedAt
            if lookedAt is None:
                self.SetupAmbientAudio()
                audsvc.lastLookedAt = self
            elif lookedAt is not self:
                lookedAt.PlayGeneralAudioEvent('shipsounds_stop')
                self.SetupAmbientAudio()
                audsvc.lastLookedAt = self
            else:
                return

    def FitBoosters(self, alwaysOn = False, enableTrails = True, isNPC = False):
        if self.typeID is None:
            return
        raceName = self.typeData.get('sofRaceName', None)
        if raceName is None:
            self.LogError('SpaceObject type %s has invaldi raceID (not set!) ' % self.typeID)
            raceName = 'generic'
        boosterSoundName = BOOSTER_GFX_SND_RESPATHS[raceName][1]
        boosterResPath = BOOSTER_GFX_SND_RESPATHS[raceName][0]
        if self.model is None:
            self.LogWarn('No model to fit boosters to on spaceobject with id = ' + str(self.id))
            return
        if not hasattr(self.model, 'boosters'):
            self.LogWarn('Model has no attribute boosters on spaceobject with id = ' + str(self.id))
            return
        if self.model.boosters is None:
            boosterFxObj = trinity.Load(boosterResPath)
            if boosterFxObj is not None:
                self.model.boosters = boosterFxObj
                self.model.RebuildBoosterSet()
        self.model.boosters.maxVel = self.maxVelocity
        self.model.boosters.alwaysOn = alwaysOn
        if not enableTrails:
            self.model.boosters.trails = None
        slimItem = self.typeData['slimItem']
        groupID = slimItem.groupID
        tmpEntity, boosterAudioEvent = spaceobjaudio.GetBoosterEmitterAndEvent(self.model, groupID, boosterSoundName)
        if tmpEntity:
            self._audioEntities.append(tmpEntity)
            dogmaAttr = const.attributeMaxVelocity
            if isNPC:
                dogmaAttr = const.attributeEntityCruiseSpeed
            velocity = self.sm.GetService('godma').GetTypeAttribute(self.typeID, dogmaAttr)
            if velocity is None:
                velocity = 1.0
            self.model.maxSpeed = velocity
            spaceobjaudio.SendEvent(tmpEntity, boosterAudioEvent)

    def EnterWarp(self):
        for t in self.turrets:
            t.EnterWarp()

        self.TriggerAnimation('warping')
        try:
            self.model.boosters.warpIntensity = 1
        except AttributeError:
            pass

    def ExitWarp(self):
        for t in self.turrets:
            t.ExitWarp()

        self.TriggerAnimation('normal')
        try:
            self.model.boosters.warpIntensity = 0
        except AttributeError:
            pass

    def UnfitHardpoints(self):
        if not self.fitted:
            return
        newModules = {}
        for key, val in self.modules.iteritems():
            if val not in self.turrets:
                newModules[key] = val

        self.modules = newModules
        del self.turrets[:]
        self.fitted = False

    def FitHardpoints(self, blocking = False):
        if getattr(self.fittingThread, 'alive', False):
            self.fitted = False
            self.fittingThread.kill()
        if blocking:
            self._FitHardpoints()
        else:
            self.fittingThread = uthread2.StartTasklet(self._FitHardpoints)

    def _FitHardpoints(self):
        if self.fitted:
            return
        if self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        self.fitted = True
        newTurretSetDict = TurretSet.FitTurrets(self.id, self.model, self.typeData.get('sofFactionName', None))
        self.turrets = []
        for key, val in newTurretSetDict.iteritems():
            self.modules[key] = val
            self.turrets.append(val)

    def Explode(self):
        explosionPath, (delay, scaling) = self.GetExplosionInfo()
        if not self.exploded:
            self.sm.ScatterEvent('OnShipExplode', self.GetModel())
        return SpaceObject.Explode(self, explosionURL=explosionPath, managed=True, delay=delay, scaling=scaling)

    def RegisterModelChangeNotification(self, callback):
        self._modelChangeCallbacks.append(callback)

    def UnregisterModelChangeNotification(self, callback):
        if callback in self._modelChangeCallbacks:
            self._modelChangeCallbacks.remove(callback)

    def ChangeSkin(self):
        if self._skinChangeTasklet is not None:
            with self._SkinLock:
                if self._skinChangeTasklet is not None:
                    self._skinChangeTasklet.kill()
        self._skinChangeTasklet = uthread.new(self._ChangeSkin)

    def _ChangeSkin(self):
        with self._SkinLock:
            if self.model is None:
                return
            self.cachedShip = self.model
            self.cachedShip.clipSphereFactor = 0.0
            self.cachedShip.clipSphereCenter = (0.0, 0.0, 0.0)
            model = self._LoadModelResource(None)
            model.clipSphereFactor = 1.0
            model.activationStrength = 0.0
            blue.resMan.Wait()
            self.LoadModel(loadedModel=model)
            if gfxsettings.Get(gfxsettings.UI_SHIPSKINSINSPACE_ENABLED):
                effectDuration = 3000 + self.radius
                self.sm.GetService('FxSequencer').OnSpecialFX(self.id, None, None, None, None, 'effects.SkinChange', 0, 1, 0, duration=effectDuration)
            else:
                effectDuration = 0.0
            for callback in self._modelChangeCallbacks:
                callback(model)

            self.fitted = False
            self.Assemble()
            if not IsNewCameraActive():
                camera = sm.GetService('sceneManager').GetActiveCamera()
                cameraParent = camera.GetCameraParent()
                if cameraParent.parent and cameraParent.parent.name == self.model.name:
                    cameraParent.parent = self.model
            blue.synchro.SleepSim(effectDuration)
            self.RemoveAndClearModel(self.cachedShip)
            self.cachedShip = None
            if self.model:
                self.model.clipSphereFactor = 0.0
                self.model.activationStrength = 1.0

    def EnableLink(self, target, barrierRadius = None, barrierRadiusZone = None):
        invulLinkID = 21190
        if target is None:
            if self.model is not None:
                currentLinks = self.model.effectChildren.Find('trinity.EveChildLink')
                for l in currentLinks:
                    self.model.effectChildren.remove(l)

        else:
            path = gfxutils.GetResPathFromGraphicID(invulLinkID)
            if path is not None:
                linkFX = blue.resMan.LoadObject(path)
                linkFX.target = target
                linkFX.linkBarrier = barrierRadius
                linkFX.linkBarrierZone = barrierRadiusZone
                if self.model is not None:
                    self.model.effectChildren.append(linkFX)

    def ApplyTorqueAtDamageLocator(self, damageLocatorID, impactVelocity, impactObjectMass):
        if not self.model:
            return
        damageLocatorPosition = self.model.GetDamageLocator(damageLocatorID)
        bsCenter = geo2.Vector(*self.model.GetBoundingSphereCenter())
        damageLocatorPosition -= bsCenter
        q = self.GetQuaternionAt(blue.os.GetSimTime())
        damageLocatorPosition = geo2.QuaternionTransformVector((q.x,
         q.y,
         q.z,
         q.w), damageLocatorPosition)
        self.ApplyTorqueAtPosition(damageLocatorPosition, impactVelocity, impactObjectMass)

    def ApplyTorqueAtPosition(self, position, impactVelocity, impactObjectMass):
        if not self.model:
            return
        impactForce = geo2.Vec3Scale(impactVelocity, impactObjectMass)
        self.ApplyImpulsiveForceAtPosition(impactForce, geo2.Vector(*position))
