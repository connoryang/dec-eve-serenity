#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\info\panels\panelSkinLicense.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries import GetFromClass, Header, Item, LabelTextSides
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.skins.uiutil import GetMaterialDragData
import evetypes
from inventorycommon.const import typeSkinMaterial
import localization

class PanelSkinLicense(Container):

    def ApplyAttributes(self, attributes):
        super(PanelSkinLicense, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.Layout()

    def Layout(self):
        self.scroll = Scroll(parent=self, padding=4)

    def Load(self):
        entries = []
        license = sm.GetService('skinSvc').GetStaticLicenseByID(self.typeID)
        entry = GetFromClass(LabelTextSides, data={'label': localization.GetByLabel('UI/Skins/Duration'),
         'text': license.durationLabel,
         'icon': 'res:/ui/texture/icons/22_32_16.png'})
        entries.append(entry)
        entry = GetFromClass(SkinMaterialEntry, data={'label': localization.GetByLabel('UI/Skins/Material'),
         'text': license.material.name,
         'icon': license.iconTexturePath,
         'skin': license.skin})
        entries.append(entry)
        entry = GetFromClass(Header, data={'label': localization.GetByLabel('UI/Skins/AppliesToTheseShips')})
        entries.append(entry)
        tempList = []
        for typeID in license.skin.types:
            entry = GetFromClass(Item, data={'typeID': typeID,
             'itemID': None,
             'label': evetypes.GetName(typeID),
             'getIcon': True})
            tempList.append(entry)

        entries.extend(sorted(tempList, key=lambda x: x.label))
        self.scroll.Load(contentList=entries)


class SkinMaterialEntry(LabelTextSides):
    isDragObject = True

    def Load(self, node):
        node.typeID = typeSkinMaterial
        super(SkinMaterialEntry, self).Load(node)

    def ShowInfo(self, *args):
        materialID = self.sr.node.skin.materialID
        sm.StartService('info').ShowInfo(typeSkinMaterial, itemID=materialID)

    def GetDragData(self):
        return GetMaterialDragData(self.sr.node.skin.material)
