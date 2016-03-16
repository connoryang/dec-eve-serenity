#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\controller.py
from itertoolsext import first
import locks
import uthread
import signals

class SkinPanelAdapter(object):

    def ApplySkin(self, controller, itemID, skin):
        uthread.new(self._ApplySkinThread, controller, itemID, skin)

    def _ApplySkinThread(self, controller, itemID, skin):
        try:
            sm.GetService('skinSvc').ApplySkin2(itemID, skin)
        except UserError as e:
            if e.msg != 'SkinAlreadyApplied':
                controller.OnApplySkinFailed(itemID, skin)
                raise
            skinID = skin.skinID if skin is not None else None
            controller.OnActiveShipSkinChange(itemID, skinID)
        except Exception:
            controller.OnApplySkinFailed(itemID, skin)
            raise

    def GetAppliedSkin(self, itemID, typeID = None):
        return sm.GetService('skinSvc').GetAppliedSkin(session.charid, itemID, typeID)

    def GetSkins(self, typeID):
        return sm.GetService('skinSvc').GetSkins(typeID)

    def GetTypesForSkin(self, skinID):
        skin = sm.GetService('skinSvc').static.GetSkinByID(skinID)
        return skin.types

    def RegisterNotify(self, controller):
        sm.RegisterNotify(controller)

    def UnregisterNotify(self, controller):
        sm.UnregisterNotify(controller)


class SkinPanelController(object):
    __notifyevents__ = ['OnSkinLicenseActivated']

    def __init__(self, typeID, adapter = None):
        self._adapter = adapter or SkinPanelAdapter()
        self._lock = locks.Lock()
        self.Reset(typeID)
        self.onChange = signals.Signal()
        self.onSkinsChange = signals.Signal()
        self.onSkinsChange.connect(self.onChange)
        self._adapter.RegisterNotify(self)

    def Close(self):
        self._adapter.UnregisterNotify(self)
        self.onSkinsChange.clear()
        self.onChange.clear()

    def Reset(self, typeID):
        self._typeID = typeID
        self._applied = None
        self._previewed = None
        self._pending = None
        self._skins = None

    @property
    def typeID(self):
        return self._typeID

    @typeID.setter
    def typeID(self, newTypeID):
        with self._lock:
            self.Reset(newTypeID)
            self.onSkinsChange()

    @property
    def applied(self):
        return self._applied

    @property
    def previewed(self):
        return self._previewed

    @property
    def pending(self):
        return self._pending

    @property
    def skins(self):
        if self._skins is None:
            self._skins = self._adapter.GetSkins(self._typeID)
        return self._skins

    def PickSkin(self, skin):
        with self._lock:
            currentID = self._previewed.materialID if self._previewed is not None else None
            pickedID = skin.materialID if skin is not None else None
            if currentID == pickedID:
                skin = None
            self._previewed = skin
            self.onChange()

    def OnSkinLicenseActivated(self, skinID):
        with self._lock:
            types = self._adapter.GetTypesForSkin(skinID)
            if self._typeID not in types:
                return
            self._skins = None
            self._UpdateActivatedSkin(skinID)
            self.onSkinsChange()

    def _UpdateActivatedSkin(self, skinID):
        if self._previewed is None:
            return
        try:
            skin = first(self.skins, lambda s: s.skinID == skinID)
            if skin.materialID == self._previewed.materialID:
                self._previewed = skin
        except StopIteration:
            pass


class SkinNotAvailableForType(Exception):
    pass


class FittingSkinPanelController(SkinPanelController):
    __notifyevents__ = SkinPanelController.__notifyevents__ + ['OnActiveShipSkinChange']

    def __init__(self, fitting, adapter = None):
        self._fitting = fitting
        super(FittingSkinPanelController, self).__init__(typeID=fitting.GetTypeID(), adapter=adapter)
        self._UpdateFittingMaterial()
        self.onChange.connect(self._UpdateFittingMaterial)
        self._fitting.on_new_itemID.connect(self.OnNewItemID)

    def Close(self):
        super(FittingSkinPanelController, self).Close()
        self._fitting.on_new_itemID.disconnect(self.OnNewItemID)

    @property
    def itemID(self):
        return self._itemID

    def Reset(self, typeID):
        super(FittingSkinPanelController, self).Reset(typeID)
        self._itemID = self._fitting.GetItemID()
        self._applied = self._adapter.GetAppliedSkin(self._itemID, typeID)

    def PickSkin(self, skin):
        itemID = self.itemID
        with self._lock:
            if skin is not None and skin not in self.skins:
                raise SkinNotAvailableForType('%s not found in %s' % (skin, self.skins))
            if skin is None:
                self._ResetPick(itemID)
            elif skin.licensed:
                self._PickLicensedSkin(skin, itemID)
            else:
                self._PickUnlicensedSkin(skin)

    def _ResetPick(self, itemID):
        if all((s is None for s in (self._applied, self._pending, self._previewed))):
            return
        self._applied = None
        self._pending = None
        self._previewed = None
        self._adapter.ApplySkin(self, itemID, None)
        self.onChange()

    def _PickLicensedSkin(self, skin, itemID):
        if self._applied == skin or self._pending == skin:
            skin = None
        self._pending = skin
        self._applied = None
        if skin is not None:
            self._previewed = None
        self._adapter.ApplySkin(self, itemID, skin)
        self.onChange()

    def _PickUnlicensedSkin(self, skin):
        if self._previewed == skin:
            self._previewed = None
        else:
            self._previewed = skin
        self.onChange()

    def OnActiveShipSkinChange(self, itemID, skinID):
        if itemID != self.itemID:
            return
        with self._lock:
            if skinID is None and self._applied is None:
                return
            if skinID is None:
                skin = None
            else:
                try:
                    skin = first(self.skins, lambda s: s.skinID == skinID)
                except StopIteration:
                    return

            if self._applied == skin:
                return
            if self._pending and self._pending.skinID == skin.skinID:
                self._pending = None
            self._applied = skin
            self.onChange()

    def OnNewItemID(self):
        self.typeID = self._fitting.GetTypeID()

    def OnApplySkinFailed(self, itemID, skin):
        if itemID != self.itemID:
            return
        with self._lock:
            if self._pending == skin:
                self._pending = None
                self._applied = self._adapter.GetAppliedSkin(itemID)
                self.onChange()

    def _UpdateActivatedSkin(self, skinID):
        if self._applied is not None and self._applied.skinID == skinID:
            self._applied = None
        if self._pending is not None and self._pending.skinID == skinID:
            self._pending = None
        if self._previewed is not None:
            try:
                skin = first(self.skins, lambda s: s.skinID == skinID)
                if self._previewed.materialID == skin.materialID:
                    self._previewed = None
            except StopIteration:
                pass

    def _UpdateFittingMaterial(self):
        if self._previewed:
            materialSetID = self._previewed.materialSetID
        elif self._pending:
            materialSetID = self._pending.materialSetID
        elif self._applied:
            materialSetID = self._applied.materialSetID
        else:
            materialSetID = None
        self._fitting.SetSkinMaterialSetID(materialSetID)
