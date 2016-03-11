#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\paperDoll\commonClientFunctions.py
import eve.common.script.paperDoll.paperDollDefinitions as pdDef
from yamlext.blueutil import ReadYamlFile
import trinity
import telemetry
import blue
import weakref
INTERIOR_FEMALE_GEOMETRY_RESPATH = const.DEFAULT_FEMALE_PAPERDOLL_MODEL
INTERIOR_MALE_GEOMETRY_RESPATH = const.DEFAULT_MALE_PAPERDOLL_MODEL
DEFAULT_FEMALE_ANIMATION_RESPATH = const.MORPHEMEPATH
DRAPE_TUCK_NAMES = ('DrapeShape', 'TuckShape')
HAIR_MESH_SHAPE = 'HairMeshShape'
TRANSLATION = intern('translation')
ROTATION = intern('rotation')

def CreateRandomDoll(name, factory, outResources = None):
    import paperDoll as PD
    dollRand = PD.DollRandomizer(factory)
    doll = dollRand.GetDoll()
    doll.name = name
    return doll


def CheckDuplicateMeshes(meshes):
    meshCount = len(meshes)
    for i in xrange(meshCount):
        for x in xrange(i + 1, meshCount):
            if meshes[i].name == meshes[x].name and meshes[i].geometryResPath == meshes[x].geometryResPath:
                raise Exception('Duplicate meshes!\n Mesh name:%s Mesh Geometry Respath:%s' % (meshes[i].name, meshes[i].geometryResPath))


def GetEffectsFromAreaList(areas):
    effects = []
    for each in iter(areas):
        effects.append(each.effect)

    return effects


def MeshAreaIterator(mesh):
    for areaList in MeshAreaListIterator(mesh):
        for area in iter(areaList):
            yield area


def MeshAreaListIterator(mesh, includePLP = False):
    yield mesh.opaqueAreas
    yield mesh.decalAreas
    yield mesh.depthAreas
    yield mesh.transparentAreas
    yield mesh.additiveAreas
    yield mesh.pickableAreas
    yield mesh.mirrorAreas
    if includePLP:
        yield mesh.decalNormalAreas
        yield mesh.depthNormalAreas
        yield mesh.opaquePrepassAreas
        yield mesh.decalPrepassAreas


@telemetry.ZONE_FUNCTION
def GetEffectsFromMesh(mesh, allowShaderMaterial = False, includePLP = False):
    effects = []
    if type(mesh) is trinity.Tr2ClothingActor:
        if hasattr(mesh, 'effect') and mesh.effect is not None:
            effects.append(mesh.effect)
        if hasattr(mesh, 'effectReversed') and mesh.effectReversed is not None:
            effects.append(mesh.effectReversed)
    elif type(mesh) is trinity.Tr2Mesh:
        for area in MeshAreaListIterator(mesh, includePLP=includePLP):
            effects += GetEffectsFromAreaList(area)

    if not allowShaderMaterial:
        effects = [ effect for effect in effects if effect and type(effect) != trinity.Tr2ShaderMaterial ]
    return effects


def MoveAreas(fromAreaList, toAreaList):
    for area in iter(fromAreaList):
        toAreaList.append(area)

    del fromAreaList[:]


def SetOrAddMap(effect, mapName, mapPath = None):
    for res in effect.resources:
        if res.name == mapName:
            if mapPath:
                res.resourcePath = mapPath
            return res

    map = trinity.TriTextureParameter()
    map.name = mapName
    if mapPath:
        map.resourcePath = mapPath
    effect.resources.append(map)
    return map


def FindOrAddMat4(effect, name):
    for r in effect.parameters:
        if r.name == name:
            return r

    p = trinity.Tr2Matrix4Parameter()
    p.name = name
    effect.parameters.append(p)
    return p


def FindOrAddVec4(effect, name):
    for r in effect.parameters:
        if r.name == name:
            return r

    p = trinity.Tr2Vector4Parameter()
    p.name = name
    effect.parameters.append(p)
    return p


