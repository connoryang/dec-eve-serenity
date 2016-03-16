#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\starbaseDogmaItem.py
from locationDogmaItem import LocationDogmaItem
from utillib import KeyVal
import inventorycommon.const as invconst
import dogma.const as dgmconst
from ccpProfile import TimedFunction

class StarbaseDogmaItem(LocationDogmaItem):

    @TimedFunction('StarbaseDogmaItem::__init__')
    def __init__(self, dogmaLocation, item, eveCfg, clientIDFunc):
        super(StarbaseDogmaItem, self).__init__(dogmaLocation, item, eveCfg, clientIDFunc)
        self.controlTower = None

    def SetLocation(self, locationID, locationDogmaItem, flagID):
        if self.controlTower and locationID != self.controlTower:
            raise RuntimeError('Structure %s being assigned to a different location than its currently marked control tower!' % self)
        super(StarbaseDogmaItem, self).SetLocation(locationID, locationDogmaItem, flagID)
        if self.controlTower:
            self.AddModifierSet(locationDogmaItem.locationMods)
            try:
                groupMods = locationDogmaItem.locationGroupMods[self.groupID]
                self.AddModifierSet(groupMods)
            except KeyError:
                pass

            for skillID in self.reqSkills:
                try:
                    skillMods = locationDogmaItem.locationReqSkillMods[skillID]
                    self.AddModifierSet(skillMods)
                except KeyError:
                    pass

    def UnsetLocation(self, locationDogmaItem):
        super(StarbaseDogmaItem, self).UnsetLocation(locationDogmaItem)
        if self.controlTower is not None:
            raise RuntimeError('Structure %s being disowned but marked as owned by tower %s' % (self, self.controlTower))
        if locationDogmaItem:
            self.RemoveModifierSet(locationDogmaItem.locationMods)
            try:
                groupMods = locationDogmaItem.locationGroupMods[self.groupID]
                self.RemoveModifierSet(groupMods)
            except KeyError:
                pass

            for skillID in self.reqSkills:
                try:
                    skillMods = locationDogmaItem.locationReqSkillMods[skillID]
                    self.RemoveModifierSet(skillMods)
                except KeyError:
                    pass

    def GetLocation(self):
        if self.controlTower:
            try:
                location = self.dogmaLocation.dogmaItems[self.controlTower]
            except KeyError:
                self.controlTower = None
                location = self.location

        else:
            location = self.location
        return location

    def GetEnvironmentInfo(self):
        otherID = self.subLocations.get(invconst.flagHiSlot0, None)
        if otherID is None:
            other = self.dogmaLocation.GetChargeNonDB(self.itemID, invconst.flagHiSlot0)
            if other is not None:
                otherID = other.itemID
        return KeyVal(itemID=self.itemID, shipID=self.controlTower, charID=None, otherID=otherID, targetID=None, effectID=None)

    def CanFitItem(self, dogmaItem, flagID):
        if dogmaItem.itemID == self.itemID:
            return True
        if flagID == invconst.flagHiSlot0:
            return True
        return False

    def IsOnline(self):
        return dgmconst.effectOnlineForStructures in self.activeEffects

    def IsActive(self):
        for effectID in self.activeEffects:
            if effectID == dgmconst.effectOnlineForStructures:
                continue
            effect = self.dogmaLocation.GetEffect(effectID)
            if effect.effectCategory in (dgmconst.dgmEffActivation, dgmconst.dgmEffTarget):
                return True

        return False

    def SetControlTower(self, newTower):
        self.controlTower = newTower
