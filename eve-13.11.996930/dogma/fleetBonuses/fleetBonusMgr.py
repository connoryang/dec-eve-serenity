#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\fleetBonuses\fleetBonusMgr.py
from dogma.dogmaLogging import *
from operator import itemgetter
from ccpProfile import TimedFunction
from dogma.attributes.attribute import AttributeInterface
from utillib import KeyVal

class FleetBonusAttribute(AttributeInterface):

    def __init__(self, modifierTypeName, targetAttribID, op, ownerCellID, isActive = True):
        self._modifierTypeName = modifierTypeName
        self._targetAttribID = targetAttribID
        self._op = op
        self._ownerCellID = ownerCellID
        dogmaStaticMgr = sm.GetService('dogmaStaticMgr')
        staticAttr = dogmaStaticMgr.attributes[self._targetAttribID]
        self.highIsGood = staticAttr.highIsGood
        self.selectBest = max if self.highIsGood else min
        self.item = None
        self.incomingModifiers = set()
        self.outgoingModifiers = set()
        self.isActive = isActive
        self.dirty = True

    def __str__(self):
        return "%s 'mod %s op %s -> %s (%s)' (FBA) on (Cell %s) [i%s:o%s]" % ('Active' if self.isActive else 'INACTIVE',
         self._modifierTypeName,
         self._op,
         cfg.dgmattribs[self._targetAttribID].attributeName,
         '+' if self.highIsGood else '-',
         self._ownerCellID,
         len(self.incomingModifiers),
         len(self.outgoingModifiers))

    def MakeNewChildAttrib_not_used(self, ownerCellID, isActive):
        return FleetBonusAttribute(self._modifierTypeName, self._targetAttribID, self._op, ownerCellID, isActive)

    def AddIncomingFleetBonus(self, bonusAttrib):
        if bonusAttrib in self.incomingModifiers:
            incomingMods = self.incomingModifiers
            return
        self.incomingModifiers.add(bonusAttrib)
        self.MarkDirty()

    def RemoveIncomingFleetBonus(self, bonusAttrib):
        try:
            self.incomingModifiers.remove(bonusAttrib)
            self.MarkDirty()
        except (TypeError, KeyError, ValueError):
            incomingMods = self.incomingModifiers

    def AddIncomingModifier(self, op, attribute):
        self.AddIncomingFleetBonus(attribute)

    def RemoveIncomingModifier(self, op, attribute):
        self.RemoveIncomingFleetBonus(attribute)

    def GetIncomingModifiers(self):
        return [ (None, attrib) for attrib in self.incomingModifiers ]

    def AddOutgoingModifier(self, op, outgoingAttrib):
        if outgoingAttrib in self.outgoingModifiers:
            outgoingMods = self.outgoingModifiers
            return
        self.outgoingModifiers.add((op, outgoingAttrib))

    def RemoveOutgoingModifier(self, op, outgoingAttrib):
        try:
            self.outgoingModifiers.remove((op, outgoingAttrib))
        except (TypeError, KeyError, ValueError):
            pass

    def GetOutgoingModifiers(self):
        return [ modifier for modifier in self.outgoingModifiers ]

    def CheckIntegrity(self):
        return True

    def Update(self):
        self.value = 0
        if self.isActive and self.incomingModifiers:
            self.value = self.selectBest((incoming.GetValue() for incoming in self.incomingModifiers))
        self.dirty = False

    def SetActive(self, newActive):
        if self.isActive != newActive:
            self.isActive = newActive
            self.MarkDirty()

    def GetBaseValue(self):
        return '<no base>'

    def GetValue(self):
        if self.dirty:
            self.Update()
        return self.value

    def MarkDirty(self):
        self.dirty = True
        for op, outgoing in self.outgoingModifiers:
            outgoing.MarkDirty()


def ApplyLocReqSkillModifier(dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib):
    skillID = modType[1]
    dogmaLM.AddLocationRequiredSkillModifierWithSource(op, toShipID, skillID, targetAttribID, fromFleetAttrib)


def RemoveLocReqSkillModifier(dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib):
    skillID = modType[1]
    dogmaLM.RemoveLocationRequiredSkillModifierWithSource(op, toShipID, skillID, targetAttribID, fromFleetAttrib)


