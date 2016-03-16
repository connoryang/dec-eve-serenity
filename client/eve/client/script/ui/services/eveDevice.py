#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\eveDevice.py
import uicontrols
import blue
import trinity
from trinity import _singletons
from carbonui.services.device import DeviceMgr
import localization
import uthread
import evegraphics.settings as gfxsettings
NVIDIA_VENDORID = 4318

class EveDeviceMgr(DeviceMgr):
    __guid__ = 'svc.eveDevice'
    __replaceservice__ = 'device'

    def AppRun(self):
        if not settings.public.generic.Get('resourceUnloading', 1):
            trinity.SetEveSpaceObjectResourceUnloadingEnabled(0)
        self.defaultPresentationInterval = trinity.PRESENT_INTERVAL.ONE
        gfx = gfxsettings.GraphicsSettings.GetGlobal()
        gfx.InitializeSettingsGroup(gfxsettings.SETTINGS_GROUP_DEVICE, settings.public.device)
        if gfxsettings.Get(gfxsettings.GFX_INTERIOR_SHADER_QUALITY) != 0:
            trinity.AddGlobalSituationFlags(['OPT_INTERIOR_SM_HIGH'])
        else:
            trinity.RemoveGlobalSituationFlags(['OPT_INTERIOR_SM_HIGH'])
        blue.classes.maxPendingDeletes = 20000
        blue.classes.maxTimeForPendingDeletes = 4.0
        blue.classes.pendingDeletesEnabled = True
        self.deviceCreated = False
        if blue.sysinfo.isTransgaming:
            self.cider = sm.GetService('cider')
            self.ciderFullscreenLast = False
            self.ciderFullscreenBackup = False

    def Initialize(self):
        DeviceMgr.Initialize(self)
        self.msaaTypes = {}
        gfxsettings.ValidateSettings()
        aaQuality = gfxsettings.Get(gfxsettings.GFX_ANTI_ALIASING)
        msaaQuality = gfxsettings.GetMSAAQuality(aaQuality)
        msaaType = self.GetMSAATypeFromQuality(aaQuality)
        if msaaQuality > 0 and msaaType == 0:
            gfxsettings.Set(gfxsettings.GFX_ANTI_ALIASING, gfxsettings.AA_QUALITY_DISABLED, pending=False)
        brightness = gfxsettings.Get(gfxsettings.GFX_BRIGHTNESS)
        trinity.settings.SetValue('eveSpaceSceneGammaBrightness', brightness)

    def CreateDevice(self):
        DeviceMgr.CreateDevice(self)
        if blue.sysinfo.isTransgaming:
            tgToggleEventHandler = blue.BlueEventToPython()
            tgToggleEventHandler.handler = self.ToggleWindowedTransGaming
            trinity.app.tgToggleEventListener = tgToggleEventHandler

    def GetMSAATypeFromQuality(self, quality):
        key = self.GetMSAAQualityFromAAQuality(quality)
        return self.msaaTypes.get(key, 0)

    def GetMSAAQualityFromAAQuality(self, quality):
        if quality == 0:
            return 0
        if len(self.msaaTypes) < 1:
            set = self.GetSettings()
            formats = [(set.BackBufferFormat, True), (set.AutoDepthStencilFormat, False), (trinity.PIXEL_FORMAT.R16G16B16A16_FLOAT, True)]
            self.RefreshSupportedAATypes(set, formats)
        if quality not in self.aaTypes:
            quality = gfxsettings.AA_QUALITY_DISABLED
        return gfxsettings.GetMSAAQuality(quality)

    def GetShaderModel(self, val):
        if val == 3:
            if not trinity.renderJobUtils.DeviceSupportsIntZ():
                return 'SM_3_0_HI'
            else:
                return 'SM_3_0_DEPTH'
        elif val == 2:
            return 'SM_3_0_HI'
        return 'SM_3_0_LO'

    def GetWindowModes(self):
        self.LogInfo('GetWindowModes')
        adapter = self.CurrentAdapter()
        if adapter.format not in self.validFormats:
            return [(localization.GetByLabel('/Carbon/UI/Service/Device/FullScreen'), 0)]
        elif blue.sysinfo.isTransgaming:
            return [(localization.GetByLabel('/Carbon/UI/Service/Device/WindowMode'), 1), (localization.GetByLabel('/Carbon/UI/Service/Device/FullScreen'), 0)]
        else:
            return [(localization.GetByLabel('/Carbon/UI/Service/Device/WindowMode'), 1), (localization.GetByLabel('/Carbon/UI/Service/Device/FullScreen'), 0), (localization.GetByLabel('/Carbon/UI/Service/Device/FixedWindowMode'), 2)]

    def GetAppShaderModel(self):
        shaderQuality = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        return self.GetShaderModel(shaderQuality)

    def GetAppSettings(self):
        appSettings = {}
        lodQuality = gfxsettings.Get(gfxsettings.GFX_LOD_QUALITY)
        if lodQuality == 1:
            appSettings = {'eveSpaceSceneVisibilityThreshold': 15.0,
             'eveSpaceSceneLowDetailThreshold': 140.0,
             'eveSpaceSceneMediumDetailThreshold': 480.0}
        elif lodQuality == 2:
            appSettings = {'eveSpaceSceneVisibilityThreshold': 6,
             'eveSpaceSceneLowDetailThreshold': 70,
             'eveSpaceSceneMediumDetailThreshold': 240}
        elif lodQuality == 3:
            appSettings = {'eveSpaceSceneVisibilityThreshold': 3.0,
             'eveSpaceSceneLowDetailThreshold': 35.0,
             'eveSpaceSceneMediumDetailThreshold': 120.0}
        return appSettings

    def GetAppMipLevelSkipExclusionDirectories(self):
        return ['res:/Texture/IntroScene', 'res:/UI/Texture']

    def IsWindowed(self, settings = None):
        if settings is None:
            settings = self.GetSettings()
        if blue.sysinfo.isTransgaming:
            return not self.cider.GetFullscreen()
        return settings.Windowed

    def SetToSafeMode(self):
        gfxsettings.Set(gfxsettings.GFX_TEXTURE_QUALITY, 2, pending=False)
        gfxsettings.Set(gfxsettings.GFX_SHADER_QUALITY, 1, pending=False)
        gfxsettings.Set(gfxsettings.GFX_HDR_ENABLED, False, pending=False)
        gfxsettings.Set(gfxsettings.GFX_POST_PROCESSING_QUALITY, 0, pending=False)
        gfxsettings.Set(gfxsettings.GFX_SHADOW_QUALITY, 0, pending=False)
        gfxsettings.Set(gfxsettings.MISC_RESOURCE_CACHE_ENABLED, 0, pending=False)

    def SetDeviceCiderStartup(self, *args, **kwds):
        devSettings = args[0]
        settingsCopy = devSettings.copy()
        devSettings.BackBufferWidth, devSettings.BackBufferHeight = self.GetPreferedResolution(False)
        self.cider.SetFullscreen(True)
        DeviceMgr.SetDevice(self, devSettings, **kwds)
        self.cider.SetFullscreen(False)
        self.ciderFullscreenLast = False
        DeviceMgr.SetDevice(self, settingsCopy, **kwds)

    def SetDeviceCiderFullscreen(self, *args, **kwds):
        DeviceMgr.SetDevice(self, *args, **kwds)
        self.cider.SetFullscreen(True)

    def SetDeviceCiderWindowed(self, *args, **kwds):
        self.cider.SetFullscreen(False)
        DeviceMgr.SetDevice(self, *args, **kwds)

    def SetDevice(self, *args, **kwds):
        if blue.sysinfo.isTransgaming:
            ciderFullscreen = self.cider.GetFullscreen()
            self.ciderFullscreenLast = self.cider.GetFullscreen(apiCheck=True)
            if not self.deviceCreated and not ciderFullscreen:
                self.SetDeviceCiderStartup(*args, **kwds)
            elif ciderFullscreen:
                self.SetDeviceCiderFullscreen(*args, **kwds)
            else:
                self.SetDeviceCiderWindowed(*args, **kwds)
            self.deviceCreated = True
            return True
        else:
            return DeviceMgr.SetDevice(self, *args, **kwds)

    def BackupSettings(self):
        DeviceMgr.BackupSettings(self)
        if blue.sysinfo.isTransgaming:
            self.ciderFullscreenBackup = self.ciderFullscreenLast

    def DiscardChanges(self, *args):
        if self.settingsBackup:
            if blue.sysinfo.isTransgaming:
                self.cider.SetFullscreen(self.ciderFullscreenBackup, setAPI=False)
            self.SetDevice(self.settingsBackup)

    def ToggleWindowedTransGaming(self, *args):
        self.LogInfo('ToggleWindowedTransGaming')
        windowed = not self.cider.GetFullscreen(apiCheck=True)
        self.cider.SetFullscreen(not windowed)
        if windowed:
            wr = trinity.app.GetWindowRect()
            self.preFullScreenPosition = (wr.left, wr.top)
        devSettings = self.GetSettings()
        devSettings.BackBufferWidth, devSettings.BackBufferHeight = self.GetPreferedResolution(windowed)
        uthread.new(self.SetDevice, devSettings, hideTitle=True)

    def RefreshSupportedAATypes(self, deviceSettings = None, formats = None, shaderModel = None):
        self.msaaTypes = {gfxsettings.AA_QUALITY_DISABLED: 0}
        self.aaTypes = [gfxsettings.AA_QUALITY_DISABLED]

        def Supported(msType):
            supported = True
            for format in formats:
                if format[1]:
                    qualityLevels = trinity.adapters.GetRenderTargetMsaaSupport(deviceSettings.Adapter, format[0], deviceSettings.Windowed, msType)
                else:
                    qualityLevels = trinity.adapters.GetDepthStencilMsaaSupport(deviceSettings.Adapter, format[0], deviceSettings.Windowed, msType)
                supported = supported and qualityLevels

            return supported

        if Supported(2):
            self.aaTypes.append(gfxsettings.AA_QUALITY_MSAA_LOW)
            self.msaaTypes[gfxsettings.AA_QUALITY_MSAA_LOW] = 2
        if Supported(4):
            self.aaTypes.append(gfxsettings.AA_QUALITY_MSAA_MEDIUM)
            self.msaaTypes[gfxsettings.AA_QUALITY_MSAA_MEDIUM] = 4
        if shaderModel is None:
            shaderModel = gfxsettings.GetPendingOrCurrent(gfxsettings.GFX_SHADER_QUALITY)
        if _singletons.platform == 'dx11' and shaderModel == gfxsettings.SHADER_MODEL_HIGH:
            self.aaTypes.append(gfxsettings.AA_QUALITY_TAA_HIGH)
            for each in self.aaTypes:
                if each in gfxsettings.AA_TO_MSAA and gfxsettings.AA_TO_MSAA[each] in self.msaaTypes:
                    self.msaaTypes[each] = self.msaaTypes[gfxsettings.AA_TO_MSAA[each]]

    def GetAntiAliasingLabel(self, aaQuality):
        aaLabels = {gfxsettings.AA_QUALITY_DISABLED: localization.GetByLabel('/Carbon/UI/Common/Disabled'),
         gfxsettings.AA_QUALITY_MSAA_LOW: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/LowQuality'),
         gfxsettings.AA_QUALITY_MSAA_MEDIUM: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/MediumQuality'),
         gfxsettings.AA_QUALITY_TAA_HIGH: localization.GetByLabel('UI/SystemMenu/DisplayAndGraphics/Common/HighQuality')}
        return aaLabels[aaQuality]

    def GetAntiAliasingOptions(self, deviceSettings = None, formats = None, shaderModel = None):
        if deviceSettings is None:
            deviceSettings = self.GetSettings()
        if formats is None:
            formats = [(deviceSettings.BackBufferFormat, True), (deviceSettings.AutoDepthStencilFormat, False)]
        self.RefreshSupportedAATypes(deviceSettings, formats, shaderModel)
        aaOptions = []
        for each in self.aaTypes:
            aaOptions.append((self.GetAntiAliasingLabel(each), each))

        return aaOptions

    def EnforceDeviceSettings(self, devSettings):
        devSettings.BackBufferFormat = self.GetBackbufferFormats()[0]
        devSettings.AutoDepthStencilFormat = self.GetStencilFormats()[0]
        devSettings.MultiSampleType = 0
        devSettings.MultiSampleQuality = 0
        return devSettings

    def GetAdapterResolutionsAndRefreshRates(self, set = None):
        options, resoptions = DeviceMgr.GetAdapterResolutionsAndRefreshRates(self, set)
        if set.Windowed:
            maxWidth = trinity.app.GetVirtualScreenWidth()
            maxHeight = trinity.app.GetVirtualScreenHeight()
            maxLabel = localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=maxWidth, height=maxHeight)
            maxOp = (maxLabel, (maxWidth, maxHeight))
            if maxOp not in options:
                options.append(maxOp)
        elif blue.sysinfo.isTransgaming and self.IsWindowed(set):
            width = trinity.app.GetVirtualScreenWidth()
            height = trinity.app.GetVirtualScreenHeight() - 44
            if height < trinity.app.minimumHeight:
                height = trinity.app.minimumHeight
            label = localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=width, height=height)
            op = (label, (width, height))
            if op not in options:
                options.append(op)
            width = width / 2
            if width < trinity.app.minimumWidth:
                width = trinity.app.minimumWidth
            label = localization.GetByLabel('/Carbon/UI/Service/Device/ScreenSize', width=width, height=height)
            op = (label, (width, height))
            if op not in options:
                options.append(op)
        return (options, resoptions)

    def GetAppFeatureState(self, featureName, featureDefaultState):
        interiorGraphicsQuality = gfxsettings.Get(gfxsettings.GFX_INTERIOR_GRAPHICS_QUALITY)
        postProcessingQuality = gfxsettings.Get(gfxsettings.GFX_POST_PROCESSING_QUALITY)
        shaderQuality = gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY)
        shadowQuality = gfxsettings.Get(gfxsettings.GFX_SHADOW_QUALITY)
        interiorShaderQuality = gfxsettings.Get(gfxsettings.GFX_INTERIOR_SHADER_QUALITY)
        if featureName == 'Interior.ParticlesEnabled':
            return interiorGraphicsQuality == 2
        elif featureName == 'Interior.LensflaresEnabled':
            return interiorGraphicsQuality >= 1
        elif featureName == 'Interior.lowSpecMaterialsEnabled':
            return interiorGraphicsQuality == 0
        elif featureName == 'Interior.ssaoEnbaled':
            identifier = self.cachedAdapterIdentifiers[0]
            if identifier is not None:
                vendorID = identifier.vendorID
                if vendorID != 4318:
                    return False
            return postProcessingQuality != 0 and shaderQuality > 1
        elif featureName == 'Interior.dynamicShadows':
            return shadowQuality > 1
        elif featureName == 'Interior.lightPerformanceLevel':
            return interiorGraphicsQuality
        elif featureName == 'Interior.clothSimulation':
            identifier = self.cachedAdapterIdentifiers[0]
            if identifier is None:
                return featureDefaultState
            vendorID = identifier.vendorID
            return vendorID == NVIDIA_VENDORID and gfxsettings.Get(gfxsettings.GFX_CHAR_CLOTH_SIMULATION) and interiorGraphicsQuality == 2 and not blue.sysinfo.isTransgaming
        elif featureName == 'CharacterCreation.clothSimulation':
            return gfxsettings.Get(gfxsettings.GFX_CHAR_CLOTH_SIMULATION)
        elif featureName == 'Interior.useSHLighting':
            return interiorShaderQuality > 0
        else:
            return featureDefaultState

    def GetUIScalingOptions(self, height = None):
        if height:
            desktopHeight = height
        else:
            desktopHeight = uicore.desktop.height
        options = [(localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=90), 0.9), (localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=100), 1.0)]
        if desktopHeight >= 900:
            options.append((localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=110), 1.1))
        if desktopHeight >= 960:
            options.append((localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=125), 1.25))
        if desktopHeight >= 1200:
            options.append((localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=150), 1.5))
        return options

    def GetChange(self, scaleValue):
        oldHeight = int(trinity.device.height / uicore.desktop.dpiScaling)
        oldWidth = int(trinity.device.width / uicore.desktop.dpiScaling)
        newHeight = int(trinity.device.height / scaleValue)
        newWidth = int(trinity.device.width / scaleValue)
        changeDict = {}
        changeDict['ScalingWidth'] = (oldWidth, newWidth)
        changeDict['ScalingHeight'] = (oldHeight, newHeight)
        return changeDict

    def CapUIScaleValue(self, checkValue):
        desktopHeight = trinity.device.height
        minScale = 0.9
        if desktopHeight < 900:
            maxScale = 1.0
        elif desktopHeight < 960:
            maxScale = 1.1
        elif desktopHeight < 1200:
            maxScale = 1.25
        else:
            maxScale = 1.5
        return max(minScale, min(maxScale, checkValue))

    def SetupUIScaling(self):
        if not uicore.desktop:
            return
        windowed = self.IsWindowed()
        self.SetUIScaleValue(self.GetUIScaleValue(windowed), windowed)

    def SetUIScaleValue(self, scaleValue, windowed):
        self.LogInfo('SetUIScaleValue', scaleValue, 'windowed', windowed)
        capValue = self.CapUIScaleValue(scaleValue)
        if windowed:
            gfxsettings.Set(gfxsettings.GFX_UI_SCALE_WINDOWED, capValue, pending=False)
        else:
            gfxsettings.Set(gfxsettings.GFX_UI_SCALE_FULLSCREEN, capValue, pending=False)
        if capValue != uicore.desktop.dpiScaling:
            PreUIScaleChange_DesktopLayout = uicontrols.Window.GetDesktopWindowLayout()
            oldValue = uicore.desktop.dpiScaling
            uicore.desktop.dpiScaling = capValue
            uicore.desktop.UpdateSize()
            self.LogInfo('SetUIScaleValue capValue', capValue)
            sm.ScatterEvent('OnUIScalingChange', (oldValue, capValue))
            uicontrols.Window.LoadDesktopWindowLayout(PreUIScaleChange_DesktopLayout)
        else:
            self.LogInfo('SetUIScaleValue No Change')

    def GetUIScaleValue(self, windowed):
        if windowed:
            scaleValue = gfxsettings.Get(gfxsettings.GFX_UI_SCALE_WINDOWED)
        else:
            scaleValue = gfxsettings.Get(gfxsettings.GFX_UI_SCALE_FULLSCREEN)
        return scaleValue

    def ApplyTrinityUserSettings(self):
        effectsEnabled = gfxsettings.Get(gfxsettings.UI_EFFECTS_ENABLED)
        trailsEnabled = effectsEnabled and gfxsettings.Get(gfxsettings.UI_TRAILS_ENABLED)
        trinity.settings.SetValue('eveSpaceObjectTrailsEnabled', trailsEnabled)
