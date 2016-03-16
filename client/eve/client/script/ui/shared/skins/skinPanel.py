#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\skinPanel.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionSmall, EveLabelSmall
from eve.client.script.ui.control.themeColored import FillThemeColored, GradientThemeColored, LabelThemeColored
from eve.client.script.ui.shared.market.marketbase import RegionalMarket
from eve.client.script.ui.shared.skins.buyButton import SkinMaterialBuyButtonAur, SkinMaterialBuyButtonIsk
from eve.client.script.ui.shared.skins.controller import SkinNotAvailableForType
from eve.client.script.ui.shared.skins.devMenuFunctions import GiveSkin, GivePermanentSkin, RemoveSkin
from eve.client.script.ui.shared.skins.event import LogBuySkinIsk
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
import evetypes
from inventorycommon.const import typeSkinMaterial
import localization
import locks
import logging
import math
from service import ROLE_GMH
import sys
import uthread
ENTRY_DEFAULT_HEIGHT = 54
ENTRY_DEFAULT_WIDTH = 240
ENTRY_EXPANDED_WIDTH = 260
log = logging.getLogger(__name__)

class SkinPanel(ScrollContainer):
    default_settingsPrefix = 'SkinPanel'

    def ApplyAttributes(self, attributes):
        super(SkinPanel, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.settingsPrefix = attributes.settingsPrefix or self.default_settingsPrefix
        self._logContext = attributes.get('logContext', None)
        self.whatchlist = []
        self.ghosts = []
        self.loaded = False
        self._loadingLock = locks.Lock()
        self.Layout()
        self.controller.onSkinsChange.connect(self.OnSkinsChange)

    def Layout(self):
        self.ghostClip = Container(name='ghostClip', parent=self.clipCont, clipChildren=True)
        self.mainCont.SetParent(self.ghostClip)
        self.ghostCont = ContainerAutoSize(parent=self.clipCont, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, clipChildren=True)
        self.ghostList = FlowContainer(parent=self.ghostCont, align=uiconst.TOPLEFT, width=ENTRY_EXPANDED_WIDTH, contentSpacing=(0, 4), idx=0)
        self.ghostShadow = GradientSprite(parent=self.ghostClip, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, height=12, width=ENTRY_EXPANDED_WIDTH, rgbData=[(0, (0.0, 0.0, 0.0))], alphaData=[(0, 0.0), (0.8, 0.6), (1, 1.0)], rotation=math.pi / 2, opacity=0.0, idx=0)

        def AutoSizeCallback():
            height = self.ghostList.height
            self.mainCont.padTop = -height
            self.ghostClip.padTop = height

        self.ghostCont.callback = AutoSizeCallback

    def Reload(self):
        with self._loadingLock:
            self.loaded = False
            self.Flush()
        self.Load()

    def Load(self):
        if self.loaded:
            return
        with self._loadingLock:
            skins = sorted(self.controller.skins, key=lambda skin: skin.name.lower())
            licensed = [ skin for skin in skins if skin.licensed ]
            licensedLabel = localization.GetByLabel('UI/Skins/LicensedSkins')
            settingName = '%s_LicensedSkins' % self.settingsPrefix
            self.AddSkinGroup(licensedLabel, licensed, settingName=settingName)
            unlicensed = [ skin for skin in skins if not skin.licensed ]
            unlicensedLabel = localization.GetByLabel('UI/Skins/UnlicensedSkins')
            settingName = '%s_UnlicensedSkins' % self.settingsPrefix
            self.AddSkinGroup(unlicensedLabel, unlicensed, settingName=settingName)
            for i, entry in enumerate(self.mainCont.children):
                if hasattr(entry, 'AnimShow') and entry.display:
                    entry.AnimShow(delay=i * 0.05)

            self.loaded = True

    def AddSkinGroup(self, label, skins, settingName = None):
        group = SkinGroupEntry(parent=self, padTop=4, text=label, collapsedSettingName=settingName)
        if len(skins) == 0:
            message = EveCaptionSmall(parent=self, align=uiconst.TOTOP, padding=(25, 12, 0, 20), text=localization.GetByLabel('UI/Skins/NoSkins'), color=(0.5, 0.5, 0.5, 1.0))
            group.AddEntry(message)
        for skin in skins:
            entry = SkinEntrySlot(parent=self, align=uiconst.TOTOP, padTop=4, controller=self.controller, skin=skin, logContext=self._logContext)
            group.AddEntry(entry)

    def OnSkinsChange(self):
        self.Reload()

    def Close(self):
        super(SkinPanel, self).Close()
        self.controller.Close()


class EntryMixin(object):

    def AnimShow(self, delay = 0.0):
        animations.FadeTo(self, duration=0.2, timeOffset=delay)
        animations.MoveInFromTop(self, curveType=uiconst.ANIM_OVERSHOT, duration=0.3, timeOffset=delay)


class SkinEntrySlot(ContainerAutoSize, EntryMixin):
    default_name = 'SkinEntrySlot'
    default_alignMode = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(SkinEntrySlot, self).ApplyAttributes(attributes)
        controller = attributes.controller
        skin = attributes.skin
        logContext = attributes.get('logContext', None)
        self.entry = SkinEntry(parent=self, controller=controller, skin=skin, logContext=logContext)

    def Unplug(self):
        self.DisableAutoSize()
        self.entry.SetParent(None)
        return self.entry

    def Plug(self):
        self.entry.align = uiconst.TOPLEFT
        self.entry.SetParent(self)
        self.EnableAutoSize()

    def GetAbsoluteScrollPosition(self):
        _, top, _, height = self.GetAbsolute()
        return (top, top + height)

    def AnimShow(self, delay = 0.0):
        super(SkinEntrySlot, self).AnimShow(delay=delay)
        if self.entry.parent == self:
            self.entry.AnimShow(delay=delay)


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.2, opacityMouseDown=0.3, bgElementFunc=lambda parent, _: parent.blinkFill, audioOnEntry='wise:/msg_ListEntryEnter_play', audioOnClick='wise:/msg_ListEntryClick_play'))

