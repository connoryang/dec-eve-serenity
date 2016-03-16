#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievementController.py


class AchievementConstants:
    EVENT_TYPE_MINING = 'mining'
    EVENT_TYPE_JUMP = 'jump'
    EVENT_TYPE_KILL = 'kill'
    EVENT_TYPE_TRACKING_CAMERA = 'TrackingEnabled'


class AchievementCondition(object):

    def __init__(self):
        pass

    def IsFullfilled(self, statDict):
        pass


class AchievementSimpleCondition(AchievementCondition):

    def __init__(self, statName, targetValue):
        self.statName = statName
        self.targetValue = targetValue

    def IsFullfilled(self, statsDict):
        fullfilled = False
        if self.statName in statsDict:
            value = int(statsDict[self.statName])
            fullfilled = value >= self.targetValue
        return fullfilled

    def __str__(self):
        return self.statName + ' Needs to be value: ' + str(self.targetValue)


class AchievementTracker(object):

    def __init__(self, notifyCallback):
        self.value = 0
        self.triggerValue = 10
        self.notifyCallback = notifyCallback

    def LogEvent(self, value):
        self.value += value
        self.checkAndNotify()

    def checkAndNotify(self):
        if self.HasFullfilledCondition():
            self.Notify()

    def Notify(self):
        self.notifyCallback('success', self)

    def HasFullfilledCondition(self):
        return self.value >= self.triggerValue


class AchievementConditionData(object):

    def __init__(self, eventName, eventType, value):
        self.eventName = eventName
        self.eventType = eventType
        self.value = value


class ExampleConditionProducer(object):

    def __init__(self):
        self.datas = {}

    def GetExampleConditionData(self):
        list = []
        list.append(AchievementConditionData('oreMined', 'ore', 1))


def GetAchievementGroup(groupID, groups):
    for each in groups:
        if each.groupID == groupID:
            return each


def GetGroupForAchievement(achievementID, groups):
    for eachGroup in groups:
        if achievementID in eachGroup.achievementTaskIDs:
            return eachGroup
