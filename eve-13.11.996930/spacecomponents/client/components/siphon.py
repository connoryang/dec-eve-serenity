#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\components\siphon.py
from dogma.attributes.format import GetFormatAndValue
import evetypes
__author__ = 'markus'
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.components.component import Component

class Siphon(Component):

    @staticmethod
    def GetAttributeInfo(godmaService, typeID, attributes, instance, localization):
        attributeEntries = [EntryData('Header', localization.GetByLabel('UI/Inflight/SpaceComponents/Siphon/SiphoningMaterials'))]
        materialNames = []
        for materialID in attributes.materials:
            materialNames.append((evetypes.GetName(materialID), materialID))

        for material in sorted(materialNames):
            attributeEntries.append(EntryData('LabelTextSides', material[0], '', evetypes.GetIconID(material[1]), material[1]))

        return attributeEntries
