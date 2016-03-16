#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\rewardsview.py
import math
import blue
import uicls
import uthread
import uicontrols
import localization
import uiprimitives
import taskimages
import carbonui.const as uiconst
from projectdiscovery.client import const
from projectdiscovery.common.const import xpNeededForRank
from carbonui.uianimations import animations
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui.control.eveLabel import EveLabelLargeBold
from projectdiscovery.client.util.eventlistener import eventlistener, on_event

@eventlistener()

class RewardsView(uiprimitives.Container):

    def ApplyAttributes(self, attributes):
        super(RewardsView, self).ApplyAttributes(attributes)
        self.projectDiscovery = sm.RemoteSvc('ProjectDiscovery')
        self.isTraining = False
        self.LP_Reward = 0
        self.XP_Reward = 0
        self.ISK_Reward = 0
        self.playerState = attributes.get('playerState')
        self.experience = self.playerState.experience
        self.player_rank = self.playerState.rank
        self.totalNeededExperience = xpNeededForRank[self.player_rank + 1]
        self.setup_rewards_screen()

    def setup_rewards_screen(self):
        self.parent_container = uiprimitives.Container(name='parentContainer', parent=self, align=uiconst.CENTER, height=400, width=450, top=-10)
        self.background_container = uiprimitives.Container(name='background', parent=self.parent_container, width=450, height=285, align=uiconst.CENTERTOP, bgColor=(0.037, 0.037, 0.037, 1))
        uicontrols.Frame(parent=self.background_container, color=(0.36, 0.36, 0.36, 0.36))
        self.main_container = uiprimitives.Container(name='mainContainer', parent=self.background_container, width=440, height=275, align=uiconst.CENTER)
        self.rank_container = uiprimitives.Container(name='rankContainer', parent=self.parent_container, width=450, height=100, align=uiconst.CENTERBOTTOM, bgColor=(0.037, 0.037, 0.037, 1))
        uicontrols.Frame(parent=self.rank_container, color=(0.36, 0.36, 0.36, 0.36))
        self.agent_container = uiprimitives.Container(name='agentContainer', parent=self.main_container, align=uiconst.TOPLEFT, height=170, width=150, left=5, top=5)
        self.agent_image = uiprimitives.Sprite(name='agentImage', parent=self.agent_container, align=uiconst.TOTOP, height=150, width=150, texturePath='res:/UI/Texture/classes/ProjectDiscovery/lundberg.png')
        self.agent_label = uicontrols.Label(name='agentName', parent=self.agent_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/AgentName'), top=5)
        self.SOE_image = uiprimitives.Sprite(name='SOE_logo', parent=self.main_container, align=uiconst.BOTTOMLEFT, height=75, width=75, texturePath='res:/UI/Texture/Corps/14_128_1.png', top=25)
        self.text_container = uiprimitives.Container(name='textContainer', parent=self.main_container, align=uiconst.TOPRIGHT, width=270, height=80)
        self.text_header_container = uiprimitives.Container(name='textHeaderContainer', parent=self.text_container, align=uiconst.TOTOP, height=20)
        self.header_message = EveLabelLargeBold(parent=self.text_header_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
        self.main_message = uicontrols.Label(parent=self.text_container, align=uiconst.TOTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksMessage'), top=15)
        self.setup_reward_container()
        self.setup_reward_footer()
        self.main_button_container = uiprimitives.Container(name='continueButtonContainer', parent=self, align=uiconst.CENTERBOTTOM, width=355, height=53, top=3, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.continue_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.continue_button = uicontrols.Button(name='RewardViewContinueButton', parent=self.continue_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ContinueButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30, func=lambda x: self.fade_out(), state=uiconst.UI_DISABLED)
        uiprimitives.Sprite(parent=self.continue_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.continue_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)

    def setup_reward_container(self):
        self.reward_container = uiprimitives.Container(name='reward_container', parent=self.main_container, align=uiconst.BOTTOMRIGHT, width=270, height=130)
        self.analysis_points_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, bgColor=(0.36, 0.36, 0.36, 0.36))
        self.analysis_points_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.analysis_points_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='Analyst_points_Logo', align=uiconst.TOTOP, height=40, width=40, texturePath='res:/UI/Texture/classes/ProjectDiscovery/analysisPointsIcon.png')
        self.analysis_points_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.analysis_points_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/AnalysisPointsLabel'), fontsize=14)
        self.analysis_points = uicontrols.Label(parent=uiprimitives.Container(parent=self.analysis_points_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')
        self.ISK_reward_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, top=5, bgColor=(0.36, 0.36, 0.36, 0.36))
        self.ISK_reward_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.ISK_reward_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='ISK_reward_Logo', align=uiconst.TOTOP, height=40, width=40, texturePath='res:/ui/texture/WindowIcons/wallet.png')
        self.ISK_reward_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.ISK_reward_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/IskLabel'), fontsize=14)
        self.ISK_reward = uicontrols.Label(parent=uiprimitives.Container(parent=self.ISK_reward_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')
        self.loyalty_points_container = uiprimitives.Container(parent=self.reward_container, width=360, height=40, align=uiconst.TOTOP, top=5, bgColor=(0.36, 0.36, 0.36, 0.36))
        self.loyalty_points_icon = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.loyalty_points_container, width=40, height=40, align=uiconst.TOLEFT, left=10), name='loyalty_points_logo', align=uiconst.TOTOP, height=40, width=40, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SoeLogo.png')
        self.loyalty_points_label = uicontrols.Label(parent=uiprimitives.Container(parent=self.loyalty_points_container, align=uiconst.TOLEFT, width=75, height=50), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/LoyaltyPointsLabel'), fontsize=14)
        self.loyalty_points = uicontrols.Label(parent=uiprimitives.Container(parent=self.loyalty_points_container, align=uiconst.CENTERRIGHT, width=20, height=50, left=25), align=uiconst.CENTER, fontsize=16, text='0')

    def setup_reward_footer(self):
        self.rank_header = uiprimitives.Container(parent=self.rank_container, align=uiconst.TOTOP, height=20, bgColor=(0.36, 0.36, 0.36, 0.36))
        uicontrols.Label(parent=self.rank_header, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ScientistRank'), align=uiconst.CENTERLEFT, left=5)
        self.footer_container = uiprimitives.Container(name='footerContainer', parent=self.rank_container, align=uiconst.CENTER, height=65, width=435, top=10, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/rankInfoBackground.png')
        self.rank_icon_container = uiprimitives.Container(name='rankIconContainer', parent=self.footer_container, align=uiconst.TOLEFT, width=64, height=64, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/rankIconBackground.png')
        self.rank_icon = uiprimitives.Sprite(name='rank_icon', parent=self.rank_icon_container, align=uiconst.TOTOP, width=64, height=64)
        self.rank_information_container = uiprimitives.Container(name='rankInfoContainer', parent=self.footer_container, align=uiconst.TOLEFT, width=360, left=5)
        self.rank_label = uicontrols.Label(name='rankLabel', parent=self.rank_information_container, align=uiconst.TOPLEFT, text='', fontsize=14)
        self.rank = uicontrols.Label(name='rank', parent=self.rank_information_container, align=uiconst.TOPRIGHT, text='', fontsize=14)
        self.scorebar_container = uiprimitives.Container(name='scorebarContainer', parent=self.rank_information_container, align=uiconst.TOBOTTOM, height=60)
        self.scoreBarLength = self.rank_information_container.width
        self.oldScoreBarLength = self.calculate_score_bar_length()
        self.total_points_container = uiprimitives.Container(name='totalPointsContainer', parent=self.scorebar_container, align=uiconst.TOTOP, width=self.scorebar_container.width, height=15, top=10)
        self.total_points_label = uicontrols.Label(name='totalPointsLabel', parent=self.total_points_container, align=uiconst.TOPLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TotalAnalysisPointsLabel'), fontsize=12)
        self.total_points = uicontrols.Label(name='totalPoints', parent=self.total_points_container, align=uiconst.TOPRIGHT, fontsize=12)
        self.score_bar = uicls.VectorLine(name='ScoreBar', parent=self.scorebar_container, align=uiconst.TOTOP, translationFrom=(0, 7), translationTo=(1, 7), colorFrom=(1.0, 1.0, 1.0, 0.95), colorTo=(1.0, 1.0, 1.0, 0.95), widthFrom=3, widthTo=3)
        uicls.VectorLine(name='EmptyScoreBar', parent=self.scorebar_container, align=uiconst.TOTOP_NOPUSH, translationFrom=(0, 7), translationTo=(self.scoreBarLength, 7), colorFrom=(0.0, 0.0, 0.0, 0.75), colorTo=(0.0, 0.0, 0.0, 0.75), widthFrom=4, widthTo=4)
        self.needed_points_container = uiprimitives.Container(parent=self.scorebar_container, align=uiconst.TOBOTTOM, width=self.scorebar_container.width, height=15, top=10)
        self.needed_points_label = uicontrols.Label(parent=self.needed_points_container, align=uiconst.BOTTOMLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/NeededXpLabel'), fontsize=12)
        self.needed_points = uicontrols.Label(parent=self.needed_points_container, align=uiconst.TOPRIGHT, fontsize=12)

    @on_event(const.Events.CloseResult)
    def on_result_closed(self, result):
        self.XP_Reward = result['XP_Reward']
        self.LP_Reward = result['LP_Reward']
        self.ISK_Reward = result['ISK_Reward']
        self.playerState = result['playerState']
        if self.LP_Reward == 0 and self.ISK_Reward == 0:
            self.loyalty_points_container.opacity = 0
            self.ISK_reward_container.opacity = 0
            self.analysis_points_container.top = 45
        if 'isTraining' in result:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TutorialCompletedHeader'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/TutorialCompletedMessage'))
        else:
            self.header_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/Header'))
            self.main_message.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ThanksMessage'))
        self.experience = self.playerState.experience
        self.player_rank = self.playerState.rank
        self.totalNeededExperience = xpNeededForRank[self.player_rank + 1]
        self.needed_experience = self.totalNeededExperience - self.experience
        self.rank_icon.SetTexturePath(self.get_rank_icon_path())
        self.score_bar.renderObject.translationTo = (self.calculate_score_bar_length(), 7)
        self.needed_points.SetText('{:,.0f}'.format(self.needed_experience))
        self.total_points.SetText('{:,.0f}'.format(self.experience))

    def update_rank_values(self):
        self.player_rank = self.playerState.rank
        self.totalNeededExperience = xpNeededForRank[self.player_rank + 1]
        self.needed_experience = self.totalNeededExperience - self.experience
        self.rank.text = const.Texts.RankLabel + str(self.player_rank)
        self.total_points.text = self.experience
        self.needed_points.text = self.needed_experience
        self.rank_icon.texturePath = self.get_rank_icon_path()
        self.rank_icon.ReloadTexture()
        self.rank_label.text = localization.GetByLabel('UI/ProjectDiscovery/RankTitles/RankTitle' + str(self.rank_band))
        self.tick_rewards()
        self.oldExperience = self.experience
        self.experience = self.playerState.experience
        uthread.new(self.update_experience_label)
        self.oldNeededExperience = self.needed_experience
        self.needed_experience = self.totalNeededExperience - self.experience
        uthread.new(self.update_needed_experience_label)
        uthread.new(self.update_score_bar)

    def tick_rewards(self):
        uthread.new(self.update_xp_reward)
        uthread.new(self.update_isk_reward)
        uthread.new(self.update_lp_reward)

    def update_needed_experience_label(self):
        while self.oldNeededExperience > self.needed_experience:
            self.oldNeededExperience -= 2
            self.needed_points.text = '{:,.0f}'.format(self.oldNeededExperience)
            blue.synchro.Sleep(1)

        self.needed_points.text = '{:,.0f}'.format(self.oldNeededExperience)

    def update_experience_label(self):
        while self.oldExperience < self.experience:
            self.oldExperience += 2
            self.total_points.text = '{:,.0f}'.format(self.oldExperience)
            blue.synchro.Sleep(1)

        self.total_points.text = '{:,.0f}'.format(self.experience)

    def update_xp_reward(self):
        counter = 0
        while counter < self.XP_Reward:
            counter += 2
            self.analysis_points.text = counter
            blue.synchro.Sleep(1)

        self.analysis_points.text = FmtAmt(self.XP_Reward)

    def update_isk_reward(self):
        if self.ISK_Reward:
            counter = 0
            while counter < self.ISK_Reward:
                counter += 1000
                self.ISK_reward.text = '{:,.0f}'.format(counter)
                blue.synchro.Sleep(1)

            self.ISK_reward.text = FmtAmt(self.ISK_Reward)

    def update_lp_reward(self):
        if self.LP_Reward:
            counter = 0
            while counter < self.LP_Reward:
                counter += 4
                self.loyalty_points.text = counter
                blue.synchro.Sleep(1)

            self.loyalty_points.text = FmtAmt(self.LP_Reward)

    def reset_reward_labels(self):
        self.loyalty_points.text = '0'
        self.ISK_reward.text = '0'
        self.analysis_points.text = '0'

    def get_rank_icon_path(self):
        self.rank_band = int(math.ceil(float(self.player_rank) / 10 + 0.1))
        if self.rank_band < 1:
            self.rank_band = 1
        return 'res:/UI/Texture/classes/ProjectDiscovery/rankIcon' + str(self.rank_band) + '.png'

    def calculate_score_bar_length(self):
        xp_needed_for_current_rank = xpNeededForRank[self.player_rank]
        ratio = (self.experience - xp_needed_for_current_rank) / float(self.totalNeededExperience - xp_needed_for_current_rank)
        return ratio * self.scoreBarLength

    def update_score_bar(self):
        sm.ScatterEvent(const.Events.UpdateScoreBar, self.playerState)
        new_score_bar_length = self.calculate_score_bar_length()
        counter = self.oldScoreBarLength
        self.oldScoreBarLength = new_score_bar_length
        while counter >= new_score_bar_length:
            counter += 1
            if counter >= self.scoreBarLength:
                counter = -1
            else:
                self.score_bar.renderObject.translationTo = (counter, 7)
                blue.synchro.Sleep(1)

        while counter < new_score_bar_length:
            counter += 1
            self.score_bar.renderObject.translationTo = (counter, 7)
            blue.synchro.Sleep(1)

    def fade_out(self):
        sm.ScatterEvent(const.Events.RewardViewFadeOut)
        animations.FadeOut(self, duration=0.5, callback=self.continue_from_reward)

    @on_event(const.Events.ProcessingViewFinished)
    def fade_in(self):
        self.update_rank_values()
        animations.FadeIn(self, duration=0.5)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopPlay)
        self.continue_button.state = uiconst.UI_NORMAL

    def continue_from_reward(self):
        if self.isTraining:
            if self.tutorial_completed:
                sm.ScatterEvent(const.Events.ProjectDiscoveryStarted, True)
        else:
            sm.ScatterEvent(const.Events.ContinueFromReward)
        self.reset_reward_labels()
        self.continue_button.state = uiconst.UI_DISABLED
        taskimages.Audio.play_sound = True
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowClosePlay)
        sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)

    def enable_button(self):
        self.continue_button.state = uiconst.UI_NORMAL

    def disable_button(self):
        self.continue_button.state = uiconst.UI_DISABLED
