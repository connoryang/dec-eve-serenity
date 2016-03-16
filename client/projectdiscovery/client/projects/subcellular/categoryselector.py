#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\categoryselector.py
__author__ = 'ru.Hjalti'
import blue
import uiprimitives
import uicontrols
import trinity
import carbonui.const as uiconst
from projectdiscovery.client import const
from carbonui.uianimations import animations
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.tooltips.tooltipUtil import SetTooltipHeaderAndDescription
from eve.client.script.ui.control.themeColored import FrameThemeColored
from carbonui.primitives.flowcontainer import FlowContainer
from projectdiscovery.client.util.eventlistener import eventlistener, on_event

class CategorySelector(FlowContainer):
    default_name = 'CategorySelector'

    def ApplyAttributes(self, attributes):
        super(CategorySelector, self).ApplyAttributes(attributes)
        self.categories = attributes.get('categories')
        self.super_categories = []
        for n, (key, supercategory) in enumerate(self.categories.iteritems()):
            self.super_categories.append(CategoryGroup(category=supercategory, parent=self, align=uiconst.NOALIGN, number=n))

    def cascade_categories_in(self):
        for super_cat in self.super_categories:
            animations.FadeIn(super_cat.category_group_hex, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeIn(super_cat.label, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            for sub_cat in super_cat.sub_categories:
                animations.SpGlowFadeIn(sub_cat.hexagon_outline, glowExpand=2)
                animations.SpGlowFadeOut(sub_cat.hexagon_outline, glowExpand=2)
                if sub_cat.unavailable:
                    animations.FadeIn(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2, endVal=0.5)
                else:
                    animations.FadeIn(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
                blue.synchro.Sleep(15)

    def cascade_categories_out(self):
        for super_cat in self.super_categories:
            animations.FadeOut(super_cat.category_group_hex, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            animations.FadeOut(super_cat.label, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
            for sub_cat in super_cat.sub_categories:
                animations.FadeOut(sub_cat, duration=0.5, curveType=uiconst.ANIM_OVERSHOT2)
                blue.synchro.Sleep(15)


class CategoryGroup(uiprimitives.Container):
    default_state = uiconst.UI_NORMAL
    default_height = 135
    MIN_WIDTH = 156
    HEX_WIDTH = 52
    HEX_HEIGHT = 46
    HEX_SPACING = 39.2
    CHAIN_TOP_OFFSET = 22
    TOP_OFFSET = {1: HEX_HEIGHT / 2,
     2: 0,
     0: HEX_HEIGHT}

    def ApplyAttributes(self, attributes):
        super(CategoryGroup, self).ApplyAttributes(attributes)
        category = attributes.get('category')
        number = attributes.get('number')
        self.sub_categories = []
        self.label = uicontrols.Label(text=category['name'].upper(), parent=self, color=(1, 1, 1, 0.5), top=4, left=self.HEX_WIDTH, opacity=0)
        SetTooltipHeaderAndDescription(targetObject=self, headerText=category['name'], descriptionText=category['description'])
        self.category_group_hex = CategoryGroupHexagon(parent=self, category=category, number=number, top=0, left=0, width=self.HEX_WIDTH, height=self.HEX_HEIGHT, opacity=0)
        count = 1
        left = -self.HEX_SPACING
        self.width = self.HEX_WIDTH - self.HEX_SPACING
        for subcat in category['children']:
            for cat in subcat['children']:
                pos = count % 3
                count += 1
                if pos is not 0:
                    left += self.HEX_SPACING
                    self.width += self.HEX_SPACING
                self.sub_categories.append(CategoryHexagon(parent=self, category=cat, top=self.TOP_OFFSET[pos] + self.CHAIN_TOP_OFFSET, left=left, width=self.HEX_WIDTH, height=self.HEX_HEIGHT, opacity=0))

        self.width = self.width if self.width >= self.MIN_WIDTH else self.MIN_WIDTH


class Hexagon(uiprimitives.Container):
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_pickRadius = -1
    default_width = 52
    default_height = 46

    def ApplyAttributes(self, attributes):
        super(Hexagon, self).ApplyAttributes(attributes)
        self.hexagon_outline = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', width=self.width, height=self.height, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))


class CategoryGroupHexagon(Hexagon):
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        super(CategoryGroupHexagon, self).ApplyAttributes(attributes)
        uicontrols.Label(text=str(attributes.get('number') + 1), parent=self, fontsize=20, align=uiconst.CENTER, color=(1, 1, 1, 0.25))
        uiprimitives.Sprite(parent=self, width=self.width, height=self.height, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', state=uiconst.UI_DISABLED, color=(0.2, 0.2, 0.2, 1))


@eventlistener()

class CategoryHexagon(Hexagon):
    GLOW_ANIMATION = {'duration': 0.3,
     'curveType': uiconst.ANIM_OVERSHOT2}
    MIN_COLOR_VALUE = (0.5, 0.22, 0.17)
    MAX_COLOR_VALUE = (0.33, 0.49, 0.26)

    def ApplyAttributes(self, attributes):
        self.category = attributes.get('category')
        self.attributes = attributes
        self.id = self.category['id']
        self.excludes = self.category['excludes']
        self.reselect = False
        self.unavailable = False
        self.unclickable = False
        attributes['tooltipHeader'] = self.category['name']
        attributes['tooltipText'] = self.category.get('descriptionIdentification', self.category['description'])
        super(CategoryHexagon, self).ApplyAttributes(attributes)
        self.consensus_percentage = uicontrols.Label(parent=self, align=uiconst.CENTER, text='0', fontsize=16, state=uiconst.UI_HIDDEN)
        self.exclude_texture = uiprimitives.Sprite(parent=self, width=self.width, height=self.height, left=-1, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryUnavailable.png', state=uiconst.UI_HIDDEN)
        self.selected_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categorySelected.png', width=68, height=62, top=-8, left=-8, opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.correct_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMatch.png', width=68, height=62, top=-8, left=-8, opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.unmatched_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryWrong.png', width=68, height=62, top=-8, left=-8, opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.missed_texture = uiprimitives.Sprite(parent=self, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMissed.png', width=68, height=62, top=-8, left=-8, opacity=0, idx=0, state=uiconst.UI_DISABLED)
        self.color_overlay = uiprimitives.Sprite(parent=self, width=self.width / 1.25, height=self.height / 1.25, align=uiconst.CENTER, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED, opacity=0)
        self.image = uiprimitives.Sprite(parent=self, width=self.width, height=self.height, texturePath='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'], textureSecondaryPath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png', spriteEffect=trinity.TR2_SFX_MASK, state=uiconst.UI_DISABLED)
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=attributes['tooltipHeader'], description=attributes['tooltipText'], image='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'])

    def OnMouseEnter(self, *args):
        if not self.unavailable:
            animations.SpGlowFadeIn(self.hexagon_outline, glowExpand=2, duration=0.3)

    def OnMouseExit(self, *args):
        if not self.unavailable:
            animations.SpGlowFadeOut(self.hexagon_outline, glowExpand=2, duration=0.3)

    def set_percentage(self, percentage):
        self.consensus_percentage.state = uiconst.UI_DISABLED
        self.consensus_percentage.SetText(percentage + '%')

    def hide_percentage(self):
        self.consensus_percentage.state = uiconst.UI_HIDDEN

    def show_percentage(self):
        self.consensus_percentage.state = uiconst.UI_NORMAL
        self.consensus_percentage.state = uiconst.UI_DISABLED

    def set_unavailable(self):
        self.unavailable = True
        self.image.texturePath = 'res:/UI/Texture/classes/ProjectDiscovery/subcellular/gray_' + self.category['url']
        self.tooltipPanelClassInfo = None

    def set_available(self):
        self.unavailable = False
        self.image.texturePath = 'res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url']
        self.tooltipPanelClassInfo = CategoryTooltipWrapper(header=self.attributes['tooltipHeader'], description=self.attributes['tooltipText'], image='res:/UI/Texture/classes/ProjectDiscovery/subcellular/' + self.category['url'])

    def set_selected(self):
        self.category['selected'] = True
        uicore.animations.FadeIn(self.selected_texture, **self.GLOW_ANIMATION)

    def set_unselected(self):
        self.category['selected'] = False
        uicore.animations.FadeOut(self.selected_texture, **self.GLOW_ANIMATION)

    def set_unclickable(self):
        self.unclickable = True

    def set_clickable(self):
        self.unclickable = False

    def lerp(self, value, maximum, start_point, end_point):
        return start_point + (end_point - start_point) * value / maximum

    def lerp_color(self, value, maximum, start_point = MIN_COLOR_VALUE, end_point = MAX_COLOR_VALUE):
        r = self.lerp(value, maximum, start_point[0], end_point[0])
        g = self.lerp(value, maximum, start_point[1], end_point[1])
        b = self.lerp(value, maximum, start_point[2], end_point[2])
        return (r,
         g,
         b,
         1)

    def OnClick(self, *args):
        if self.exclude_texture.state is not uiconst.UI_HIDDEN or self.unclickable is True:
            return
        self.category['selected'] = not self.category['selected']
        if self.category['selected']:
            uicore.animations.FadeIn(self.selected_texture, **self.GLOW_ANIMATION)
        else:
            uicore.animations.FadeOut(self.selected_texture, **self.GLOW_ANIMATION)
        sm.ScatterEvent(const.Events.CategoryChanged, self)

    def GetTooltipPosition(self, *args):
        return self.GetAbsolute()

    @on_event(const.Events.ExcludeCategories)
    def on_exclude_categories(self, excluder, excluded):
        cat_id = self.category['id']
        if excluder is cat_id:
            self.category['excluded'] = False
            return
        if '*' in excluded or cat_id in excluded:
            self.category['excluded'] = True
            self.exclude_texture.state = uiconst.UI_DISABLED
            self.selected_texture.opacity = 0
        else:
            self.category['excluded'] = False
            self.exclude_texture.state = uiconst.UI_HIDDEN
            if self.category['selected']:
                self.selected_texture.opacity = 1

    @on_event(const.Events.ContinueFromResult)
    def reset_result(self):
        self.reset()

    @on_event(const.Events.ContinueFromTrainingResult)
    def reset(self):
        self.category['selected'] = False
        self.category['excluded'] = False
        self.correct_texture.opacity = 0
        self.unmatched_texture.opacity = 0
        self.missed_texture.opacity = 0
        self.selected_texture.opacity = 0
        self.exclude_texture.state = uiconst.UI_HIDDEN


class CategoryTooltipWrapper(TooltipBaseWrapper):
    IMAGE_SIZE = 300

    def __init__(self, header, description, image, *args, **kwargs):
        self._headerText = header
        self._descriptionText = description
        self._image = image

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.tooltipPanel.AddLabelMedium(text=self._headerText, bold=True, cellPadding=(0, 5, 0, 5), wrapWidth=300)
        self.tooltipPanel.AddLabelMedium(text=self._descriptionText, align=uiconst.TOPLEFT, wrapWidth=300, color=(0.6, 0.6, 0.6, 1))
        image_container = uiprimitives.Container(width=self.IMAGE_SIZE, height=self.IMAGE_SIZE, align=uiconst.TOPLEFT)
        FrameThemeColored(bgParent=image_container, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        uiprimitives.Sprite(parent=image_container, width=self.IMAGE_SIZE - 2, height=self.IMAGE_SIZE - 2, texturePath=self._image, align=uiconst.CENTER)
        self.tooltipPanel.AddCell(image_container, cellPadding=(0, 5, 0, 5))
        return self.tooltipPanel
