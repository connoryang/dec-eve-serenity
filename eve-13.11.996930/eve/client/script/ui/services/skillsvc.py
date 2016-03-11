#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\skillsvc.py
import sys
import operator
from collections import defaultdict
import blue
import evetypes
import service
import uiutil
from notifications.common.formatters.skillPoints import UnusedSkillPointsFormatter
from notifications.common.notification import Notification
import uthread
import util
import xtriui
import characterskills.util
import carbonui.const as uiconst
import localization
import telemetry
from characterskills.util import GetSkillLevelRaw
import const
from utillib import KeyVal
from inventorycommon import const as invconst
import eve.common.script.util.notificationconst as notificationConst
from copy import deepcopy
SKILLREQ_DONTHAVE = 1
SKILLREQ_HAVEBUTNOTTRAINED = 2
SKILLREQ_HAVEANDTRAINED = 3
SKILLREQ_HAVEANDTRAINEDFULLY = 4
SKILLREQ_TRIALRESTRICTED = 5
TEXTURE_PATH_BY_SKILLREQ = {SKILLREQ_DONTHAVE: 'res:/UI/Texture/Classes/Skills/doNotHaveFrame.png',
 SKILLREQ_HAVEBUTNOTTRAINED: 'res:/UI/Texture/Classes/Skills/levelPartiallyTrainedFrame.png',
 SKILLREQ_HAVEANDTRAINED: 'res:/UI/Texture/Classes/Skills/levelTrainedFrame.png',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'res:/UI/Texture/Classes/Skills/fullyTrainedFrame.png',
 SKILLREQ_TRIALRESTRICTED: 'res:/UI/Texture/Classes/Skills/trialRestrictedFrame.png'}
SHIP_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/ShipSkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/ShipSkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/ShipSkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/ShipSkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/ShipSkillReqRestrictedForTrial'}
SKILL_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/SkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/SkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/SkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/SkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/SkillReqRestrictedForTrial'}
ITEM_SKILLREQ_HINT = {SKILLREQ_DONTHAVE: 'UI/InfoWindow/ItemSkillReqDoNotHave',
 SKILLREQ_HAVEBUTNOTTRAINED: 'UI/InfoWindow/ItemSkillReqPartiallyTrained',
 SKILLREQ_HAVEANDTRAINED: 'UI/InfoWindow/ItemSkillReqTrained',
 SKILLREQ_HAVEANDTRAINEDFULLY: 'UI/InfoWindow/ItemSkillReqFullyTrained',
 SKILLREQ_TRIALRESTRICTED: 'UI/InfoWindow/ItemSkillReqRestrictedForTrial'}

