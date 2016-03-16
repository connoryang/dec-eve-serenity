#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\achievements\client\achievementTreeWindow.py
import weakref
from achievements.client.achievementGroupEntry import AchievementGroupEntry
from achievements.client.achievementSettings import OpportunitiesSettingsMenu
from achievements.common.achievementGroups import GetAchievementGroups, GetAchievementGroup
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.base import ReverseScaleDpi
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from carbonui.util.mouseTargetObject import MouseTargetObject
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge, EveLabelSmall
from eve.client.script.ui.control.eveWindow import Window
import carbonui.const as uiconst
import math
import sys
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import SpriteThemeColored, ColorThemeMixin, FrameThemeColored
from eve.client.script.ui.shared.infoPanels.infoPanelControls import InfoPanelLabel
from localization import GetByLabel
import trinity
import geo2
import eve.client.script.ui.eveFontConst as fontConst
import service
LINE_SOLID = 1
LINE_DASHED = 2
LINE_DASHED_ACTIVE = 3
LINE_HIDDEN = 4
STATE_INCOMPLETE = 1
STATE_INPROGRESS = 2
STATE_COMPLETED = 3
SLOT_SIZE = 80
BACKGROUND_SLOT_SIZE = 110
SLOT_SHOW_MOUSEOVER_INFO = False

def hex_slot_size(hexSize):
    width = hexSize * 2
    height = math.sqrt(3.0) / 2.0 * width
    return (width, height)


def hex_slot_center_position(column, row, hexSize):
    width, height = hex_slot_size(hexSize)
    centerX = 0.75 * width * column
    centerY = height * row + column % 2 * height * 0.5
    return (centerX, centerY)


def pixel_to_hex(x, y, hexSize):
    column = 2.0 / 3.0 * x / hexSize
    row = (-1.0 / 3.0 * x + 1.0 / 3.0 * math.sqrt(3.0) * y) / hexSize
    return (column, row)


def axial_to_cube_coordinate(column, row):
    x = column
    z = row
    y = -x - z
    return (x, y, z)


def hex_round(x, y, z):
    rx = round(x)
    ry = round(y)
    rz = round(z)
    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return (int(rx), int(ry), int(rz))


def cube_to_odd_q_axial_coordinate(x, y, z):
    column = x
    row = z + (x - (x & 1)) / 2
    return (column, row)


class ActiveAchievementInfo(Container):
    __notifyevents__ = ['OnAchievementTreeMouseOver']
    loadedAchievementGroupID = None
    resetToActiveTimer = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.content = Container(parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL)
        sm.RegisterNotify(self)
        if attributes.achievementGroupID:
            self.LoadAchievementGroup(attributes.achievementGroupID)
        self.mouseOverTimer = AutoTimer(10, self.MonitorMouseOver)

    def OnAchievementTreeMouseOver(self, groupID):
        if self.loadedAchievementGroupID != groupID:
            self.LoadAchievementGroup(groupID)
            uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.1)
            activeAchievementGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
            if groupID != activeAchievementGroupID:
                self.resetToActiveTimer = AutoTimer(3000, self.ResetToActive)

    def MonitorMouseOver(self):
        if self.destroyed:
            self.mouseOverTimer = None
            return
        if uicore.uilib.mouseOver.IsUnder(self):
            self.StopAnimations()
            self.opacity = 1.0
        elif not self.resetToActiveTimer:
            self.resetToActiveTimer = AutoTimer(3000, self.ResetToActive)

    def ResetToActive(self):
        resetTimer = False
        if uicore.uilib.mouseOver.IsUnderClass(AchievementTreeSlot):
            resetTimer = True
        elif isinstance(uicore.uilib.mouseOver, AchievementTreeSlot):
            resetTimer = True
        elif uicore.uilib.mouseOver.IsUnder(self):
            resetTimer = True
        if resetTimer:
            uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.1)
            self.resetToActiveTimer = AutoTimer(3000, self.ResetToActive)
            return
        activeAchievementGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        if activeAchievementGroupID and self.loadedAchievementGroupID != activeAchievementGroupID:
            uicore.animations.FadeTo(self, startVal=1.0, endVal=0.0, duration=1.0, callback=self.LoadActiveGroup)
        self.resetToActiveTimer = None

    def LoadActiveGroup(self):
        activeAchievementGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        if activeAchievementGroupID:
            uicore.animations.FadeTo(self, startVal=self.opacity, endVal=1.0, duration=0.1)
            self.LoadAchievementGroup(activeAchievementGroupID)

    def ReloadAchievementGroup(self):
        self.LoadAchievementGroup(self.loadedAchievementGroupID)

    def LoadAchievementGroup(self, groupID):
        self.loadedAchievementGroupID = groupID
        self.content.Flush()
        groupData = GetAchievementGroup(groupID)
        if groupData:
            AchievementGroupEntry(parent=self.content, groupInfo=groupData, align=uiconst.TOTOP, padding=(10, 4, 4, 0), markActive=True, animateIn=True, loadTaskBackgrounds=False)


