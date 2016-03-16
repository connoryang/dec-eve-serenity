#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\slimDogmaItem.py
import itertools
import weakref
from dogma.dogmaLogging import *
import blue
import evetypes
from eveexceptions.exceptionEater import ExceptionEater
import dogma.const as const
from dogma.effects.environment import Environment
from dogma.attributes.attribute import NewItemAttributeFactory
from utillib import KeyVal, keydefaultdict
from collections import defaultdict
from ccpProfile import TimedFunction
RESISTANCEMATRIX = {const.attributeShieldCharge: [1,
                               1,
                               1,
                               1],
 const.attributeArmorDamage: [1,
                              1,
                              1,
                              1],
 const.attributeDamage: [1,
                         1,
                         1,
                         1]}
OPERATOR_OFFSET = 1

class SlimDogmaItem(object):

    @TimedFunction('SlimDogmaItem::__init__')
    def __init__(self, dogmaLocation, invItem, clientIDFunc, attributes = None):
        self._owner = None
        self.dogmaLocation = dogmaLocation
        self.dogmaLocation.dogmaItems[invItem.itemID] = self
        self.invItem = invItem
        self.itemID = invItem.itemID
        self.typeID = invItem.typeID
        self.groupID = invItem.groupID
        self.categoryID = invItem.categoryID
        self.reqSkills = dogmaLocation.dogmaStaticMgr.GetRequiredSkills(invItem.typeID)
        self.contentsChangedCallbacks = set()
        self.FindClientID = clientIDFunc
        attributeFactory = NewItemAttributeFactory(self, self.dogmaLocation, self.dogmaLocation.dogmaStaticMgr, attributes)
        self.attributes = keydefaultdict(attributeFactory.GetAttributeInstance)
        self.activeEffects = {}
        self._SetupLocationLinks()
        self._SetupLocationMods()
        self._SetupOwnerLinks()
        self._SetupOwnerMods()
        locationItem = self.location
        if locationItem:
            for callBack in locationItem.contentsChangedCallbacks:
                with ExceptionEater('Contents callback excepted'):
                    callBack(self)

    def __str__(self):
        return '<%s::%s::%s>' % (self.__class__.__name__, self.itemID, self.typeID)

    def __repr__(self):
        return '<%s::%s::%s>' % (self.__class__.__name__, self.itemID, self.typeID)

    @property
    def owner(self):
        try:
            if self._owner:
                return self._owner
            return None
        except ReferenceError:
            return None

    @owner.setter
    def owner(self, value):
        self._owner = value

    def _SetupLocationLinks(self):
        self.subItems = self.__ClaimSubItems()
        for theSubItem in self.subItems:
            self.dogmaLocation.LogInfo('Patching-up location link for item {} to location {}'.format(theSubItem, self))
            theSubItem.location = self

        try:
            locationItem = self.dogmaLocation.dogmaItems[self.invItem.locationID]
            locationItem.subItems.add(self)
            self.location = locationItem
        except KeyError:
            self.location = None
            if self.invItem.locationID is not None:
                self.__MarkMissingLocation()

    def _SetupOwnerLinks(self):
        self.ownedItems = self.__ClaimOwnedItems()
        for theOwnedItem in self.ownedItems:
            self.dogmaLocation.LogInfo('Patching-up owner link for item {} to location {}'.format(theOwnedItem, self))
            theOwnedItem.owner = weakref.proxy(self)

        self.ownedItemsAtCreation = self.ownedItems.copy()
        try:
            ownerItem = self.dogmaLocation.dogmaItems[self.invItem.ownerID]
            ownerItem.ownedItems.add(self)
            self.owner = weakref.proxy(ownerItem)
        except KeyError:
            self.owner = None
            if self.invItem.ownerID is not None:
                self.__MarkMissingOwner()

    def __ClaimSubItems(self):
        if self.itemID not in self.dogmaLocation.itemsMissingLocation:
            return set()
        return self.dogmaLocation.itemsMissingLocation.pop(self.itemID)

    def __ClaimOwnedItems(self):
        if self.itemID not in self.dogmaLocation.itemsMissingOwner:
            return set()
        return self.dogmaLocation.itemsMissingOwner.pop(self.itemID)

    def __MarkMissingLocation(self):
        locationID = self.invItem.locationID
        if locationID == self.dogmaLocation.locationID:
            return
        self.dogmaLocation.itemsMissingLocation[locationID].add(self)

    def __MarkMissingOwner(self):
        ownerID = self.invItem.ownerID
        if ownerID < 2:
            return
        self.dogmaLocation.itemsMissingOwner[ownerID].add(self)

    def __UnmarkMissingLocation(self, locationID):
        if locationID == self.dogmaLocation.locationID:
            return
        self.dogmaLocation.itemsMissingLocation[locationID].discard(self)
        if not self.dogmaLocation.itemsMissingLocation[locationID]:
            del self.dogmaLocation.itemsMissingLocation[locationID]

    def __UnmarkMissingOwner(self, ownerID):
        self.dogmaLocation.itemsMissingOwner[ownerID].discard(self)
        if not self.dogmaLocation.itemsMissingOwner[ownerID]:
            del self.dogmaLocation.itemsMissingOwner[ownerID]

    def _SetupLocationMods(self):
        self.locationMods = defaultdict(set)
        self.locationGroupMods = defaultdict(lambda : defaultdict(set))
        self.locationReqSkillMods = defaultdict(lambda : defaultdict(set))

    def _SetupOwnerMods(self):
        self.ownerReqSkillMods = defaultdict(lambda : defaultdict(set))

    def _PickUpInitialModifiersFromLocationTo(fromSelf, toAttrib):
        attribID = toAttrib.attribID
        dogmaItem = toAttrib.item
        groupID = dogmaItem.groupID
        if attribID in fromSelf.locationMods:
            myLocMods = fromSelf.locationMods[attribID]
            fromSelf._ApplyModsToAttrib(myLocMods, toAttrib, debugContext='PickUp LocMods')
        if groupID in fromSelf.locationGroupMods and attribID in fromSelf.locationGroupMods[groupID]:
            myLocGroupMods = fromSelf.locationGroupMods[groupID][attribID]
            fromSelf._ApplyModsToAttrib(myLocGroupMods, toAttrib, debugContext='PickUp LogGroupMods')
        for skillID in dogmaItem.reqSkills:
            if skillID in fromSelf.locationReqSkillMods and attribID in fromSelf.locationReqSkillMods[skillID]:
                myLocReqSkillMods = fromSelf.locationReqSkillMods[skillID][attribID]
                fromSelf._ApplyModsToAttrib(myLocReqSkillMods, toAttrib, debugContext='PickUp LocReqSkillMods')

    def _PickUpInitialModifiersFromOwnerTo(fromSelf, toAttrib):
        attribID = toAttrib.attribID
        dogmaItem = toAttrib.item
        for skillID in dogmaItem.reqSkills:
            if skillID in fromSelf.ownerReqSkillMods and attribID in fromSelf.ownerReqSkillMods[skillID]:
                myOwnerReqSkillMods = fromSelf.ownerReqSkillMods[skillID][attribID]
                fromSelf._ApplyModsToAttrib(myOwnerReqSkillMods, toAttrib, debugContext='PickUp OwnerReqSkillMods')

    def _ApplyModsToAttrib(self, modSeq, toAttrib, callOnAttributeChanged = False, debugContext = '<no debug context>'):
        if not modSeq:
            return
        itemsToPurge = None
        for modifier in modSeq:
            operation, fromAttrib = modifier
            if fromAttrib.IsAnOrphan():
                if itemsToPurge is None:
                    itemsToPurge = set()
                itemsToPurge.add(modifier)
            else:
                fromAttrib.AddModifierTo(operation, toAttrib)
                if callOnAttributeChanged:
                    self.dogmaLocation.OnAttributeChanged(toAttrib.attribID, self.itemID)

        if itemsToPurge:
            self.dogmaLocation.LogError('SlimDogmaItem::_ApplyModsToAttrib PURGING ORPHANS (attempting self-repair)! \nmodSeq = {}, \nitemsToPurge = {}, \ntoAttrib = {} \n, debugContext = {}'.format(modSeq, itemsToPurge, toAttrib, debugContext))
            modSeq.difference_update(itemsToPurge)

    def CanAttributeBeModified(self):
        return True

    def IsOwnerModifiable(self):
        return False

    def GetOwnedItemsToModify(self):
        LogTraceback('GetOwnedItemsToModify called on non-owner item %s of type %s' % (self.itemID, self.__class__))
        return []

    @property
    def locationID(self):
        return self.invItem.locationID

    @property
    def ownerID(self):
        return self.invItem.ownerID

    @ownerID.setter
    def ownerID(self, ownerID):
        self.invItem.ownerID = ownerID

    def GetPilot(self):
        return None

    def GetLocation(self):
        return self.location

    def GetValue(self, attributeID):
        return self.attributes[attributeID].GetValue()

    def GetResistanceMatrix(self):
        return RESISTANCEMATRIX

    def Unload(self):
        if self.owner:
            self.dogmaLocation.LogInfo('SlimDogmaItem removing self from ownedItems of owner:', self.owner)
            try:
                self.owner.ownedItems.remove(self)
            except KeyError:
                LogTraceback("Tried to remove self from ownedItems but wasn't there")

        else:
            self.__UnmarkMissingOwner(self.invItem.ownerID)
        if self.location:
            self.dogmaLocation.LogInfo('SlimDogmaItem removing self from subItems of location:', self.location)
            try:
                self.location.subItems.remove(self)
            except KeyError:
                LogTraceback("Tried to remove self from subItems but wasn't there")

        else:
            self.__UnmarkMissingLocation(self.invItem.locationID)

    def RemoveModifierSet(self, modifiers):
        for attribID, modSet in modifiers.iteritems():
            if attribID in self.attributes:
                toAttrib = self.attributes[attribID]
                for operation, fromAttrib in modSet:
                    fromAttrib.RemoveOutgoingModifier(operation, toAttrib)
                    toAttrib.RemoveIncomingModifier(operation, fromAttrib)

    def AddModifierSet(self, modifiers):
        for attribID, modSet in modifiers.iteritems():
            if attribID in self.attributes:
                toAttrib = self.attributes[attribID]
                for operation, fromAttrib in modSet:
                    fromAttrib.AddOutgoingModifier(operation, toAttrib)
                    toAttrib.AddIncomingModifier(operation, fromAttrib)
                    self.dogmaLocation.OnAttributeChanged(attribID, self.itemID)

    def HandleLocationChange(self, oldLocationID):
        if self.location is None:
            self.__UnmarkMissingLocation(oldLocationID)
        else:
            self.RemoveModifierSet(self.location.locationMods)
            try:
                locationGroupMods = self.location.locationGroupMods[self.groupID]
            except KeyError:
                pass
            else:
                self.RemoveModifierSet(locationGroupMods)

            for skillID in self.reqSkills:
                try:
                    locationReqSkillMods = self.location.locationReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    self.RemoveModifierSet(locationReqSkillMods)

        newLocationID = self.invItem.locationID
        try:
            locationItem = self.dogmaLocation.dogmaItems[newLocationID]
        except KeyError:
            self.location = None
            if newLocationID is not None:
                self.__MarkMissingLocation()
        else:
            self.AddModifierSet(locationItem.locationMods)
            try:
                locationGroupMods = locationItem.locationGroupMods[self.groupID]
            except KeyError:
                pass
            else:
                self.AddModifierSet(locationGroupMods)

            for skillID in self.reqSkills:
                try:
                    locationReqSkillMods = locationItem.locationReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    self.AddModifierSet(locationReqSkillMods)

    def HandlePilotChange(self, pilotID):
        if not pilotID:
            oldPilotItem = self.dogmaLocation.dogmaItems[self.GetPilot()]
            for skillID in self.reqSkills:
                try:
                    ownerReqSkillMods = oldPilotItem.ownerReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    self.RemoveModifierSet(ownerReqSkillMods)

        else:
            newPilotItem = self.dogmaLocation.dogmaItems[pilotID]
            for skillID in self.reqSkills:
                try:
                    ownerReqSkillMods = newPilotItem.ownerReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    self.RemoveModifierSet(ownerReqSkillMods)

    def HandleOwnerChange(self, oldOwnerID):
        if self.owner is None:
            self.__UnmarkMissingOwner(oldOwnerID)
        oldOwner = self.dogmaLocation.dogmaItems.get(oldOwnerID, None)
        if oldOwner is not None:
            for skillID in self.reqSkills:
                try:
                    ownerReqSkillMods = oldOwner.ownerReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    self.RemoveModifierSet(ownerReqSkillMods)

        newOwnerID = self.invItem.ownerID
        try:
            ownerItem = self.dogmaLocation.dogmaItems[newOwnerID]
        except KeyError:
            self.owner = None
            if newOwnerID is not None:
                self.dogmaLocation.itemsMissingOwner[newOwnerID].add(self)
        else:
            for skillID in self.reqSkills:
                try:
                    ownerReqSkillMods = ownerItem.ownerReqSkillMods[skillID]
                except KeyError:
                    pass
                else:
                    if self.IsOwnerModifiable():
                        self.AddModifierSet(ownerReqSkillMods)

                self.dogmaLocation.HandleDogmaLocationEffectsOnItem(self)

    @WrappedMethod
    def FlushAllModifiers(self):
        for attrib in self.attributes.itervalues():
            attrib.RemoveAllModifiers()

    def SerializeForPropagation(self):
        return _SlimDogmaItemPacker(self).PackItem()

    def UnpackPropagationData(self, propData, charID, shipID):
        _SlimDogmaItemUnpacker(self, self.dogmaLocation, propData, charID, shipID).UnpackItem()


