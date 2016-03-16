#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipskins\static.py
import fsdlite
from itertools import chain
import os
from shipskins.util import Base

class License(Base):
    __metaclass__ = fsdlite.Immutable
    MAPPING = []
    INDEXES = ['skinID.(?P<skinID>[0-9]+)$']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.licenseTypeID = None
        obj.skinID = None
        obj.duration = None
        return obj


License.MAPPING.append(('$', License))

def LicenseStorage():
    return fsdlite.EveStorage(data='skins/licenses', cache='skinLicenses.static', mapping=License.MAPPING, indexes=License.INDEXES)


class Skin(Base):
    __metaclass__ = fsdlite.Immutable
    MAPPING = []
    INDEXES = ['skinMaterialID.(?P<skinMaterialID>[0-9]+)',
     'types.(?P<typeID>[0-9]+)$',
     'allowCCPDevs.(?P<CCP>True|False)$',
     'visibleSerenity.(?P<SERENITY>True|False)$',
     'visibleTranquility.(?P<TRANQUILITY>True|False)$']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.skinID = None
        obj.skinMaterialID = None
        obj.types = []
        obj.internalName = None
        obj.visibleTranquility = False
        obj.visibleSerenity = False
        obj.allowCCPDevs = False
        return obj


Skin.MAPPING.append(('$', Skin))

def SkinStorage():
    return fsdlite.EveStorage(data='skins/skins', cache='skins.static', mapping=Skin.MAPPING, indexes=Skin.INDEXES)


class SkinMaterial(Base):
    __metaclass__ = fsdlite.Immutable
    MAPPING = []
    INDEXES = ['skinMaterialID.(?P<skinMaterialID>[0-9]+)']

    def __new__(cls, *args, **kwargs):
        obj = Base.__new__(cls)
        obj.skinMaterialID = None
        obj.materialSetID = None
        obj.displayNameID = None
        return obj


SkinMaterial.MAPPING.append(('$', SkinMaterial))

def SkinMaterialStorage():
    return fsdlite.EveStorage(data='skins/materials', cache='skinMaterials.static', mapping=SkinMaterial.MAPPING)


class SkinStaticData(object):

    def __init__(self, bootrole = 'client', packaged = False, resolvePathFunc = None, region = None):
        self._bootrole = bootrole
        self._packaged = packaged
        self._ResolvePath = resolvePathFunc
        self._region = region
        self.licenses = self._LoadLicenceStorage()
        self.skins = self._LoadSkinStorage()
        self.materials = self._LoadSkinMaterialStorage()

    def GetSkinByID(self, skinID):
        return self.skins.Get(skinID)

    def GetMaterialByID(self, materialID):
        return self.materials.Get(materialID)

    def GetMaterialBySkinId(self, skinID):
        skin = self.skins.Get(skinID)
        return self.materials.Get(skin.skinMaterialID)

    def GetLicenseByID(self, licenseID):
        return self.licenses.Get(licenseID)

    def GetSkinsForTypeID(self, typeID):
        skins_by_type = self.skins.filter('typeID', typeID)
        return self._FilterSkinsByRegion(skins_by_type)

    def GetLicensesForTypeID(self, typeID):
        skins = self.GetSkinsForTypeID(typeID)
        skinIDs = (skin.skinID for skin in skins)
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def GetLicenseIDsForTypeID(self, typeID):
        licenses = self.GetLicensesForTypeID(typeID)
        return [ l.licenseTypeID for l in licenses ]

    def GetSkinsForTypeWithMaterial(self, typeID, materialID):
        skins = self.GetSkinsForMaterialID(materialID)
        skins = self._FilterSkinsByRegion(skins)
        return filter(lambda s: typeID in s.types, skins)

    def GetLicensesForTypeWithMaterial(self, typeID, materialID):
        skins = self.GetSkinsForTypeWithMaterial(typeID, materialID)
        skinIDs = (s.skinID for s in skins)
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def GetSkinsForMaterialID(self, materialID):
        skins = self.skins.filter('skinMaterialID', materialID)
        return self._FilterSkinsByRegion(skins)

    def GetLicencesForSkinID(self, skinID):
        return self.licenses.filter('skinID', skinID)

    def GetSkinsForCcp(self):
        skins = self.skins.filter('CCP', True)
        return self._FilterSkinsByRegion(skins)

    def GetAllSkins(self):
        return self._FilterSkinsByRegion(self.skins.values())

    def GetAllLicenses(self):
        skinIDs = (s.skinID for s in self.GetAllSkins())
        return list(chain.from_iterable(map(self.GetLicencesForSkinID, skinIDs)))

    def IsLicenseUsable(self, licenseID):
        license = self.GetLicenseByID(licenseID)
        skin = self.GetSkinByID(license.skinID)
        if self._region == 'optic':
            return skin.visibleSerenity
        else:
            return skin.visibleTranquility

    def _FilterSkinsByRegion(self, skins):
        if self._region == 'optic':
            return self._FilterSerenitySkins(skins)
        else:
            return self._FilterTranquilitySkins(skins)

    def _FilterSerenitySkins(self, skins):
        return filter(lambda s: s.visibleSerenity, skins)

    def _FilterTranquilitySkins(self, skins):
        return filter(lambda s: s.visibleTranquility, skins)

    def _LoadLicenceStorage(self):
        return self._CreateStaticDataStorage(License, 'skins/licenses', 'skinLicenses.static')

    def _LoadSkinStorage(self):
        return self._CreateStaticDataStorage(Skin, 'skins/skins', 'skins.static')

    def _LoadSkinMaterialStorage(self):
        return self._CreateStaticDataStorage(SkinMaterial, 'skins/materials', 'skinMaterials.static')

    def _CreateStaticDataStorage(self, klass, data, cache):
        storage = fsdlite.EveStorage(data, cache, mapping=klass.MAPPING, indexes=klass.INDEXES)
        storage.prime()
        return storage
