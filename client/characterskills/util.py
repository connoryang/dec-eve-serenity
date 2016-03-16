#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\util.py
import math
import characterskills.const
DIVCONSTANT = math.log(2) * 2.5

def GetLevelProgress(skillPoints, skillTimeConstant):
    level = GetSkillLevelRaw(skillPoints, skillTimeConstant)
    if level >= characterskills.const.maxSkillLevel:
        return 0.0
    baseLevelPoints = GetSPForLevelRaw(skillTimeConstant, level)
    nextLevelPoints = GetSPForLevelRaw(skillTimeConstant, level + 1)
    return (skillPoints - baseLevelPoints) / float(nextLevelPoints - baseLevelPoints)


def GetSkillLevelRaw(skillPoints, skillTimeConstant):
    baseSkillLevelConstant = float(skillTimeConstant) * characterskills.const.skillPointMultiplier
    if baseSkillLevelConstant > skillPoints or baseSkillLevelConstant == 0:
        return 0
    level = 1 + int(math.log(skillPoints / baseSkillLevelConstant) / DIVCONSTANT)
    return min(level, characterskills.const.maxSkillLevel)


def GetSkillPointsPerMinute(primaryAttributeValue, secondaryAttributeValue):
    return primaryAttributeValue + secondaryAttributeValue / 2.0


def GetSPForAllLevels(skillTimeConstant):
    levelList = []
    for i in range(characterskills.const.maxSkillLevel + 1):
        levelList.append(GetSPForLevelRaw(skillTimeConstant, i))

    return levelList


def GetSPForLevelRaw(skillTimeConstant, level):
    if level <= 0:
        return 0
    if level > characterskills.const.maxSkillLevel:
        level = characterskills.const.maxSkillLevel
    preMultipliedSkillPoints = float(skillTimeConstant) * characterskills.const.skillPointMultiplier
    return int(math.ceil(preMultipliedSkillPoints * 2 ** (2.5 * (level - 1))))
