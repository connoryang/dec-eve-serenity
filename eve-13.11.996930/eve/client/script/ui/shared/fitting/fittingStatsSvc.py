#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fitting\fittingStatsSvc.py
import service

class FittingStatsSvc(service.Service):
    __guid__ = 'svc.fittingStatsSvc'
    __displayname__ = 'Fitting Stats Service'
    __notifyevents__ = []

    def Run(self, ms = None):
        pass

    def GetMultiplyCpy(self):
        pass


NO_HILITE_GROUPS_DICT = {const.groupRemoteSensorBooster: [const.attributeCpu, const.attributePower],
 const.groupRemoteSensorDamper: [const.attributeCpu, const.attributePower]}

class FittingStatsMagic(object):

    def __init__(self, typeID):
        self.dgmAttr = sm.GetService('godma').GetType(typeID)
        displayAttributes = self.dgmAttr.displayAttributes
        self.allowedAttributesByID = {x.attributeID:x for x in displayAttributes}
        self.noHiliteAttributesForGroup = NO_HILITE_GROUPS_DICT.get(self.dgmAttr.groupID, [])

    def GetMultiplyCpu(self):
        defaultValue = 1.0
        return self.GetAttributeValue(const.attributeCpuMultiplier, defaultValue)

    def GetExtraPower(self):
        defaultValue = 0.0
        increase = self.GetAttributeValue(const.attributePowerIncrease, defaultValue)
        output = self.GetAttributeValue(const.attributePowerOutput, defaultValue)
        return max(increase, output)

    def GetMultiplyPower(self):
        defaultMultiplierValue = 1.0
        multiplier = self.GetAttributeValue(const.attributePowerIncrease, defaultMultiplierValue)
        outputBonusValue = self.GetAttributeValue(const.attributePowerOutputMultiplier, 0)
        outputMultiplier = 1 + outputBonusValue / 100
        return max(multiplier, outputMultiplier)

    def GetExtraCalibrationLoad(self):
        defaultValue = 0.0
        return self.GetAttributeValue(const.attributeUpgradeCost, defaultValue)

    def GetExtraCargoSpaceMultiplier(self):
        defaultValue = 1.0
        return self.GetAttributeValue(const.attributeCargoCapacityMultiplier, defaultValue)

    def GetExtraDroneSpaceMultiplier(self):
        defaultValue = 1.0
        return self.GetAttributeValue(const.attributeDroneCapacity, defaultValue)

    def GetAttributeValue(self, attributeID, defaultValue):
        if self.UseDefaultValue(attributeID) or attributeID not in self.allowedAttributesByID:
            return defaultValue
        attributeValue = self.allowedAttributesByID[attributeID].value
        return attributeValue

    def UseDefaultValue(self, attributeID):
        if attributeID in self.noHiliteAttributesForGroup:
            return True
        return False

    def GetExtraValue(self, attributeID, startValue):
        return startValue + self.GetAttributeValue(attributeID, 0.0)

    def GetExtraCpuLoad(self, startValue = 0.0):
        cpuLoad = self.GetExtraValue(const.attributeCpuLoad, startValue)
        cpuLoad = self.GetExtraValue(const.attributeCpu, cpuLoad)
        return cpuLoad

    def GetExtraCpu(self, startValue = 0.0):
        cpu = self.GetExtraValue(const.attributeCpuOutput, startValue)
        return cpu

    def GetExtraPowerLoad(self, startValue = 0.0):
        powerLoad = self.GetExtraValue(const.attributePowerLoad, startValue)
        powerLoad = self.GetExtraValue(const.attributePower, powerLoad)
        return powerLoad
