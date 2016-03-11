#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\settings.py
import trinity
import threadutils
from yamlext.blueutil import ReadYamlFile
SETTINGS_GROUP_DEVICE = 'settings.public.device'
SETTINGS_GROUP_UI = 'settings.user.ui'
GFX_ANTI_ALIASING = (SETTINGS_GROUP_DEVICE, 'antiAliasing')
GFX_HDR_ENABLED = (SETTINGS_GROUP_DEVICE, 'hdrEnabled')
GFX_LOD_QUALITY = (SETTINGS_GROUP_DEVICE, 'lodQuality')
GFX_POST_PROCESSING_QUALITY = (SETTINGS_GROUP_DEVICE, 'postProcessingQuality')
GFX_SHADER_QUALITY = (SETTINGS_GROUP_DEVICE, 'shaderQuality')
GFX_SHADOW_QUALITY = (SETTINGS_GROUP_DEVICE, 'shadowQuality')
GFX_TEXTURE_QUALITY = (SETTINGS_GROUP_DEVICE, 'textureQuality')
GFX_INTERIOR_GRAPHICS_QUALITY = (SETTINGS_GROUP_DEVICE, 'interiorGraphicsQuality')
GFX_INTERIOR_SHADER_QUALITY = (SETTINGS_GROUP_DEVICE, 'interiorShaderQuality')
GFX_CHAR_TEXTURE_QUALITY = (SETTINGS_GROUP_DEVICE, 'charTextureQuality')
GFX_CHAR_FAST_CHARACTER_CREATION = (SETTINGS_GROUP_DEVICE, 'fastCharacterCreation')
GFX_CHAR_CLOTH_SIMULATION = (SETTINGS_GROUP_DEVICE, 'charClothSimulation')
GFX_UI_SCALE_WINDOWED = (SETTINGS_GROUP_DEVICE, 'UIScaleWindowed')
GFX_UI_SCALE_FULLSCREEN = (SETTINGS_GROUP_DEVICE, 'UIScaleFullscreen')
GFX_RESOLUTION_WINDOWED = (SETTINGS_GROUP_DEVICE, 'WindowedResolution')
GFX_RESOLUTION_FULLSCREEN = (SETTINGS_GROUP_DEVICE, 'FullScreenResolution')
GFX_WINDOW_BORDER_FIXED = (SETTINGS_GROUP_DEVICE, 'FixedWindow')
MISC_LOAD_STATION_ENV = (SETTINGS_GROUP_DEVICE, 'loadstationenv2')
MISC_RESOURCE_CACHE_ENABLED = (SETTINGS_GROUP_DEVICE, 'resourceCacheEnabled')
GFX_DEVICE_SETTINGS = (SETTINGS_GROUP_DEVICE, 'DeviceSettings')
GFX_BRIGHTNESS = (SETTINGS_GROUP_DEVICE, 'brightness')
UI_TURRETS_ENABLED = (SETTINGS_GROUP_UI, 'turretsEnabled')
UI_EFFECTS_ENABLED = (SETTINGS_GROUP_UI, 'effectsEnabled')
UI_MISSILES_ENABLED = (SETTINGS_GROUP_UI, 'missilesEnabled')
UI_DRONE_MODELS_ENABLED = (SETTINGS_GROUP_UI, 'droneModelsEnabled')
UI_EXPLOSION_EFFECTS_ENABLED = (SETTINGS_GROUP_UI, 'explosionEffectsEnabled')
UI_TRAILS_ENABLED = (SETTINGS_GROUP_UI, 'trailsEnabled')
UI_GPU_PARTICLES_ENABLED = (SETTINGS_GROUP_UI, 'gpuParticlesEnabled')
UI_ASTEROID_ATMOSPHERICS = (SETTINGS_GROUP_UI, 'UI_ASTEROID_ATMOSPHERICS')
UI_ASTEROID_FOG = (SETTINGS_GROUP_UI, 'UI_ASTEROID_FOG')
UI_ASTEROID_CLOUDFIELD = (SETTINGS_GROUP_UI, 'UI_ASTEROID_CLOUDFIELD')
UI_ASTEROID_GODRAYS = (SETTINGS_GROUP_UI, 'UI_ASTEROID_GODRAYS')
UI_ASTEROID_PARTICLES = (SETTINGS_GROUP_UI, 'UI_ASTEROID_PARTICLES')
UI_GODRAYS = (SETTINGS_GROUP_UI, 'UI_GODRAYS')
UI_CAMERA_OFFSET = (SETTINGS_GROUP_UI, 'cameraOffset')
UI_OFFSET_UI_WITH_CAMERA = (SETTINGS_GROUP_UI, 'offsetUIwithCamera')
UI_CAMERA_SHAKE_ENABLED = (SETTINGS_GROUP_UI, 'cameraShakeEnabled')
UI_CAMERA_BOBBING_ENABLED = (SETTINGS_GROUP_UI, 'cameraBobbingEnabled')
UI_ADVANCED_CAMERA = (SETTINGS_GROUP_UI, 'advancedCamera')
UI_INVERT_CAMERA_ZOOM = (SETTINGS_GROUP_UI, 'invertCameraZoom')
UI_INCARNA_CAMERA_OFFSET = (SETTINGS_GROUP_UI, 'incarnaCameraOffset')
UI_INCARNA_CAMERA_INVERT_Y = (SETTINGS_GROUP_UI, 'incarnaCameraInvertY')
UI_INCARNA_CAMERA_MOUSE_LOOK_SPEED = (SETTINGS_GROUP_UI, 'incarnaCameraMouseLookSpeed')
UI_NCC_GREEN_SCREEN = (SETTINGS_GROUP_UI, 'NCCgreenscreen')
UI_SHIPSKINSINSPACE_ENABLED = (SETTINGS_GROUP_UI, 'shipskinsInSpaceEnabled')
AA_TYPE_MSAA = 4096
AA_TYPE_TAA = 8192
AA_QUALITY_MASK = 4095
AA_TYPE_MASK = 61440
AA_QUALITY_DISABLED = 0
AA_QUALITY_MSAA_LOW = AA_TYPE_MSAA + 1
AA_QUALITY_MSAA_MEDIUM = AA_TYPE_MSAA + 2
AA_QUALITY_MSAA_HIGH = AA_TYPE_MSAA + 3
AA_QUALITY_TAA_LOW = AA_TYPE_TAA + 1
AA_QUALITY_TAA_MEDIUM = AA_TYPE_TAA + 2
AA_QUALITY_TAA_HIGH = AA_TYPE_TAA + 3
AA_TO_MSAA = {AA_QUALITY_TAA_LOW: AA_QUALITY_DISABLED,
 AA_QUALITY_TAA_MEDIUM: AA_QUALITY_MSAA_LOW,
 AA_QUALITY_TAA_HIGH: AA_QUALITY_MSAA_MEDIUM}

