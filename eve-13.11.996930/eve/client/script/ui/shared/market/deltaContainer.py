#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\deltaContainer.py
from carbon.common.script.util.format import FmtAmt
from carbonui import const as uiconst
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel

class DeltaContainer(ButtonIcon):
    __guid__ = 'uicls.DeltaContainer'
    default_height = 24
    upArrow = 'res:/UI/Texture/classes/MultiSell/up.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/down.png'
    equalSprite = 'res:/UI/Texture/classes/MultiSell/equal.png'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        delta = attributes.delta
        self.deltaText = Label(parent=self, align=uiconst.CENTER, fontsize=9, top=2)
        self.UpdateDelta(delta)

    def ConstructIcon(self):
        self.icon = GlowSprite(name='icon', parent=self, align=uiconst.CENTERTOP, width=self.iconSize, height=self.iconSize, texturePath=self.texturePath, state=uiconst.UI_DISABLED, color=self.iconColor, rotation=self.rotation)

    def UpdateDelta(self, delta):
        deltaText = self.GetDeltaText(delta)
        if delta > 0:
            self.deltaText.text = deltaText
            self.deltaText.align = uiconst.CENTERBOTTOM
            self.icon.align = uiconst.CENTERTOP
            texturePath = self.upArrow
        elif delta < 0:
            self.deltaText.text = deltaText
            self.deltaText.align = uiconst.CENTERTOP
            self.icon.align = uiconst.CENTERBOTTOM
            texturePath = self.downArrow
        else:
            self.icon.align = uiconst.CENTER
            self.deltaText.text = ''
            texturePath = self.equalSprite
        self.icon.SetTexturePath(texturePath)

    def GetDeltaText(self, delta):
        if delta < 0:
            color = self.belowColor
        else:
            color = self.aboveColor
        if abs(delta) < 1.0:
            showFraction = 1
        else:
            showFraction = 0
        deltaText = '%s%s</color>' % (color, GetByLabel('UI/Common/Percentage', percentage=FmtAmt(delta * 100, showFraction=showFraction)))
        return deltaText


class BuyDeltaContainer(DeltaContainer):
    upArrow = 'res:/UI/Texture/classes/MultiSell/upBuy.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/downBuy.png'
    belowColor = '<color=0xff00ff00>'
    aboveColor = '<color=0xffff5050>'


class SellDeltaContainer(DeltaContainer):
    upArrow = 'res:/UI/Texture/classes/MultiSell/up.png'
    downArrow = 'res:/UI/Texture/classes/MultiSell/down.png'
    belowColor = '<color=0xffff5050>'
    aboveColor = '<color=0xff00ff00>'
