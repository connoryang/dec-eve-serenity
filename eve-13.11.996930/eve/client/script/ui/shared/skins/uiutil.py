#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\uiutil.py
from inventorycommon.const import typeSkinMaterial
from utillib import KeyVal

def GetMaterialDragData(material):
    data = KeyVal({'typeID': typeSkinMaterial,
     'materialID': material.materialID,
     'label': material.name,
     'texturePath': material.iconTexturePath})
    return [data]