def IsTAAEnabled(aaQuality):
    return aaQuality & AA_TYPE_TAA


def GetMSAAQuality(aaQuality):
    if aaQuality in AA_TO_MSAA:
        aaQuality = AA_TO_MSAA[aaQuality]
    return aaQuality


@threadutils.Memoize
def _LoadDeviceClassifications():
    result = ReadYamlFile('res:/videoCardCategories.yaml')
    if result is None:
        result = {'high': {},
         'medium': {},
         'low': {}}
    return result


DEVICE_HIGH_END = 'high'
DEVICE_MID_RANGE = 'medium'
DEVICE_LOW_END = 'low'

class UninitializedSettingsGroupError(Exception):
    pass


class NoAdaptersFoundError(Exception):
    pass


@threadutils.Memoize
def GetDeviceClassification():
    identifier = None
    if trinity.device.deviceType == trinity.TriDeviceType.SOFTWARE:
        return DEVICE_HIGH_END
    if trinity.adapters.GetAdapterCount() > 0:
        identifier = trinity.adapters.GetAdapterInfo(0)
    if identifier is None:
        raise NoAdaptersFoundError()
    deviceID = identifier.vendorID
    vendorID = identifier.deviceID
    deviceClassifications = _LoadDeviceClassifications()
    if (vendorID, deviceID) in deviceClassifications['high']:
        return DEVICE_HIGH_END
    if (vendorID, deviceID) in deviceClassifications['medium']:
        return DEVICE_MID_RANGE
    if (vendorID, deviceID) in deviceClassifications['low']:
        return DEVICE_LOW_END
    return DEVICE_HIGH_END


SECONDARY_LIGHTING_INTENSITY = 7
SHADER_MODEL_LOW = 1
SHADER_MODEL_MEDIUM = 2
SHADER_MODEL_HIGH = 3
if not trinity.renderJobUtils.DeviceSupportsIntZ():
    MAX_SHADER_MODEL = SHADER_MODEL_MEDIUM
else:
    MAX_SHADER_MODEL = SHADER_MODEL_HIGH
