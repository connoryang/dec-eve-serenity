#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelAchievements.py
from achievements.client.achievementGroupEntry import AchievementGroupEntry
from achievements.client.achievementSettings import OpportunitySettings
from achievements.client.achievementTreeWindow import AchievementTreeWindow
from achievements.client.auraAchievementWindow import AchievementAuraWindow
from achievements.common.achievementConst import AchievementSettingConst
from achievements.common.achievementGroups import GetAchievementGroup
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.util.color import Color
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.eveFontConst import EVE_SMALL_FONTSIZE, EVE_LARGE_FONTSIZE
from eve.client.script.ui.shared.infoPanels import infoPanelConst
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
import carbonui.const as uiconst
from eve.client.script.ui.shared.infoPanels.infoPanelConst import PANEL_ACHIEVEMENTS, MODE_COLLAPSED, MODE_NORMAL
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelLabel
from localization import GetByLabel
from eve.client.script.ui.control.buttons import ButtonIcon
import uthread

class InfoPanelAchievements(InfoPanelBase):
    __guid__ = 'uicls.InfoPanelAchievements'
    default_name = 'InfoPanelAchievements'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesPanelIcon.png'
    default_state = uiconst.UI_PICKCHILDREN
    default_height = 120
    label = 'UI/Achievements/OpportunitiesHint'
    hasSettings = True
    panelTypeID = PANEL_ACHIEVEMENTS
    groupEntry = None
    achievementContent = None
    __notifyevents__ = ['OnAchievementsDataInitialized', 'OnAchievementActiveGroupChanged', 'OnAchievementChanged']

    def ApplyAttributes(self, attributes):
        InfoPanelBase.ApplyAttributes(self, attributes)
        self.settingsObject = None
        self.titleLabel = self.headerCls(name='title', text='<color=white>' + GetByLabel('UI/Achievements/InfoPanelHeader'), parent=self.headerCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.headerButton.OnMenuClosed = self.OnSettingsMenuClosed

    @staticmethod
    def IsAvailable():
        if settings.user.ui.Get(AchievementSettingConst.INFOPANEL_DISABLE_CONFIG, False):
            return False
        return sm.GetService('achievementSvc').IsEnabled()

    def ConstructCompact(self):
        self.mainCont.Flush()
        self.achievementContent = None

    def ConstructNormal(self, blinkAchievementID = None):
        if not self.achievementContent or self.achievementContent.destroyed:
            self.mainCont.Flush()
            self.achievementContent = ContainerAutoSize(parent=self.mainCont, name='achievementContent', align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
            grid = LayoutGrid(parent=self.mainCont, align=uiconst.TOTOP, columns=2, opacity=0.0)
            button = ButtonIcon(texturePath='res:/ui/Texture/Classes/InfoPanels/opportunitiesTreeIcon.png', align=uiconst.TOPLEFT, iconSize=16, parent=grid, func=self.OpenOpportunitiesTree, pos=(0, 0, 16, 16))
            subTextLabel = InfoPanelLabel(parent=grid, align=uiconst.CENTERLEFT, text=GetByLabel('Achievements/UI/showAll'), state=uiconst.UI_NORMAL, fontsize=EVE_SMALL_FONTSIZE, bold=True, left=4)
            subTextLabel.OnClick = self.OpenOpportunitiesTree
            uicore.animations.FadeIn(grid)
        groupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        self.LoadContent(groupID, blinkAchievementID=blinkAchievementID)

    def LoadContent(self, groupID = None, blinkAchievementID = None):
        activeGroupData = GetAchievementGroup(groupID)
        if activeGroupData:
            if self.groupEntry is None or self.groupEntry.destroyed:
                self.achievementContent.Flush()
                self.groupEntry = AchievementGroupEntry(parent=self.achievementContent, align=uiconst.TOTOP, groupInfo=activeGroupData, blinkAchievementID=blinkAchievementID, animateIn=True)
            else:
                self.groupEntry.LoadGroupData(activeGroupData, blinkAchievementID=blinkAchievementID, animateIn=True)
            return
        self.achievementContent.Flush()
        self.groupEntry = None
        label = InfoPanelLabel(name='noActiveOpp', text=GetByLabel('Achievements/UI/noActiveOpp'), parent=self.achievementContent, fontsize=EVE_LARGE_FONTSIZE, padding=(0, 2, 0, 2), state=uiconst.UI_NORMAL, align=uiconst.TOTOP)

    def OpenAchievementAuraWindow(self, *args):
        AchievementAuraWindow.Open()

    def OpenOpportunitiesTree(self, *args):
        auraWindow = AchievementAuraWindow.GetIfOpen()
        if auraWindow:
            auraWindow.FadeOutTransitionAndClose()
        AchievementTreeWindow.Open()
        sm.GetService('experimentClientSvc').LogWindowOpenedActions('OpportunityWindowInfoPanel')

    def OnAchievementActiveGroupChanged(self, groupID, emphasize):
        if self.mode != MODE_NORMAL:
            self.SetMode(MODE_NORMAL)
        self.Refresh()
        if emphasize:
            uicore.animations.BlinkIn(self, duration=0.4, loops=4)

    def OnAchievementChanged(self, achievement, *args, **kwds):
        if achievement:
            blinkAchievementID = achievement.achievementID
        else:
            blinkAchievementID = None
        self.Refresh(blinkAchievementID)

    def OnAchievementsDataInitialized(self):
        self.Refresh()

    def Refresh(self, blinkAchievementID = None):
        if self.mode != infoPanelConst.MODE_NORMAL:
            self.ConstructCompact()
        else:
            self.ConstructNormal(blinkAchievementID=blinkAchievementID)

    def GetSettingsMenu(self, menuParent):
        if self.settingsObject is None:
            self.settingsObject = OpportunitySettings()
        return self.settingsObject.GetOpportunitySettings(menuParent)

    def OnSettingsMenuClosed(self, *args):
        UtilMenu.OnMenuClosed(self.headerButton, *args)
        uthread.new(self.StoreSettingChanges_thread)

    def StoreSettingChanges_thread(self):
        if self.settingsObject:
            self.settingsObject.StoreChanges()
            self.settingsObject = None