class SkinEntry(Container):
    default_align = uiconst.TOPLEFT
    default_clipChildren = True
    default_height = ENTRY_DEFAULT_HEIGHT
    default_state = uiconst.UI_NORMAL
    default_width = ENTRY_DEFAULT_WIDTH
    SKIN_ICON_SIZE = 64
    STATE_IDLE = 1
    STATE_APPLIED = 2
    STATE_PENDING = 3
    STATE_PREVIEWED = 4

    def ApplyAttributes(self, attributes):
        super(SkinEntry, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.skin = attributes.skin
        self.skinstate = self.STATE_IDLE
        self._logContext = attributes.get('logContext', None)
        self.Layout()
        self.UpdateSkinState()
        self.controller.onChange.connect(self.UpdateSkinState)

    def Layout(self):
        if self.skin.licensed:
            colorType = uiconst.COLORTYPE_UIHEADER
        else:
            colorType = uiconst.COLORTYPE_UIBASECONTRAST
        FillThemeColored(bgParent=self, padLeft=self.SKIN_ICON_SIZE / 2, colorType=colorType)
        self.iconGlow = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=-5, width=self.SKIN_ICON_SIZE, height=self.SKIN_ICON_SIZE, texturePath='res:/UI/Texture/classes/skins/skin-icon-glow.png', opacity=0.0)
        Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=-5, width=self.SKIN_ICON_SIZE, height=self.SKIN_ICON_SIZE, texturePath=self.skin.iconTexturePath)
        self.iconShadow = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=0, left=28, width=38, height=54, texturePath='res:/UI/Texture/classes/skins/icon-shadow.png')
        if self.skin.licensed:
            color = (0.9, 0.9, 0.9, 1.0)
            top = 6
        else:
            color = (0.4, 0.4, 0.4, 1.0)
            top = 4
        title = EveCaptionSmall(parent=self, left=self.SKIN_ICON_SIZE + 6, top=top, text=self.skin.name, color=color)
        title.SetRightAlphaFade(fadeEnd=ENTRY_DEFAULT_WIDTH - title.left - 4, maxFadeWidth=12)
        if self.skin.licensed:
            duration = SkinDurationLabel(parent=self, left=self.SKIN_ICON_SIZE + 6, top=title.top + title.height, skin=self.skin)
            duration.SetRightAlphaFade(fadeEnd=ENTRY_DEFAULT_WIDTH - duration.left - 4, maxFadeWidth=12)
        else:
            buttonCont = FlowContainer(parent=self, align=uiconst.TOPLEFT, top=title.top + title.height + 2, left=self.SKIN_ICON_SIZE + 7, width=200, contentSpacing=(4, 0))
            SkinMaterialBuyButtonIsk(parent=buttonCont, align=uiconst.NOALIGN, typeID=self.controller.typeID, materialID=self.skin.materialID, logContext=self._logContext)
            SkinMaterialBuyButtonAur(parent=buttonCont, align=uiconst.NOALIGN, typeID=self.controller.typeID, materialID=self.skin.materialID, logContext=self._logContext)
        self.pendingIcon = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=self.height / 2 - 16 / 2, left=ENTRY_DEFAULT_WIDTH + 2, width=16, height=16, texturePath='res:/UI/Texture/classes/skins/pending.png', opacity=0.0)
        animations.MorphScalar(self.pendingIcon, 'rotation', startVal=0.0, endVal=-2 * math.pi, duration=1.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        self.appliedIcon = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=self.height / 2 - 16 / 2, left=ENTRY_DEFAULT_WIDTH + 2, width=16, height=16, texturePath='res:/UI/Texture/classes/skins/applied.png', opacity=0.0)
        self.previewedIcon = Sprite(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=self.height / 2 - 16 / 2, left=ENTRY_DEFAULT_WIDTH + 2, width=16, height=16, texturePath='res:/UI/Texture/classes/skins/previewed.png', opacity=0.0)
        self.stateIconLight = GradientThemeColored(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, rotation=0, alphaData=[(0.0, 0.0),
         (0.25, 0.01),
         (0.5, 0.1),
         (0.6, 0.2),
         (0.7, 0.4),
         (0.8, 0.8),
         (0.9, 1.0)], colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.0)
        if self.skin.licensed:
            colorType = uiconst.COLORTYPE_UIHILIGHT
        else:
            colorType = uiconst.COLORTYPE_UIHEADER
        self.selectionGradient = GradientThemeColored(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, rotation=0, alphaData=[(0.0, 0.0), (0.9, 1.0)], colorType=colorType, opacity=0.0)
        self.blinkFill = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, padLeft=self.SKIN_ICON_SIZE / 2, opacity=0.0)

    def UpdateSkinState(self):
        if self.controller.applied == self.skin:
            self.SetSkinState(self.STATE_APPLIED)
        elif self.controller.pending == self.skin:
            self.SetSkinState(self.STATE_PENDING)
        elif self.controller.previewed == self.skin:
            self.SetSkinState(self.STATE_PREVIEWED)
        else:
            self.SetSkinState(self.STATE_IDLE)

    def SetSkinState(self, state):
        if state == self.skinstate:
            return
        if state == self.STATE_IDLE:
            self.AnimCollapse()
        elif self.skinstate == self.STATE_IDLE:
            self.AnimExpand()
        if state == self.STATE_APPLIED:
            self.AnimStateApplied()
        elif state == self.STATE_PENDING:
            self.AnimStatePending()
        elif state == self.STATE_PREVIEWED:
            self.AnimStatePreviewed()
        elif state == self.STATE_IDLE:
            self.AnimStateIdle()
        self.skinstate = state

    def AnimShow(self, delay = 0.0):
        animations.FadeIn(self.blinkFill, endVal=0.4, curveType=uiconst.ANIM_WAVE, duration=0.4, timeOffset=delay * 1.4 + 0.4)

    def AnimExpand(self):
        animations.MorphScalar(self, 'width', startVal=self.width, endVal=ENTRY_EXPANDED_WIDTH, duration=0.15)
        animations.FadeIn(self.selectionGradient, endVal=0.4, duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        self._AnimShowIconGlow()

    def AnimCollapse(self):
        animations.MorphScalar(self, 'width', startVal=self.width, endVal=ENTRY_DEFAULT_WIDTH, duration=0.1)
        animations.FadeOut(self.selectionGradient, duration=0.1)
        self._AnimHideIconGlow()

    def _AnimShowIconGlow(self):
        self.iconGlow.opacity = 0.1
        animations.SpMaskIn(self.iconGlow, duration=0.4)
        animations.MorphScalar(self.iconShadow, 'left', startVal=self.iconShadow.left, endVal=32, duration=0.2)

    def _AnimHideIconGlow(self):
        animations.FadeOut(self.iconGlow, duration=0.3)
        animations.MorphScalar(self.iconShadow, 'left', startVal=self.iconShadow.left, endVal=28, duration=0.2)

    def AnimStateIdle(self):
        for icon in (self.pendingIcon, self.previewedIcon, self.pendingIcon):
            animations.FadeOut(icon, duration=0.15)

    def AnimStateApplied(self):
        animations.FadeOut(self.pendingIcon, duration=0.15)
        animations.FadeOut(self.previewedIcon, duration=0.15)
        self._AnimShowStateIcon(self.appliedIcon)

    def AnimStatePending(self):
        animations.FadeOut(self.appliedIcon, duration=0.15)
        animations.FadeOut(self.previewedIcon, duration=0.15)
        animations.FadeIn(self.pendingIcon, duration=0.15)

    def AnimStatePreviewed(self):
        animations.FadeOut(self.appliedIcon, duration=0.15)
        animations.FadeOut(self.pendingIcon, duration=0.15)
        self._AnimShowStateIcon(self.previewedIcon)

    def _AnimShowStateIcon(self, icon):

        def continue_glowExpand():
            animations.MorphScalar(icon, 'glowExpand', startVal=0.0, endVal=20.0, duration=0.5, curveType=uiconst.ANIM_SMOOTH)
            animations.SpColorMorphTo(icon, attrName='glowColor', startColor=(1.0, 1.0, 1.0, 0.5), endColor=(0.0, 0.0, 0.0, 0.0), duration=0.25, curveType=uiconst.ANIM_SMOOTH)

        animations.FadeIn(icon, duration=0.15, timeOffset=0.15)
        animations.SpColorMorphTo(icon, startColor=(0.0, 0.0, 0.0, 0.0), endColor=(1.0, 1.0, 1.0, 1.0), duration=0.15, timeOffset=0.2, curveType=uiconst.ANIM_SMOOTH)
        animations.SpColorMorphTo(icon, attrName='glowColor', startColor=(0.3, 0.3, 0.3, 0.0), endColor=(1.0, 1.0, 1.0, 0.5), duration=0.15, timeOffset=0.2, curveType=uiconst.ANIM_SMOOTH)
        animations.MorphScalar(icon, 'glowExpand', startVal=30.0, endVal=0.0, duration=0.2, timeOffset=0.15, curveType=uiconst.ANIM_SMOOTH, callback=continue_glowExpand)
        animations.FadeTo(self.stateIconLight, startVal=0.0, endVal=0.15, duration=0.55, timeOffset=0.15, curveType=uiconst.ANIM_BOUNCE)

    def GetMenu(self):
        entries = []
        gmEntries = self._GetGMMenuEntries()
        if len(gmEntries) > 0:
            entries.extend(gmEntries)
            entries.append(None)
        entries.extend([[localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowMaterialInfo], None, [localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), self.OpenMarketWindow]])
        return entries

    def _GetGMMenuEntries(self):
        if session.role & ROLE_GMH != ROLE_GMH:
            return []
        elif self.skin.skinID is None:
            return [['GM: Give me limited', GiveSkin, (self.skin.materialID, self.controller.typeID)], ['GM: Give me permanently', GivePermanentSkin, (self.skin.materialID, self.controller.typeID)]]
        else:
            return [['GM: Remove SKIN', RemoveSkin, (self.skin.skinID,)]]

    def OpenMarketWindow(self):
        shipName = evetypes.GetName(self.controller.typeID)
        materialName = self.skin.name
        searchString = localization.GetByLabel('UI/Skins/MarketSearchTemplate', shipName=shipName, materialName=materialName)
        RegionalMarket.OpenAndSearch(searchString)
        LogBuySkinIsk(self.controller.typeID, self.skin.materialID, self._logContext)

    def ShowMaterialInfo(self):
        sm.GetService('info').ShowInfo(typeSkinMaterial, itemID=self.skin.materialID)

    def Pick(self):
        try:
            self.controller.PickSkin(self.skin)
        except SkinNotAvailableForType:
            log.warning('PickSkin failed with SkinNotAvailableForType. Most likely due to the shipID changing in the controller before the UI is torn down.')
            sys.exc_clear()

    def OnClick(self, *args):
        self.Pick()


