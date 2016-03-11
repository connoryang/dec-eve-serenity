#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\utils.py
import dogma.attributes

def GetAttributeValuesByCategoryNames(dbdogma, attributeList):
    categories = dbdogma.AttributeCategories_Select().Index('categoryID')
    attributesByCategories = {}
    for attributeID, value in attributeList.iteritems():
        attribute = dogma.attributes.GetAttribute(attributeID)
        categoryName = categories[attribute.categoryID].categoryName
        if categoryName not in attributesByCategories:
            attributesByCategories[categoryName] = []
        attributesByCategories[categoryName].append((attributeID, attribute.attributeName, value))

    for category, attributes in attributesByCategories.iteritems():
        attributesByCategories[category] = sorted(attributes, key=lambda x: x[1])

    return attributesByCategories


def GetDisplayNamesForAttributeList(attributeList):
    attributeNames = []
    for attribute in attributeList:
        name = dogma.attributes.GetDisplayName(attribute)
        attributeNames.append(name)

    return attributeNames


def GetModifyingItemIDs(dogmaItem, attributeID):
    try:
        attrib = dogmaItem.attributes[attributeID]
    except KeyError:
        return []

    ret = []
    for operator, modifyingAttrib in attrib.GetIncomingModifiers():
        if modifyingAttrib.item is not None:
            ret.append(modifyingAttrib.item.itemID)

    return ret
