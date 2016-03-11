#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\graphicWrappers\tr2InteriorScene.py
import blue
import decometaclass
import cef
import geo2
import trinity
import yaml
ENLIGHTEN_BUILD_WAIT_TIME = 200
INTERIOR_RES_PATH = const.res.INTERIOR_RES_PATH
INTERIOR_REFMAP_PATH = 'res:/Graphics/Interior/StaticEnvmaps/'

class Tr2InteriorScene(decometaclass.WrapBlueClass('trinity.Tr2InteriorScene')):
    __guid__ = 'graphicWrappers.Tr2InteriorScene'

    @staticmethod
    def Wrap(triObject, resPath):
        Tr2InteriorScene(triObject)
        triObject.objects = {}
        triObject.id = ''
        triObject.cellData = {}
        return triObject

    def SetID(self, id):
        self.id = id

    def _GetCell(self, cellName):
        for cell in self.cells:
            if cell.name == cellName:
                return cell

        cell = trinity.Tr2InteriorCell()
        cell.name = cellName
        cell.shProbeResPath = INTERIOR_RES_PATH + str(self.id) + '_' + cellName + '.shp'
        cell.reflectionMapPath = INTERIOR_REFMAP_PATH + 'Cube_%s_%s.dds' % (self.id, cellName)
        cell.irradianceTexturePath = '%s%s_%s_rad.dds' % (INTERIOR_RES_PATH, self.id, cell.name)
        cell.directionalIrradianceTexturePath = '%s%s_%s_dir_rad.dds' % (INTERIOR_RES_PATH, self.id, cell.name)
        self.cells.append(cell)
        self._LoadUVData(cellName)
        return cell

    def _RemoveCellIfEmpty(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

    def AddStatic(self, staticObj, cellName = 'DefaultCell', systemName = 0, id = None):
        if staticObj in self.objects:
            return
        cell = self._GetCell(cellName)
        cell.AddStatic(staticObj)
        self.objects[staticObj] = cell
        if id is None:
            id = staticObj.objectID
        uvData = self.cellData.get(cellName, {}).get(id, None)
        if uvData:
            staticObj.SetInstanceData(*uvData)

    def RemoveStatic(self, staticObj):
        cell = self.objects.get(staticObj, None)
        if cell:
            cell.RemoveStatic(staticObj)
            self.objects[staticObj] = None
            self._RemoveCellIfEmpty(cell)

    def AddLight(self, lightObj):
        if lightObj in self.lights:
            return
        self.AddLightSource(lightObj)

    def RemoveLight(self, lightObj):
        if lightObj in self.lights:
            self.RemoveLightSource(lightObj)

    def AddAvatarToScene(self, avatar):
        self.AddDynamicToScene(avatar)

    def RemoveAvatarFromScene(self, avatar):
        self.RemoveDynamicFromScene(avatar)

    def AddDynamicToScene(self, obj):
        if type(obj) is trinity.Tr2IntSkinnedObject:
            obj.visualModel.ResetAnimationBindings()
        self.AddDynamic(obj)
        return obj

    def RemoveDynamicFromScene(self, obj):
        if obj in self.dynamics:
            self.RemoveDynamic(obj)

    def AddCurveSetToScene(self, curveSet):
        self.curveSets.append(curveSet)

    def RemoveCurveSetFromScene(self, curveSet):
        self.curveSets.remove(curveSet)

    def Refresh(self):
        pass

    def _LoadUVData(self, cellName):
        filePath = INTERIOR_RES_PATH + str(self.id) + '_' + str(cellName) + '.uv'
        if blue.paths.exists(filePath):
            file = blue.ResFile()
            file.open(filePath)
            marshalData = file.read()
            file.close()
            self.cellData[cellName] = blue.marshal.Load(marshalData)
        else:
            self.cellData[cellName] = {}

    def RemoveSkyboxTexture(self):
        self.backgroundEffect = None
        self.backgroundCubemapPath = ''

    def SetSkyboxTexture(self, texturePath):
        self.backgroundEffect = trinity.Tr2Effect()
        texture = trinity.TriTextureParameter()
        texture.name = 'EnvMap1'
        texture.resourcePath = texturePath
        self.backgroundEffect.resources.append(texture)
        self.backgroundEffect.effectFilePath = 'res:/Graphics/Effect/Managed/Interior/Static/EnvironmentCubemap.fx'
        self.backgroundCubemapPath = str(texturePath)

    def GetBoundingBox(self):
        minBB = (99999999.9, 99999999.9, 99999999.9)
        maxBB = (-99999999.9, -99999999.9, -99999999.9)
        for cell in self.cells:
            minBB = geo2.Vec3Minimize(minBB, cell.minBounds)
            maxBB = geo2.Vec3Maximize(maxBB, cell.maxBounds)

        return (minBB, maxBB)
