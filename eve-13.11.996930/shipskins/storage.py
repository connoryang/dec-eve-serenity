#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\shipskins\storage.py


class LicensedSkin(object):

    def __init__(self, skinID, expires = None):
        self._skinID = skinID
        self._expires = expires

    def __repr__(self):
        return "<LicensedSkin %s expires='%s' >" % (self._skinID, self._expires)

    @property
    def skinID(self):
        return self._skinID

    @property
    def expires(self):
        return self._expires

    def lastsLongerThan(self, other):
        if other is None:
            return True
        if other.expires is None:
            return False
        return self.expires is None or other.expires < self.expires


class Cache(dict):

    def __init__(self, get_func):
        super(Cache, self).__init__()
        self.get_func = get_func

    def __missing__(self, key):
        result = self[key] = self.get_func(key)
        return result


class LicensedSkinStorage(object):

    def __init__(self, clock):
        self.clock = clock
        self.skins_by_charid = Cache(self._get_licensed_skins_map)

    def is_skin_licensed(self, characterID, skinID):
        if skinID is None:
            return True
        self._check_skin_expiry(characterID, skinID)
        return skinID in self.skins_by_charid[characterID]

    def is_skin_permanently_licensed(self, characterID, skinID):
        if not self.is_skin_licensed(characterID, skinID):
            return False
        skin = self.get_licensed_skin(characterID, skinID)
        return skin.expires is None

    def add_licensed_skin(self, characterID, skinID, duration):
        self._check_skin_expiry(characterID, skinID)
        skin = self.skins_by_charid[characterID].get(skinID, None)
        if skin is not None and skin.expires is None:
            raise SkinAlreadyLicensed()
        if skin is None:
            new_skin = self._add_licensed_skin(characterID, skinID, duration)
        else:
            new_skin = self._update_licensed_skin(characterID, skinID, duration)
        self.skins_by_charid[characterID][skinID] = new_skin

    def get_licensed_skins(self, characterID):
        skins = self.skins_by_charid[characterID].values()
        for skin in skins:
            self._check_skin_expiry(characterID, skin.skinID)

        return self.skins_by_charid[characterID].values()

    def get_licensed_skin(self, characterID, skinID):
        try:
            self._check_skin_expiry(characterID, skinID)
            return self.skins_by_charid[characterID][skinID]
        except KeyError:
            raise SkinNotLicensed()

    def remove_licensed_skin(self, characterID, skinID):
        skins = self.skins_by_charid[characterID]
        if skinID not in skins:
            raise KeyError()
        self._remove_licensed_skin(characterID, skinID)
        del self.skins_by_charid[characterID][skinID]

    def prime(self, characterID):
        return self.skins_by_charid[characterID]

    def unprime(self, characterID):
        if characterID in self.skins_by_charid:
            del self.skins_by_charid[characterID]

    def _check_skin_expiry(self, characterID, skinID):
        skins = self.skins_by_charid[characterID]
        if skinID not in skins:
            return
        skin = skins[skinID]
        if skin.expires is not None and skin.expires < self.clock():
            self._remove_licensed_skin(characterID, skinID)
            del self.skins_by_charid[characterID]

    def _get_licensed_skins_map(self, characterID):
        skins = self._get_licensed_skins(characterID)
        return {skin.skinID:skin for skin in skins}

    def _add_licensed_skin(self, characterID, skinID, duration):
        raise NotImplementedError()

    def _update_licensed_skin(self, characterID, skinID, duration):
        raise NotImplementedError()

    def _get_licensed_skins(self, characterID):
        raise NotImplementedError()

    def _remove_licensed_skin(self, characterID, skinID):
        raise NotImplementedError()


class AppliedSkinStorage(object):

    def __init__(self, licensed_skin_storage):
        self.licensed_skins = licensed_skin_storage
        self.applied_skins = Cache(self._get_applied_skins)

    def apply_skin(self, characterID, skinID, itemID):
        if not self.licensed_skins.is_skin_licensed(characterID, skinID):
            raise SkinNotLicensed()
        if skinID is None:
            self.clear_applied_skin(characterID, itemID)
        else:
            self._insert_or_update(characterID, skinID, itemID)

    def clear_applied_skin(self, characterID, itemID):
        if itemID in self.applied_skins[characterID]:
            self._remove_applied_skin(characterID, itemID)
            del self.applied_skins[characterID][itemID]

    def get_applied_skin_id(self, characterID, itemID):
        if itemID not in self.applied_skins[characterID]:
            return
        skinID = self.applied_skins[characterID][itemID]
        if not self.licensed_skins.is_skin_licensed(characterID, skinID):
            self._remove_applied_skin(characterID, itemID)
            skinID = None
        return skinID

    def _insert_or_update(self, characterID, skinID, itemID):
        if itemID in self.applied_skins[characterID]:
            self._update_applied_skin(characterID, skinID, itemID)
        else:
            self._insert_applied_skin(characterID, skinID, itemID)
        self.applied_skins[characterID][itemID] = skinID

    def _get_applied_skins(self, characterID):
        raise NotImplementedError()

    def _insert_applied_skin(self, characterID, skinID, itemID):
        raise NotImplementedError()

    def _update_applied_skin(self, characterID, skinID, itemID):
        raise NotImplementedError()

    def _remove_applied_skin(self, characterID, itemID):
        raise NotImplementedError()


class SkinNotLicensed(Exception):
    pass


class SkinAlreadyLicensed(Exception):
    pass