def ApplyLocGrpSkillModifier(dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib):
    groupID = modType[1]
    dogmaLM.AddLocationGroupModifierWithSource(op, toShipID, groupID, targetAttribID, fromFleetAttrib)


def RemoveLocGrpSkillModifier(dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib):
    groupID = modType[1]
    dogmaLM.RemoveLocationGroupModifierWithSource(op, toShipID, groupID, targetAttribID, fromFleetAttrib)


def ApplyDirectModifier(dogmaLM, toShipID, targetAttribID, op, _modType, fromFleetAttrib):
    dogmaLM.AddModifierWithSource(op, toShipID, targetAttribID, fromFleetAttrib)


def RemoveDirectModifier(dogmaLM, toShipID, targetAttribID, op, _modType, fromFleetAttrib):
    dogmaLM.RemoveModifierWithSource(op, toShipID, targetAttribID, fromFleetAttrib)


getTargetAttribID = {'I': itemgetter(1),
 'LRS': itemgetter(2),
 'LG': itemgetter(2)}
ApplyBonus = {'I': ApplyDirectModifier,
 'LRS': ApplyLocReqSkillModifier,
 'LG': ApplyLocGrpSkillModifier}
RemoveBonus = {'I': RemoveDirectModifier,
 'LRS': RemoveLocReqSkillModifier,
 'LG': RemoveLocGrpSkillModifier}