class AchievementTreeLegend(LayoutGrid):
    default_columns = 2
    default_cellPadding = 3
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        LayoutGrid.ApplyAttributes(self, attributes)
        EveLabelSmall(text=GetByLabel('Achievements/UI/active'), parent=self, align=uiconst.CENTERRIGHT)
        activeEffectSprite = SpriteThemeColored(parent=self, state=uiconst.UI_DISABLED, blendMode=trinity.TR2_SBM_ADDX2, texturePath='res:/UI/Texture/classes/Achievements/iconActiveLegend.png', pos=(0, 0, 20, 20))
        iconMap = [(GetByLabel('Achievements/UI/incomplete'), 'res:/UI/Texture/classes/Achievements/iconIncomplete.png'), (GetByLabel('Achievements/UI/partial'), 'res:/UI/Texture/classes/Achievements/iconPartial.png'), (GetByLabel('Achievements/UI/complete'), 'res:/UI/Texture/classes/Achievements/iconComplete.png')]
        for label, texturePath in iconMap:
            EveLabelSmall(text=label, parent=self, align=uiconst.CENTERRIGHT)
            GlowSprite(texturePath=texturePath, parent=self, pos=(0, 0, 20, 20))


class AchievementTreeConnection(VectorLineTrace, ColorThemeMixin):
    default_lineWidth = 1.0
    default_colorType = uiconst.COLORTYPE_UIHILIGHTGLOW
    default_opacity = 1.0
    glowLine = None
    glowLineColor = (1, 1, 1, 0.5)
    localScale = 1.0
    __notifyevents__ = ['OnUIScalingChange']

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)
        self.lineType = LINE_SOLID
        self.fromID = attributes.fromID
        self.toID = attributes.toID
        self.glowLine = VectorLineTrace(parent=self.parent, lineWidth=20, spriteEffect=trinity.TR2_SFX_COPY, texturePath='res:/UI/Texture/classes/Achievements/lineGlow.png', name='glowLine', blendMode=trinity.TR2_SBM_ADDX2, opacity=0.3)
        sm.RegisterNotify(self)

    def Close(self, *args):
        if self.glowLine and not self.glowLine.destroyed:
            self.glowLine.Close()
        VectorLineTrace.Close(self, *args)

    def OnUIScalingChange(self, *args):
        self.PlotLineTrace()

    def UpdateFromToPosition(self, fromObject, toObject, localScale):
        self.localScale = localScale
        self.fromPosition = (fromObject.left + fromObject.width / 2, fromObject.top + fromObject.height / 2)
        self.toPosition = (toObject.left + toObject.width / 2, toObject.top + toObject.height / 2)
        self.PlotLineTrace()

    def SetLineType(self, lineType):
        self.lineType = lineType
        self.PlotLineTrace()

    def PlotLineTrace(self):
        self.Flush()
        if self.glowLine:
            self.glowLine.Flush()
        if self.lineType in (LINE_DASHED, LINE_DASHED_ACTIVE):
            self.PlotDashLine()
        elif self.lineType == LINE_SOLID:
            self.PlotSolidLine()
        else:
            return
        if self.lineType == LINE_DASHED_ACTIVE:
            vecDir = geo2.Vec2Subtract(self.toPosition, self.fromPosition)
            vecLength = geo2.Vec2Length(vecDir)
            vecDirNorm = geo2.Vec2Normalize(vecDir)
            r, g, b = self.GetRGB()
            GLOWCOLOR = (r,
             g,
             b,
             1.0)
            GAPCOLOR = (r,
             g,
             b,
             0.0)
            self.glowLine.AddPoint(self.fromPosition, GAPCOLOR)
            point = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, vecLength * 0.5))
            self.glowLine.AddPoint(point, GLOWCOLOR)
            self.glowLine.AddPoint(self.toPosition, GAPCOLOR)
            self.glowLine.textureWidth = vecLength
            uicore.animations.MorphScalar(self.glowLine, 'textureOffset', startVal=0.0, endVal=1.0, curveType=uiconst.ANIM_LINEAR, duration=2.0, loops=uiconst.ANIM_REPEAT)

    def PlotSolidLine(self):
        r, g, b = self.GetRGB()
        DASHCOLOR = (r,
         g,
         b,
         1.0)
        GAPCOLOR = (r,
         g,
         b,
         0.0)
        MARGIN = 16.0 * self.localScale
        vecDir = geo2.Vec2Subtract(self.toPosition, self.fromPosition)
        vecLength = geo2.Vec2Length(vecDir)
        vecDirNorm = geo2.Vec2Normalize(vecDir)
        startPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, MARGIN))
        self.AddPoint(startPoint, GAPCOLOR)
        startPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, MARGIN + 8))
        self.AddPoint(startPoint, DASHCOLOR)
        startPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, vecLength - MARGIN - 8))
        self.AddPoint(startPoint, DASHCOLOR)
        startPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, vecLength - MARGIN))
        self.AddPoint(startPoint, GAPCOLOR)

    def PlotDashLine(self):
        dashSize = 2.0
        gapSize = 7.0
        r, g, b = self.GetRGB()
        DASHCOLOR = (r,
         g,
         b,
         1.0)
        GAPCOLOR = (r,
         g,
         b,
         0.0)
        MARGIN = 16.0 * self.localScale
        vecDir = geo2.Vec2Subtract(self.toPosition, self.fromPosition)
        vecLength = geo2.Vec2Length(vecDir)
        vecDirNorm = geo2.Vec2Normalize(vecDir)
        p = MARGIN
        while p < vecLength - MARGIN:
            startPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, p - 0.5))
            self.AddPoint(startPoint, GAPCOLOR)
            fromPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, p))
            self.AddPoint(fromPoint, DASHCOLOR)
            p = min(vecLength - MARGIN, dashSize + p)
            toPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, p))
            self.AddPoint(toPoint, DASHCOLOR)
            endPoint = geo2.Vec2Add(self.fromPosition, geo2.Vec2Scale(vecDirNorm, p + 0.5))
            self.AddPoint(endPoint, GAPCOLOR)
            p += gapSize


