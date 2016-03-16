#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementGroupStore.py


class AchievementGroupStore(object):

    def __init__(self, groups):
        self.groups = groups

    def GetTaskIds(self):
        allTaskIds = set()
        for group in self.GetAchievementGroups():
            allTaskIds.update(group.GetAchievementTaskIDs())

        return allTaskIds

    def GetAchievementGroups(self):
        return self.groups

    def GetAchievementGroup(self, groupID):
        for each in self.GetAchievementGroups():
            if each.groupID == groupID:
                return each

    def GetGroupForAchievement(self, achievementID):
        for eachGroup in self.GetAchievementGroups():
            if achievementID in eachGroup.achievementTaskIDs:
                return eachGroup

    def GetFirstIncompleteAchievementGroup(self, alreadyActivated):
        for each in self.GetAchievementGroups():
            if not each.suggestedGroup:
                continue
            if each.groupID not in alreadyActivated and not each.IsCompleted():
                return each

    def GroupTriggeredByTask(self, task, alreadyActivated):
        for each in self.GetAchievementGroups():
            if each.triggeredBy == task and each.groupID not in alreadyActivated and not each.IsCompleted():
                return each
