#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\skins\test\test_controller.py
import contextlib
import mock
import unittest
from fsdlite import Signal

class MockSkin(object):

    def __init__(self, materialID, skinID = None, licensed = False):
        self.materialID = materialID
        self.skinID = skinID
        self.licensed = licensed

    @property
    def material(self):
        return str(self.materialID)

    def __eq__(self, other):
        if other is None:
            return False
        return self.materialID == other.materialID and self.skinID == other.skinID and self.licensed == other.licensed

    def __repr__(self):
        return '<MockSkin materialID=%s skinID=%s licensed=%s>' % (self.materialID, self.skinID, self.licensed)


class MockFittingController(object):

    def __init__(self, itemID, typeID):
        self.itemID = itemID
        self.typeID = typeID
        self.on_new_itemID = Signal()
        self.material = None

    def GetItemID(self):
        return self.itemID

    def GetTypeID(self):
        return self.typeID

    def UpdateItem(self, itemID, typeID):
        self.itemID = itemID
        self.typeID = typeID
        self.on_new_itemID()

    def SetSkinMaterial(self, material):
        self.material = material


class MockLock(object):

    def __init__(self, lock):
        self._lock = lock

    def __enter__(self):
        self._lock.acquire()

    def __exit__(self, ex_type, ex_value, traceback):
        self._lock.release()
        return ex_type is None

    @property
    def acquire(self):
        return self._lock.acquire

    @property
    def release(self):
        return self._lock.release


TYPE_ID = 1
OTHER_TYPE_ID = 2
SKIN_ID = 10
SKIN = MockSkin(materialID=1)
OTHER_SKIN = MockSkin(materialID=2)
LICENSED_SKIN = MockSkin(materialID=1, skinID=20, licensed=True)
OTHER_LICENSED_SKIN = MockSkin(materialID=2, skinID=30, licensed=True)
UNLICENSED_SKIN = MockSkin(materialID=3, licensed=False)
OTHER_UNLICENSED_SKIN = MockSkin(materialID=4, licensed=False)
ITEM_ID = 100
OTHER_ITEM_ID = 200

class SkinPanelControllerBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.locks_module = mock.Mock()
        mock_modules = {'uthread': mock.Mock(),
         'locks': cls.locks_module}
        cls.import_patcher = mock.patch.dict('sys.modules', mock_modules)
        cls.import_patcher.start()
        from eve.client.script.ui.shared.skins import controller
        cls.module = controller

    @classmethod
    def tearDownClass(cls):
        cls.import_patcher.stop()

    def setUp(self):
        self.lock = MockLock(mock.MagicMock())
        self.locks_module.Lock.return_value = self.lock

    def prime_skins_cache(self, cached = None, fresh = None):
        cached = cached or []
        fresh = fresh or []
        self.adapter.GetSkins.return_value = cached
        self.controller.skins
        self.adapter.GetSkins.return_value = fresh

    def assertSkinState(self, applied = None, pending = None, previewed = None):
        if applied is None:
            self.assertIsNone(self.controller.applied)
        else:
            self.assertEqual(self.controller.applied, applied)
        if pending is None:
            self.assertIsNone(self.controller.pending)
        else:
            self.assertEqual(self.controller.pending, pending)
        if previewed is None:
            self.assertIsNone(self.controller.previewed)
        else:
            self.assertEqual(self.controller.previewed, previewed)

    @contextlib.contextmanager
    def assertLockedTransaction(self):
        self.lock.acquire.reset_mock()
        self.lock.release.reset_mock()
        try:
            yield
        finally:
            self.lock.acquire.assert_called_once_with()
            self.lock.release.assert_called_once_with()

    @contextlib.contextmanager
    def assertNotLockedTransaction(self):
        self.lock.acquire.reset_mock()
        self.lock.release.reset_mock()
        try:
            yield
        finally:
            self.assertFalse(self.lock.acquire.called)
            self.assertFalse(self.lock.release.called)


