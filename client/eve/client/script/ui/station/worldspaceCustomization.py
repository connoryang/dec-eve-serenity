#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\worldspaceCustomization.py
import worldspaceCustomizationDefinitions
import evetypes

def ApplyWorldspaceCustomization():
    if not eve.stationItem or session.worldspaceid != session.stationid2:
        return
    stationTypeID = eve.stationItem.stationTypeID
    stationRace = evetypes.GetRaceID(stationTypeID)
    if stationRace not in worldspaceCustomizationDefinitions.themeSettings:
        return
    if eve.stationItem.ownerID not in worldspaceCustomizationDefinitions.themeSettings[stationRace]:
        return
    changes = worldspaceCustomizationDefinitions.themeSettings[stationRace][eve.stationItem.ownerID]
    UpdateShaderParameters(changes.shaderParameters)
    if changes.flares:
        UpdateFlares(*changes.flares)
    if changes.pointLights:
        UpdateSpotPointLights(*changes.pointLights)
    if changes.cylendricalLights:
        UpdateCylendricalLights(*changes.cylendricalLights)
    UpdateEnlightenTexture()


def UpdateFlares(r = 1, g = 1, b = 1, a = 1):
    MultiplyColorValue('trinity.Tr2InteriorFlare', r, g, b, a)


def UpdateSpotPointLights(r = 1, g = 1, b = 1, a = 1):
    MultiplyColorValue('trinity.Tr2InteriorLightSource', r, g, b, a)


def UpdateCylendricalLights(r = 1, g = 1, b = 1, a = 1):
    MultiplyColorValue('trinity.Tr2InteriorCylinderLight', r, g, b, a)


def MultiplyColorValue(trinityObjectName, r = 1, g = 1, b = 1, a = 1):
    scene = sm.GetService('sceneManager').incarnaRenderJob.scene.object
    for effect in scene.Find(trinityObjectName):
        currentColor = effect.color
        effect.color = (currentColor[0] * r,
         currentColor[1] * g,
         currentColor[2] * b,
         currentColor[3] * a)


def UpdateShaderParameters(params):
    meshAreas = []
    scene = sm.GetService('sceneManager').incarnaRenderJob.scene.object
    meshAreas.extend(scene.Find('trinity.Tr2MeshArea'))
    for interiorStatic, system in scene.objects.iteritems():
        staticMesh = interiorStatic.Find('trinity.Tr2MeshArea')
        meshAreas.extend(staticMesh)

    for each in meshAreas:
        if not hasattr(each, 'effect'):
            continue
        if not hasattr(each.effect, 'highLevelShaderName'):
            continue
        for entry in params:
            if entry.highLevelShader != each.effect.highLevelShaderName:
                continue
            resourcePath = ''
            if entry.textureName != 'NoTexture' and entry.parameter in each.effect.parameters and hasattr(each.effect.parameters[entry.parameter], 'resourcePath'):
                resourcePath = each.effect.parameters[entry.parameter].resourcePath.lower()
            if entry.textureName.lower() in resourcePath or entry.textureName == 'NoTexture':
                SetShaderMaterialValue(each.effect.parameters, entry.parameter, entry.value, entry.hdr)


def SetShaderMaterialValue(parameter, effectEntry, value, modifier = 1.0):
    if isinstance(value, basestring):
        parameter[effectEntry].resourcePath = value
    elif isinstance(value, float):
        parameter[effectEntry].value = value * modifier
    else:
        parameter[effectEntry].value = [ x * modifier for x in value ]


def UpdateEnlightenTexture():
    pass


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('worldspaceCustomization', locals())
