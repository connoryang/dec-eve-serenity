#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\views\purchaseView.py
import blue
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import CONTENT_ALIGN_CENTER, FlowContainer
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.uianimations import animations
import contextlib
from eve.client.script.ui.shared.vgs.button import VgsBuyButton
from eve.client.script.ui.shared.vgs.events import LogPurchaseAurum
from eve.client.script.ui.shared.vgs.label import AurPriceTagLarge, VgsLabelLarge, VgsLabelMedium, VgsLabelSmall
from eve.client.script.ui.shared.vgs.loading import VgsLoadingPanel
from eve.client.script.ui.shared.vgs.offer import Offer, OfferProductList
import localization
import logging
import uthread
log = logging.getLogger(__name__)
MINIMUM_PROGRESS_DISPLAY_TIME = 1.2 * const.SEC

class PurchaseView(Container):

    def ApplyAttributes(self, attributes):
        super(PurchaseView, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.onBuyOffer = attributes.onBuyOffer
        self.onCloseView = attributes.onCloseView
        self.panel = None
        uthread.new(self.Layout)

    def Layout(self):
        self.panelCont = Container(parent=self, align=uiconst.TOBOTTOM, height=220)
        Offer(parent=self, align=uiconst.TOALL, offer=self.controller.offer)
        panel = OfferDetailsPanel(controller=self.controller, onBuy=self.OnPurchase, opacity=1.0)
        self.DisplayPanel(panel)

    def DisplayPanel(self, panel):
        if self.panel:
            self.ClosePanel(self.panel)
        self.panel = panel
        panel.SetParent(self.panelCont, idx=-1)
        self.panel.AnimEntry()

    def ClosePanel(self, panel):

        def thread():
            panel.AnimExit()
            blue.synchro.SleepWallclock(panel.TRANSITION_TIME * 1000)
            panel.Close()

        uthread.new(thread)

    def OnPurchase(self):
        if self.controller.balance < self.controller.totalPrice:
            self.PurchaseAurum()
        else:
            self.onBuyOffer()
            self.PurchaseOffer()

    def PurchaseAurum(self):
        sm.GetService('audio').SendUIEvent('store_aur')
        aurBalance = sm.GetService('vgsService').GetStore().GetAccount().GetAurumBalance()
        LogPurchaseAurum(aurBalance, 'PurchaseView')
        sm.GetService('cmd').BuyAurumOnline()

    def PurchaseOffer(self):
        self.DisplayPanel(ProcessingPurchasePanel())
        try:
            with self._MinimumActionDelay(MINIMUM_PROGRESS_DISPLAY_TIME):
                self.controller.Buy()
        except Exception:
            log.exception('Failed to purchase offer')
            self.DisplayPanel(PurchaseFailedPanel())
            return

        if not self.controller.IsProductActivatable():
            self.DisplayPanel(PurchaseSuccessPanel())
        else:
            self.DisplayPanel(PurchaseSuccessPanel(subText=None))
            blue.synchro.SleepWallclock(2000)
            typeID = self.controller.activatableProductTypeID
            self.DisplayPanel(ActivatePromptPanel(typeID=typeID, onActivate=lambda : self.ActivateProduct(typeID), onCancel=self.onCloseView))

    @contextlib.contextmanager
    def _MinimumActionDelay(self, delay):
        startTime = blue.os.GetWallclockTime()
        try:
            yield
        finally:
            blue.pyos.synchro.SleepUntilWallclock(startTime + delay)

    def ActivateProduct(self, typeID):
        try:
            sm.GetService('redeem').RedeemAndActivateType(typeID)
        except Exception:
            log.exception('Failed to activate item')
            self.DisplayPanel(ActivationFailedPanel())
        else:
            self.DisplayPanel(ActivationSuccessfulPanel())


class BasePanel(Container):
    default_align = uiconst.TOALL
    default_opacity = 0.0
    TRANSITION_TIME = 0.5

    def AnimEntry(self):
        animations.FadeIn(self, duration=self.TRANSITION_TIME, timeOffset=self.TRANSITION_TIME)

    def AnimExit(self):
        animations.FadeOut(self, duration=self.TRANSITION_TIME)


class OfferDetailsPanel(BasePanel):

    def ApplyAttributes(self, attributes):
        super(OfferDetailsPanel, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.onBuy = attributes.onBuy
        self.Layout()
        self.controller.onAurBalanceChanged.connect(self.OnAurBalanceChanged)

    def Layout(self):
        offer = self.controller.offer
        bottomCont = Container(parent=self, align=uiconst.TOBOTTOM, height=50)
        AurPriceTagLarge(parent=bottomCont, align=uiconst.CENTERLEFT, left=10, amount=offer.price, baseAmount=offer.basePrice)
        if self.controller.balance < self.controller.totalPrice:
            text = localization.GetByLabel('UI/VirtualGoodsStore/BuyAurOnline')
        else:
            text = localization.GetByLabel('UI/VirtualGoodsStore/OfferDetailBuyNowButton')
        self.buyButton = VgsBuyButton(parent=bottomCont, align=uiconst.CENTERRIGHT, left=10, text=text, onClick=self.onBuy)
        scroll = ScrollContainer(parent=self, align=uiconst.TOALL, top=10)
        products = offer.productQuantities.values()
        OfferProductList(parent=scroll, align=uiconst.TOTOP, margin=(10, 0), products=products)

    def Reload(self):
        self.Flush()
        self.Layout()

    def OnAurBalanceChanged(self, newBalance):
        self.Reload()


class ProcessingPurchasePanel(BasePanel):

    def ApplyAttributes(self, attributes):
        super(ProcessingPurchasePanel, self).ApplyAttributes(attributes)
        VgsLoadingPanel(parent=self, align=uiconst.TOALL, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/Processing'))


class PurchaseSuccessPanel(BasePanel):
    ICON_FOREGROUND = 'res:/UI/Texture/vgs/purchase_success_fg.png'
    ICON_BACKGROUND = 'res:/UI/Texture/vgs/purchase_success_bg.png'
    AUDIO_EVENT = 'store_purchase_success'
    default_text = 'UI/VirtualGoodsStore/Purchase/Completed'
    default_subText = 'UI/VirtualGoodsStore/Purchase/NewPurchaseInstruction'

    def ApplyAttributes(self, attributes):
        super(PurchaseSuccessPanel, self).ApplyAttributes(attributes)
        text = attributes.pop('text', localization.GetByLabel(self.default_text))
        subText = attributes.pop('subText', localization.GetByLabel(self.default_subText) if self.default_subText is not None else None)
        mainCont = ContainerAutoSize(parent=self, align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=1)
        iconCont = Container(parent=mainCont, align=uiconst.TOTOP, height=72)
        self.iconForegroundTransform = Transform(parent=iconCont, align=uiconst.CENTERTOP, width=72, height=78, scalingCenter=(0.5, 0.5))
        self.iconForeground = Sprite(parent=self.iconForegroundTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.ICON_FOREGROUND, width=72, height=64, opacity=0)
        self.iconBackgroundTransform = Transform(parent=iconCont, align=uiconst.CENTERTOP, width=72, height=78, scalingCenter=(0.5, 0.5))
        self.iconBackground = Sprite(parent=self.iconBackgroundTransform, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.ICON_BACKGROUND, width=72, height=64, opacity=0)
        labelCont = ContainerAutoSize(parent=mainCont, align=uiconst.TOTOP, top=4)
        VgsLabelLarge(parent=labelCont, align=uiconst.CENTER, text=text)
        if subText:
            self.subTextCont = ContainerAutoSize(parent=mainCont, align=uiconst.TOTOP, top=12, opacity=0)
            VgsLabelSmall(parent=self.subTextCont, align=uiconst.CENTER, width=460, text='<center>%s</center>' % subText)

    def AnimEntry(self):
        super(PurchaseSuccessPanel, self).AnimEntry()
        sm.GetService('audio').SendUIEvent(self.AUDIO_EVENT)
        animations.FadeIn(self.iconBackground, duration=0.5, timeOffset=self.TRANSITION_TIME)
        animations.FadeIn(self.iconForeground, duration=0.5, timeOffset=self.TRANSITION_TIME + 0.5)
        animations.Tr2DScaleTo(self.iconBackgroundTransform, startScale=(2.0, 2.0), endScale=(1.0, 1.0), duration=0.25, timeOffset=self.TRANSITION_TIME)
        animations.Tr2DScaleTo(self.iconForegroundTransform, startScale=(2.0, 2.0), endScale=(1.0, 1.0), duration=0.25, timeOffset=self.TRANSITION_TIME + 0.5)
        if hasattr(self, 'subTextCont'):
            animations.FadeTo(self.subTextCont, timeOffset=2)


class PurchaseFailedPanel(PurchaseSuccessPanel):
    ICON_FOREGROUND = 'res:/UI/Texture/vgs/purchase_fail_fg.png'
    ICON_BACKGROUND = 'res:/UI/Texture/vgs/purchase_fail_bg.png'
    AUDIO_EVENT = 'store_purchase_failure'
    default_text = 'UI/VirtualGoodsStore/Purchase/Failed'
    default_subText = None


class ActivatePromptPanel(BasePanel):

    def ApplyAttributes(self, attributes):
        super(ActivatePromptPanel, self).ApplyAttributes(attributes)
        typeID = attributes.typeID
        onActivate = attributes.onActivate
        onCancel = attributes.onCancel
        VgsLabelMedium(parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/ActivationPurchaseSuccess'), center=True, top=10, padding=(10, 0, 10, 0))
        cont = ContainerAutoSize(parent=self, align=uiconst.TOTOP)
        OfferProductList(parent=cont, align=uiconst.CENTER, products=[(typeID, 1)])
        VgsLabelMedium(parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/ActivationQuestion'), center=True, top=10, padding=(10, 0, 10, 0))
        VgsLabelSmall(parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/ActivationQuestionDetails'), center=True, padding=(10, 0, 10, 0))
        buttonCont = FlowContainer(parent=self, align=uiconst.TOBOTTOM, contentAlignment=CONTENT_ALIGN_CENTER, padding=(0, 10, 0, 10), contentSpacing=(10, 10), idx=0)
        VgsBuyButton(parent=buttonCont, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/DontActivate'), onClick=onCancel, color=(0.5, 0.5, 0.5, 1.0))
        VgsBuyButton(parent=buttonCont, align=uiconst.NOALIGN, text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/Activate'), onClick=onActivate, color=(0.255, 0.4, 0.545, 1.0))


class ActivationSuccessfulPanel(PurchaseSuccessPanel):
    default_text = 'UI/VirtualGoodsStore/Purchase/ActivationSuccessful'
    default_subText = None


class ActivationFailedPanel(PurchaseFailedPanel):
    default_text = 'UI/VirtualGoodsStore/Purchase/ActivationFailed'
    default_subText = None
