#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\achievementTaskEntry.py
from achievements.client.auraAchievementWindow import AchievementAuraWindow
from achievements.common.extraInfoForTasks import ACHIEVEMENT_TASK_EXTRAINFO, TaskInfoEntry_Text, TaskInfoEntry_ImageText
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelMedium
import carbonui.const as uiconst
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelHeaderBackground
from localization import GetByLabel
import uthread
import blue
import trinity
COLOR_COMPLETED_BG = (0.227, 0.627, 0.8, 0.5)
COLOR_INCOMPLETE_BG = (1.0, 1.0, 1.0, 0.15)
COLOR_COMPLETED = (0.6, 0.9, 1.0, 1.0)
COLOR_INCOMPLETED = (1.0, 1.0, 1.0, 0.8)

def CheckMouseOverUtil(uiObject, callback):

    def IsMouseOver(uiObject):
        if uicore.uilib.mouseOver is uiObject:
            return
        if uicore.uilib.mouseOver.IsUnder(uiObject):
            return
        uiObject.__checkMouseOverTimer = None
        callback(uiObject)

    uiObject.__checkMouseOverTimer = AutoTimer(1, IsMouseOver, uiObject)


class BlurredBackgroundSprite(Sprite):
    __notifyevents__ = ['OnBlurredBufferCreated']
    default_name = 'BlurredBackgroundSprite'
    default_state = uiconst.UI_DISABLED
    default_spriteEffect = trinity.TR2_SFX_BLURBACKGROUND

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        if uicore.uilib.blurredBackBufferAtlas:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
        trinity.device.RegisterResource(self)

    def OnCreate(self, *args):
        pass

    def OnBlurredBufferCreated(self, *args):
        if not self.destroyed:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas


