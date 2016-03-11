#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\utilButtons\showInMapButton.py
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap

class ShowInMapButton(GlowSprite):
    default_texturePath = 'res:/ui/Texture/Icons/show_in_map_20.png'
    default_width = 20
    default_height = 20

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.itemID = attributes.itemID
        self.hint = GetByLabel('UI/Commands/ShowLocationOnMap')

    def OnClick(self, *args):
        OpenMap(interestID=self.itemID)
