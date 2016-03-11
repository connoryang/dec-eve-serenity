#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\utilButtons\marketDetailsButton.py
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel

class ShowMarketDetailsButton(GlowSprite):
    default_texturePath = 'res:/ui/Texture/Icons/show_in_market_20.png'
    default_width = 20
    default_height = 20

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.hint = GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails')

    def OnClick(self, *args):
        sm.StartService('marketutils').ShowMarketDetails(self.typeID, None)