def __WeakBlueRemoveHelper(weakInstance, dictionaryName, weakObjectKey):
    if weakInstance():
        dictionary = getattr(weakInstance(), dictionaryName)
        if dictionary is not None:
            dictionary.pop(weakObjectKey, None)
    if weakObjectKey:
        weakObjectKey.callback = None


def AddWeakBlue(classInstance, dictionaryName, blueObjectKey, value):
    dictionary = getattr(classInstance, dictionaryName)
    if dictionary is None:
        return
    for key in dictionary.iterkeys():
        if key.object == blueObjectKey:
            dictionary[key] = value
            return

    weakInstance = weakref.ref(classInstance)
    weakObjectKey = blue.BluePythonWeakRef(blueObjectKey)
    weakObjectKey.callback = lambda : __WeakBlueRemoveHelper(weakInstance, dictionaryName, weakObjectKey)
    dictionary[weakObjectKey] = value


def DestroyWeakBlueDict(dictionary):
    for weakObjectKey in dictionary.iterkeys():
        if weakObjectKey:
            weakObjectKey.callback = None


def IsBeard(areaMesh):
    return areaMesh.effect is not None and 'furshell' in areaMesh.effect.effectFilePath.lower()


def IsSkin(fx):
    fxName = fx.name.lower()
    return fxName.startswith('c_skin') and 'tearduct' not in fxName


def IsGlasses(areaMesh):
    return areaMesh.effect is not None and 'glassshader' in areaMesh.effect.effectFilePath.lower()


def StripDigits(name):
    return ''.join((letter.lower() for letter in name if not letter.isdigit()))


def PutMeshToLookup(lookup, m):
    meshName = StripDigits(m.name)
    c = 0
    try:
        c = int(m.name.split(meshName)[-1])
    except ValueError:
        c = 0

    meshName = StripDigits(m.name)
    lookup[meshName] = max([c, lookup.get(meshName)]) + 1


def FindParameterByName(effect, parameterName):
    for param in effect.parameters:
        if hasattr(param, 'name') and param.name == parameterName:
            return param


def FindResourceByName(effect, resourceName):
    for res in effect.resources:
        if res.name == resourceName:
            return res


def GetHighLevelShaderByName(name):
    sm = trinity.GetShaderManager()
    for shader in sm.shaderLibrary:
        if shader.name == name:
            return shader


def GetSkintypeColor(skintypePath, isMale):
    if isMale:
        basePath = pdDef.MALE_BASE_PATH
    else:
        basePath = pdDef.FEMALE_BASE_PATH
    if skintypePath.startswith('/'):
        fmt = '{0}{1}'
    else:
        fmt = '{0}/{1}'
    completePath = fmt.format(basePath, skintypePath)
    skintypeData = ReadYamlFile(completePath)
    if skintypeData is None:
        return
    return skintypeData[2]


def TryGetSkintypeColorVariation(dnaRow):
    modifierLocations = cfg.paperdollModifierLocations
    resources = cfg.paperdollResources
    for modifierRow in dnaRow.modifiers:
        modifierInfo = modifierLocations.GetIfExists(modifierRow.modifierLocationID)
        if modifierInfo.modifierKey == pdDef.BODY_CATEGORIES.SKINTYPE:
            resourcesInfo = resources.GetIfExists(modifierRow.paperdollResourceID)
            return GetSkintypeColor(resourcesInfo.resPath, resourcesInfo.resGender)


def TryGetSkintoneColorVariation(dnaRow):
    colors = cfg.paperdollColors
    colorNames = cfg.paperdollColorNames
    for colorRow in dnaRow.colors:
        colorInfo = colors.GetIfExists(colorRow.colorID)
        colorNameInfo = colorNames.GetIfExists(colorRow.colorNameA)
        colorNameA = colorNameInfo.colorName
        if colorInfo.colorKey == pdDef.BODY_CATEGORIES.SKINTONE:
            return colorNameA


def GetSkinTypeOrToneColorVariation(dnaRow):
    colorVar = TryGetSkintypeColorVariation(dnaRow)
    if colorVar is not None:
        return colorVar
    return TryGetSkintoneColorVariation(dnaRow)


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('paperDoll', globals())
