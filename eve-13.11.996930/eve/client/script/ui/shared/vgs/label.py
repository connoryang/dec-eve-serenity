#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\label.py
from carbon.common.script.util.format import FmtAmt
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveFontConst as fontConst
from eve.client.script.ui.control.eveLabel import Label
from eve.common.lib.appConst import Plex2AurExchangeRatio
from eve.common.script.util.eveFormat import RoundISK
from inventorycommon.const import typePilotLicence
import localization
import inventorycommon.typeHelpers
FONTSIZE_LARGE = 28
FONTSIZE_MEDIUM = 18
FONTSIZE_SMALL = 12
FONT_COLOR_WHITE = (1.0, 1.0, 1.0, 0.75)
FONT_COLOR_DISCOUNT = (0.627, 0.145, 0.094, 1.0)

class VgsLabel(Label):
    default_center = False

    def ApplyAttributes(self, attributes):
        self.center = attributes.get('center', self.default_center)
        super(VgsLabel, self).ApplyAttributes(attributes)

    def GetText(self):
        return super(VgsLabel, self).GetText()

    def SetText(self, text):
        if self.center:
            text = '<center>%s</center>' % text
        super(VgsLabel, self).SetText(text)

    text = property(GetText, SetText)


class VgsLabelLarge(VgsLabel):
    default_name = 'VgsLabelLarge'
    default_fontsize = FONTSIZE_LARGE
    BASELINE = 0


class VgsLabelMedium(VgsLabel):
    default_name = 'VgsLabelMedium'
    default_fontsize = FONTSIZE_MEDIUM
    BASELINE = 0


class VgsLabelSmall(VgsLabel):
    default_name = 'VgsLabelSmall'
    default_fontsize = FONTSIZE_SMALL
    BASELINE = 4


class VgsHeaderLarge(VgsLabel):
    default_name = 'VgsHeaderLarge'
    default_fontsize = FONTSIZE_LARGE
    default_fontStyle = fontConst.STYLE_HEADER
    BASELINE = 8


class VgsHeaderMedium(VgsLabel):
    default_name = 'VgsHeaderMedium'
    default_fontsize = FONTSIZE_MEDIUM
    default_fontStyle = fontConst.STYLE_HEADER
    BASELINE = 5


class VgsHeaderSmall(VgsLabel):
    default_name = 'VgsHeaderSmall'
    default_fontsize = FONTSIZE_SMALL
    default_fontStyle = fontConst.STYLE_HEADER
    BASELINE = 4


class VgsButtonLabelMedium(VgsLabel):
    default_name = 'VgsButtonLabelMedium'
    default_fontsize = FONTSIZE_MEDIUM
    default_fontStyle = fontConst.STYLE_HEADER
    default_uppercase = True
    BASELINE = 5


class AurPriceTag(ContainerAutoSize):
    default_alignMode = uiconst.TOLEFT
    AUR_SYMBOL_SIZE = 16
    AUR_FONT_CLASS = VgsHeaderMedium
    ISK_FONT_CLASS = VgsLabelSmall
    ISK_FONT_COLOR = (0.5, 0.5, 0.5, 1.0)
    WORD_PADDING = 8

    def ApplyAttributes(self, attributes):
        super(AurPriceTag, self).ApplyAttributes(attributes)
        self.height = self.AUR_FONT_CLASS.default_fontsize
        amount = attributes.amount
        baseAmount = attributes.get('baseAmount', None)
        cont = Container(parent=self, align=uiconst.TOLEFT, padRight=4, width=self.AUR_SYMBOL_SIZE)
        Sprite(parent=cont, align=uiconst.BOTTOMLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Vgs/aur_symbol_32.png', height=self.AUR_SYMBOL_SIZE, width=self.AUR_SYMBOL_SIZE, color=FONT_COLOR_WHITE)
        self.AddAurAmount(amount)
        if baseAmount is not None and baseAmount > amount:
            self.AddAurAmount(baseAmount, color=FONT_COLOR_DISCOUNT, strikeThrough=True)
        iskWorth = self._CalculateEstimatedIskWorth(amount)
        if iskWorth is not None:
            self.AddEstimatedIskPrice(iskWorth)

    def AddAurAmount(self, amount, color = None, strikeThrough = False):
        self.AddLabel(FmtAmt(amount), font=self.AUR_FONT_CLASS, color=color, strikeThrough=strikeThrough)

    def AddEstimatedIskPrice(self, amount):
        label = localization.GetByLabel('UI/VirtualGoodsStore/EstimatedIskPrice', amount=amount)
        self.AddLabel(label, font=self.ISK_FONT_CLASS, color=self.ISK_FONT_COLOR)

    def AddLabel(self, text, font, color = None, strikeThrough = False):
        color = color or FONT_COLOR_WHITE
        cont = Container(parent=self, align=uiconst.TOLEFT, padRight=self.WORD_PADDING)
        if strikeThrough:
            Sprite(parent=cont, align=uiconst.TOALL, texturePath='res:/UI/Texture/Vgs/strikethrough.png', color=color, state=uiconst.UI_DISABLED)
        label = font(parent=cont, align=uiconst.BOTTOMLEFT, top=-font.BASELINE, text=text, color=color)
        cont.width = label.textwidth

    def _CalculateEstimatedIskWorth(self, aurAmount):
        try:
            plexPrice = inventorycommon.typeHelpers.GetAveragePrice(typePilotLicence)
        except KeyError:
            plexPrice = None

        if plexPrice is None:
            return
        iskPerAur = plexPrice / Plex2AurExchangeRatio
        return RoundISK(aurAmount * iskPerAur)


class AurPriceTagLarge(AurPriceTag):
    AUR_SYMBOL_SIZE = 18
    AUR_FONT_CLASS = VgsHeaderLarge
    ISK_FONT_CLASS = VgsLabelSmall
