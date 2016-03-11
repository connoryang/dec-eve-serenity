#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\offerWindow.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveWindow import Window
from eve.client.script.ui.shared.vgs.controllers.offerPurchase import OfferPurchaseController
from eve.client.script.ui.shared.vgs.aurBalance import AurBalance
from eve.client.script.ui.shared.vgs.events import LogOpenOffer, LogPurchaseAurum
from eve.client.script.ui.shared.vgs.label import VgsLabelLarge
from eve.client.script.ui.shared.vgs.loading import VgsLoadingPanel
from eve.client.script.ui.shared.vgs.views.pickOffer import PickOfferView
from eve.client.script.ui.shared.vgs.views.purchaseView import PurchaseView
from eve.client.script.ui.util.uiComponents import Component, ButtonEffect
import localization

class OfferWindow(Window):
    default_width = 512
    default_height = 710
    default_windowID = 'offerWindow'
    default_captionLabelPath = 'UI/VirtualGoodsStore/OfferWindowCaption'
    default_iconNum = 'res:/UI/Texture/WindowIcons/NES.png'
    default_isCollapseable = False
    default_isStackable = False
    default_topParentHeight = 0

    @classmethod
    def OpenWithOffers(cls, offers):
        cls.CloseIfOpen()
        return cls.Open(offers=offers, useDefaultPos=True)

    def ApplyAttributes(self, attributes):
        super(OfferWindow, self).ApplyAttributes(attributes)
        self.view = None
        self.Layout()
        self.SetOffers(attributes.offers)

    def Layout(self):
        self.HideHeader()
        self.MakeUnResizeable()
        self.header = OfferWindowHeader(parent=self.GetMainArea(), align=uiconst.TOTOP, onExit=self.CloseByUser, onBack=self.DisplayPickOfferView)
        self.viewCont = Container(parent=self.GetMainArea(), align=uiconst.TOTOP, height=660)

    def SetOffers(self, offers):
        self.offers = offers
        if self.offers is None:
            self.DisplayLoadingView()
        elif len(self.offers) == 0:
            self.DisplayNoOffersFoundView()
        elif len(self.offers) == 1:
            self.DisplayPurchaseView(self.offers[0])
        else:
            self.DisplayPickOfferView()

    def DisplayLoadingView(self):
        self.header.DisableBackButton()
        view = VgsLoadingPanel(align=uiconst.TOALL, text=localization.GetByLabel('UI/VirtualGoodsStore/SearchingForOffers'))
        self.DisplayView(view)

    def DisplayNoOffersFoundView(self):
        self.DisplayErrorMessage('UI/VirtualGoodsStore/NoOffersFound')

    def DisplayErrorMessage(self, message):
        self.DisplayView(ErrorMessageView(message=message))

    def DisplayPickOfferView(self):
        self.header.DisableBackButton()
        view = PickOfferView(align=uiconst.TOALL, offers=self.offers, onPick=self.PickOffer)
        self.DisplayView(view)

    def DisplayPurchaseView(self, offer):
        store = sm.GetService('vgsService').GetStore()
        controller = OfferPurchaseController(offer, store)
        view = PurchaseView(controller=controller, onBuyOffer=self.BuyOffer, onCloseView=self.CloseIfOpen)
        self.DisplayView(view)
        LogOpenOffer(offer.id)

    def DisplayView(self, view):
        if self.destroyed:
            return
        if self.view:
            self.AnimCloseView(self.view)
        self.view = view
        self.view.SetParent(self.viewCont, idx=-1)
        self.AnimOpenView(self.view)

    def AnimCloseView(self, view):
        animations.FadeOut(view, duration=0.5, callback=view.Close)

    def AnimOpenView(self, view):
        animations.FadeTo(view, startVal=0.0, endVal=1.0, duration=0.5)

    def PickOffer(self, offer):
        self.header.EnableBackButton()
        self.DisplayPurchaseView(offer)

    def BuyOffer(self):
        self.header.DisableBackButton()

    def Prepare_HeaderButtons_(self):
        pass

    def Prepare_Background_(self):
        self.sr.underlay = OfferWindowUnderlay(parent=self)


class OfferWindowHeader(Container):
    default_height = 50

    def ApplyAttributes(self, attributes):
        super(OfferWindowHeader, self).ApplyAttributes(attributes)
        Fill(bgParent=self, color=(0.08, 0.08, 0.08, 1.0))
        Sprite(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=171, height=40, padLeft=10, texturePath='res:/UI/Texture/Vgs/storeLogoOfferWindow.png')
        exit = HeaderButton(parent=self, align=uiconst.TOPRIGHT, left=8, top=8, texturePath='res:/UI/Texture/Vgs/exit.png', hint=localization.GetByLabel('UI/Common/Buttons/Close'), onClick=attributes.onExit)
        self.backButton = HeaderButton(parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_DISABLED, left=8, top=exit.top + exit.height + 2, texturePath='res:/UI/Texture/Vgs/back.png', hint=localization.GetByLabel('UI/VirtualGoodsStore/BackToPickOffer'), onClick=attributes.onBack, opacity=0.0)
        AurBalance(parent=self, align=uiconst.TOPRIGHT, left=8 + exit.width + 16, top=12, account=sm.GetService('vgsService').GetStore().GetAccount(), onClick=self.OnBuyAurumClicked)

    def EnableBackButton(self):
        self.backButton.disabled = False
        self.backButton.state = uiconst.UI_NORMAL
        animations.FadeIn(self.backButton)

    def DisableBackButton(self):
        self.backButton.disabled = True
        self.backButton.state = uiconst.UI_DISABLED
        animations.FadeOut(self.backButton)

    def OnBuyAurumClicked(self):
        sm.GetService('audio').SendUIEvent('store_aur')
        aurBalance = sm.GetService('vgsService').GetStore().GetAccount().GetAurumBalance()
        LogPurchaseAurum(aurBalance, 'OfferWindowHeader')
        sm.GetService('cmd').BuyAurumOnline()


@Component(ButtonEffect())

class HeaderButton(Container):
    default_width = 16
    default_height = 16
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onClick = attributes.onClick
        Sprite(parent=self, texturePath=attributes.texturePath, width=self.width, height=self.height, align=uiconst.CENTER, state=uiconst.UI_DISABLED, color=(0.8, 0.8, 0.8, 1.0))

    def OnClick(self):
        if not self.disabled:
            self.onClick()


class OfferWindowUnderlay(Container):
    default_name = 'underlay'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        super(OfferWindowUnderlay, self).ApplyAttributes(attributes)
        self.Layout()

    def Layout(self):
        self.backFill = Fill(bgParent=self, color=(0.133, 0.141, 0.149, 0.98))
        self.frame = Fill(bgParent=self, color=(0.4, 0.4, 0.4, 0.8), padding=(-10, -10, -10, -10))

    def AnimEntry(self):
        pass

    def AnimExit(self):
        pass

    def Pin(self):
        pass

    def UnPin(self):
        pass


class ErrorMessageView(Container):

    def ApplyAttributes(self, attributes):
        super(ErrorMessageView, self).ApplyAttributes(attributes)
        message = attributes.message
        VgsLabelLarge(parent=self, align=uiconst.CENTER, width=460, text='<center>%s</center>' % localization.GetByLabel(message))
