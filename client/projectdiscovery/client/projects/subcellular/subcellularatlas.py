#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\subcellularatlas.py
import time
import math
import uthread
import logging
import uicontrols
import uiprimitives
import localization
import carbonui.const as uiconst
from info import INFO as PROJECT_INFO
from projectdiscovery.client import const
from carbonui.uianimations import animations
from categoryselector import CategorySelector
from projectdiscovery.client.util.dialogue import Dialogue
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from projectdiscovery.client.projects.subcellular.taskimages import TaskImage
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.client.projects.subcellular.rewardsview import RewardsView
from projectdiscovery.client.projects.subcellular.resultwindow import ResultWindow
from projectdiscovery.client.projects.subcellular.processingview import ProcessingView
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

class SubcellularAtlas(uiprimitives.Container):
    PROJECT_ID = 16
    MAX_CATEGORIES = 9

    def ApplyAttributes(self, attributes):
        super(SubcellularAtlas, self).ApplyAttributes(attributes)
        self.task_time = None
        self.solution = []
        self.tutorial = None
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.submitting = False
        self.playerState = attributes.get('playerState')
        self.dialogue_container = uiprimitives.Container(name='dialogue_container', parent=self.parent, idx=0)
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.CENTERLEFT, height=400, width=475)
        self.task_label = EveCaptionLarge(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/TaskLabel'), top=-30, color=(0.48, 0.48, 0.48, 1))
        self.task_image = TaskImage(label=const.Texts.TaskImageLabel, parent=self.left_main_container, align=uiconst.CENTER, width=370, height=410)
        self.result_window = ResultWindow(name='ResultWindow', parent=self.parent, align=uiconst.TOALL, opacity=0, isTrainingPhase=False)
        self.rewards_view = RewardsView(parent=self.parent, opacity=0, align=uiconst.TOALL, playerState=self.playerState)
        self.processing_view = ProcessingView(parent=self.parent, opacity=0)
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.CENTERRIGHT, width=404, height=385)
        self.category_selector = CategorySelector(categories=_nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_DISABLED)
        self.main_button_container = uiprimitives.Container(name='main_button_container', parent=self, align=uiconst.CENTERBOTTOM, width=355, height=53, top=3, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.submit_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.submit_button = uicontrols.Button(name='SubcellularSubmitButton', parent=self.submit_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/SubmitButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.submit_solution())
        uiprimitives.Sprite(parent=self.submit_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.submit_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        self.task_id = uicontrols.Label(parent=self, align=uiconst.BOTTOMRIGHT, height=20, opacity=0.5, left=10)

    def start(self, show_dialogue):
        if show_dialogue:
            self.disable_ui()
            Dialogue(name='finishedTutorialDialogue', parent=self.dialogue_container, align=uiconst.CENTER, width=450, height=330, messageText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FinishedMessage'), messageHeaderText=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FinishedHeader'), label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/GreetingLabel'), buttonLabel=localization.GetByLabel('UI/ProjectDiscovery/ErrorButton'), toHide=self)
        uthread.new(self.new_task)

    def new_task(self):
        self.solution = []
        self.task = self.service.new_task(self.PROJECT_ID)
        self.task_time = self._time()
        self.category_selector.cascade_categories_in()
        if 'message' in self.task:
            logger.error('Subcellularatlas.py: On function new_task() ' + self.task)
            return
        task_information = self.service.get_task_information(self.task['taskId'], 'channelGreenBlueRed', self.task['assetsSecurityPass'])
        self.task_id.SetText(self.task['taskId'])
        self.category_selector.state = uiconst.UI_NORMAL
        settings.char.ui.Set('UpdateAccInfo', True)
        sm.ScatterEvent(const.Events.NewTask, task_information, self.task['assetsSecurityPass'])

    def _update_excluded(self, excluder):
        excluded = set()
        for cat in self.solution:
            if '*' in cat.get('excludes'):
                excluded.update(cat.get('excludes', []))
            elif 12 in cat.get('excludes', []):
                excludes = list(cat.get('excludes', []))
                excludes.append(121)
                excludes.append(122)
                excludes.append(123)
                excluded.update(excludes, [])
            else:
                excluded.update(cat.get('excludes', []))

        sm.ScatterEvent(const.Events.ExcludeCategories, excluder, excluded)

    def _time(self):
        return int(time.time() * 1000)

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
        self.task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL

    def submit_solution(self):
        if self.submitting:
            return
        if not self.solution:
            self.open_error_dialogue()
            return
        self.submitting = True
        animations.FadeOut(self.main_button_container)
        animations.FadeOut(self.task_image.colorFilterContainer)
        animations.FadeOut(self.task_label)
        uthread.new(self.category_selector.cascade_categories_out)
        self.category_selector.state = uiconst.UI_DISABLED
        self.task_image.start_transmission_animation()
        classification = list(set([ cat['id'] for cat in self.solution if not cat['excluded'] ]))
        duration = self._time() - self.task_time
        self.result = self.service.post_classification(self.task, classification, duration)
        self.result['playerSelection'] = classification
        self.result_window.assign_result(self.result)
        if settings.char.ui.Get('loadStatisticsAfterSubmission'):
            sm.ScatterEvent('OnUpdateHeader')
            settings.char.ui.Set('loadStatisticsAfterSubmission', False)
        self.left_main_container.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.main_button_container.state = uiconst.UI_DISABLED
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)

    @on_event(const.Events.TransmissionFinished)
    def show_category_selector(self):
        self.left_main_container.state = uiconst.UI_NORMAL
        self.result_window.open()
        animations.FadeIn(self.task_image.colorFilterContainer)

    def get_tutorial_steps(self):
        return [{'owner': self.task_image.image_sprite,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SampleImageText')},
         {'owner': self.category_selector,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CategorySelectionText')},
         {'owner': self.category_selector.super_categories[0],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NucleusText')},
         {'owner': self.category_selector.super_categories[1],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplashHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/CytoplashText')},
         {'owner': self.category_selector.super_categories[2],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/PeripheryText')},
         {'owner': self.category_selector.super_categories[3],
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/NotIdentifiableText')}]

    @on_event(const.Events.CategoryChanged)
    def on_category_changed(self, hexagon):
        sm.GetService('audio').SendUIEvent(const.Sounds.CategorySelectPlay)
        if hexagon.category['selected']:
            if len(self.solution) > self.MAX_CATEGORIES:
                hexagon.set_unselected()
                self.open_too_many_categories_selected_dialogue()
                return
            self.solution.append(hexagon.category)
        elif hexagon.category in self.solution:
            self.solution.remove(hexagon.category)
        self._update_excluded(hexagon.category['id'])

    @on_event(const.Events.ContinueFromReward)
    def on_continue_from_reward(self):
        uthread.new(self.new_task)
        animations.FadeIn(self, duration=1)
        animations.FadeIn(self.main_button_container)
        animations.FadeIn(self.task_image.colorFilterContainer)
        animations.FadeIn(self.task_label)
        self.task_image.state = uiconst.UI_NORMAL
        self.left_main_container.state = uiconst.UI_NORMAL
        self.category_container.state = uiconst.UI_NORMAL
        self.main_button_container.state = uiconst.UI_NORMAL

    @on_event(const.Events.ContinueFromResult)
    def on_continue_from_result(self):
        self.submitting = False
        self.task_image.state = uiconst.UI_DISABLED
        animations.FadeOut(self, duration=0.4, callback=self.task_image.reset)
