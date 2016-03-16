#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\skilltrading\skillExtractorController.py
import characterskills as charskills
from collections import defaultdict
import signals

class SkillExtractorError(Exception):
    pass


class NoSkillpointsError(SkillExtractorError):
    pass


class SkillNotFoundError(SkillExtractorError):
    pass


class SkillLockedError(SkillExtractorError):
    pass


class NotEnoughExtractedError(SkillExtractorError):
    pass


class GoalAlreadyReachedError(SkillExtractorError):
    pass


class SkillNotExtractedError(SkillExtractorError):
    pass


class SkillSourceInterface(object):

    def GetSkills(self):
        raise NotImplementedError()

    def GetSkillQueue(self):
        raise NotImplementedError()

    def GetSkillRestrictions(self):
        raise NotImplementedError()

    def PerformExtraction(self, itemID, skills):
        raise NotImplementedError()


class SkillExtractorControllerBase(SkillSourceInterface):
    SKILL_POINT_GOAL = const.SKILL_TRADING_BUCKET_SIZE

    def __init__(self, itemID):
        super(SkillExtractorControllerBase, self).__init__()
        self.itemID = itemID
        self.isCompleted = False
        self._skills = None
        self._skillsByID = None
        self._extracted = defaultdict(list)
        self.onUpdate = signals.Signal()
        self.onSkillListUpdate = signals.Signal()
        self.onSkillListUpdate.connect(self.onUpdate)

    @property
    def extractedPoints(self):
        return sum((sum(p) for p in self._extracted.itervalues()), 0)

    @property
    def progress(self):
        return self.extractedPoints / float(self.SKILL_POINT_GOAL)

    @property
    def skills(self):
        if self._skills is None:
            self._skills = self.GetSkills()
            for skill in self._skills:
                self._UpdateSkillExtracted(skill)
                self._UpdateSkillRequired(skill)
                self._UpdateSkillQueued(skill)
                self._UpdateSkillRestricted(skill)

        return self._skills

    @property
    def skillsByID(self):
        if self._skillsByID is None:
            self._skillsByID = {s.typeID:s for s in self.skills}
        return self._skillsByID

    def ExtractSkill(self, skillID):
        if self.extractedPoints >= self.SKILL_POINT_GOAL:
            raise GoalAlreadyReachedError()
        if skillID not in self.skillsByID:
            raise SkillNotFoundError()
        skill = self.skillsByID[skillID]
        if skill.IsLocked():
            raise SkillLockedError()
        clamped_points = self._GetClampedSkillPointAdjustment(skill)
        self._extracted[skill.typeID].append(clamped_points)
        self._UpdateSkillExtracted(skill)
        self._UpdateSkillRequired(skill)
        self._UpdateSkillRestricted(skill)
        for requiredSkillID in skill.requirements:
            if requiredSkillID not in self.skillsByID:
                continue
            s = self.skillsByID[requiredSkillID]
            self._UpdateSkillRequired(s)
            s.NotifyOnUpdateIfDirty()

        skill.NotifyOnUpdateIfDirty()
        self.onUpdate()

    def Revert(self, skillID):
        if skillID not in self._extracted:
            raise SkillNotExtractedError()
        self._RevertSingleLevel(skillID)
        self._RevertRequirements(skillID)
        skill = self.skillsByID[skillID]
        self._UpdateSkillRestricted(skill)
        for skill in self.skills:
            skill.NotifyOnUpdateIfDirty()

        self.onUpdate()

    def _RevertRequirements(self, skillID):
        skill = self.skillsByID[skillID]
        for requiredSkillID, requiredLevel in skill.requirements.iteritems():
            if requiredSkillID not in self.skillsByID:
                continue
            requiredSkill = self.skillsByID[requiredSkillID]
            while requiredSkill.level < requiredLevel and requiredSkillID in self._extracted:
                self._RevertSingleLevel(requiredSkillID)

            self._RevertRequirements(requiredSkillID)
            self._UpdateSkillRequired(requiredSkill)

        self._UpdateSkillRequired(skill)

    def _RevertSingleLevel(self, skillID):
        self._extracted[skillID].pop()
        if len(self._extracted[skillID]) == 0:
            del self._extracted[skillID]
        skill = self.skillsByID[skillID]
        self._UpdateSkillExtracted(skill)

    def _UpdateSkillExtracted(self, skill):
        extractedPoints = sum(self._extracted.get(skill.typeID, []))
        skill.points = skill.unmodifiedPoints - extractedPoints

    def _UpdateSkillRequired(self, skill):
        required = False
        for dependentSkillID, level in skill.dependencies.iteritems():
            if dependentSkillID not in self.skillsByID:
                continue
            isDependentQueued = dependentSkillID in (s for s, _ in self.GetSkillQueue())
            dependentSkillPoints = self.skillsByID[dependentSkillID].points
            if dependentSkillPoints == 0 and not isDependentQueued:
                continue
            requiredPoints = charskills.GetSPForLevelRaw(skill.rank, level)
            if skill.points <= requiredPoints:
                required = True
                break

        skill.isRequired = required

    def _UpdateSkillQueued(self, skill):
        queuedSkills = set((skillID for skillID, _ in self.GetSkillQueue()))
        skill.isQueued = skill.typeID in queuedSkills

    def _GetClampedSkillPointAdjustment(self, skill):
        adjustment = self._GetNextExtractionIncrement(skill)
        return self._ClampToRemainingSkillPoints(adjustment)

    def _GetNextExtractionIncrement(self, skill):
        if skill.points == 0:
            raise NoSkillpointsError()
        current_level_absolute_points = charskills.GetSPForLevelRaw(skill.rank, skill.level)
        if current_level_absolute_points < skill.points:
            adjust_to_level = skill.level
        else:
            adjust_to_level = skill.level - 1
        return skill.points - charskills.GetSPForLevelRaw(skill.rank, adjust_to_level)

    def _ClampToRemainingSkillPoints(self, points):
        remaining = self.SKILL_POINT_GOAL - self.extractedPoints
        return min(remaining, max(0, points))

    def Commit(self):
        if self.extractedPoints < self.SKILL_POINT_GOAL:
            raise NotEnoughExtractedError()
        skills = {sid:sum(p) for sid, p in self._extracted.iteritems()}
        self.PerformExtraction(self.itemID, skills)
        self.isCompleted = True
        self.onUpdate()

    def OnSkillTrained(self, skillID, points):
        if skillID not in self.skillsByID:
            self.Clear()
            return
        skill = self.skillsByID[skillID]
        if points == -1:
            self._CheckAndRemoveExtracted(skill)
            self.Clear()
        else:
            skill.points = points
            skill._unmodifiedPoints = points
            wasExtracted = self._CheckAndRemoveExtracted(skill)
            if wasExtracted:
                self.onUpdate()
            skill.NotifyOnUpdateIfDirty()

    def Clear(self):
        self._skills = None
        self._skillsByID = None
        self.onSkillListUpdate()

    def OnSkillQueueUpdated(self):
        extractedBefore = self.extractedPoints
        for skill in self.skills:
            self._UpdateSkillQueued(skill)

        queuedSkills = [ self.skillsByID[sid] for sid, _ in self.GetSkillQueue() ]
        for skill in queuedSkills:
            self._CheckAndRemoveExtracted(skill)
            self._RevertRequirements(skill.typeID)

        for skill in self.skills:
            self._UpdateSkillRequired(skill)
            skill.NotifyOnUpdateIfDirty()

        if extractedBefore != self.extractedPoints:
            self.onUpdate()

    def _CheckAndRemoveExtracted(self, skill):
        isExtracted = skill.typeID in self._extracted
        if isExtracted:
            del self._extracted[skill.typeID]
            self._UpdateSkillExtracted(skill)
            self._UpdateSkillRestricted(skill)
        return isExtracted

    def Close(self):
        self.onSkillListUpdate.clear()
        self.onUpdate.clear()
        if self._skills is not None:
            for skill in self._skills:
                skill.onUpdate.clear()

    def OnSkillRestrictionsUpdated(self):
        for skill in self.skills:
            self._UpdateSkillRestricted(skill)

        extractedBefore = self.extractedPoints
        restrictions = self.GetSkillRestrictions()
        for skillID, restrictedLevel in restrictions.iteritems():
            if skillID not in self.skillsByID:
                continue
            skill = self.skillsByID[skillID]
            self._RevertToLevel(skill, restrictedLevel)
            self._RevertRequirements(skillID)
            skill.NotifyOnUpdateIfDirty()

        for skill in self.skills:
            skill.NotifyOnUpdateIfDirty()

        if self.extractedPoints != extractedBefore:
            self.onUpdate()

    def _RevertToLevel(self, skill, level):
        while skill.level < level and skill.typeID in self._extracted:
            self._extracted[skill.typeID].pop()
            if len(self._extracted[skill.typeID]) == 0:
                del self._extracted[skill.typeID]
            self._UpdateSkillExtracted(skill)

    def _UpdateSkillRestricted(self, skill):
        restrictions = self.GetSkillRestrictions()
        if skill.typeID not in restrictions:
            skill.isRestricted = False
        else:
            restrictedPoints = charskills.GetSPForLevelRaw(skill.rank, restrictions[skill.typeID])
            skill.isRestricted = skill.points <= restrictedPoints


