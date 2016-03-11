#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\achievementSettings.py
from achievements.common.achievementConst import AchievementSettingConst
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.utilMenu import UtilMenu
import eve.common.script.util.notificationconst as notificationConst
from localization import GetByLabel
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
import uthread
NOTIFICATIONIDS = [notificationConst.notificationTypeAchievementTaskFinished, notificationConst.notificationTypeOpportunityFinished]

class OpportunitySettings(object):

    def __init__(self, *args, **kwargs):
        self.handler = NotificationSettingHandler()
        self.disableNotifications = self.GetNotifcationSettingCheckState()
        self.oldDisableNotifications = self.disableNotifications
        self.disableAura = settings.user.ui.Get(AchievementSettingConst.AURA_DISABLE_CONFIG, False)
        self.oldDisableAura = self.disableAura
        self.hideInfoPanel = settings.user.ui.Get(AchievementSettingConst.INFOPANEL_DISABLE_CONFIG, False)
        self.oldHideInfoPanel = self.hideInfoPanel

    def GetOpportunitySettings(self, menuParent):
        menuParent.AddCheckBox(text=GetByLabel('UI/Achievements/SupressNotifications'), checked=self.disableNotifications, callback=self.OnNotificationSettingsChanged)
        menuParent.AddCheckBox(text=GetByLabel('UI/Achievements/SuppressAura'), checked=self.disableAura, callback=self.OnAuraSettingsChanged)
        menuParent.AddCheckBox(text=GetByLabel('UI/Achievements/HideFromInfoPanel'), checked=self.hideInfoPanel, callback=self.OnInfoPanelSettingsChanged)

    def OnAuraSettingsChanged(self):
        self.disableAura = not self.disableAura

    def OnInfoPanelSettingsChanged(self):
        self.hideInfoPanel = not self.hideInfoPanel

    def OnNotificationSettingsChanged(self):
        self.disableNotifications = not self.disableNotifications

    def GetNotifcationSettingCheckState(self):
        notificationSetting = self.handler.LoadSettings()
        for settingID in NOTIFICATIONIDS:
            specificSetting = notificationSetting.get(settingID)
            if specificSetting.showPopup or specificSetting.showAtAll:
                return False

        return True

    def StoreChanges(self):
        self.StoreInfoPanelChanges()
        self.StoreAuraChanges()
        self.StoreNotificationChanges()

    def OnOpportunitiesSettingChanged(self, configName, value):
        settings.user.ui.Set(configName, value)

    def StoreInfoPanelChanges(self):
        if self.hideInfoPanel == self.oldHideInfoPanel:
            return
        self.OnOpportunitiesSettingChanged(AchievementSettingConst.INFOPANEL_DISABLE_CONFIG, self.hideInfoPanel)
        sm.GetService('infoPanel').Reload()

    def StoreAuraChanges(self):
        if self.disableAura == self.oldDisableAura:
            return
        self.OnOpportunitiesSettingChanged(AchievementSettingConst.AURA_DISABLE_CONFIG, self.disableAura)
        if self.disableAura:
            from achievements.client.auraAchievementWindow import AchievementAuraWindow
            auraWnd = AchievementAuraWindow.GetIfOpen()
            if auraWnd and not auraWnd.destroyed:
                auraWnd.Close()

    def StoreNotificationChanges(self):
        if self.disableNotifications == self.oldDisableNotifications:
            return
        newNotificationValue = not self.disableNotifications
        notificationSetting = self.handler.LoadSettings()
        for settingID in NOTIFICATIONIDS:
            specificSetting = notificationSetting.get(settingID)
            specificSetting.showPopup = newNotificationValue
            specificSetting.showAtAll = newNotificationValue

        self.handler.SaveSettings(notificationSetting)
        from notifications.client.controls.notificationSettingsWindow import NotificationSettingsWindow
        notificationWnd = NotificationSettingsWindow.GetIfOpen()
        if notificationWnd and not notificationWnd.destroyed:
            notificationWnd.ReloadSettings()
            notificationWnd.Open()


class OpportunitiesSettingsMenu(Container):
    default_height = 18
    default_width = 18

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.settingsObject = None
        self.settingMenu = UtilMenu(parent=self, align=uiconst.BOTTOMLEFT, GetUtilMenu=self.GetOpportunitySettings, texturePath='res:/UI/Texture/SettingsCogwheel.png', iconSize=18, pos=(0, 0, 18, 18))
        self.settingMenu.OnMenuClosed = self.OnMenuClosed

    def GetOpportunitySettings(self, menuParent):
        if self.settingsObject is None:
            self.settingsObject = OpportunitySettings()
        return self.settingsObject.GetOpportunitySettings(menuParent)

    def OnMenuClosed(self, *args):
        UtilMenu.OnMenuClosed(self.settingMenu, *args)
        uthread.new(self.StoreChanges_thread)

    def StoreChanges_thread(self):
        if self.settingsObject:
            self.settingsObject.StoreChanges()
            self.settingsObject = None
