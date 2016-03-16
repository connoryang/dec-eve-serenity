#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\devMenuFunctions.py
from eve.client.script.ui.util.uix import ListWnd, QtyPopup
from eve.devtools.script.slashError import Error

def GiveSkin(materialID, typeID):
    skin = _PickSkinForMaterialAndType(materialID, typeID)
    duration = _SelectSkinDuration()
    if duration is None:
        return
    sm.RemoteSvc('shipSkinMgr').GiveSkin(skin.skinID, duration=duration)


def GivePermanentSkin(materialID, typeID):
    skin = _PickSkinForMaterialAndType(materialID, typeID)
    sm.RemoteSvc('shipSkinMgr').GiveSkin(skin.skinID)


def _PickSkinForMaterialAndType(materialID, typeID):
    skins = _GetSkinsForTypeWithMaterial(materialID, typeID)
    if len(skins) == 0:
        message = 'No skins found for type {} that use material {}'.format(typeID, materialID)
        raise Error(message)
    else:
        if len(skins) == 1:
            return skins[0]
        return _SelectSkinFromList(skins)


def _GetSkinsForTypeWithMaterial(materialID, typeID):
    static = sm.GetService('skinSvc').static
    return static.GetSkinsForTypeWithMaterial(typeID, materialID)


def _SelectSkinFromList(skins):
    entry_list = [ (skin.internalName, skin) for skin in skins ]
    caption = 'AutoComplete: %d types found' % len(entry_list)
    selection = ListWnd(entry_list, listtype='generic', caption=caption)
    if len(selection) != 1:
        return None
    skin = selection[1]
    return skin


def _SelectSkinDuration():
    result = QtyPopup(minvalue=1, setvalue=1, caption='SKIN Duration', label='Set SKIN duration in days')
    if result is None:
        return
    return int(result['qty'])


def RemoveSkin(skinID):
    sm.RemoteSvc('shipSkinMgr').RemoveSkin(skinID)
