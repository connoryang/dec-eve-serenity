#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\skinSvc.py
import blue
import localization
from localization.formatters.timeIntervalFormatters import FormatTimeIntervalShortWritten, TIME_CATEGORY_DAY
import locks
from service import Service
import shipskins
import evetypes

class SkinService(Service):
    __guid__ = 'svc.skinSvc'
    __notifyevents__ = ['OnSkinLicenseActivated']

    def Run(self, memStream = None):
        Service.Run(self, memStream)
        sm.FavourMe(self.OnSkinLicenseActivated)
        self.static = shipskins.SkinStaticData(bootrole=boot.role, packaged=blue.pyos.packaged, resolvePathFunc=blue.paths.ResolvePath, region=boot.region)
        self._applySkinLock = locks.Lock()
        self.ResetCache()

    def ResetCache(self):
        self._licensedSkins = None
        self._licensedSkinsByType = {}

    def ActivateSkinLicense(self, itemID, typeID):
        sm.RemoteSvc('shipSkinMgr').ActivateSkinLicense(itemID)

    def GetAppliedSkinMaterialSetID(self, characterID, itemID, typeID = None):
        shipSkinMgr = sm.RemoteSvc('shipSkinMgr')
        return shipSkinMgr.GetAppliedSkinMaterialSetID(characterID, itemID, typeID)

    def GetSkins(self, typeID):
        licensedSkins = self.GetLicensedSkinsForType(typeID)
        skinsByMaterial = {}
        for licensedSkin in licensedSkins:
            skin = self._CreateSkinFromID(licensedSkin.skinID, licensed=True, expires=licensedSkin.expires)
            skinsByMaterial[skin.materialID] = skin

        for skin in self.static.GetSkinsForTypeID(typeID):
            material = self.static.materials[skin.skinMaterialID]
            if material.skinMaterialID not in skinsByMaterial:
                skinsByMaterial[material.skinMaterialID] = Skin(material)

        return skinsByMaterial.values()

    def GetLicensedSkins(self):
        if self._licensedSkins is None:
            shipSkinMgr = sm.RemoteSvc('shipSkinMgr')
            self._licensedSkins = shipSkinMgr.GetLicencedSkins()
        return self._licensedSkins

    def GetLicensedSkinsForType(self, typeID):
        if typeID not in self._licensedSkinsByType:
            shipSkinMgr = sm.RemoteSvc('shipSkinMgr')
            licensedSkins = shipSkinMgr.GetLicencedSkinsForType(typeID)
            self._licensedSkinsByType[typeID] = licensedSkins
        return self._licensedSkinsByType[typeID]

    def GetAppliedSkin(self, characterID, itemID, typeID = None):
        skin = sm.RemoteSvc('shipSkinMgr').GetAppliedSkin(characterID, itemID, typeID)
        if skin is None:
            return
        return self._CreateSkinFromID(skin.skinID, licensed=True, expires=skin.expires)

    def GetSkinByLicenseType(self, typeID):
        license = self.static.licenses[typeID]
        return self._CreateSkinFromID(license.skinID)

    def ApplySkin2(self, itemID, skin):
        self._nextSkin = skin
        with self._applySkinLock:
            if self._nextSkin != skin:
                return
            skinID = skin.skinID if skin is not None else None
            sm.RemoteSvc('shipSkinMgr').ApplySkin(itemID, skinID)
            blue.synchro.SleepWallclock(1000)

    def _CreateSkinFromID(self, skinID, licensed = False, expires = None):
        skin = self.static.skins[skinID]
        material = self.static.materials[skin.skinMaterialID]
        return Skin(material, skin=skin, licensed=licensed, expires=expires)

    def GetStaticLicenseByID(self, typeID):
        return StaticLicense(self.static, self.static.GetLicenseByID(typeID))

    def GetStaticSkinByID(self, skinID):
        return StaticSkin(self.static, self.static.GetSkinByID(skinID))

    def GetStaticMaterialByID(self, materialID):
        return StaticMaterial(self.static, self.static.GetMaterialByID(materialID))

    def FindOffersForTypes(self, typeIDs):
        try:
            store = sm.GetService('vgsService').GetStore()
            offers = store.SearchOffersByTypeIDs(typeIDs)
            return offers
        except Exception as e:
            if len(e.args) >= 1 and e.args[0] == 'tokenMissing':
                self.LogWarn('Failed to search the NES for offers due to missing token')
            else:
                self.LogException('Failed to search the NES for offers')
            return []

    def FindOffersForTypeWithMaterial(self, typeID, materialID):
        licenses = self.static.GetLicensesForTypeWithMaterial(typeID, materialID)
        licenseTypes = [ l.licenseTypeID for l in licenses ]
        return self.FindOffersForTypes(licenseTypes)

    def OnSkinLicenseActivated(self, skinID):
        self.ResetCache()