class SkillsSvc(service.Service):
    __guid__ = 'svc.skills'
    __exportedcalls__ = {'HasSkill': [],
     'GetSkill': [],
     'GetSkills': [],
     'MySkillLevelsByID': [],
     'GetSkillPoints': [],
     'GetSkillGroups': [],
     'GetSkillCount': [],
     'GetAllSkills': [],
     'GetSkillHistory': [],
     'GetFreeSkillPoints': [],
     'SetFreeSkillPoints': [],
     'GetBoosters': []}
    __notifyevents__ = ['ProcessSessionChange',
     'OnServerSkillsChanged',
     'OnSkillForcedRefresh',
     'OnRespecInfoChanged',
     'OnFreeSkillPointsChanged',
     'OnServerBoostersChanged',
     'OnServerImplantsChanged',
     'OnCloneDestruction']
    __servicename__ = 'skills'
    __displayname__ = 'Skill Client Service'
    __dependencies__ = ['settings', 'godma']

    def Run(self, memStream = None):
        self.LogInfo('Starting Skills')
        self.Reset()

    def Stop(self, memStream = None):
        self.Reset()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Reset()

    def Reset(self):
        self.allskills = None
        self.skillGroups = None
        self.respecInfo = None
        self.myskills = None
        self.skillHistory = None
        self.freeSkillPoints = None
        self.skillHandler = None
        self.boosters = None
        self.implants = None
        self.characterAttributes = None

    def ResetSkillHistory(self):
        self.skillHistory = None

    def GetSkillHandler(self):
        if not self.skillHandler:
            self.skillHandler = session.ConnectToRemoteService('skillMgr2').GetMySkillHandler()
        return self.skillHandler

    def RefreshMySkills(self):
        if self.myskills is not None:
            self.LogError('skillSvc is force refreshing client side skill state!')
        self.myskills = self.GetSkillHandler().GetSkills()
        for typeID, skillInfo in self.myskills.iteritems():
            setattr(skillInfo, 'typeID', typeID)

    def NotifySkillTrained(self, skillTypeID, skillLevel):
        oldNotification = settings.user.ui.Get('skills_showoldnotification', 0)
        try:
            self.skillHistory = None
            if oldNotification == 1:
                eve.Message('SkillTrained', {'name': evetypes.GetName(skillTypeID),
                 'lvl': skillLevel})
        except:
            sys.exc_clear()

        if oldNotification == 0:
            eve.Message('skillTrainingFanfare')
            onlineTraining = True
            uthread.new(sm.StartService('neocom').ShowSkillNotification, [skillTypeID], onlineTraining)

    def NotifyMultipleSkillsTrained(self, skillTypeIDs):
        oldNotification = settings.user.ui.Get('skills_showoldnotification', 0)
        if oldNotification == 1:
            if len(skillTypeIDs) == 1:
                skill = self.GetSkill(skillTypeIDs[0])
                skillLevel = skill.skillLevel if skill is not None else localization.GetByLabel('UI/Common/Unknown')
                eve.Message('SkillTrained', {'name': evetypes.GetName(skillTypeIDs[0]),
                 'lvl': skillLevel})
            else:
                eve.Message('MultipleSkillsTrainedNotify', {'num': len(skillTypeIDs)})
        else:
            eve.Message('skillTrainingFanfare')
            onlineTraining = False
            uthread.new(sm.StartService('neocom').ShowSkillNotification, skillTypeIDs, onlineTraining)

    def OnServerSkillsChanged(self, skillInfos, event):
        notifySkills = {}
        skills = self.GetSkills()
        for skillTypeID, skillInfo in skillInfos.iteritems():
            setattr(skillInfo, 'typeID', skillTypeID)
            if skillInfo.skillPoints >= 0:
                currentSkill = skills.get(skillTypeID, None)
                if currentSkill and currentSkill.skillLevel != skillInfo.skillLevel:
                    notifySkills[skillTypeID] = skillInfo
                self.myskills[skillTypeID] = skillInfo
            else:
                del self.myskills[skillTypeID]

        if notifySkills:
            if len(notifySkills) == 1:
                skillTypeID = skillInfos.keys()[0]
                self.NotifySkillTrained(skillTypeID, skillInfos[skillTypeID].skillLevel)
            else:
                self.NotifyMultipleSkillsTrained([ x for x in notifySkills.keys() ])
        sm.GetService('skillqueue').OnServerSkillsChanged(skillInfos)
        if event:
            sm.ScatterEvent(event, skillInfos)
        sm.ScatterEvent('OnSkillsChanged', skillInfos)

    def GetSkills(self, renew = 0):
        if self.myskills is None or renew:
            self.RefreshMySkills()
        return self.myskills

    def GetCharacterAttributes(self, renew = False):
        if self.characterAttributes is None or renew:
            self.GetBoosters(True)
            self.GetImplants(True)
            self.characterAttributes = self.GetSkillHandler().GetAttributes()
            for attributeID, attributeValue in self.characterAttributes.iteritems():
                self.godma.GetStateManager().ApplyAttributeChange(session.charid, session.charid, attributeID, blue.os.GetWallclockTime(), attributeValue, None, False)

        return deepcopy(self.characterAttributes)

    def GetCharacterAttribute(self, attributeID):
        return self.GetCharacterAttributes()[attributeID]

    def GetSkill(self, skillTypeID, renew = 0):
        if self.myskills is None or renew:
            self.RefreshMySkills()
        return self.myskills.get(skillTypeID, None)

    def MySkillLevel(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        if skill is not None:
            return skill.skillLevel
        return 0

    def MySkillPoints(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        if skill is not None:
            return skill.skillPoints

    def MySkillLevelsByID(self, renew = 0):
        skills = {}
        for skillTypeID, skill in self.GetSkills(renew).iteritems():
            skills[skillTypeID] = skill.skillLevel

        return skills

    def SkillpointsCurrentLevel(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        return characterskills.util.GetSPForLevelRaw(skill.skillRank, skill.skillLevel)

    def SkillpointsNextLevel(self, skillTypeID):
        skill = self.GetSkill(skillTypeID)
        if skill.skillLevel >= const.maxSkillLevel:
            return None
        return characterskills.util.GetSPForLevelRaw(skill.skillRank, skill.skillLevel + 1)

    def HasSkill(self, skillTypeID):
        return skillTypeID in self.GetSkills()

    @telemetry.ZONE_METHOD
    def GetAllSkills(self):
        if not self.allskills:
            self.allskills = {}
            for typeID in evetypes.GetTypeIDsByCategory(const.categorySkill):
                if evetypes.IsPublished(typeID):
                    self.allskills[typeID] = KeyVal(typeID=typeID, skillLevel=0, skillPoints=0, skillRank=self.GetSkillRank(typeID))

        return self.allskills

    @telemetry.ZONE_METHOD
    def GetAllSkillGroups(self):
        if not self.skillGroups:
            skillgroups = [ util.KeyVal(groupID=groupID, groupName=evetypes.GetGroupNameByGroup(groupID)) for groupID in evetypes.GetGroupIDsByCategory(const.categorySkill) if groupID not in [const.groupFakeSkills] ]
            skillgroups = localization.util.Sort(skillgroups, key=operator.attrgetter('groupName'))
            self.skillGroups = skillgroups
        return self.skillGroups

    @telemetry.ZONE_METHOD
    def GetSkillHistory(self, maxresults = 50):
        if self.skillHistory is None:
            self.skillHistory = self.GetSkillHandler().GetSkillHistory(maxresults)
        return self.skillHistory

    @telemetry.ZONE_METHOD
    def GetRecentlyTrainedSkills(self):
        skillChanges = {}
        skillData = self.GetSkillHandler().GetSkillChangesForISIS()
        for typeID, pointChange in skillData:
            currentSkillPoints = self.MySkillPoints(typeID) or 0
            timeConstant = self.godma.GetTypeAttribute2(typeID, const.attributeSkillTimeConstant)
            pointsBefore = currentSkillPoints - pointChange
            oldLevel = GetSkillLevelRaw(pointsBefore, timeConstant)
            if self.MySkillLevel(typeID) > oldLevel:
                skillChanges[typeID] = oldLevel

        return skillChanges

    @telemetry.ZONE_METHOD
    def GetSkillGroups(self, advanced = False):
        if session.charid:
            ownSkills = self.GetSkills()
            skillQueue = sm.GetService('skillqueue').GetServerQueue()
            skillsInQueue = [ skill.trainingTypeID for skill in skillQueue ]
        else:
            ownSkills = []
            skillsInQueue = []
        ownSkillTypeIDs = []
        ownSkillsByGroupID = defaultdict(list)
        ownSkillsInTrainingByGroupID = defaultdict(list)
        ownSkillsInQueueByGroupID = defaultdict(list)
        ownSkillPointsByGroupID = defaultdict(int)
        for skillTypeID, skill in ownSkills.iteritems():
            groupID = evetypes.GetGroupID(skillTypeID)
            ownSkillsByGroupID[groupID].append(skill)
            if sm.GetService('skillqueue').SkillInTraining(skillTypeID):
                ownSkillsInTrainingByGroupID[groupID].append(skill)
            if skillTypeID in skillsInQueue:
                ownSkillsInQueueByGroupID[groupID].append(skillTypeID)
            ownSkillPointsByGroupID[groupID] += skill.skillPoints
            ownSkillTypeIDs.append(skillTypeID)

        missingSkillsByGroupID = defaultdict(list)
        if advanced:
            allSkills = self.GetAllSkills()
            for skillTypeID, skill in allSkills.iteritems():
                if skillTypeID not in ownSkillTypeIDs:
                    groupID = evetypes.GetGroupID(skillTypeID)
                    missingSkillsByGroupID[groupID].append(skill)

        skillsByGroup = []
        skillgroups = self.GetAllSkillGroups()
        for invGroup in skillgroups:
            mySkillsInGroup = ownSkillsByGroupID[invGroup.groupID]
            skillsIDontHave = missingSkillsByGroupID[invGroup.groupID]
            mySkillsInTraining = ownSkillsInTrainingByGroupID[invGroup.groupID]
            mySkillsInQueue = ownSkillsInQueueByGroupID[invGroup.groupID]
            skillPointsInGroup = ownSkillPointsByGroupID[invGroup.groupID]
            skillsByGroup.append([invGroup,
             mySkillsInGroup,
             skillsIDontHave,
             mySkillsInTraining,
             mySkillsInQueue,
             skillPointsInGroup])

        return skillsByGroup

    def IsSkillRequirementMet(self, typeID):
        required = self.GetRequiredSkills(typeID)
        for skillTypeID, lvl in required.iteritems():
            if self.MySkillLevel(skillTypeID) < lvl:
                return False

        return True

    def GetRequiredSkills(self, typeID):
        ret = {}
        for i in xrange(1, 7):
            attrID = getattr(const, 'attributeRequiredSkill%s' % i)
            skillTypeID = sm.GetService('godma').GetTypeAttribute(typeID, attrID)
            if skillTypeID is not None:
                skillTypeID = int(skillTypeID)
                attrID = getattr(const, 'attributeRequiredSkill%sLevel' % i)
                lvl = sm.GetService('godma').GetTypeAttribute(typeID, attrID, 1.0)
                ret[skillTypeID] = lvl

        return ret

    def GetRequiredSkillsLevel(self, skills):
        if not skills:
            return SKILLREQ_HAVEANDTRAINED
        allLevel5 = True
        haveAll = True
        missingSkill = False
        for skillTypeID, level in skills:
            if self.IsTrialRestricted(skillTypeID):
                return SKILLREQ_TRIALRESTRICTED
            mySkill = self.GetSkill(skillTypeID)
            if mySkill is None:
                missingSkill = True
                continue
            if mySkill.skillLevel < level:
                haveAll = False
            if mySkill.skillLevel != 5:
                allLevel5 = False

        if missingSkill:
            return SKILLREQ_DONTHAVE
        elif not haveAll:
            return SKILLREQ_HAVEBUTNOTTRAINED
        elif allLevel5:
            return SKILLREQ_HAVEANDTRAINEDFULLY
        else:
            return SKILLREQ_HAVEANDTRAINED

    def GetRequiredSkillsLevelTexturePathAndHint(self, skills, typeID = None):
        skillLevel = self.GetRequiredSkillsLevel(skills)
        texturePath = TEXTURE_PATH_BY_SKILLREQ[skillLevel]
        if typeID is None:
            hint = ITEM_SKILLREQ_HINT[skillLevel]
        else:
            categoryID = evetypes.GetCategoryID(typeID)
            if categoryID == invconst.categoryShip:
                hint = SHIP_SKILLREQ_HINT[skillLevel]
            elif categoryID == invconst.categorySkill:
                hint = SKILL_SKILLREQ_HINT[skillLevel]
            else:
                hint = ITEM_SKILLREQ_HINT[skillLevel]
        return (texturePath, localization.GetByLabel(hint))

    def GetRequiredSkillsRecursive(self, typeID):
        ret = {}
        self._GetSkillsRequiredToUseTypeRecursive(typeID, ret)
        return ret

    def _GetSkillsRequiredToUseTypeRecursive(self, typeID, ret):
        for skillTypeID, lvl in self.GetRequiredSkills(typeID).iteritems():
            ret[skillTypeID] = max(ret.get(skillTypeID, 0), lvl)
            if skillTypeID != typeID:
                self._GetSkillsRequiredToUseTypeRecursive(skillTypeID, ret)

    def GetSkillTrainingTimeLeftToUseType(self, skillTypeID):
        if self.IsSkillRequirementMet(skillTypeID):
            return 0
        totalTime = 0
        required = self.GetRequiredSkillsRecursive(skillTypeID)
        have = self.GetSkills()
        requiredMax = {}
        for typeID, lvl in required.iteritems():
            haveSkill = have.get(typeID, None)
            if haveSkill and haveSkill.skillLevel >= lvl:
                continue
            elif typeID not in requiredMax or lvl > requiredMax[typeID]:
                requiredMax[typeID] = lvl

        for typeID, lvl in requiredMax.iteritems():
            totalTime += self.GetRawTrainingTimeForSkillLevel(typeID, lvl)

        return totalTime

    def GetSkillToolTip(self, skillTypeID, level):
        if session.charid is None:
            return
        mySkill = self.GetSkill(skillTypeID)
        mySkillLevel = 0
        if mySkill is not None:
            mySkillLevel = mySkill.skillLevel
        tooltipText = evetypes.GetDescription(skillTypeID)
        tooltipTextList = []
        for i in xrange(int(mySkillLevel) + 1, int(level) + 1):
            timeLeft = self.GetRawTrainingTimeForSkillLevel(skillTypeID, i)
            tooltipTextList.append(localization.GetByLabel('UI/SkillQueue/Skills/SkillLevelAndTrainingTime', skillLevel=i, timeLeft=long(timeLeft)))

        levelsText = '<br>'.join(tooltipTextList)
        if levelsText:
            tooltipText += '<br><br>' + levelsText
        return tooltipText

    def GetSkillpointsPerMinute(self, skillTypeID):
        primaryAttributeID = sm.GetService('godma').GetTypeAttribute(skillTypeID, const.attributePrimaryAttribute)
        secondaryAttributeID = sm.GetService('godma').GetTypeAttribute(skillTypeID, const.attributeSecondaryAttribute)
        playerPrimaryAttribute = self.GetCharacterAttribute(primaryAttributeID)
        playerSecondaryAttribute = self.GetCharacterAttribute(secondaryAttributeID)
        return characterskills.util.GetSkillPointsPerMinute(playerPrimaryAttribute, playerSecondaryAttribute)

    def GetRawTrainingTimeForSkillLevel(self, skillTypeID, skillLevel):
        skillTimeConstant = self.GetSkillRank(skillTypeID)
        rawSkillPointsToTrain = characterskills.util.GetSPForLevelRaw(skillTimeConstant, skillLevel)
        trainingRate = self.GetSkillpointsPerMinute(skillTypeID)
        existingSP = 0
        priorLevel = skillLevel - 1
        skillInfo = self.GetSkills().get(skillTypeID, None)
        if skillInfo and priorLevel >= 0 and priorLevel == skillInfo.skillLevel:
            existingSP = sm.GetService('skillqueue').GetSkillPointsFromSkillObject(skillTypeID, skillInfo)
        skillPointsToTrain = rawSkillPointsToTrain - existingSP
        trainingTimeInMinutes = float(skillPointsToTrain) / float(trainingRate)
        return trainingTimeInMinutes * const.MIN

    @telemetry.ZONE_METHOD
    def GetSkillCount(self):
        return len(self.GetSkills())

    @telemetry.ZONE_METHOD
    def GetSkillPoints(self, groupID = None):
        return sum([ skillInfo.skillPoints for skillTypeID, skillInfo in self.GetSkills().iteritems() if groupID is None or evetypes.GetGroupID(skillTypeID) == groupID ])

    def GetSkillRank(self, skillTypeID):
        return self.godma.GetTypeAttribute(skillTypeID, const.attributeSkillTimeConstant)

    def Train(self, skillX):
        skill = sm.GetService('skillqueue').SkillInTraining()
        if skill and eve.Message('ConfirmResetSkillTraining', {'name': evetypes.GetName(skill.typeID),
         'lvl': skill.skillLevel + 1}, uiconst.OKCANCEL) != uiconst.ID_OK:
            return
        self.GetSkillHandler().CharStartTrainingSkill(skillX.itemID, skillX.locationID)

    def InjectSkillIntoBrain(self, skillX):
        skillIDList = [ skill.itemID for skill in skillX ]
        if not skillIDList:
            return
        try:
            self.godma.GetDogmaLM().InjectSkillIntoBrain(skillIDList)
        except UserError as e:
            if e.msg == 'TrialAccountRestriction':
                uicore.cmd.OpenTrialUpsell(origin='skills', reason=e.dict['skill'], message=localization.GetByLabel('UI/TrialUpsell/SkillRestrictionBody', skillname=evetypes.GetName(e.dict['skill'])))
            else:
                raise

    def AbortTrain(self):
        if eve.Message('ConfirmAbortSkillTraining', {}, uiconst.OKCANCEL) == uiconst.ID_OK:
            self.GetSkillHandler().AbortTraining()

    @telemetry.ZONE_METHOD
    def GetRespecInfo(self):
        if self.respecInfo is None:
            self.respecInfo = self.GetSkillHandler().GetRespecInfo()
        return self.respecInfo

    def OnRespecInfoChanged(self, *args):
        self.respecInfo = None
        self.GetCharacterAttributes(True)
        sm.ScatterEvent('OnRespecInfoUpdated')

    def OnOpenCharacterSheet(self, skillIDs, *args):
        sm.GetService('charactersheet').ForceShowSkillHistoryHighlighting(skillIDs)

    def MakeSkillQueueEmptyNotification(self, skillQueueNotification):
        queueText = localization.GetByLabel('UI/SkillQueue/NoSkillsInQueue')
        skillQueueNotification = Notification.MakeSkillNotification(header=queueText, text='', created=blue.os.GetWallclockTime(), callBack=sm.StartService('skills').OnOpenCharacterSheet, callbackargs=None, notificationType=Notification.SKILL_NOTIFICATION_EMPTYQUEUE)
        return skillQueueNotification

    def ShowSkillNotification(self, skillTypeIDs, left, onlineTraining):
        data = util.KeyVal()
        skillText = ''
        skillLevel = localization.GetByLabel('UI/Generic/Unknown')
        notifySkillTraining = False
        if len(skillTypeIDs) == 1:
            skill = self.GetSkill(skillTypeIDs[0])
            if skill:
                skillLevel = skill.skillLevel
            skillText = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndLevel', skill=skillTypeIDs[0], amount=skillLevel)
            if onlineTraining:
                notifySkillTraining = True
        else:
            notifySkillTraining = True
            skillText = localization.GetByLabel('UI/SkillQueue/Skills/NumberOfSkills', amount=len(skillTypeIDs))
        queue = sm.GetService('skillqueue').GetServerQueue()
        skillQueueNotification = None
        if len(queue) == 0:
            skillQueueNotification = self.MakeSkillQueueEmptyNotification(skillQueueNotification)
        headerText = localization.GetByLabel('UI/Generic/SkillTrainingComplete')
        skillnotification = Notification.MakeSkillNotification(headerText + ' - ' + skillText, skillText, blue.os.GetWallclockTime(), callBack=sm.StartService('skills').OnOpenCharacterSheet, callbackargs=skillTypeIDs)
        if notifySkillTraining:
            sm.ScatterEvent('OnNewNotificationReceived', skillnotification)
        if skillQueueNotification:
            sm.ScatterEvent('OnNewNotificationReceived', skillQueueNotification)

    def OnFreeSkillPointsChanged(self, newFreeSkillPoints):
        self.SetFreeSkillPoints(newFreeSkillPoints)

    @telemetry.ZONE_METHOD
    def GetFreeSkillPoints(self):
        if self.freeSkillPoints is None:
            self.freeSkillPoints = self.GetSkillHandler().GetFreeSkillPoints()
        return self.freeSkillPoints

    def ApplyFreeSkillPoints(self, skillTypeID, pointsToApply):
        if self.freeSkillPoints is None:
            self.GetFreeSkillPoints()
        if sm.GetService('skillqueue').SkillInTraining() is not None:
            raise UserError('CannotApplyFreePointsWhileQueueActive')
        skill = self.GetSkill(skillTypeID)
        if skill is None:
            raise UserError('CannotApplyFreePointsDoNotHaveSkill', {'skillName': evetypes.GetName(skillTypeID)})
        spAtMaxLevel = characterskills.util.GetSPForLevelRaw(skill.skillRank, 5)
        if skill.skillPoints + pointsToApply > spAtMaxLevel:
            pointsToApply = spAtMaxLevel - skill.skillPoints
        if pointsToApply > self.freeSkillPoints:
            raise UserError('CannotApplyFreePointsNotEnoughRemaining', {'pointsRequested': pointsToApply,
             'pointsRemaining': self.freeSkillPoints})
        if pointsToApply <= 0:
            return
        skillQueue = sm.GetService('skillqueue').GetQueue()
        for trainingSkill in skillQueue:
            if trainingSkill.trainingTypeID == skillTypeID:
                raise UserError('CannotApplyFreePointsToQueuedSkill', {'skillName': evetypes.GetName(skillTypeID)})

        newFreePoints = self.GetSkillHandler().ApplyFreeSkillPoints(skill.typeID, pointsToApply)
        self.SetFreeSkillPoints(newFreePoints)

    def SetFreeSkillPoints(self, newFreePoints):
        if self.freeSkillPoints is None or newFreePoints != self.freeSkillPoints:
            if self.freeSkillPoints is None or newFreePoints > self.freeSkillPoints:
                uthread.new(self.ShowSkillPointsNotification_thread)
            self.freeSkillPoints = newFreePoints
            sm.ScatterEvent('OnFreeSkillPointsChanged_Local')

    def MakeAndScatterSkillPointNotification(self):
        notificationData = UnusedSkillPointsFormatter.MakeData()
        sm.GetService('notificationSvc').MakeAndScatterNotification(type=notificationConst.notificationTypeUnusedSkillPoints, data=notificationData)

    def ShowSkillPointsNotification(self, number = (0, 0), time = 5000, *args):
        skillPointsNow = self.GetFreeSkillPoints()
        skillPointsLast = settings.user.ui.Get('freeSkillPoints', -1)
        if skillPointsLast == skillPointsNow:
            return
        if skillPointsNow <= 0:
            return
        self.MakeAndScatterSkillPointNotification()
        settings.user.ui.Set('freeSkillPoints', skillPointsNow)

    def ShowSkillPointsNotification_thread(self):
        blue.pyos.synchro.SleepWallclock(5000)
        self.ShowSkillPointsNotification()

    def IsTrialRestricted(self, typeID):
        isTrialUser = session.userType == const.userTypeTrial
        if not isTrialUser:
            return False
        restricted = self.godma.GetTypeAttribute(typeID, const.attributeCanNotBeTrainedOnTrial)
        if evetypes.GetCategoryID(typeID) == invconst.categorySkill and restricted:
            return True
        requirements = self.GetRequiredSkillsRecursive(typeID)
        for skillID in requirements.iterkeys():
            restricted = self.godma.GetTypeAttribute(skillID, const.attributeCanNotBeTrainedOnTrial)
            if restricted:
                return True

        return False

    def OnSkillForcedRefresh(self):
        uthread.Pool('skillSvc::OnSkillForcedRefresh', self.ForceRefresh)

    def ForceRefresh(self):
        self.Reset()
        sm.ScatterEvent('OnSkillQueueRefreshed')

    def OnServerBoostersChanged(self, *args):
        self.GetBoosters(forced=1)
        self.GetCharacterAttributes(True)
        sm.ScatterEvent('OnBoosterUpdated')
        sm.GetService('charactersheet').OnUIRefresh()

    def OnServerImplantsChanged(self, *args):
        self.GetImplants(forced=1)
        self.GetCharacterAttributes(True)
        sm.GetService('charactersheet').OnUIRefresh()

    def OnCloneDestruction(self, *args):
        self.GetBoosters(forced=1)
        sm.ScatterEvent('OnBoosterUpdated')
        self.GetImplants(forced=1)
        self.GetCharacterAttributes(True)
        sm.GetService('charactersheet').OnUIRefresh()

    def OnJumpCloneTransitionCompleted(self):
        self.GetImplants(True)
        if self.boosters:
            self.GetBoosters(True)
            sm.ScatterEvent('OnBoosterUpdated')
        self.GetCharacterAttributes(True)

    def GetBoosters(self, forced = 0):
        if self.boosters is None or forced:
            self.boosters = self.GetSkillHandler().GetBoosters()
        return self.boosters

    def GetImplants(self, forced = 0):
        if self.implants is None or forced:
            self.implants = self.GetSkillHandler().GetImplants()
        return self.implants
