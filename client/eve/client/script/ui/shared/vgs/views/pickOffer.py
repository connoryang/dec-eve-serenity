#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\views\pickOffer.py
from carbonui import const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from eve.client.script.ui.shared.vgs.label import VgsHeaderLarge, VgsHeaderMedium, VgsLabelSmall
from eve.client.script.ui.shared.vgs.offer import Offer, OfferProductList
import localization

class PickOfferView(Container):
    PADDING = 10

    def ApplyAttributes(self, attributes):
        super(PickOfferView, self).ApplyAttributes(attributes)
        self.offers = attributes.offers
        self.onPick = attributes.get('onPick', None)
        self.Layout()

    def Layout(self):
        scroll = ScrollContainer(parent=self, align=uiconst.TOALL, pushContent=False)
        VgsHeaderLarge(parent=scroll, align=uiconst.TOTOP, padding=(self.PADDING,
         self.PADDING,
         self.PADDING,
         0), text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/ChooseOffer'))
        VgsLabelSmall(parent=scroll, align=uiconst.TOTOP, padding=(self.PADDING,
         0,
         self.PADDING,
         self.PADDING), text=localization.GetByLabel('UI/VirtualGoodsStore/Purchase/ChooseOfferSubtext'))
        sortedOffers = self._SortOffers(self.offers)
        for offer in sortedOffers:
            OfferEntry(parent=scroll, align=uiconst.TOTOP, padding=(self.PADDING,
             0,
             self.PADDING,
             self.PADDING), offer=offer, onClick=lambda offer = offer: self.PickOffer(offer))

    def _SortOffers(self, offers):

        def sortKey(offer):
            return (offer.label is not None, offer.price, offer.name)

        return sorted(offers, key=sortKey, reverse=True)

    def PickOffer(self, offer):
        if callable(self.onPick):
            self.onPick(offer)


class OfferEntryImage(Offer):
    default_showDescription = False
    default_showPrice = True
    default_showImage = True
    TITLE_FONT_CLASS = VgsHeaderMedium
    RIBBON_ALIGN = uiconst.TOPRIGHT


class OfferEntry(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    BACKGROUND_COLOR = (0.1, 0.1, 0.1, 1.0)
    PADDING = 8

    def ApplyAttributes(self, attributes):
        super(OfferEntry, self).ApplyAttributes(attributes)
        self.offer = attributes.offer
        self.onClick = attributes.onClick
        Fill(bgParent=self, color=self.BACKGROUND_COLOR)
        self.bannerOffer = OfferEntryImage(parent=self, align=uiconst.TOTOP, height=160, padBottom=self.PADDING, offer=self.offer)
        products = list(self.offer.productQuantities.itervalues())
        OfferProductList(parent=self, align=uiconst.TOTOP, padding=(self.PADDING,
         0,
         self.PADDING,
         self.PADDING), iconSize=32, products=products)

    def OnMouseEnter(self, *args):
        animations.Tr2DScaleTo(self.bannerOffer.imageLayer, startScale=self.bannerOffer.imageLayer.scale, endScale=(1.04, 1.04), duration=0.05)

    def OnMouseExit(self, *args):
        animations.Tr2DScaleTo(self.bannerOffer.imageLayer, self.bannerOffer.imageLayer.scale, endScale=(1.0, 1.0), duration=0.2)

    def OnClick(self, *args):
        self.onClick()