class SkillStaticDataInterface(object):

    def GetRequirements(self):
        raise NotImplementedError()

    def GetDependencies(self):
        raise NotImplementedError()

    def GetRank(self):
        raise NotImplementedError()


class SkillBase(SkillStaticDataInterface):

    def __init__(self, typeID, points):
        super(SkillBase, self).__init__()
        self._typeID = typeID
        self._points = points
        self._unmodifiedPoints = points
        self._isRequired = False
        self._isQueued = False
        self._isRestricted = False
        self._rank = None
        self._level = None
        self._dirty = False
        self.onUpdate = signals.Signal()

    @property
    def typeID(self):
        return self._typeID

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, points):
        self._dirty |= points != self._points
        self._points = points
        self._level = None

    @property
    def unmodifiedPoints(self):
        return self._unmodifiedPoints

    @property
    def progress(self):
        return self._CalculateProgress(self.points)

    @property
    def unmodifiedProgress(self):
        return self._CalculateProgress(self.unmodifiedPoints)

    def _CalculateProgress(self, points):
        level = charskills.GetSkillLevelRaw(points, self.rank)
        if level == 5:
            return 0.0
        last_level_points = charskills.GetSPForLevelRaw(self.rank, level)
        next_level_points = charskills.GetSPForLevelRaw(self.rank, level + 1)
        current_level_points = points - last_level_points
        return current_level_points / float(next_level_points - last_level_points)

    @property
    def level(self):
        if self._level is None:
            self._level = charskills.GetSkillLevelRaw(self.points, self.rank)
        return self._level

    @property
    def unmodifiedLevel(self):
        return charskills.GetSkillLevelRaw(self.unmodifiedPoints, self.rank)

    @property
    def rank(self):
        if self._rank is None:
            self._rank = self.GetRank()
        return self._rank

    @property
    def requirements(self):
        return self.GetRequirements()

    @property
    def dependencies(self):
        return self.GetDependencies()

    @property
    def isRequired(self):
        return self._isRequired

    @isRequired.setter
    def isRequired(self, required):
        self._dirty |= required != self._isRequired
        self._isRequired = required

    @property
    def isQueued(self):
        return self._isQueued

    @isQueued.setter
    def isQueued(self, queued):
        self._dirty |= queued != self._isQueued
        self._isQueued = queued

    @property
    def isRestricted(self):
        return self._isRestricted

    @isRestricted.setter
    def isRestricted(self, restricted):
        self._dirty |= restricted != self._isRestricted
        self._isRestricted = restricted

    def NotifyOnUpdateIfDirty(self):
        if self._dirty:
            self._dirty = False
            self.onUpdate()

    def IsLocked(self):
        return self.isRequired or self.isQueued or self.isRestricted


