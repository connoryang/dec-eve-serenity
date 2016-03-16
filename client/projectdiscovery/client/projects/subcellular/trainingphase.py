#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\trainingphase.py
__author__ = 'ru.Hjalti'
import copy
import math
import random
import uthread
import uicontrols
import logging
import uiprimitives
import localization
import carbonui.const as uiconst
from taskimages import TaskImage
from rewardsview import RewardsView
from resultwindow import ResultWindow
from info import INFO as PROJECT_INFO
from processingview import ProcessingView
from projectdiscovery.client import const
from carbonui.uianimations import animations
from categoryselector import CategorySelector
from projectdiscovery.client.util.dialogue import Dialogue
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
LEVEL_ZERO = 'starter'
LEVEL_ONE = 'levelOne'
LEVEL_TWO = 'levelTwo'
LEVEL_THREE = 'levelThree'
LEVEL_FOUR = 'levelFour'
LEVEL_FIVE = 'levelFive'
LEVEL_SIX = 'negative'
LEVEL_SEVEN = 'unspecific'
LEVEL_COUNT = {LEVEL_ZERO: 1,
 LEVEL_ONE: 1,
 LEVEL_TWO: 1,
 LEVEL_THREE: 1,
 LEVEL_FOUR: 1,
 LEVEL_FIVE: 1,
 LEVEL_SIX: 1}
logger = logging.getLogger(__name__)

def _nested_categories_from_json(categories):
    keyed = {cat['id']:cat for cat in categories}
    nested = {}
    for cat in categories:
        cat['children'] = []
        cat['selected'] = False
        if not cat['parentId']:
            nested[cat['id']] = cat
        elif cat['parentId'] in keyed:
            keyed[cat['parentId']]['children'].append(cat)

    return nested


@eventlistener()