class TestSkinPanelController(SkinPanelControllerBase):
    SKIN_LIST = [SKIN, OTHER_SKIN]

    def setUp(self):
        super(TestSkinPanelController, self).setUp()
        self.adapter = mock.Mock(spec=self.module.SkinPanelAdapter)
        self.adapter.GetSkins.return_value = self.SKIN_LIST
        self.adapter.GetTypesForSkin.return_value = [TYPE_ID]
        self.controller = self.module.SkinPanelController(adapter=self.adapter, typeID=TYPE_ID)
        self.events = mock.Mock()
        self.controller.onChange.connect(self.events.onChange)
        self.controller.onSkinsChange.connect(self.events.onSkinsChange)

    def test_initial_state(self):
        self.assertEqual(self.controller.typeID, TYPE_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_change_type(self):
        with self.assertLockedTransaction():
            self.controller.typeID = OTHER_TYPE_ID
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertEqual(self.controller.typeID, OTHER_TYPE_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_skin(self):
        with self.assertLockedTransaction():
            self.controller.PickSkin(SKIN)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(previewed=SKIN)

    def test_change_type_resets_picked_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_same_skin_again(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(SKIN)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_none_skin_after_another_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(None)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_another_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.PickSkin(OTHER_SKIN)
        self.assertSkinState(previewed=OTHER_SKIN)

    def test_change_type_with_picked_skin(self):
        self.controller.PickSkin(SKIN)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertEqual(self.controller.typeID, OTHER_TYPE_ID)
        self.assertSkinState(previewed=None)

    def test_get_skins(self):
        self.adapter.GetSkins.return_value = self.SKIN_LIST
        skins = self.controller.skins
        self.assertItemsEqual(skins, self.SKIN_LIST)

    def test_skins_are_cached(self):
        self.prime_skins_cache(cached=self.SKIN_LIST)
        with self.assertNotLockedTransaction():
            skins = self.controller.skins
        self.assertItemsEqual(skins, self.SKIN_LIST)

    def test_changing_type_resets_skins_cache(self):
        self.prime_skins_cache(fresh=self.SKIN_LIST)
        self.controller.typeID = OTHER_TYPE_ID
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    def test_controller_registers_for_events(self):
        self.assertIn('OnSkinLicenseActivated', self.controller.__notifyevents__)
        self.adapter.RegisterNotify.assert_called_once_with(self.controller)

    def test_skin_license_activated_event(self):
        with self.assertLockedTransaction():
            self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()

    def test_skins_cache_is_reset_on_license_activated_for_relevant_type(self):
        self.prime_skins_cache(fresh=self.SKIN_LIST)
        self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    def test_skins_cache_is_not_reset_on_license_activated_for_irrelevant_type(self):
        self.adapter.GetTypesForSkin.return_value = [OTHER_TYPE_ID]
        self.prime_skins_cache(cached=self.SKIN_LIST)
        self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.assertItemsEqual(self.controller.skins, self.SKIN_LIST)

    def test_license_activated_does_not_change_preview_state(self):
        self.controller.PickSkin(SKIN)
        self.adapter.GetSkins.return_value = [LICENSED_SKIN]
        self.events.onChange.reset_mock()
        self.controller.OnSkinLicenseActivated(LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(previewed=LICENSED_SKIN)


class TestFittingSkinPanelController(SkinPanelControllerBase):
    SKIN_LIST = [LICENSED_SKIN,
     OTHER_LICENSED_SKIN,
     UNLICENSED_SKIN,
     OTHER_UNLICENSED_SKIN]

    def setUp(self):
        super(TestFittingSkinPanelController, self).setUp()
        self.adapter = mock.Mock(spec=self.module.SkinPanelAdapter)
        self.adapter.GetSkins.return_value = self.SKIN_LIST
        self.adapter.GetAppliedSkin.return_value = None
        self.adapter.GetTypesForSkin.return_value = [TYPE_ID]
        self.fitting = MockFittingController(ITEM_ID, TYPE_ID)
        self.controller = self.module.FittingSkinPanelController(fitting=self.fitting, adapter=self.adapter)
        self.events = mock.Mock()
        self.controller.onChange.connect(self.events.onChange)
        self.controller.onSkinsChange.connect(self.events.onSkinsChange)

    def apply_skin(self, skin, itemID = None):
        itemID = itemID or self.fitting.itemID
        self.controller.PickSkin(skin)
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, skin.skinID)
        self.events.onChange.reset_mock()
        self.adapter.ApplySkin.reset_mock()

    def test_initial_state(self):
        self.assertEqual(self.controller.typeID, TYPE_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_pick_none_with_nothing_picked(self):
        with self.assertLockedTransaction():
            self.controller.PickSkin(None)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(applied=None, previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_pick_unlicensed_skin(self):
        with self.assertLockedTransaction():
            self.controller.PickSkin(UNLICENSED_SKIN)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(previewed=UNLICENSED_SKIN)
        self.assertEqual(self.fitting.material, UNLICENSED_SKIN.material)

    def test_pick_licensed_skin(self):
        with self.assertLockedTransaction():
            self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, LICENSED_SKIN)
        self.assertSkinState(pending=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_pick_none_with_previewed_and_pending_skins(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.reset_mock()
        self.events.onChange.reset_mock()
        self.controller.PickSkin(None)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, None)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_unpicking_applied_skin_does_not_reset_previewed_skin(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, None)
        self.assertSkinState(previewed=UNLICENSED_SKIN)
        self.assertEqual(self.fitting.material, UNLICENSED_SKIN.material)

    def test_picked_skins_must_be_actually_available(self):
        self.adapter.GetSkins.return_value = []
        with self.assertRaises(self.module.SkinNotAvailableForType):
            self.controller.PickSkin(LICENSED_SKIN)

    def test_pick_two_different_unlicensed_skins(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(OTHER_UNLICENSED_SKIN)
        self.assertSkinState(previewed=OTHER_UNLICENSED_SKIN)
        self.assertEqual(self.fitting.material, OTHER_UNLICENSED_SKIN.material)

    def test_pick_licensed_skin_after_an_unlicensed_skin(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(LICENSED_SKIN)
        self.assertSkinState(pending=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_pick_two_different_licensed_skins(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.controller.PickSkin(OTHER_LICENSED_SKIN)
        self.assertSkinState(pending=OTHER_LICENSED_SKIN)
        self.assertEqual(self.fitting.material, OTHER_LICENSED_SKIN.material)

    def test_pick_same_licensed_skin_again(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.reset_mock()
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, None)
        self.assertSkinState(pending=None)
        self.assertIsNone(self.fitting.material)

    def test_pick_same_unlicensed_skin_again(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.assertSkinState(previewed=None)
        self.assertIsNone(self.fitting.material)

    def test_pick_applied_skin_again(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, None)
        self.assertSkinState(applied=None)
        self.assertIsNone(self.fitting.material)

    def test_pick_none_skin_after_unlicensed_skin(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.controller.PickSkin(None)
        self.assertSkinState(previewed=None)
        self.assertIsNone(self.fitting.material)

    def test_pick_none_skin_after_licensed_skin(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.controller.PickSkin(None)
        self.assertSkinState(pending=None)
        self.assertIsNone(self.fitting.material)

    def test_controller_registers_for_events(self):
        self.assertIn('OnActiveShipSkinChange', self.controller.__notifyevents__)
        self.adapter.RegisterNotify.assert_called_once_with(self.controller)

    def test_new_fitting_item_id(self):
        with self.assertLockedTransaction():
            self.fitting.UpdateItem(OTHER_ITEM_ID, OTHER_TYPE_ID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertEqual(self.controller.typeID, OTHER_TYPE_ID)
        self.assertEqual(self.controller.itemID, OTHER_ITEM_ID)
        self.assertSkinState(applied=None, previewed=None, pending=None)

    def test_new_fitting_item_id_resets_pick(self):
        self.controller.PickSkin(LICENSED_SKIN)
        with self.assertLockedTransaction():
            self.fitting.UpdateItem(OTHER_ITEM_ID, OTHER_TYPE_ID)
        self.assertSkinState(pending=None)

    def test_skin_change_event(self):
        with self.assertLockedTransaction():
            self.controller.OnActiveShipSkinChange(self.fitting.itemID, LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(applied=LICENSED_SKIN)

    def test_skin_change_event_for_other_item(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnActiveShipSkinChange(OTHER_ITEM_ID, LICENSED_SKIN.skinID)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(applied=None, pending=LICENSED_SKIN)

    def test_skin_change_event_updates_pending_skin_to_applied(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, LICENSED_SKIN.skinID)
        self.assertSkinState(applied=LICENSED_SKIN, pending=None)

    def test_skin_change_event_does_not_mess_with_other_pending_skins(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, OTHER_LICENSED_SKIN.skinID)
        self.assertSkinState(applied=OTHER_LICENSED_SKIN, pending=LICENSED_SKIN)

    def test_skin_change_event_does_not_change_previewed(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(applied=LICENSED_SKIN, previewed=UNLICENSED_SKIN)

    def test_skin_change_event_with_same_skin_already_applied(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, LICENSED_SKIN.skinID)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(applied=LICENSED_SKIN, pending=None)

    def test_pick_none_skin_with_applied_skin(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.PickSkin(None)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(applied=None, previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_skin_change_event_handles_none_skin_with_nothing_picked(self):
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, None)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(applied=None, previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_skin_change_event_handles_none_skin_with_applied_skin(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, None)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(applied=None, previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_skin_change_event_handles_none_skin_with_pending_skin(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, None)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(pending=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_skin_change_event_handles_none_skin_with_previewed_skin(self):
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnActiveShipSkinChange(self.fitting.itemID, None)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(previewed=UNLICENSED_SKIN)
        self.assertEqual(self.fitting.material, UNLICENSED_SKIN.material)

    def test_applied_skin_is_initially_pulled_from_storage(self):
        self.adapter.GetAppliedSkin.return_value = LICENSED_SKIN
        self.controller = self.module.FittingSkinPanelController(fitting=self.fitting, adapter=self.adapter)
        self.assertSkinState(applied=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_applied_skin_is_fetched_on_new_item_id(self):
        self.adapter.GetAppliedSkin.return_value = LICENSED_SKIN
        self.fitting.UpdateItem(OTHER_ITEM_ID, OTHER_TYPE_ID)
        self.assertSkinState(applied=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_on_apply_failed_event(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        with self.assertLockedTransaction():
            self.controller.OnApplySkinFailed(ITEM_ID, LICENSED_SKIN)
        self.events.onChange.assert_called_once_with()
        self.assertSkinState(pending=None)
        self.assertIsNone(self.fitting.material)

    def test_on_apply_failed_reverts_to_known_applied(self):
        self.adapter.GetAppliedSkin.return_value = LICENSED_SKIN
        self.controller.PickSkin(OTHER_LICENSED_SKIN)
        self.controller.OnApplySkinFailed(ITEM_ID, OTHER_LICENSED_SKIN)
        self.assertSkinState(applied=LICENSED_SKIN, pending=None)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_on_apply_failed_for_irrelevant_item(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnApplySkinFailed(OTHER_ITEM_ID, LICENSED_SKIN)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(pending=LICENSED_SKIN)

    def test_on_apply_skin_failed_with_different_pending(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.controller.OnApplySkinFailed(ITEM_ID, OTHER_LICENSED_SKIN)
        self.assertFalse(self.events.onChange.called)
        self.assertSkinState(pending=LICENSED_SKIN)
        self.assertEqual(self.fitting.material, LICENSED_SKIN.material)

    def test_on_skin_license_activated_with_nothing_picked(self):
        with self.assertLockedTransaction():
            self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(applied=None, previewed=None, pending=None)
        self.assertIsNone(self.fitting.material)

    def test_on_skin_license_activated_with_previewed_skin(self):
        skin = MockSkin(UNLICENSED_SKIN.materialID, skinID=SKIN_ID, licensed=True)
        self.controller.PickSkin(UNLICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.adapter.GetSkins.return_value = [skin]
        self.controller.OnSkinLicenseActivated(SKIN_ID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(previewed=None)
        self.assertIsNone(self.fitting.material)

    def test_on_skin_license_activated_with_pending_skin(self):
        self.controller.PickSkin(LICENSED_SKIN)
        self.events.onChange.reset_mock()
        self.adapter.GetSkins.return_value = [SKIN]
        self.controller.OnSkinLicenseActivated(LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(pending=None)
        self.assertIsNone(self.fitting.material)

    def test_on_skin_license_activated_with_applied_skin(self):
        self.apply_skin(LICENSED_SKIN)
        self.controller.OnSkinLicenseActivated(LICENSED_SKIN.skinID)
        self.events.onChange.assert_called_once_with()
        self.events.onSkinsChange.assert_called_once_with()
        self.assertSkinState(applied=None)
        self.assertIsNone(self.fitting.material)

    def test_picking_skin_while_item_changes_applies_to_correct_item(self):

        def change_item_id():
            self.lock.acquire.side_effect = None
            self.fitting.UpdateItem(OTHER_ITEM_ID, OTHER_TYPE_ID)

        self.lock.acquire.side_effect = change_item_id
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, LICENSED_SKIN)

    def test_picking_skin_uses_cached_item_id(self):
        self.fitting.typeID = OTHER_TYPE_ID
        self.fitting.itemID = OTHER_ITEM_ID
        self.controller.PickSkin(LICENSED_SKIN)
        self.adapter.ApplySkin.assert_called_once_with(self.controller, ITEM_ID, LICENSED_SKIN)


if __name__ == '__main__':
    unittest.main()