class FleetBonusCell(object):

    def __init__(self, cellID, dogmaLM):
        self.dogmaLM = dogmaLM
        self.cellID = cellID
        self.members = set()
        self.booster = None
        self.parent = None
        self.children = {}
        self._active = True
        self.FBAs = {}

    def __str__(self):
        parentCellID = self.parent.cellID if self.parent else None
        return 'FleetBonusCell: <ID %s: Members %s: Children %s: ParentID %s>' % (self.cellID,
         len(self.members),
         len(self.children),
         parentCellID)

    def __repr__(self):
        return '<' + self.__str__() + ' at ' + '0x%x' % id(self) + '>'

    def AddNewChildCell(self, childCell):
        childCell.parent = self
        self.children[childCell.cellID] = childCell
        for FBA_Key, fleetAttrib in self.FBAs.iteritems():
            childCell.SetUpModifier_recurse(FBA_Key, fleetAttrib)

    def AlterMemberList(self, newMemberList):
        local_members = self.members
        toBeRemoved = self.members.copy()
        toBeAdded = []
        oldMemberLookupDict = {(m.characterID, m.shipID):m for m in self.members}
        for newMember in newMemberList:
            key = (newMember.characterID, newMember.shipID)
            if key in oldMemberLookupDict:
                toBeRemoved.remove(oldMemberLookupDict[key])
            elif newMember is not None:
                toBeAdded.append(newMember)

        for departingMember in toBeRemoved:
            self._RemoveMember(departingMember)

        for joiningMember in toBeAdded:
            self._AddMember(joiningMember)

    def RemoveUsingShipID(self, shipID):
        if self.booster is not None:
            if self.booster.shipID == shipID:
                self.RemoveCellBooster()
        for member in self.members:
            if shipID == member.shipID:
                self._RemoveMember(member)
                return

    @TimedFunction('FleetBonusCell::SetCellBooster')
    def SetCellBooster(self, booster, booster_modifiers):
        if booster is None:
            self.RemoveCellBooster()
            return
        self.booster = booster
        for modType, modInfoList in booster_modifiers.iteritems():
            for modInfo in modInfoList:
                self.SetUpModifier(modType, modInfo)

    @TimedFunction('FleetBonusCell::RemoveCellBooster')
    def RemoveCellBooster(self):
        removes = []
        for fleetBonusAttrib in self.FBAs.itervalues():
            for incomingAttrib in fleetBonusAttrib.incomingModifiers:
                if not isinstance(incomingAttrib, FleetBonusAttribute):
                    removes.append((fleetBonusAttrib, incomingAttrib))

        for fleetBonusAttrib, incomingAttrib in removes:
            fleetBonusAttrib.RemoveIncomingFleetBonus(incomingAttrib)
            incomingAttrib.RemoveOutgoingModifier(None, fleetBonusAttrib)

    def SetCellActive(self, isActive):
        self._active = isActive
        for FBA in self.FBAs.itervalues():
            FBA.SetActive(self._active)

    @TimedFunction('FleetBonusCell::SetUpModifier')
    def SetUpModifier(self, modType, modInfo):
        _rank, op, fromAttrib, _shipID = modInfo
        targetAttribID = getTargetAttribID[modType[0]](modType)
        FBA_Key = (modType, targetAttribID, op)
        self.SetUpModifier_recurse(FBA_Key, fromAttrib)

    def SetUpModifier_recurse(self, FBA_Key, fromAttrib):
        modType, targetAttribID, op = FBA_Key
        try:
            fleetAttrib = self.FBAs[FBA_Key]
            isExistingAttrib = True
        except KeyError:
            isExistingAttrib = False
            fleetAttrib = FleetBonusAttribute(modType[0], targetAttribID, op, self.cellID, self._active)
            self.FBAs[FBA_Key] = fleetAttrib

        fromAttrib.AddModifierTo(operation=None, toAttrib=fleetAttrib)
        if isExistingAttrib:
            return
        self._ApplyBonusToMembers(FBA_Key)
        for childCell in self.children.itervalues():
            childCell.SetUpModifier_recurse(FBA_Key, fleetAttrib)

    @TimedFunction('FleetBonusCell::TearDownModifier')
    def TearDownModifier(self, modType, modInfo):
        _rank, op, fromAttrib, _shipID = modInfo
        targetAttribID = getTargetAttribID[modType[0]](modType)
        key = (modType, targetAttribID, op)
        if key in self.FBAs:
            recvAttrib = self.FBAs[key]
            recvAttrib.RemoveIncomingFleetBonus(fromAttrib)
            fromAttrib.RemoveOutgoingModifier(None, recvAttrib)
        else:
            self.dogmaLM.LogError('FleetBonusCell::TearDownModifier : Cell %s trying to tear down a non existent modifier : %s' % (self.cellID, key))

    @TimedFunction('FleetBonusCell::RemoveFleetBonusTreeChild__ONLY_USED_BY_TESTS')
    def RemoveFleetBonusTreeChild__ONLY_USED_BY_TESTS(self, childCell):
        for child in childCell.children.itervalues():
            childCell.RemoveFleetBonusTreeChild__ONLY_USED_BY_TESTS(child)
            del self.children[childCell.cellID]

        self._RemoveExistingBonuses()
        removes = []
        for fleetAttrib in self.FBAs.itervalues():
            for recvAttrib in fleetAttrib.outgoingModifiers.copy():
                if isinstance(recvAttrib, FleetBonusAttribute):
                    removes.append((recvAttrib, fleetAttrib))

        for recvAttrib, fleetAttrib in removes:
            recvAttrib.RemoveIncomingFleetBonus(fleetAttrib)
            fleetAttrib.RemoveOutgoingModifier(None, recvAttrib)

        self.parent = None
        self.dogmaLM.LogInfo('RemoveFleetBonusTreeChild__ONLY_USED_BY_TESTS', childCell.cellID, self.cellID)

    def GetChild(self, childCellID):
        if childCellID in self.children:
            return self.children[childCellID]

    def _AddMember(self, newMember):
        if newMember not in self.members:
            self.members.add(newMember)
            self._ApplyBonusesToMember(newMember)

    def _RemoveMember(self, oldMember):
        if oldMember in self.members:
            self.members.remove(oldMember)
            self._RemoveBonusesFromMember(oldMember)

    def _ApplyExistingBonuses(self):
        for member in self.members:
            self._ApplyBonusesToMember(member)

    def _RemoveExistingBonuses(self):
        for member in self.members:
            self._RemoveBonusesFromMember(member)

    @TimedFunction('FleetBonusCell::_ApplyBonusToMembers')
    def _ApplyBonusToMembers(self, FBA_Key):
        modType, targetAttribID, op = FBA_Key
        fromFleetAttrib = self.FBAs[FBA_Key]
        for member in self.members:
            charID = member.characterID
            toShipID = member.shipID
            ApplyBonus[modType[0]](self.dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib)

    @TimedFunction('FleetBonusCell::_RemoveBonusFromMembers__NOT_USED')
    def _RemoveBonusFromMembers__NOT_USED(self, FBA_Key):
        modType, targetAttribID, op = FBA_Key
        fromFleetAttrib = self.FBAs[FBA_Key]
        for member in self.members:
            charID = member.characterID
            toShipID = member.shipID
            RemoveBonus[modType[0]](self.dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib)

    @TimedFunction('FleetBonusCell::_ApplyBonusesToMember')
    def _ApplyBonusesToMember(self, member):
        charID = member.characterID
        toShipID = member.shipID
        for (modType, targetAttribID, op), fromFleetAttrib in self.FBAs.iteritems():
            ApplyBonus[modType[0]](self.dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib)

    @TimedFunction('FleetBonusCell::_RemoveBonusesFromMember')
    def _RemoveBonusesFromMember(self, member):
        charID = member.characterID
        toShipID = member.shipID
        for (modType, targetAttribID, op), fromFleetAttrib in self.FBAs.iteritems():
            RemoveBonus[modType[0]](self.dogmaLM, toShipID, targetAttribID, op, modType, fromFleetAttrib)


