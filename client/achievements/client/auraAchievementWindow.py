#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\auraAchievementWindow.py
from achievements.client.achievementSettings import OpportunitiesSettingsMenu
from achievements.common.achievementGroups import GetFirstIncompleteAchievementGroup, GetActiveAchievementGroup
from achievements.common.extraInfoForTasks import ACHIEVEMENT_TASK_EXTRAINFO, TaskInfoEntry_Text, TaskInfoEntry_ImageText
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_RIGHT
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.buttons import Button, ButtonIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium, Label, EveLabelSmall
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FrameThemeColored
from localization import GetByLabel
import uthread
TEXT_MARGIN = 12
WINDOW_WIDTH = 320
WINDOW_MIN_HEIGHT = 144
COL1_WIDTH = 20
COL3_WIDTH = 32
MAIN_MARGIN = 14
AURA_SIZE = 120

class TextButton(Container):
    IDLE_OPACITY = 0.5
    MOUSEOVER_OPACITY = 1.0
    default_state = uiconst.UI_NORMAL
    default_opacity = IDLE_OPACITY

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        textMargin = attributes.textMargin or 2
        self.label = EveLabelSmall(parent=self, text=attributes.label, bold=True, left=textMargin, top=textMargin)
        self.width = self.label.textwidth + textMargin * 2
        self.height = self.label.textheight + textMargin * 2
        self.func = attributes.func
        self.args = attributes.args or ()

    def OnMouseEnter(self, *args):
        self.opacity = self.MOUSEOVER_OPACITY

    def OnMouseExit(self, *args):
        self.opacity = self.IDLE_OPACITY

    def OnClick(self, *args):
        if self.func:
            self.func(self, *self.args)


class IconTextButton(TextButton):

    def ApplyAttributes(self, attributes):
        TextButton.ApplyAttributes(self, attributes)
        size = attributes.iconSize
        self.icon = GlowSprite(texturePath=attributes.texturePath, width=size, height=size, parent=self, state=uiconst.UI_DISABLED, iconOpacity=0.5, gradientStrength=0.5)
        self.label.left += self.icon.width + 2
        self.width += self.icon.width + 2
        self.height = max(self.height, self.icon.height)

    def OnMouseEnter(self, *args):
        TextButton.OnMouseEnter(self, *args)
        uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, self.MOUSEOVER_OPACITY, duration=0.1)

    def OnMouseExit(self, *args):
        TextButton.OnMouseExit(self, *args)
        uicore.animations.MorphScalar(self.icon, 'glowAmount', self.icon.glowAmount, self.IDLE_OPACITY, duration=0.3)

    def OnClick(self, *args):
        TextButton.OnClick(self, *args)


STEP_INTRO = 1
STEP_INTRO2 = 2
STEP_NEXT = 3
STEP_COMPLETED_NEXT = 4
STEP_PRESENT_OPPORTUNITY = 5
STEP_TASK_INFO = 6
STEP_TASK_INFO_MANUAL = 7
STEP_ALL_DONE = 100
FADE_STATE_OUT = 1
FADE_STATE_IN = 2

class WindowTransition(Container):
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        Frame(bgParent=self, color=(1, 1, 1, 0.1))
        self.cornerPoints = FrameThemeColored(name='bgFrame', colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, bgParent=self, texturePath='res:/UI/Texture/Shared/windowFrame.png', cornerSize=10, fillCenter=False, padding=1, opacity=0.5)
        self.whiteFill = Fill(bgParent=self, color=(1, 1, 1, 0))


