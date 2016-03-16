#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\skillQueueSvc.py
from carbonui.util.various_unsorted import GetAttrs
import service
import blue
import form
import characterskills.util
import sys
from textImporting.importSkillplan import ImportSkillPlan
import uix
import carbonui.const as uiconst
import uiutil
import localization
import evetypes
from collections import defaultdict
from util import KeyVal
from eve.client.script.ui.shared.neocom.skillqueueUI import ShowMultiTrainingMessage
from uthread import Lock, UnLock

class SkillQueueService(service.Service):
    __exportedcalls__ = {'SkillInTraining': []}
    __guid__ = 'svc.skillqueue'
    __servicename__ = 'skillqueue'
    __displayname__ = 'Skill Queue Client Service'
    __dependencies__ = ['godma', 'skills', 'machoNet']
    __notifyevents__ = ['OnSkillQueuePaused', 'OnMultipleCharactersTrainingUpdated', 'OnNewSkillQueueSaved']

    def __init__(self):
        service.Service.__init__(self)
        self.skillQueue = []
        self.cachedSkillQueue = None
        self.skillQueueCache = None
        self.skillplanImporter = None
        self.maxSkillqueueTimeLength = characterskills.util.GetSkillQueueTimeLength(session.userType)

    def Run(self, memStream = None):
        self.skillQueue, freeSkillPoints = self.skills.GetSkillHandler().GetSkillQueueAndFreePoints()
        if freeSkillPoints is not None and freeSkillPoints > 0:
            self.skills.SetFreeSkillPoints(freeSkillPoints)

    def BeginTransaction(self):
        Lock('SkillQueueSvc:xActLock')
        try:
            sendEvent = False
            skillInTraining = self.SkillInTraining()
            if self.cachedSkillQueue is not None:
                sendEvent = True
                self.LogError('%s: New skill queue transaction being opened - skill queue being overwritten!' % session.charid)
            self.skillQueueCache = None
            self.skillQueue, freeSkillPoints = self.skills.GetSkillHandler().GetSkillQueueAndFreePoints()
            if freeSkillPoints > 0:
                self.skills.SetFreeSkillPoints(freeSkillPoints)
            self.cachedSkillQueue = self.GetQueue()
            if not skillInTraining:
                queueWithTimestamps = []
                for idx, trainingSkill in enumerate(self.skillQueue):
                    startTime = None
                    if idx > 0:
                        startTime = self.skillQueue[idx - 1].trainingEndTime
                    currentSkill = self.skills.GetSkill(trainingSkill.trainingTypeID)
                    queueEntry = characterskills.util.GetQueueEntry(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, idx, currentSkill, queueWithTimestamps, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, True)
                    queueWithTimestamps.append(queueEntry)

                self.skillQueue = queueWithTimestamps
            if sendEvent:
                sm.ScatterEvent('OnSkillQueueRefreshed')
        finally:
            UnLock('SkillQueueSvc:xActLock')

    def RollbackTransaction(self):
        Lock('SkillQueueSvc:xActLock')
        try:
            if self.cachedSkillQueue is None:
                self.LogError('%s: Cannot rollback a skill queue transaction - no transaction was opened!' % session.charid)
                return
            self.skillQueue = self.cachedSkillQueue
            self.skillQueueCache = None
            self.cachedSkillQueue = None
        finally:
            UnLock('SkillQueueSvc:xActLock')

    def CommitTransaction(self):
        Lock('SkillQueueSvc:xActLock')
        try:
            if self.cachedSkillQueue is None:
                self.LogError('%s: Cannot commit a skill queue transaction - no transaction was opened!' % session.charid)
                return
            self.PrimeCache(True)
            cachedQueueCache = defaultdict(dict)
            hasChanges = False
            if len(self.skillQueue) != len(self.cachedSkillQueue):
                hasChanges = True
            else:
                for i, skill in enumerate(self.cachedSkillQueue):
                    cachedQueueCache[skill.trainingTypeID][skill.trainingToLevel] = i
                    if self.skillQueue[i].trainingTypeID != skill.trainingTypeID or self.skillQueue[i].trainingToLevel != skill.trainingToLevel:
                        hasChanges = True

            scatterEvent = False
            try:
                skillHandler = self.skills.GetSkillHandler()
                self.TrimQueue(hasChanges)
                queueInfo = {idx:(x.trainingTypeID, x.trainingToLevel) for idx, x in enumerate(self.skillQueue)}
                if hasChanges or len(self.skillQueue) and self.SkillInTraining() is None:
                    scatterEvent = True
                    skillHandler.SaveNewQueue(queueInfo, True)
            except UserError as e:
                if e.msg == 'UserAlreadyHasSkillInTraining':
                    scatterEvent = True
                    ShowMultiTrainingMessage()
                else:
                    raise
            finally:
                self.cachedSkillQueue = None
                if scatterEvent:
                    sm.ScatterEvent('OnSkillQueueRefreshed')

        finally:
            UnLock('SkillQueueSvc:xActLock')

    def CheckCanInsertSkillAtPosition(self, skillTypeID, skillLevel, position, check = 0, performLengthTest = True):
        if position is None or position < 0 or position > len(self.skillQueue):
            raise UserError('QueueInvalidPosition')
        self.PrimeCache()
        mySkill = self.skills.GetSkill(skillTypeID)
        ret = True
        try:
            if mySkill is None:
                raise UserError('QueueSkillNotUploaded')
            if mySkill.skillLevel >= skillLevel:
                raise UserError('QueueCannotTrainPreviouslyTrainedSkills')
            if mySkill.skillLevel >= 5:
                raise UserError('QueueCannotTrainPastMaximumLevel', {'typeName': (const.UE_TYPEID, skillTypeID)})
            if skillTypeID in self.skillQueueCache:
                for lvl, lvlPosition in self.skillQueueCache[skillTypeID].iteritems():
                    if lvl < skillLevel and lvlPosition >= position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')
                    elif lvl > skillLevel and lvlPosition < position:
                        raise UserError('QueueCannotPlaceSkillLevelsOutOfOrder')

            if position > 0 and performLengthTest:
                if self.GetTrainingLengthOfQueue(position) > self.maxSkillqueueTimeLength:
                    raise UserError('QueueTooLong')
        except UserError as ue:
            if check and ue.msg in ('QueueTooLong', 'QueueCannotPlaceSkillLevelsOutOfOrder', 'QueueCannotTrainPreviouslyTrainedSkills', 'QueueSkillNotUploaded'):
                sys.exc_clear()
                ret = False
            else:
                raise

        return ret

    def AddSkillToQueue(self, skillTypeID, skillLevel, position = None):
        if self.FindInQueue(skillTypeID, skillLevel) is not None:
            raise UserError('QueueSkillAlreadyPresent')
        skillQueueLength = len(self.skillQueue)
        if skillQueueLength >= characterskills.util.SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('QueueTooManySkills', {'num': characterskills.util.SKILLQUEUE_MAX_NUM_SKILLS})
        newPos = position if position is not None and position >= 0 else skillQueueLength
        currentSkill = self.skills.GetSkill(skillTypeID)
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, newPos)
        startTime = None
        if newPos != 0:
            startTime = self.skillQueue[newPos - 1].trainingEndTime
        queueEntry = characterskills.util.GetQueueEntry(skillTypeID, skillLevel, newPos, currentSkill, self.skillQueue, lambda x, y: self.GetTimeForTraining(x, y, startTime), KeyVal, self.SkillInTraining() is not None)
        if newPos == skillQueueLength:
            self.skillQueue.append(queueEntry)
            self.AddToCache(skillTypeID, skillLevel, newPos)
        else:
            if newPos > skillQueueLength:
                raise UserError('QueueInvalidPosition')
            self.skillQueueCache = None
            self.skillQueue.insert(newPos, queueEntry)
            self.TrimQueue(True)
        return newPos

    def RemoveSkillFromQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID in self.skillQueueCache:
            for cacheLevel in self.skillQueueCache[skillTypeID]:
                if cacheLevel > skillLevel:
                    raise UserError('QueueCannotRemoveSkillsWithHigherLevelsStillInQueue')

        self.InternalRemoveFromQueue(skillTypeID, skillLevel)

    def FindInQueue(self, skillTypeID, skillLevel):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            return None
        if skillLevel not in self.skillQueueCache[skillTypeID]:
            return None
        return self.skillQueueCache[skillTypeID][skillLevel]

    def MoveSkillToPosition(self, skillTypeID, skillLevel, position):
        self.CheckCanInsertSkillAtPosition(skillTypeID, skillLevel, position)
        self.PrimeCache()
        currentPosition = self.skillQueueCache[skillTypeID][skillLevel]
        if currentPosition < position:
            position -= 1
        self.InternalRemoveFromQueue(skillTypeID, skillLevel)
        return self.AddSkillToQueue(skillTypeID, skillLevel, position)

    def GetQueue(self):
        return self.skillQueue[:]

    def GetServerQueue(self):
        if self.cachedSkillQueue is not None:
            return self.cachedSkillQueue[:]
        else:
            return self.GetQueue()

    def GetNumberOfSkillsInQueue(self):
        return len(self.skillQueue)

    def GetTrainingLengthOfQueue(self, position = None):
        if position is not None and position < 0:
            raise RuntimeError('Invalid queue position: ', position)
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        booster = self.GetAttributeBooster()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        currentIndex = 0
        finalIndex = position
        if finalIndex is None:
            finalIndex = len(self.skillQueue)
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= finalIndex:
                break
            currentIndex += 1
            if queueSkillTypeID not in playerTheoreticalSkillPoints:
                skill = self.skills.GetSkill(queueSkillTypeID)
                playerTheoreticalSkillPoints[queueSkillTypeID] = self.GetSkillPointsFromSkillObject(queueSkillTypeID, skill)
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, booster, currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        return trainingTime

    def GetTrainingEndTimeOfQueue(self):
        return blue.os.GetWallclockTime() + self.GetTrainingLengthOfQueue()

    def GetTrainingLengthOfSkill(self, skillTypeID, skillLevel, position = None):
        if position is not None and (position < 0 or position > len(self.skillQueue)):
            raise RuntimeError('GetTrainingLengthOfSkill received an invalid position.')
        trainingTime = 0
        currentIndex = 0
        targetIndex = position
        if targetIndex is None:
            targetIndex = self.FindInQueue(skillTypeID, skillLevel)
            if targetIndex is None:
                targetIndex = len(self.skillQueue)
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        currentAttributes = self.GetPlayerAttributeDict()
        booster = self.GetAttributeBooster()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            if currentIndex >= targetIndex:
                break
            elif queueSkillTypeID == skillTypeID and queueSkillLevel == skillLevel and currentIndex < targetIndex:
                currentIndex += 1
                continue
            addedSP, addedTime, _ = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, booster, currentAttributes)
            currentIndex += 1
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP

        addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(skillTypeID, skillLevel, skills, playerTheoreticalSkillPoints, trainingTime, booster, currentAttributes)
        trainingTime += addedTime
        return (long(trainingTime), long(addedTime), isAccelerated)

    def GetTrainingParametersOfSkillInEnvironment(self, skillTypeID, skillLevel, existingSkillPoints = 0, playerAttributeDict = None):
        playerCurrentSP = existingSkillPoints
        skillTimeConstant = self.godma.GetTypeAttribute(skillTypeID, const.attributeSkillTimeConstant)
        primaryAttributeID = self.godma.GetTypeAttribute(skillTypeID, const.attributePrimaryAttribute)
        secondaryAttributeID = self.godma.GetTypeAttribute(skillTypeID, const.attributeSecondaryAttribute)
        if existingSkillPoints is None:
            skill = self.skills.GetSkill(skillTypeID)
            if skill is not None:
                playerCurrentSP = skill.skillPoints
            else:
                playerCurrentSP = 0
        if skillTimeConstant is None:
            self.LogWarn('GetTrainingLengthOfSkillInEnvironment could not find skill type ID:', skillTypeID, 'via Godma')
            return 0
        skillPointsToTrain = characterskills.util.GetSPForLevelRaw(skillTimeConstant, skillLevel) - playerCurrentSP
        if skillPointsToTrain <= 0:
            return (0, 0)
        attrDict = playerAttributeDict
        if attrDict is None:
            attrDict = self.GetPlayerAttributeDict()
        playerPrimaryAttribute = attrDict[primaryAttributeID]
        playerSecondaryAttribute = attrDict[secondaryAttributeID]
        if playerPrimaryAttribute <= 0 or playerSecondaryAttribute <= 0:
            raise RuntimeError('GetTrainingLengthOfSkillInEnvironment found a zero attribute value on character', session.charid, 'for attributes [', primaryAttributeID, secondaryAttributeID, ']')
        trainingRate = characterskills.util.GetSkillPointsPerMinute(playerPrimaryAttribute, playerSecondaryAttribute)
        trainingTimeInMinutes = float(skillPointsToTrain) / float(trainingRate)
        return (skillPointsToTrain, trainingTimeInMinutes * const.MIN)

    def TrimQueue(self, hasChanges):
        if not hasChanges:
            return
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        booster = self.GetAttributeBooster()
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        cutoffIndex = 0
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            cutoffIndex += 1
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, booster, currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            if trainingTime > self.maxSkillqueueTimeLength:
                break

        if cutoffIndex < len(self.skillQueue):
            removedSkills = self.skillQueue[cutoffIndex:]
            self.skillQueue = self.skillQueue[:cutoffIndex]
            self.skillQueueCache = None
            eve.Message('skillQueueTrimmed', {'num': len(removedSkills)})

    def GetAttributeBooster(self):
        myGodmaItem = sm.GetService('godma').GetItem(session.charid)
        boosters = myGodmaItem.boosters
        return characterskills.util.FindAttributeBooster(self.godma, boosters)

    def GetAttributesWithoutCurrentBooster(self, booster):
        currentAttributes = self.GetPlayerAttributeDict()
        for attributeID, value in currentAttributes.iteritems():
            newValue = characterskills.util.GetBoosterlessValue(self.godma, booster.typeID, attributeID, value)
            currentAttributes[attributeID] = newValue

        return currentAttributes

    def GetAddedSpAndAddedTimeForSkill(self, skillTypeID, skillLevel, skillSet, theoreticalSkillPointsDict, trainingTimeOffset, attributeBooster, currentAttributes = None):
        if currentAttributes is None:
            currentAttributes = self.GetPlayerAttributeDict()
        isAccelerated = False
        if attributeBooster:
            if characterskills.util.IsBoosterExpiredThen(long(trainingTimeOffset), attributeBooster.expiryTime):
                currentAttributes = self.GetAttributesWithoutCurrentBooster(attributeBooster)
            else:
                isAccelerated = True
        if skillTypeID not in theoreticalSkillPointsDict:
            skillObj = skillSet.get(skillTypeID, None)
            theoreticalSkillPointsDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skillObj)
        addedSP, addedTime = self.GetTrainingParametersOfSkillInEnvironment(skillTypeID, skillLevel, theoreticalSkillPointsDict[skillTypeID], currentAttributes)
        return (addedSP, addedTime, isAccelerated)

    def GetAllTrainingLengths(self):
        trainingTime = 0
        currentAttributes = self.GetPlayerAttributeDict()
        booster = self.GetAttributeBooster()
        resultsDict = {}
        playerTheoreticalSkillPoints = {}
        skills = self.skills.GetSkills()
        for trainingSkill in self.skillQueue:
            queueSkillTypeID = trainingSkill.trainingTypeID
            queueSkillLevel = trainingSkill.trainingToLevel
            addedSP, addedTime, isAccelerated = self.GetAddedSpAndAddedTimeForSkill(queueSkillTypeID, queueSkillLevel, skills, playerTheoreticalSkillPoints, trainingTime, booster, currentAttributes)
            trainingTime += addedTime
            playerTheoreticalSkillPoints[queueSkillTypeID] += addedSP
            resultsDict[queueSkillTypeID, queueSkillLevel] = (trainingTime, addedTime, isAccelerated)

        return resultsDict

    def InternalRemoveFromQueue(self, skillTypeID, skillLevel):
        if not len(self.skillQueue):
            return
        skillPosition = self.FindInQueue(skillTypeID, skillLevel)
        if skillPosition is None:
            raise UserError('QueueSkillNotPresent')
        if skillPosition == len(self.skillQueue):
            del self.skillQueueCache[skillTypeID][skillLevel]
            self.skillQueue.pop()
        else:
            self.skillQueueCache = None
            self.skillQueue.pop(skillPosition)

    def ClearCache(self):
        self.skillQueueCache = None

    def AddToCache(self, skillTypeID, skillLevel, position):
        self.PrimeCache()
        if skillTypeID not in self.skillQueueCache:
            self.skillQueueCache[skillTypeID] = {}
        self.skillQueueCache[skillTypeID][skillLevel] = position

    def GetPlayerAttributeDict(self):
        return self.skills.GetCharacterAttributes()

    def PrimeCache(self, force = False):
        if force:
            self.skillQueueCache = None
        if self.skillQueueCache is None:
            i = 0
            self.skillQueueCache = {}
            for trainingSkill in self.skillQueue:
                self.AddToCache(trainingSkill.trainingTypeID, trainingSkill.trainingToLevel, i)
                i += 1

    def GetSkillPointsFromSkillObject(self, skillTypeID, skillInfo):
        if skillInfo is None:
            return 0
        totalSkillPoints = skillInfo.skillPoints
        trainingSkill = self.SkillInTraining(skillTypeID)
        serverQueue = self.GetServerQueue()
        if trainingSkill and len(serverQueue):
            trainingRecord = serverQueue[0]
            spHi = trainingRecord.trainingDestinationSP
            spm = self.skills.GetSkillpointsPerMinute(skillInfo.typeID)
            ETA = trainingRecord.trainingEndTime
            time = ETA - blue.os.GetWallclockTime()
            secs = time / 10000000L
            totalSkillPoints = spHi - secs / 60.0 * spm
        return totalSkillPoints

    def OnServerSkillsChanged(self, skillInfos):
        self.PrimeCache()
        sanitizedSkills = {}
        for skillTypeID, skillInfo in skillInfos.iteritems():
            skill = self.skills.GetSkill(skillTypeID)
            if not skill and skillInfo.skillLevel > 0:
                self.LogError('skillQueueSvc::OnServerSkillsChanged skill %s not found' % skillTypeID)
                continue
            sanitizedSkills[skillTypeID] = skillInfo
            skillLevel = skillInfo.skillLevel
            if skillTypeID in self.skillQueueCache:
                if skillLevel in self.skillQueueCache[skillTypeID]:
                    self.InternalRemoveFromQueue(skillTypeID, skillLevel)
            if self.cachedSkillQueue:
                keepSkills = []
                for trainingSkill in self.cachedSkillQueue:
                    if trainingSkill.trainingTypeID == skillTypeID:
                        finishedSkill = skillInfos[skillTypeID]
                        if trainingSkill.trainingToLevel <= finishedSkill.skillLevel:
                            continue
                    keepSkills.append(trainingSkill)

                self.cachedSkillQueue = keepSkills

    def OnSkillQueuePaused(self, *args):
        queue = self.skillQueue
        if self.cachedSkillQueue is not None:
            queue = self.cachedSkillQueue
        if queue:
            for skillEntry in queue:
                skillEntry.trainingStartTime = skillEntry.trainingEndTime = None

        sm.ScatterEvent('OnSkillQueueChanged')

    def OnNewSkillQueueSaved(self, newQueue):
        if self.cachedSkillQueue is not None:
            self.cachedSkillQueue = newQueue
        self.skillQueue = newQueue
        sm.ScatterEvent('OnSkillQueueChanged')

    def TrainSkillNow(self, skillTypeID, toSkillLevel, *args):
        inTraining = self.SkillInTraining()
        if inTraining and eve.Message('ConfirmSkillTrainingNow', {'name': evetypes.GetName(inTraining.typeID),
         'lvl': inTraining.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.BeginTransaction()
        commit = True
        try:
            if self.FindInQueue(skillTypeID, toSkillLevel) is not None:
                self.MoveSkillToPosition(skillTypeID, toSkillLevel, 0)
                eve.Message('SkillQueueStarted')
            else:
                self.AddSkillToQueue(skillTypeID, toSkillLevel, 0)
                text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=toSkillLevel)
                if inTraining:
                    eve.Message('AddedToQueue', {'skillname': text})
                else:
                    eve.Message('AddedToQueueAndStarted', {'skillname': text})
        except (UserError, RuntimeError):
            commit = False
            raise
        finally:
            if commit:
                self.CommitTransaction()
            else:
                self.RollbackTransaction()

    def AddSkillToEnd(self, skillTypeID, current, nextLevel = None):
        queueLength = self.GetNumberOfSkillsInQueue()
        if queueLength >= characterskills.util.SKILLQUEUE_MAX_NUM_SKILLS:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/SkillQueue/QueueIsFull')})
        totalTime = self.GetTrainingLengthOfQueue()
        if totalTime > self.maxSkillqueueTimeLength:
            raise UserError('CustomNotify', {'notify': localization.GetByLabel('UI/SkillQueue/QueueIsFull')})
        else:
            if nextLevel is None:
                queue = self.GetServerQueue()
                nextLevel = self.FindNextLevel(skillTypeID, current, queue)
            self.AddSkillToQueue(skillTypeID, nextLevel)
            try:
                self.skills.GetSkillHandler().AddToEndOfSkillQueue(skillTypeID, nextLevel)
                text = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeID, amount=nextLevel)
                if self.SkillInTraining():
                    eve.Message('AddedToQueue', {'skillname': text})
                else:
                    eve.Message('AddedToQueueAndStarted', {'skillname': text})
            except UserError as e:
                self.RemoveSkillFromQueue(skillTypeID, nextLevel)
                if e.msg == 'UserAlreadyHasSkillInTraining':
                    ShowMultiTrainingMessage()
                else:
                    raise

        sm.ScatterEvent('OnSkillQueueRefreshed')

    def FindNextLevel(self, skillTypeID, current, skillQueue = None):
        if skillQueue is None:
            skillQueue = self.GetServerQueue()
        skillQueue = [ (skill.trainingTypeID, skill.trainingToLevel) for skill in skillQueue ]
        nextLevel = None
        for i in xrange(1, 7):
            if i <= current:
                continue
            inQueue = bool((skillTypeID, i) in skillQueue)
            if inQueue is False:
                nextLevel = i
                break

        return nextLevel

    def OnMultipleCharactersTrainingUpdated(self):
        sm.GetService('objectCaching').InvalidateCachedMethodCall('userSvc', 'GetMultiCharactersTrainingSlots')
        self.PrimeCache(True)
        sm.ScatterEvent('OnMultipleCharactersTrainingRefreshed')

    def GetMultipleCharacterTraining(self, force = False):
        if force:
            sm.GetService('objectCaching').InvalidateCachedMethodCall('userSvc', 'GetMultiCharactersTrainingSlots')
        return sm.RemoteSvc('userSvc').GetMultiCharactersTrainingSlots()

    def IsQueueWndOpen(self):
        return form.SkillQueue.IsOpen()

    def GetAddMenuForSkillEntries(self, skillTypeID, skillInfo):
        m = []
        if skillInfo is None:
            return m
        skillLevel = skillInfo.skillLevel
        if skillLevel is not None:
            sqWnd = form.SkillQueue.GetIfOpen()
            if skillLevel < 5:
                queue = self.GetQueue()
                nextLevel = self.FindNextLevel(skillTypeID, skillInfo.skillLevel, queue)
                if not self.SkillInTraining(skillTypeID):
                    trainingTime, totalTime, _ = self.GetTrainingLengthOfSkill(skillTypeID, skillInfo.skillLevel + 1, 0)
                    if trainingTime <= 0:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/CompletionImminent')
                    else:
                        takesText = localization.GetByLabel('UI/SkillQueue/Skills/SkillTimeLeft', timeLeft=long(trainingTime))
                    if sqWnd:
                        if nextLevel < 6 and self.FindInQueue(skillTypeID, skillInfo.skillLevel + 1) is None:
                            trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToFrontOfQueueTime', {'takes': takesText})
                            m.append((trainText, sqWnd.AddSkillsThroughOtherEntry, (skillTypeID,
                              0,
                              queue,
                              nextLevel,
                              1)))
                    else:
                        trainText = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainNowWithTime', {'skillLevel': skillInfo.skillLevel + 1,
                         'takes': takesText})
                        m.append((trainText, self.TrainSkillNow, (skillTypeID, skillInfo.skillLevel + 1)))
                if nextLevel < 6:
                    if sqWnd:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AddToEndOfQueue', {'nextLevel': nextLevel})
                        m.append((label, sqWnd.AddSkillsThroughOtherEntry, (skillInfo.typeID,
                          -1,
                          queue,
                          nextLevel,
                          1)))
                    else:
                        label = uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/TrainAfterQueue', {'nextLevel': nextLevel})
                        m.append((label, self.AddSkillToEnd, (skillInfo.typeID, skillInfo.skillLevel, nextLevel)))
                if sm.GetService('skills').GetFreeSkillPoints() > 0:
                    diff = sm.GetService('skills').SkillpointsNextLevel(skillTypeID) + 0.5 - skillInfo.skillPoints
                    m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints'), self.UseFreeSkillPoints, (skillInfo.typeID, diff)))
            if self.SkillInTraining(skillTypeID):
                m.append((uiutil.MenuLabel('UI/SkillQueue/AddSkillMenu/AbortTraining'), sm.StartService('skills').AbortTrain))
        if m:
            m.append(None)
        return m

    def UseFreeSkillPoints(self, skillTypeID, diff):
        if self.SkillInTraining():
            eve.Message('CannotApplyFreePointsWhileQueueActive')
            return
        freeSkillPoints = sm.StartService('skills').GetFreeSkillPoints()
        text = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/UseSkillPointsWindow', skill=skillTypeID, skillPoints=int(diff))
        caption = localization.GetByLabel('UI/SkillQueue/AddSkillMenu/ApplySkillPoints')
        ret = uix.QtyPopup(maxvalue=freeSkillPoints, caption=caption, label=text)
        if ret is None:
            return
        sp = int(ret.get('qty', ''))
        sm.StartService('skills').ApplyFreeSkillPoints(skillTypeID, sp)

    def SkillInTraining(self, skillTypeID = None):
        activeQueue = self.GetServerQueue()
        if len(activeQueue) and activeQueue[0].trainingEndTime:
            if skillTypeID is None or activeQueue[0].trainingTypeID == skillTypeID:
                return self.skills.GetSkill(activeQueue[0].trainingTypeID)

    def GetTimeForTraining(self, skillTypeID, toLevel, trainingStartTime = 0):
        currentTraining = self.SkillInTraining(skillTypeID)
        skillDict = {}
        if currentTraining:
            trainingEndTime = self.GetEndOfTraining(skillTypeID)
            timeForTraining = trainingEndTime - blue.os.GetWallclockTime()
        else:
            timeOffset = 0
            if trainingStartTime:
                timeOffset = trainingStartTime - blue.os.GetWallclockTime()
            skill = self.skills.GetSkill(skillTypeID)
            attributes = self.GetPlayerAttributeDict()
            booster = self.GetAttributeBooster()
            if booster and characterskills.util.IsBoosterExpiredThen(timeOffset, booster.expiryTime):
                attributes = self.GetAttributesWithoutCurrentBooster(booster)
            skillDict[skillTypeID] = self.GetSkillPointsFromSkillObject(skillTypeID, skill)
            _, timeForTraining = self.GetTrainingParametersOfSkillInEnvironment(skillTypeID, toLevel, skillDict[skillTypeID], attributes)
        return long(timeForTraining)

    def GetEndOfTraining(self, skillTypeID):
        skillQueue = self.GetServerQueue()
        if not len(skillQueue) or skillQueue[0].trainingTypeID != skillTypeID:
            return None
        else:
            return skillQueue[0].trainingEndTime

    def GetStartOfTraining(self, skillTypeID):
        pass

    def IsMoveAllowed(self, draggedNode, checkedIdx):
        queue = self.GetQueue()
        if checkedIdx is None:
            checkedIdx = len(queue)
        if draggedNode.skillID:
            if draggedNode.panel and draggedNode.panel.__guid__ == 'listentry.SkillEntry':
                level = self.FindNextLevel(draggedNode.skillID, draggedNode.skill.skillLevel, queue)
            else:
                level = draggedNode.Get('trainToLevel', 1)
                if draggedNode.inQueue is None:
                    level += 1
            return self.CheckCanInsertSkillAtPosition(draggedNode.skillID, level, checkedIdx, check=1, performLengthTest=False)
        if draggedNode.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            category = GetAttrs(draggedNode, 'rec', 'categoryID')
            if category != const.categorySkill:
                return
            typeID = GetAttrs(draggedNode, 'rec', 'typeID')
            if typeID is None:
                return
            skill = sm.StartService('skills').GetSkill(typeID)
            if skill:
                return False
            meetsReq = sm.StartService('godma').CheckSkillRequirementsForType(typeID)
            if not meetsReq:
                return False
            return True
        if draggedNode.__guid__ == 'listentry.SkillTreeEntry':
            typeID = draggedNode.typeID
            if typeID is None:
                return
            mySkills = sm.StartService('skills').GetMyGodmaItem().skills
            skill = mySkills.get(typeID, None)
            if skill is None:
                return
            skill = sm.StartService('skills').GetSkill(typeID)
            level = self.FindNextLevel(typeID, skill.skillLevel, queue)
            return self.CheckCanInsertSkillAtPosition(typeID, level, checkedIdx, check=1, performLengthTest=False)

    def GetSkillPlanImporter(self):
        if self.skillplanImporter is None:
            self.skillplanImporter = ImportSkillPlan()
        return self.skillplanImporter
