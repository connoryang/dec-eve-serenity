#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\PanelSkinMaterial.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_RIGHT
from eve.client.script.ui.control.entries import GetFromClass, Header, Item
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.skins.buyButton import SkinMaterialBuyButtonAur, SkinMaterialBuyButtonIsk
from itertools import chain
import evetypes
import localization

class PanelSkinMaterial(Container):
    LOG_CONTEXT = 'MaterialInfoWindow'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.material = sm.GetService('skinSvc').GetStaticMaterialByID(attributes.itemID)
        self.Layout()

    def Layout(self):
        self.scroll = Scroll(name='scroll', parent=self, padding=4)

    def Load(self):
        entries = []
        entry = GetFromClass(Header, data={'label': localization.GetByLabel('UI/Skins/AppliesToTheseShips')})
        entries.append(entry)
        skinSvc = sm.GetService('skinSvc')
        skins = skinSvc.static.GetSkinsForMaterialID(self.material.materialID)
        types = set([ t for t in chain.from_iterable((skin.types for skin in skins)) ])
        typeEntries = []
        for typeID in types:
            entry = GetFromClass(ShipSkinMaterialEntry, data={'typeID': typeID,
             'itemID': self.material.materialID,
             'label': evetypes.GetName(typeID),
             'getIcon': True,
             'logContext': self.LOG_CONTEXT})
            typeEntries.append(entry)

        entries.extend(sorted(typeEntries, key=lambda x: x.label))
        self.scroll.Load(contentList=entries)


class ShipSkinMaterialEntry(Item):

    def Load(self, node):
        Item.Load(self, node)
        buttonCont = FlowContainer(parent=self, align=uiconst.CENTERRIGHT, left=20, width=200, height=16, contentAlignment=CONTENT_ALIGN_RIGHT, contentSpacing=(4, 0))
        SkinMaterialBuyButtonAur(parent=buttonCont, align=uiconst.NOALIGN, typeID=self.typeID, materialID=self.itemID, logContext=node.logContext)
        SkinMaterialBuyButtonIsk(parent=buttonCont, align=uiconst.NOALIGN, typeID=self.typeID, materialID=self.itemID, logContext=node.logContext)

    def ShowInfo(self, *args):
        typeID = self.typeID
        itemID = None
        sm.StartService('info').ShowInfo(typeID, itemID=itemID)