defaultCommonSettings = {SETTINGS_GROUP_DEVICE: {MISC_LOAD_STATION_ENV: 1,
                         MISC_RESOURCE_CACHE_ENABLED: 0,
                         GFX_UI_SCALE_WINDOWED: 1.0,
                         GFX_UI_SCALE_FULLSCREEN: 1.0,
                         GFX_RESOLUTION_WINDOWED: None,
                         GFX_RESOLUTION_FULLSCREEN: None,
                         GFX_WINDOW_BORDER_FIXED: 0,
                         GFX_ANTI_ALIASING: AA_QUALITY_DISABLED,
                         GFX_HDR_ENABLED: 0,
                         GFX_LOD_QUALITY: 3,
                         GFX_TEXTURE_QUALITY: 0,
                         GFX_SHADER_QUALITY: MAX_SHADER_MODEL,
                         GFX_CHAR_TEXTURE_QUALITY: 1,
                         GFX_CHAR_FAST_CHARACTER_CREATION: 0,
                         GFX_CHAR_CLOTH_SIMULATION: 1,
                         GFX_DEVICE_SETTINGS: None,
                         GFX_BRIGHTNESS: 1.0},
 SETTINGS_GROUP_UI: {UI_TURRETS_ENABLED: 1,
                     UI_EFFECTS_ENABLED: 1,
                     UI_MISSILES_ENABLED: 1,
                     UI_DRONE_MODELS_ENABLED: 1,
                     UI_EXPLOSION_EFFECTS_ENABLED: 1,
                     UI_TRAILS_ENABLED: 1,
                     UI_GPU_PARTICLES_ENABLED: 1,
                     UI_ASTEROID_ATMOSPHERICS: 1,
                     UI_ASTEROID_CLOUDFIELD: 1,
                     UI_ASTEROID_FOG: 1,
                     UI_ASTEROID_GODRAYS: 1,
                     UI_ASTEROID_PARTICLES: 1,
                     UI_GODRAYS: 0,
                     UI_SHIPSKINSINSPACE_ENABLED: 1,
                     UI_CAMERA_OFFSET: 0,
                     UI_OFFSET_UI_WITH_CAMERA: 0,
                     UI_CAMERA_SHAKE_ENABLED: 1,
                     UI_CAMERA_BOBBING_ENABLED: 1,
                     UI_ADVANCED_CAMERA: 0,
                     UI_INVERT_CAMERA_ZOOM: 0,
                     UI_INCARNA_CAMERA_OFFSET: 0.0,
                     UI_INCARNA_CAMERA_INVERT_Y: 0,
                     UI_INCARNA_CAMERA_MOUSE_LOOK_SPEED: 0.005,
                     UI_NCC_GREEN_SCREEN: 0}}
defaultClassificationSettings = {SETTINGS_GROUP_DEVICE: {DEVICE_HIGH_END: {GFX_POST_PROCESSING_QUALITY: 2,
                                           GFX_SHADOW_QUALITY: 2,
                                           GFX_INTERIOR_GRAPHICS_QUALITY: 2,
                                           GFX_INTERIOR_SHADER_QUALITY: 1},
                         DEVICE_MID_RANGE: {GFX_POST_PROCESSING_QUALITY: 1,
                                            GFX_SHADOW_QUALITY: 1,
                                            GFX_INTERIOR_GRAPHICS_QUALITY: 1,
                                            GFX_INTERIOR_SHADER_QUALITY: 0},
                         DEVICE_LOW_END: {GFX_POST_PROCESSING_QUALITY: 0,
                                          GFX_SHADOW_QUALITY: 0,
                                          GFX_INTERIOR_GRAPHICS_QUALITY: 0,
                                          GFX_INTERIOR_SHADER_QUALITY: 0}},
 SETTINGS_GROUP_UI: {DEVICE_HIGH_END: {},
                     DEVICE_MID_RANGE: {},
                     DEVICE_LOW_END: {}}}

def GetSettingKey(setting):
    return setting[1]


def GetSettingGroupName(setting):
    return setting[0]


def GetDefault(setting):
    group, item = setting
    if setting in defaultCommonSettings[group]:
        return defaultCommonSettings[group][setting]
    return defaultClassificationSettings[group][GetDeviceClassification()][setting]


def GetSettingFromSettingKey(key):
    for group in defaultCommonSettings:
        for setting in defaultCommonSettings[group]:
            if key == GetSettingKey(setting):
                return setting

    for group in defaultClassificationSettings:
        for setting in defaultClassificationSettings[group][GetDeviceClassification()]:
            if key == GetSettingKey(setting):
                return setting


