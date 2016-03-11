#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\client\display.py
import localization
from dogma.attributes.format import GetFormattedAttributeAndValue
COMPONENT_INFO_ORDER = ['deploy',
 'activate',
 'decay',
 'bountyEscrow',
 'scoop',
 'warpDisruption']
TIMER_ICON = '22_16'
CYCLE_TIME_ICON = '22_21'
RANGE_ICON = '22_15'
BANNED_ICON = '77_12'

def EntryData(entryClass, label, text = None, iconID = 0, typeID = None):
    return (entryClass, {'line': 1,
      'label': label,
      'text': text,
      'iconID': iconID,
      'typeID': typeID})


def DogmaEntryData(entryClass, attribute):
    return EntryData(entryClass, attribute.displayName, attribute.value, attribute.iconID)


def IterAttributeCollectionInInfoOrder(attributeCollection):
    for name in COMPONENT_INFO_ORDER:
        if name in attributeCollection:
            yield attributeCollection.pop(name)

    remainingLists = localization.util.Sort(attributeCollection.values(), key=lambda attrList: attrList[0][1]['label'])
    for attributeList in remainingLists:
        yield attributeList


def GetDogmaAttributeAndValue(godmaService, typeID, attributeID):
    value = godmaService.GetTypeAttribute2(typeID, attributeID)
    return GetFormattedAttributeAndValue(attributeID, value)