class TrainingPhase(uiprimitives.Container):
    PROJECT_ID = 16
    MAX_CATEGORIES = 9

    def ApplyAttributes(self, attributes):
        super(TrainingPhase, self).ApplyAttributes(attributes)
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.selection = []
        self.isGreeting = False
        self.level = LEVEL_ZERO
        self.taskDict = copy.deepcopy(const.TrainingTasks)
        self.taskList = copy.deepcopy(self.taskDict[self.level])
        self.levelCount = copy.deepcopy(LEVEL_COUNT)
        self.finishedLevelCount = 1
        self.playerState = attributes.get('playerState')
        self.setup_layout()
        self.task_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TaskLabel') + ' ' + str(self.finishedLevelCount) + '/' + str(self.get_total_level_count()))

    def setup_layout(self):
        self.dialogue_container = uiprimitives.Container(name='dialogue_container', parent=self.parent, idx=0)
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.CENTERLEFT, height=400, width=475)
        self.task_label = EveCaptionLarge(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TaskLabel'), top=-30, color=(0.48, 0.48, 0.48, 1))
        self.training_task_image = TaskImage(label=const.Texts.TaskImageLabel, parent=self.left_main_container, align=uiconst.CENTER, width=370, height=410)
        self.result_window = ResultWindow(name='ResultWindow', parent=self.parent, align=uiconst.TOALL, opacity=0, isTrainingPhase=True, taskImage=self.training_task_image)
        self.rewards_view = RewardsView(parent=self.parent, opacity=0, playerState=self.playerState)
        self.rewards_view.isTraining = True
        self.rewards_view.tutorial_completed = False
        self.processing_view = ProcessingView(parent=self.parent, opacity=0)
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.CENTERRIGHT, width=404, height=385)
        self.training_category_selector = CategorySelector(categories=_nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_HIDDEN)
        self.main_button_container = uiprimitives.Container(name='main_button_container', parent=self, align=uiconst.CENTERBOTTOM, width=355, height=53, top=3, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.submit_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.submit_button = uicontrols.Button(name='submitButton', parent=self.submit_button_container, align=uiconst.CENTER, label='Submit', fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.submit_training_solution())
        uiprimitives.Sprite(parent=self.submit_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.submit_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self.task_id = uicontrols.Label(parent=self, align=uiconst.BOTTOMRIGHT, height=20, opacity=0.5, left=10)

    def get_total_level_count(self):
        count = 0
        for level in LEVEL_COUNT:
            count += 1 + (1 - LEVEL_COUNT[level])

        return count

    def get_tutorial_steps(self):
        return [{'owner': self.training_task_image.images_container,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageText')},
         {'owner': self.training_category_selector,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionText')},
         {'owner': self.training_category_selector.super_categories[0],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusText')},
         {'owner': self.training_category_selector.super_categories[1],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplasmHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplasmText')},
         {'owner': self.training_category_selector.super_categories[2],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryText')},
         {'owner': self.training_category_selector.super_categories[3],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableText')},
         {'owner': self.training_task_image.colorFilterContainer,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/ChannelFilterHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/ChannelFilterText')},
         {'owner': self.main_button_container,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmitButtonHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmitButtonText')}]

    def start(self):
        self.taskDict = copy.deepcopy(const.TrainingTasks)
        self.taskList = copy.deepcopy(self.taskDict[self.level])
        self.levelCount = copy.deepcopy(LEVEL_COUNT)
        self.new_training_task()
        self.disable_ui()
        Dialogue(name='greetingDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=340, messageText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingText'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingLabel'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingButton'), toHide=self, isTutorial=True)

    def close(self):
        self.result_window.Close()
        self.processing_view.Close()
        self.training_task_image.Flush()
        self.training_task_image.Close()
        self.training_category_selector.Close()
        self.rewards_view.Close()
        self.Close()

    def new_training_task(self):
        self.training_task_image.SetParent(self.left_main_container)
        self.selection = []
        task_number = random.choice(self.taskList.keys())
        self.task = self.service.new_training_task(task_number)
        if 'message' in self.task:
            logger.error('Trainingphase.py: On function new_training_task() ' + str(self.task))
            return
        self.task_id.SetText(self.task['taskId'])
        del self.taskList[task_number]
        relevant_categories = list(self.task['solution'])
        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id in self.task['solution']:
                    relevant_categories.extend(sub.excludes)

        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id in self.task['solution']:
                    temp_list = list(super_cat.sub_categories)
                    temp_list.remove(sub)
                    max_cats = 2
                    if len(temp_list) < max_cats:
                        max_cats = len(temp_list)
                    for n in range(0, max_cats):
                        item = random.choice(temp_list)
                        relevant_categories.append(item.id)
                        temp_list.remove(item)

                    break

        for super_cat in self.training_category_selector.super_categories:
            for sub in super_cat.sub_categories:
                if sub.id not in relevant_categories:
                    sub.set_unavailable()
                    sub.set_unclickable()
                else:
                    sub.set_clickable()
                    sub.set_available()

        task_information = self.service.get_task_information(self.task['taskId'], 'channelGreenBlueRed', self.task['assetsSecurityPass'])
        self.task_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/TaskLabel') + ' ' + str(self.finishedLevelCount) + '/' + str(self.get_total_level_count()))
        sm.ScatterEvent(const.Events.NewTask, task_information, self.task['assetsSecurityPass'])

    @on_event(const.Events.MainImageLoaded)
    def cascade_in(self):
        self.training_category_selector.state = uiconst.UI_NORMAL
        self.training_category_selector.cascade_categories_in()

    def open_error_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedErrorMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/NoCategorySelectedHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def open_too_many_categories_selected_dialogue(self):
        self.disable_ui()
        self.dialogue = Dialogue(name='ErrorDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=215, messageText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/TooManyCategoriesHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/NotificationHeader'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)

    def disable_ui(self):
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED

    @on_event(const.Events.EnableUI)
    def enable_ui(self):
        self.training_task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL

    def submit_training_solution(self):
        if not self.selection:
            self.open_error_dialogue()
            return
        self.levelCount[self.level] -= 1
        self.finishedLevelCount += 1
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        classification = list(set([ cat['id'] for cat in self.selection if not cat['excluded'] ]))
        self.result = {'playerSelection': classification,
         'task': {'solution': self.task['solution']}}
        self.result_window.assign_result(self.result)
        self.training_category_selector.cascade_categories_out()
        self.training_category_selector.state = uiconst.UI_DISABLED
        animations.FadeOut(self.main_button_container)
        animations.FadeOut(self.training_task_image.colorFilterContainer)
        animations.FadeOut(self.task_label)
        self.training_task_image.start_transmission_animation()
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED
        self.increment_level()

    @on_event(const.Events.TransmissionFinished)
    def show_category_selector(self):
        self.left_main_container.state = uiconst.UI_NORMAL
        self.result_window.open()
        animations.FadeIn(self.training_task_image.colorFilterContainer)

    def tutorial_finished(self):
        if self.levelCount[LEVEL_SIX] <= 0:
            return True

    @on_event(const.Events.ContinueFromTrainingResult)
    def on_training_result_closed(self):
        if self.tutorial_finished():
            if self.service.give_tutorial_rewards():
                result = {'XP_Reward': 1000,
                 'LP_Reward': 0,
                 'ISK_Reward': 0,
                 'playerState': self.service.get_player_state(),
                 'player': {'score': 0.5},
                 'isTraining': True}
                self.rewards_view.tutorial_completed = True
                sm.ScatterEvent(const.Events.CloseResult, result)
                self.processing_view.start()
                settings.char.ui.Set('loadStatisticsAfterSubmission', True)
            else:
                sm.ScatterEvent(const.Events.ProjectDiscoveryStarted, True)
            self.Close()
        else:
            self.training_task_image.reset()
            uthread.new(self.new_training_task)
            animations.FadeIn(self, duration=1)
            animations.FadeIn(self.main_button_container)
            animations.FadeIn(self.training_task_image.colorFilterContainer)
            animations.FadeIn(self.task_label, timeOffset=1)
            self.training_task_image.state = uiconst.UI_NORMAL
            self.left_main_container.state = uiconst.UI_NORMAL
            self.category_container.state = uiconst.UI_NORMAL
            self.main_button_container.state = uiconst.UI_NORMAL

    def increment_level(self):
        if self.levelCount[self.level] <= 0:
            if self.level == LEVEL_ZERO:
                self.level = LEVEL_ONE
            elif self.level == LEVEL_ONE:
                self.level = LEVEL_TWO
            elif self.level == LEVEL_TWO:
                self.level = LEVEL_THREE
            elif self.level == LEVEL_THREE:
                self.level = LEVEL_FOUR
            elif self.level == LEVEL_FOUR:
                self.level = LEVEL_FIVE
            elif self.level == LEVEL_FIVE:
                self.level = LEVEL_SIX
            self.taskList = copy.deepcopy(self.taskDict[self.level])

    def _update_excluded(self, excluder):
        excluded = set()
        for cat in self.selection:
            excluded.update(cat.get('excludes', []))

        sm.ScatterEvent(const.Events.ExcludeCategories, excluder, excluded)

    @on_event(const.Events.CategoryChanged)
    def on_category_changed(self, hexagon):
        sm.GetService('audio').SendUIEvent(const.Sounds.CategorySelectPlay)
        if hexagon.category['selected']:
            if len(self.selection) > self.MAX_CATEGORIES:
                hexagon.set_unselected()
                self.open_too_many_categories_selected_dialogue()
                return
            self.selection.append(hexagon.category)
        elif hexagon.category in self.selection:
            self.selection.remove(hexagon.category)
        self._update_excluded(hexagon.category['id'])