class GraphicsSettings(object):
    _globalInstance = None

    def __init__(self):
        self.settingsGroups = {}
        self.pendingSettings = {}
        self.storedValues = {}

    def InitializeSettingsGroup(self, groupName, settingsGroup):
        self.pendingSettings[groupName] = {}
        self.settingsGroups[groupName] = settingsGroup
        self._InitializeSettings(groupName, settingsGroup)

    def _GetSettingsGroup(self, group):
        if group not in self.settingsGroups:
            msg = 'GraphicsSettings.Get called on uninitialized settings group, ' + group
            raise UninitializedSettingsGroupError(msg)
        return self.settingsGroups[group]

    def _GetPendingGroup(self, group):
        if group not in self.pendingSettings:
            msg = 'GraphicsSettings.Get called on uninitialized settings group, ' + group
            raise UninitializedSettingsGroupError(msg)
        return self.pendingSettings[group]

    def _InitializeSettings(self, groupName, settingsGroup):

        def _SetSetting(setting):
            key = GetSettingKey(setting)
            settingsGroup.Set(key, settingsGroup.Get(key, GetDefault(setting)))

        for setting in defaultCommonSettings[groupName]:
            _SetSetting(setting)

        for setting in defaultClassificationSettings[groupName][GetDeviceClassification()]:
            _SetSetting(setting)

    def Get(self, setting):
        group = self._GetSettingsGroup(GetSettingGroupName(setting))
        key = GetSettingKey(setting)
        return group.Get(key)

    def Set(self, setting, value):
        group = self._GetSettingsGroup(GetSettingGroupName(setting))
        key = GetSettingKey(setting)
        return group.Set(key, value)

    def SetPending(self, setting, value):
        group = self._GetPendingGroup(GetSettingGroupName(setting))
        group[setting] = value

    def GetPendingOrCurrent(self, setting):
        group = self._GetPendingGroup(GetSettingGroupName(setting))
        if setting in group:
            return group[setting]
        return self.Get(setting)

    def ApplyPendingChanges(self, groupName):
        changes = []
        group = self._GetPendingGroup(groupName)
        for setting in group:
            if group[setting] != self.Get(setting):
                changes.append(setting)
                self.Set(setting, group[setting])

        self.ClearPendingChanges(groupName)
        return changes

    def ClearPendingChanges(self, groupName):
        group = self._GetPendingGroup(groupName)
        group.clear()

    @staticmethod
    def GetGlobal():
        if GraphicsSettings._globalInstance is None:
            GraphicsSettings._globalInstance = GraphicsSettings()
        return GraphicsSettings._globalInstance


def Get(setting, default = None):
    gfx = GraphicsSettings.GetGlobal()
    value = gfx.Get(setting)
    if value is None:
        return default
    return value


def Set(setting, value, pending = True):
    gfx = GraphicsSettings.GetGlobal()
    if pending:
        gfx.SetPending(setting, value)
    else:
        gfx.Set(setting, value)


def SetDefault(setting, pending = True):
    gfx = GraphicsSettings.GetGlobal()
    if pending:
        gfx.SetPending(setting, GetDefault(setting))
    else:
        gfx.Set(setting, GetDefault(setting))


def GetPendingOrCurrent(setting):
    gfx = GraphicsSettings.GetGlobal()
    return gfx.GetPendingOrCurrent(setting)


def ApplyPendingChanges(groupName):
    gfx = GraphicsSettings.GetGlobal()
    return gfx.ApplyPendingChanges(groupName)


def ClearPendingChanges(groupName):
    gfx = GraphicsSettings.GetGlobal()
    gfx.ClearPendingChanges(groupName)


def ValidateSettings():
    aaQuality = Get(GFX_ANTI_ALIASING)
    if aaQuality & AA_QUALITY_MASK != 0 and aaQuality & AA_TYPE_MASK == 0:
        if aaQuality == 3:
            aaQuality = AA_QUALITY_TAA_HIGH
        else:
            aaQuality = aaQuality + AA_TYPE_MSAA
        Set(GFX_ANTI_ALIASING, aaQuality, pending=False)
    taaSupported = trinity._singletons.platform == 'dx11' and Get(GFX_SHADER_QUALITY) == SHADER_MODEL_HIGH
    if not taaSupported and aaQuality & AA_TYPE_MASK == AA_TYPE_TAA:
        Set(GFX_ANTI_ALIASING, AA_QUALITY_MSAA_MEDIUM, pending=False)
    shaderQuality = Get(GFX_SHADER_QUALITY)
    if MAX_SHADER_MODEL < shaderQuality:
        Set(GFX_SHADER_QUALITY, SHADER_MODEL_MEDIUM, pending=False)
