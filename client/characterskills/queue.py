#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\queue.py
import carbon.common.lib.const as const
from characterskills.util import GetSPForLevelRaw
import gametime
CHINA_SKILLQUEUE_TIME = const.DAY
TRIAL_SKILLQUEUE_TIME = const.DAY
NORMAL_SKILLQUEUE_TIME = 10 * const.YEAR365
SKILLQUEUE_MAX_NUM_SKILLS = 50
USER_TYPE_NOT_ENFORCED = -1

def HasShortSkillqueue(userType):
    return IsTrialRestricted(userType) or IsChinaRestricted()


def GetSkillQueueTimeLength(userType):
    if IsChinaRestricted():
        return CHINA_SKILLQUEUE_TIME
    elif IsTrialRestricted(userType):
        return TRIAL_SKILLQUEUE_TIME
    else:
        return NORMAL_SKILLQUEUE_TIME


def IsTrialRestricted(userType):
    return userType == const.userTypeTrial


def IsChinaRestricted():
    return boot.region == 'optic'


def GetQueueEntry(skillTypeID, skillLevel, queuePosition, currentSkill, currentQueue, GetTimeForTraining, KeyVal, activate, trainingStartTime = None):
    trainingEndTime = None
    if trainingStartTime is None and activate:
        if queuePosition == 0 or len(currentQueue) == 0:
            trainingStartTime = gametime.GetWallclockTime()
        else:
            trainingStartTime = currentQueue[queuePosition - 1].trainingEndTime
        trainingTime = GetTimeForTraining(skillTypeID, skillLevel)
        trainingEndTime = long(trainingStartTime) + long(trainingTime)
    if currentSkill.skillLevel == skillLevel - 1:
        trainingStartSP = currentSkill.skillPoints
    else:
        trainingStartSP = GetSPForLevelRaw(currentSkill.skillRank, skillLevel - 1)
    trainingDestinationSP = GetSPForLevelRaw(currentSkill.skillRank, skillLevel)
    return SkillQueueEntry(queuePosition, skillTypeID, skillLevel, trainingStartSP, trainingStartTime, trainingDestinationSP, trainingEndTime, KeyVal)


def SkillQueueEntry(queuePosition, skillTypeID, skillLevel, trainingStartSP, trainingStartTime, trainingDestinationSP, trainingEndTime, KeyVal):
    return KeyVal(queuePosition=queuePosition, trainingStartTime=trainingStartTime, trainingEndTime=trainingEndTime, trainingTypeID=skillTypeID, trainingToLevel=skillLevel, trainingStartSP=trainingStartSP, trainingDestinationSP=trainingDestinationSP)
