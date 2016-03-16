#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\utilButtons\showInfoButton.py
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel

class ShowInfoButton(GlowSprite):
    default_texturePath = 'res:/ui/Texture/Icons/show_info20.png'
    default_width = 20
    default_height = 20

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.itemID = attributes.itemID
        self.hint = GetByLabel('UI/Commands/ShowInfo')

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(self.typeID, self.itemID)