@Component(ButtonEffect(opacityIdle=0.0, opacityHover=0.2, opacityMouseDown=0.3, bgElementFunc=lambda parent, _: parent.hilite, audioOnEntry='wise:/msg_ListEntryEnter_play', audioOnClick='wise:/msg_ListEntryClick_play'))

class SkinGroupEntry(ContainerAutoSize, EntryMixin):
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_PICKCHILDREN
    default_collapsed = False
    default_collapsedSettingName = 'SkinGroupEntry_collapsed'

    def ApplyAttributes(self, attributes):
        super(SkinGroupEntry, self).ApplyAttributes(attributes)
        self.text = attributes.text
        self.collapsedSettingName = attributes.collapsedSettingName or self.default_collapsedSettingName
        self._entries = set()
        self.Layout()

    @property
    def collapsed(self):
        return settings.user.ui.Get(self.collapsedSettingName, self.default_collapsed)

    @collapsed.setter
    def collapsed(self, collapsed):
        settings.user.ui.Set(self.collapsedSettingName, 1 if collapsed else 0)

    def AddEntry(self, entry):
        self._entries.add(entry)
        if self.collapsed:
            entry.GetAbsoluteSize()
            entry.display = False

    def Layout(self):
        panel = Container(parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, left=16, height=20, width=ENTRY_DEFAULT_WIDTH - 16)
        panel.DelegateEvents(self)
        FillThemeColored(bgParent=panel, colorType=uiconst.COLORTYPE_UIHEADER)
        self.arrow = Sprite(parent=panel, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Icons/38_16_229.png', left=2, width=16, height=16, rotation=math.pi / 2.0 if self.collapsed else 0)
        EveLabelSmall(parent=panel, align=uiconst.CENTERLEFT, text=self.text, left=18)
        self.hilite = FillThemeColored(bgParent=panel, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)

    def OnClick(self, *args):
        if self.disabled:
            return
        uthread.new(self.ToggleCollapse)

    def ToggleCollapse(self):
        self.disabled = True
        try:
            self.collapsed = not self.collapsed
            if self.collapsed:
                self.Collapse()
            else:
                self.Expand()
        finally:
            self.disabled = False

    def Collapse(self):
        animations.Tr2DRotateTo(self.arrow, endAngle=math.pi / 2.0, duration=0.15)
        reverseSortedEntries = reversed(sorted(self._entries, key=self._GetEntrySortKey))
        for i, entry in enumerate(reverseSortedEntries):
            entry.Disable()
            animations.FadeTo(entry, startVal=1.0, endVal=0.0, duration=0.2, timeOffset=i * 0.02)
            animations.MoveTo(entry, startPos=(0, 0), endPos=(0, -(entry.height + entry.padTop + entry.padBottom)), duration=0.2, timeOffset=i * 0.02 + 0.1)

        sleepDuration = len(self._entries) * 0.02 + 0.3
        blue.synchro.SleepWallclock(sleepDuration * 1000)

    def Expand(self):
        animations.Tr2DRotateTo(self.arrow, startAngle=math.pi / 2.0, endAngle=0.0, duration=0.15)
        sortedEntries = sorted(self._entries, key=self._GetEntrySortKey)
        for i, entry in enumerate(sortedEntries):
            entry.display = True
            animations.MoveTo(entry, startPos=(0, -(entry.height + entry.padTop + entry.padBottom)), endPos=(0, 0), duration=0.2, timeOffset=i * 0.02)
            animations.FadeTo(entry, startVal=0.0, endVal=1.0, duration=0.2, timeOffset=i * 0.02 + 0.1, callback=entry.Enable)

        sleepDuration = len(self._entries) * 0.02 + 0.3
        blue.synchro.SleepWallclock(sleepDuration * 1000)

    def _GetEntrySortKey(self, entry):
        return entry.parent.children.index(entry)


class SkinDurationLabel(LabelThemeColored):
    default_colorType = uiconst.COLORTYPE_UIHILIGHTGLOW

    def ApplyAttributes(self, attributes):
        super(SkinDurationLabel, self).ApplyAttributes(attributes)
        self.skin = attributes.skin
        self.text = self.skin.GetExpiresLabel()
        if not self.skin.permanent:
            uthread.new(self._UpdateLabelThread)

    def _UpdateLabelThread(self):
        while True:
            blue.synchro.SleepWallclock(1000)
            if self.destroyed:
                break
            self.text = self.skin.GetExpiresLabel()
