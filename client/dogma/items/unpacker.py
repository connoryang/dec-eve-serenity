#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\unpacker.py
from dogma.const import attributeShieldCharge, attributeCharge

def UnpackItems(packData, charID, shipID):
    ship = None
    shipData = None
    shipValuesByAttributeID = None
    char = None
    charData = None
    for dogmaItem, itemData in packData:
        if dogmaItem.itemID == shipID:
            ship = dogmaItem
            shipData = itemData
            shipValuesByAttributeID = dict(itemData.attributeValues)
        elif dogmaItem.itemID == charID:
            char = dogmaItem
            charData = itemData
        else:
            dogmaItem.UnpackPropagationData(itemData, charID, shipID)

    char.UnpackPropagationData(charData, charID, shipID)
    ship.UnpackPropagationData(shipData, charID, shipID)
    _RebaseChargeAttributes(ship, shipValuesByAttributeID)


def _RebaseChargeAttributes(ship, shipValuesByAttributeID):
    if ship is not None:
        for attributeID in (attributeShieldCharge, attributeCharge):
            if attributeID in shipValuesByAttributeID:
                ship.attributes[attributeID].SetBaseValue(shipValuesByAttributeID.get(attributeID, 0.0))