class _SlimDogmaItemPacker(object):

    def __init__(self, dogmaItem):
        self.dogmaItem = dogmaItem

    @TimedFunction('DogmaLocation::PackItem')
    def PackItem(self):
        packedItem = KeyVal()
        self.PackAttributes(packedItem)
        self.PackModifiers(packedItem)
        self.PackModifierGroups(packedItem)
        self.PackEffects(packedItem)
        return packedItem

    def PackAttributes(self, packedItem):
        attributeValues = []
        for attribID, attrib in self.dogmaItem.attributes.iteritems():
            persistData = attrib.GetPersistData()
            if persistData is not None:
                attributeValues.append((attribID, persistData))

        packedItem.attributeValues = attributeValues

    def PackModifiers(self, packedItem):
        outgoingModifiers = defaultdict(list)
        for attribID, attribute in self.dogmaItem.attributes.iteritems():
            for operator, destAttrib in attribute.GetOutgoingModifiers():
                if destAttrib is not None:
                    if destAttrib.attribID is None:
                        LogTraceback('Packing modifiers with attribID None on %s which is definitely going to break while unpacking' % destAttrib)
                    else:
                        outgoingModifiers[attribID].append((operator, destAttrib.item.itemID, destAttrib.attribID))

        sanitized = {}
        sanitized.update(outgoingModifiers)
        packedItem.outgoingModifiers = sanitized

    def _SerializeModifierSet(self, modSet):
        modList = []
        for attribID, opSet in modSet.iteritems():
            for operation, fromAttrib in opSet:
                if hasattr(fromAttrib, 'noPropagation'):
                    continue
                try:
                    modList.append((attribID,
                     operation,
                     fromAttrib.item.itemID,
                     fromAttrib.attribID))
                except:
                    LogWarn("_SerializeModifierSet: Couldn't serialize fromAttrib {}".format(fromAttrib))

        return modList

    def PackModifierGroups(self, packedItem):
        packedItem.locationMods = self._SerializeModifierSet(self.dogmaItem.locationMods)
        packedItem.locationGroupMods = {groupID:self._SerializeModifierSet(modSet) for groupID, modSet in self.dogmaItem.locationGroupMods.iteritems()}
        packedItem.locationReqSkillMods = {skillID:self._SerializeModifierSet(modSet) for skillID, modSet in self.dogmaItem.locationReqSkillMods.iteritems()}
        packedItem.ownerReqSkillMods = {skillID:self._SerializeModifierSet(modSet) for skillID, modSet in self.dogmaItem.ownerReqSkillMods.iteritems()}

    def PackEffects(self, packedItem):
        packedItem.effectIDs = self.dogmaItem.activeEffects.keys()


