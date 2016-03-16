#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\charactercreator\client\logging\stepLogger.py
from collections import defaultdict

class TimeStepInformation:

    def __init__(self):
        self.timePerStep = defaultdict(long)
        self.totalTime = 0L
        self.entryCountPerStep = defaultdict(int)
        self.nextTriesPerStep = defaultdict(int)


class FinalStepResult(object):

    def __init__(self):
        self.ancestryChoiceChanged = -1
        self.schoolChoiceChanged = -1
        self.nameValidatationTries = -1
        self.didFinish = False
        self.finalizeTryCount = 0


class FinalStepLogger(object):

    def __init__(self):
        self.triedNames = []
        self.startingAncestry = -1
        self.startingSchool = -1
        self.chosenAncestry = -1
        self.chosenSchool = -1
        self.ancestryChanged = -1
        self.schoolChanged = -1
        self.didFinish = None
        self.storedSteps = []
        self.finalizeCount = 0

    def Start(self):
        pass

    def SetAncestry(self, ancestry):
        if ancestry != self.chosenAncestry:
            self.ancestryChanged += 1
            self.chosenAncestry = ancestry

    def SetSchool(self, school):
        if school != self.chosenSchool:
            self.schoolChanged += 1
            self.chosenSchool = school

    def AddTriedName(self, name):
        self.triedNames.append(name)

    def End(self):
        self.didFinish = True

    def Cancel(self):
        self.didFinish = False

    def Finalize(self):
        self.finalizeCount += 1

    def GetFinalStepResult(self):
        result = FinalStepResult()
        result.nameValidatationTries = len(self.triedNames)
        result.didFinish = self.didFinish
        result.ancestryChoiceChanged = self.ancestryChanged
        result.schoolChoiceChanged = self.schoolChanged
        result.finalizeTryCount = self.finalizeCount
        return result


class StepLogger(object):

    def __init__(self, timeProvider):
        self.startTime = None
        self.stopTime = None
        self.nowTimeProvider = timeProvider
        self.stepOrder = []
        self.timeStartOrder = []
        self.timeEndOrder = []
        self.currentStepID = None
        self.stepTimeSpent = defaultdict(long)
        self.stepEntryCount = defaultdict(int)
        self.nextTryCount = defaultdict(int)

    def IncrementNextTryCount(self):
        if self.currentStepID is not None:
            self.nextTryCount[self.currentStepID] += 1

    def Start(self):
        self.startTime = self._getTime()

    def SetStep(self, stepID):
        self._endCurrentStep()
        self.timeStartOrder.append(self._getTime())
        self.currentStepID = stepID
        self.stepEntryCount[stepID] += 1
        self.stepOrder.append(stepID)

    def _endCurrentStep(self):
        if self.currentStepID:
            self.timeEndOrder.append(self._getTime())

    def _getTime(self):
        return self.nowTimeProvider()

    def Stop(self):
        self._endCurrentStep()
        self.stopTime = self._getTime()

    def GetStepOrder(self):
        return self.stepOrder

    def GetTimeObject(self):
        finalTimes = defaultdict(long)
        timeObject = TimeStepInformation()
        for index in range(len(self.stepOrder)):
            entry = self.stepOrder[index]
            startTime = self.timeStartOrder[index]
            endTime = self.timeEndOrder[index]
            finalTimes[entry] += endTime - startTime

        timeObject.timePerStep = finalTimes
        timeObject.nextTriesPerStep = self.nextTryCount.copy()
        timeObject.entryCountPerStep = self.stepEntryCount.copy()
        timeObject.totalTime = self.stopTime - self.startTime
        return timeObject


class StepInfo(object):

    def __init__(self, stepID, nextTryCount, totalTime, entryCount):
        self.stepID = stepID
        self.nextTryCount = nextTryCount
        self.totalCount = totalTime
        self.entryCount = entryCount


import eve.common.lib.infoEventConst as infoConst

class StepInfoEventServiceLogger(object):

    def __init__(self, logInfoEventFunction, sessionID, userID):
        self.LogInfoEvent = logInfoEventFunction
        self.sessionID = sessionID
        self.userID = userID

    def LogTimeObject(self, timeObject):
        stepInfos = []
        for stepID, entryCount in timeObject.entryCountPerStep.iteritems():
            nextTryCount = timeObject.nextTriesPerStep[stepID]
            totalTimeSpent = timeObject.timePerStep[stepID]
            stepInfos.append(StepInfo(stepID=stepID, nextTryCount=nextTryCount, totalTime=totalTimeSpent, entryCount=entryCount))

        for stepInfo in stepInfos:
            self.LogInfoEvent(eventTypeID=infoConst.infoEventCharacterCreationStep, itemID=self.sessionID, itemID2=self.userID, int_1=stepInfo.stepID, int_2=stepInfo.entryCount, int_3=stepInfo.nextTryCount, float_1=stepInfo.totalCount / 10000000L)


class FinalStepInfoEventServiceLogger(object):

    def __init__(self, logInfoEventFunction, sessionID, userID):
        self.LogInfoEvent = logInfoEventFunction
        self.sessionID = sessionID
        self.userID = userID

    def TernaryBooleanToFloat(self, value):
        if value is True:
            return 1
        elif value is False:
            return 0
        else:
            return -1

    def LogFinalStepObjects(self, finalStepResult):
        floatDidFinish = self.TernaryBooleanToFloat(finalStepResult.didFinish)
        self.LogInfoEvent(eventTypeID=infoConst.infoEventCharacterFinalStep, itemID=self.sessionID, itemID2=self.userID, int_1=int(finalStepResult.ancestryChoiceChanged), int_2=int(finalStepResult.schoolChoiceChanged), int_3=int(finalStepResult.nameValidatationTries), float_1=float(finalStepResult.finalizeTryCount), float_2=floatDidFinish)
