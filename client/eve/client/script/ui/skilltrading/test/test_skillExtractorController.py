#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\skilltrading\test\test_skillExtractorController.py
from itertools import izip
import mock
import unittest
from eve.client.script.ui.skilltrading.skillExtractorController import *

class SkillExtractorControllerTestImpl(SkillExtractorControllerBase):

    def __init__(self, *args, **kwargs):
        super(SkillExtractorControllerTestImpl, self).__init__(*args, **kwargs)
        self._mock_skill_list = []
        self._mock_skill_queue = []
        self._mock_skill_restrictions = {}
        self._final_extracted_skills = None
        self._final_itemID = None

    def GetSkills(self):
        skills = []
        for s in self._mock_skill_list:
            if hasattr(s, 'typeID'):
                skills.append(s)
            else:
                skill = SkillFixture(s['typeID'], s['sp'], s.get('rank', 1.0), s.get('requirements', None), s.get('dependencies', None))
                skills.append(skill)

        return skills

    def GetSkillQueue(self):
        return self._mock_skill_queue

    def GetSkillRestrictions(self):
        return self._mock_skill_restrictions

    def PerformExtraction(self, itemID, skills):
        self._final_extracted_skills = skills
        self._final_itemID = itemID


class SkillFixture(SkillBase):

    def __init__(self, typeID, points, rank, requirements = None, dependencies = None):
        super(SkillFixture, self).__init__(typeID=typeID, points=points)
        self._rank = rank
        self._requirements = requirements if requirements is not None else {}
        self._dependencies = dependencies if dependencies is not None else {}
        self.onUpdateHandler = mock.Mock()
        self.onUpdate.connect(self.onUpdateHandler)

    def GetRequirements(self):
        return self._requirements

    def GetDependencies(self):
        return self._dependencies

    def GetRank(self):
        return self._rank


EXTRACTOR_ITEM_ID = 123
SP_R1_L1 = 250
SP_R1_L2 = 1415
SP_R1_L3 = 8000
SP_R1_L4 = 45255
SP_R1_L5 = 256000
SKILL_R1_L0 = {'typeID': 1,
 'rank': 1.0,
 'sp': 0,
 'level': 0,
 'requirements': {10: 1}}
SKILL_R1_L0_TRAINED = {'typeID': 2,
 'rank': 1.0,
 'sp': 125,
 'level': 0}
SKILL_R1_L1 = {'typeID': 3,
 'rank': 1.0,
 'sp': SP_R1_L1,
 'level': 1,
 'requirements': {10: 1}}
SKILL_R1_L1_TRAINED = {'typeID': 4,
 'rank': 1.0,
 'sp': 500,
 'level': 1}
SKILL_R1_L2 = {'typeID': 5,
 'rank': 1.0,
 'sp': SP_R1_L2,
 'level': 2}
SKILL_R1_L4 = {'typeID': 6,
 'rank': 1.0,
 'sp': SP_R1_L4,
 'level': 4}
SKILL_R1_L5 = {'typeID': 7,
 'rank': 1.0,
 'sp': SP_R1_L5,
 'level': 5}
SKILL_R4_L5 = {'typeID': 8,
 'rank': 4.0,
 'sp': 1024000,
 'level': 5}
SKILL_R10_L5 = {'typeID': 9,
 'rank': 10.0,
 'sp': 2560000,
 'level': 5}
SKILL_R1_L1_PREREQ_L1 = {'typeID': 10,
 'rank': 1.0,
 'sp': SP_R1_L1,
 'level': 1,
 'dependencies': {3: 1,
                  1: 1}}
SKILL_R1_L1_PREREQ_L1_TRAINED = {'typeID': 10,
 'rank': 1.0,
 'sp': 500,
 'level': 1,
 'dependencies': {3: 1,
                  1: 1}}
SKILL_R1_L1_PREREQ_L5 = {'typeID': 10,
 'rank': 1.0,
 'sp': SP_R1_L5,
 'level': 5,
 'dependencies': {3: 1,
                  1: 1}}

