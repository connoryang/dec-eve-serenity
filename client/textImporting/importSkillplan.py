#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\textImporting\importSkillplan.py
from textImporting import GetValidNamesAndTypesDict, GetLines, SplitAndStrip
import inventorycommon.const as invconst

class ImportSkillPlan(object):

    def __init__(self):
        self.nameAndTypeIDsDict = GetValidNamesAndTypesDict([invconst.categorySkill])
        self.levelDict = {'i': 1,
         'ii': 2,
         'iii': 3,
         'iv': 4,
         'v': 5}
        self.validLevelStrings = ('1', '2', '3', '4', '5')

    def GetSkillsToAdd(self, text):
        lines = GetLines(text)
        skillsAndLevels = []
        failed = []
        for eachLine in lines:
            parts = SplitAndStrip(eachLine, ' ')
            if not parts:
                continue
            levelString = parts[-1]
            if levelString in self.validLevelStrings:
                level = int(levelString)
            else:
                level = self.levelDict.get(levelString.lower(), None)
            if not level:
                failed.append(eachLine)
                continue
            skillName = ' '.join(parts[:-1]).strip()
            typeID = self.nameAndTypeIDsDict.get(skillName.lower(), None)
            if typeID:
                skillsAndLevels.append((typeID, level))
            else:
                failed.append(eachLine)

        return (skillsAndLevels, failed)


class SkillPlanImportingStatus(object):

    def __init__(self):
        self.failedLevels = []
        self.failedSkillTypeIDs = {}
        self.alreadyTrainedLevels = []
        self.skillLevelsAdded = 0
        self.tooManySkills = False

    def AddToFailed(self, typeID, skillLevel, reason = None):
        infoTuple = (typeID, skillLevel, reason)
        if reason == 'QueueCannotTrainPreviouslyTrainedSkills':
            self.alreadyTrainedLevels.append(infoTuple)
        else:
            self.failedLevels.append(infoTuple)
            if reason == 'QueueTooManySkills':
                self.tooManySkills = True
            if typeID in self.failedSkillTypeIDs:
                lowestLevelWithError = self.failedSkillTypeIDs[typeID][0]
            else:
                lowestLevelWithError = 6
            if skillLevel < lowestLevelWithError:
                self.failedSkillTypeIDs[typeID] = (skillLevel, reason)

    def TooManySkillsAdded(self):
        return self.tooManySkills

    def ReasonForFailingForLowerLevel(self, typeID, skillLevel):
        if typeID not in self.failedSkillTypeIDs:
            return None
        failureInfo = self.failedSkillTypeIDs[typeID]
        if skillLevel > failureInfo[0]:
            return failureInfo[1]

    def IncreaseAddedCount(self):
        self.skillLevelsAdded += 1
