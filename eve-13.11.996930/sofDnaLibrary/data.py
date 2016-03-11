#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sofDnaLibrary\data.py
from evetypes.storages import TypeStorage
from shipskins.static import SkinStorage, SkinMaterialStorage
import fsdSchemas.binaryLoader as fsdBinaryLoader
_skins = None
_materials = None
_materialSets = None
_typeIDs = None
_graphicIDs = None

def GetSkins():
    global _skins
    if _skins is None:
        _skins = SkinStorage()
    return _skins


def GetMaterialSets():
    global _materialSets
    if _materialSets is None:
        _materialSets = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/graphicMaterialSets.static')
    return _materialSets


def GetMaterials():
    global _materials
    if _materials is None:
        materials = SkinMaterialStorage()
        materialSets = GetMaterialSets()
        _materials = {}
        for materialID, material in materials.iteritems():
            _materials[int(material.skinMaterialID)] = materialSets[int(material.materialSetID)]

    return _materials


def GetTypes():
    global _typeIDs
    if _typeIDs is None:
        _typeIDs = TypeStorage()
    return _typeIDs


def GetGraphicIDs():
    global _graphicIDs
    if _graphicIDs is None:
        _graphicIDs = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/graphicIDs.static')
    return _graphicIDs
