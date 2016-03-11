#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\achievementSvc.py
from achievements.client.eventHandler import EventHandler
from achievements.common.achievementConst import AchievementSettingConst
from achievements.common.util import UpdateAndGetNewAchievements, GetClientAchievements, GetAchievementsByEventsDict
from achievements.common.achievementController import StatsTracker
from achievements.common.achievementGroups import GetGroupForAchievement, GetTaskIds, GroupTriggeredByTask, GetActiveAchievementGroup
from achievements.common.achievementLoader import AchievementLoader
from achievements.common.achievementGroups import GetAchievementGroup
import service
import blue
from carbon.common.script.util.timerstuff import AutoTimer
import eve.common.script.util.notificationconst as notificationConst
from notifications.common.formatters.achievementTask import AchievementTaskFormatter
from notifications.common.formatters.opportunity import AchievementOpportunityFormatter
import threadutils
import eve.common.lib.infoEventConst as infoEventConst
from achievements.client.achievementSettingUtil import OpportunitySettingUtil

class AchievementTrackerClientService(service.Service):
    __guid__ = 'svc.achievementSvc'
    service = 'svc.achievementSvc'
    __startupdependencies__ = ['machoNet']
    __dependencies__ = ['machoNet']
    __notifyevents__ = ['OnServerAchievementUnlocked',
     'OnAchievementsReset',
     'OnSessionChanged',
     'ProcessShutdown']
    _debugStatsForCharacter = None
    remoteService = None
    hasAllData = False
    achievementsEnabled = False

    def Run(self, memStream = None, remoteService = None, scatterService = sm):
        self.scatterService = scatterService
        self.eventHandler = EventHandler(self)
        self.allAchievements = self.LoadAchievements(getDisabled=True)
        self.clientAchievements = GetClientAchievements(self.allAchievements)
        self.achievementsByEventsDict = GetAchievementsByEventsDict(self.clientAchievements)
        self.clientStatsTracker = StatsTracker()
        self.completedDict = {}
        self.scatterService.ScatterEvent('OnAchievementsDataInitialized')

    def UpdateEnabledStatus(self):
        self.achievementsEnabled = sm.GetService('experimentClientSvc').OpportunitiesEnabled()

    def IsEnabled(self):
        return self.achievementsEnabled

    def GetDebugStatsFromCharacter(self, force = False):
        if self._debugStatsForCharacter is None or force is True:
            self._debugStatsForCharacter = self.remoteService.GetDebugStatsFromCharacter(session.charid)
        return self._debugStatsForCharacter

    def HasData(self):
        return self.hasAllData

    def GetFullAchievementList(self):
        return self.allAchievements.values()

    def LogTaskCompletion(self, taskCompletedID):
        activeAchievementID = self.GetActiveAchievementGroupID()
        if activeAchievementID is None:
            activeAchievementID = -1
        charID = session.charid
        userID = session.userid
        auraSuppressed = OpportunitySettingUtil.GetIsAuraSuggestionsSuppressed()
        infoPanelSuppressed = OpportunitySettingUtil.GetIsInfoPanelSuppressed()
        notificationSuppressed = OpportunitySettingUtil.GetIsNotificationSettingSuppressed()
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=infoEventConst.infoEventTaskCompleted, itemID=charID, itemID2=userID, int_1=int(taskCompletedID), int_2=int(activeAchievementID), int_3=int(self.IsAchievementInGroup(taskCompletedID, activeAchievementID)), float_1=float(auraSuppressed), float_2=float(infoPanelSuppressed), float_3=float(notificationSuppressed))

    def OnAchievementsReset(self):
        for eachAchievement in self.allAchievements.itervalues():
            eachAchievement.completed = False

        self.FetchMyAchievementStatus()
        self.scatterService.ScatterEvent('OnAchievementsDataInitialized')
        self.AuraIntroduction()
        uicore.layer.inflight.ResetAchievementVariables()

    def ResetAllForCharacter(self):
        from achievements.client.auraAchievementWindow import AchievementAuraWindow
        self.remoteService.ResetAllForChar()
        AchievementAuraWindow.CloseIfOpen()
        settings.char.ui.Set('opportunities_aura_introduced', False)
        settings.char.ui.Set('opportunities_aura_activated', [])
        self.SetActiveAchievementGroupID(None)

    def SetActiveAchievementGroupID(self, groupID, emphasize = False):
        if groupID != self.GetActiveAchievementGroupID():
            settings.char.ui.Set('opportunities_active_group', groupID)
            sm.ScatterEvent('OnAchievementActiveGroupChanged', groupID, emphasize)

    def GetActiveAchievementGroupID(self):
        return settings.char.ui.Get('opportunities_active_group', None)

    def GetAchievementTask(self, achievementTaskID):
        return self.allAchievements.get(achievementTaskID, None)

    def OnServerAchievementUnlocked(self, achievementsInfo):
        if sm.GetService('experimentClientSvc').OpportunitiesEnabled():
            achievementDict = achievementsInfo['achievementDict']
            self.HandleAchievementsUnlocked(achievementDict)

    def GetAuraWnd(self):
        from achievements.client.auraAchievementWindow import AchievementAuraWindow
        auraWindow = AchievementAuraWindow.Open()
        return auraWindow

    def HandleAchievementsUnlocked(self, achievementDict, taskIdsForMe = None):
        self.MarkAchievementAsCompleted(achievementDict)
        if not self.IsEnabled():
            return
        taskIdsForMyGroup = taskIdsForMe
        if taskIdsForMyGroup is None:
            taskIdsForMyGroup = GetTaskIds()
        for achievementID in achievementDict:
            if achievementID not in self.allAchievements:
                continue
            if achievementID not in taskIdsForMyGroup:
                continue
            achievement = self.allAchievements[achievementID]
            self.SendAchievementNotification(achievementID)
            self.SendOpportunityNotification(achievementID)
            activeGroupID = self.GetActiveAchievementGroupID()
            if activeGroupID and self.IsAchievementInGroup(achievementID, activeGroupID):
                activeGroupCompleted = self.IsCurrentGroupCompleted()
            else:
                activeGroupCompleted = False
            self.TriggerAura(achievementID, activeGroupCompleted)
            sm.ScatterEvent('OnAchievementChanged', achievement, activeGroupCompleted=activeGroupCompleted)

    def TriggerAura(self, achievementID, activeGroupCompleted):
        if settings.user.ui.Get(AchievementSettingConst.AURA_DISABLE_CONFIG, False):
            return
        forcedGroup = GroupTriggeredByTask(achievementID)
        if forcedGroup and GetActiveAchievementGroup() != forcedGroup:
            auraWindow = self.GetAuraWnd()
            auraWindow.TriggerForcedGroup(forcedGroup)
        elif activeGroupCompleted:
            auraWindow = self.GetAuraWnd()
            auraWindow.Step_ActiveCompleted()

    def MarkAchievementAsCompleted(self, achievementDict):
        for achievementID, timestamp in achievementDict.iteritems():
            if achievementID not in self.allAchievements:
                continue
            self.completedDict[achievementID] = timestamp
            self.allAchievements[achievementID].completed = True
            self.LogTaskCompletion(achievementID)

    def SendAchievementNotification(self, achievementID):
        notificationData = AchievementTaskFormatter.MakeData(achievementID)
        self.SendNotification(notificationData, notificationConst.notificationTypeAchievementTaskFinished)

    def SendOpportunityNotification(self, achievementID):
        group = GetGroupForAchievement(achievementID)
        if not group:
            return
        if group.IsCompleted():
            notificationData = AchievementOpportunityFormatter.MakeData(group.groupID)
            self.SendNotification(notificationData, notificationConst.notificationTypeOpportunityFinished)

    def SendNotification(self, notificationData, notificationType):
        sm.ScatterEvent('OnNotificationReceived', 123, notificationType, session.charid, blue.os.GetWallclockTime(), data=notificationData)

    def FetchMyAchievementStatus(self):
        achievementAndEventInfo = self.remoteService.GetCompletedAchievementsAndClientEventCount()
        self.completedDict = achievementAndEventInfo['completedDict']
        self.PopulateEventHandler(achievementAndEventInfo['eventDict'])
        self.UpdateAchievementList()
        self.hasAllData = True

    def PopulateEventHandler(self, eventCountDict):
        for eventName, eventCount in eventCountDict.iteritems():
            if eventCount < 1:
                self.clientStatsTracker.statistics[eventName] = 0
            else:
                self.clientStatsTracker.LogStatistic(eventName, eventCount, addToUnlogged=False)

    def UpdateAchievementList(self):
        for achievementID in self.completedDict:
            if achievementID in self.allAchievements:
                self.allAchievements[achievementID].completed = True

    def LoadAchievements(self, getDisabled = False):
        return AchievementLoader().GetAchievements(getDisabled=getDisabled)

    def IsAchievementCompleted(self, achievementID):
        return achievementID in self.completedDict

    def IsAchievementInGroup(self, achievementID, groupID):
        achievementGroup = GetAchievementGroup(groupID)
        if achievementGroup:
            return achievementGroup.HasAchievement(achievementID)
        else:
            return False

    def IsCurrentGroupCompleted(self):
        currentGroupID = self.GetActiveAchievementGroupID()
        if not currentGroupID:
            return False
        achievementGroup = GetAchievementGroup(currentGroupID)
        return achievementGroup.IsCompleted()

    def OnSessionChanged(self, isRemote, session, change):
        if 'charid' in change and not self.HasData():
            if self.remoteService is None:
                self.remoteService = sm.RemoteSvc('achievementTrackerMgr')
            self.FetchMyAchievementStatus()
            self.UpdateEnabledStatus()
        if 'stationid' in change and change['stationid'][1] or 'solarsystemid' in change and change['solarsystemid'][1]:
            self.AuraIntroduction()

    def ProcessShutdown(self):
        try:
            self.UpdateClientAchievementsAndCountersOnServer()
        except Exception as e:
            self.LogError('Failed at storing client achievement events, e = ', e)

    def AuraIntroduction(self):
        if not self.IsEnabled():
            return
        self.openAuraThread = AutoTimer(3000, self._AuraIntroduction_Delayed)

    def _AuraIntroduction_Delayed(self):
        self.openAuraThread = None
        auraDisabled = settings.user.ui.Get(AchievementSettingConst.AURA_DISABLE_CONFIG, False)
        if not auraDisabled and not settings.char.ui.Get('opportunities_aura_introduced', False):
            from achievements.client.auraAchievementWindow import AchievementAuraWindow
            AchievementAuraWindow.Open()

    def LogClientEvent(self, eventName, value = 1):
        achievementsWithEvent = self.achievementsByEventsDict.get(eventName, set())
        achievementsLeft = achievementsWithEvent - set(self.completedDict.keys())
        if not achievementsLeft:
            return
        self.clientStatsTracker.LogStatistic(eventName, value, addToUnlogged=False)
        achievementsWereCompleted = self.CheckAchievementStatus()
        if not achievementsWereCompleted:
            self.UpdateClientAchievementsAndCountersOnServer_throttled(self)

    def CheckAchievementStatus(self):
        newAchievementSet = self.GetNewAchievementsForCharacter()
        if newAchievementSet:
            self.HandleAchievementsUnlocked(newAchievementSet)
            self.UpdateClientAchievementsAndCountersOnServer()
            return True
        return False

    @threadutils.throttled(180)
    def UpdateClientAchievementsAndCountersOnServer_throttled(self):
        self.UpdateClientAchievementsAndCountersOnServer()

    def UpdateClientAchievementsAndCountersOnServer(self):
        stats = self.clientStatsTracker.GetStatistics()
        self.remoteService.UpdateClientAchievmentsAndCounters(self.completedDict, dict(stats))

    def GetNewAchievementsForCharacter(self):
        return UpdateAndGetNewAchievements(self.clientAchievements, self.completedDict, self.clientStatsTracker)
