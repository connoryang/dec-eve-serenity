#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementGroup.py


class AchievementGroupData(object):

    def __init__(self, groupID, taskIds):
        pass


class AchievementGroup(object):
    _achievementTasks = None

    def __init__(self, groupID, nameLabelPath, descriptionLabelPath, notificationPath, achievementTaskIDs, groupConnections, treePosition = None, triggeredBy = None, suggestedGroup = True, allAchievementGetter = None, completedAchievementGetter = None, *args, **kwargs):
        self.groupID = groupID
        self.groupName = nameLabelPath
        self.groupDescription = descriptionLabelPath
        self.groupConnections = groupConnections
        self.achievementTaskIDs = achievementTaskIDs
        self.notificationPath = notificationPath
        self.triggeredBy = triggeredBy
        self.suggestedGroup = suggestedGroup
        if treePosition:
            self.SetTreePosition(treePosition)
        else:
            self.treePosition = (1, 1)
        self._getAllAchievementsFunc = allAchievementGetter
        self.GetAllCompletedAchievements = completedAchievementGetter

    def SetTreePosition(self, treePosition):
        self.treePosition = treePosition

    def GetAchievementTaskIDs(self):
        return self.achievementTaskIDs

    def HasAchievement(self, achievementID):
        return achievementID in self.achievementTaskIDs

    def GetAllAchievements(self):
        if self._getAllAchievementsFunc is None:
            self._getAllAchievementsFunc = sm.GetService('achievementSvc').GetAllAchievements
        return self._getAllAchievementsFunc()

    def _GetAchievementTasks(self):
        if self._achievementTasks is None:
            self._achievementTasks = []
            allAchievements = self.GetAllAchievements()
            for achievementTaskID in self.achievementTaskIDs:
                self._achievementTasks.append(allAchievements[achievementTaskID])

        return self._achievementTasks

    def GetAchievementTasks(self):
        return self._GetAchievementTasks()

    def _GetCompletedAchievementTasks(self):
        if self.GetAllCompletedAchievements is None:
            self.GetAllCompletedAchievements = sm.GetService('achievementSvc').GetCompletedTaskIds
        return self.GetAllCompletedAchievements()

    def IsCompleted(self):
        groupTasks = self._GetAchievementTasks()
        totalNum = len(groupTasks)
        numberOfCompleted = self.GetNumberOfCompleted()
        return totalNum == numberOfCompleted

    def GetNumberOfCompleted(self):
        groupTasks = self._GetAchievementTasks()
        completedTasks = self._GetCompletedAchievementTasks()
        completed = len([ x for x in groupTasks if x.achievementID in completedTasks ])
        return completed

    def GetNumberOfTasks(self):
        return len(self.achievementTaskIDs)

    def GetProgressProportion(self):
        total = self.GetNumberOfTasks()
        completed = self.GetNumberOfCompleted()
        return completed / float(total)

    def GetNextIncompleteTask(self, currentAchievementTaskID = None):
        tasks = self._GetAchievementTasks()
        completed = self.GetAllCompletedAchievements()
        foundCurrent = currentAchievementTaskID is None
        for each in tasks:
            if each.achievementID == currentAchievementTaskID:
                foundCurrent = True
                continue
            if foundCurrent and each.achievementID not in completed:
                return each

    def GetFirstCompletedTask(self):
        tasks = self._GetAchievementTasks()
        completed = self.GetAllCompletedAchievements()
        for each in tasks:
            if each.achievementID in completed:
                return each
