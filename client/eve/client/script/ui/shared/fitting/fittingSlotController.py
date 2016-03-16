#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\fittingSlotController.py
import sys
import signals
from carbon.common.script.util.logUtil import LogException
from carbonui import const as uiconst
from eve.client.script.ui.shared.fitting.fittingUtil import GetPowerType
from eve.client.script.ui.shared.fittingGhost.slotControllerGhostFittingExtension import ShipFittingSlotControllerGhostFittingExtension
from inventorycommon import const as invConst
from localization import GetByLabel

class FittingSlotController(object):

    def __init__(self, flagID, parentController):
        self.flagID = flagID
        self.moduleItemID = None
        self.chargeItemID = None
        self.parentController = parentController
        self.ghostFittingExtension = ShipFittingSlotControllerGhostFittingExtension(self)
        self.on_online_state_change = signals.Signal()
        self.on_item_fitted = signals.Signal()

    @apply
    def dogmaModuleItem():

        def fget(self):
            if self.moduleItemID:
                return self.dogmaLocation.SafeGetDogmaItem(self.moduleItemID)
            else:
                return None

        def fset(self, value):
            LogException('Setting dogmaModuleItem, no one should be doing that!')

        return property(**locals())

    @apply
    def dogmaChargeItem():

        def fget(self):
            if self.chargeItemID:
                return self.dogmaLocation.SafeGetDogmaItem(self.chargeItemID)
            else:
                return None

        def fset(self, value):
            LogException('Setting dogmaChargeItem, no one should be doing that!')

        return property(**locals())

    @apply
    def dogmaLocation():

        def fget(self):
            return self.parentController.GetDogmaLocation()

        def fset(self, value):
            LogException('Setting dogmaLocation, no one should be doing that!')

        return property(**locals())

    def SetModuleAndChargeIDs(self, moduleItemID, chargeItemID):
        self.moduleItemID = moduleItemID
        self.chargeItemID = chargeItemID

    def GetParentID(self):
        return self.parentController.GetItemID()

    def GetPowerType(self):
        return GetPowerType(self.flagID)

    def GetFlagID(self):
        return self.flagID

    def Close(self):
        self.on_online_state_change.clear()
        self.on_item_fitted.clear()

    def GetModule(self):
        return self.dogmaModuleItem

    def GetModuleID(self):
        return self.moduleItemID

    def GetModuleTypeID(self):
        if self.dogmaModuleItem:
            return self.dogmaModuleItem.typeID

    def GetCharge(self):
        return self.dogmaChargeItem

    def GetChargeQuantity(self):
        if self.moduleItemID:
            self.dogmaLocation.GetQuantity(self.moduleItemID)
        return 0

    def IsChargeable(self):
        return bool(self.dogmaModuleItem and self.dogmaModuleItem.groupID in cfg.__chargecompatiblegroups__)

    def GetChargeCapacity(self):
        return self.dogmaLocation.GetCapacity(self.GetModule().locationID, const.attributeCapacity, self.GetFlagID())

    def FitCharge(self, item):
        self.dogmaLocation.inventory.Add(item.itemID, item.locationID, qty=1, flag=self.GetFlagID())

    def FitCharges(self, items):
        if self.IsSimulated():
            return self.ghostFittingExtension.FitCharges(self.flagID, items)
        chargeTypeID = items[0].typeID
        self.dogmaLocation.DropLoadChargeToModule(self.GetModuleID(), chargeTypeID, items)

    def IsSimulated(self):
        return self.parentController.IsSimulated()

    def UnfitCharge(self):
        parentID = self.GetParentID()
        if parentID is None:
            return
        chargeID = self.GetCharge().itemID
        invCache = sm.GetService('invCache')
        parentInv = invCache.GetInventoryFromId(parentID, locationID=session.stationid2)
        if isinstance(chargeID, tuple):
            chargeIDs = self.GetWeaponBankChargeIDs()
            if chargeIDs:
                if session.stationid2:
                    invCache.GetInventory(const.containerHangar).MultiAdd(chargeIDs, parentID, flag=const.flagHangar, fromManyFlags=True)
                else:
                    invCache.GetInventoryFromId(session.shipid).MultiAdd(chargeIDs, parentID, flag=const.flagCargo)
            elif session.stationid2:
                parentInv.RemoveChargeToHangar(chargeID)
            else:
                parentInv.RemoveChargeToCargo(chargeID)
        else:
            crystalIDs = self.GetWeaponBankCrystalIDs()
            if crystalIDs:
                if session.stationid2:
                    invCache.GetInventory(const.containerHangar).MultiAdd(crystalIDs, parentID, flag=const.flagHangar, fromManyFlags=True)
                else:
                    parentInv.MultiAdd(crystalIDs, parentID, flag=const.flagCargo, fromManyFlags=True)
            elif session.stationid2:
                invCache.GetInventory(const.containerHangar).Add(chargeID, parentID)
            else:
                parentInv.Add(chargeID, parentID, qty=None, flag=const.flagCargo)

    def FitModule(self, item):
        self.dogmaLocation.TryFit(item, self.flagID)

    def UnfitModule(self, *args):
        if self.GetModule() is None:
            return
        parentID = self.GetParentID()
        if parentID is None:
            return
        masterID = self.IsInWeaponBank()
        invCache = sm.GetService('invCache')
        if masterID:
            ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/Common/Confirm'),
             'question': GetByLabel('UI/Fitting/ClearGroupModule')}, uiconst.YESNO)
            if ret != uiconst.ID_YES:
                return
            self.GetModule().dogmaLocation.UngroupModule(parentID, masterID)
        if self.GetCharge() is not None:
            self.UnfitCharge()
        if session.stationid2:
            invCache.GetInventory(const.containerHangar).Add(self.GetModuleID(), parentID)
        else:
            shipInv = invCache.GetInventoryFromId(parentID, locationID=session.stationid2)
            shipInv.Add(self.GetModuleID(), parentID, qty=None, flag=const.flagCargo)

    def Unfit(self, *args):
        parentID = self.GetParentID()
        if parentID is None:
            return
        invCache = sm.GetService('invCache')
        parentInv = invCache.GetInventoryFromId(parentID, locationID=session.stationid2)
        if self.GetPowerType() == const.effectRigSlot:
            ret = eve.Message('RigUnFittingInfo', {}, uiconst.OKCANCEL)
            if ret != uiconst.ID_OK:
                return
            parentInv.DestroyFitting(self.GetModuleID())
        elif self.GetCharge():
            self.UnfitCharge()
        else:
            self.UnfitModule()

    def IsGroupable(self):
        return self.GetModule().groupID in const.dgmGroupableGroupIDs

    def GetDragData(self):
        l = []
        if self.dogmaChargeItem:
            l.extend(self.GetChargeDragNodes())
        if l:
            return l
        if self.GetModule() is None:
            return l
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            if not self.IsGroupable():
                return []
            sm.ScatterEvent('OnStartSlotLinkingMode', self.GetModule().typeID)
        return self.GetModuleDragData()

    def GetModuleDragData(self):
        return self.dogmaLocation.GetDragData(self.GetModuleID())

    def GetChargeDragNodes(self, *args):
        return self.dogmaLocation.GetDragData(self.chargeItemID)

    def SlotExists(self):
        if self.IsSubsystemSlot():
            if self.parentController.HasStance() or not self.parentController.HasSubsystems():
                return False
        return self.dogmaLocation.SlotExists(self.GetParentID(), self.flagID)

    def IsSubsystemSlot(self):
        return self.flagID in invConst.subSystemSlotFlags

    def IsOnlineable(self):
        if not self.GetModule() or not self.SlotExists():
            return False
        try:
            return const.effectOnline in self.dogmaLocation.dogmaStaticMgr.effectsByType[self.GetModuleTypeID()]
        except ReferenceError:
            pass

    def IsOnline(self):
        return self.GetModule().IsOnline()

    def OnlineModule(self):
        self.dogmaLocation.OnlineModule(self.GetModuleID())

    def OfflineModule(self):
        self.dogmaLocation.OfflineModule(self.GetModuleID())

    def IsInWeaponBank(self, item = None):
        if not item:
            return self.dogmaLocation.IsInWeaponBank(self.GetModule().locationID, self.GetModuleID())
        else:
            return self.dogmaLocation.IsInWeaponBank(item.locationID, item.itemID)

    def GetWeaponBankChargeIDs(self):
        return self.dogmaLocation.GetSubLocationsInBank(self.GetParentID(), self.GetCharge().itemID)

    def GetWeaponBankCrystalIDs(self):
        return self.dogmaLocation.GetCrystalsInBank(self.GetParentID(), self.GetCharge().itemID)

    def LinkWithWeapon(self, item):
        self.dogmaLocation.LinkWeapons(self.GetModule().locationID, self.GetModuleID(), item.itemID)

    def DestroyWeaponBank(self):
        masterID = self.IsInWeaponBank()
        if masterID:
            self.dogmaLocation.DestroyWeaponBank(self.GetModule().locationID, masterID)

    def ToggleOnlineModule(self):
        if self.IsOnline():
            if self.IsInWeaponBank():
                ret = eve.Message('CustomQuestion', {'header': GetByLabel('UI/Common/Confirm'),
                 'question': GetByLabel('UI/Fitting/QueryGroupOffline')}, uiconst.YESNO)
                if ret != uiconst.ID_YES:
                    return
            self.OfflineModule()
        else:
            self.OnlineModule()

    def IsRigSlot(self):
        return self.flagID in invConst.rigSlotFlags

    def OnSlotAttributeChanged(self, parentID, itemID, attributeID, value):
        try:
            if self.GetModule() is not None and self.GetModuleID() == itemID and attributeID == const.attributeIsOnline:
                self.on_online_state_change()
            elif attributeID == const.attributeQuantity:
                if not isinstance(itemID, tuple):
                    return
                parentID, flagID, typeID = itemID
                if parentID != self.GetParentID() or flagID != self.GetFlagID():
                    return
                if not value:
                    self.chargeItemID = None
                self.on_item_fitted()
        except ReferenceError:
            self.chargeItemID = None
            sys.exc_clear()

    def IsModulePreviewModule(self):
        return False


class ShipFittingSlotController(FittingSlotController):
    pass
