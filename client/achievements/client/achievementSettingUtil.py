#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\achievementSettingUtil.py
import eve.common.script.util.notificationconst as notificationConst
from achievements.common.achievementConst import AchievementSettingConst
from notifications.client.notificationSettings.notificationSettingHandler import NotificationSettingHandler
NOTIFICATIONIDS = [notificationConst.notificationTypeAchievementTaskFinished, notificationConst.notificationTypeOpportunityFinished]

class OpportunitySettingUtil(object):

    @staticmethod
    def GetIsAuraSuggestionsSuppressed():
        return bool(settings.user.ui.Get(AchievementSettingConst.AURA_DISABLE_CONFIG, False))

    @staticmethod
    def GetIsInfoPanelSuppressed():
        return bool(settings.user.ui.Get(AchievementSettingConst.INFOPANEL_DISABLE_CONFIG, False))

    @staticmethod
    def GetIsNotificationSettingSuppressed():
        handler = NotificationSettingHandler()
        notificationSetting = handler.LoadSettings()
        for settingID in NOTIFICATIONIDS:
            specificSetting = notificationSetting.get(settingID)
            if specificSetting.showPopup or specificSetting.showAtAll:
                return False

        return True
