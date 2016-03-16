#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\tutorial.py
from carbonui.primitives.fill import Fill
from eve.client.script.ui.control.eveLabel import EveLabelLarge, EveLabelMedium
from eve.client.script.ui.control.tooltips import TooltipPersistentPanel
from projectdiscovery.client.const import Events as events
import uthread
import uicontrols
import localization
import carbonui.const as uiconst
from eve.client.script.ui.control.pointerPanel import RefreshPanelPosition
from projectdiscovery.client.util.eventlistener import eventlistener, on_event

@eventlistener()

class Tutorial(object):

    def __init__(self):
        self.steps = []
        self.sub_categories = {}
        self.category_selector = None

    def _step(self):
        try:
            if not self.current:
                next_step = self.steps[0]
            else:
                self._close_step(self.current)
                self.index += 1
                next_step = self.steps[self.index]
            next_step['owner'].state = uiconst.UI_NORMAL
            if next_step['owner'].name == 'CategorySelector':
                self.category_selector = next_step['owner']
                for cat in next_step['owner'].super_categories:
                    for sub in cat.sub_categories:
                        if not sub.unavailable:
                            self.sub_categories[sub.id] = True
                        else:
                            sub.set_available()
                            self.sub_categories[sub.id] = False

            self.current = uicore.uilib.tooltipHandler.LoadPersistentTooltip(next_step['owner'], loadArguments=(next_step['header'],
             next_step['text'],
             lambda : self._step(),
             lambda : self.quit()), customTooltipClass=BasicTutorialTooltip)
            self._fade(next_step['owner'], 1.0)
        except IndexError:
            self.quit()

    def _close_step(self, step):
        step.CloseWithFade()
        if step.owner.name == 'ImagesContainer':
            self.task_image = step.owner.parent
            self.task_image.mini_map_container.opacity = 0
            self.task_image.zoom_image_container.opacity = 0
            self.task_image.image_sprite.opacity = 1
            self.task_image.is_zoom_fixed = False
        if not step.owner.name == 'CategorySelector':
            step.owner.state = uiconst.UI_DISABLED
            self._fade(step.owner, 0.3)
        else:
            for cat in step.owner.super_categories:
                cat.state = uiconst.UI_DISABLED
                self._fade(cat, 0.3)

    def _fade(self, item, end_val):
        uthread.new(uicore.animations.FadeTo, item, startVal=item.opacity, endVal=end_val, duration=0.2)

    def add_steps(self, steps):
        self.steps += steps

    def start(self):
        for step in self.steps:
            if not step['owner'].name == 'CategoryGroup':
                self._fade(step['owner'], 0.3)
                step['owner'].state = uiconst.UI_DISABLED

        self.current = None
        self.index = 0
        self._step()

    def quit(self):
        if not self.current.destroyed:
            self._close_step(self.current)
        for step in self.steps:
            self._fade(step['owner'], 1)
            step['owner'].state = uiconst.UI_NORMAL

        self.task_image.mini_map_container.opacity = 1
        self.task_image.zoom_image_container.opacity = 1
        if self.category_selector:
            for cat in self.category_selector.super_categories:
                for sub in cat.sub_categories:
                    if sub.category['selected']:
                        sub.category['selected'] = False
                        sub.selected_texture.opacity = 0
                        sm.ScatterEvent(events.CategoryChanged, sub.category)
                    if not self.sub_categories[sub.id]:
                        sub.set_unavailable()

        sm.ScatterEvent(events.QuitTutorial)


class TutorialTooltip(TooltipPersistentPanel):
    picktestEnabled = False

    def ApplyAttributes(self, attributes):
        attributes['parent'] = uicore.layer.menu
        super(TutorialTooltip, self).ApplyAttributes(attributes)
        self.owner = attributes.get('owner')
        self.pickState = uiconst.TR2_SPS_ON
        uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVEDRAG, self.OnGlobalMouseMoveDrag)

    def OnGlobalMouseMoveDrag(self, *args):
        if not self.destroyed:
            RefreshPanelPosition(self)
            return True
        return False


class BasicTutorialTooltip(TutorialTooltip):
    default_columns = 2
    default_margin = (12, 4, 12, 4)
    default_cellPadding = 0
    default_cellSpacing = 0

    def ApplyAttributes(self, attributes):
        super(BasicTutorialTooltip, self).ApplyAttributes(attributes)

    def LoadTooltip(self, header, description, on_continue, on_quit):
        self.AddCell(EveLabelLarge(text=header, state=uiconst.UI_DISABLED, width=250), width=250)
        self.AddCell(uicontrols.ButtonIcon(texturePath='res:/UI/Texture/icons/38_16_220.png', iconSize=16, width=16, height=16, func=on_quit), margin=(0, 0, 0, 0))
        self.AddCell(Fill(align=uiconst.TOTOP, state=uiconst.UI_DISABLED, color=(1, 1, 1, 0.3), height=1, padding=(0, 3, 0, 3)), colSpan=self.columns)
        self.AddCell(EveLabelMedium(text=description, state=uiconst.UI_DISABLED, width=250), width=250, colSpan=self.columns)
        self.AddCell(uicontrols.Button(label=localization.GetByLabel('UI/ProjectDiscovery/TutorialContinueButtonLabel'), align=uiconst.CENTER, func=lambda _: on_continue()), colSpan=self.columns)
