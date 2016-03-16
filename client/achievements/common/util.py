#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\util.py
from collections import defaultdict
from achievements.common.opportunityTaskMap import BuildIndex
import gametime

def UpdateAndGetNewAchievements(existingAchivements, completedDict, statsTrakcer):
    newAchievementDict = {}
    for key, achievement in existingAchivements.iteritems():
        if achievement.achievementID in completedDict:
            continue
        if achievement.IsAchievementFulfilled(statsTrakcer.GetStatistics()):
            timestamp = gametime.GetWallclockTime()
            statsTrakcer.AddAchievement(achievement.achievementID, dateAchieved=timestamp)
            newAchievementDict[achievement.achievementID] = timestamp

    return newAchievementDict


def GetClientAchievements(allAchievementsDict):
    clientAchievements = {}
    for achievementID, achievementData in allAchievementsDict.iteritems():
        if not achievementData.isClientAchievement:
            continue
        clientAchievements[achievementID] = achievementData

    return clientAchievements


def GetAchievementsByEventsDict(achievementDict):
    eventDict = defaultdict(set)
    for achievementID, achievementData in achievementDict.iteritems():
        for c in achievementData.conditions:
            eventDict[c.statName].add(achievementID)

    return eventDict


def GetUnlockedGroupsFromDefault(achieved, newAchievements):
    from achievements.common.opportunityTaskMap import GROUP_TO_TASK_IDS, TASK_ID_TO_GROUP
    return _GetUnlockedOpportunities(achieved, GROUP_TO_TASK_IDS, newAchievements, TASK_ID_TO_GROUP)


def GetUnlockedGroups(achieved, newAchievements, allOpportunities):
    reverseIndex = BuildIndex(allOpportunities)
    return _GetUnlockedOpportunities(achieved, allOpportunities, newAchievements, reverseIndex)


def _GetUnlockedOpportunities(achieved, allOpportunities, newAchievements, reverseIndex):
    unlockedGroups = {}
    totalAchieved = newAchievements.keys() + achieved.keys()
    for newID, timeStamp in newAchievements.iteritems():
        groupID = reverseIndex.get(newID, None)
        if groupID:
            allTasksForGroup = allOpportunities[groupID]
            achievementCount = 0
            for task in allTasksForGroup:
                if task in totalAchieved:
                    achievementCount += 1

            if achievementCount == len(allTasksForGroup):
                unlockedGroups[groupID] = timeStamp

    return unlockedGroups
