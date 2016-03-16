#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\vgs\offer.py
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.shared.vgs.label import VgsLabelSmall, VgsHeaderLarge, VgsHeaderMedium, AurPriceTag
from eve.client.script.ui.view.aurumstore.vgsUiPrimitives import LazyUrlSprite
from eve.client.script.ui.util.uix import GetTechLevelIcon
import evetypes
from inventorycommon.const import categoryBlueprint
import localization
from utillib import KeyVal

class Ribbon(ContainerAutoSize):
    default_name = 'Ribbon'
    default_state = uiconst.UI_DISABLED
    default_align = uiconst.TOPLEFT
    default_left = 8
    FONT_CLASS = VgsHeaderMedium
    FONT_BOLD = True
    PADDING = (10, 2, 10, 2)

    def ApplyAttributes(self, attributes):
        super(Ribbon, self).ApplyAttributes(attributes)
        Sprite(bgParent=self, texturePath=attributes.label.url)
        self.FONT_CLASS(parent=self, align=uiconst.TOPLEFT, text=attributes.label.description, bold=self.FONT_BOLD, uppercase=True, padding=self.PADDING)


class Offer(Container):
    default_clipChildren = True
    default_showDescription = True
    default_showPrice = False
    default_showImage = True
    BACKGROUND_COLOR = (0.349, 0.439, 0.529, 1.0)
    RADIAL_SHADOW = (0.196, 0.208, 0.224)
    TEXT_BOX_COLOR = (0.133, 0.141, 0.149, 0.5)
    PADDING_BIG = 10
    TITLE_FONT_CLASS = VgsHeaderLarge
    DESCRIPTION_FONT_CLASS = VgsLabelSmall
    RIBBON_TYPE = Ribbon
    RIBBON_ALIGN = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        super(Offer, self).ApplyAttributes(attributes)
        self.offer = attributes.offer
        self.description = attributes.get('showDescription', self.default_showDescription)
        self.price = attributes.get('showPrice', self.default_showPrice)
        self.image = attributes.get('showImage', self.default_showImage)
        self.onClick = attributes.get('onClick', None)
        self.Layout()

    def Layout(self):
        self.imageLayer = Transform(parent=self, align=uiconst.CENTER, scalingCenter=(0.5, 0.5), bgColor=self.BACKGROUND_COLOR)
        GradientSprite(align=uiconst.TOALL, bgParent=self.imageLayer, rgbData=((1.0, self.RADIAL_SHADOW),), alphaData=((0.0, 0.0), (1.0, 1.0)), radial=True, idx=0)
        if self.image:
            self.lazySprite = LazyUrlSprite(parent=self.imageLayer, align=uiconst.TOALL, imageUrl=self.offer.imageUrl, state=uiconst.UI_DISABLED)
        descriptionBox = ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, bgColor=self.TEXT_BOX_COLOR, clipChildren=True, idx=0)
        if self.price:
            AurPriceTag(parent=descriptionBox, align=uiconst.TOBOTTOM, amount=self.offer.price, baseAmount=self.offer.basePrice, padding=(self.PADDING_BIG,
             0,
             self.PADDING_BIG,
             10))
        if self.description:
            self.DESCRIPTION_FONT_CLASS(parent=descriptionBox, align=uiconst.TOBOTTOM, text=self.offer.description, padding=(self.PADDING_BIG,
             0,
             self.PADDING_BIG,
             10))
        self.TITLE_FONT_CLASS(parent=descriptionBox, align=uiconst.TOBOTTOM, text=self.offer.name, padding=(self.PADDING_BIG,
         2,
         self.PADDING_BIG + 32,
         2))
        if self.offer.label is not None:
            self.RIBBON_TYPE(parent=self, align=self.RIBBON_ALIGN, label=self.offer.label, idx=0)

    def OnClick(self, *args):
        if callable(self.onClick):
            self.onClick()

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        size = max(self.displayWidth, self.displayHeight)
        self.imageLayer.width = size
        self.imageLayer.height = size
        return super(Offer, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly=updateChildrenOnly)


class OfferProductList(LayoutGrid):
    default_columns = 2
    default_cellSpacing = (0, 8)

    def ApplyAttributes(self, attributes):
        super(OfferProductList, self).ApplyAttributes(attributes)
        self.iconSize = attributes.get('iconSize', None)
        products = attributes.get('products', [])
        for typeID, quantity in products:
            self.AddProduct(typeID, quantity=quantity)

    def AddProduct(self, typeID, quantity = 1):
        self.AddRow(rowClass=OfferProductRow, typeID=typeID, quantity=quantity, iconSize=self.iconSize)


class OfferProductRow(LayoutGridRow):
    default_columns = 2
    default_iconSize = 64
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(OfferProductRow, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.quantity = attributes.get('quantity', 1)
        self.iconSize = attributes.get('iconSize', None) or self.default_iconSize
        self.Layout()

    def Layout(self):
        self.AddCell(cellObject=self._PrepareProductIcon())
        self.AddCell(cellObject=self._PrepareProductLabel())

    def _PrepareProductIcon(self):
        icon = Container(name='productIcon', align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.iconSize, height=self.iconSize)
        techIcon = GetTechLevelIcon(typeID=self.typeID)
        if techIcon:
            techIcon.SetParent(icon)
        Icon(parent=icon, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, size=self.iconSize, typeID=self.typeID, isCopy=True)
        return icon

    def _PrepareProductLabel(self):
        labelCont = LayoutGrid(align=uiconst.CENTERLEFT, columns=2)
        VgsLabelSmall(parent=labelCont, padding=(8, 0, 4, 0), text=localization.GetByLabel('UI/Contracts/ContractsWindow/TypeNameWithQuantity', typeID=self.typeID, quantity=self.quantity))
        InfoIcon(parent=labelCont, align=uiconst.CENTERLEFT, typeID=self.typeID, abstractinfo=self._GetAbstractInfo())
        return labelCont

    def GetMenu(self):
        abstractInfo = self._GetAbstractInfo()
        return sm.GetService('menu').GetMenuFormItemIDTypeID(None, self.typeID, ignoreMarketDetails=False, abstractInfo=abstractInfo)

    def _GetAbstractInfo(self):
        if evetypes.GetCategoryID(self.typeID) != categoryBlueprint:
            return None
        bpSvc = sm.GetService('blueprintSvc')
        bpData = bpSvc.GetBlueprintTypeCopy(self.typeID, original=False)
        return KeyVal(bpData=bpData)