class AchievementTaskEntry(ContainerAutoSize):
    default_padLeft = 0
    default_padRight = 0
    default_padTop = 0
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    default_alignMode = uiconst.TOTOP
    checkedTexturePath = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesCheck.png'
    uncheckedTexturePath = 'res:/UI/Texture/Classes/InfoPanels/opportunitiesIncompleteBox.png'
    tooltipPointer = uiconst.POINT_LEFT_2
    achievementGroup = None
    autoShowDetails = False
    detailsParent = None
    callbackTaskExpanded = None

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.autoShowDetails = bool(attributes.autoShowDetails) or True
        if attributes.get('showBackground', True):
            Fill(bgParent=self, color=(0, 0, 0, 0.2))
            BlurredBackgroundSprite(bgParent=self, color=(1, 1, 1, 0.9))
        self.headerContainer = Container(parent=self, align=uiconst.TOTOP)
        self.mouseOverFill = FillThemeColored(bgParent=self.headerContainer, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.completedFill = FillThemeColored(bgParent=self.headerContainer, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        self.backgroundContainer = InfoPanelHeaderBackground(bgParent=self.headerContainer)
        self.achievementTask = attributes.achievement
        self.achievementGroup = attributes.achievementGroup
        self.callbackTaskExpanded = attributes.callbackTaskExpanded
        self.checkbox = Sprite(parent=self.headerContainer, texturePath=self.uncheckedTexturePath, pos=(4, 3, 14, 14))
        self.achievementText = EveLabelMedium(name='achievementText', text=self.achievementTask.name, parent=self.headerContainer, padLeft=2 * self.checkbox.left + self.checkbox.width, align=uiconst.TOTOP, padTop=2)
        self.UpdateAchievementTaskState()
        newHeight = max(self.checkbox.height + 2 * self.checkbox.top, self.achievementText.textheight + 2 * self.achievementText.padTop)
        self.headerContainer.height = newHeight
        if attributes.blinkIn and self.IsTaskCompleted():
            uthread.new(uicore.animations.BlinkIn, self, duration=0.2, loops=4)

    def ToggleDetails(self):
        if self.detailsParent and not self.detailsParent.destroyed:
            self.HideDetails()
        else:
            self.ShowDetails()

    def HideDetails(self, *args):
        if self.detailsParent and not self.detailsParent.destroyed:
            detailsParent = self.detailsParent
            self.detailsParent = None
            detailsParent.DisableAutoSize()
            uicore.animations.FadeOut(detailsParent, duration=0.15)
            uicore.animations.MorphScalar(detailsParent, 'height', detailsParent.height, 0, duration=0.15, callback=detailsParent.Close)

    def ShowDetails(self):
        if self.detailsParent and not self.detailsParent.destroyed:
            return
        uthread.new(self._ShowDetails)

    def _ShowDetails(self):
        if not self.autoShowDetails:
            return
        self.detailsParent = ContainerAutoSize(align=uiconst.TOTOP, parent=self, clipChildren=True)
        if self.callbackTaskExpanded:
            self.callbackTaskExpanded(self)
        self.detailsParent.DisableAutoSize()
        label = EveLabelMedium(parent=self.detailsParent, text=self.achievementTask.description, align=uiconst.TOTOP, padding=(6, 3, 6, 2))
        extraInfo = ACHIEVEMENT_TASK_EXTRAINFO.get(self.achievementTask.achievementID, None)
        if extraInfo:
            grid = LayoutGrid(parent=self.detailsParent, align=uiconst.TOTOP, cellPadding=2, columns=2, padding=4)
            for taskInfoEntry in extraInfo:
                if isinstance(taskInfoEntry, TaskInfoEntry_Text):
                    label = EveLabelMedium(text=taskInfoEntry.text, color=taskInfoEntry.textColor, width=240)
                    grid.AddCell(label, colSpan=2)
                elif isinstance(taskInfoEntry, TaskInfoEntry_ImageText):
                    texturePath = taskInfoEntry.GetTexturePath()
                    icon = Sprite(name='icon', parent=grid, pos=(0,
                     0,
                     taskInfoEntry.imageSize,
                     taskInfoEntry.imageSize), texturePath=texturePath, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=taskInfoEntry.imageColor)
                    text = GetByLabel(taskInfoEntry.textPath)
                    label = EveLabelMedium(text=text, color=taskInfoEntry.textColor, width=220, align=uiconst.CENTERLEFT)
                    grid.AddCell(label)

        blue.synchro.Yield()
        height = self.detailsParent.GetAutoSize()[1]
        uicore.animations.FadeIn(self.detailsParent, duration=0.3)
        uicore.animations.MorphScalar(self.detailsParent, 'height', self.detailsParent.height, height, duration=0.25, sleep=True)
        if self.detailsParent and not self.detailsParent.destroyed:
            self.detailsParent.EnableAutoSize()

    def OnMouseEnter(self, *args):
        uicore.animations.MorphScalar(self.headerContainer, 'opacity', startVal=self.opacity, endVal=2.0, curveType=uiconst.ANIM_OVERSHOT, duration=0.5)
        CheckMouseOverUtil(self, self.ResetMouseOverState)

    def ResetMouseOverState(self, *args):
        if self.destroyed:
            return
        uicore.animations.MorphScalar(self.headerContainer, 'opacity', startVal=self.opacity, endVal=1.0, duration=0.1)

    def OnClick(self, *args):
        if self.autoShowDetails:
            self.ToggleDetails()
        else:
            aura = AchievementAuraWindow.GetIfOpen()
            if aura:
                aura.Step_TaskInfo_Manual(self.achievementTask, self.achievementGroup)
            else:
                AchievementAuraWindow.Open(loadAchievementTask=self.achievementTask, loadAchievementGroup=self.achievementGroup)

    def IsTaskCompleted(self):
        completedTasks = sm.GetService('achievementSvc').GetCompletedTaskIds()
        return self.achievementTask.achievementID in completedTasks

    def UpdateAchievementTaskState(self, animate = False):
        if self.IsTaskCompleted():
            self.checkbox.SetTexturePath(self.checkedTexturePath)
            if animate:
                self.completedFill.displayWidth = 0.0
                self.completedFill.opacity = 1.5
                uicore.animations.MorphScalar(self.completedFill, 'displayWidth', 0, self.displayWidth, duration=0.75)
                uicore.animations.FadeTo(self.completedFill, startVal=1.5, endVal=0.5, duration=1.5, timeOffset=0.5)
                uicore.animations.MorphScalar(self.checkbox, 'glowExpand', startVal=5.0, endVal=0.0, duration=0.33)
                uicore.animations.SpColorMorphTo(self.checkbox, startColor=(0.5, 0.5, 0.5, 0.5), endColor=(0, 0, 0, 0), attrName='glowColor', duration=0.33)
            else:
                self.completedFill.opacity = 0.5
        else:
            self.checkbox.SetTexturePath(self.uncheckedTexturePath)
            uicore.animations.FadeTo(self.completedFill, startVal=self.completedFill.opacity, endVal=0.0)

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        return
        if uicore.uilib.tooltipHandler.IsUnderTooltip(self):
            return
        achievementID = self.achievementTask.achievementID
        tooltipPanel.LoadGeneric2ColumnTemplate()
        if self.achievementTask.description:
            tooltipPanel.AddLabelMedium(text=self.achievementTask.description, colSpan=tooltipPanel.columns, wrapWidth=200)
        extraInfo = ACHIEVEMENT_TASK_EXTRAINFO.get(achievementID, None)
        if extraInfo:
            for taskInfoEntry in extraInfo:
                if isinstance(taskInfoEntry, TaskInfoEntry_Text):
                    tooltipPanel.AddLabelMedium(text=taskInfoEntry.text, color=taskInfoEntry.textColor, colSpan=tooltipPanel.columns, wrapWidth=200)
                elif isinstance(taskInfoEntry, TaskInfoEntry_ImageText):
                    texturePath = taskInfoEntry.GetTexturePath()
                    icon = Sprite(name='icon', parent=tooltipPanel, pos=(0,
                     0,
                     taskInfoEntry.imageSize,
                     taskInfoEntry.imageSize), texturePath=texturePath, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=taskInfoEntry.imageColor)
                    text = GetByLabel(taskInfoEntry.textPath)
                    label = EveLabelMedium(text=text, color=taskInfoEntry.textColor, width=180, align=uiconst.CENTERLEFT)
                    tooltipPanel.AddCell(label)

    def GetHint(self):
        return None
