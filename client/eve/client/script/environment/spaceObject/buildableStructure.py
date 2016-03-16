#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\buildableStructure.py
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
from evegraphics.utils import GetResPathFromGraphicID, GetCorrectEffectPath
import locks
import trinity
NANO_CONTAINER_GRAPHIC_ID = 20930
CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID = 20931
TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID = 21098
STATE_NONE = None
STATE_BUILDING = 'Building'
STATE_TEARDOWN = 'TearDown'

class BuildableStructure(LargeCollidableStructure):

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        self.overlayEffects = {}
        self.nanoContainerModel = None
        self.nanoContainerModelLoadedEvent = locks.Event()
        self.structureModel = None
        self.structureModelLoadedEvent = locks.Event()
        self.overlayEffectEvent = locks.Event()
        self.isConstructing = False
        self.oldClipSphereCenter = (0.0, 0.0, 0.0)
        self.LoadOverlayEffects()

    def Prepare(self):
        self.LogInfo('BuildableStructure: Preparing')
        self.LoadOverlayEffects()
        self.LoadNanoContainerModel()
        self.LoadStructureModel()
        LargeCollidableStructure.Prepare(self)

    def LoadNanoContainerModel(self):
        self.LogInfo('BuildableStructure: Loading nano container model')
        self.nanoContainerModel = self.LoadAdditionalModel(GetResPathFromGraphicID(NANO_CONTAINER_GRAPHIC_ID))
        self.nanoContainerModel.name += '_nanocontainer'
        self.nanoContainerModelLoadedEvent.set()

    def LoadStructureModel(self):
        self.LogInfo('BuildableStructure: Loading structure model')
        self.structureModel = self.LoadAdditionalModel()
        self.structureModelLoadedEvent.set()

    def SetModelDisplay(self, model, display):
        if model is not None:
            model.display = display

    def LoadUnLoadedModels(self):
        if self.nanoContainerModel is None:
            self.LoadNanoContainerModel()
        if self.structureModel is None:
            self.LoadStructureModel()

    def SetupModel(self, unanchored):
        sendOutModelLoadedEvent = self.model is None
        if unanchored:
            self.ApplyUnanchoredModels()
        else:
            self.ApplyAnchoredModels()
        if sendOutModelLoadedEvent:
            self.NotifyModelLoaded()
        self.SetupAnimationInformation(self.GetStructureModel())
        self.SetAnimationSequencer(self.model)

    def GetNanoContainerModel(self):
        if self.nanoContainerModel is None:
            self.LogInfo('BuildableStructure: waiting for nanocontainer model')
            self.nanoContainerModelLoadedEvent.wait()
            self.LogInfo('BuildableStructure: done waiting for nanocontainer model')
        return self.nanoContainerModel

    def GetStructureModel(self):
        if self.structureModel is None:
            self.LogInfo('BuildableStructure: waiting for structure model')
            self.structureModelLoadedEvent.wait()
            self.LogInfo('BuildableStructure: done waiting for structure model')
        return self.structureModel

    def LoadOverlayEffects(self):
        constructionOverlayPath = GetCorrectEffectPath(GetResPathFromGraphicID(CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID), self.structureModel)
        teardownOverlayPath = GetCorrectEffectPath(GetResPathFromGraphicID(TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID), self.structureModel)
        self.overlayEffects[CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID] = trinity.Load(constructionOverlayPath)
        self.overlayEffects[TEARDOWN_OVERLAY_EFFECT_GRAPHIC_ID] = trinity.Load(teardownOverlayPath)
        self.overlayEffectEvent.set()

    def ApplyAnchoredModels(self):
        self.SetModelDisplay(self.GetNanoContainerModel(), self.isConstructing)
        self.SetModelDisplay(self.GetStructureModel(), True)
        self.model = self.GetStructureModel()

    def ApplyUnanchoredModels(self):
        self.SetModelDisplay(self.GetNanoContainerModel(), True)
        self.SetModelDisplay(self.GetStructureModel(), self.isConstructing)
        if self.isConstructing:
            self.model = self.GetStructureModel()
        else:
            self.model = self.GetNanoContainerModel()

    def HasModels(self):
        return self.nanoContainerModel is not None or self.structureModel is not None

    def ClearAndRemoveAllModels(self, scene):
        self.RemoveAndClearModel(self.nanoContainerModel, scene)
        self.RemoveAndClearModel(self.structureModel, scene)
        self.nanoContainerModel = None
        self.structureModel = None
        self.model = None

    def RemoveAllModelsFromScene(self, scene):
        scene.objects.fremove(self.nanoContainerModel)
        scene.objects.fremove(self.structureModel)

    def SetupOverlayEffect(self, overlayGraphicID):
        clipCenter = self.GetStructureModel().clipSphereCenter
        boundingSphereCenter = self.GetStructureModel().boundingSphereCenter
        self.oldClipSphereCenter = (clipCenter[0], clipCenter[1], clipCenter[2])
        self.GetStructureModel().clipSphereCenter = (-boundingSphereCenter[0], -boundingSphereCenter[1], -boundingSphereCenter[2])
        if overlayGraphicID == CONSTRUCTION_OVERLAY_EFFECT_GRAPHIC_ID:
            self.GetStructureModel().clipSphereFactor = 0.0
        else:
            self.GetStructureModel().clipSphereFactor = 1.0
        if self.overlayEffects[overlayGraphicID] is None:
            self.LogInfo('BuildableStructure: waiting for anchoring effect')
            self.overlayEffectEvent.wait()
            self.LogInfo('BuildableStructure: done waiting for anchoring effect')
        self.GetStructureModel().overlayEffects.append(self.overlayEffects[overlayGraphicID])

    def PreBuildingSteps(self, overlayGraphicIDToApply):
        self.isConstructing = True
        self.SetupOverlayEffect(overlayGraphicIDToApply)
        self.SetupModel(False)
        self.StartNanoContainerAnimation()

    def PostBuildingSteps(self, overlayGraphicIdToRemove):
        self.isConstructing = False
        if self.GetStructureModel() is not None:
            self.GetStructureModel().overlayEffects.remove(self.overlayEffects[overlayGraphicIdToRemove])
            self.GetStructureModel().clipSphereCenter = (self.oldClipSphereCenter[0], self.oldClipSphereCenter[1], self.oldClipSphereCenter[2])
        self.EndNanoContainerAnimation()

    def StartNanoContainerAnimation(self, deployScale = 1):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimationEx('Deploy', 1, 0, deployScale)
            self.nanoContainerModel.ChainAnimationEx('OpenLoop', 0, 0, 1)

    def EndNanoContainerAnimation(self):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimation('Pack')