class StaticLicense(object):

    def __init__(self, static, license):
        self._static = static
        self._license = license

    @property
    def typeID(self):
        return self._license.licenseTypeID

    @property
    def name(self):
        return evetypes.GetName(self._license.licenseTypeID)

    @property
    def duration(self):
        return self._license.duration

    @property
    def durationLabel(self):
        if self.duration == -1:
            return localization.GetByLabel('UI/Skins/SkinDurationPermanent')
        else:
            return localization.GetByLabel('UI/Skins/SkinDurationLimited', days=self.duration)

    @property
    def is_permanent(self):
        return self._license.duration == -1

    @property
    def iconTexturePath(self):
        return skin_icon_texture_path(self.skin.materialID)

    @property
    def skin(self):
        if not getattr(self, '_cached_skin', None):
            self._cached_skin = self._static.GetSkinByID(self._license.skinID)
        return StaticSkin(self._static, self._cached_skin)

    @property
    def material(self):
        return self.skin.material


class StaticSkin(object):

    def __init__(self, static, skin):
        self._static = static
        self._skin = skin

    @property
    def skinID(self):
        return self._skin.skinID

    @property
    def materialID(self):
        return self._skin.skinMaterialID

    @property
    def material(self):
        if not getattr(self, '_cached_material', None):
            self._cached_material = self._static.GetMaterialByID(self._skin.skinMaterialID)
        return StaticMaterial(self._static, self._cached_material)

    @property
    def types(self):
        return self._skin.types

    @property
    def licenses(self):
        licenses = self._static.GetLicencesForSkinID(self._skin.skinID)
        return [ StaticLicense(self._static, license) for license in licenses ]


class StaticMaterial(object):

    def __init__(self, static, material):
        self._static = static
        self._material = material

    @property
    def iconTexturePath(self):
        return skin_icon_texture_path(self._material.skinMaterialID)

    @property
    def materialID(self):
        return self._material.skinMaterialID

    @property
    def name(self):
        messageID = int(self._material.displayNameID)
        return localization.GetByMessageID(messageID)

    @property
    def skins(self):
        skins = self._static.GetSkinsForMaterialID(self._material.skinMaterialID)
        return [ StaticSkin(self._static, skin) for skin in skins ]


class Skin(object):

    def __init__(self, material, skin = None, licensed = False, expires = None):
        self._skin = skin
        self._material = material
        self._materialSet = cfg.graphicMaterialSets.GetIfExists(self._material.materialSetID)
        self.licensed = licensed
        self.expires = expires

    @property
    def skinID(self):
        if self._skin:
            return self._skin.skinID
        else:
            return None

    @property
    def expired(self):
        return self.expires is not None and self.expires < blue.os.GetWallclockTime()

    @property
    def permanent(self):
        return self.expires is None

    def GetExpiresLabel(self):
        if not self.licensed:
            return
        if self.expires is None:
            return localization.GetByLabel('UI/Skins/PermanentLicense')
        duration = self.expires - blue.os.GetWallclockTime()
        if duration < 0:
            return localization.GetByLabel('UI/Skins/ExpiredLicense')
        expires = FormatTimeIntervalShortWritten(duration, showFrom=TIME_CATEGORY_DAY)
        return localization.GetByLabel('UI/Skins/LicenseExpiresIn', expires=expires)

    @property
    def materialSetID(self):
        return self._material.materialSetID

    @property
    def materialID(self):
        return self._material.skinMaterialID

    @property
    def name(self):
        messageID = int(self._material.displayNameID)
        return localization.GetByMessageID(messageID)

    @property
    def types(self):
        return self._skin.types

    @property
    def iconTexturePath(self):
        return skin_icon_texture_path(self._material.skinMaterialID)

    @property
    def colorPrimary(self):
        return getattr(self._materialSet, 'colorPrimary', None)

    @property
    def colorSecondary(self):
        return getattr(self._materialSet, 'colorSecondary', None)

    @property
    def colorHull(self):
        return getattr(self._materialSet, 'colorHull', None)

    @property
    def colorWindows(self):
        return getattr(self._materialSet, 'colorWindow', None)

    def __eq__(self, other):
        if other is None:
            return False
        if not hasattr(other, 'skinID'):
            return False
        if not hasattr(other, 'materialID'):
            return False
        if not hasattr(other, 'licensed'):
            return False
        if not hasattr(other, 'expires'):
            return False
        return self.skinID == other.skinID and self.materialID == other.materialID and self.licensed == other.licensed and self.expires == other.expires

    def __repr__(self):
        return "<%s material='%s' skinID=%s licensed=%s expires='%s'>" % (self.__class__.__name__,
         self.material,
         self.skinID,
         self.licensed,
         self.expires)


def skin_icon_texture_path(materialID):
    return 'res:/UI/Texture/classes/skins/icons/%s.png' % materialID