class AchievementTreeSlot(Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = -1
    nameLabel = None
    tooltipPanel = None
    localScale = 1.0
    moveEnabled = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.achievementGroupID = attributes.achievementGroupID
        self.hexGridPosition = attributes.hexGridPosition
        self.nameLabel = InfoPanelLabel(parent=self.parent, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, idx=0)
        self.stateSprite = GlowSprite(parent=self, pos=(0, 0, 20, 20), align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        self.activeEffectSprite = SpriteThemeColored(parent=self, state=uiconst.UI_DISABLED, spriteEffect=trinity.TR2_SFX_MODULATE, blendMode=trinity.TR2_SBM_ADDX2, texturePath='res:/UI/Texture/classes/Achievements/hexPingGlow.png', textureSecondaryPath='res:/UI/Texture/classes/Achievements/hexPingMask.png', pos=(0, 0, 300, 300), align=uiconst.CENTER, opacity=0.0)
        self.activeStateSprite = SpriteThemeColored(parent=self, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Achievements/hexActive.png', pos=(0, 0, 200, 200), align=uiconst.CENTER, opacity=0.0, blendMode=trinity.TR2_SBM_ADDX2, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        self.backgroundSprite = SpriteThemeColored(bgParent=self, texturePath='res:/UI/Texture/classes/Achievements/hexBackIncomplete.png', colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.5)
        self.UpdateGroupState()

    def Close(self, *args, **kwds):
        if self.nameLabel and not self.nameLabel.destroyed:
            self.nameLabel.LoadTooltipPanel = None
            self.nameLabel.GetTooltipPosition = None
        return Container.Close(self, *args, **kwds)

    def GetTooltipPosition(self, *args, **kwds):
        return self.GetAbsolute()

    def UpdateGroupState(self):
        activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        groupData = GetAchievementGroup(self.achievementGroupID)
        totalNum = groupData.GetNumberOfTasks()
        completed = groupData.GetNumberOfCompleted()
        if totalNum == completed:
            self.stateSprite.SetTexturePath('res:/UI/Texture/classes/Achievements/iconComplete.png')
            self.progressState = STATE_COMPLETED
            self.backgroundSprite.texturePath = 'res:/UI/Texture/classes/Achievements/hexBackComplete.png'
        elif completed:
            if activeGroupID == self.achievementGroupID:
                self.stateSprite.SetTexturePath('res:/UI/Texture/classes/Achievements/iconPartialActive.png')
            else:
                self.stateSprite.SetTexturePath('res:/UI/Texture/classes/Achievements/iconPartial.png')
            self.progressState = STATE_INPROGRESS
            self.backgroundSprite.texturePath = 'res:/UI/Texture/classes/Achievements/hexBackIncomplete.png'
        else:
            if activeGroupID == self.achievementGroupID:
                self.stateSprite.SetTexturePath('res:/UI/Texture/classes/Achievements/iconIncompleteActive.png')
            else:
                self.stateSprite.SetTexturePath('res:/UI/Texture/classes/Achievements/iconIncomplete.png')
            self.progressState = STATE_INCOMPLETE
            self.backgroundSprite.texturePath = 'res:/UI/Texture/classes/Achievements/hexBackIncomplete.png'
        self.nameLabel.text = GetByLabel(groupData.groupName)
        if activeGroupID == self.achievementGroupID:
            self.activeEffectSprite.display = True
            self.activeStateSprite.display = True
            uicore.animations.FadeTo(self.activeEffectSprite, startVal=0.7, endVal=0.2, duration=0.5)
            r, g, b, a = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
            uicore.animations.MorphVector2(self.activeEffectSprite, 'scale', startVal=(2.5, 2.5), endVal=(0.0, 0.0), duration=0.7)
            uicore.animations.SpColorMorphTo(self.activeStateSprite, startColor=(0, 0, 0, 0), endColor=(r,
             g,
             b,
             1.0), duration=0.5, curveType=uiconst.ANIM_OVERSHOT, callback=self.PulseActive)
            uicore.animations.SpColorMorphTo(self.backgroundSprite, startColor=(r,
             g,
             b,
             0.5), endColor=(r,
             g,
             b,
             1.5), duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        else:
            uicore.animations.FadeOut(self.activeStateSprite, duration=0.125)
            uicore.animations.FadeOut(self.activeEffectSprite, duration=0.125)
            r, g, b, a = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHTGLOW)
            uicore.animations.SpColorMorphTo(self.backgroundSprite, startColor=(r,
             g,
             b,
             0.5), endColor=(r,
             g,
             b,
             0.5), duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        if self.tooltipPanel:
            tooltipPanel = self.tooltipPanel()
            if tooltipPanel and not tooltipPanel.destroyed:
                tooltipPanel.Flush()
                self.LoadTooltipPanel(tooltipPanel)

    def PulseActive(self):
        r, g, b, a = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
        uicore.animations.SpColorMorphTo(self.activeStateSprite, startColor=(r,
         g,
         b,
         1.0), endColor=(r * 0.8,
         g * 0.8,
         b * 0.8,
         1.0), duration=1.5, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def UpdateLabelPosition(self):
        if not self.nameLabel:
            return
        if self.localScale < 1.0:
            self.nameLabel.fontsize = fontConst.EVE_MEDIUM_FONTSIZE
        else:
            self.nameLabel.fontsize = fontConst.EVE_LARGE_FONTSIZE
        self.nameLabel.left = self.left + self.width / 2 + 14
        self.nameLabel.top = self.top + (self.height - self.nameLabel.textheight) / 2

    def SetLocalScale(self, localScale):
        self.localScale = localScale
        self.activeEffectSprite.width = self.activeEffectSprite.height = SLOT_SIZE * localScale * 3.0
        self.activeStateSprite.width = self.activeStateSprite.height = SLOT_SIZE * localScale * 2.0

    def OnClick(self, *args):
        from achievements.client.auraAchievementWindow import AchievementAuraWindow
        auraWindow = AchievementAuraWindow.GetIfOpen()
        if auraWindow:
            auraWindow.FadeOutTransitionAndClose()
        sm.GetService('achievementSvc').SetActiveAchievementGroupID(self.achievementGroupID)
        sm.GetService('experimentClientSvc').LogWindowOpenedActions('opportunitySelect')

    def OnMouseDown(self, *args):
        if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            self.moveEnabled = True

    def OnMouseUp(self, *args):
        if session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            self.moveEnabled = False
            self._PrintPositions()

    def OnMouseMove(self, *args):
        if getattr(self, 'moveEnabled', False):
            pl, pt, pw, ph = self.parent.GetAbsolute()
            px_hx = pixel_to_hex(uicore.uilib.x - pl, uicore.uilib.y - pt, self.parent.hexGridSize * self.parent.localScale)
            ax_cu = axial_to_cube_coordinate(*px_hx)
            ax_cu_rounded = hex_round(*ax_cu)
            cu_ax = cube_to_odd_q_axial_coordinate(*ax_cu_rounded)
            self.SetHexGridPosition(*cu_ax)

    def SetHexGridPosition(self, hexColumn, hexRow):
        centerX, centerY = hex_slot_center_position(hexColumn, hexRow, self.parent.hexGridSize * self.parent.localScale)
        self.left = centerX - self.width / 2
        self.top = centerY - self.height / 2

    def _PrintPositions(self):
        print '# -----------------------------------'
        for each in self.parent.children:
            if not isinstance(each, AchievementTreeSlot):
                continue
            centerX = each.left + each.width / 2
            centerY = each.top + each.height / 2
            px_hx = pixel_to_hex(centerX, centerY, self.parent.hexGridSize * self.parent.localScale)
            ax_cu = axial_to_cube_coordinate(*px_hx)
            ax_cu_rounded = hex_round(*ax_cu)
            cu_ax = cube_to_odd_q_axial_coordinate(*ax_cu_rounded)
            groupData = GetAchievementGroup(each.achievementGroupID)
            print 'group%s.SetTreePosition(%s) # %s' % (each.achievementGroupID, cu_ax, GetByLabel(groupData.groupName))

    def OnMouseEnter(self, *args):
        activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        if activeGroupID == self.achievementGroupID:
            r, g, b, a = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
            uicore.animations.SpColorMorphTo(self.backgroundSprite, startColor=(r,
             g,
             b,
             1.5), endColor=(r,
             g,
             b,
             3.0), duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        else:
            uicore.animations.FadeTo(self.backgroundSprite, startVal=self.backgroundSprite.opacity, endVal=1.0, duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        self.moTimer = AutoTimer(10, self.CheckMouseOver)
        if not SLOT_SHOW_MOUSEOVER_INFO:
            self.mouseEnterDelay = AutoTimer(300, self.CheckMouseEnter)

    def CheckMouseEnter(self, *args):
        self.mouseEnterDelay = None
        if uicore.uilib.mouseOver is self:
            sm.ScatterEvent('OnAchievementTreeMouseOver', self.achievementGroupID)

    def CheckMouseOver(self):
        if uicore.uilib.mouseOver is self:
            return
        if uicore.uilib.mouseOver.IsUnder(self):
            return
        if self.nameLabel and uicore.uilib.mouseOver is self.nameLabel:
            return
        self.moTimer = None
        activeGroupID = sm.GetService('achievementSvc').GetActiveAchievementGroupID()
        if activeGroupID == self.achievementGroupID:
            r, g, b, a = sm.GetService('uiColor').GetUIColor(uiconst.COLORTYPE_UIHILIGHT)
            uicore.animations.SpColorMorphTo(self.backgroundSprite, startColor=(r,
             g,
             b,
             1.5), endColor=(r,
             g,
             b,
             1.5), duration=0.1, curveType=uiconst.ANIM_OVERSHOT)
        else:
            uicore.animations.FadeTo(self.backgroundSprite, startVal=self.backgroundSprite.opacity, endVal=0.5, duration=0.1)

    def GetBounds(self):
        return (self.left,
         self.top,
         self.left + self.width,
         self.top + self.height)

    def LoadTooltipPanel(self, tooltipPanel, *args, **kwds):
        if not SLOT_SHOW_MOUSEOVER_INFO:
            return
        tooltipPanel.columns = 1
        tooltipPanel.margin = (10, 5, 10, 3)
        tooltipPanel.state = uiconst.UI_NORMAL
        groupData = GetAchievementGroup(self.achievementGroupID)
        if groupData:
            AchievementGroupEntry(parent=tooltipPanel, groupInfo=groupData, align=uiconst.TOPLEFT, width=240)

    def GetTooltipPosition(self, *args):
        return self.GetAbsolute()

    def GetTooltipPositionFallbacks(self, *args):
        return []

    def GetTooltipPointer(self, *args):
        return uiconst.POINT_TOP_2

    @apply
    def pos():
        fget = Container.pos.fget

        def fset(self, value):
            Container.pos.fset(self, value)
            self.UpdateLabelPosition()

        return property(**locals())

    @apply
    def left():
        fget = Container.left.fget

        def fset(self, value):
            Container.left.fset(self, value)
            self.UpdateLabelPosition()

        return property(**locals())

    @apply
    def top():
        fget = Container.top.fget

        def fset(self, value):
            Container.top.fset(self, value)
            self.UpdateLabelPosition()

        return property(**locals())


class AchievementTree(Container):
    hexGridSize = float(BACKGROUND_SLOT_SIZE / 2)
    localScale = 0.75
    gridBackground = None
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_clipChildren = True
    dragThread = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.connections = {}
        self.slotsByID = {}
        self.gridBackground = Container(parent=self)
        self.treeMargin = attributes.treeMargin
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        FrameThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1, padding=3)

    def Close(self, *args):
        Container.Close(self, *args)
        self.connections = None
        self.slotsByID = None

    def OnMouseWheel(self, dz):
        return
        if self.dragThread:
            return
        if dz < 0:
            newScale = self.localScale * 1.5
        else:
            newScale = self.localScale / 1.5
        newScale = max(0.5, min(1.0, newScale))
        if newScale != self.localScale:
            uicore.animations.MorphScalar(self, 'mousewheelscale', self.localScale, newScale, duration=0.2)

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.StopAnimations()
            self.dragData = (self.left,
             self.top,
             uicore.uilib.x,
             uicore.uilib.y)
            self.dragThread = AutoTimer(1, self.PanUpdate)

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self.dragThread = None
            self.ClampPosition()

    def PanUpdate(self):
        if uicore.uilib.GetMouseCapture() is not self:
            self.dragThread = None
            self.ClampPosition()
            return
        startLeft, startTop, startX, startY = self.dragData
        dX = uicore.uilib.x - startX
        dY = uicore.uilib.y - startY
        self.left = startLeft + dX
        self.top = startTop + dY
        self.ClampPosition(smooth=False)

    def ClampPosition(self, smooth = True):
        mL, mT, mR, mB = self.treeMargin
        pW = ReverseScaleDpi(self.parent.displayWidth)
        pH = ReverseScaleDpi(self.parent.displayHeight)
        if self.width < pW:
            left = (pW - self.width) / 2
        else:
            left = max(pW - self.width, mL + -self.width / 2, self.left)
            left = min(0, -mR + pW - self.width / 2, left)
        if self.height < pH:
            top = (pH - self.height) / 2
        else:
            top = max(pH - self.height, mT + -self.height / 2, self.top)
            top = min(0, -mB + pH - self.height / 2, top)
        if smooth:
            if self.left != left:
                uicore.animations.MorphScalar(self, 'left', startVal=self.left, endVal=left, duration=0.3)
            if self.top != top:
                uicore.animations.MorphScalar(self, 'top', startVal=self.top, endVal=top, duration=0.3)
        else:
            self.left = left
            self.top = top
        self.RegisterPosition(position=(left, top))

    def RegisterPosition(self, position = None):
        pW = ReverseScaleDpi(self.parent.displayWidth)
        pH = ReverseScaleDpi(self.parent.displayHeight)
        if position:
            left, top = position
        else:
            left = self.left
            top = self.top
        cX = left + self.width / 2
        cY = top + self.height / 2
        proportionX = cX / float(pW)
        proportionY = cY / float(pH)
        settings.char.ui.Set('opportunities_tree_position8', (proportionX, proportionY))

    def LoadRegisteredPosition(self):
        proportionX, proportionY = settings.char.ui.Get('opportunities_tree_position8', (0.5, 0.5))
        pW, pH = self.parent.GetAbsoluteSize()
        self.left = pW * proportionX - self.width / 2
        self.top = pH * proportionY - self.height / 2
        self.ClampPosition(smooth=False)

    @apply
    def mousewheelscale():

        def fget(self):
            pass

        def fset(self, value):
            self.localScale = value
            self.UpdateTreePositions()

        return property(**locals())

    def ShowBackgroundGrid(self):
        if not self.width or not self.height:
            return
        self.gridBackground.Flush()
        hexRow = 0
        i = 0
        while True:
            hexColumn = 0
            while True:
                centerX, centerY = hex_slot_center_position(hexColumn, hexRow, BACKGROUND_SLOT_SIZE * self.localScale * 0.5)
                slotSize = BACKGROUND_SLOT_SIZE * self.localScale
                left = centerX - slotSize / 2
                top = centerY - slotSize / 2
                if left > self.width:
                    break
                hexSlot = Sprite(parent=self.gridBackground, left=left, top=top, width=slotSize, height=slotSize, texturePath='res:/UI/Texture/classes/Achievements/hexBack.png', opacity=0.04, state=uiconst.UI_DISABLED)
                hexSlot.hexGridPosition = (hexColumn, hexRow)
                hexColumn += 1

            hexRow += 1
            if top > self.height:
                break

    def AddSlot(self, hexColumn, hexRow, achievementGroupID):
        centerX, centerY = hex_slot_center_position(hexColumn, hexRow, self.hexGridSize * self.localScale)
        slotSize = SLOT_SIZE * self.localScale
        hexSlot = AchievementTreeSlot(parent=self, left=centerX - slotSize / 2, top=centerY - slotSize / 2, width=slotSize, height=slotSize, achievementGroupID=achievementGroupID, hexGridPosition=(hexColumn, hexRow), idx=0)
        self.slotsByID[achievementGroupID] = hexSlot

    def AddConnection(self, fromAchievementGroupID, toAchievementGroupID):
        fromSlot = self.GetSlotByAchievementGroupID(fromAchievementGroupID)
        toSlot = self.GetSlotByAchievementGroupID(toAchievementGroupID)
        if not fromSlot or not toSlot:
            return
        connection = AchievementTreeConnection(parent=self, fromID=fromAchievementGroupID, toID=toAchievementGroupID)
        self.connections[fromAchievementGroupID, toAchievementGroupID] = connection

    def GetConnectionByIDs(self, fromOrToID1, fromOrToID2):
        if (fromOrToID1, fromOrToID2) in self.connections:
            return self.connections[fromOrToID1, fromOrToID2]
        if (fromOrToID2, fromOrToID1) in self.connections:
            return self.connections[fromOrToID2, fromOrToID1]

    def GetSlotByAchievementGroupID(self, achievementGroupID):
        return self.slotsByID.get(achievementGroupID, None)

    def GetSlots(self):
        return self.slotsByID.values()

    def UpdateTreeState(self):
        for each in self.GetSlots():
            each.UpdateGroupState()

        for connectionID, connection in self.connections.iteritems():
            fromID, toID = connectionID
            fromSlot = self.GetSlotByAchievementGroupID(fromID)
            toSlot = self.GetSlotByAchievementGroupID(toID)
            if not fromSlot or not toSlot:
                continue
            connection.SetLineType(LINE_DASHED)

    def UpdateTreePositions(self):
        minColumn = sys.maxint
        maxColumn = -sys.maxint
        minRow = sys.maxint
        maxRow = -sys.maxint
        slots = self.GetSlots()
        for each in slots:
            hexColumn, hexRow = each.hexGridPosition
            centerX, centerY = hex_slot_center_position(hexColumn, hexRow, self.hexGridSize * self.localScale)
            slotSize = SLOT_SIZE * self.localScale
            each.pos = (centerX - slotSize / 2,
             centerY - slotSize / 2,
             slotSize,
             slotSize)
            minColumn = min(hexColumn, minColumn)
            maxColumn = max(hexColumn, maxColumn)
            minRow = min(hexRow, minRow)
            maxRow = max(hexRow, maxRow)
            each.SetLocalScale(self.localScale)

        xmargin = 6
        ymargin = 4
        leftMargin, topMargin = hex_slot_center_position(minColumn - xmargin, minRow - ymargin, self.hexGridSize * self.localScale)
        rightMargin, bottomMargin = hex_slot_center_position(maxColumn + xmargin, maxRow + ymargin, self.hexGridSize * self.localScale)
        for each in slots:
            each.left -= leftMargin
            each.top -= topMargin

        self.width = -leftMargin + rightMargin
        self.height = -topMargin + bottomMargin
        for connectionID, connection in self.connections.iteritems():
            fromID, toID = connectionID
            fromSlot = self.GetSlotByAchievementGroupID(fromID)
            toSlot = self.GetSlotByAchievementGroupID(toID)
            if not fromSlot or not toSlot:
                continue
            connection.UpdateFromToPosition(fromSlot, toSlot, self.localScale)

        if self.gridBackground:
            for each in self.gridBackground.children:
                hexColumn, hexRow = each.hexGridPosition
                centerX, centerY = hex_slot_center_position(hexColumn, hexRow, BACKGROUND_SLOT_SIZE * self.localScale * 0.5)
                slotSize = BACKGROUND_SLOT_SIZE * self.localScale
                each.pos = (centerX - slotSize / 2,
                 centerY - slotSize / 2,
                 slotSize,
                 slotSize)

    def SetLocalScale(self, localScale):
        if localScale != self.localScale:
            self.localScale = localScale
            self.UpdateTreePositions()


class AchievementTreeWindowHeader(Container):
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        grid = LayoutGrid(parent=self, columns=2)
        self.auraSprite = Sprite(pos=(14, 0, 80, 80), texturePath='res:/UI/Texture/classes/achievements/auraAlpha.png')
        grid.AddCell(self.auraSprite, rowSpan=2)
        header = EveLabelLarge(parent=grid, text='Welcome!', top=16)
        message = EveLabelMedium(parent=grid, text='Welcome blurb', width=300)


class AchievementTreeWindow(Window):
    __guid__ = 'form.AchievementTreeWindow'
    default_captionLabelPath = 'Achievements/UI/OpportunitiesTreeHeader'
    default_windowID = 'AchievementTreeWindow'
    default_width = 900
    default_height = 600
    default_minSize = (default_width, default_height)
    default_maxSize = (1200, 800)
    default_iconNum = 'res:/ui/Texture/WindowIcons/opportunitiesTree.png'
    default_topParentHeight = 0
    achievementTree = None
    activeInfo = None
    __notifyevents__ = ['OnAchievementChanged',
     'OnAchievementActiveGroupChanged',
     'OnUIColorsChanged',
     'OnAchievementsDataInitialized']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnstackable()
        mainArea = self.GetMainArea()
        mainArea.clipChildren = True
        infoContainer = Container(parent=mainArea, align=uiconst.TOLEFT_NOPUSH, width=260, padding=6)
        if not SLOT_SHOW_MOUSEOVER_INFO:
            self.activeInfo = ActiveAchievementInfo(parent=infoContainer, achievementGroupID=sm.GetService('achievementSvc').GetActiveAchievementGroupID())
            MouseTargetObject(self.activeInfo)
        self.legendInfo = AchievementTreeLegend(parent=mainArea, align=uiconst.BOTTOMRIGHT, left=10, top=26)
        settingControl = OpportunitiesSettingsMenu(parent=mainArea, align=uiconst.TOPRIGHT, left=6, top=6)
        treeClipper = Container(parent=mainArea, padding=4, clipChildren=True)
        treeClipper._OnSizeChange_NoBlock = self.OnTreeClipperSizeChanged
        self.achievementTree = AchievementTree(parent=treeClipper, treeMargin=(infoContainer.width,
         0,
         0,
         0))
        connections = set()
        for i, achievementGroup in enumerate(GetAchievementGroups()):
            column, row = achievementGroup.treePosition
            self.achievementTree.AddSlot(column, row, achievementGroup.groupID)

        for groupID1, groupID2 in connections:
            self.achievementTree.AddConnection(groupID1, groupID2)

        self.achievementTree.UpdateTreePositions()
        self.achievementTree.UpdateTreeState()
        self.achievementTree.ShowBackgroundGrid()
        self.achievementTree.LoadRegisteredPosition()
        sm.RegisterNotify(self)

    def OnTreeClipperSizeChanged(self, *args, **kwds):
        self.achievementTree.LoadRegisteredPosition()

    def OnAchievementsDataInitialized(self, *args, **kwds):
        self.achievementTree.UpdateTreeState()
        if self.activeInfo:
            self.activeInfo.ReloadAchievementGroup()

    def OnAchievementActiveGroupChanged(self, *args, **kwds):
        self.achievementTree.UpdateTreeState()

    def OnAchievementChanged(self, *args, **kwds):
        self.achievementTree.UpdateTreeState()
        if self.activeInfo:
            self.activeInfo.ReloadAchievementGroup()

    def OnUIColorsChanged(self, *args, **kwds):
        self.achievementTree.UpdateTreeState()

    def OnResize_(self, *args, **kwds):
        pass