class SkillServiceStaticDataInterface(SkillStaticDataInterface):

    def GetRequirements(self):
        return sm.GetService('skills').GetRequiredSkills(self.typeID)

    def GetDependencies(self):
        return sm.GetService('skills').GetDependentSkills(self.typeID)

    def GetRank(self):
        return sm.GetService('skills').GetSkillRank(self.typeID)


class SkillImpl(SkillBase, SkillServiceStaticDataInterface):
    pass


class SkillServiceSkillSource(SkillSourceInterface):

    def GetSkills(self):
        raw_skills = sm.GetService('skills').GetSkills().values()
        return [ SkillImpl(typeID=s.typeID, points=s.skillPoints) for s in raw_skills ]

    def GetSkillQueue(self):
        queue = sm.GetService('skillqueue').GetQueue()
        return [ (x.trainingTypeID, x.trainingToLevel) for x in queue ]

    def GetSkillRestrictions(self):
        restrictions = {}
        restrictions.update(self._GetRestrictedPlanetSkills())
        restrictions.update(self._GetRestrictedCloneSkills())
        restrictions.update(self._GetRestrictedImplantSkills())
        return restrictions

    def _GetRestrictedPlanetSkills(self):
        restrictions = {}
        colonies = sm.GetService('planetSvc').GetMyPlanets()
        if len(colonies) > 0:
            colonyLimit = 1 + len(colonies)
            restrictions[const.typeInterplanetaryConsolidation] = colonyLimit
        maxUpgradeLevel = 0
        for planetID in (c.planetID for c in colonies):
            planet = sm.GetService('planetSvc').GetPlanet(planetID)
            colonyLevel = planet.GetCommandCenterLevel(session.charid)
            maxUpgradeLevel = max(colonyLevel, maxUpgradeLevel)

        if maxUpgradeLevel > 0:
            restrictions[const.typeCommandCenterUpgrade] = maxUpgradeLevel
        return restrictions

    def _GetRestrictedCloneSkills(self):
        restrictions = {}
        cloneCount = len(sm.GetService('clonejump').GetClones())
        if cloneCount > 0:
            restrictions[const.typeInfomorphPsychology] = min(cloneCount, 5)
        if cloneCount > 5:
            restrictions[const.typeAdvancedInfomorphPsychology] = cloneCount - 5
        return restrictions

    def _GetRestrictedImplantSkills(self):
        restrictions = {}
        implants = self._GetAllMyImplants()
        for typeID in implants:
            requirements = sm.GetService('skills').GetRequiredSkills(typeID)
            for requiredSkillID, requiredLevel in requirements.iteritems():
                maxRequiredLevel = max(requiredLevel, restrictions.get(requiredSkillID, 0))
                restrictions[requiredSkillID] = maxRequiredLevel

        return restrictions

    def _GetAllMyImplants(self):
        implants = set()
        currentImplants = sm.GetService('skills').GetImplants().values()
        implants.update((i.typeID for i in currentImplants))
        jumpCloneImplants = sm.GetService('clonejump').GetCloneImplants()
        implants.update((i.typeID for i in jumpCloneImplants or []))
        return implants

    def PerformExtraction(self, itemID, skills):
        sm.GetService('skills').ExtractSkills(skills, itemID)
        sm.UnregisterNotify(self)


