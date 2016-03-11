#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\sceneManager.py
from math import asin, atan2
import blue
import telemetry
from eve.client.script.ui.camera import cameraClsByCameraID
from eve.client.script.ui.camera.cameraBase import CameraBase
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
import evecamera
import util
import log
import trinity
import service
import nodemanager
import locks
import geo2
import sys
import evegraphics.settings as gfxsettings
import evegraphics.utils as gfxutils
from eve.client.script.parklife.sceneManagerConsts import *
from eve.client.script.ui.view.viewStateConst import ViewState

class SceneContext:

    def __init__(self, scene = None, camera = None, sceneKey = 'default', sceneType = None, renderJob = None):
        self.scene = scene
        self.camera = camera
        self.sceneKey = sceneKey
        self.sceneType = sceneType
        self.renderJob = renderJob
        self.activeCameraMode = None


class SceneManager(service.Service):
    __guid__ = 'svc.sceneManager'
    __exportedcalls__ = {'LoadScene': [],
     'GetScene': [],
     'GetIncarnaRenderJob': [],
     'EnableIncarnaRendering': []}
    __startupdependencies__ = ['settings', 'device']
    __notifyevents__ = ['OnGraphicSettingsChanged', 'OnSessionChanged']

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.registeredScenes = {}
        self.registeredCameras = {}
        self.sceneLoadedEvents = {}
        self.registeredJobs = []
        self.cameraOffsetOverride = None
        self.uiBackdropScene = None
        self.ProcessImportsAndCreateScenes()
        self.primaryJob = SceneContext()
        self.secondaryJob = None
        self.activeCameraMode = None
        self.loadingClearJob = trinity.CreateRenderJob()
        self.loadingClearJob.name = 'loadingClear'
        self.loadingClearJob.Clear((0, 0, 0, 1))
        self.loadingClearJob.enabled = False
        self.overlaySceneKeys = [ViewState.StarMap,
         ViewState.SystemMap,
         ViewState.Planet,
         ViewState.ShipTree,
         ViewState.DockPanel]
        self._sharedResources = {}
        self.routeVisualizer = None
        self.podDeathScene = None
        self.particlePoolManager = trinity.Tr2GPUParticlePoolManager()
        if '/skiprun' not in blue.pyos.GetArg():
            self._EnableLoadingClear()
        limit = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY) * 30
        self.explosionManager = util.ExplosionManager(limit)

    def ProcessImportsAndCreateScenes(self):
        from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
        from trinity.eveSceneRenderJobInterior import CreateEveSceneRenderJobInterior
        from trinity.sceneRenderJobCharacters import CreateSceneRenderJobCharacters
        self.fisRenderJob = CreateSceneRenderJobSpace('SpaceScenePrimary')
        self.incarnaRenderJob = CreateEveSceneRenderJobInterior()
        self.characterRenderJob = CreateSceneRenderJobCharacters()
        self._CreateJobInterior()
        self._CreateJobCharCreation()
        self._CreateJobFiS()

    def _EnableLoadingClear(self):
        if not self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = True
            trinity.renderJobs.recurring.insert(0, self.loadingClearJob)

    def _DisableLoadingClear(self):
        if self.loadingClearJob.enabled:
            self.loadingClearJob.enabled = False
            trinity.renderJobs.recurring.remove(self.loadingClearJob)

    def EnableIncarnaRendering(self):
        self._DisableLoadingClear()
        if self.secondaryJob is None:
            self.incarnaRenderJob.Enable()

    def RefreshJob(self, camera):
        sceneType = self.primaryJob.sceneType
        if sceneType == SCENE_TYPE_INTERIOR or sceneType == SCENE_TYPE_CHARACTER_CREATION:
            self.primaryJob.renderJob.SetActiveCamera(camera)
            uicore.uilib.SetSceneView(camera.viewMatrix, camera.projectionMatrix)

    def _CreateJobInterior(self):
        rj = self.incarnaRenderJob
        rj.CreateBasicRenderSteps()
        rj.EnableSceneUpdate(True)
        rj.EnableVisibilityQuery(True)

    def _CreateJobCharCreation(self):
        self.characterRenderJob.CreateBasicRenderSteps()
        self.characterRenderJob.EnableShadows(True)
        self.characterRenderJob.EnableScatter(True)
        self.characterRenderJob.EnableSculpting(True)
        self.characterRenderJob.Set2DBackdropScene(self.uiBackdropScene)

    def _CreateJobFiS(self, rj = None):
        if rj is None:
            rj = self.fisRenderJob
        rj.CreateBasicRenderSteps()
        rj.EnablePostProcessing(True)

    def GetFiSPostProcessingJob(self):
        return self.fisRenderJob.postProcessingJob

    def ApplyClothSimulationSettings(self):
        if 'character' not in sm.services:
            return
        if self.primaryJob.sceneType == SCENE_TYPE_INTERIOR:
            clothSimulation = sm.GetService('device').GetAppFeatureState('Interior.clothSimulation', False)
            sm.GetService('character').EnableClothSimulation(clothSimulation)
        elif self.primaryJob.sceneType == SCENE_TYPE_CHARACTER_CREATION:
            clothSimulation = sm.GetService('device').GetAppFeatureState('CharacterCreation.clothSimulation', True)
            sm.GetService('character').EnableClothSimulation(clothSimulation)

    def OnGraphicSettingsChanged(self, changes):
        self.incarnaRenderJob.SetSettingsBasedOnPerformancePreferences()
        self.fisRenderJob.SetSettingsBasedOnPerformancePreferences()
        self.characterRenderJob.SetSettingsBasedOnPerformancePreferences()
        if self.secondaryJob is not None:
            self.secondaryJob.renderJob.SetSettingsBasedOnPerformancePreferences()
        for each in self.registeredJobs:
            each.object.SetSettingsBasedOnPerformancePreferences()

        if gfxsettings.GFX_INTERIOR_GRAPHICS_QUALITY in changes or gfxsettings.GFX_CHAR_CLOTH_SIMULATION in changes:
            self.ApplyClothSimulationSettings()
        if gfxsettings.GFX_LOD_QUALITY in changes:
            limit = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY) * 30
            self.explosionManager.SetLimit(limit)
        if gfxsettings.UI_CAMERA_OFFSET in changes:
            self.CheckCameraOffsets()
        if gfxsettings.UI_INCARNA_CAMERA_OFFSET in changes:
            sm.GetService('cameraClient').CheckCameraOffsets()
        if gfxsettings.UI_INCARNA_CAMERA_MOUSE_LOOK_SPEED in changes:
            sm.GetService('cameraClient').CheckMouseLookSpeed()
        if gfxsettings.MISC_LOAD_STATION_ENV in changes:
            val = gfxsettings.Get(gfxsettings.MISC_LOAD_STATION_ENV)
            if sm.GetService('viewState').IsViewActive('hangar') and not val:
                sm.GetService('station').ReloadLobby()
        if session.userid is not None:
            effectsEnabled = gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED)
            if gfxsettings.UI_TRAILS_ENABLED in changes or gfxsettings.UI_EFFECTS_ENABLED in changes:
                trailsEnabled = effectsEnabled and gfxsettings.Get(gfxsettings.UI_TRAILS_ENABLED)
                trinity.settings.SetValue('eveSpaceObjectTrailsEnabled', trailsEnabled)
            if gfxsettings.UI_GPU_PARTICLES_ENABLED in changes or gfxsettings.UI_EFFECTS_ENABLED in changes:
                gpuParticlesEnabled = effectsEnabled and gfxsettings.Get(gfxsettings.UI_GPU_PARTICLES_ENABLED)
                trinity.settings.SetValue('gpuParticlesEnabled', gpuParticlesEnabled)
            if gfxsettings.UI_GODRAYS in changes:
                scene = self.GetRegisteredScene('default')
                if scene is not None and scene.sunBall is not None:
                    scene.sunBall.HandleGodraySetting()

    def GetIncarnaRenderJob(self):
        return self.incarnaRenderJob

    def GetIncarnaRenderJobVisualizationsMenu(self):
        return self.incarnaRenderJob.GetInsiderVisualizationMenu()

    def SetupIncarnaBackground(self, scene, sceneTranslation, sceneRotation):
        if scene is not None:
            self.incarnaRenderJob.SetBackgroundScene(scene)
            self.backgroundView = trinity.TriView()
            self.backgroundProjection = trinity.TriProjection()
            backGroundCameraUpdateFunction = self.incarnaRenderJob.GetBackgroundCameraUpdateFunction(self.backgroundView, self.backgroundProjection, 10.0, 40000.0, sceneTranslation, sceneRotation)
            self.incarnaRenderJob.SetBackgroundCameraViewAndProjection(self.backgroundView, self.backgroundProjection, backGroundCameraUpdateFunction)

    @telemetry.ZONE_METHOD
    def OnSessionChanged(self, isremote, session, change):
        if 'locationid' in change:
            newLocationID = change['locationid'][1]
            if util.IsSolarSystem(newLocationID) and self.primaryJob.sceneType != SCENE_TYPE_SPACE:
                log.LogWarn('SceneManager: I detected a session change into space but no one has bothered to update my scene type!')
                self.SetSceneType(SCENE_TYPE_SPACE)

    @telemetry.ZONE_METHOD
    def SetSceneType(self, sceneType):
        if self.primaryJob.sceneType == sceneType:
            if sceneType == SCENE_TYPE_INTERIOR:
                self._EnableLoadingClear()
            return
        self.primaryJob = SceneContext(sceneType=sceneType)
        if sceneType == SCENE_TYPE_INTERIOR:
            log.LogInfo('Setting up WiS interior scene rendering')
            self.primaryJob.renderJob = self.incarnaRenderJob
            self.characterRenderJob.Disable()
            self.fisRenderJob.SetActiveScene(None)
            self.fisRenderJob.Disable()
            for each in self.registeredJobs:
                each.object.UseFXAA(True)

            self.ApplyClothSimulationSettings()
            if getattr(self.secondaryJob, 'sceneType', None) == SCENE_TYPE_SPACE:
                self.secondaryJob.renderJob.UseFXAA(True)
            else:
                self._EnableLoadingClear()
        elif sceneType == SCENE_TYPE_CHARACTER_CREATION:
            log.LogInfo('Setting up character creation scene rendering')
            self.primaryJob.renderJob = self.characterRenderJob
            self.incarnaRenderJob.SetScene(None)
            self.incarnaRenderJob.SetBackgroundScene(None)
            self.incarnaRenderJob.Disable()
            self.fisRenderJob.SetActiveScene(None)
            self.fisRenderJob.Disable()
            self.ApplyClothSimulationSettings()
            self._DisableLoadingClear()
            self.characterRenderJob.Enable()
        elif sceneType == SCENE_TYPE_SPACE:
            log.LogInfo('Setting up space scene rendering')
            self.primaryJob.renderJob = self.fisRenderJob
            self.incarnaRenderJob.SetScene(None)
            self.incarnaRenderJob.SetBackgroundScene(None)
            self.incarnaRenderJob.Disable()
            self.characterRenderJob.SetScene(None)
            self.characterRenderJob.Disable()
            self.fisRenderJob.UseFXAA(False)
            for each in self.registeredJobs:
                each.object.UseFXAA(False)

            self._DisableLoadingClear()
            if getattr(self.secondaryJob, 'sceneType', None) == SCENE_TYPE_SPACE:
                self.secondaryJob.renderJob.UseFXAA(False)
            if self.secondaryJob is None:
                self.fisRenderJob.Enable()

    @telemetry.ZONE_METHOD
    def Initialize(self, scene):
        self.uiBackdropScene = trinity.Tr2Sprite2dScene()
        self.uiBackdropScene.isFullscreen = True
        self.uiBackdropScene.backgroundColor = (0, 0, 0, 1)
        self.characterRenderJob.Set2DBackdropScene(self.uiBackdropScene)
        self.primaryJob = SceneContext(scene=scene, renderJob=self.fisRenderJob)

    def _ApplyCamera(self, jobContext, camera, **kwargs):
        currCam = self.GetActiveCamera()
        jobContext.camera = camera
        if jobContext.renderJob is not None:
            if isinstance(camera, CameraBase):
                jobContext.renderJob.SetActiveCamera(camera.GetTrinityCamera())
            elif isinstance(camera, trinity.EveCamera):
                jobContext.renderJob.SetActiveCamera(camera)
            else:
                jobContext.renderJob.SetActiveCamera(None, camera.viewMatrix, camera.projectionMatrix)
        if hasattr(camera, 'cameraID'):
            sm.ScatterEvent('OnActiveCameraChanged', camera.cameraID)
            if camera.cameraID in evecamera.INSPACE_CAMERAS:
                self.UpdateSceneCameraReferences(camera)
            if camera.cameraID in evecamera.INSPACE_CAMERAS_MAIN:
                self.activeCameraMode = camera.cameraID
        if hasattr(camera, 'OnActivated'):
            camera.OnActivated(lastCamera=currCam, **kwargs)
        if currCam and hasattr(currCam, 'OnDeactivated'):
            currCam.OnDeactivated()

    def GetActiveCameraMode(self):
        return self.activeCameraMode

    def UpdateSceneCameraReferences(self, camera):
        scene = self.GetRegisteredScene('default')
        if not scene:
            return
        if scene.dustfieldConstraint:
            scene.dustfieldConstraint.cameraView = camera.viewMatrix
        if scene.cloudfieldConstraint:
            scene.cloudfieldConstraint.cameraView = camera.viewMatrix
        for distanceField in scene.distanceFields:
            distanceField.cameraView = camera.viewMatrix

    @telemetry.ZONE_METHOD
    def SetActiveCamera(self, camera, **kwargs):
        uicore.uilib.SetSceneCamera(camera)
        if camera == self.GetActiveCamera():
            return
        if self.secondaryJob is None:
            renderJob = self.primaryJob
        else:
            renderJob = self.secondaryJob
        self._ApplyCamera(renderJob, camera, **kwargs)

    def SetActiveCameraByID(self, cameraID, **kwargs):
        activeCam = self.GetActiveCamera()
        if activeCam and activeCam.cameraID == cameraID:
            return
        camera = self._GetOrCreateCamera(cameraID)
        self.SetActiveCamera(camera, **kwargs)
        return camera

    def _SetActiveCameraForScene(self, camera, sceneKey):
        if self.secondaryJob is not None and self.secondaryJob.sceneKey == sceneKey:
            self.SetActiveCamera(camera)
        elif self.primaryJob.sceneKey == sceneKey:
            self._ApplyCamera(self.primaryJob, camera)
            if self.secondaryJob is None:
                uicore.uilib.SetSceneCamera(camera)

    @telemetry.ZONE_METHOD
    def SetSecondaryScene(self, scene, sceneKey, sceneType):
        if sceneType == SCENE_TYPE_SPACE:
            newJob = self.secondaryJob is None
            if newJob:
                from trinity.sceneRenderJobSpace import CreateSceneRenderJobSpace
                self.secondaryJob = SceneContext(scene=scene, sceneKey=sceneKey, sceneType=sceneType)
                self.secondaryJob.renderJob = CreateSceneRenderJobSpace('SpaceSceneSecondary')
                self._CreateJobFiS(self.secondaryJob.renderJob)
            else:
                self.secondaryJob.scene = scene
                self.secondaryJob.sceneKey = sceneKey
            self.secondaryJob.renderJob.SetActiveScene(scene, sceneKey)
            self.secondaryJob.renderJob.UseFXAA(self.primaryJob.sceneType != SCENE_TYPE_SPACE)
            if newJob:
                self.secondaryJob.renderJob.Enable()

    def ClearSecondaryScene(self):
        if self.secondaryJob is None:
            return
        if self.secondaryJob.renderJob is not None:
            self.secondaryJob.renderJob.Disable()
        self.secondaryJob = None

    def SetActiveScene(self, scene, sceneKey = None):
        sceneType = SCENE_TYPE_INTERIOR
        if getattr(scene, '__bluetype__', None) == 'trinity.EveSpaceScene':
            sceneType = SCENE_TYPE_SPACE
        if sceneKey in self.overlaySceneKeys:
            self.primaryJob.renderJob.SuspendRendering()
            self.SetSecondaryScene(scene, sceneKey, sceneType)
        elif sceneType == SCENE_TYPE_SPACE:
            self.primaryJob.sceneKey = sceneKey
            self.primaryJob.scene = scene
            self.primaryJob.renderJob.SetActiveScene(scene, sceneKey)
        else:
            self.primaryJob.scene = scene
            self.primaryJob.renderJob.SetScene(scene)

    def RegisterJob(self, job):
        wr = blue.BluePythonWeakRef(job)
        if self.primaryJob.sceneType == SCENE_TYPE_INTERIOR:
            job.UseFXAA(True)

        def ClearDereferenced():
            self.registeredJobs.remove(wr)

        wr.callback = ClearDereferenced
        self.registeredJobs.append(wr)

    def GetRegisteredCamera(self, key):
        if key in self.registeredCameras:
            return self.registeredCameras[key]
        self.LogNotice('No camera registered for:', key, self.registeredCameras)

    def GetActiveSpaceCamera(self):
        ret = self.GetActivePrimaryCamera()
        if ret is None:
            if IsNewCameraActive():
                cameraID = evecamera.CAM_SHIPORBIT
            else:
                cameraID = evecamera.CAM_SPACE_PRIMARY
            ret = self._GetOrCreateCamera(cameraID)
        return ret

    def GetActivePrimaryCamera(self):
        return self.primaryJob.camera

    def GetActiveCamera(self):
        if self.secondaryJob is not None:
            return self.GetActiveSecondaryCamera()
        return self.GetActivePrimaryCamera()

    def GetActiveSecondaryCamera(self):
        return self.secondaryJob.camera

    def UnregisterCamera(self, key):
        if key in self.registeredCameras:
            self.LogNotice('sceneManager::UnregisterCamera', key, self.registeredCameras[key])
            cam = self.registeredCameras[key]
            if cam == self.GetActiveCamera():
                sm.ScatterEvent('OnActiveCameraChanged', None)
            if hasattr(cam, 'OnDeactivated'):
                cam.OnDeactivated()
            del self.registeredCameras[key]

    def RegisterCamera(self, camera):
        cameraID = camera.cameraID
        if cameraID in self.registeredCameras:
            return
        self.LogNotice('sceneManager::RegisterCamera', cameraID, camera)
        self.registeredCameras[camera.cameraID] = camera
        self.SetCameraOffset(camera)

    def SetCameraOffset(self, camera):
        cameraOffsetOverride = self.cameraOffsetOverride
        if cameraOffsetOverride:
            camera.centerOffset = cameraOffsetOverride * -0.01
        else:
            camera.centerOffset = gfxsettings.Get(gfxsettings.UI_CAMERA_OFFSET) * -0.01
        defaultCamera = self.GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY)
        if defaultCamera and camera is defaultCamera:
            sm.ScatterEvent('OnSetCameraOffset', camera, camera.centerOffset)

    def SetCameraOffsetOverride(self, cameraOffsetOverride):
        self.cameraOffsetOverride = cameraOffsetOverride
        self.CheckCameraOffsets()

    def GetCameraOffset(self, cameraID):
        camera = self.GetRegisteredCamera(cameraID)
        if camera:
            return camera.centerOffset
        return 0.0

    def CheckCameraOffsets(self):
        for cam in self.registeredCameras.itervalues():
            self.SetCameraOffset(cam)

    def UnregisterScene(self, key):
        if key in self.registeredScenes:
            del self.registeredScenes[key]

    def RegisterScene(self, scene, key):
        self.registeredScenes[key] = scene

    def GetRegisteredScene(self, key, defaultOnActiveScene = 0):
        if key in self.registeredScenes:
            return self.registeredScenes[key]
        if self.IsLoadingScene(key):
            self.sceneLoadedEvents[key].wait()
            return self.registeredScenes[key]
        if defaultOnActiveScene:
            return self.primaryJob.scene

    def IsLoadingScene(self, key):
        return key in self.sceneLoadedEvents and not self.sceneLoadedEvents[key].is_set()

    def SetRegisteredScenes(self, key):
        if key == 'default' and self.secondaryJob is not None:
            if self.primaryJob.renderJob.enabled:
                self.primaryJob.renderJob.Start()
            else:
                self.primaryJob.renderJob.Enable()
            self.ClearSecondaryScene()
        if self.primaryJob.sceneType != SCENE_TYPE_INTERIOR or key in self.overlaySceneKeys:
            scene = self.registeredScenes.get(key, None)
            if IsNewCameraActive() and key == evecamera.CAM_SPACE_PRIMARY:
                camera = self.registeredCameras.get(evecamera.CAM_SHIPORBIT, None)
            else:
                camera = self.registeredCameras.get(key, None)
            self.SetActiveScene(scene, key)
            if camera:
                self.SetActiveCamera(camera)

    def GetActiveScene(self):
        if self.secondaryJob is not None:
            return self.secondaryJob.scene
        return self.primaryJob.scene

    def Get2DBackdropScene(self):
        return self.uiBackdropScene

    @telemetry.ZONE_METHOD
    def Show2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = True
        if updateRenderJob:
            self.characterRenderJob.Set2DBackdropScene(self.uiBackdropScene)

    @telemetry.ZONE_METHOD
    def Hide2DBackdropScene(self, updateRenderJob = False):
        self.showUIBackdropScene = False
        if updateRenderJob:
            self.characterRenderJob.Set2DBackdropScene(None)

    def GetScene(self, location = None):
        if location is None:
            location = (eve.session.solarsystemid2, eve.session.constellationid, eve.session.regionid)
        resPath = cfg.GetNebula(*location)
        return resPath

    def GetSceneForSystem(self, solarSystemID):
        _, regionID, constellationID, _, _ = sm.GetService('map').GetParentLocationID(solarSystemID)
        return self.GetScene((solarSystemID, constellationID, regionID))

    def GetNebulaPathForSystem(self, solarSystemID):
        scene = trinity.Load(self.GetSceneForSystem(solarSystemID))
        return scene.envMapResPath

    def DeriveTextureFromSceneName(self, scenePath):
        scene = trinity.Load(scenePath)
        if scene is None:
            return ''
        return scene.envMap1ResPath

    def CleanupSpaceResources(self):
        self._sharedResources = {}

    def _GetSharedResource(self, path, key = None):
        comboKey = (path, key)
        if comboKey not in self._sharedResources:
            self._sharedResources[comboKey] = trinity.Load(path)
        return self._sharedResources[comboKey]

    def _PrepareBackgroundLandscapes(self, scene, solarSystemID, constellationID = None):
        starSeed = 0
        securityStatus = 1
        if constellationID is None:
            constellationID = sm.GetService('map').GetConstellationForSolarSystem(solarSystemID)
        if bool(solarSystemID) and bool(constellationID):
            starSeed = int(constellationID)
            securityStatus = sm.GetService('map').GetSecurityStatus(solarSystemID)
        if not gfxutils.BlockStarfieldOnLionOSX():
            scene.starfield = self._GetSharedResource('res:/dx9/scene/starfield/spritestars.red')
            if scene.starfield is not None:
                scene.starfield.seed = starSeed
                scene.starfield.minDist = 40
                scene.starfield.maxDist = 80
                if util.IsWormholeSystem(solarSystemID):
                    scene.starfield.numStars = 0
                else:
                    scene.starfield.numStars = 500 + int(250 * securityStatus)

    def _SetupUniverseStars(self, scene, solarsystemID):
        if gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED) and solarsystemID is not None:
            universe = self._GetSharedResource('res:/dx9/scene/starfield/universe.red')
            scene.backgroundObjects.append(universe)
            here = sm.GetService('map').GetItem(solarsystemID)
            if here:
                scale = 10000000000.0
                position = (here.x / scale, here.y / scale, -here.z / scale)
                universe.children[0].translation = position

    def ApplySolarsystemAttributes(self, scene, camera, solarsystemID = None):
        if solarsystemID is None:
            solarsystemID = session.solarsystemid
        if scene.dustfield is None:
            scene.dustfield = self._GetSharedResource('res:/dx9/scene/dustfield.red')
        scene.dustfieldConstraint = scene.dustfield.Find('trinity.EveDustfieldConstraint')[0]
        if scene.dustfieldConstraint is not None:
            scene.dustfieldConstraint.cameraView = camera.viewMatrix
        scene.sunDiffuseColor = (1.5, 1.5, 1.5, 1.0)
        self._SetupUniverseStars(scene, solarsystemID)
        self._PrepareBackgroundLandscapes(scene, solarsystemID)
        scene.gpuParticlePoolManager = self.particlePoolManager

    def ApplySceneInflightAttributes(self, scene, camera, bp = None):
        if bp is None:
            bp = sm.GetService('michelle').GetBallpark()
        scene.ballpark = bp
        if not IsNewCameraActive() and camera and bp is not None:
            myShipBall = bp.GetBallById(bp.ego)
            vel = geo2.Vector(myShipBall.vx, myShipBall.vy, myShipBall.vz)
            if geo2.Vec3Length(vel) > 0.0:
                vel = geo2.Vec3Normalize(vel)
                pitch = asin(-vel[1])
                yaw = atan2(vel[0], vel[2])
                yaw = yaw - 0.3
                pitch = pitch - 0.15
                camera.SetOrbit(yaw, pitch)

    def ApplyScene(self, scene, camera = None, registerKey = None):
        if registerKey is not None:
            self.RegisterScene(scene, registerKey)
            self.SetActiveScene(scene, registerKey)
            if camera:
                self.RegisterCamera(camera)
                self._SetActiveCameraForScene(camera, registerKey)
        else:
            self.SetActiveScene(scene, registerKey)
            if camera:
                self.SetActiveCamera(camera)
        sm.ScatterEvent('OnLoadScene', scene, registerKey)

    def _GetOrCreateCamera(self, cameraID):
        if cameraID in self.registeredCameras:
            return self.GetRegisteredCamera(cameraID)
        else:
            return self._CreateAndRegisterCamera(cameraID)

    def _CreateAndRegisterCamera(self, key, **kwargs):
        cameraCls = cameraClsByCameraID[key]
        camera = cameraCls(**kwargs)
        self.RegisterCamera(camera)
        return camera

    @telemetry.ZONE_METHOD
    def LoadScene(self, scenefile, inflight = 0, registerKey = None, setupCamera = True, applyScene = True):
        scene = None
        camera = None
        try:
            if registerKey:
                self.sceneLoadedEvents[registerKey] = locks.Event(registerKey)
            self.SetSceneType(SCENE_TYPE_SPACE)
            sceneFromFile = trinity.Load(scenefile)
            if sceneFromFile is None:
                return
            scene = sceneFromFile
            if IsNewCameraActive() and registerKey == evecamera.CAM_SPACE_PRIMARY:
                cameraID = evecamera.CAM_SHIPORBIT
            else:
                cameraID = registerKey
            camera = self._GetOrCreateCamera(cameraID)
            if inflight:
                self.ApplySolarsystemAttributes(scene, camera)
                self.ApplySceneInflightAttributes(scene, camera)
            if applyScene:
                self.ApplyScene(scene, camera, registerKey)
        except Exception:
            log.LogException('sceneManager::LoadScene')
            sys.exc_clear()
        finally:
            if registerKey and registerKey in self.sceneLoadedEvents:
                self.sceneLoadedEvents.pop(registerKey).set()

        return (scene, camera)
