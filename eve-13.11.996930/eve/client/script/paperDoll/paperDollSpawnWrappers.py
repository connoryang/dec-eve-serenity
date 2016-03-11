#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\paperDoll\paperDollSpawnWrappers.py
import trinity
import uthread
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
import eve.common.script.paperDoll.paperDollDataManagement as pdDm
import eve.client.script.paperDoll.commonClientFunctions as pdCcf
import eve.common.script.paperDoll.paperDollCommonFunctions as pdCf
import eve.client.script.paperDoll.paperDollImpl as pdImpl
import eve.client.script.paperDoll.paperDollLOD as pdLod
import eve.client.script.paperDoll.paperDollPortrait as pdPor
from eve.client.script.paperDoll.SkinSpotLightShadows import SkinSpotLightShadows
import blue
import telemetry
import yaml
import log

class PaperDollManager(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __guid__ = 'paperDoll.PaperDollManager'

    def __init__(self, factory, keyFunc = None):
        self.factory = factory
        self.keyFunc = keyFunc
        self.__pdc = {}

    def __del__(self):
        self.ClearDolls()

    def __iter__(self):
        for pdc in self.__pdc.itervalues():
            yield pdc

    def Count(self):
        return len(self.__pdc)

    def GetPaperDollCharacterByDoll(self, doll):
        for pdc in iter(self):
            if pdImpl.Doll.InstanceEquals(pdc.doll, doll):
                return pdc

    def GetPaperDollCharacterByAvatar(self, avatar):
        for pdc in iter(self):
            if pdc.avatar == avatar:
                return pdc

    def GetPaperDollCharacterByKey(self, key):
        return self.__pdc.get(key)

    def RemovePaperDollCharacter(self, pdc):
        key = self.__GetKey(pdc)
        if key in self.__pdc:
            del self.__pdc[key]

    def ClearDolls(self):
        self.__pdc.clear()

    def __GetKey(self, pdc):
        doll = pdc.GetDoll()
        if self.keyFunc:
            return self.keyFunc(doll)
        else:
            return doll.instanceID

    def SpawnPaperDollCharacterFromDNA(self, scene, dollName, dollDNA, position = None, rotation = None, lodEnabled = False, compressionSettings = None, gender = pdDef.GENDER.FEMALE, usePrepass = False, textureResolution = None, updateDoll = True, spawnAtLOD = 0):
        pdc = PaperDollCharacter(self.factory)
        pdc.LoadDollFromDNA(dollDNA, dollName=dollName, lodEnabled=lodEnabled, compressionSettings=compressionSettings)
        if textureResolution:
            pdc.doll.SetTextureSize(textureResolution)
        if lodEnabled:
            pdc.SpawnLOD(scene, point=position, rotation=rotation, gender=gender, usePrepass=usePrepass)
        else:
            pdc.Spawn(scene, point=position, rotation=rotation, gender=gender, usePrepass=usePrepass, updateDoll=updateDoll, lod=spawnAtLOD)
        self.__pdc[self.__GetKey(pdc)] = pdc
        sm.ScatterEvent('OnDollCreated', self.__GetKey(pdc))
        return pdc

    def SpawnRandomDoll(self, scene, **kwargs):
        pdc = PaperDollCharacter(self.factory)
        pdc.MakeRandomDoll()
        autoLod = kwargs.get('autoLOD')
        if autoLod:
            pdc.SpawnLOD(scene, **kwargs)
        else:
            pdc.Spawn(scene, **kwargs)
        self.__pdc[self.__GetKey(pdc)] = pdc
        sm.ScatterEvent('OnDollCreated', self.__GetKey(pdc))
        return pdc

    def SpawnDoll(self, scene, **kwargs):
        doll = kwargs.get('doll')
        autoLod = kwargs.get('autoLOD')
        pdc = PaperDollCharacter(self.factory, doll=doll)
        if autoLod:
            pdc.SpawnLOD(scene, **kwargs)
        else:
            pdc.Spawn(scene, **kwargs)
        self.__pdc[self.__GetKey(pdc)] = pdc
        sm.ScatterEvent('OnDollCreated', self.__GetKey(pdc))
        return pdc

    def SpawnDollFromRes(self, scene, resPath, **kwargs):
        pdc = PaperDollCharacter(self.factory)
        pdc.LoadFromRes(resPath)
        pdc.Spawn(scene, **kwargs)
        self.__pdc[self.__GetKey(pdc)] = pdc
        sm.ScatterEvent('OnDollCreated', self.__GetKey(pdc))
        return pdc

    def GetAllDolls(self):
        dolls = []
        for dc in self.__pdc.itervalues():
            dollInfo = {}
            dollInfo['name'] = dc.doll.name
            dollInfo['translation'] = dc.avatar.translation
            dollInfo['rotation'] = dc.avatar.rotation
            dollInfo['dna'] = dc.GetDNA()
            dollInfo['doll'] = dc
            dolls.append(dollInfo)

        return dolls

    def RestoreDollsFromDnaToScene(self, dolls, scene):
        for dc in dolls:
            self.SpawnPaperDollCharacterFromDNA(scene, dc['name'], dc['dna'], position=dc['translation'], rotation=dc['rotation'])

    def WaitForAllDolls(self):
        for dc in self.__pdc.itervalues():
            dc.WaitForUpdate()


class PaperDollCharacter(object):
    __metaclass__ = telemetry.ZONE_PER_METHOD
    __guid__ = 'paperDoll.PaperDollCharacter'
    __DEFAULT_NAME = 'Spawned Character'

    def setscene(self, scene):
        self.__scene = blue.BluePythonWeakRef(scene)

    scene = property(fget=lambda self: self.__scene.object, fset=lambda self, x: self.setscene(x))

    def __init__(self, factory, doll = None, avatar = None, visualModel = None):
        self.factory = factory
        self.doll = None
        self.factory.WaitUntilLoaded()
        self.doll = doll
        self.avatar = avatar
        self.visualModel = visualModel
        if not visualModel and hasattr(avatar, 'visualModel'):
            self.visualModel = avatar.visualModel
        self.__scene = blue.BluePythonWeakRef(None)
        self.autoLod = False
        self.disableDel = False
        trinity.device.RegisterResource(self)

    def __del__(self):
        if self.disableDel:
            return
        del self.doll
        del self.visualModel
        if self.scene:
            self.factory.RemoveAvatarFromScene(self.avatar, self.scene)
        if self.avatar:
            self.avatar.visualModel = None
        if self.autoLod:
            pdLod.AbortAllLod(self.avatar)
        del self.avatar

    def OnInvalidate(self, dev):
        pass

    def OnCreate(self, dev):
        if self.doll and self.avatar:
            self.doll.KillUpdate()
            self.doll.mapBundle.ReCreate()
            for modifier in self.doll.buildDataManager.GetModifiersAsList():
                modifier.IsDirty |= modifier.decalData is not None or modifier.IsMeshDirty()

            self.doll.decalBaker = None
            if SkinSpotLightShadows.instance is not None:
                SkinSpotLightShadows.instance.RefreshLights()
            uthread.new(self.doll.Update, self.factory, self.avatar)

    def ExportCharacter(self, resPath):

        def fun():
            path = resPath

            def GetMapResourcePath(map):
                return path + '/' + pdDef.MAPNAMES[map] + '.dds'

            for map in pdDef.MAPS:
                texture = self.doll.mapBundle[map]
                texture.SaveAsync(GetMapResourcePath(map))
                texture.WaitForSave()

            meshGeometryResPaths = {}
            for modifier in self.doll.buildDataManager.GetSortedModifiers():
                meshGeometryResPaths.update(modifier.meshGeometryResPaths)

            for mesh in self.avatar.visualModel.meshes:
                mesh.geometryResPath = meshGeometryResPaths.get(mesh.name, '')
                for fx in pdCcf.GetEffectsFromMesh(mesh):
                    for resource in fx.resources:
                        if resource.name in pdDef.MAPNAMES:
                            resource.resourcePath = GetMapResourcePath(pdDef.MAPNAMES.index(resource.name))

            trinity.Save(self.avatar, path + '/unique.red')
            morphTargets = {}
            for modifier in self.doll.buildDataManager.GetSortedModifiers():
                if modifier.categorie in pdDef.BLENDSHAPE_CATEGORIES:
                    morphTargets[modifier.name] = modifier.weight

            bsFilePath = blue.paths.ResolvePath(path + '/blendshapes.yaml')
            f = file(bsFilePath, 'w')
            yaml.dump(morphTargets, f)
            f.close()
            animOffsets = {}
            for bone in self.doll.boneOffsets:
                trans = self.doll.boneOffsets[bone]['translation']
                animOffsets[bone] = trans

            aoFilePath = blue.paths.ResolvePath(path + '/animationOffsets.yaml')
            f = file(aoFilePath, 'w')
            yaml.dump(animOffsets, f)
            f.close()

        uthread.new(fun)

    @staticmethod
    def ImportCharacter(factory, scene, resPath, **kwargs):
        blocking = kwargs.get('blocking')
        callBack = kwargs.get('callBack')
        rotation = kwargs.get('rotation')
        position = kwargs.get('point')
        pdc = PaperDollCharacter(factory)
        pdc.scene = scene
        pdc.avatar = trinity.Load(resPath + '/unique.red')
        if pdc.avatar is None:
            log.LogInfo('Import failed on ' + resPath + '/unique.red')
            return
        pdc.visualModel = pdc.avatar.visualModel
        slash = resPath.rfind('/')
        pdc.avatar.name = str(resPath[slash + 1:] + ' (import)')
        if position:
            pdc.avatar.translation = position
        if rotation:
            pdc.avatar.rotation = rotation
        rf = blue.ResFile()
        bsPath = resPath + '/blendshapes.yaml'
        meshes = None
        morphTargets = pdDm.LoadYamlFileNicely(bsPath)
        if morphTargets:
            meshes = pdc.visualModel.meshes

        def fun():
            if meshes:
                factory.ApplyMorphTargetsToMeshes(meshes, morphTargets)
                if trinity.GetShaderModel() == 'SM_2_0_LO':
                    pdPor.PortraitTools.RebindDXT5ShadersForSM2(meshes)
            if callBack:
                callBack()

        if blocking:
            fun()
        else:
            uthread.worker('paperDoll::PaperDollCharacter::ImportCharacter', fun)
        scene.AddDynamic(pdc.avatar)
        aoPath = resPath + '/animationOffsets.yaml'
        animationOffsets = pdDm.LoadYamlFileNicely(aoPath)
        if animationOffsets:
            pdc.ApplyAnimationOffsets(animationOffsets)
        pdc.avatar.explicitMinBounds = (-5, -5, -5)
        pdc.avatar.explicitMaxBounds = (5, 5, 5)
        pdc.avatar.useExplicitBounds = True
        if SkinSpotLightShadows.instance is not None:
            for mesh in pdc.visualModel.meshes:
                SkinSpotLightShadows.instance.CreateEffectParamsForMesh(mesh)

        return pdc

    def ApplyAnimationOffsets(self, animationOffsets = None):
        import GameWorld
        if animationOffsets and self.avatar.animationUpdater and type(self.avatar.animationUpdater) == GameWorld.GWAnimation and self.avatar.animationUpdater.network:
            for animationOffset in iter(self.animationOffsets):
                self.avatar.animationUpdater.network.boneOffset.SetOffset(animationOffset, animationOffsets[animationOffset][0], animationOffsets[animationOffset][1], animationOffsets[animationOffset][2])

    def GetDoll(self):
        return self.doll

    def GetAvatar(self):
        return self.avatar

    def MakeRandomDoll(self):
        self.doll = pdCcf.CreateRandomDoll(self.doll.name if self.doll else PaperDollCharacter.__DEFAULT_NAME, self.factory)
        if self.avatar:
            self.doll.Update(self.factory, self.avatar)

    def MakeDollNude(self):
        self.doll.buildDataManager = pdDm.BuildDataManager()
        if self.avatar:
            self.doll.Update(self.factory, self.avatar)

    def LoadFromRes(self, resPath):
        self.doll = pdImpl.Doll(PaperDollCharacter.__DEFAULT_NAME)
        while not self.factory.IsLoaded:
            pdCf.Yield()

        self.doll.Load(resPath, self.factory)
        if self.avatar:
            self.doll.Update(self.factory, self.avatar)

    def LoadDollFromDNA(self, dollDNA, dollName = None, lodEnabled = True, compressionSettings = None):
        name = dollName if dollName is not None else PaperDollCharacter.__DEFAULT_NAME
        self.doll = pdImpl.Doll(name)
        self.doll.LoadDNA(dollDNA, self.factory)
        if compressionSettings:
            self.doll.compressionSettings = compressionSettings
        if self.avatar:
            gender = pdDef.GENDER.MALE if self.doll.gender else pdDef.GENDER.FEMALE
            networkToLoad = const.FEMALE_MORPHEME_PATH if gender == pdDef.GENDER.FEMALE else const.MALE_MORPHEME_PATH
            if lodEnabled:
                uthread.worker('^PaperDollCharacter::LoadFromDNA', pdLod.SetupLODFromPaperdoll, self.avatar, self.doll, self.factory, networkToLoad)
            else:
                uthread.worker('^PaperDollCharacter::LoadFromDNA', self.doll.Update, self.factory, self.avatar)

    def GetDNA(self):
        return self.doll.GetDNA()

    def __PrepareAvatar(self, scene, point = None, rotation = None):
        if scene is None:
            raise ValueError('None type passed as scene to paperDoll::__PrepareAvatar!')
        oldAnimation = None
        sceneTypesDifferent = getattr(self.scene, '__typename__', None) != getattr(scene, '__typename__', None)
        if self.avatar:
            oldAnimation = self.avatar.animationUpdater
            if self.scene:
                self.factory.RemoveAvatarFromScene(self.avatar, self.scene)
            if sceneTypesDifferent:
                pdLod.AbortAllLod(self.avatar)
                del self.avatar
        if type(scene) in (trinity.Tr2InteriorScene, trinity.WodBakingScene) and type(self.scene) is not type(scene):
            self.avatar = trinity.Tr2IntSkinnedObject()
            self.doll.avatarType = 'interior'
        self.factory.AddAvatarToScene(self.avatar, scene)
        if point:
            self.avatar.translation = point
        if rotation:
            self.avatar.rotation = rotation
            self.avatar.animationUpdater = oldAnimation
        if getattr(self.avatar.animationUpdater, 'network', None):
            if self.doll.gender == pdDef.GENDER.MALE and self.avatar.animationUpdater.network.GetAnimationSetCount() > 1:
                self.avatar.animationUpdater.network.SetAnimationSetIndex(1)
            else:
                self.avatar.animationUpdater.network.SetAnimationSetIndex(0)

    def SpawnLOD(self, scene, **kwargs):
        self.Spawn(scene, spawnLod=True, **kwargs)

    def Spawn(self, scene, **kwargs):
        gender = pdDef.GENDER.FEMALE
        if 'gender' in kwargs:
            gender = kwargs['gender']
        if self.doll is None:
            self.doll = pdImpl.Doll(PaperDollCharacter.__DEFAULT_NAME, gender=gender)
        else:
            gender = self.doll.gender
        spawnLod = kwargs.get('spawnLod', False)
        usePrepass = kwargs.get('usePrepass', False)
        self.doll.SetUsePrepass(usePrepass)
        if 'lod' in kwargs and not spawnLod:
            self.doll.overrideLod = kwargs['lod']
        if self.visualModel is None:
            self.visualModel = self.factory.CreateVisualModel(gender=gender)
        self.__PrepareAvatar(scene, point=kwargs.get('point'), rotation=kwargs.get('rotation'))
        self.scene = scene
        self.avatar.visualModel = self.visualModel
        if spawnLod:
            networkToLoad = const.FEMALE_MORPHEME_PATH if gender == pdDef.GENDER.FEMALE else const.MALE_MORPHEME_PATH
            pdLod.SetupLODFromPaperdoll(self.avatar, self.doll, self.factory, networkToLoad)
        elif kwargs.get('updateDoll', True):
            self.doll.Update(self.factory, self.avatar)

    def MoveToScene(self, scene, point = None):
        if scene and self.doll:
            if getattr(self.scene, '__typename__', None) != getattr(scene, '__typename__', None):
                self.doll.buildDataManager.SetAllAsDirty(clearMeshes=True)
            self.Spawn(scene, point=point)

    def Update(self, channel = None):
        return self.doll.Update(self.factory, self.avatar, channel=channel)

    def UpdateClothSimulationStatus(self):
        self.doll.buildDataManager.SetAllAsDirty(clearMeshes=True)
        self.Update()

    def WaitForUpdate(self):
        while self.doll.busyUpdating:
            pdCf.Yield()