class _SlimDogmaItemUnpacker(object):

    def __init__(self, dogmaItem, dogmaLM, propData, charID, shipID):
        self.dogmaItem = dogmaItem
        self.dogmaLM = dogmaLM
        self.propData = propData
        self.charID = charID
        self.shipID = shipID

    def UnpackItem(self):
        self.UnpackAttributes()
        self.UnpackModifiers()
        self.UnpackModifierSets()
        self.UnpackEffects()

    @TimedFunction('DogmaLocation::UnpackProp::Attribs')
    def UnpackAttributes(self):
        for attribID, newBaseValue in self.propData.attributeValues:
            self.dogmaItem.attributes[attribID].ApplyPersistData(newBaseValue)

    @TimedFunction('DogmaLocation::UnpackProp::Modifiers')
    def UnpackModifiers(self):
        for attribID, modList in self.propData.outgoingModifiers.iteritems():
            attrib = self.dogmaItem.attributes[attribID]
            for operator, destItemID, destAttribID in modList:
                destItem = self.dogmaLM.dogmaItems.get(destItemID)
                if destItem is None:
                    continue
                destAttrib = destItem.attributes[destAttribID]
                attrib.AddModifierTo(operator, destAttrib)

    def _UnpackModifierSet(self, modSet, packedData):
        for attribID, operation, fromItemID, fromAttribID in packedData:
            fromItem = self.dogmaLM.dogmaItems.get(fromItemID)
            if fromItem is None:
                continue
            fromAttrib = fromItem.attributes[fromAttribID]
            modSet[attribID].add((operation, fromAttrib))

    @TimedFunction('DogmaLocation::UnpackProp::ModSets')
    def UnpackModifierSets(self):
        self._UnpackModifierSet(self.dogmaItem.locationMods, self.propData.locationMods)
        for groupID, packedModSet in self.propData.locationGroupMods.iteritems():
            self._UnpackModifierSet(self.dogmaItem.locationGroupMods[groupID], packedModSet)

        for skillID, packedModSet in self.propData.locationReqSkillMods.iteritems():
            self._UnpackModifierSet(self.dogmaItem.locationReqSkillMods[skillID], packedModSet)

        for skillID, packedModSet in self.propData.ownerReqSkillMods.iteritems():
            self._UnpackModifierSet(self.dogmaItem.ownerReqSkillMods[skillID], packedModSet)

        ownerReqSkillMods = self.dogmaItem.ownerReqSkillMods
        if ownerReqSkillMods:
            for ownedItem in self.dogmaItem.ownedItemsAtCreation:
                modsToSetup = [ ownerReqSkillMods[skillID] for skillID in ownedItem.reqSkills if skillID in ownerReqSkillMods ]
                for mods in modsToSetup:
                    for attribID, modSet in mods.iteritems():
                        if attribID in ownedItem.attributes:
                            toAttrib = ownedItem.attributes[attribID]
                            for operator, fromAttrib in modSet:
                                fromAttrib.AddOutgoingModifier(operator, toAttrib)
                                toAttrib.AddIncomingModifier(operator, fromAttrib)

    def _MakeEnvironment(self, effectID, otherID):
        return Environment(self.dogmaItem.itemID, self.charID, self.shipID, None, otherID, effectID, self.dogmaLM, None)

    @TimedFunction('DogmaLocation::UnpackProp::Effects')
    def UnpackEffects(self):
        dogmaItem = self.dogmaItem
        now = blue.os.GetSimTime()
        otherID = None
        if evetypes.GetIsGroupFittableNonSingletonByGroup(dogmaItem.groupID):
            otherID = self.dogmaLM.GetSlotOther(self.shipID, dogmaItem.flagID)
        onlineEffect = None
        for possibleOnlineEffectID in self.dogmaLM.onlineEffects:
            if possibleOnlineEffectID in self.propData.effectIDs:
                onlineEnv = self._MakeEnvironment(possibleOnlineEffectID, otherID)
                onlineEffect = [now,
                 -1,
                 onlineEnv,
                 0]
                dogmaItem.activeEffects[possibleOnlineEffectID] = onlineEffect
                self.propData.effectIDs.remove(possibleOnlineEffectID)

        IsEffectPythonOverridden = self.dogmaLM.effectCompiler.IsEffectPythonOverridden
        staticEffects = self.dogmaLM.dogmaStaticMgr.effects
        passiveEffectEnvironment = None
        for effectID in self.propData.effectIDs:
            effectCategory = staticEffects[effectID].effectCategory
            if effectCategory == const.dgmEffPassive:
                if IsEffectPythonOverridden(effectID):
                    dogmaItem.activeEffects[effectID] = [now,
                     -1,
                     self._MakeEnvironment(effectID, otherID),
                     0]
                else:
                    if passiveEffectEnvironment is None:
                        passiveEffectEnvironment = self._MakeEnvironment(effectID, otherID)
                    dogmaItem.activeEffects[effectID] = [now,
                     -1,
                     passiveEffectEnvironment,
                     0]
            elif effectCategory == const.dgmEffOnline:
                dogmaItem.activeEffects[effectID] = onlineEffect[:]
            else:
                dogmaItem.activeEffects[effectID] = [now,
                 -1,
                 self._MakeEnvironment(effectID, otherID),
                 0]
