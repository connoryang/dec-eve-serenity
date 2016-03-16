#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\statsTracker.py
from collections import defaultdict
import gametime

class StatsTracker(object):

    def __init__(self, achievementGroups = None):
        self.statistics = defaultdict(int)
        self.extraInfo = {}
        self.achievedDict = {}
        self.ResetUnloggedStats()
        self.ResetUnloggedAchievements()
        self.achievementGroups = achievementGroups

    def GetStatValue(self, key):
        return self.statistics[key]

    def ThrowErrorIfBelowZero(self, count):
        if count < 0:
            raise BelowZeroCountException()

    def CheckDidJustUnlockGroup(self, taskID):
        pass

    def LogStatistic(self, key, count = 1, addToUnlogged = True):
        self.ThrowErrorIfBelowZero(count)
        if count < 1:
            return
        self.statistics[key] += count
        if addToUnlogged:
            self.unloggedStats[key] += count

    def GetStatistics(self):
        return self.statistics.copy()

    def GetCurrentAchievements(self):
        return self.achievedDict.copy()

    def AddAchievement(self, achievementID, addToUnlogged = True, dateAchieved = None):
        if achievementID in self.achievedDict:
            return
        if dateAchieved:
            timestamp = dateAchieved
        else:
            timestamp = gametime.GetWallclockTimeNow()
        self.achievedDict[achievementID] = timestamp
        if addToUnlogged:
            self.unloggedAchievements[achievementID] = timestamp

    def GetUnloggedStats(self):
        return self.unloggedStats.copy()

    def ResetUnloggedStats(self):
        self.unloggedStats = defaultdict(int)

    def GetUnloggedAchievements(self):
        return self.unloggedAchievements.copy()

    def ResetUnloggedAchievements(self):
        self.unloggedAchievements = {}

    def ResetStatistics(self):
        self.statistics.clear()
        self.ResetUnloggedStats()

    def ResetAchieved(self):
        self.achievedDict.clear()
        self.ResetUnloggedAchievements()

    def RemoveAchieved(self, achievementID):
        if achievementID in self.achievedDict:
            self.achievedDict.pop(achievementID)

    def RemoveEvent(self, eventName):
        self.statistics.pop(eventName, None)

    def IsSomethingUnlogged(self):
        return bool(self.GetUnloggedAchievements() or self.GetUnloggedStats())


class BelowZeroCountException(Exception):
    pass
