#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\components\fitting.py
from carbon.common.script.util.format import FmtDist
from spacecomponents.client.display import EntryData, RANGE_ICON
from spacecomponents.common.components.component import Component
from carbonui.control.menuLabel import MenuLabel

class Fitting(Component):

    def __init__(self, *args):
        Component.__init__(self, *args)
        self.fittingRange = self.attributes.range

    @staticmethod
    def GetAttributeInfo(godmaService, typeID, attributes, instance, localization):
        attributeEntries = [EntryData('Header', localization.GetByLabel('UI/Inflight/SpaceComponents/Fitting/InfoAttributesHeader')), EntryData('LabelTextSides', localization.GetByLabel('UI/Inflight/SpaceComponents/Fitting/DistanceLabel'), FmtDist(attributes.range), iconID=RANGE_ICON)]
        return attributeEntries


def GetFittingMenu(openFittingWindowCallback):
    return [[MenuLabel('UI/Fitting/UseFittingService'), openFittingWindowCallback, ()]]
