#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\shipFittingControllerGhost.py
from dogma import const as dogmaConst
from eve.client.script.ui.shared.fitting.fittingController import ShipFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GHOST_FITTABLE_GROUPS, ModifiedAttribute, GetEffectiveHp
from eve.client.script.ui.shared.fittingGhost.fittingSlotControllerGhost import ShipFittingSlotControllerGhost
import evetypes

class ShipFittingControllerGhost(ShipFittingController):
    SLOT_CLASS = ShipFittingSlotControllerGhost
    __notifyevents__ = ['OnDogmaAttributeChanged',
     'OnStanceActive',
     'OnDogmaItemChange',
     'OnAttributes',
     'OnAttribute',
     'ProcessActiveShipChanged',
     'OnFittingUpdateStatsNeeded',
     'OnPostCfgDataChanged',
     'OnSimulatedShipLoaded',
     'OnFakeUpdateFittingWindow']

    def __init__(self, itemID, typeID = None):
        ShipFittingController.__init__(self, itemID, typeID)
        self.attributesBeforeGhostfitting = {}

    def OnFakeUpdateFittingWindow(self, *args):
        self._UpdateSlots()

    def OnSimulatedShipLoaded(self, itemID, typeID = None):
        self.SetDogmaLocation()
        self.UpdateItem(itemID, typeID)

    def IsSimulated(self):
        return sm.GetService('fittingSvc').IsShipSimulated()

    def SetGhostFittedItem(self, ghostItem = None):
        if not self.IsSimulated():
            ShipFittingController.SetGhostFittedItem(self, ghostItem)
            return
        self.ResetFakeItemInfo()
        if ghostItem and evetypes.GetCategoryID(ghostItem.typeID) not in GHOST_FITTABLE_GROUPS:
            return
        dogmaItem = None
        if ghostItem:
            self.attributesBeforeGhostfitting = self.GetCurrentAttributeValues()
            dogmaItem = self.ghostFittingExtension.GhostFitItem(ghostItem)
        self.ghostFittedItem = dogmaItem
        self.on_item_ghost_fitted()
        self.on_stats_changed()

    def ResetFakeItemInfo(self):
        self.attributesBeforeGhostfitting = {}
        self.RemoveFakeItem()

    def RemoveFakeItem(self):
        if not self.ghostFittedItem:
            return
        dogmaItem = self.dogmaLocation.SafeGetDogmaItem(self.ghostFittedItem.itemID)
        if dogmaItem:
            self.ghostFittingExtension.UnFitItem(dogmaItem)

    def GetCurrentAttributeValues(self):
        attributeValueDict = {dogmaConst.attributeScanResolution: self.GetScanResolution().value,
         dogmaConst.attributeMaxTargetRange: self.GetMaxTargetRange().value,
         dogmaConst.attributeMaxLockedTargets: self.GetMaxTargets().value,
         dogmaConst.attributeSignatureRadius: self.GetSignatureRadius().value,
         dogmaConst.attributeScanRadarStrength: self.GetScanRadarStrength().value,
         dogmaConst.attributeScanMagnetometricStrength: self.GetScanMagnetometricStrength().value,
         dogmaConst.attributeScanGravimetricStrength: self.GetScanGravimetricStrength().value,
         dogmaConst.attributeScanLadarStrength: self.GetScanLadarStrength().value,
         dogmaConst.attributeMass: self.GetMass().value,
         dogmaConst.attributeAgility: self.GetAgility().value,
         dogmaConst.attributeBaseWarpSpeed: self.GetBaseWarpSpeed().value,
         dogmaConst.attributeWarpSpeedMultiplier: self.GetWarpSpeedMultiplier().value,
         dogmaConst.attributeMaxVelocity: self.GetMaxVelocity().value,
         dogmaConst.attributeCpuLoad: self.GetCPULoad().value,
         dogmaConst.attributeCpuOutput: self.GetCPUOutput().value,
         dogmaConst.attributePowerLoad: self.GetPowerLoad().value,
         dogmaConst.attributePowerOutput: self.GetPowerOutput().value,
         dogmaConst.attributeUpgradeLoad: self.GetCalibrationLoad().value,
         dogmaConst.attributeUpgradeCapacity: self.GetCalibrationOutput().value,
         dogmaConst.attributeShieldCapacity: self.GetShieldHp().value,
         dogmaConst.attributeArmorHP: self.GetArmorHp().value,
         dogmaConst.attributeHp: self.GetStructureHp().value,
         dogmaConst.attributeShieldRechargeRate: self.GetRechargeRate().value,
         dogmaConst.attributeShieldEmDamageResonance: self.GetShieldEmDamageResonance().value,
         dogmaConst.attributeShieldExplosiveDamageResonance: self.GetShieldExplosiveDamageResonance().value,
         dogmaConst.attributeShieldKineticDamageResonance: self.GetShieldKineticDamageResonance().value,
         dogmaConst.attributeShieldThermalDamageResonance: self.GetShieldThermalDamageResonance().value,
         dogmaConst.attributeArmorEmDamageResonance: self.GetArmorEmDamageResonance().value,
         dogmaConst.attributeArmorExplosiveDamageResonance: self.GetArmorExplosiveDamageResonance().value,
         dogmaConst.attributeArmorKineticDamageResonance: self.GetArmorKineticDamageResonance().value,
         dogmaConst.attributeArmorThermalDamageResonance: self.GetArmorThermalDamageResonance().value,
         dogmaConst.attributeEmDamageResonance: self.GetStructureEmDamageResonance().value,
         dogmaConst.attributeExplosiveDamageResonance: self.GetStructureExplosiveDamageResonance().value,
         dogmaConst.attributeKineticDamageResonance: self.GetStructureKineticDamageResonance().value,
         dogmaConst.attributeThermalDamageResonance: self.GetStructureThermalDamageResonance().value,
         dogmaConst.attributeCapacity: self.GetCargoCapacity().value,
         dogmaConst.attributeDroneCapacity: self.GetDroneCapacity().value,
         'effectiveHp': self.GetEffectiveHp().value}
        return attributeValueDict

    def GetScanResolution(self):
        return self.GetStatsInfo(dogmaConst.attributeScanResolution, higherIsBetter=False)

    def GetMaxTargetRange(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxTargetRange)

    def GetMaxTargets(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxLockedTargets)

    def GetSignatureRadius(self):
        return self.GetStatsInfo(dogmaConst.attributeSignatureRadius, higherIsBetter=False)

    def GetScanRadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanRadarStrength)

    def GetScanMagnetometricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanMagnetometricStrength)

    def GetScanGravimetricStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanGravimetricStrength)

    def GetScanLadarStrength(self):
        return self.GetStatsInfo(dogmaConst.attributeScanLadarStrength)

    def GetMass(self):
        return self.GetStatsInfo(dogmaConst.attributeMass, higherIsBetter=False)

    def GetAgility(self):
        return self.GetStatsInfo(dogmaConst.attributeAgility, higherIsBetter=False)

    def GetBaseWarpSpeed(self):
        return self.GetStatsInfo(dogmaConst.attributeBaseWarpSpeed)

    def GetWarpSpeedMultiplier(self):
        return self.GetStatsInfo(dogmaConst.attributeWarpSpeedMultiplier)

    def GetMaxVelocity(self):
        return self.GetStatsInfo(dogmaConst.attributeMaxVelocity)

    def GetCPULoad(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuLoad, higherIsBetter=False)

    def GetCPUOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeCpuOutput)

    def GetPowerLoad(self):
        return self.GetStatsInfo(dogmaConst.attributePowerLoad, higherIsBetter=False)

    def GetPowerOutput(self):
        return self.GetStatsInfo(dogmaConst.attributePowerOutput)

    def GetCalibrationLoad(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeLoad, higherIsBetter=False)

    def GetCalibrationOutput(self):
        return self.GetStatsInfo(dogmaConst.attributeUpgradeCapacity)

    def GetShieldHp(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldCapacity)

    def GetArmorHp(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorHP)

    def GetStructureHp(self):
        return self.GetStatsInfo(dogmaConst.attributeHp)

    def GetRechargeRate(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldRechargeRate)

    def GetShieldEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldEmDamageResonance, higherIsBetter=False)

    def GetShieldExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldExplosiveDamageResonance, higherIsBetter=False)

    def GetShieldKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldKineticDamageResonance, higherIsBetter=False)

    def GetShieldThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeShieldThermalDamageResonance, higherIsBetter=False)

    def GetArmorEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorEmDamageResonance, higherIsBetter=False)

    def GetArmorExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorExplosiveDamageResonance, higherIsBetter=False)

    def GetArmorKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorKineticDamageResonance, higherIsBetter=False)

    def GetArmorThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeArmorThermalDamageResonance, higherIsBetter=False)

    def GetStructureEmDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeEmDamageResonance, higherIsBetter=False)

    def GetStructureExplosiveDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeExplosiveDamageResonance, higherIsBetter=False)

    def GetStructureKineticDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeKineticDamageResonance, higherIsBetter=False)

    def GetStructureThermalDamageResonance(self):
        return self.GetStatsInfo(dogmaConst.attributeThermalDamageResonance, higherIsBetter=False)

    def GetCargoCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeCapacity)

    def GetDroneCapacity(self):
        return self.GetStatsInfo(dogmaConst.attributeDroneCapacity)

    def GetStatsInfo(self, attributeID, higherIsBetter = True):
        oldValue = self.attributesBeforeGhostfitting.get(attributeID, None)
        currentValue = self.GetAttribute(attributeID)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue, higherIsBetter=higherIsBetter, attributeID=attributeID)

    def GetEffectiveHp(self):
        oldValue = self.attributesBeforeGhostfitting.get('effectiveHp', None)
        currentValue = GetEffectiveHp(self)
        return ModifiedAttribute(value=currentValue, oldValue=oldValue)
