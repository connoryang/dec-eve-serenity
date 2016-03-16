#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\systemMenu\betaOptions.py
from carbonui.util.bunch import Bunch
import evecamera
import localization
import service
BETA_MAP_SETTING_KEY = 'experimental_map_default'
BETA_SCANNERS_SETTING_KEY = 'experimental_scanners'
BETA_NEWCAM_SETTING_KEY = 'experimental_newcam'
DEFAULT_SETTINGS = {BETA_MAP_SETTING_KEY: True,
 BETA_SCANNERS_SETTING_KEY: True,
 BETA_NEWCAM_SETTING_KEY: False}

def ConstructOptInSection(column, columnWidth):
    optInOptions = GetOptInOptions()
    if not optInOptions:
        return
    from eve.client.script.ui.util.uix import GetContainerHeader
    from eve.client.script.ui.control.checkbox import Checkbox
    GetContainerHeader(localization.GetByLabel('UI/SystemMenu/GeneralSettings/Experimental/Header'), column, xmargin=-5)
    for each in optInOptions:
        Checkbox(text=each.label, parent=column, configName=each.settingKey, checked=GetUserSetting(each.settingKey), prefstype=('user', 'ui'), callback=OnBetaSettingChanged)


def OnBetaSettingChanged(checkbox):
    sm.GetService('neocom').UpdateNeocomButtons()
    settingID = checkbox.data['config']
    if settingID == BETA_NEWCAM_SETTING_KEY:
        ToggleNewCamera(checkbox.GetValue())


def ToggleNewCamera(activate):
    sceneMan = sm.GetService('sceneManager')
    camera = sceneMan.GetActiveCamera()
    if activate:
        if session.solarsystemid:
            sceneMan.SetActiveCameraByID(evecamera.CAM_SHIPORBIT)
    else:
        if session.solarsystemid:
            sceneMan.SetActiveCameraByID(evecamera.CAM_SPACE_PRIMARY)
        for cameraID in (evecamera.CAM_SHIPORBIT, evecamera.CAM_SHIPPOV, evecamera.CAM_TACTICAL):
            sceneMan.UnregisterCamera(cameraID)

    if uicore.layer.shipui.isopen:
        uicore.layer.shipui.SetupShip()
    uicore.cmd.Reload()


def IsGMRole():
    return session.role & (service.ROLE_GML | service.ROLE_WORLDMOD)


def IsBetaFeaturedEnabledInGlobalConfig(settingKey):
    globalConfig = sm.GetService('machoNet').GetGlobalConfig()
    if globalConfig is not None:
        return bool(int(globalConfig.get(settingKey, 0)))
    return True


def AppendNewMapOption(options):
    newMap = Bunch()
    newMap.settingKey = BETA_MAP_SETTING_KEY
    newMap.label = 'Try the New Map'
    options.append(newMap)


def AppendNewScannersOption(options):
    newMap = Bunch()
    newMap.settingKey = BETA_SCANNERS_SETTING_KEY
    newMap.label = 'Try the New Probe and Directional Scanners'
    options.append(newMap)


def AppendNewcamOption(options):
    newMap = Bunch()
    newMap.settingKey = BETA_NEWCAM_SETTING_KEY
    newMap.label = 'Try the New Camera'
    options.append(newMap)


def GetOptInOptions():
    if not session.userid:
        return []
    options = []
    if IsGMRole() or IsBetaFeaturedEnabledInGlobalConfig(BETA_MAP_SETTING_KEY):
        AppendNewMapOption(options)
    if IsGMRole() or IsBetaFeaturedEnabledInGlobalConfig(BETA_SCANNERS_SETTING_KEY):
        AppendNewScannersOption(options)
    if IsGMRole() or IsBetaFeaturedEnabledInGlobalConfig(BETA_NEWCAM_SETTING_KEY):
        AppendNewcamOption(options)
    return options


def GetUserSetting(settingKey):
    defaultValue = DEFAULT_SETTINGS.get(settingKey, False)
    return settings.user.ui.Get(settingKey, defaultValue)


def BetaFeatureEnabled(settingKey):
    if IsGMRole() or IsBetaFeaturedEnabledInGlobalConfig(settingKey):
        return bool(GetUserSetting(settingKey))
    return False


def IsBetaScannersEnabled():
    return BetaFeatureEnabled(BETA_SCANNERS_SETTING_KEY)