class FleetBonusManagement(object):

    def __init__(self, dogmaLM):
        self.dogmaLM = dogmaLM
        self.broker = dogmaLM.broker
        self.locationID = dogmaLM.locationID
        self.gangModifiersByShip = {}
        self.gangRecsUnique = {}
        self.cellPathForShip = {}
        self.fleets = {}

    def __str__(self):
        return 'FleetBonusManagement location %d' % self.locationID

    @WrappedMethod
    def EvaluateFleetBonuses(self, fleetStructure, fleetID, wingID, squadID):
        if fleetID in self.fleets:
            fleetRootObject = self.fleets[fleetID]
        else:
            fleetRootObject = FleetBonusCell(fleetID, self.dogmaLM)
            self.fleets[fleetID] = fleetRootObject
        annotatedCellPath = [(fleetID, ''), (wingID, 'wings'), (squadID, 'squads')]
        self._EvaluateFleetBonuses(fleetStructure, annotatedCellPath, fleetRootObject)

    @TimedFunction('FleetBonusManagement::_EvaluateFleetBonuses')
    def _EvaluateFleetBonuses(self, fleetStructure, annotatedCellPath, fleetCellObject):
        cellPath = []
        fleetBonusCell = fleetCellObject
        structureCell = fleetStructure
        for cellID, cellLevelName in annotatedCellPath:
            cellPath.append(cellID)
            if cellID == -1:
                return
            fleetBonusCell, structureCell = self._GetCurrentCells(fleetBonusCell, cellID, cellPath, cellLevelName, structureCell)
            if fleetBonusCell is None:
                return
            if structureCell is not None:
                self._EvaluateCell(fleetBonusCell, cellPath, structureCell)
            else:
                self._EvaluateDeadCell(fleetBonusCell, cellPath)

    @WrappedMethod
    def _GetCurrentCells(self, fleetBonusCell, cellID, cellPath, cellLevelName, structureCell):
        if len(cellPath) > 1:
            if structureCell is not None:
                structureCell = structureCell.get(cellLevelName).get(cellID, None)
            _workCell = fleetBonusCell.GetChild(cellID)
            if _workCell is None and structureCell is not None:
                _workCell = FleetBonusCell(cellID, self.dogmaLM)
                fleetBonusCell.AddNewChildCell(_workCell)
            fleetBonusCell = _workCell
        return (fleetBonusCell, structureCell)

    @WrappedMethod
    def _EvaluateCell(self, fleetBonusCell, cellPath, structureCell):
        fleetBonusCell.SetCellActive(structureCell.isActive == 1)
        members = []
        if structureCell.leader is not None:
            members.append(structureCell.leader)
            self.cellPathForShip[structureCell.leader.shipID] = cellPath
        if structureCell.get('members') is not None:
            for member in structureCell.members.itervalues():
                members.append(member)
                self.cellPathForShip[member.shipID] = cellPath

        fleetBonusCell.AlterMemberList(members)
        if structureCell.booster is not None:
            if fleetBonusCell.booster != structureCell.booster:
                booster_modifiers = self.gangModifiersByShip.get(structureCell.booster.shipID, {})
                fleetBonusCell.SetCellBooster(structureCell.booster, booster_modifiers)
        else:
            fleetBonusCell.RemoveCellBooster()

    @WrappedMethod
    def _EvaluateDeadCell(self, fleetBonusCell, cellPath):
        fleetBonusCell.SetCellActive(False)
        self.broker.LogNotice('_EvaluateDeadCell: About to AlterMemberList to clear it. self.members =', fleetBonusCell.members)
        fleetBonusCell.AlterMemberList([])
        self.broker.LogNotice('_EvaluateDeadCell: MemberList cleared')
        fleetBonusCell.RemoveCellBooster()

    def FindFirstCellThatShipIsBoostingFor(self, shipID):
        if shipID in self.cellPathForShip:
            cellPath = self.cellPathForShip[shipID]
            fleetID = cellPath[0]
            if fleetID in self.fleets:
                fleetBonusCell = self.fleets[fleetID]
                if fleetBonusCell.booster is not None and shipID == fleetBonusCell.booster.shipID:
                    return fleetBonusCell
                for cellID in cellPath[1:]:
                    for _childID, fleetBonusCell in fleetBonusCell.children.iteritems():
                        if fleetBonusCell.cellID == cellID:
                            if fleetBonusCell.booster is not None and shipID == fleetBonusCell.booster.shipID:
                                return fleetBonusCell
                            break

    def FindShipsCell(self, shipID):
        if shipID in self.cellPathForShip:
            cellPath = self.cellPathForShip[shipID]
            fleetID = cellPath[0]
            if fleetID in self.fleets:
                fleetBonusCell = self.fleets[fleetID]
                for member in fleetBonusCell.members:
                    if shipID == member.shipID:
                        return fleetBonusCell

                for cellAddress in cellPath[1:]:
                    for _childID, fleetBonusCell in fleetBonusCell.children.iteritems():
                        if fleetBonusCell.cellID == cellAddress:
                            for member in fleetBonusCell.members:
                                if shipID == member.shipID:
                                    return fleetBonusCell

    def PreemptiveGangRemoval(self, shipID, suppress = False):
        fleetSliceRoot = self.FindShipsCell(shipID)
        if fleetSliceRoot is not None:
            fleetSliceRoot.RemoveUsingShipID(shipID)
            self.broker.LogNotice(self.locationID, 'PreemptiveGangRemoval : Ship removed.', shipID, 'cellID =', fleetSliceRoot.cellID)
        else:
            self.broker.LogInfo(self.locationID, 'PreemptiveGangRemoval : Ship not found.', shipID)

    def GenericAddRecord(self, shipID, operation, fromAttrib, k):
        k2 = k + (shipID, fromAttrib)
        if k2 in self.gangRecsUnique:
            self.broker.LogTraceback('%s: I already have a unique %s modifier %s' % (self.locationID, k[0], str(k2)))
            self.GenericRemoveRecord(shipID, fromAttrib, k)
        attributeValue = abs(fromAttrib.GetValue())
        rec = (attributeValue,
         operation,
         fromAttrib,
         shipID)
        self._InsertUniqueGangRec(shipID, k2, rec)
        self._InsertGangModifierByShip(shipID, k, rec)
        self.SetUpGangModifierIfBooster(shipID, k, rec)

    def GenericRemoveRecord(self, shipID, fromAttrib, k):
        k2 = k + (shipID, fromAttrib)
        if k2 not in self.gangRecsUnique:
            self.broker.LogTraceback("%s: I don't have unique %s modifier %s" % (self.locationID, k[0], str(k2)))
            return
        rec = self._RemoveUniqueGangRec(shipID, k2)
        gms = self.gangModifiersByShip.get(shipID, {})
        if k in gms:
            self.TearDownGangModifierIfBooster(shipID, k, rec)
            self._RemoveGangModifierByShip(shipID, k, rec)

    def AddGangRequiredSkillModifier(self, shipID, op, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attribute[fromAttribID]
        self.AddGangRequiredSkillModifierWithSource(shipID, op, skillID, toAttribID, fromAttrib)

    def AddGangRequiredSkillModifierWithSource(self, shipID, operation, skillID, toAttribID, fromAttrib):
        k = ('LRS', skillID, toAttribID)
        self.GenericAddRecord(shipID, operation, fromAttrib, k)

    def RemoveGangRequiredSkillModifier(self, shipID, operation, skillID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveGangRequiredSkillModifierWithSource(shipID, operation, skillID, toAttribID, fromAttrib)

    def RemoveGangRequiredSkillModifierWithSource(self, shipID, _operation, skillID, toAttribID, fromAttrib):
        k = ('LRS', skillID, toAttribID)
        self.GenericRemoveRecord(shipID, fromAttrib, k)

    def AddGangShipModifier(self, shipID, op, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddGangGroupModifierWithSource(shipID, op, toAttribID, fromAttrib)

    def AddGangShipModifierWithSource(self, shipID, operation, toAttribID, fromAttrib):
        k = ('I', toAttribID)
        self.GenericAddRecord(shipID, operation, fromAttrib, k)

    def RemoveGangShipModifier(self, shipID, op, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveGangRequiredSkillModifierWithSource(shipID, op, toAttribID, fromAttrib)

    def RemoveGangShipModifierWithSource(self, shipID, _operation, toAttribID, fromAttrib):
        k = ('I', toAttribID)
        self.GenericRemoveRecord(shipID, fromAttrib, k)

    def AddGangGroupModifier(self, shipID, op, groupID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attributes[fromAttribID]
        self.AddGangGroupModifierWithSource(shipID, op, groupID, toAttribID, fromAttrib)

    def AddGangGroupModifierWithSource(self, shipID, operation, groupID, toAttribID, fromAttrib):
        k = ('LG', groupID, toAttribID)
        self.GenericAddRecord(shipID, operation, fromAttrib, k)

    def RemoveGangGroupModifier(self, shipID, op, groupID, toAttribID, fromItemID, fromAttribID):
        fromAttrib = self.dogmaLM.dogmaItems[fromItemID].attributes[fromAttribID]
        self.RemoveGangGroupModifierWithSource(shipID, op, groupID, toAttribID, fromAttrib)

    def RemoveGangGroupModifierWithSource(self, shipID, _operation, groupID, toAttribID, fromAttrib):
        k = ('LG', groupID, toAttribID)
        self.GenericRemoveRecord(shipID, fromAttrib, k)

    def _InsertUniqueGangRec(self, shipID, k2, rec):
        self.gangRecsUnique[k2] = rec

    @TimedFunction('FleetBonusManagement::_RemoveUniqueGangRec')
    def _RemoveUniqueGangRec(self, shipID, k2):
        rec = self.gangRecsUnique[k2]
        del self.gangRecsUnique[k2]
        return rec

    def _InsertGangModifierByShip(self, shipID, k, rec):
        if shipID not in self.gangModifiersByShip:
            self.gangModifiersByShip[shipID] = {}
        gms = self.gangModifiersByShip[shipID]
        if k in gms:
            gms[k].append(rec)
        else:
            gms[k] = [rec]

    def _RemoveGangModifierByShip(self, shipID, k, rec):
        if shipID in self.gangModifiersByShip:
            gms = self.gangModifiersByShip[shipID]
            gms[k].remove(rec)
            if not len(gms[k]):
                del gms[k]
            if not len(gms):
                del self.gangModifiersByShip[shipID]

    def SetUpGangModifierIfBooster(self, shipID, k, rec):
        fleetSliceRoot = self.FindFirstCellThatShipIsBoostingFor(shipID)
        if fleetSliceRoot is not None:
            fleetSliceRoot.SetUpModifier(k, rec)

    def TearDownGangModifierIfBooster(self, shipID, k, rec):
        fleetSliceRoot = self.FindFirstCellThatShipIsBoostingFor(shipID)
        if fleetSliceRoot is not None:
            fleetSliceRoot.TearDownModifier(k, rec)

    @TimedFunction('fleetBonusMgr::ClearShipFromCell')
    def ClearShipFromCell(self, shipID):
        if shipID not in self.gangModifiersByShip:
            return
        self.broker.LogNotice("%s Ship %s hasn't been properly cleaned-up. Fixing now..." % (self.locationID, shipID))
        for k, records in self.gangModifiersByShip[shipID].iteritems():
            for rec in records:
                fromAttrib = rec[2]
                k2 = k + (shipID, fromAttrib)
                self.broker.LogNotice('%s Removing key %s, key2 %s, rec %s' % (self.locationID,
                 k,
                 k2,
                 rec))
                self._RemoveUniqueGangRec(shipID, k2)
                self.TearDownGangModifierIfBooster(shipID, k, rec)

        del self.gangModifiersByShip[shipID]
