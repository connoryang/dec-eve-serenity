#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\resultwindow.py
__author__ = 'ru.Hjalti'
import math
import uicontrols
import uiprimitives
import localization
from carbonui.uianimations import animations
from info import INFO as PROJECT_INFO
from projectdiscovery.client import const
from categoryselector import CategorySelector
from carbon.common.script.util.format import FmtAmt
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipBaseWrapper
from eve.client.script.ui.control.eveLabel import *

def _nested_categories_from_json(categories):
    keyed = {cat['id']:cat for cat in categories}
    nested = {}
    for cat in categories:
        cat['children'] = []
        cat['selected'] = False
        if not cat['parentId']:
            nested[cat['id']] = cat
        elif cat['parentId'] in keyed:
            keyed[cat['parentId']]['children'].append(cat)

    return nested


class ResultWindow(uiprimitives.Container):

    def ApplyAttributes(self, attributes):
        super(ResultWindow, self).ApplyAttributes(attributes)
        self.isTrainingPhase = attributes.get('isTrainingPhase')
        self.projectdiscoverySvc = sm.RemoteSvc('ProjectDiscovery')
        self.finishedTraining = False
        self.setup_layout()

    def setup_layout(self):
        self.left_main_container = uiprimitives.Container(name='left_main_container', parent=self, align=uiconst.TOLEFT, width=475)
        self.task_label = EveCaptionLarge(parent=self.left_main_container, align=uiconst.CENTERTOP, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderText'), top=35, color=(0.498, 0.627, 0.74, 1))
        self.category_container = uiprimitives.Container(name='category_container', parent=self, align=uiconst.CENTERRIGHT, width=404, height=385)
        self.categories_selected = CategorySelector(name='CategoriesSelected', categories=_nested_categories_from_json(PROJECT_INFO['info']['classes']), parent=self.category_container, state=uiconst.UI_DISABLED)
        self.legend_icon = LegendIcon(name='legendIcon', parent=self.category_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/helpTooltipUp.png', top=10, left=90, align=uiconst.BOTTOMRIGHT, width=28, height=28, idx=0)
        self.legend_label = uicontrols.Label(parent=self.category_container, align=uiconst.BOTTOMRIGHT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/LegendIconLabel'), top=15, left=50)
        self.main_button_container = uiprimitives.Container(name='continueButtonContainer', parent=self, align=uiconst.CENTERBOTTOM, width=355, height=53, top=3, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/footerBG.png')
        self.continue_button_container = uiprimitives.Container(name='submitButtonContainer', parent=self.main_button_container, width=250, align=uiconst.CENTER, height=40, top=5)
        self.continue_button = uicontrols.Button(name='resultContinueButton', parent=self.continue_button_container, align=uiconst.CENTER, label=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/ContinueButtonLabel'), fontsize=18, fixedwidth=170, fixedheight=30)
        uiprimitives.Sprite(parent=self.continue_button_container, align=uiconst.CENTERLEFT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)
        uiprimitives.Sprite(parent=uiprimitives.Transform(parent=self.continue_button_container, align=uiconst.CENTERRIGHT, width=34, height=20, rotation=math.pi), align=uiconst.CENTERRIGHT, width=34, height=20, texturePath='res:/UI/Texture/classes/ProjectDiscovery/submitArrow.png', opacity=0.7)

    def close(self):
        if self.isTrainingPhase:
            sm.ScatterEvent(const.Events.ContinueFromTrainingResult)
            sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowLoopStop)
            sm.GetService('audio').SendUIEvent(const.Sounds.RewardsWindowClosePlay)
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)
        else:
            sm.ScatterEvent(const.Events.CloseResult, self.result)
            sm.ScatterEvent(const.Events.ContinueFromResult)
        animations.FadeOut(self, duration=0.4)
        self.categories_selected.cascade_categories_out()
        self.state = uiconst.UI_DISABLED
        self.category_container.state = uiconst.UI_DISABLED
        self.categories_selected.state = uiconst.UI_DISABLED
        self.continue_button.func = None
        self.solutionIsUnknown = False

    def assign_result(self, result):
        self.result = result
        self.solutionIsUnknown = 'votes' in result['task']
        if self.solutionIsUnknown:
            self.task_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderTextUnknown'))
            self.legend_icon.tooltipPanelClassInfo = LegendTooltipWrapper(known_solution=False)
        else:
            self.task_label.SetText(localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/WindowHeaderText'))
            self.legend_icon.tooltipPanelClassInfo = LegendTooltipWrapper(known_solution=True)

    def open(self):
        self.state = uiconst.UI_NORMAL
        for super_cat in self.categories_selected.super_categories:
            for subcat in super_cat.sub_categories:
                subcat.set_available()
                if self.solutionIsUnknown:
                    subcat.color_overlay.opacity = 0
                    subcat.hide_percentage()
                    subcat.set_unavailable()
                    if subcat.category['id'] in self.result['playerSelection']:
                        subcat.set_selected()
                        subcat.set_available()
                        subcat.set_percentage(str(0))
                        subcat.show_percentage()
                    else:
                        subcat.set_unselected()
                    if self.result['task']['votes']:
                        for vote in self.result['task']['votes']:
                            if subcat.category['id'] == vote['result']:
                                if vote['percentage'] > 0 or subcat.category['id'] in self.result['playerSelection']:
                                    subcat.color_overlay.opacity = 1
                                    subcat.show_percentage()
                                    subcat.set_percentage(FmtAmt(vote['percentage'] * 100, showFraction=0))
                                    color = subcat.lerp_color(vote['percentage'], 1)
                                    subcat.color_overlay.SetRGB(color[0], color[1], color[2], 1)
                                    subcat.set_available()
                                else:
                                    subcat.color_overlay.opacity = 0
                                    subcat.hide_percentage()
                                    subcat.set_unavailable()

                else:
                    if subcat.category['id'] not in self.result['playerSelection'] and subcat.category['id'] not in self.result['task']['solution']:
                        subcat.set_unavailable()
                    elif subcat.category['id'] in self.result['playerSelection'] and subcat.category['id'] in self.result['task']['solution']:
                        subcat.correct_texture.opacity = 1
                    elif subcat.category['id'] in self.result['playerSelection'] and subcat.category['id'] not in self.result['task']['solution']:
                        subcat.unmatched_texture.opacity = 1
                    elif subcat.category['id'] not in self.result['playerSelection'] and subcat.category['id'] in self.result['task']['solution']:
                        subcat.missed_texture.opacity = 1
                    subcat.set_unselected()
                subcat.exclude_texture.state = uiconst.UI_HIDDEN
                subcat.category['selected'] = False
                subcat.set_unclickable()

        animations.FadeIn(self, callback=self.enable_close)
        self.categories_selected.cascade_categories_in()

    def enable_cats(self):
        self.category_container.state = uiconst.UI_NORMAL
        self.categories_selected.state = uiconst.UI_NORMAL

    def enable_close(self):
        self.continue_button.func = lambda x: self.close()
        self.enable_cats()


class LegendIcon(uiprimitives.Sprite):

    def OnMouseEnter(self, *args):
        self.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/helpTooltipOver.png')

    def OnMouseExit(self, *args):
        self.SetTexturePath('res:/UI/Texture/classes/ProjectDiscovery/helpTooltipUp.png')


class LegendTooltipWrapper(TooltipBaseWrapper):

    def __init__(self, known_solution):
        self._knownSolution = known_solution

    def CreateTooltip(self, parent, owner, idx):
        self.tooltipPanel = TooltipPanel(parent=parent, owner=owner, idx=idx)
        self.tooltipPanel.LoadGeneric1ColumnTemplate()
        self.legend_container = uiprimitives.Container(name='legendContainer', align=uiconst.TOPLEFT, height=210, width=210)
        if self._knownSolution:
            self.create_known_solution_tooltip()
        else:
            self.create_unknown_solution_tooltip()
        self.tooltipPanel.AddCell(self.legend_container, cellPadding=(0, 5, 0, -10))
        return self.tooltipPanel

    def create_unknown_solution_tooltip(self):
        self.selection_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.selection_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.selection_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categorySelected.png')
        self.selection_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.selection_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.TOLEFT, width=50)
        self.selection_legend_label_header = EveLabelMediumBold(parent=self.selection_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/SelectionLegendLabelHeader'), align=uiconst.TOPLEFT, top=20, left=5)
        self.popular_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.popular_sprite_container = uiprimitives.Container(parent=self.popular_legend_container, align=uiconst.TOLEFT, width=55)
        self.popular_other_hex = uiprimitives.Sprite(parent=self.popular_sprite_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', height=40, width=44, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))
        self.popular_other_sprite = uiprimitives.Sprite(parent=self.popular_sprite_container, height=32, width=36, top=4, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png')
        self.popular_other_sprite.SetRGB(0.33, 0.49, 0.26, 1)
        self.popular_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.popular_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65, top=-5)
        self.popular_legend_label_header = EveLabelMediumBold(parent=self.popular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/PopularLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.popular_legend_label = uicontrols.Label(parent=self.popular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/PopularLegendLabel'), align=uiconst.CENTERLEFT, width=200)
        self.unpopular_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.unpopular_sprite_container = uiprimitives.Container(parent=self.unpopular_legend_container, align=uiconst.TOLEFT, width=55)
        self.unpopular_other_hex = uiprimitives.Sprite(parent=self.unpopular_sprite_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexOutline.png', height=40, width=44, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, color=(0.32, 0.32, 0.32, 1))
        self.unpopular_other_sprite = uiprimitives.Sprite(parent=self.unpopular_sprite_container, height=32, width=36, top=4, align=uiconst.CENTERTOP, texturePath='res:/UI/Texture/classes/ProjectDiscovery/hexMask.png')
        self.unpopular_other_sprite.SetRGB(0.5, 0.22, 0.17, 1)
        self.unpopular_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.unpopular_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65, top=-5)
        self.unpopular_legend_label_header = EveLabelMediumBold(parent=self.unpopular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnpopularLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.unpopular_legend_label = uicontrols.Label(parent=self.unpopular_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnpopularLegendLabel'), align=uiconst.CENTERLEFT, width=150)

    def create_known_solution_tooltip(self):
        self.correct_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.correct_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.correct_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMatch.png')
        self.correct_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.correct_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.correct_legend_label_header = EveLabelMediumBold(parent=self.correct_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/CorrectLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.correct_legend_label = uicontrols.Label(parent=self.correct_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/CorrectLegendLabel'), align=uiconst.CENTERLEFT, width=200)
        self.missed_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.missed_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.missed_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryMissed.png')
        self.missed_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.missed_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.missed_legend_label_header = EveLabelMediumBold(parent=self.missed_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/MissedLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.missed_legend_label = uicontrols.Label(parent=self.missed_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/MissedLegendLabel'), align=uiconst.CENTERLEFT, width=150)
        self.unmatched_legend_container = uiprimitives.Container(parent=self.legend_container, align=uiconst.TOTOP, height=70)
        self.unmatched_legend_sprite = uiprimitives.Sprite(parent=uiprimitives.Container(parent=self.unmatched_legend_container, align=uiconst.TOLEFT, width=55), height=51, width=54, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ProjectDiscovery/categoryWrong.png')
        self.unmatched_legend_label_container = uiprimitives.Container(parent=uiprimitives.Container(parent=self.unmatched_legend_container, align=uiconst.TOLEFT, width=145), align=uiconst.CENTERLEFT, width=50, height=65)
        self.unmatched_legend_label_header = EveLabelMediumBold(parent=self.unmatched_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnmatchedLegendLabelHeader'), align=uiconst.TOPLEFT)
        self.unmatched_legend_label = uicontrols.Label(parent=self.unmatched_legend_label_container, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/ResultScreen/UnmatchedLegendLabel'), align=uiconst.CENTERLEFT, width=150)
