#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\development\achievementHistoryProvider.py
from achievements.common.achievementGroups import GetAchievementGroups, GetTaskIds
from achievements.common.achievementLoader import AchievementLoader
import eve.common.script.util.notificationconst as notificationConst
from notifications.client.development.baseHistoryProvider import BaseHistoryProvider
from notifications.common.formatters.achievementTask import AchievementTaskFormatter
from notifications.common.formatters.opportunity import AchievementOpportunityFormatter
from notifications.common.notification import Notification

class AchievementHistoryProvider(BaseHistoryProvider):

    def provide(self):
        notificationList = []
        completedDict = sm.GetService('achievementSvc').completedDict
        allAchievements = AchievementLoader().GetAchievements(getDisabled=False)
        taskIdsForGroup = GetTaskIds()
        for taskID, timestamp in completedDict.iteritems():
            if self.IsNotificationTooOld(timestamp):
                continue
            if taskID not in allAchievements:
                continue
            if taskID not in taskIdsForGroup:
                continue
            notificationData = AchievementTaskFormatter.MakeData(taskID)
            notification = Notification.MakeAchievementNotification(data=notificationData, created=timestamp)
            notificationList.append(notification)
            if self.scatterDebug:
                sm.ScatterEvent('OnNewNotificationReceived', notification)

        allGroups = GetAchievementGroups()
        for eachGroup in allGroups:
            if not eachGroup.IsCompleted():
                continue
            lastCompleteTimestamp = max((completedDict.get(taskID, None) for taskID in eachGroup.achievementTaskIDs))
            if self.IsNotificationTooOld(lastCompleteTimestamp):
                continue
            notificationData = AchievementOpportunityFormatter.MakeData(eachGroup.groupID)
            notification = Notification.MakeAchievementNotification(data=notificationData, created=lastCompleteTimestamp + 1, notificationType=notificationConst.notificationTypeOpportunityFinished)
            notificationList.append(notification)

        return notificationList