class AchievementAuraWindow(Window):
    default_captionLabelPath = 'UI/Achievements/OpportunitiesHint'
    default_windowID = 'AchievementAuraWindow'
    default_width = WINDOW_WIDTH
    default_fixedWidth = default_width
    default_height = 160
    default_fixedHeight = default_height
    default_left = 370
    default_top = '__center__'
    default_topParentHeight = 0
    default_isCollapseable = False
    aura = None
    activeStep = None
    animHeight = 0
    transitionBox = None
    fadeoutState = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnMinimizable()
        self.MakeUnpinable()
        self.MakeUnstackable()
        mainArea = self.GetMainArea()
        mainArea.clipChildren = True
        leftSide = Container(parent=mainArea, align=uiconst.TOLEFT, width=AURA_SIZE * 0.8)
        auraSprite = Sprite(parent=leftSide, texturePath='res:/UI/Texture/classes/achievements/auraAlpha.png', pos=(0,
         -4,
         AURA_SIZE,
         AURA_SIZE), align=uiconst.CENTERTOP)
        self.mainContent = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.TOTOP, alignMode=uiconst.TOTOP, padding=(0, 6, 10, 10))
        self.opacity = 0.0
        self.fadeoutState = FADE_STATE_OUT
        self.sizeTimer = AutoTimer(10, self.UpdateWindowSize)
        if not settings.char.ui.Get('opportunities_aura_introduced', False):
            settings.char.ui.Set('opportunities_aura_introduced', True)
            self.Step_Intro()
        elif attributes.loadAchievementTask:
            self.Step_TaskInfo_Manual(attributes.loadAchievementTask, attributes.loadAchievementGroup)
        else:
            self.UpdateOpportunityState()

    def OpenOpportunitiesTree(self, *args):
        from achievements.client.achievementTreeWindow import AchievementTreeWindow
        AchievementTreeWindow.Open()
        sm.GetService('experimentClientSvc').LogWindowOpenedActions('OpportunityWindowAuraWindow')
        self.FadeOutTransitionAndClose()

    def Prepare_HeaderButtons_(self, *args, **kwds):
        Window.Prepare_HeaderButtons_(self, *args, **kwds)

    def UpdateWindowSize(self):
        if self.destroyed:
            self.sizeTimer = None
            return
        headerHeight = self.GetCollapsedHeight()
        newheight = max(WINDOW_MIN_HEIGHT, headerHeight + self.mainContent.height + self.mainContent.padTop + self.mainContent.padBottom)
        if newheight != self.height:
            self.height = newheight
            self.SetFixedHeight(self.height)
            if self.transitionBox and not self.transitionBox.destroyed:
                self.transitionBox.height = newheight

    def CloseByUser(self, *args, **kwds):
        Window.CloseByUser(self, *args, **kwds)
        if self.activeStep == STEP_TASK_INFO:
            settings.char.ui.Set('opportunities_suppress_taskinfo', True)
            return
        self.ResetActiveAchievementGroup(self.activeStep)

    def FadeOutTransitionAndClose(self, *args, **kwds):
        self.FadeOutTransition()
        activeStep = self.activeStep
        self.Close()
        self.ResetActiveAchievementGroup(activeStep)

    def ResetActiveAchievementGroup(self, activeStep):
        if activeStep in (STEP_INTRO,
         STEP_INTRO2,
         STEP_COMPLETED_NEXT,
         STEP_PRESENT_OPPORTUNITY):
            sm.GetService('achievementSvc').SetActiveAchievementGroupID(None)

    def FadeOutTransition(self):
        if not self.opacity or self.fadeoutState == FADE_STATE_OUT:
            return
        self.fadeoutState = FADE_STATE_OUT
        timeScale = 1.0
        wasCacheContent = self.cacheContents
        self.cacheContents = False
        l, t, w, h = self.GetAbsolute()
        transform = Transform(parent=self.parent, state=uiconst.UI_DISABLED, align=uiconst.TOALL, scalingCenter=(float(l + w / 2) / uicore.desktop.width, float(t + h / 2) / uicore.desktop.height), scaling=(1.0, 1.0), idx=self.parent.children.index(self))
        self.SetParent(transform)
        self.transitionBox = WindowTransition(parent=transform, pos=self.pos)
        uicore.animations.BlinkOut(self.transitionBox.cornerPoints, loops=5, duration=0.3 * timeScale)
        uicore.animations.FadeOut(self, duration=0.2 * timeScale, sleep=True)
        uicore.animations.FadeTo(self.transitionBox.whiteFill, startVal=0.2, endVal=0.05, duration=0.1 * timeScale, sleep=True)
        uicore.animations.SpColorMorphTo(self.transitionBox.whiteFill, startColor=(0, 0, 0, 0.1), endColor=(1, 1, 1, 0.1), duration=0.1 * timeScale)
        uicore.animations.Tr2DScaleTo(transform, startScale=(1.0, 1.0), endScale=(1.0, 0.0), duration=0.3 * timeScale, sleep=True)
        if not self.destroyed:
            self.SetParent(uicore.layer.main, idx=0)
            self.cacheContents = wasCacheContent
        transform.Close()

    def FadeInTransition(self):
        if self.fadeoutState == FADE_STATE_IN:
            return
        self.fadeoutState = FADE_STATE_IN
        uthread.new(self._FadeInTransition)

    def _FadeInTransition(self):
        timeScale = 1.0
        wasCacheContent = self.cacheContents
        self.cacheContents = False
        self.opacity = 0.0
        l, t, w, h = self.GetAbsolute()
        transform = Transform(parent=self.parent, state=uiconst.UI_DISABLED, align=uiconst.TOALL, scalingCenter=(float(l + w / 2) / uicore.desktop.width, float(t + h / 2) / uicore.desktop.height), scaling=(1.0, 0.0), idx=self.parent.children.index(self))
        self.SetParent(transform)
        self.transitionBox = WindowTransition(parent=transform, pos=self.pos)
        uicore.animations.Tr2DScaleTo(transform, startScale=(1.0, 0.0), endScale=(1.0, 1.0), duration=0.2 * timeScale)
        uicore.animations.FadeTo(self.transitionBox.whiteFill, startVal=0.2, endVal=0.5, sleep=True, duration=0.1 * timeScale)
        uicore.animations.SpColorMorphTo(self.transitionBox.whiteFill, startColor=(1, 1, 1, 0.125), endColor=(0, 0, 0, 0.25), sleep=True, duration=0.1 * timeScale)
        uicore.animations.BlinkIn(self.transitionBox.cornerPoints, loops=5, duration=0.3 * timeScale)
        uicore.animations.FadeIn(self, duration=0.3 * timeScale, sleep=True)
        if not self.destroyed:
            self.SetParent(uicore.layer.main, idx=0)
            self.cacheContents = wasCacheContent
        transform.Close()

    def TriggerForcedGroup(self, forcedGroup):
        activeGroup = GetActiveAchievementGroup()
        if activeGroup != forcedGroup:
            self.Step_PresentOpportunity(groupToPresent=forcedGroup)

    def Step_Intro(self):
        self.FadeOutTransition()
        self.mainContent.Flush()
        self.LoadMediumText(GetByLabel('Achievements/AuraText/intro'), padRight=8)
        self.LoadButtons(((GetByLabel('Achievements/UI/Accept'), self.Step_PresentOpportunity, None), (GetByLabel('Achievements/UI/Dismiss'), self.FadeOutTransitionAndClose, None)))
        self.LoadTreeLink()
        self.SetOrder(0)
        self.activeStep = STEP_INTRO
        settings.char.ui.Set('opportunities_suppress_taskinfo', False)
        self.FadeInTransition()

    def Step_AskStart(self):
        self.FadeOutTransition()
        self.mainContent.Flush()
        self.LoadLargeText(GetByLabel('Achievements/AuraText/IntroAfterDismissHeader'))
        self.LoadMediumText(GetByLabel('Achievements/AuraText/IntroAfterDismissText'))
        self.LoadButtons(((GetByLabel('Achievements/UI/Accept'), self.Step_PresentOpportunity, None), (GetByLabel('Achievements/UI/Dismiss'), self.FadeOutTransitionAndClose, None)))
        self.LoadTreeLink()
        self.SetCaption(GetByLabel('UI/Achievements/OpportunitiesHint'))
        self.SetOrder(0)
        self.activeStep = STEP_INTRO2
        self.FadeInTransition()

    def Step_ActiveCompleted(self):
        self.FadeOutTransition()
        self.mainContent.Flush()
        self.LoadLargeText(GetByLabel('Achievements/AuraText/CompletedReactivatedHeader'))
        self.LoadMediumText(GetByLabel('Achievements/AuraText/CompletedReactivatedText'))
        self.LoadButtons(((GetByLabel('Achievements/UI/Accept'), self.Step_PresentOpportunity, None), (GetByLabel('Achievements/UI/Dismiss'), self.FadeOutTransitionAndClose, None)))
        self.LoadTreeLink()
        self.SetCaption(GetByLabel('UI/Achievements/OpportunitiesHint'))
        self.SetOrder(0)
        self.activeStep = STEP_COMPLETED_NEXT
        self.FadeInTransition()

    def Step_PresentOpportunity(self, btn = None, groupToPresent = None, *args):
        if groupToPresent:
            nextGroup = groupToPresent
        else:
            nextGroup = GetFirstIncompleteAchievementGroup()
        if not nextGroup:
            return self.Step_AllDone()
        self.FadeOutTransition()
        self.mainContent.Flush()
        self.LoadLargeText(GetByLabel(nextGroup.groupName))
        self.LoadDivider()
        self.LoadMediumText(GetByLabel(nextGroup.groupDescription))
        self.LoadButtons(((GetByLabel('Achievements/UI/Accept'), self.ActivateNextIncompleteOpportunity, (False, groupToPresent)), (GetByLabel('Achievements/UI/Dismiss'), self.FadeOutTransitionAndClose, None)))
        self.LoadTreeLink()
        self.SetCaption(GetByLabel('Achievements/UI/NewOpportunity'))
        self.SetOrder(0)
        self.activeStep = STEP_PRESENT_OPPORTUNITY
        self.FadeInTransition()

    def Step_TaskInfo(self, achievementTask, activeGroup, manualLoad = False):
        self.FadeOutTransition()
        self.mainContent.Flush()
        if activeGroup:
            self.SetCaption(GetByLabel(activeGroup.groupName))
        self.LoadLargeText(achievementTask.name)
        self.LoadDivider()
        self.LoadMediumText(achievementTask.description)
        extraInfo = ACHIEVEMENT_TASK_EXTRAINFO.get(achievementTask.achievementID, None)
        if extraInfo:
            grid = LayoutGrid(parent=self.mainContent, align=uiconst.TOTOP, cellPadding=2, columns=2)
            for taskInfoEntry in extraInfo:
                if isinstance(taskInfoEntry, TaskInfoEntry_Text):
                    label = EveLabelMedium(text=taskInfoEntry.text, color=taskInfoEntry.textColor, width=200)
                    grid.AddCell(label, colSpan=2)
                elif isinstance(taskInfoEntry, TaskInfoEntry_ImageText):
                    texturePath = taskInfoEntry.GetTexturePath()
                    icon = Sprite(name='icon', parent=grid, pos=(0,
                     0,
                     taskInfoEntry.imageSize,
                     taskInfoEntry.imageSize), texturePath=texturePath, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=taskInfoEntry.imageColor)
                    text = GetByLabel(taskInfoEntry.textPath)
                    label = EveLabelMedium(text=text, color=taskInfoEntry.textColor, width=180, align=uiconst.CENTERLEFT)
                    grid.AddCell(label)

        self.LoadTreeLink()
        self.SetOrder(0)
        settings.char.ui.Set('opportunities_suppress_taskinfo', False)
        if manualLoad:
            self.activeStep = STEP_TASK_INFO_MANUAL
        else:
            self.activeStep = STEP_TASK_INFO
        self.FadeInTransition()

    def Step_TaskInfo_Manual(self, achievementTask, achievementGroup):
        self.Step_TaskInfo(achievementTask, achievementGroup, manualLoad=True)

    def Step_AllDone(self):
        self.FadeOutTransition()
        self.mainContent.Flush()
        self.LoadLargeText(GetByLabel('Achievements/AuraText/AllCompletedHeader'))
        self.LoadMediumText(GetByLabel('Achievements/AuraText/AllCompletedText'))
        self.LoadButtons(((GetByLabel('Achievements/UI/Accept'), self.ActivateCareerFunnel, (False,)), (GetByLabel('Achievements/UI/Dismiss'), self.FadeOutTransitionAndClose, None)))
        self.SetCaption(GetByLabel('UI/Achievements/OpportunitiesHint'))
        self.SetOrder(0)
        self.activeStep = STEP_ALL_DONE
        self.FadeInTransition()

    def ActivateNextIncompleteOpportunity(self, emphasize, groupToPresent = None, **kwargs):
        if groupToPresent:
            nextGroup = groupToPresent
        else:
            nextGroup = GetFirstIncompleteAchievementGroup()
        if nextGroup:
            if True:
                self.FadeOutTransitionAndClose()
            done = settings.char.ui.Get('opportunities_aura_activated', [])
            if nextGroup.groupID not in done:
                done.append(nextGroup.groupID)
            settings.char.ui.Set('opportunities_aura_activated', done)
            sm.GetService('achievementSvc').SetActiveAchievementGroupID(nextGroup.groupID, emphasize=emphasize)
        else:
            self.UpdateOpportunityState()

    def ActivateCareerFunnel(self, *args):
        self.FadeOutTransitionAndClose()
        sm.GetService('achievementSvc').SetActiveAchievementGroupID(None)
        sm.StartService('tutorial').ShowCareerFunnel()

    def UpdateOpportunityState(self, activeGroupChanged = False, activeGroupCompleted = False):
        activeGroup = GetActiveAchievementGroup()
        nextGroup = GetFirstIncompleteAchievementGroup()
        if activeGroup:
            if nextGroup:
                if activeGroupCompleted:
                    self.Step_PresentOpportunity()
                return
        elif nextGroup:
            if self.activeStep not in (STEP_INTRO, STEP_INTRO2, STEP_PRESENT_OPPORTUNITY):
                self.Step_AskStart()
            return
        self.Step_AllDone()

    def LoadDivider(self):
        divider = Sprite(parent=self.mainContent, height=1, align=uiconst.TOTOP, texturePath='res:/UI/Texture/classes/achievements/divider_horizontal.png', color=(1, 1, 1, 0.3), padding=(0, 2, 0, 2))

    def LoadLargeText(self, text, *args, **kwargs):
        label = Label(parent=self.mainContent, text=text, align=uiconst.TOTOP, fontsize=18, color=(1, 1, 1, 1), **kwargs)

    def LoadMediumText(self, text, *args, **kwargs):
        label = EveLabelMedium(parent=self.mainContent, text=text, align=uiconst.TOTOP, **kwargs)

    def LoadButton(self, label, func, args = None):
        buttonContainer = Container(parent=self.mainContent, align=uiconst.TOTOP)
        button = Button(parent=buttonContainer, label=label, func=func, args=args, align=uiconst.CENTERLEFT)
        buttonContainer.height = button.height + 8

    def LoadButtons(self, buttonData):
        buttonContainer = FlowContainer(parent=self.mainContent, align=uiconst.TOTOP, padTop=14, contentSpacing=(4, 4), contentAlignment=CONTENT_ALIGN_RIGHT)
        for label, func, args in buttonData:
            button = Button(parent=buttonContainer, label=label, func=func, args=args, align=uiconst.NOALIGN)

    def LoadTreeLink(self):
        buttonContainer = ContainerAutoSize(parent=self.mainContent, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
        textButton = IconTextButton(parent=buttonContainer, align=uiconst.TOPLEFT, label=GetByLabel('Achievements/UI/showAll'), texturePath='res:/ui/Texture/Classes/InfoPanels/opportunitiesTreeIcon.png', func=self.OpenOpportunitiesTree, iconSize=16, top=10)
        settingControl = OpportunitiesSettingsMenu(parent=self.GetMainArea(), align=uiconst.BOTTOMRIGHT, top=6, left=6)


class WindowUnderlayCustom(Container):
    default_name = 'underlay'
    default_state = uiconst.UI_DISABLED
    default_padLeft = 1
    default_padTop = 1
    default_padRight = 1
    default_padBottom = 1
    __notifyevents__ = ['OnCameraDragStart', 'OnCameraDragEnd']
    isCameraDragging = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.frame = FrameThemeColored(name='bgFrame', colorType=attributes.frameColorType or uiconst.COLORTYPE_UIHILIGHTGLOW, bgParent=self, texturePath=attributes.frameTexturePath, cornerSize=attributes.frameCornerSize or 0, offset=attributes.frameOffset or 0, fillCenter=attributes.frameFillCenter or False, opacity=attributes.frameOpacity or 0.5)
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASE, texturePath=attributes.fillTexturePath, cornerSize=attributes.fillCornerSize or 0, offset=attributes.fillOffset or 0, fillCenter=attributes.fillFillCenter or False, opacity=attributes.fillOpacity or 0.1)
        sm.RegisterNotify(self)

    def AnimEntry(self):
        uicore.animations.FadeTo(self.frame, self.frame.opacity, 1.0, duration=0.4, curveType=uiconst.ANIM_OVERSHOT3)

    def AnimExit(self):
        uicore.animations.FadeTo(self.frame, self.frame.opacity, 0.5, duration=0.6)

    def OnCameraDragStart(self):
        pass

    def OnCameraDragEnd(self):
        pass

    def Pin(self):
        pass

    def UnPin(self):
        pass