class TestSkill(unittest.TestCase):

    def test_untrained_skill(self):
        skill = SkillFixture(typeID=1, points=0, rank=1.0)
        self.assertAlmostEqual(skill.progress, 0.0)

    def test_trained_level_zero_skill(self):
        skill = SkillFixture(typeID=1, points=125, rank=1.0)
        self.assertAlmostEqual(skill.progress, 0.5)

    def test_trained_level_four_skill(self):
        skill = SkillFixture(typeID=1, points=87404, rank=1.0)
        self.assertAlmostEqual(skill.progress, 0.2)

    def test_level_five_skill(self):
        skill = SkillFixture(typeID=1, points=256000, rank=1.0)
        self.assertAlmostEqual(skill.progress, 0.0)

    def test_unmodified_attributes(self):
        skill = SkillFixture(typeID=1, points=250, rank=1.0)
        skill.points = 125
        self.assertEqual(skill.points, 125)
        self.assertEqual(skill.level, 0)
        self.assertEqual(skill.progress, 0.5)
        self.assertEqual(skill.unmodifiedPoints, 250)
        self.assertEqual(skill.unmodifiedLevel, 1)
        self.assertEqual(skill.unmodifiedProgress, 0.0)


class TestSkillExtractorController(unittest.TestCase):

    def setUp(self):
        super(TestSkillExtractorController, self).setUp()
        self._next_skill_id = 1
        self.controller = SkillExtractorControllerTestImpl(EXTRACTOR_ITEM_ID)
        self.events = mock.Mock()
        self.controller.onUpdate.connect(self.events.on_update)
        self.controller.onSkillListUpdate.connect(self.events.on_skill_list_update)

    def test_get_no_skills(self):
        self.controller._mock_skill_list = []
        skills = self.controller.skills
        self.assertEqual(skills, [])

    def test_get_skills(self):
        self.controller._mock_skill_list = expected = [SKILL_R1_L0, SKILL_R1_L5]
        self.assertSkillListEqual(expected)

    def test_extract_nonexisting_skill(self):
        self.controller._mock_skill_list = []
        with self.assertRaises(SkillNotFoundError):
            self.controller.ExtractSkill(1)
        self.assertEqual(self.events.on_update.call_count, 0)

    def test_extract_untrained_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L0]
        with self.assertRaises(NoSkillpointsError):
            self.controller.ExtractSkill(SKILL_R1_L0['typeID'])
        self.assertEqual(self.events.on_update.call_count, 0)

    def test_extract_trained_level_zero_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L0_TRAINED]
        self.controller.ExtractSkill(SKILL_R1_L0_TRAINED['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L0_TRAINED['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L0_TRAINED).points, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L0_TRAINED).level, 0)

    def test_skill_extraction_events(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller.ExtractSkill(SKILL_R1_L1['typeID'])
        self.events.on_update.assert_called_once_with()
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()

    def test_extract_level_one_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller.ExtractSkill(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, 250)
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1).level, 0)
        self.events.on_update.assert_called_once_with()

    def test_extract_fully_extracted_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        with self.assertRaises(NoSkillpointsError):
            self.controller.ExtractSkill(SKILL_R1_L1['typeID'])

    def test_extract_level_five_skill_five_times(self):
        self.controller._mock_skill_list = [SKILL_R1_L5]
        self.controller.ExtractSkill(SKILL_R1_L5['typeID'])
        self.controller.ExtractSkill(SKILL_R1_L5['typeID'])
        self.controller.ExtractSkill(SKILL_R1_L5['typeID'])
        self.controller.ExtractSkill(SKILL_R1_L5['typeID'])
        self.controller.ExtractSkill(SKILL_R1_L5['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L5['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L5).points, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L5).level, 0)
        self.assertEqual(self.events.on_update.call_count, 5)

    def test_extract_level_two_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L2]
        self.controller.ExtractSkill(SKILL_R1_L2['typeID'])
        self.assertEqual(self.controller.extractedPoints, 1165)
        self.assertEqual(self.getSkill(SKILL_R1_L2).points, 250)
        self.assertEqual(self.getSkill(SKILL_R1_L2).level, 1)
        self.events.on_update.assert_called_once_with()

    def test_extract_trained_level_one_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_TRAINED]
        self.controller.ExtractSkill(SKILL_R1_L1_TRAINED['typeID'])
        self.assertEqual(self.controller.extractedPoints, 250)
        self.assertEqual(self.getSkill(SKILL_R1_L1_TRAINED).points, 250)
        self.assertEqual(self.getSkill(SKILL_R1_L1_TRAINED).level, 1)
        self.events.on_update.assert_called_once_with()

    def test_fully_extract_trained_level_one_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_TRAINED]
        self.controller.ExtractSkill(SKILL_R1_L1_TRAINED['typeID'])
        self.controller.ExtractSkill(SKILL_R1_L1_TRAINED['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L1_TRAINED['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1_TRAINED).points, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1_TRAINED).level, 0)
        self.assertEqual(self.events.on_update.call_count, 2)

    def test_extraction_skillpoint_goal(self):
        self.controller._mock_skill_list = [SKILL_R4_L5]
        self.controller.ExtractSkill(SKILL_R4_L5['typeID'])
        self.assertEqual(self.controller.extractedPoints, self.controller.SKILL_POINT_GOAL)
        self.assertEqual(self.getSkill(SKILL_R4_L5).points, 524000)
        self.assertEqual(self.getSkill(SKILL_R4_L5).level, 4)

    def test_extract_skill_with_goal_reached(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R10_L5]
        self.preExtract(SKILL_R10_L5)
        with self.assertRaises(GoalAlreadyReachedError):
            self.controller.ExtractSkill(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, self.controller.SKILL_POINT_GOAL)
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1).level, SKILL_R1_L1['level'])
        self.assertEqual(self.events.on_update.call_count, 0)

    def test_revert_unextracted_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        with self.assertRaises(SkillNotExtractedError):
            self.controller.Revert(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1).onUpdateHandler.call_count, 0)

    def test_revert_unextracted_skill_with_other_skill_extracted(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L5]
        self.preExtract(SKILL_R1_L1)
        with self.assertRaises(SkillNotExtractedError):
            self.controller.Revert(SKILL_R1_L5['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L5).points, SKILL_R1_L5['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L5).onUpdateHandler.call_count, 0)

    def test_revert_single_skill_level(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller.Revert(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, SKILL_R1_L1['sp'])
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()

    def test_revert_skill_after_extracting_other_different_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L5]
        self.preExtract(SKILL_R1_L1, SKILL_R1_L5)
        self.controller.Revert(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L5['sp'] - SKILL_R1_L4['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, SKILL_R1_L1['sp'])
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()
        self.assertEqual(self.getSkill(SKILL_R1_L5).points, SKILL_R1_L4['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L5).onUpdateHandler.call_count, 0)

    def test_revert_skill_after_extracting_it_twice(self):
        self.controller._mock_skill_list = [SKILL_R1_L5]
        self.preExtract(SKILL_R1_L5, SKILL_R1_L5)
        self.controller.Revert(SKILL_R1_L5['typeID'])
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L5['sp'] - SKILL_R1_L4['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L5).points, SKILL_R1_L4['sp'])
        self.getSkill(SKILL_R1_L5).onUpdateHandler.assert_called_once_with()

    def test_extract_required_skill_level(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1, SKILL_R1_L1]
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L1['typeID'])

    def test_extract_required_skill_nonrequired_level(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L5, SKILL_R1_L1]
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L5).isRequired)
        self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L5['typeID'])
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L5).isRequired)

    def test_extract_required_half_trained_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1_TRAINED, SKILL_R1_L1]
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L1_TRAINED).isRequired)
        self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L1_TRAINED['typeID'])
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1_TRAINED).isRequired)

    def test_extracting_dependent_skill_unlocks_requirements(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1, SKILL_R1_L1]
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)
        self.controller.ExtractSkill(SKILL_R1_L1['typeID'])
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)

    def test_extract_required_skill_after_dependent_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1, SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L1['typeID'])
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)
        self.getSkill(SKILL_R1_L1_PREREQ_L1).onUpdateHandler.assert_called_once_with()

    def test_revert_updates_required_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1_TRAINED, SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1_PREREQ_L1_TRAINED)
        self.controller.Revert(SKILL_R1_L1_PREREQ_L1_TRAINED['typeID'])
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L1_TRAINED).isRequired)

    def test_revert_updates_dependent_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1, SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller.Revert(SKILL_R1_L1['typeID'])
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()

    def test_revert_dependent_skill_also_reverts_required_skills(self):
        self.controller._mock_skill_list = [SKILL_R1_L1_PREREQ_L1, SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1, SKILL_R1_L1_PREREQ_L1)
        self.controller.Revert(SKILL_R1_L1['typeID'])
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1).points, SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L1_PREREQ_L1).points, SKILL_R1_L1_PREREQ_L1['sp'])
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()
        self.getSkill(SKILL_R1_L1_PREREQ_L1).onUpdateHandler.assert_called_once_with()

    def test_revert_dependent_skill_also_reverts_whole_chain_of_required_skills(self):
        SKILL_A = {'typeID': 100,
         'rank': 1.0,
         'sp': SP_R1_L1,
         'level': 1,
         'requirements': {101: 1}}
        SKILL_B = {'typeID': 101,
         'rank': 1.0,
         'sp': SP_R1_L1,
         'level': 1,
         'requirements': {102: 1},
         'dependencies': {100: 1}}
        SKILL_C = {'typeID': 102,
         'rank': 1.0,
         'sp': SP_R1_L1,
         'level': 1,
         'dependencies': {101: 1}}
        self.controller._mock_skill_list = [SKILL_A, SKILL_B, SKILL_C]
        self.preExtract(SKILL_A, SKILL_B, SKILL_C)
        self.controller.Revert(SKILL_A['typeID'])
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(self.getSkill(SKILL_A).points, SKILL_A['sp'])
        self.assertEqual(self.getSkill(SKILL_B).points, SKILL_B['sp'])
        self.assertEqual(self.getSkill(SKILL_C).points, SKILL_C['sp'])
        self.getSkill(SKILL_A).onUpdateHandler.assert_called_once_with()
        self.getSkill(SKILL_B).onUpdateHandler.assert_called_once_with()
        self.getSkill(SKILL_C).onUpdateHandler.assert_called_once_with()

    def test_revert_dependent_skill_reverts_requirements_to_minimum_required_level(self):
        SKILL_B = self.addSkill(points=SP_R1_L3)
        SKILL_A = self.addSkill(points=SP_R1_L1, requirements=[(SKILL_B, 2)])
        self.preExtract(SKILL_A, SKILL_B, SKILL_B)
        self.controller.Revert(SKILL_A.typeID)
        self.assertEqual(SKILL_B.level, 2)
        self.assertEqual(SKILL_B.points, SP_R1_L2)
        SKILL_A.onUpdateHandler.assert_called_once_with()
        SKILL_B.onUpdateHandler.assert_called_once_with()

    def test_commit_with_nothing_extracted(self):
        with self.assertRaises(NotEnoughExtractedError):
            self.controller.Commit()
        self.assertFalse(self.controller.isCompleted)

    def test_commit_with_less_than_needed_extracted(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller.ExtractSkill(SKILL_R1_L1['typeID'])
        with self.assertRaises(NotEnoughExtractedError):
            self.controller.Commit()
        self.assertFalse(self.controller.isCompleted)

    def test_commit_with_enough_extracted(self):
        self.controller._mock_skill_list = [SKILL_R10_L5]
        self.preExtract(SKILL_R10_L5)
        expected = {SKILL_R10_L5['typeID']: 500000}
        self.controller.Commit()
        self.assertTrue(self.controller.isCompleted)
        self.events.on_update.assert_called_once_with()
        self.assertEqual(self.controller._final_itemID, EXTRACTOR_ITEM_ID)
        self.assertDictEqual(self.controller._final_extracted_skills, expected)

    def test_commit_with_multiple_levels_of_a_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L5, SKILL_R10_L5]
        self.preExtract(SKILL_R1_L5, SKILL_R1_L5, SKILL_R1_L5, SKILL_R1_L5, SKILL_R1_L5, SKILL_R10_L5)
        expected = {SKILL_R1_L5['typeID']: 256000,
         SKILL_R10_L5['typeID']: 244000}
        self.controller.Commit()
        self.assertTrue(self.controller.isCompleted)
        self.events.on_update.assert_called_once_with()
        self.assertEqual(self.controller._final_itemID, EXTRACTOR_ITEM_ID)
        self.assertDictEqual(self.controller._final_extracted_skills, expected)

    def test_skills_in_queue_are_set_as_such(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L2]
        self.controller._mock_skill_queue = [(SKILL_R1_L1['typeID'], 2)]
        self.assertTrue(self.getSkill(SKILL_R1_L1).isQueued)
        self.assertFalse(self.getSkill(SKILL_R1_L2).isQueued)

    def test_extract_skill_in_queue(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller._mock_skill_queue = [(SKILL_R1_L1['typeID'], 2)]
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(SKILL_R1_L1['typeID'])

    def test_queue_updated(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L2]
        self.assertFalse(self.getSkill(SKILL_R1_L1).isQueued)
        self.assertFalse(self.getSkill(SKILL_R1_L2).isQueued)
        self.controller._mock_skill_queue = [(SKILL_R1_L1['typeID'], 2)]
        self.controller.OnSkillQueueUpdated()
        self.assertTrue(self.getSkill(SKILL_R1_L1).isQueued)
        self.assertFalse(self.getSkill(SKILL_R1_L2).isQueued)
        self.getSkill(SKILL_R1_L1).onUpdateHandler.assert_called_once_with()

    def test_unextracted_skill_added_to_queue(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L2]
        self.preExtract(SKILL_R1_L1)
        self.controller._mock_skill_queue = [(SKILL_R1_L2['typeID'], 3)]
        self.controller.OnSkillQueueUpdated()
        self.assertEqual(self.controller.extractedPoints, SKILL_R1_L1['sp'])
        self.assertEqual(self.events.on_update.call_count, 0)
        self.assertEqual(self.getSkill(SKILL_R1_L1).onUpdateHandler.call_count, 0)
        self.getSkill(SKILL_R1_L2).onUpdateHandler.assert_called_once_with()

    def test_extracted_skill_added_to_queue(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller._mock_skill_queue = [(SKILL_R1_L1['typeID'], 2)]
        self.controller.OnSkillQueueUpdated()
        skill = self.getSkill(SKILL_R1_L1)
        self.assertEqual(skill.level, SKILL_R1_L1['level'])
        self.assertEqual(skill.points, SKILL_R1_L1['sp'])
        skill.onUpdateHandler.assert_called_once_with()
        self.assertEqual(self.controller.extractedPoints, 0)
        self.events.on_update.assert_called_once_with()

    def test_queued_dependent_skill_prevents_requirement_from_being_extracted(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R1_L1_PREREQ_L1]
        self.controller._mock_skill_queue = [(SKILL_R1_L1['typeID'], 2)]
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L1['typeID'])
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)

    def test_untrained_queued_dependent_skill_prevents_requirements_being_extracted(self):
        self.controller._mock_skill_list = [SKILL_R1_L0, SKILL_R1_L1_PREREQ_L1]
        self.controller._mock_skill_queue = [(SKILL_R1_L0['typeID'], 1)]
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(SKILL_R1_L1_PREREQ_L1['typeID'])
        self.assertTrue(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)

    def test_dependent_skill_in_queue_removed_from_queue(self):
        self.controller._mock_skill_list = [SKILL_R1_L0, SKILL_R1_L1_PREREQ_L1]
        self.controller._mock_skill_queue = [(SKILL_R1_L0['typeID'], 1)]
        self.controller.skills
        self.controller._mock_skill_queue = []
        self.controller.OnSkillQueueUpdated()
        self.assertFalse(self.getSkill(SKILL_R1_L1_PREREQ_L1).isRequired)
        self.getSkill(SKILL_R1_L1_PREREQ_L1).onUpdateHandler.assert_called_once_with()

    def test_dependent_untrained_skill_added_to_queue_resets_requirements(self):
        self.controller._mock_skill_list = [SKILL_R1_L0, SKILL_R1_L1_PREREQ_L1]
        self.preExtract(SKILL_R1_L1_PREREQ_L1)
        self.controller._mock_skill_queue = [(SKILL_R1_L0['typeID'], 1)]
        self.controller.OnSkillQueueUpdated()
        self.assertEqual(self.getSkill(SKILL_R1_L1_PREREQ_L1).points, SKILL_R1_L1_PREREQ_L1['sp'])
        self.getSkill(SKILL_R1_L1_PREREQ_L1).onUpdateHandler.assert_called_once_with()

    def test_dependent_skill_added_to_queue_reverts_chain_of_required_skills(self):
        SKILL_A = self.addSkill(points=SP_R1_L1)
        SKILL_B = self.addSkill(points=SP_R1_L1, requirements=[(SKILL_A, 1)])
        SKILL_C = self.addSkill(points=SP_R1_L1, requirements=[(SKILL_B, 1)])
        self.preExtract(SKILL_C, SKILL_B, SKILL_A)
        self.controller._mock_skill_queue = [(SKILL_C.typeID, 2)]
        self.controller.OnSkillQueueUpdated()
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(SKILL_A.points, SP_R1_L1)
        self.assertEqual(SKILL_B.points, SP_R1_L1)
        self.assertEqual(SKILL_C.points, SP_R1_L1)
        SKILL_A.onUpdateHandler.assert_called_once_with()
        SKILL_B.onUpdateHandler.assert_called_once_with()
        SKILL_C.onUpdateHandler.assert_called_once_with()

    def test_skill_trained(self):
        self.controller._mock_skill_list = [SKILL_R1_L0]
        self.controller.OnSkillTrained(SKILL_R1_L0['typeID'], SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L0).points, SKILL_R1_L1['sp'])
        self.assertEqual(self.getSkill(SKILL_R1_L0).level, 1)
        self.assertEqual(self.events.on_update.call_count, 0)
        self.getSkill(SKILL_R1_L0).onUpdateHandler.assert_called_once_with()

    def test_extracted_skill_trained(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller.OnSkillTrained(SKILL_R1_L1['typeID'], SKILL_R1_L2['sp'])
        skill = self.getSkill(SKILL_R1_L1)
        self.assertEqual(skill.points, SKILL_R1_L2['sp'])
        self.assertEqual(skill.unmodifiedPoints, skill.points)
        self.assertEqual(self.controller.extractedPoints, 0)
        self.events.on_update.assert_called_once_with()
        skill.onUpdateHandler.assert_called_once_with()

    def test_extracted_skill_removed(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller.OnSkillTrained(SKILL_R1_L1['typeID'], -1)
        self.assertEqual(self.controller.extractedPoints, 0)
        self.events.on_update.assert_called_once_with()

    def test_unknown_skill_trained(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller.skills
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R4_L5]
        self.controller.OnSkillTrained(SKILL_R4_L5['typeID'], SKILL_R4_L5['sp'])
        self.assertSkillListEqual([SKILL_R1_L1, SKILL_R4_L5])
        self.events.on_update.assert_called_once_with()
        self.events.on_skill_list_update.assert_called_once_with()

    def test_skill_removed(self):
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R4_L5]
        self.controller.skills
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.controller.OnSkillTrained(SKILL_R4_L5['typeID'], -1)
        self.assertSkillListEqual([SKILL_R1_L1])
        self.events.on_update.assert_called_once_with()
        self.events.on_skill_list_update.assert_called_once_with()

    def test_skill_list_update_with_extracted_skill(self):
        self.controller._mock_skill_list = [SKILL_R1_L1]
        self.preExtract(SKILL_R1_L1)
        self.controller._mock_skill_list = [SKILL_R1_L1, SKILL_R4_L5]
        self.controller.OnSkillTrained(SKILL_R4_L5['typeID'], SKILL_R4_L5['sp'])
        skill = self.getSkill(SKILL_R1_L1)
        self.assertEqual(skill.points, 0)

    def test_restricted_skill_properties(self):
        skill_a = self.addSkill(points=SP_R1_L1, restrictedLevel=1)
        skill_b = self.addSkill(points=SP_R1_L2, restrictedLevel=1)
        self.controller.skills
        self.assertTrue(skill_a.isRestricted)
        self.assertFalse(skill_b.isRestricted)

    def test_extract_restricted_skill(self):
        restricted_skill = self.addSkill(points=SP_R1_L1, restrictedLevel=1)
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(restricted_skill.typeID)
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(restricted_skill.points, SP_R1_L1)
        self.assertEqual(restricted_skill.onUpdateHandler.call_count, 0)

    def test_extract_restricted_skill_of_higher_level(self):
        restricted_skill = self.addSkill(points=SP_R1_L2, restrictedLevel=1)
        self.controller.ExtractSkill(restricted_skill.typeID)
        with self.assertRaises(SkillLockedError):
            self.controller.ExtractSkill(restricted_skill.typeID)
        self.assertEqual(self.controller.extractedPoints, SP_R1_L2 - SP_R1_L1)
        self.assertEqual(restricted_skill.points, SP_R1_L1)
        restricted_skill.onUpdateHandler.assert_called_once_with()

    def test_revert_extracted_restricted_skill(self):
        restricted_skill = self.addSkill(points=SP_R1_L2, restrictedLevel=1)
        self.preExtract(restricted_skill)
        self.controller.Revert(restricted_skill.typeID)
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertFalse(restricted_skill.isRestricted)
        self.assertEqual(restricted_skill.points, SP_R1_L2)

    def test_on_restrictions_updated_skill_properties_are_updated(self):
        skill_a = self.addSkill(points=SP_R1_L1)
        skill_b = self.addSkill(points=SP_R1_L1, restrictedLevel=1)
        self.controller.skills
        self.restrictSkill(skill_a, 1)
        self.restrictSkill(skill_b, 0)
        self.controller.OnSkillRestrictionsUpdated()
        self.assertTrue(skill_a.isRestricted)
        self.assertFalse(skill_b.isRestricted)

    def test_on_restrictions_updated_restricted_skills_are_reverted(self):
        skill = self.addSkill(points=SP_R1_L1)
        self.preExtract(skill)
        self.restrictSkill(skill, 1)
        self.controller.OnSkillRestrictionsUpdated()
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertTrue(skill.isRestricted)
        self.assertEqual(skill.points, SP_R1_L1)
        skill.onUpdateHandler.assert_called_once_with()
        self.events.on_update.assert_called_once_with()

    def test_on_restrictions_updated_restricted_skills_are_reverted_up_to_restricted_level(self):
        skill = self.addSkill(points=SP_R1_L2)
        self.preExtract(skill, skill)
        self.restrictSkill(skill, 1)
        self.controller.OnSkillRestrictionsUpdated()
        self.assertEqual(self.controller.extractedPoints, SP_R1_L2 - SP_R1_L1)
        self.assertTrue(skill.isRestricted)
        self.assertEqual(skill.points, SP_R1_L1)
        skill.onUpdateHandler.assert_called_once_with()
        self.events.on_update.assert_called_once_with()

    def test_on_restrictions_updated_restricted_skills_and_requirements_are_reverted(self):
        skill_a = self.addSkill(points=SP_R1_L1)
        skill_b = self.addSkill(points=SP_R1_L1, requirements=[(skill_a, 1)])
        self.preExtract(skill_b, skill_a)
        self.restrictSkill(skill_b, 1)
        self.controller.OnSkillRestrictionsUpdated()
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(skill_a.points, SP_R1_L1)
        self.assertEqual(skill_b.points, SP_R1_L1)
        self.assertTrue(skill_a.isRequired)
        self.assertTrue(skill_b.isRestricted)
        skill_a.onUpdateHandler.assert_called_once_with()
        skill_b.onUpdateHandler.assert_called_once_with()
        self.events.on_update.assert_called_once_with()

    def test_extracted_restricted_skill_added_to_queue(self):
        skill = self.addSkill(points=SP_R1_L2, restrictedLevel=1)
        self.preExtract(skill)
        self.controller._mock_skill_queue = [(skill.typeID, 3)]
        self.controller.OnSkillQueueUpdated()
        self.assertEqual(self.controller.extractedPoints, 0)
        self.assertEqual(skill.points, SP_R1_L2)
        self.assertTrue(skill.isQueued)
        self.assertFalse(skill.isRestricted)
        skill.onUpdateHandler.assert_called_once_with()
        self.events.on_update.assert_called_once_with()

    def test_restricted_skill_trained(self):
        skill = self.addSkill(points=SP_R1_L1, restrictedLevel=1)
        self.controller.skills
        updated_skill = self.addSkill(typeID=skill.typeID, points=SP_R1_L2)
        self.controller.OnSkillTrained(skill.typeID, SP_R1_L2)
        self.assertFalse(updated_skill.isRestricted)

    def assertSkillListEqual(self, expected):
        skills = self.controller.skills
        sorted_skills = sorted(skills, key=lambda s: s.typeID)
        sorted_expected = sorted(expected, key=lambda e: e['typeID'])
        self.assertEqual(len(skills), len(expected))
        for skill, expected_skill in izip(sorted_skills, sorted_expected):
            self.assertEqual(skill.typeID, expected_skill['typeID'])
            self.assertEqual(skill.points, expected_skill['sp'])
            self.assertEqual(skill.level, expected_skill['level'])
            self.assertEqual(skill.rank, expected_skill['rank'])

    def addSkill(self, typeID = None, points = SP_R1_L1, rank = 1.0, requirements = None, restrictedLevel = None):
        if typeID is None:
            typeID = self._next_skill_id
            self._next_skill_id += 1
        skill = SkillFixture(typeID=typeID, points=points, rank=rank)
        self.controller._mock_skill_list = filter(lambda s: s.typeID != typeID, self.controller._mock_skill_list)
        self.controller._mock_skill_list.append(skill)
        requirements = requirements or []
        for requiredSkill, requiredLevel in requirements:
            skill._requirements[requiredSkill.typeID] = requiredLevel
            requiredSkill._dependencies[skill.typeID] = requiredLevel

        if restrictedLevel is not None:
            self.restrictSkill(skill, restrictedLevel)
        return skill

    def restrictSkill(self, skill, level):
        if level == 0:
            del self.controller._mock_skill_restrictions[skill.typeID]
        else:
            self.controller._mock_skill_restrictions[skill.typeID] = level

    def getSkill(self, target):
        skills = self.controller.skills
        for skill in skills:
            if skill.typeID == target['typeID']:
                return skill

        self.fail('Skill with ID %s not found in the controller' % target['typeID'])

    def preExtract(self, *skills):
        for skill in skills:
            try:
                typeID = skill.typeID
            except AttributeError:
                typeID = skill['typeID']

            self.controller.ExtractSkill(typeID)

        for skill in self.controller.skills:
            skill.onUpdateHandler.reset_mock()

        self.events.on_update.reset_mock()


def __SakeReloadHook():
    try:
        import sys
        suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
        unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite)
    except:
        import log
        log.LogException()
