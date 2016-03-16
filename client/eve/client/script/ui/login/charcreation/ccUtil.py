#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\charcreation\ccUtil.py
import paperDoll
import charactercreator.const as ccConst
import telemetry
import blue
import yaml
import trinity

@telemetry.ZONE_FUNCTION
def GenderIDToPaperDollGender(genderID):
    if genderID == ccConst.GENDERID_FEMALE:
        return paperDoll.GENDER.FEMALE
    if genderID == ccConst.GENDERID_MALE:
        return paperDoll.GENDER.MALE
    raise RuntimeError('GenderIDToPaperDollGender: Invalid genderID!')


@telemetry.ZONE_FUNCTION
def PaperDollGenderToGenderID(gender):
    if gender == paperDoll.GENDER.MALE:
        return ccConst.GENDERID_MALE
    if gender == paperDoll.GENDER.FEMALE:
        return ccConst.GENDERID_FEMALE
    raise RuntimeError('PaperDollGenderToGenderID: Invalid gender!')


@telemetry.ZONE_FUNCTION
def SetupLighting(scene, lightScene, lightColorScene, lightIntensity = 0.5):
    intensityMultiplier = 0.75 + lightIntensity / 2.0
    if scene is not None:
        lightList = []
        for l in scene.lights:
            lightList.append(l)

        for l in lightList:
            scene.RemoveLightSource(l)

        for index in range(len(lightScene.lights)):
            light = lightScene.lights[index]
            for l in lightColorScene.lights:
                if l.name == light.name:
                    light.color = l.color

            light.color = (light.color[0] * intensityMultiplier,
             light.color[1] * intensityMultiplier,
             light.color[2] * intensityMultiplier,
             1.0)
            scene.AddLightSource(light)

        if paperDoll.SkinSpotLightShadows.instance is not None:
            paperDoll.SkinSpotLightShadows.instance.RefreshLights()


@telemetry.ZONE_FUNCTION
def LoadFromYaml(path):
    return paperDoll.LoadYamlFileNicely(path)


def HasUserDefinedWeight(category):
    return ccConst.COLORMAPPING.get(category, (0, 0))[0]


def HasUserDefinedSpecularity(category):
    return ccConst.COLORMAPPING.get(category, (0, 0))[1]


def SupportsHigherShaderModel():
    shaderModel = trinity.GetShaderModel()
    maxSupported = trinity.GetMaxShaderModelSupported()
    if shaderModel == 'SM_2_0_LO' and maxSupported.startswith('SM_3'):
        return True
    return False


def CreateCategoryFolderIfNeeded(outputroot, folderName):
    import os
    folderName = os.path.normpath(folderName)
    if os.path.isdir(outputroot + folderName):
        return
    os.mkdir(outputroot + folderName)


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('ccUtil', globals())
