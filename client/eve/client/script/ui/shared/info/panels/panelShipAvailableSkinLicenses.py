#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\panelShipAvailableSkinLicenses.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries import Item
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.entries import GetFromClass
from eve.client.script.ui.control.listgroup import ListGroup
import evetypes

class PanelShipAvailableSkinLicenses(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.Layout()

    def Layout(self):
        self.scroll = Scroll(name='scroll', parent=self, padding=4)

    def Load(self):
        entries = []
        skins = sm.GetService('skinSvc').GetSkins(self.typeID)
        for skin in skins:
            static = sm.GetService('skinSvc').static
            licenses = static.GetLicensesForTypeWithMaterial(self.typeID, skin.materialID)
            entry = GetFromClass(ListGroup, data={'id': ('skinLicenses', skin.skinID),
             'label': skin.name,
             'showicon': skin.iconTexturePath,
             'GetSubContent': GetSubContent,
             'groupItems': licenses,
             'BlockOpenWindow': True,
             'state': 'locked'})
            entries.append(entry)

        self.scroll.Load(contentList=sorted(entries, key=lambda x: x.label))


def GetSubContent(nodedata, *args):
    entries = []
    for license in nodedata.groupItems:
        entry = GetFromClass(Item, data={'typeID': license.licenseTypeID,
         'itemID': None,
         'label': evetypes.GetName(license.licenseTypeID),
         'sublevel': 1,
         'getIcon': True})
        entries.append(entry)

    return sorted(entries, key=lambda x: x.label)
