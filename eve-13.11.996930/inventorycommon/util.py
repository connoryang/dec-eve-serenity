#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\util.py
from carbon.common.lib.const import minPlayerOwner, minFakeItem
from eve.common.lib.appConst import mapWormholeSystemMin, mapWormholeSystemMax, minPlayerItem
from eve.common.lib.appConst import mapWormholeConstellationMin, mapWormholeConstellationMax
from eve.common.lib.appConst import mapWormholeRegionMin, mapWormholeRegionMax
import evetypes
from inventorycommon.const import typePlasticWrap
from inventorycommon.const import categoryShip
from inventorycommon.const import typeBHMegaCargoShip
from inventorycommon.const import shipPackagedVolumesPerGroup
from inventorycommon.const import containerPackagedVolumesPerType
import dogma.const as dgmconst
from itertoolsext import Bundle
import inventorycommon.const as invconst

def IsNPC(ownerID):
    return ownerID < minPlayerOwner and ownerID > 10000


def IsWormholeSystem(itemID):
    return mapWormholeSystemMin <= itemID < mapWormholeSystemMax


def IsWormholeConstellation(constellationID):
    return mapWormholeConstellationMin <= constellationID < mapWormholeConstellationMax


def IsWormholeRegion(regionID):
    return mapWormholeRegionMin <= regionID < mapWormholeRegionMax


def GetItemVolume(item, qty = None):
    if item.typeID == typePlasticWrap and item.singleton:
        volume = -item.quantity / 100.0
        if volume <= 0:
            raise RuntimeError('Volume of a plastic wrap should never be zero or less')
    elif item.categoryID == categoryShip and not item.singleton and item.groupID in shipPackagedVolumesPerGroup and item.typeID != typeBHMegaCargoShip:
        volume = shipPackagedVolumesPerGroup[item.groupID]
    elif item.typeID in containerPackagedVolumesPerType and not item.singleton:
        volume = containerPackagedVolumesPerType[item.typeID]
    else:
        volume = evetypes.GetVolume(item.typeID)
    if volume != -1:
        if qty is None:
            qty = item.stacksize
        if qty < 0:
            qty = 1
        volume *= qty
    return volume


def GetTypeVolume(typeID, qty = -1):
    if typeID == typePlasticWrap:
        raise RuntimeError('GetTypeVolume: cannot determine volume of plastic from type alone')
    item = Bundle(typeID=typeID, groupID=evetypes.GetGroupID(typeID), categoryID=evetypes.GetCategoryID(typeID), quantity=qty, singleton=-qty if qty < 0 else 0, stacksize=qty if qty >= 0 else 1)
    return GetItemVolume(item)


def IsSubSystemFlag(flagID):
    return invconst.flagSubSystemSlot0 <= flagID <= invconst.flagSubSystemSlot7


def IsModularShip(typeID):
    return evetypes.GetGroupID(typeID) == invconst.groupStrategicCruiser


def IsShipFittingFlag(flag):
    return flag >= invconst.flagSlotFirst and flag <= invconst.flagSlotLast or flag >= invconst.flagRigSlot0 and flag <= invconst.flagRigSlot7 or flag >= invconst.flagSubSystemSlot0 and flag <= invconst.flagSubSystemSlot7 or flag == invconst.flagHiddenModifers


def IsPlayerItem(itemID):
    return minPlayerItem <= itemID < minFakeItem
