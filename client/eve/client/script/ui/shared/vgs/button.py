#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\button.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import EveHeaderMedium, EveHeaderSmall
from eve.client.script.ui.shared.vgs.label import VgsButtonLabelMedium
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
from eve.client.script.ui.shared.monetization.events import LogBuyPlexOnlineClicked
import localization
import log
import math
import numbers
import trinity
import uthread
COLOR_AUR = (0.769, 0.322, 0.263, 1.0)
COLOR_ISK = (0.2, 0.6, 0.8, 1.0)
COLOR_PLEX = (0.902, 0.659, 0.18, 1.0)

@Component(ButtonEffect(audioOnEntry='store_menuhover', audioOnClick='store_click'))

class ButtonCore(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    default_color = (0.4, 0.4, 0.4, 1.0)
    default_contentSpacing = 3
    default_iconSize = (16, 16)
    default_labelClass = EveHeaderSmall
    default_labelColor = (1.0, 1.0, 1.0, 1.0)
    default_labelShadow = False
    default_labelShadowColor = (0.0, 0.0, 0.0, 0.25)
    default_labelTop = 0
    default_padding = (4, 4, 4, 4)
    default_state = uiconst.UI_NORMAL
    default_text = None
    default_texturePath = None

    def ApplyAttributes(self, attributes):
        self.onClick = attributes.get('onClick', None)
        color = attributes.pop('color', self.default_color)
        contentSpacing = attributes.pop('contentSpacing', self.default_contentSpacing)
        iconSize = attributes.pop('iconSize', self.default_iconSize)
        labelClass = attributes.pop('labelClass', self.default_labelClass)
        labelColor = attributes.pop('labelColor', self.default_labelColor)
        labelShadow = attributes.pop('labelShadow', self.default_labelShadow)
        labelShadowColor = attributes.pop('labelShadowColor', self.default_labelShadowColor)
        labelTop = attributes.pop('labelTop', self.default_labelTop)
        padding = attributes.pop('padding', self.default_padding)
        text = attributes.pop('text', self.default_text)
        texturePath = attributes.pop('texturePath', self.default_texturePath)
        iconWidth, iconHeight = iconSize
        padLeft, padTop, padRight, padBottom = padding
        super(ButtonCore, self).ApplyAttributes(attributes)
        Fill(bgParent=self, align=uiconst.TOALL, padding=(1, 1, 1, 1), color=color)
        GradientSprite(bgParent=self, align=uiconst.TOALL, rgbData=((0.0, (0.9, 0.9, 0.9)), (0.5, (0.2, 0.2, 0.2)), (1.0, (0.9, 0.9, 0.9))), alphaData=((0.0, 0.3), (1.0, 0.3)), rotation=-math.pi / 4)
        Fill(bgParent=self, align=uiconst.TOALL, color=color)
        if texturePath:
            iconCont = Container(parent=self, align=uiconst.TOPLEFT, padding=(padLeft,
             padTop,
             contentSpacing if text else padRight,
             padBottom), height=iconHeight, width=iconWidth)
            Sprite(parent=iconCont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath=texturePath, height=iconHeight, width=iconWidth)
        if text:
            if texturePath:
                left = padLeft + iconWidth
                labelPadding = (contentSpacing,
                 padTop,
                 padRight,
                 padBottom)
                top = labelTop
            else:
                left = 0
                labelPadding = padding
                top = 0
            labelCont = ContainerAutoSize(parent=self, align=uiconst.TOPLEFT, alignMode=uiconst.TOPLEFT, left=left, top=top)
            labelClass(parent=labelCont, align=uiconst.TOPLEFT, padding=labelPadding, text=text, color=labelColor)
            if labelShadow:
                shadow = labelClass(parent=labelCont, align=uiconst.TOPLEFT, padding=labelPadding, text=text, color=labelShadowColor)
                shadow.renderObject.spriteEffect = trinity.TR2_SFX_BLUR
                Frame(parent=labelCont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/radialShadow.png', cornerSize=8, color=labelShadowColor, opacity=labelShadowColor[3] * 0.5)
        self.SetSizeAutomatically()

    def OnClick(self, *args):
        if self.disabled:
            return
        self.disabled = True
        uthread.new(self._OnClickThread)

    def _OnClickThread(self):
        try:
            if callable(self.onClick):
                self.onClick()
        finally:
            self.disabled = False

    def AnimShow(self):
        self.Show()
        animations.FadeTo(self, duration=0.4)


class VgsBuyAurButton(ButtonCore):
    default_color = COLOR_AUR
    default_padding = (4, 4, 4, 4)
    default_hint = localization.GetByLabel('UI/VirtualGoodsStore/BuyAurOnline')
    default_iconSize = (20, 20)
    default_texturePath = 'res:/UI/Texture/Vgs/aur_symbol_20.png'


class VgsBuyButton(ButtonCore):
    default_color = COLOR_AUR
    default_padding = (14, 4, 14, 4)
    default_labelClass = VgsButtonLabelMedium


class BuyButtonAurCore(ButtonCore):
    default_color = COLOR_AUR
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenOfferWindow
        super(BuyButtonAurCore, self).ApplyAttributes(attributes)
        self.offers = None
        types = attributes.get('types', None)
        if types is not None:
            uthread.new(self.FindOffersAndReveal, types)

    def FindOffersAndReveal(self, types):
        try:
            if callable(types):
                types = types()
            if isinstance(types, numbers.Number):
                types = [types]
            store = sm.GetService('vgsService').GetStore()
            self.offers = store.SearchOffersByTypeIDs(types)
            if self.offers:
                self.AnimShow()
        except Exception as e:
            if len(e.args) >= 1 and e.args[0] == 'tokenMissing':
                log.LogInfo('Failed to search the NES for offers due to missing token')
            else:
                log.LogException('Failed to search the NES for offers')

    def OpenOfferWindow(self):
        from eve.client.script.ui.shared.vgs.offerWindow import OfferWindow
        OfferWindow.OpenWithOffers(self.offers)


class BuyButtonAur(BuyButtonAurCore):
    default_contentSpacing = 4
    default_padding = (4, 4, 5, 3)
    default_iconSize = (16, 16)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelTop = 1
    default_text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/BuyNow')
    default_texturePath = 'res:/UI/Texture/Vgs/aur_16.png'


class BuyButtonAurSmall(BuyButtonAurCore):
    default_contentSpacing = 3
    default_padding = (3, 2, 6, 1)
    default_iconSize = (12, 12)
    default_labelClass = EveHeaderSmall
    default_labelShadow = True
    default_labelTop = 0
    default_text = localization.GetByLabel('UI/Skins/BuyWithAur')
    default_texturePath = 'res:/UI/Texture/classes/skins/aur_12.png'


class BuyButtonIskCore(ButtonCore):
    default_color = COLOR_ISK

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenMarketWindow
        super(BuyButtonIskCore, self).ApplyAttributes(attributes)
        self.typeID = attributes.get('typeID', None)

    def OpenMarketWindow(self):
        sm.GetService('marketutils').ShowMarketDetails(self.typeID, None)


class BuyButtonIsk(BuyButtonIskCore):
    default_contentSpacing = 4
    default_padding = (4, 4, 5, 3)
    default_iconSize = (16, 16)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelTop = 1
    default_text = localization.GetByLabel('UI/SkillQueue/MultiTrainingOverlay/BuyNow')
    default_texturePath = 'res:/UI/Texture/Vgs/isk_16.png'


class BuyButtonIskSmall(BuyButtonIskCore):
    default_contentSpacing = 3
    default_padding = (3, 2, 6, 1)
    default_iconSize = (12, 12)
    default_labelClass = EveHeaderSmall
    default_labelShadow = True
    default_labelTop = 0
    default_text = localization.GetByLabel('UI/Skins/BuyWithIsk')
    default_texturePath = 'res:/UI/Texture/classes/skins/isk_12.png'


class BuyButtonPlex(ButtonCore):
    default_color = COLOR_PLEX
    default_padding = (8, 4, 8, 4)
    default_labelClass = EveHeaderMedium
    default_labelShadow = True
    default_labelShadowColor = (0.0, 0.0, 0.0, 0.4)
    default_labelTop = 1
    default_logContext = 'None'
    default_text = localization.GetByLabel('UI/VirtualGoodsStore/Buttons/BuyPlex')

    def ApplyAttributes(self, attributes):
        if attributes.get('onClick', None) is None:
            attributes.onClick = self.OpenAccountManagement
        super(BuyButtonPlex, self).ApplyAttributes(attributes)
        self.logContext = attributes.get('logContext', self.default_logContext)

    def OpenAccountManagement(self):
        sm.GetService('cmd').BuyPlexOnline()
        LogBuyPlexOnlineClicked(self.logContext)
