#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\projects\subcellular\taskimages.py
__author__ = 'ru.Hjalti'
import math
import uicontrols
import uiprimitives
import carbonui.const as uiconst
import logging
import localization
from projectdiscovery.client import const
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from projectdiscovery.client.util.eventlistener import eventlistener, on_event
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveCaptionSmall
from carbon.common.script.util.format import FmtAmt
logger = logging.getLogger(__name__)

@eventlistener()

class TaskImage(uiprimitives.Container):

    def ApplyAttributes(self, attributes):
        super(TaskImage, self).ApplyAttributes(attributes)
        self.selected_channel = 'channelGreenBlueRed'
        self.images = {'channelGreenBlueRed': None,
         'channelGreen': None,
         'channelGreenBlue': None,
         'channelGreenRed': None}
        self.service = sm.RemoteSvc('ProjectDiscovery')
        self.is_zoom_fixed = False
        self.transmitting_container = uiprimitives.Container(name='transmitting_container', parent=self, align=uiconst.CENTER, width=364, height=70, top=-15, opacity=0, state=uiconst.UI_DISABLED)
        self.label_container = uiprimitives.Container(parent=self.transmitting_container, width=225, height=20, align=uiconst.CENTER, fontsize=16)
        self.processing_percentage_label = EveCaptionSmall(parent=self.label_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/ProjectDiscovery/Subcellular/RewardsScreen/ProcessingLabel'))
        self.processing_percentage = EveCaptionSmall(parent=self.label_container, align=uiconst.CENTERRIGHT, text='0%')
        self.expandTopContainer = uiprimitives.Container(name='expandTopContainer', parent=self.transmitting_container, width=364, height=8, align=uiconst.TOTOP)
        uiprimitives.Sprite(name='expandTop', parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERTOP)
        uiprimitives.Sprite(parent=self.expandTopContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=364, height=3, align=uiconst.CENTERTOP, top=5)
        self.expandBottomContainer = uiprimitives.Transform(name='expandBottomContainer', parent=self.transmitting_container, width=364, height=8, align=uiconst.TOBOTTOM, rotation=math.pi)
        uiprimitives.Sprite(parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandBrackets.png', width=364, height=3, align=uiconst.CENTERTOP, top=5)
        uiprimitives.Sprite(name='expandBot', parent=self.expandBottomContainer, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandTop.png', width=174, height=5, align=uiconst.CENTERBOTTOM, top=3)
        self.expandGradient = uiprimitives.Sprite(parent=self.transmitting_container, align=uiconst.CENTER, width=364, height=64, texturePath='res:/UI/Texture/classes/ProjectDiscovery/expandGradient.png')
        self.colorFilterContainer = uiprimitives.Container(name='colorFilterContainer', parent=self, align=uiconst.CENTERBOTTOM, width=187, height=32)
        self.colorFilterButtonsContainer = uiprimitives.Container(name='colorFilterButtonsContainer', parent=self.colorFilterContainer, align=uiconst.CENTERTOP, width=120, height=24)
        self.selectedFilter = uiprimitives.Container(name='selectedFilter', parent=self.colorFilterButtonsContainer, width=30, height=24, align=uiconst.TOPLEFT, bgTexturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSelection.png')
        self.colorCube = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, iconSize=30, opacity=2, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterCubeNew.png', func=self.rgbchosen)
        self.colorSwatchGreen = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, iconSize=30, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_Gnew.png', func=self.gchosen)
        self.colorSwatchGreenBlue = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, iconSize=30, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_GBnew.png', func=self.gbchosen)
        self.colorSwatchRedGreen = uicontrols.ButtonIcon(parent=self.colorFilterButtonsContainer, align=uiconst.TOLEFT, width=30, height=24, iconSize=30, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterSwatch_RGnew.png', func=self.rgchosen)
        self.colorFilterBack = uiprimitives.Sprite(parent=self.colorFilterContainer, align=uiconst.CENTER, width=187, height=32, texturePath='res:/UI/Texture/classes/ProjectDiscovery/colorFilterBack.png')
        self.images_container = uiprimitives.Container(name='ImagesContainer', parent=self, align=uiconst.CENTERTOP, width=384, height=384, clipChildren=True)
        self.image_locked_sprite = uiprimitives.Sprite(name='lockImage', parent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/magnifyLocked.png', width=54, height=64, align=uiconst.CENTER, opacity=0, state=uiconst.UI_DISABLED)
        self.image_unlocked_sprite = uiprimitives.Sprite(name='unlockImage', parent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/magnifyUnlocked.png', width=108, height=64, align=uiconst.CENTER, opacity=0, state=uiconst.UI_DISABLED)
        self.image_container = uiprimitives.Container(name='mainImageContainer', parent=self.images_container, align=uiconst.CENTER, width=384, height=384, clipChildren=True)
        self.image_frame = uicontrols.Frame(name='imageFrame', bgParent=self.images_container, texturePath='res:/UI/Texture/classes/ProjectDiscovery/SampleBack.png', cornerSize=20)
        self.loading_wheel = LoadingWheel(name='SampleLoadingIndicator', parent=self.images_container, align=uiconst.CENTER, width=64, height=64)
        self.image_sprite = SubCellularSprite(name='mainImage', parent=self.image_container, width=364, height=364, top=10, left=10, opacity=1)
        self.image_sprite.texture = None
        self.mini_map_container = uiprimitives.Container(name='miniMapContainer', parent=self.images_container, align=uiconst.BOTTOMRIGHT, width=100, height=100, top=12, left=12)
        self.mini_map_container_frame = uicontrols.Frame(name='zoomContainerFrame', parent=self.mini_map_container, state=uiconst.UI_HIDDEN)
        self.mini_map_frame_container = uiprimitives.Container(name='miniMapFrameContainer', parent=self.mini_map_container, align=uiconst.TOPLEFT, width=30, height=30)
        self.mini_map_frame = uicontrols.Frame(name='zoomFrame', parent=self.mini_map_frame_container, state=uiconst.UI_HIDDEN)
        self.mini_map_image_sprite = uiprimitives.Sprite(name='miniMapSprite', parent=self.mini_map_container, width=100, height=100)
        self.zoom_image_container = uiprimitives.Container(name='zoomContainer', parent=self.images_container, align=uiconst.CENTER, width=364, height=364, clipChildren=True)
        self.zoom_image_sprite = uiprimitives.Sprite(name='zoomSprite', parent=self.zoom_image_container, width=1200, height=1200)
        self.error_message = uicontrols.Label(parent=self.images_container, align=uiconst.CENTER, text='Could not load image, please try again.', opacity=0)
        self.oldTranslationTop = self.expandTopContainer.translation
        self.oldTranslationBottom = self.expandBottomContainer.translation

    def gchosen(self):
        sm.GetService('audio').SendUIEvent(const.Sounds.ColorSelectPlay)
        self.image_sprite.SetRGB(0, 1, 0)
        self.zoom_image_sprite.SetRGB(0, 1, 0)
        self.mini_map_image_sprite.SetRGB(0, 1, 0)
        if self.is_zoom_fixed:
            self.image_sprite.opacity = 0
        self.colorSwatchGreen.isSelected = True
        self.colorCube.isSelected = False
        self.colorSwatchGreenBlue.isSelected = False
        self.colorSwatchRedGreen.isSelected = False
        self.colorCube.opacity = 1
        self.colorSwatchGreen.opacity = 2
        self.colorSwatchGreenBlue.opacity = 1
        self.colorSwatchRedGreen.opacity = 1
        self.selectedFilter.left = 30

    def gbchosen(self):
        sm.GetService('audio').SendUIEvent(const.Sounds.ColorSelectPlay)
        self.image_sprite.SetRGB(0, 1, 1)
        self.zoom_image_sprite.SetRGB(0, 1, 1)
        self.mini_map_image_sprite.SetRGB(0, 1, 1)
        if self.is_zoom_fixed:
            self.image_sprite.opacity = 0
        self.colorSwatchGreenBlue.isSelected = True
        self.colorCube.isSelected = False
        self.colorSwatchGreen.isSelected = False
        self.colorSwatchRedGreen.isSelected = False
        self.colorCube.opacity = 1
        self.colorSwatchGreen.opacity = 1
        self.colorSwatchGreenBlue.opacity = 2
        self.colorSwatchRedGreen.opacity = 1
        self.selectedFilter.left = 60

    def rgchosen(self):
        sm.GetService('audio').SendUIEvent(const.Sounds.ColorSelectPlay)
        self.image_sprite.SetRGB(1, 1, 0)
        self.zoom_image_sprite.SetRGB(1, 1, 0)
        self.mini_map_image_sprite.SetRGB(1, 1, 0)
        if self.is_zoom_fixed:
            self.image_sprite.opacity = 0
        self.colorSwatchRedGreen.isSelected = True
        self.colorCube.isSelected = False
        self.colorSwatchGreen.isSelected = False
        self.colorSwatchGreenBlue.isSelected = False
        self.colorCube.opacity = 1
        self.colorSwatchGreen.opacity = 1
        self.colorSwatchGreenBlue.opacity = 1
        self.colorSwatchRedGreen.opacity = 2
        self.selectedFilter.left = 90

    def _set_image(self, channel_id):
        self.error_message.SetAlpha(0)
        self.loading_wheel.opacity = 1
        if Audio.play_sound:
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopStop)
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadPlay)
        self.image_sprite.texture = None
        self.zoom_image_sprite.texture = None
        self.mini_map_image_sprite.texture = None
        self.mini_map_container_frame.state = uiconst.UI_HIDDEN
        self.mini_map_frame.state = uiconst.UI_HIDDEN
        self.selected_channel = channel_id
        self.image_sprite.texture = sm.GetService('photo').GetTextureFromURL(self.images[channel_id], retry=False)[0]
        if self.image_sprite.texture.resPath.startswith('res:'):
            self.error_message.SetAlpha(1)
            self.images[channel_id] = None
        self.zoom_image_sprite.texture = self.image_sprite.texture
        self.mini_map_image_sprite.texture = self.image_sprite.texture
        self.loading_wheel.opacity = 0
        if self.is_zoom_fixed:
            self.mini_map_container_frame.state = uiconst.UI_NORMAL
            self.mini_map_frame.state = uiconst.UI_NORMAL
        if Audio.play_sound:
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoadStop)
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageOpenPlay)
            sm.GetService('audio').SendUIEvent(const.Sounds.MainImageLoopPlay)

    def rgbchosen(self):
        if self.image_sprite.texture:
            self.image_sprite.SetRGB(1, 1, 1)
            self.zoom_image_sprite.SetRGB(1, 1, 1)
            self.mini_map_image_sprite.SetRGB(1, 1, 1)
            if self.is_zoom_fixed:
                self.image_sprite.opacity = 0
        else:
            self.image_sprite.SetRGB(1, 1, 1)
            self.zoom_image_sprite.SetRGB(1, 1, 1)
            self.mini_map_image_sprite.SetRGB(1, 1, 1)
            self._set_image('channelGreenBlueRed')
        sm.ScatterEvent(const.Events.MainImageLoaded)
        sm.GetService('audio').SendUIEvent(const.Sounds.ColorSelectPlay)
        self.colorCube.isSelected = True
        self.colorSwatchGreen.isSelected = False
        self.colorSwatchGreenBlue.isSelected = False
        self.colorSwatchRedGreen.isSelected = False
        self.colorCube.opacity = 2
        self.colorSwatchGreen.opacity = 1
        self.colorSwatchGreenBlue.opacity = 1
        self.colorSwatchRedGreen.opacity = 1
        self.selectedFilter.left = 0

    @on_event(const.Events.NewTask)
    def on_new_task(self, task, securitypass):
        self.image_frame.SetRGB(1, 1, 1, 0.5)
        self.task = task
        self.secPass = securitypass
        self.images['channelGreenBlueRed'] = task['assets']['url']
        self.images['channelGreen'] = None
        self.images['channelGreenBlue'] = None
        self.images['channelGreenRed'] = None
        self.rgbchosen()
        self.image_sprite.opacity = 1
        self.is_zoom_fixed = False

    def reset(self):
        if hasattr(self, 'image_sprite'):
            self.image_sprite.texture = None
            self.zoom_image_sprite.texture = None
            self.mini_map_image_sprite.texture = None
            self.loading_wheel.opacity = 1

    @on_event(const.Events.ClickMainImage)
    def fix_post(self):
        animations.FadeTo(self.image_frame, duration=0.3, endVal=2.0, startVal=1.0, curveType=uiconst.ANIM_BOUNCE)
        self.is_zoom_fixed = not self.is_zoom_fixed
        if self.is_zoom_fixed:
            self.fade_in_lock()
        else:
            self.fade_in_unlock()

    def fade_in_lock(self):
        animations.FadeIn(self.image_locked_sprite, duration=0.3, endVal=0.5, callback=self.fade_out_lock)

    def fade_out_lock(self):
        animations.FadeOut(self.image_locked_sprite, duration=0.5)

    def fade_in_unlock(self):
        animations.FadeIn(self.image_unlocked_sprite, duration=0.3, endVal=0.5, callback=self.fade_out_unlock)

    def fade_out_unlock(self):
        animations.FadeOut(self.image_unlocked_sprite, duration=0.5)

    @on_event(const.Events.HoverMainImage)
    def zoom_in(self):
        if self.image_sprite.texture is None or self.image_sprite.texture.resPath.startswith('res:'):
            return
        self.mini_map_container.SetOpacity(1)
        if self.is_zoom_fixed:
            self.image_sprite.opacity = 0
            uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)
        else:
            mouse_position = (uicore.uilib.x, uicore.uilib.y)
            img_position = self.image_sprite.GetAbsolutePosition()
            zoom_aspect_ratio = self.zoom_image_sprite.width / float(self.image_sprite.width) - 1
            if mouse_position[1] - img_position[1] > 364 or mouse_position[1] - img_position[1] < 0 or mouse_position[0] - img_position[0] > 364 or mouse_position[0] - img_position[0] < 0:
                self.image_sprite.opacity = 1
                uicore.uilib.SetCursor(uiconst.UICURSOR_POINTER)
            else:
                self.image_sprite.opacity = 0
                if self.image_sprite.texture:
                    self.mini_map_frame.state = uiconst.UI_NORMAL
                    self.mini_map_container_frame.state = uiconst.UI_NORMAL
                uicore.uilib.SetCursor(uiconst.UICURSOR_MAGNIFIER)
                self.zoom_image_sprite.left = (img_position[0] - mouse_position[0]) * zoom_aspect_ratio
                self.zoom_image_sprite.top = (img_position[1] - mouse_position[1]) * zoom_aspect_ratio
                self.mini_map_frame_container.left = self.zoom_image_sprite.left / -12
                self.mini_map_frame_container.top = self.zoom_image_sprite.top / -12

    @on_event(const.Events.MouseExitMainImage)
    def on_mouse_exit_main_image(self):
        animations.FadeTo(self.image_frame, duration=0.3, endVal=0.5, startVal=1.0)
        if self.is_zoom_fixed:
            self.mini_map_container.SetOpacity(0)

    @on_event(const.Events.MouseEnterMainImage)
    def on_mouse_enter_main_image(self):
        animations.FadeIn(self.image_frame, duration=0.3)

    def reset_animation(self):
        self.expandTopContainer.translation = self.oldTranslationTop
        self.expandBottomContainer.translation = self.oldTranslationBottom
        self.expandGradient.height = 64

    @property
    def gradient_height(self):
        return self._gradient_height

    @gradient_height.setter
    def gradient_height(self, value):
        self._gradient_height = value
        self.expandGradient.SetSize(364, self._gradient_height)

    def gradient_height_callback(self):
        self.gradient_height = 364
        animations.FadeOut(self.transmitting_container, callback=self.reset_animation)
        if self.is_zoom_fixed:
            animations.FadeIn(self.zoom_image_sprite)
        else:
            animations.FadeIn(self.image_sprite)
            self.zoom_image_sprite.SetAlpha(1)
        sm.ScatterEvent(const.Events.TransmissionFinished)

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        self._percentage = value
        self.processing_percentage.SetText(str(FmtAmt(self._percentage)) + '%')

    def percentage_callback(self):
        self.percentage = 100
        self.move_image_out()
        sm.ScatterEvent(const.Events.ResultReceived)
        sm.GetService('audio').SendUIEvent(const.Sounds.ProcessingStop)
        sm.GetService('audio').SendUIEvent(const.Sounds.AnalysisDonePlay)

    def start_transmission_animation(self):
        self.reset_animation()
        sm.GetService('audio').SendUIEvent(const.Sounds.ProcessingPlay)
        self.mini_map_container.SetOpacity(0)
        self.move_image_in()
        self.percentage = 0
        if self.is_zoom_fixed:
            animations.FadeTo(self.zoom_image_sprite, startVal=1.0, endVal=0.5)
            self.image_sprite.SetAlpha(0)
        else:
            animations.FadeTo(self.image_sprite, startVal=1.0, endVal=0.5)
            self.zoom_image_sprite.SetAlpha(0)
        animations.FadeIn(self.transmitting_container, duration=0.5)
        animations.MorphScalar(self, 'percentage', startVal=self.percentage, endVal=100, curveType=uiconst.ANIM_LINEAR, duration=3, callback=self.percentage_callback)

    def expand_screen(self):
        self.oldTranslationTop = self.expandTopContainer.translation
        self.oldTranslationBottom = self.expandBottomContainer.translation
        translationtop = (self.expandTopContainer.displayX, -145.0)
        translationbottom = (self.expandBottomContainer.displayX, -150.0)
        self.image_frame.SetRGB(0.498, 0.627, 0.74, 0.5)
        animations.MoveTo(self.expandTopContainer, startPos=(0, 0), endPos=translationtop, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.MoveTo(self.expandBottomContainer, startPos=(0, 0), endPos=translationbottom, duration=0.2, curveType=uiconst.ANIM_LINEAR)
        animations.MorphScalar(self, 'gradient_height', startVal=48, endVal=365, curveType=uiconst.ANIM_LINEAR, duration=0.2, callback=self.gradient_height_callback)
        sm.GetService('audio').SendUIEvent(const.Sounds.AnalysisWindowMovePlay)

    def move_image_in(self):
        animations.SpShadowAppear(self.image_sprite, duration=1, curveType=uiconst.ANIM_BOUNCE)
        animations.MoveTo(self.parent, startPos=(0, 0), endPos=(200, 0), duration=1)

    def move_image_out(self):
        animations.SpShadowDisappear(self.image_sprite, duration=1, curveType=uiconst.ANIM_BOUNCE)
        animations.MoveTo(self.parent, startPos=(200, 0), endPos=(0, 0), duration=1, timeOffset=0.8, callback=self.expand_screen)


class Audio():
    _play_sound = True

    @property
    def play_sound(self):
        return self._play_sound

    @play_sound.setter
    def play_sound(self, val):
        self._play_sound = val


class SubCellularSprite(uiprimitives.Sprite):

    def OnClick(self, *args):
        sm.ScatterEvent(const.Events.ClickMainImage)

    def OnMouseMoveDrag(self, *args):
        sm.ScatterEvent(const.Events.HoverMainImage)

    def OnMouseExit(self, *args):
        sm.ScatterEvent(const.Events.MouseExitMainImage)

    def OnMouseEnter(self, *args):
        sm.ScatterEvent(const.Events.MouseEnterMainImage)
