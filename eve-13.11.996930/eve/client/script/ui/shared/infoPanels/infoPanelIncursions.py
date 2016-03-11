#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelIncursions.py
import uicls
import carbonui.const as uiconst
import blue
import base
import uiprimitives
import util
import trinity
import localization
import infoPanelConst
import talecommon as taleCommon
import uthread
import uicontrols
from talecommon.const import scenesTypes, INCURSION_TEMPLATES
SEVERITY = {scenesTypes.staging: util.KeyVal(severityIcon='', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaStaging.png', hint='UI/Incursion/HUD/StagingClassHint', subTitle='UI/Incursion/HUD/SubtitleStaging'),
 scenesTypes.vanguard: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionLightInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaLight.png', hint='UI/Incursion/HUD/VanguardClassHint', subTitle='UI/Incursion/HUD/SubtitleVanguard'),
 scenesTypes.assault: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionMediumInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaMedium.png', hint='UI/Incursion/HUD/AssaultClassHint', subTitle='UI/Incursion/HUD/SubtitleAssault'),
 scenesTypes.headquarters: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaHeavy.png', hint='UI/Incursion/HUD/HeadquarterClassHint', subTitle='UI/Incursion/HUD/SubtitleHeadquarters'),
 scenesTypes.boss: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionSanshaHeavy.png', hint='UI/Incursion/HUD/HeadquarterClassHint', subTitle='UI/Incursion/HUD/SubtitleHeadquarters'),
 scenesTypes.incursionStaging: util.KeyVal(severityIcon='', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersStaging.png', hint='UI/Incursion/HUD/IncursionStagingClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionStaging'),
 scenesTypes.incursionLightInfestation: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionLightInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersLight.png', hint='UI/Incursion/HUD/IncursionLightInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionLightInfestation'),
 scenesTypes.incursionMediumInfestation: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionMediumInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersMedium.png', hint='UI/Incursion/HUD/IncursionMediumInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionMediumInfestation'),
 scenesTypes.incursionHeavyInfestation: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersHeavy.png', hint='UI/Incursion/HUD/IncursionHeavyInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionHeavyInfestation'),
 scenesTypes.incursionFinalEncounter: util.KeyVal(severityIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionHeavyInfestation.png', corpIcon='res:/UI/Texture/classes/InfoPanels/taleIncursionDriftersHeavy.png', hint='UI/Incursion/HUD/IncursionHeavyInfestationClassHint', subTitle='UI/Incursion/HUD/SubtitleIncursionHeavyInfestation')}
ARROWS = ('ui_77_32_41', 'ui_77_32_42')
EFFECT_SPACING = 16
COLOR_ENABLED = (1, 1, 1, 0.75)
COLOR_DISABLED = (1, 1, 1, 0.25)
INCURSION_UPDATE_RATE = 60000

class InfoPanelIncursions(uicls.InfoPanelBase):
    __guid__ = 'uicls.InfoPanelIncursions'
    default_name = 'InfoPanelIncursions'
    hasSettings = False
    panelTypeID = infoPanelConst.PANEL_INCURSIONS
    label = 'UI/Incursion/HUD/IncursionProfileTitle'
    default_iconTexturePath = 'res:/UI/Texture/Classes/InfoPanels/taleDefaultIcon.png'
    default_severity = scenesTypes.vanguard
    default_height = 120
    __notifyevents__ = ['OnInfluenceUpdate', 'ProcessUpdateInfoPanel']

    def ApplyAttributes(self, attributes):
        uicls.InfoPanelBase.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.lastInfluence = None
        self.headerTextCont = uiprimitives.Container(name='headerTextCont', parent=self.headerCont, align=uiconst.TOALL)
        self.title = self.headerCls(name='title', text='<color=white url=localsvc:service=journal&method=ShowIncursionTab&constellationID=%d&open=1>%s</url>' % (session.constellationid, localization.GetByLabel(self.label)), parent=self.headerTextCont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL)
        self.subTitle = uicontrols.EveHeaderMedium(name='subtitle', parent=self.headerTextCont, left=self.title.width + 4, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, top=3)
        self.finalEncounterIcon = IncursionFinalEncounterIcon(name='finalEncounterIcon', parent=self.headerCont, align=uiconst.CENTERRIGHT, left=8)
        self.headerInfluenceBar = uicls.SystemInfluenceBar(parent=self.headerCont, state=uiconst.UI_HIDDEN, align=uiconst.TOALL, height=0, padding=(0, 6, 24, 6))
        self.headerInfluenceBar.OnClick = self.topCont.OnClick
        self.headerInfluenceBar.OnMouseEnter = self.topCont.OnMouseEnter
        self.headerInfluenceBar.OnMouseExit = self.topCont.OnMouseExit
        self.influenceBar = uicls.SystemInfluenceBar(parent=self.mainCont, padding=(0, 0, 0, 2))
        self.bottomContainer = uiprimitives.Container(name='bottomContainer', parent=self.mainCont, align=uiconst.TOTOP, height=33)
        self.severityIcon = uicontrols.Icon(name='severityIcon', parent=self.bottomContainer, align=uiconst.RELATIVE, color=COLOR_ENABLED, pos=(0, 10, 32, 32), ignoreSize=True, size=48, state=uiconst.UI_NORMAL)
        self.corpIcon = uicontrols.Icon(name='corpIcon', parent=self.bottomContainer, align=uiconst.RELATIVE, color=COLOR_ENABLED, pos=(35, 10, 32, 32), ignoreSize=True, size=48, state=uiconst.UI_NORMAL)
        iconCont = uicontrols.ContainerAutoSize(name='iconCont', parent=self.bottomContainer, align=uiconst.CENTERLEFT, pos=(70, 0, 0, 22))
        iconParams = {'align': uiconst.TOLEFT,
         'parent': iconCont,
         'color': COLOR_ENABLED,
         'width': iconCont.height,
         'padRight': 6}
        self.effects = self._GetEffectsForTale(iconParams)
        uthread.new(self.UpdateInfluenceThread)

    def _GetEffectsForTale(self, iconParams):
        data = sm.GetService('incursion').GetActiveIncursionData()
        if not hasattr(data, 'effects'):
            return []
        return [ TaleSystemEffect(effectInfo, iconParams) for effectInfo in data.effects ]

    def ConstructCompact(self):
        data = sm.GetService('incursion').GetActiveIncursionData()
        self._SetFinalEncounterSpawned(data.hasFinalEncounter, data.templateClassID)
        influence = taleCommon.CalculateDecayedInfluence(data.influenceData)
        self.SetInfluence(influence, None, animate=False)

    def ConstructNormal(self):
        data = sm.GetService('incursion').GetActiveIncursionData()
        info = SEVERITY[data.severity]
        influence = taleCommon.CalculateDecayedInfluence(data.influenceData)
        self.subTitle.text = localization.GetByLabel(info.subTitle)
        self.severityIcon.LoadIcon(info.severityIcon, ignoreSize=True)
        self.severityIcon.hint = localization.GetByLabel(info.hint)
        self.corpIcon.LoadIcon(info.corpIcon, ignoreSize=True)
        self.corpIcon.hint = localization.GetByLabel(info.hint)
        self._SetFinalEncounterSpawned(data.hasFinalEncounter, data.templateClassID)
        self.SetInfluence(influence, None, animate=False)
        self.severityIcon.opacity = 0.0
        self.corpIcon.opacity = 0.0
        for effect in self.effects:
            icon = effect.GetIcon()
            icon.opacity = 0.0

    def OnEndModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_NORMAL and oldMode:
            uicore.animations.BlinkIn(self.severityIcon)
            uicore.animations.BlinkIn(self.corpIcon)
            blue.synchro.SleepWallclock(200)
            for effect in self.effects:
                icon = effect.GetIcon()
                uicore.animations.BlinkIn(icon, endVal=COLOR_ENABLED[3])
                blue.synchro.SleepWallclock(50)

        else:
            self.severityIcon.opacity = 1.0
            self.corpIcon.opacity = 1.0
            for effect in self.effects:
                icon = effect.GetIcon()
                icon.opacity = COLOR_ENABLED[3]

    def OnStartModeChanged(self, oldMode):
        uthread.new(self._OnStartModeChanged, oldMode)

    def _OnStartModeChanged(self, oldMode):
        if self.mode == infoPanelConst.MODE_COMPACT:
            if oldMode:
                uicore.animations.FadeOut(self.headerTextCont, duration=0.3, sleep=True)
                self.headerTextCont.Hide()
                self.headerInfluenceBar.Show()
                uicore.animations.FadeTo(self.headerInfluenceBar, 0.0, 1.0, duration=0.3)
            else:
                self.headerTextCont.Hide()
                self.headerInfluenceBar.Show()
        elif self.headerInfluenceBar.display:
            uicore.animations.FadeOut(self.headerInfluenceBar, duration=0.3, sleep=True)
            self.headerInfluenceBar.Hide()
            self.headerTextCont.Show()
            uicore.animations.FadeTo(self.headerTextCont, 0.0, 1.0, duration=0.3)

    @staticmethod
    def IsAvailable():
        return sm.GetService('incursion').IsIncursionActive()

    def UpdateInfluenceThread(self):
        while not self.destroyed:
            newInfluence = None
            data = sm.GetService('incursion').GetActiveIncursionData()
            if data:
                newInfluence = taleCommon.CalculateDecayedInfluence(data.influenceData)
                if self.lastInfluence is None or self.lastInfluence != newInfluence:
                    self.SetInfluence(newInfluence, False, True)
            blue.pyos.synchro.SleepWallclock(INCURSION_UPDATE_RATE)

    def SetInfluence(self, influence, positiveProgress, animate = True):
        self.influenceBar.SetInfluence(influence, positiveProgress, animate)
        self.headerInfluenceBar.SetInfluence(influence, positiveProgress, animate)
        for effect in self.effects:
            icon = effect.GetIcon()
            if not effect.IsEffectScalable():
                icon.color.SetRGB(*COLOR_ENABLED)
                continue
            if influence < 1.0:
                icon.color.SetRGB(*COLOR_ENABLED)
            else:
                icon.color.SetRGB(*COLOR_DISABLED)

        self.lastInfluence = influence

    def OnInfluenceUpdate(self, taleID, newInfluenceData):
        data = sm.GetService('incursion').GetActiveIncursionData()
        if data and data.taleID == taleID:
            influenceData = data.influenceData
            oldInfluence = taleCommon.CalculateDecayedInfluence(influenceData)
            influenceData.influence = newInfluenceData.influence
            influenceData.lastUpdated = newInfluenceData.lastUpdated
            newInfluence = taleCommon.CalculateDecayedInfluence(influenceData)
            positiveProgress = oldInfluence < newInfluence
            self.SetInfluence(newInfluence, positiveProgress)

    def _SetFinalEncounterSpawned(self, hasSpawned, templateClassId):
        if templateClassId in INCURSION_TEMPLATES:
            self.finalEncounterIcon.SetFinalEncounterSpawned(hasSpawned)


class IncursionFinalEncounterIcon(uiprimitives.Sprite):
    __guid__ = 'uicls.IncursionFinalEncounterIcon'
    default_name = 'finalEncounterIcon'
    default_texturePath = 'res:/UI/Texture/Icons/skullCrossBones10.png'
    default_state = uiconst.UI_NORMAL
    default_width = 10
    default_height = 10

    def SetFinalEncounterSpawned(self, hasSpawned):
        self.SetHint(localization.GetByLabel('UI/Incursion/HUD/IncursionFinalEncounterReportHint') if hasSpawned else localization.GetByLabel('UI/Incursion/HUD/NoIncursionFinalEncounterHint'))
        self.color.SetRGB(*(COLOR_ENABLED if hasSpawned else COLOR_DISABLED))


class BarFill(uiprimitives.Sprite):
    __guid__ = 'uicls.BarFill'
    default_name = 'BarFill'
    default_rect = (0, 0, 0, 32)
    default_texturePath = 'res:/ui/texture/classes/InfluenceBar/influenceBarDefault.png'
    default_slice = None
    default_state = uiconst.UI_HIDDEN
    default_align = uiconst.RELATIVE
    default_spriteEffect = trinity.TR2_SFX_COPY
    TEX_SIZE = 134

    def ApplyAttributes(self, attributes):
        uiprimitives.Sprite.ApplyAttributes(self, attributes)
        slice = attributes.get('slice', self.default_slice)
        if slice is not None:
            self.SetTextureSlice(slice)

    def SetTextureSlice(self, slice):
        self.SetTexturePath(slice)

    def SetBar(self, delta):
        if not self.parent:
            return
        ppl, ppt, mainBarWidth, h = self.parent.parent.GetAbsolute()
        pl, pt, parentWidth, h = self.parent.GetAbsolute()
        barOffset = pl - ppl
        self.left = int(-barOffset + mainBarWidth - round(mainBarWidth * delta))
        self.width = mainBarWidth


class SystemInfluenceBar(uiprimitives.Container):
    __guid__ = 'uicls.SystemInfluenceBar'
    default_name = 'SystemInfluenceBar'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 12
    default_influence = 0.0
    default_align = uiconst.TOTOP
    default_padTop = 4
    default_padBottom = 4
    default_state = uiconst.UI_NORMAL
    default_clipChildren = False
    FRAME_COLOR = (0.5, 0.5, 0.5, 1.0)
    TEX_WIDTH = 256
    PADDING = (0, 4, 0, 4)
    ARROW_HEIGHT = 32
    LEFT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarNegative.png'
    RIGHT_SLICE = 'res:/ui/texture/classes/InfluenceBar/influenceBarPositive.png'

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        l, t, w, h = self.GetAbsolute()
        self.influence = attributes.get('influence', 0.0)
        self.targetInfluence = self.influence
        self.blueBar = uiprimitives.Container(parent=self, name='blueBar', align=uiconst.TOLEFT_PROP, width=0, clipChildren=True)
        uiprimitives.Fill(name='blueBase', parent=self.blueBar, color=(0, 0, 1, 0.25))
        self.blueArrows = uicls.BarFill(name='blueFill', pos=(0,
         0,
         w,
         h), parent=self.blueBar, color=(0, 0, 1, 0.75))
        self.knob = uiprimitives.Line(parent=self, name='sliderKnob', color=self.FRAME_COLOR, align=uiconst.TOLEFT)
        self.redBar = uiprimitives.Container(parent=self, name='redBar', align=uiconst.TOALL, clipChildren=True)
        uiprimitives.Fill(name='redBase', parent=self.redBar, color=(1, 0, 0, 0.25))
        self.redArrows = uicls.BarFill(pos=(0,
         0,
         w,
         h), name='redFill', parent=self.redBar, color=(1, 0, 0, 0.75))

    def SetInfluence(self, influence, positiveProgress, animate = True):
        self.SetHint(localization.GetByLabel('UI/Incursion/HUD/InfluenceBarHint', influence=int(round((1.0 - influence) * 100))))
        if animate:
            self.targetInfluence = influence
            self.animationTimer = base.AutoTimer(100, self.Animation_Thread, positiveProgress)
        else:
            self.influence = self.targetInfluence = influence
            self.blueBar.width = influence

    def Animation_Thread(self, positiveProgress):
        l, t, w, h = self.GetAbsolute()
        totalWidth = w - self.knob.width
        count = 5
        if positiveProgress is None:
            moveFunc = None
            self.blueArrows.state = uiconst.UI_HIDDEN
            self.redArrows.state = uiconst.UI_HIDDEN
        elif positiveProgress:
            moveFunc = self.MoveRight
            self.blueArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.RIGHT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        else:
            moveFunc = self.MoveLeft
            self.blueArrows.SetTextureSlice(self.LEFT_SLICE)
            self.blueArrows.state = uiconst.UI_DISABLED
            self.redArrows.SetTextureSlice(self.LEFT_SLICE)
            self.redArrows.state = uiconst.UI_DISABLED
        while count > 0:
            start = blue.os.GetWallclockTime()
            lastDelta = delta = 0.0
            while delta < 2.0:
                delta = max(0.0, min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 1000.0, 2.0))
                dt = delta - lastDelta
                if self.targetInfluence > self.influence:
                    self.influence = min(self.influence + 0.25 * dt, self.targetInfluence)
                else:
                    self.influence = max(self.influence - 0.25 * dt, self.targetInfluence)
                self.blueBar.width = self.influence
                if moveFunc:
                    moveFunc(delta)
                lastDelta = delta
                blue.pyos.synchro.Yield()
                if not self or self.destroyed:
                    return

            count -= 1

        self.animationTimer = None

    def MoveRight(self, delta):
        self.blueArrows.SetBar(2.0 - delta)
        self.redArrows.SetBar(2.0 - delta)

    def MoveLeft(self, delta):
        self.blueArrows.SetBar(delta)
        self.redArrows.SetBar(delta)


class TaleSystemEffect(object):

    def __init__(self, effectInfo, iconParams):
        self.icon = uiprimitives.Sprite(name=effectInfo['name'], texturePath=effectInfo['texturePath'], hint=localization.GetByLabel(effectInfo['hint']), **iconParams)
        self.isScalable = effectInfo['isScalable']

    def GetIcon(self):
        return self.icon

    def IsEffectScalable(self):
        return self.isScalable
