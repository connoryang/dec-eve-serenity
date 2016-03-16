#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\client\development\skillHistoryProvider.py
from notifications.client.development.skillHistoryRow import SkillHistoryRow
from notifications.common.notification import Notification
import localization
EVENT_TYPE_TO_ACTION = {const.skillEventClonePenalty: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillClonePenalty'),
 const.skillEventTrainingStarted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingStarted'),
 const.skillEventTrainingComplete: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
 const.skillEventTrainingCancelled: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingCanceled'),
 const.skillEventGMGive: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/GMGiveSkill'),
 const.skillEventQueueTrainingCompleted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
 const.skillEventFreeSkillPointsUsed: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPointsApplied'),
 const.skillEventSkillExtracted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillLevelExtracted')}

class SkillHistoryProvider(object):

    def __init__(self, scatterDebug = False, onlyShowAfterDate = None):
        self.skillSvc = sm.GetService('skills')
        self.scatterDebug = scatterDebug
        self.onlyShowAfterDate = onlyShowAfterDate
        self.skillSvc.GetSkillHandler().CheckAndSendNotifications()

    def provide(self):
        notificationList = []
        result = []
        skillRowSet = self.skillSvc.GetSkillHistory(10)
        for row in skillRowSet:
            skill = self.skillSvc.GetSkill(row.skillTypeID)
            if skill is None:
                continue
            objectRow = SkillHistoryRow(row, skill.skillRank, cfg, EVENT_TYPE_TO_ACTION)
            if self.onlyShowAfterDate and objectRow.logDate <= self.onlyShowAfterDate:
                continue
            skillnameAndLevel = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=objectRow.skillTypeID, amount=objectRow.level)
            result.append(objectRow)
            notification = Notification.MakeSkillNotification(header='%s - %s' % (objectRow.actionString, skillnameAndLevel), text='', created=objectRow.logDate, callBack=None, callbackargs=[objectRow.skillTypeID])
            notificationList.append(notification)
            if self.scatterDebug:
                sm.ScatterEvent('OnNewNotificationReceived', notification)

        return notificationList
