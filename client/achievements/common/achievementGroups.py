#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementGroups.py
from achievements.common.achievementConst import AchievementConsts
from achievements.common.achievementGroup import AchievementGroup
from opportunityTaskMap import OpportunityConst
from opportunityTaskMap import GROUP_TO_TASK_IDS
from achievements.common.achievementGroupStore import AchievementGroupStore
group100 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/look', descriptionLabelPath='Achievements/GroupDescriptionText/look', notificationPath='Achievements/GroupNotificationText/look', groupID=OpportunityConst.LOOK, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.LOOK], groupConnections=[OpportunityConst.FLY], treePosition=(1, 1))
group101 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fly', descriptionLabelPath='Achievements/GroupDescriptionText/fly', notificationPath='Achievements/GroupNotificationText/fly', groupID=OpportunityConst.FLY, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.FLY], groupConnections=[102], treePosition=(1, 2))
group102 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/kill', descriptionLabelPath='Achievements/GroupDescriptionText/kill', notificationPath='Achievements/GroupNotificationText/kill', groupID=OpportunityConst.KILL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.KILL], groupConnections=[OpportunityConst.SKILL], treePosition=(1, 3))
group103 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/skill', descriptionLabelPath='Achievements/GroupDescriptionText/skill', notificationPath='Achievements/GroupNotificationText/skill', groupID=OpportunityConst.SKILL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SKILL], groupConnections=[OpportunityConst.WARP], treePosition=(2, 3))
group104 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/warp', descriptionLabelPath='Achievements/GroupDescriptionText/warp', notificationPath='Achievements/GroupNotificationText/warp', groupID=OpportunityConst.WARP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.WARP], groupConnections=[OpportunityConst.STATION], treePosition=(2, 2))
group105 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/station', descriptionLabelPath='Achievements/GroupDescriptionText/station', notificationPath='Achievements/GroupNotificationText/station', groupID=OpportunityConst.STATION, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.STATION], groupConnections=[OpportunityConst.MINE], treePosition=(2, 1))
group106 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/mine', descriptionLabelPath='Achievements/GroupDescriptionText/mine', notificationPath='Achievements/GroupNotificationText/mine', groupID=OpportunityConst.MINE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.MINE], groupConnections=[OpportunityConst.MARKET], treePosition=(3, 1))
group107 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/market', descriptionLabelPath='Achievements/GroupDescriptionText/market', notificationPath='Achievements/GroupNotificationText/market', groupID=OpportunityConst.MARKET, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.MARKET], groupConnections=[OpportunityConst.FITTING], treePosition=(3, 2))
group108 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/fitting', descriptionLabelPath='Achievements/GroupDescriptionText/fitting', notificationPath='Achievements/GroupNotificationText/fitting', groupID=OpportunityConst.FITTING, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.FITTING], groupConnections=[OpportunityConst.SOCIAL], treePosition=(3, 3))
group109 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/social', descriptionLabelPath='Achievements/GroupDescriptionText/social', notificationPath='Achievements/GroupNotificationText/social', groupID=OpportunityConst.SOCIAL, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SOCIAL], groupConnections=[OpportunityConst.STARGATE], treePosition=(4, 3))
group110 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/stargate', descriptionLabelPath='Achievements/GroupDescriptionText/stargate', notificationPath='Achievements/GroupNotificationText/stargate', groupID=OpportunityConst.STARGATE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.STARGATE], groupConnections=[OpportunityConst.ROUTE], treePosition=(4, 2))
group111 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/route', descriptionLabelPath='Achievements/GroupDescriptionText/route', notificationPath='Achievements/GroupNotificationText/route', groupID=OpportunityConst.ROUTE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.ROUTE], groupConnections=[OpportunityConst.INDUSTRY], treePosition=(4, 1))
group112 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/industry', descriptionLabelPath='Achievements/GroupDescriptionText/industry', notificationPath='Achievements/GroupNotificationText/industry', groupID=OpportunityConst.INDUSTRY, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.INDUSTRY], groupConnections=[OpportunityConst.EXPLORATION], treePosition=(5, 1))
group113 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/exploration', descriptionLabelPath='Achievements/GroupDescriptionText/exploration', notificationPath='Achievements/GroupNotificationText/exploration', groupID=OpportunityConst.EXPLORATION, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.EXPLORATION], groupConnections=[OpportunityConst.AGENTS], treePosition=(5, 2))
group114 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/agents', descriptionLabelPath='Achievements/GroupDescriptionText/agents', notificationPath='Achievements/GroupNotificationText/agents', groupID=OpportunityConst.AGENTS, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.AGENTS], groupConnections=[OpportunityConst.DEATH], treePosition=(5, 3))
group115 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/death', descriptionLabelPath='Achievements/GroupDescriptionText/death', notificationPath='Achievements/GroupNotificationText/death', groupID=OpportunityConst.DEATH, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.DEATH], groupConnections=[OpportunityConst.CORP], treePosition=(6, 3), triggeredBy=AchievementConsts.LOSE_SHIP, suggestedGroup=False)
group116 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/corp', descriptionLabelPath='Achievements/GroupDescriptionText/corp', notificationPath='Achievements/GroupNotificationText/corp', groupID=OpportunityConst.CORP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.CORP], groupConnections=[OpportunityConst.WORMHOLE], treePosition=(6, 2), suggestedGroup=False)
group117 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/wormhole', descriptionLabelPath='Achievements/GroupDescriptionText/wormhole', notificationPath='Achievements/GroupNotificationText/wormhole', groupID=OpportunityConst.WORMHOLE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.WORMHOLE], groupConnections=[OpportunityConst.SALVAGE], treePosition=(6, 1), triggeredBy=AchievementConsts.ENTER_WORMHOLE, suggestedGroup=False)
group118 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/salvage', descriptionLabelPath='Achievements/GroupDescriptionText/salvage', notificationPath='Achievements/GroupNotificationText/salvage', groupID=OpportunityConst.SALVAGE, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.SALVAGE], groupConnections=[OpportunityConst.PODDED], treePosition=(7, 1), suggestedGroup=False)
group119 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/podded', descriptionLabelPath='Achievements/GroupDescriptionText/podded', notificationPath='Achievements/GroupNotificationText/podded', groupID=OpportunityConst.PODDED, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.PODDED], groupConnections=[], treePosition=(7, 2), triggeredBy=AchievementConsts.LOSE_POD, suggestedGroup=False)
group120 = AchievementGroup(nameLabelPath='Achievements/GroupNameText/agents', descriptionLabelPath='Achievements/GroupDescriptionText/career', notificationPath='Achievements/GroupNotificationText/agents', groupID=OpportunityConst.AGENTSEXP, achievementTaskIDs=GROUP_TO_TASK_IDS[OpportunityConst.AGENTSEXP], groupConnections=[OpportunityConst.DEATH], treePosition=(8, 7))
group119.SetTreePosition((13, 10))
group118.SetTreePosition((10, 9))
group117.SetTreePosition((15, 7))
group116.SetTreePosition((13, 8))
group115.SetTreePosition((14, 10))
group114.SetTreePosition((9, 8))
group113.SetTreePosition((16, 7))
group112.SetTreePosition((16, 5))
group111.SetTreePosition((13, 4))
group110.SetTreePosition((12, 4))
group109.SetTreePosition((12, 8))
group108.SetTreePosition((7, 9))
group107.SetTreePosition((6, 10))
group106.SetTreePosition((16, 4))
group105.SetTreePosition((6, 9))
group104.SetTreePosition((9, 5))
group103.SetTreePosition((12, 6))
group102.SetTreePosition((9, 7))
group101.SetTreePosition((10, 5))
group100.SetTreePosition((9, 4))
group120.SetTreePosition((10, 8))
_achievementGroups3 = [group100,
 group101,
 group102,
 group103,
 group104,
 group105,
 group106,
 group107,
 group108,
 group109,
 group110,
 group111,
 group112,
 group113,
 group114,
 group115,
 group116,
 group117,
 group118,
 group119]
mainGroupsStore = AchievementGroupStore(_achievementGroups3)

def GetAchievementGroups():
    return mainGroupsStore.GetAchievementGroups()


def GetTaskIds():
    return mainGroupsStore.GetTaskIds()


def GetFirstIncompleteAchievementGroup():
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    return mainGroupsStore.GetFirstIncompleteAchievementGroup(alreadyActivated)


def GroupTriggeredByTask(task):
    alreadyActivated = settings.char.ui.Get('opportunities_aura_activated', [])
    for each in GetAchievementGroups():
        if each.triggeredBy == task and each.groupID not in alreadyActivated and not each.IsCompleted():
            return each


def GetAchievementGroup(groupID):
    return mainGroupsStore.GetAchievementGroup(groupID=groupID)


def GetGroupForAchievement(achievementID):
    return mainGroupsStore.GetGroupForAchievement(achievementID)


def GetActiveAchievementGroup():
    activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
    return GetAchievementGroup(activeGroupID)
