#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\window.py
import math
import blue
import const
import uicls
import uthread
import trinity
import listentry
import datetime
import logging
import uicontrols
import uiprimitives
import localization
import carbonui.const as uiconst
from utillib import KeyVal
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbon.common.script.util.format import FmtAmt
from projectdiscovery.common.const import xpNeededForRank
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.eveWindow import Window
from projectdiscovery.client.util.tutorial import Tutorial
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from projectdiscovery.client.projects.subcellular.trainingphase import TrainingPhase
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from projectdiscovery.client.projects.subcellular.subcellularatlas import SubcellularAtlas
logger = logging.getLogger(__name__)

@eventlistener()

class ProjectDiscoveryWindow(Window):
    __guid__ = 'ProjectDiscoveryWindow'
    default_captionLabelPath = 'UI/Industry/Industry'
    default_descriptionLabelPath = 'UI/Industry/IndustryTooltip'
    default_caption = 'Project Discovery'
    default_windowID = 'ProjectDiscoveryWindow'
    default_iconNum = 'res:/UI/Texture/WindowIcons/projectdiscovery.png'
    default_topParentHeight = 0
    default_isStackable = False
    default_isCollapseable = False
    default_minSize = (875, 565)
    default_fixedWidth = 875
    default_fixedHeight = 565

    @on_event('OnWindowClosed')
    def on_window_closed(self, wndID, wndCaption, wndGUID):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)

    @on_event('OnWindowMinimized')
    def on_window_minimized(self, wnd):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)

    @on_event('OnWindowMaximized')
    def on_window_maximized(self, wnd, wasMinimized):
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)

    @on_event('OnProjectDiscoveryHeaderDragged')
    def on_drag_header(self):
        self._BeginDrag()

    @on_event('OnProjectDiscoveryMouseDownOnHeader')
    def on_mouse_down_header(self):
        self.dragMousePosition = (uicore.uilib.x, uicore.uilib.y)

    @on_event('OnProjectDiscoveryMouseEnterHeader')
    def on_mouse_enter_header(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_HASMENU)

    @on_event('OnProjectDiscoveryMouseExitHeader')
    def on_mouse_exit_header(self):
        uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)

    def ApplyAttributes(self, attributes):
        super(ProjectDiscoveryWindow, self).ApplyAttributes(attributes)
        self.isTraining = False
        self.isSubHistoryOpen = False
        self.projectdiscoverySvc = sm.RemoteSvc('ProjectDiscovery')
        settings.char.ui.Set('loadStatisticsAfterSubmission', False)
        self.training = None
        self.project = None
        self.tutorial = None
        self.oldScrollList = []
        self.playerState = self.projectdiscoverySvc.get_player_state()
        self.main = self.GetMainArea()
        uthread.new(self.setup_layout)
        uthread.new(self.show_background_grid)
        uthread.new(self.animate_background)

    def setup_layout(self):
        self.setup_side_panels()
        self.dialogue_container = uiprimitives.Container(name='dialogue_container', parent=self.main)
        self.project_container = uiprimitives.Container(name='ProjectContainer', parent=self.main, align=uiconst.TOALL)
        self.header = WindowHeader(parent=self.main.parent, align=uiconst.CENTERTOP, height=53, width=355, idx=0, top=2, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/headerBG.png', playerState=self.playerState)
        self.submissionHistoryContainer = uiprimitives.Container(name='submissionHistoryContainer', parent=self.project_container, width=270, align=uiconst.CENTERTOP, height=300, bgColor=(0, 0, 0, 0.8), opacity=0, top=-45, state=uiconst.UI_HIDDEN)
        uicontrols.Frame(parent=self.submissionHistoryContainer, color=(0.31, 0.31, 0.31, 1))
        EveLabelLargeBold(name='submissionHistoryLabel', parent=self.submissionHistoryContainer, align=uiconst.CENTERTOP, fontSize=24, text=localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryLabel'), top=10)
        self.submissionHistoryScroll = Scroll(name='submissionHistoryScroll', parent=self.submissionHistoryContainer, align=uiconst.CENTERTOP, id='submissionHistoryScrollID', width=250, height=250, bgColor=(0, 0, 0, 0.8), top=35)
        self.help_button = uicontrols.ButtonIcon(name='helpButton', parent=self.project_container, align=uiconst.BOTTOMLEFT, iconSize=22, width=22, height=22, texturePath='res:/UI/Texture/WindowIcons/question.png', func=lambda : self.start_tutorial())
        SetTooltipHeaderAndDescription(targetObject=self.help_button, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/HelpTutorialTooltip'))
        uthread.new(self.load_project)

    def setup_side_panels(self):
        uiprimitives.Sprite(parent=self.main, align=uiconst.CENTERRIGHT, width=14, height=416, top=-20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.main, align=uiconst.CENTERLEFT, width=14, height=416, top=-20, rotation=math.pi), align=uiconst.TOLEFT_NOPUSH, width=14, height=416, texturePath='res:/UI/Texture/classes/ProjectDiscovery/sideElement.png')

    def hide_submission_history(self):
        self.submissionHistoryContainer.state = uiconst.UI_HIDDEN

    def enable_submission_history_button(self):
        self.header.submissionHistoryButton.state = uiconst.UI_NORMAL

    def disable_submission_history_button(self):
        self.header.submissionHistoryButton.state = uiconst.UI_DISABLED

    def toggle_submission_history(self):
        if not self.isSubHistoryOpen:
            self.submissionHistoryContainer.state = uiconst.UI_NORMAL
            self.disable_submission_history_button()
            animations.MoveOutBottom(self.submissionHistoryContainer, amount=60, duration=0.85, curveType=uiconst.ANIM_OVERSHOT, callback=self.enable_submission_history_button)
            animations.FadeIn(self.submissionHistoryContainer, duration=0.5)
            self.isSubHistoryOpen = not self.isSubHistoryOpen
        else:
            self.disable_submission_history_button()
            animations.MoveOutTop(self.submissionHistoryContainer, amount=60, duration=0.5, callback=self.enable_submission_history_button)
            animations.FadeOut(self.submissionHistoryContainer, duration=0.3, callback=self.hide_submission_history)
            self.isSubHistoryOpen = not self.isSubHistoryOpen
            return
        scroll_list = self.header.get_scroll_content()
        if len(scroll_list) > len(self.oldScrollList):
            self.oldScrollList = scroll_list
            self.submissionHistoryScroll.Load(contentList=scroll_list, headers=(localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryHeaderLabel1'), localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryHeaderLabel2')), fixedEntryHeight=30)
        self.header.submissionHistoryButton.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/iconSubmissionsEmpty.png')

    def load_project(self):
        if not self.playerState.finishedTutorial:
            uthread.new(self.start_tutorial)
        else:
            uthread.new(self.start_project, False)

    @on_event(const.Events.ProjectDiscoveryStarted)
    def start_project(self, show_dialogue):
        if self.training:
            self.training.close()
            self.isTraining = False
        self.project = SubcellularAtlas(parent=self.project_container, playerState=self.playerState)
        self.project.start(show_dialogue)

    def start_tutorial(self):
        if self.project:
            self.project.result_window.Close()
            self.project.rewards_view.Close()
            self.project.processing_view.Close()
            self.project.Close()
            self.project = None
        if self.isTraining:
            return
        self.training = TrainingPhase(parent=self.project_container, playerState=self.playerState)
        self.isTraining = True
        self.training.start()

    @on_event(const.Events.StartTutorial)
    def play_ui_help(self):
        if not self.tutorial:
            self.tutorial = Tutorial()
            if self.isTraining:
                self.tutorial.add_steps(self.training.get_tutorial_steps())
            else:
                self.tutorial.add_steps(self.project.get_tutorial_steps())
            self.tutorial.add_steps(self.get_tutorial_steps())
        self.tutorial.start()

    @on_event(const.Events.QuitTutorial)
    def close_tutorial(self):
        self.tutorial = None

    def get_tutorial_steps(self):
        return [{'owner': self.header.rankIcon,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/RankIconHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/RankIconText')},
         {'owner': self.header.accuracyRatingContainer,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/AccuracyRatingHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/AccuracyRatingText')},
         {'owner': self.header.submissionHistoryButton,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmissionHistoryHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/SubmissionHistoryText')},
         {'owner': self.help_button,
          'header': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FooterButtonsHeader'),
          'text': localization.GetByLabel('UI/ProjectDiscovery/Subcellular/Tutorial/FooterButtonsText')}]

    def show_background_grid(self):
        self.gridContainer = uiprimitives.Container(name='gridContainer', parent=self.main, align=uiconst.TOALL, clipChildren=True)
        self.gridBackground = uiprimitives.Sprite(name='gridBackground', parent=self.gridContainer, align=uiconst.CENTER, pos=(0, 0, 874, 610), textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/gradient.png', texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexFieldBackground.png', spriteEffect=trinity.TR2_SFX_MODULATE, top=-10)
        self.result_background = uiprimitives.Sprite(name='gridBackgroundResult', parent=self.gridContainer, align=uiconst.CENTER, pos=(0, 0, 874, 610), textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/gradient.png', texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexFieldBackgroundResults.png', spriteEffect=trinity.TR2_SFX_MODULATE, opacity=0, top=-10)
        self.fill = Fill(name='backgroundFill', align=uiconst.TOALL, parent=self.main, color=(0.0, 0.0, 0.0, 0.5), padTop=-20, padLeft=2, padRight=2, padBottom=2)
        self.fillResult = Fill(name='backgroundFillResult', align=uiconst.TOALL, parent=self.main, color=(0.14, 0.21, 0.21, 0.5), padTop=-20, padLeft=2, padRight=2, padBottom=2, opacity=0)

    def animate_background(self):
        animations.FadeTo(self.gridBackground, duration=1, curveType=uiconst.ANIM_OVERSHOT5)

    def close_background_grid(self):
        self.gridContainer.Flush()
        self.gridContainer.Close()

    @on_event(const.Events.ResultReceived)
    def animate_result_background_in(self):
        animations.FadeOut(self.gridBackground, duration=0.5)
        animations.FadeIn(self.result_background, duration=1, curveType=uiconst.ANIM_OVERSHOT5)

    @on_event(const.Events.ContinueFromReward)
    def animate_normal_background(self):
        animations.FadeOut(self.result_background, duration=0.5)
        animations.FadeIn(self.gridBackground, duration=1, curveType=uiconst.ANIM_OVERSHOT5)

    @on_event(const.Events.ContinueFromTrainingResult)
    def animate_training_background(self):
        self.animate_normal_background()


@eventlistener()

class WindowHeader(uiprimitives.Container):
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        super(WindowHeader, self).ApplyAttributes(attributes)
        self.pdService = sm.RemoteSvc('ProjectDiscovery')
        self.playerState = attributes.get('playerState')
        self.experience = self.playerState.experience
        self.rank = self.playerState.rank
        self.totalNeededExperience = xpNeededForRank[self.rank + 1]
        self.full_needle_rotation = -4.7
        self.setup_layout()
        self.oldScoreBarLength = self.calculate_score_bar_length()
        self.oldUnscoredSubmissionsCount = 0
        self.submissionHistory = []
        if self.playerState.finishedTutorial and not settings.char.ui.Get('loadStatisticsAfterSubmission'):
            self.update_header()
        self.state = uiconst.UI_NORMAL

    def setup_layout(self):
        self.headerContainer = uiprimitives.Container(name='headerContainer', parent=self, align=uiconst.CENTERTOP, height=34, width=230)
        self.scoreBarContainer = uiprimitives.Container(name='scoreBarContainer', parent=self, align=uiconst.CENTERBOTTOM, height=8, width=self.headerContainer.width - 10, bgColor=(0.62, 0.54, 0.53, 0.26), top=10)
        self.scoreBarLength = self.scoreBarContainer.width - 10
        self.scoreBar = uicls.VectorLine(name='scoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.calculate_score_bar_length(), 0), colorFrom=(1.0, 1.0, 1.0, 0.95), colorTo=(1.0, 1.0, 1.0, 0.95), widthFrom=3, widthTo=3, left=3)
        uicls.VectorLine(name='emptyScoreBar', parent=self.scoreBarContainer, align=uiconst.CENTERLEFT, translationFrom=(0, 0), translationTo=(self.scoreBarContainer.width - 7, 0), colorFrom=(0.0, 0.0, 0.0, 0.75), colorTo=(0.0, 0.0, 0.0, 0.75), widthFrom=3, widthTo=3, left=5)
        self.rankInfoContainer = uiprimitives.Container(name='rankInfoContainer', parent=self.headerContainer, align=uiconst.TOLEFT, width=75)
        self.rankIcon = uiprimitives.Sprite(name='rankIcon', parent=self.rankInfoContainer, texturePath=self.get_rank_icon_path(), height=36, width=36, align=uiconst.TOLEFT, left=5)
        SetTooltipHeaderAndDescription(targetObject=self.rankIcon, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AnalystRankTooltip'))
        self.rankLabel = uicontrols.Label(parent=self.rankInfoContainer, fontsize=16, text=self.rank, align=uiconst.CENTERLEFT, height=20, left=40)
        self.accuracyRatingContainer = uiprimitives.Container(name='accuracyRatingContainer', parent=self.headerContainer, align=uiconst.TOLEFT, width=70)
        self.accuracyRatingIconContainer = uiprimitives.Container(name='accuracyRatingIconContainer', parent=self.accuracyRatingContainer, height=32, width=32, align=uiconst.CENTERLEFT, left=40, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterBack.png')
        self.emptySprite = uiprimitives.Sprite(name='emptySprite', parent=self.accuracyRatingIconContainer, width=32, height=32, align=uiconst.CENTER)
        SetTooltipHeaderAndDescription(targetObject=self.emptySprite, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/AccuracyRatingTooltip'))
        self.accuracyNeedleIconContainer = uiprimitives.Transform(parent=self.accuracyRatingIconContainer, height=32, width=32, align=uiconst.TORIGHT, rotation=0)
        self.accuracyNeedleIcon = uiprimitives.Sprite(name='accuracyNeedleIcon', parent=self.accuracyNeedleIconContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/accuracyMeterNeedle.png', width=32, height=32, rotation=2.4, align=uiconst.CENTER)
        self.accuracyArcFill = uicls.Polygon(parent=self.accuracyRatingIconContainer, align=uiconst.CENTER)
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=-225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))
        self.accuracyRatingLabel = uicontrols.Label(name='AccuracyRating', parent=self.accuracyRatingContainer, fontsize=16, text='00,0%', align=uiconst.CENTERLEFT, autoFitToText=True, height=20)
        self.submissionHistoryContainer = uiprimitives.Container(name='submissionHistoryContainer', parent=self.headerContainer, align=uiconst.TORIGHT, width=75)
        self.submissionHistoryButton = uicontrols.ButtonIcon(name='submissionHistoryButton', parent=self.submissionHistoryContainer, align=uiconst.CENTERRIGHT, width=36, height=36, iconSize=36, texturePath='res:/UI/Texture/classes/ProjectDiscovery/iconSubmissionsEmpty.png', func=self.toggle_submission_history, iconColor=(1, 1, 1, 1))
        SetTooltipHeaderAndDescription(targetObject=self.submissionHistoryButton, headerText='', descriptionText=localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryTooltip'))
        self.unscoredSubmissionsLabel = uicontrols.Label(name='submissionLabel', parent=self.submissionHistoryContainer, fontsize=16, text='0', align=uiconst.CENTERRIGHT, autoFitToText=True, height=20, left=35)
        self.state = uiconst.UI_NORMAL

    def OnMouseDownDrag(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryHeaderDragged')

    def OnMouseDown(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseDownOnHeader')

    def OnMouseEnter(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseEnterHeader')

    def OnMouseExit(self, *args):
        sm.ScatterEvent('OnProjectDiscoveryMouseExitHeader')

    def toggle_submission_history(self):
        self.parent.parent.toggle_submission_history()

    def get_player_statistics(self, get_history):
        return self.pdService.player_statistics(get_history)

    def check_submission_count(self):
        if self.unscored_submissions_count < self.oldUnscoredSubmissionsCount:
            self.submissionHistoryButton.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/iconSubmissionsNew.png')
        self.oldUnscoredSubmissionsCount = self.unscored_submissions_count
        self.unscoredSubmissionsLabel.SetText(FmtAmt(self.unscored_submissions_count))

    def update_accuracy_rating_text(self):
        self.accuracyRatingLabel.SetText(str(FmtAmt(self.score * 100, showFraction=1) + '%'))

    def update_accuracy_meter(self):
        animations.Tr2DRotateTo(self.accuracyNeedleIconContainer, startAngle=self.accuracyNeedleIconContainer.rotation, endAngle=self.needle_Rotation, curveType=uiconst.ANIM_LINEAR)
        self.accuracyArcFill.MakeArc(radius=0, outerRadius=10, fromDeg=-225.0, toDeg=self.score * 265 - 225.0, outerColor=(1.0, 1.0, 0, 0.7), innerColor=(1.0, 1.0, 0, 0.7))

    @on_event('OnUpdateHeader')
    def update_header(self):
        self.player_Statistics = self.get_player_statistics(True)
        if 'message' in self.player_Statistics:
            logger.error(self.player_Statistics)
            if 'code' in self.player_Statistics:
                if self.player_Statistics['code'] == 103010:
                    self.score = 0.5
                    self.needle_Rotation = self.score * self.full_needle_rotation
        else:
            self.unscored_submissions_count = self.player_Statistics['projects'][0]['classificationCountUnscored']
            self.score = self.player_Statistics['projects'][0]['score']
            self.needle_Rotation = self.score * self.full_needle_rotation
            self.submissionHistory = self.player_Statistics['projects'][0]['history']
            self.check_submission_count()
        self.update_accuracy_rating_text()
        self.update_accuracy_meter()

    @on_event(const.Events.CloseResult)
    def on_result_closed(self, result):
        self.score = result['player']['score']
        self.needle_Rotation = self.score * self.full_needle_rotation
        self.update_accuracy_rating_text()
        self.update_accuracy_meter()
        self.update_header()

    @on_event(const.Events.UpdateScoreBar)
    def on_score_bar_update(self, player_state):
        self.playerState = player_state
        self.rank = self.playerState.rank
        self.totalNeededExperience = xpNeededForRank[self.rank + 1]
        self.experience = self.playerState.experience
        uthread.new(self.update_score_bar)

    def calculate_score_bar_length(self):
        xp_needed_for_current_rank = xpNeededForRank[self.rank]
        ratio = (self.experience - xp_needed_for_current_rank) / float(self.totalNeededExperience - xp_needed_for_current_rank)
        return ratio * self.scoreBarLength

    def update_score_bar(self):
        new_score_bar_length = self.calculate_score_bar_length()
        counter = self.oldScoreBarLength
        self.oldScoreBarLength = new_score_bar_length
        while counter >= new_score_bar_length:
            counter += 0.5
            if counter >= self.scoreBarLength - 5:
                counter = -1
                self.update_rank_values()
            else:
                if self.scoreBar.renderObject.translationTo:
                    self.scoreBar.renderObject.translationTo = (counter, 0)
                blue.synchro.Sleep(1)

        while counter < new_score_bar_length:
            counter += 0.5
            self.scoreBar.renderObject.translationTo = (counter, 0)
            blue.synchro.Sleep(1)

        self.update_rank_values()

    def get_rank_icon_path(self):
        rank_band = int(math.ceil(float(self.rank) / 10 + 0.1))
        if rank_band < 1:
            rank_band = 1
        return 'res:/UI/Texture/classes/ProjectDiscovery/rankIcon' + str(rank_band) + '.png'

    def update_rank_values(self):
        self.rankIcon.SetTexturePath(self.get_rank_icon_path())
        self.rankIcon.ReloadTexture()
        self.rankLabel.SetText(self.rank)
        self.rankLabel.ResolveAutoSizing()

    def get_scroll_content(self):
        if not self.submissionHistory:
            return []
        entries = []
        for i in self.submissionHistory:
            red_state = False
            green_state = False
            if i['playerScoreChange'] is None:
                value1 = datetime.datetime.strptime(i['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                value1 = value1.strftime('%Y-%m-%d %H:%M:%S')
                value2 = localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryPendingLabel')
            else:
                value1 = datetime.datetime.strptime(i['createdAt'], '%Y-%m-%dT%H:%M:%S.%fZ')
                value1 = value1.strftime('%Y-%m-%d %H:%M:%S')
                value2 = str(FmtAmt(i['playerScoreChange'] * 100, showFraction=4) + '%')
                if i['playerScoreChange'] > 0:
                    value2 = '+' + value2
                    green_state = True
                elif i['playerScoreChange'] < 0:
                    red_state = True
                else:
                    value2 = localization.GetByLabel('UI/ProjectDiscovery/SubmissionHistoryNoChangeLabel')
            data = KeyVal(label='%s<t>%s' % (value1, value2), redstate=red_state, greenstate=green_state)
            entry = listentry.Get(decoClass=SubmissionHistoryEntry, data=data)
            entries.append(entry)

        return entries


class SubmissionHistoryEntry(listentry.Generic):

    def ApplyAttributes(self, attributes):
        listentry.Generic.ApplyAttributes(self, attributes)
        self.bgColor = Fill(bgParent=self)

    def Load(self, *args, **kwds):
        listentry.Generic.Load(self, *args, **kwds)
        if args[0].redstate:
            self.bgColor.color = (0.1607, 0.0705, 0.0745, 1)
            self.bgColor.display = True
        elif args[0].greenstate:
            self.bgColor.color = (0.11, 0.129, 0.08, 1)
            self.bgColor.display = True
        else:
            self.bgColor.display = False

    def GetHeight(self, *args):
        return 30
