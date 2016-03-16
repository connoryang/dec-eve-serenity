#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\common\achievement.py


class Achievement(object):

    def __init__(self, achievementID, name, description, conditions = None, notificationText = None, isClientAchievement = False, isEnabled = True):
        self.achievementID = achievementID
        self.name = name
        self.description = description
        self.notificationText = notificationText
        self.isClientAchievement = isClientAchievement
        self.isEnabled = isEnabled
        if conditions is None:
            self.conditions = []
        else:
            self.conditions = conditions

    def AddCondition(self, condition):
        self.conditions.append(condition)

    def GetConditions(self):
        return self.conditions

    def IsAchievementFulfilled(self, playerStats):
        conditions = self.GetConditions()
        for condition in conditions:
            if not condition.IsFullfilled(playerStats):
                return False

        return True