class SkillExtractorController(SkillExtractorControllerBase, SkillServiceSkillSource):
    __notifyevents__ = ['OnCloneJumpUpdate',
     'OnImplantsChanged',
     'OnNewSkillQueueSaved',
     'OnPlanetChangesSubmitted',
     'OnPlanetCommandCenterDeployedOrRemoved',
     'OnSkillsChanged']

    def __init__(self, *args, **kwargs):
        super(SkillExtractorController, self).__init__(*args, **kwargs)
        self._cached_queue = None
        self._cached_planet_restrictions = None
        self._cached_clone_restrictions = None
        self._cached_implant_restrictions = None
        sm.RegisterNotify(self)

    def Close(self):
        super(SkillExtractorController, self).Close()
        sm.UnregisterNotify(self)

    def GetSkillQueue(self):
        if self._cached_queue is None:
            self._cached_queue = super(SkillExtractorController, self).GetSkillQueue()
        return self._cached_queue

    def _GetRestrictedPlanetSkills(self):
        if self._cached_planet_restrictions is None:
            restrictions = super(SkillExtractorController, self)._GetRestrictedPlanetSkills()
            self._cached_planet_restrictions = restrictions
        return self._cached_planet_restrictions

    def _GetRestrictedCloneSkills(self):
        if self._cached_clone_restrictions is None:
            restrictions = super(SkillExtractorController, self)._GetRestrictedCloneSkills()
            self._cached_clone_restrictions = restrictions
        return self._cached_clone_restrictions

    def _GetRestrictedImplantSkills(self):
        if self._cached_implant_restrictions is None:
            restrictions = super(SkillExtractorController, self)._GetRestrictedImplantSkills()
            self._cached_implant_restrictions = restrictions
        return self._cached_implant_restrictions

    def OnCloneJumpUpdate(self):
        self._cached_clone_restrictions = None
        self._cached_implant_restrictions = None
        self.OnSkillRestrictionsUpdated()

    def OnImplantsChanged(self):
        self._cached_implant_restrictions = None
        self.OnSkillRestrictionsUpdated()

    def OnNewSkillQueueSaved(self, newQueue):
        self._cached_queue = None
        self.OnSkillQueueUpdated()

    def OnPlanetChangesSubmitted(self, planetID):
        self._cached_planet_restrictions = None
        self.OnSkillRestrictionsUpdated()

    def OnPlanetCommandCenterDeployedOrRemoved(self):
        self._cached_planet_restrictions = None
        self.OnSkillRestrictionsUpdated()

    def OnSkillsChanged(self, skillInfo):
        for skillID, info in skillInfo.iteritems():
            self.OnSkillTrained(skillID, info.skillPoints)


def __SakeReloadHook():
    import log
    try:
        from eve.client.script.ui.skilltrading.test import test_skillExtractorController
        import unittest
        import sys
        suite = unittest.TestLoader().loadTestsFromModule(test_skillExtractorController)
        unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    except:
        log.LogException()
