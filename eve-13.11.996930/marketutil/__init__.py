#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\marketutil\__init__.py


def GetTypeIDFromDragItem(node):
    try:
        typeID = node.typeID
        if typeID:
            return typeID
    except AttributeError:
        pass

    nodeGuid = getattr(node, '__guid__', None)
    if nodeGuid in INVENTORY_GUIDS:
        return node.item.typeID


INVENTORY_GUIDS = ('xtriui.InvItem', 'listentry.InvItem')
