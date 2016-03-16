#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\attribute.py
import dogma
from dogma.dogmaLogging import *
from characterskills.util import GetSkillLevelRaw
from dogma.attributes import CalculateHeat
import operator
import bisect
import math
import blue
import pytelemetry.zoning as zoning
import itertools
import dogma.const as const
import weakref
from ccpProfile import TimedFunction
OPERATOR_OFFSET = const.dgmOperatorOffset

def Seq(sequenceOrNone):
    if sequenceOrNone is None:
        return []
    return sequenceOrNone


class NewItemAttributeFactory():

    def __init__(self, item, dogmaLocation, staticMgr, baseAttributes):
        self.dogmaLocation = dogmaLocation
        self.staticMgr = staticMgr
        self.attributes = baseAttributes
        self.item = weakref.proxy(item)

    def GetAttributeInstance(self, attrID):
        staticAttr = self.staticMgr.attributes[attrID]
        baseValue = None
        if self.attributes and attrID in self.attributes:
            baseValue = self.attributes[attrID]
        if attrID == const.attributeSkillLevel:
            return SkillLevelAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif attrID in self.staticMgr.chargedAttributes:
            return ChargedAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif attrID in [const.attributeHeatHi, const.attributeHeatMed, const.attributeHeatLow]:
            return HeatAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        elif not staticAttr.stackable:
            return StackingNurfedAttribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)
        else:
            return Attribute(attrID, baseValue, self.item, self.dogmaLocation, staticAttr)


class AttributeInterface(object):

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<' + self.__str__() + ' at ' + '0x%x' % id(self) + '>'

    def friendlyStr(self):
        return str(self)

    def performantStr(self):
        return str(self)

    def AddModifierTo(self, operation, toAttrib):
        self.AddOutgoingModifier(operation, toAttrib)
        toAttrib.AddIncomingModifier(operation, self)

    def RemoveModifierTo(self, operation, toAttrib):
        self.RemoveOutgoingModifier(operation, toAttrib)
        toAttrib.RemoveIncomingModifier(operation, self)

    def GetIncomingModifiers(self):
        return []

    def GetOutgoingModifiers(self):
        return []

    def RemoveAllModifiers(self):
        pass

    def IsAnOrphan(self):
        return False

    def CheckIntegrity(self):
        if self.IsAnOrphan():
            LogWarn("CheckIntegrity: 'Orphan' Attribute detected (its dogmaItem has gone!):", self)
            TraceReferrers(self, depthLimit=6)
            LogTraceback('Orphan Attribute!')
            return False
        else:
            return True

    def GetBaseValue(self):
        return '<no base value reported>'

    def GetValue(self):
        return '<no value reported>'


class Attribute(AttributeInterface):

    def __str__(self):
        return self.performantStr()

    def performantStr(self):
        try:
            itemID = self.item.itemID
            itemClass = self.item.__class__.__name__
            itemAddress = id(self.item)
        except ReferenceError:
            itemID = self.invItem.itemID
            itemClass = 'UNLOADED-ITEM'
            itemAddress = '[GONE]'

        attribID = self.attribID
        attributeClass = self.__class__.__name__
        invItemCategoryID = self.invItem.categoryID
        invItemGroupID = self.invItem.groupID
        invItemTypeID = self.invItem.typeID
        return "'{attribID}' ({attributeClass}) on '{invItemCategoryID} / {invItemTypeID}' ({itemClass} {itemID}) ".format(**locals())

    def friendlyStr(self):
        try:
            itemID = self.item.itemID
            itemClass = self.item.__class__.__name__
            itemAddress = id(self.item)
        except ReferenceError:
            itemID = self.invItem.itemID
            itemClass = 'UNLOADED-ITEM'
            itemAddress = '[GONE]'

        attribID = self.attribID
        attributeName = cfg.dgmattribs[attribID].attributeName
        attributeClass = self.__class__.__name__
        invItemCategoryName = GetCategoryNameFromID(self.invItem.categoryID)
        invItemGroupName = GetGroupNameFromID(self.invItem.groupID)
        invItemTypeName = GetTypeNameFromID(self.invItem.typeID)
        numIncoming = self.CountIncomingModifiers()
        numOutgoing = self.CountOutgoingModifiers()
        return "'{attributeName}' ({attributeClass}) on '{invItemCategoryName} / {invItemTypeName}' ({itemClass} {itemID}) [i{numIncoming}:o{numOutgoing}] ".format(**locals())

    def printInvItemDetails(self, itemClass):
        print 'START INV ITEM DETAILS:'
        print
        try:
            i = self.invItem
            print 'invItem:', i
            print 'type:', type(i)
            print 'columns:', i.__columns__
            print
            for a in ['itemID',
             'typeID',
             'ownerID',
             'locationID',
             'flagID',
             'quantity',
             'groupID',
             'categoryID',
             'customInfo',
             'stacksize',
             'singleton']:
                print a, getattr(i, a)

            print
            print 'Underlying item:', self.item
            print
            print 'class:', itemClass
        except:
            print "*** OUCH. THAT DIDN'T WORK! ***"

        print
        print 'END INV ITEM DETAILS'
        print

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        self.attribID = attribID
        self.item = dogmaItem
        self.dogmaLM = dogmaLM
        self.invItem = dogmaItem.invItem
        if attribID is not None:
            self.typeValue = dogmaLM.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.invItem.typeID, attribID)
        else:
            self.typeValue = baseValue
        if baseValue is None:
            baseValue = self.typeValue
        self.baseValue = baseValue
        self.incomingModifiers = None
        self._outgoingModifiers = None
        self.nonModifyingDependants = None
        self._onChangeCallbacks = None
        self.highIsGood = staticAttr.highIsGood
        self.category = staticAttr.attributeCategory
        self.currentValue = self.baseValue
        self.dirty = False
        if staticAttr.maxAttributeID:
            self.capAttrib = weakref.proxy(dogmaItem.attributes[staticAttr.maxAttributeID])
            self.capAttrib.AddNonModifyingDependant(self)
        else:
            self.capAttrib = None
        self._PickUpInitialModifiers(dogmaItem)
        try:
            pass
        except:
            LogNotice('Exception thrown when logging InitAttr!')

    def IsAnOrphan(self):
        try:
            testWhetherItemIsStillValid = self.item.invItem
            return False
        except ReferenceError:
            return True

    def _PickUpInitialModifiers(self, dogmaItem):
        location = dogmaItem.GetLocation()
        if location:
            location._PickUpInitialModifiersFromLocationTo(self)
        pilotID = dogmaItem.GetPilot()
        ownerItem = self.dogmaLM.dogmaItems.get(pilotID, None)
        if ownerItem and self.item.IsOwnerModifiable():
            ownerItem._PickUpInitialModifiersFromOwnerTo(self)

    def Update(self):
        prevValue = self.currentValue
        capVal = None
        if self.capAttrib:
            capVal = self.capAttrib.GetValue()
            val = self.baseValue = min(self.baseValue, capVal)
        else:
            val = self.baseValue
        val = self._ApplyModifierOperationsToVal(val)
        if capVal is not None:
            val = min(val, capVal)
        if self.category in (10, 11, 12):
            val = int(val)
        if self.attribID in (const.attributeCpuLoad,
         const.attributePowerLoad,
         const.attributePowerOutput,
         const.attributeCpuOutput,
         const.attributeCpu,
         const.attributePower):
            val = round(val, 2)
        self.currentValue = val
        self.dirty = False
        self._PerformCallbacksIfValueChanged(prevValue)

    def _ApplyModifierOperationsToVal(self, val):
        if self.incomingModifiers:
            for idx, mods in enumerate(self.incomingModifiers):
                dogmaOperator = const.dgmOperators[idx - const.dgmOperatorOffset]
                for modAttrib in mods:
                    val = dogmaOperator(val, modAttrib.GetValue())

        return val

    def GetValue(self):
        if self.dirty:
            self.Update()
        return self.currentValue

    def MarkDirty(self, silent = False):
        self.dirty = True
        for op, nowDirtyAttrib in list(Seq(self._outgoingModifiers)):
            nowDirtyAttrib().MarkDirty()

        for nowDirtyAttrib in Seq(self.nonModifyingDependants):
            nowDirtyAttrib.MarkDirty()

        if silent:
            return
        ownerID = None
        if True:
            try:
                ownerID = self.item.ownerID
            except AttributeError:
                LogError('Attribute {} has no `ownerID` on its `item`, just: {}'.format(self, sorted(vars(self.item))))

        if self.attribID in self.dogmaLM.attributeChangeCallbacksByAttributeID and not self.dogmaLM.IsIgnoringOwnerEvents(ownerID):
            try:
                oldValue = self.currentValue
                newValue = self.GetValue()
                self.dogmaLM.attributeChangeCallbacksByAttributeID[self.attribID](self.attribID, self.item.itemID, newValue, oldValue)
            except Exception:
                LogException('Error broadcasting attribute change {}'.format(self.dogmaLM.attributeChangeCallbacksByAttributeID[self.attribID]))

        if dogma.IsClient():
            return
        if not self.dogmaLM.IsIgnoringOwnerEvents(ownerID):
            try:
                if self.attribID is not None:
                    self.dogmaLM.msgMgr.AddAttribute(self)
            except Exception:
                LogException('Error broadcasting attribute change')

    def AddCallbackForChanges(self, func, params):
        if self._onChangeCallbacks is None:
            self._onChangeCallbacks = {}
        self._onChangeCallbacks[func] = params

    def RemoveCallbackForChanges(self, func):
        del self._onChangeCallbacks[func]
        if not self._onChangeCallbacks:
            self._onChangeCallbacks = None

    def _PerformCallbacksIfValueChanged(self, prevValue):
        if self._onChangeCallbacks is None:
            return
        if prevValue != self.currentValue:
            for func, params in self._onChangeCallbacks.iteritems():
                func(self, prevValue, self.currentValue, *params)

    def ConstructMessage(self):
        try:
            if self.item.ownerID is None:
                return
        except ReferenceError:
            return

        clientID = self.item.FindClientID('charid', [self.item.ownerID])
        if clientID is not None:
            newValue = self.GetValue()
            try:
                oldValue = self.clientSideValue
                if oldValue == newValue:
                    return
            except AttributeError:
                oldValue = newValue

            self.clientSideValue = newValue
            if not self.dogmaLM.IsIgnoringOwnerEvents(self.item.ownerID):
                return (clientID, ('OnModuleAttributeChange',
                  self.item.ownerID,
                  self.item.itemID,
                  self.attribID,
                  blue.os.GetSimTime(),
                  newValue,
                  oldValue,
                  blue.os.GetWallclockTime()))
        else:
            return

    def _makeEmptyIncomingModifiers(self):
        return tuple((set() for x in xrange(const.dgmNumOperators)))

    def _initIncomingModifiers(self):
        self.incomingModifiers = self._makeEmptyIncomingModifiers()

    @WrappedMethod
    def AddIncomingModifier(self, op, attribute):
        if self.incomingModifiers is None:
            self._initIncomingModifiers()
        opIndex = op + OPERATOR_OFFSET
        self.incomingModifiers[opIndex].add(attribute)
        self.MarkDirty()

    @WrappedMethod
    def RemoveIncomingModifier(self, op, attribute):
        opIndex = op + OPERATOR_OFFSET
        try:
            self.incomingModifiers[opIndex].remove(attribute)
            self.MarkDirty()
        except (TypeError,
         IndexError,
         KeyError,
         ValueError):
            return

        if self.incomingModifiers is None:
            return
        if not any(self.incomingModifiers):
            self.incomingModifiers = None

    def GetIncomingModifiers(self):
        if self.incomingModifiers is None:
            return []
        result = []
        for opIdx, attribSet in enumerate(self.incomingModifiers):
            result.extend(((opIdx - OPERATOR_OFFSET, attrib) for attrib in attribSet))

        return result

    def CountIncomingModifiers(self):
        return len(self.GetIncomingModifiers())

    def AddNonModifyingDependant(self, attribute):
        if self.nonModifyingDependants is None:
            self.nonModifyingDependants = set()
        self.nonModifyingDependants.add(attribute)
        attribute.MarkDirty(silent=True)

    def _makeEmptyOutgoingModifiers(self):
        return set()

    def _initOutgoingModifiers(self):
        self._outgoingModifiers = self._makeEmptyOutgoingModifiers()

    @WrappedMethod
    def AddOutgoingModifier(self, op, attribute):
        if self._outgoingModifiers is None:
            self._initOutgoingModifiers()
        weak = weakref.ref(attribute)
        self._outgoingModifiers.add((op, weak))

    @WrappedMethod
    def RemoveOutgoingModifier(self, op, attribute):
        weak = weakref.ref(attribute)
        try:
            self._outgoingModifiers.remove((op, weak))
        except (AttributeError, KeyError, ValueError):
            return

        if not any(self._outgoingModifiers):
            self._outgoingModifiers = None

    def GetOutgoingModifiers(self):
        if self._outgoingModifiers is None:
            return []
        return [ (opIdx, attrib_weakref()) for opIdx, attrib_weakref in self._outgoingModifiers ]

    def CountOutgoingModifiers(self):
        return len(self.GetOutgoingModifiers())

    def RemoveAllModifiers(self):
        for operator, incomingAttrib in self.GetIncomingModifiers():
            incomingAttrib.RemoveOutgoingModifier(operator, self)

        for operator, outgoingAttrib in self.GetOutgoingModifiers():
            outgoingAttrib.RemoveIncomingModifier(operator, self)

        self._DiscardAllModifiers()

    def _DiscardAllModifiers(self):
        self.incomingModifiers = None
        self._outgoingModifiers = None

    def GetBaseValue(self):
        return self.baseValue

    def SetBaseValue(self, newBaseValue):
        if self.baseValue != newBaseValue:
            self.baseValue = newBaseValue
            self.MarkDirty()

    def ResetBaseValue(self):
        if self.baseValue != self.typeValue:
            self.baseValue = self.typeValue
            self.MarkDirty()

    def IncreaseBaseValue(self, addAmount):
        if not self.item.CanAttributeBeModified():
            return
        self.baseValue += addAmount
        self.MarkDirty()

    def DecreaseBaseValue(self, decAmount):
        if not self.item.CanAttributeBeModified():
            return
        self.baseValue -= decAmount
        self.MarkDirty()

    def GetModifyingItems(self):
        modifyingItems = set()
        if self.incomingModifiers is None:
            return modifyingItems
        for srcAttrib in itertools.chain(*self.incomingModifiers):
            if srcAttrib.item is not None:
                modifyingItems.add(srcAttrib.item.itemID)

        return modifyingItems

    def GetPersistData(self):
        if self.baseValue != self.typeValue:
            return self.baseValue
        else:
            return None

    @zoning.ZONE_METHOD
    def ApplyPersistData(self, pData):
        self.SetBaseValue(pData)


class SkillLevelAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(SkillLevelAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        self.skillTimeConstant = dogmaLM.dogmaStaticMgr.GetTypeAttribute2(dogmaItem.invItem.typeID, const.attributeSkillTimeConstant)
        self.skillPointAttribute = weakref.ref(self.item.attributes[const.attributeSkillPoints])
        self.skillPointAttribute().AddNonModifyingDependant(self)

    def Update(self):
        prevValue = self.currentValue
        if self.skillPointAttribute() is not None:
            self.currentValue = GetSkillLevelRaw(self.skillPointAttribute().GetValue(), self.skillTimeConstant)
        self.dirty = False
        self._PerformCallbacksIfValueChanged(prevValue)

    def AddIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a skill level!')

    def RemoveIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a skill level!')


class ChargedAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(ChargedAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        self.rechargeRateAttribute = weakref.proxy(self.item.attributes[staticAttr.chargeRechargeTimeID])
        capVal = self.capAttrib.GetValue()
        self.currentValue = min(capVal, self.currentValue)
        self.prevCap = capVal
        self.lastCalcTime = blue.os.GetSimTime()
        self.rechargeRate = self.rechargeRateAttribute.GetValue() / 5.0
        self.rechargeRateAttribute.AddNonModifyingDependant(self)

    def Update(self):
        capVal = self.capAttrib.GetValue()
        self.rechargeRate = self.rechargeRateAttribute.GetValue() / 5.0
        rechargeDelayFactor = self.rechargeRate
        if capVal == 0:
            self.currentValue = 0
            self.prevCap = 0
            return
        if capVal != self.prevCap:
            if self.prevCap > 0:
                oldRatio = self.currentValue / self.prevCap
                self.currentValue = oldRatio * capVal
            self.prevCap = capVal
        if capVal <= self.currentValue:
            self.currentValue = capVal
            return
        if rechargeDelayFactor == 0:
            self.lastCalcTime = blue.os.GetSimTime()
            return
        currentTime = blue.os.GetSimTime()
        timeDiff_ms = (currentTime - self.lastCalcTime) / float(const.dgmTauConstant)
        if timeDiff_ms < -0.0001:
            return
        oldRatio = self.currentValue / capVal
        root = math.sqrt(oldRatio)
        rootBlendFactor = math.exp(-timeDiff_ms / rechargeDelayFactor)
        rootBlended = (root - 1.0) * rootBlendFactor + 1.0
        newRatio = rootBlended ** 2
        self.currentValue = newRatio * capVal
        self.lastCalcTime = currentTime

    def GetValue(self):
        if self.dirty or self.lastCalcTime != blue.os.GetSimTime():
            self.Update()
        return self.currentValue

    def GetFullChargedInfo(self):
        if self.dirty or self.lastCalcTime != blue.os.GetSimTime():
            self.Update()
        return (self.currentValue, self.prevCap, self.rechargeRate)

    def MarkDirty(self, silent = False):
        super(ChargedAttribute, self).MarkDirty(silent)
        if not silent:
            self.Update()

    def SetBaseValue(self, newBaseValue):
        if self.currentValue != newBaseValue:
            self.currentValue = newBaseValue
            self.lastCalcTime = blue.os.GetSimTime()
            self.MarkDirty()

    def AddIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a charged attribute!')

    def RemoveIncomingModifier(self, op, attribute):
        LogTraceback('Cannot modify a charged attribute!')

    def ResetBaseValue(self):
        self.Update()
        self.currentValue = self.typeValue

    def IncreaseBaseValue(self, addAmount):
        self.Update()
        self.currentValue += addAmount

    def DecreaseBaseValue(self, decAmount):
        self.Update()
        self.currentValue -= decAmount

    def GetPersistData(self):
        self.Update()
        return self.currentValue


class HeatAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        super(HeatAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)
        dissipationAttributeByHeatID = {const.attributeHeatHi: const.attributeHeatDissipationRateHi,
         const.attributeHeatMed: const.attributeHeatDissipationRateMed,
         const.attributeHeatLow: const.attributeHeatDissipationRateLow}
        heatCapacityByHeatID = {const.attributeHeatHi: const.attributeHeatCapacityHi,
         const.attributeHeatMed: const.attributeHeatCapacityMed,
         const.attributeHeatLow: const.attributeHeatCapacityLow}
        self.heatGenerationMultiplierAttribute = weakref.proxy(self.item.attributes[const.attributeHeatGenerationMultiplier])
        self.capAttrib = weakref.proxy(self.item.attributes[heatCapacityByHeatID[attribID]])
        self.heatDissipationRateAttribute = weakref.proxy(self.item.attributes[dissipationAttributeByHeatID[attribID]])
        capVal = self.capAttrib.GetValue()
        self.currentValue = min(capVal, self.currentValue)
        self.prevCap = capVal
        self.lastCalcTime = blue.os.GetSimTime()
        self.incomingHeat = Attribute(None, 0, dogmaItem, dogmaLM, staticAttr)

    def Update(self):
        currentTime = blue.os.GetSimTime()
        timeDiff = (currentTime - self.lastCalcTime) / float(const.dgmTauConstant)
        incHeat = self.incomingHeat.GetValue()
        self.currentValue = CalculateHeat(self.currentValue, timeDiff, incHeat, self.heatDissipationRateAttribute.GetValue(), self.heatGenerationMultiplierAttribute.GetValue(), self.capAttrib.GetValue())
        self.dirty = False
        self.lastCalcTime = currentTime
        return self.currentValue

    def GetValue(self):
        if self.dirty or self.lastCalcTime != blue.os.GetSimTime():
            self.Update()
        return self.currentValue

    def GetFullHeatInfo(self):
        if self.dirty or self.lastCalcTime != blue.os.GetSimTime():
            self.MarkDirty()
            self.Update()
        return (self.currentValue, self.lastCalcTime, self.capAttrib.GetValue())

    def GetHeatMessage(self):
        if self.dirty or self.lastCalcTime != blue.os.GetSimTime():
            self.MarkDirty()
            self.Update()
        return (self.currentValue,
         self.capAttrib.currentValue,
         self.incomingHeat.GetValue(),
         self.heatGenerationMultiplierAttribute.currentValue,
         self.heatDissipationRateAttribute.currentValue,
         self.lastCalcTime)

    def SetBaseValue(self, newBaseValue, asPercentage = False):
        if self.currentValue != newBaseValue:
            if asPercentage:
                newBaseValue *= self.currentValue
            self.currentValue = newBaseValue
            self.lastCalcTime = blue.os.GetSimTime()
            self.MarkDirty()

    def AddIncomingModifier(self, op, attribute):
        self.Update()
        self.incomingHeat.AddIncomingModifier(op, attribute)

    def RemoveIncomingModifier(self, op, attribute):
        self.Update()
        self.incomingHeat.RemoveIncomingModifier(op, attribute)

    def ResetBaseValue(self):
        self.Update()
        self.currentValue = self.typeValue

    def IncreaseBaseValue(self, addAmount):
        self.Update()
        self.currentValue += addAmount

    def DecreaseBaseValue(self, decAmount):
        self.Update()
        self.currentValue -= decAmount

    def GetPersistData(self):
        self.Update()
        return self.currentValue


NurfDenoms = [ math.exp((i / 2.67) ** 2.0) for i in xrange(10) ]

def StackingOperator(valueDenomTuple):
    return (valueDenomTuple[0] - 1.0) * (1.0 / valueDenomTuple[1]) + 1.0


class StackingNurfedAttribute(Attribute):

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        self.unnurfedMods = None
        self.nurfedMods = None
        super(StackingNurfedAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)

    def _initIncomingUnNurfedModifiers(self):
        self.unnurfedMods = self._makeEmptyIncomingModifiers()

    def _initIncomingNurfedModifiers(self):
        self.nurfedMods = self._makeEmptyIncomingModifiers()

    def AddIncomingModifier(self, op, attribute):
        if self._ShouldNotNurf(op, attribute):
            if self.unnurfedMods is None:
                self._initIncomingUnNurfedModifiers()
            self.unnurfedMods[op + OPERATOR_OFFSET].add(attribute)
        else:
            if self.nurfedMods is None:
                self._initIncomingNurfedModifiers()
            self.nurfedMods[op + OPERATOR_OFFSET].add(attribute)
        super(StackingNurfedAttribute, self).AddIncomingModifier(op, attribute)

    def RemoveIncomingModifier(self, op, attribute):
        try:
            doNotNurf = self._ShouldNotNurf(op, attribute)
            if doNotNurf:
                self.unnurfedMods[op + OPERATOR_OFFSET].remove(attribute)
                if not any(self.unnurfedMods):
                    self.unnurfedMods = None
            else:
                self.nurfedMods[op + OPERATOR_OFFSET].remove(attribute)
                if not any(self.nurfedMods):
                    self.nurfedMods = None
        except:
            pass

        super(StackingNurfedAttribute, self).RemoveIncomingModifier(op, attribute)

    def _ShouldNotNurf(self, op, attribute):
        if op not in (const.dgmAssPreMul,
         const.dgmAssPostMul,
         const.dgmAssPostPercent,
         const.dgmAssPreDiv,
         const.dgmAssPostDiv):
            return True
        try:
            if attribute.item is not None and attribute.item.invItem.categoryID in const.dgmUnnerfedCategories:
                return True
        except ReferenceError:
            LogWarn("_ShouldNotNurf: 'Orphan' Attribute detected (its dogmaItem has gone!):", attribute)
            LogWarn('referrers are:')
            TraceReferrers(self)

        if hasattr(attribute, 'forceUnnurfed') and attribute.forceUnnurfed:
            return True
        return False

    def _ApplyModifierOperationsToVal(self, val):
        unnurfedMods = self.unnurfedMods if self.unnurfedMods else self._makeEmptyIncomingModifiers()
        nurfedMods = self.nurfedMods if self.nurfedMods else self._makeEmptyIncomingModifiers()
        for idx, (unnurfedMods, nurfedMods) in enumerate(zip(unnurfedMods, nurfedMods)):
            dogmaOperator = const.dgmOperators[idx - const.dgmOperatorOffset]
            for modAttrib in unnurfedMods:
                val = dogmaOperator(val, modAttrib.GetValue())

            if len(nurfedMods) <= 1:
                for modAttrib in nurfedMods:
                    val = dogmaOperator(val, modAttrib.GetValue())

            else:
                factors = sorted([ dogmaOperator(1, modAttrib.GetValue()) for modAttrib in nurfedMods ])
                splitPoint = bisect.bisect(factors, 1.0)
                denoms = itertools.chain(NurfDenoms[:splitPoint], reversed(NurfDenoms[:len(factors) - splitPoint]))
                val *= reduce(operator.mul, map(StackingOperator, zip(factors, denoms)))

        return val


class LiteralAttribute(AttributeInterface):

    def __init__(self, value):
        self.value = value
        self.item = None

    def __str__(self):
        return 'LiteralAttribute value %s' % self.value

    def GetBaseValue(self):
        return self.value

    def GetValue(self):
        return self.value

    def AddOutgoingModifier(self, op, attribute):
        pass

    def RemoveOutgoingModifier(self, op, attribute):
        pass

    def CheckIntegrity(self):
        return True


class BrainLiteralAttribute(LiteralAttribute):

    def __init__(self, value):
        self.skills, value = value
        super(BrainLiteralAttribute, self).__init__(value)
        self.forceUnnurfed = True
        self.noPropagation = True

    def __str__(self):
        skills = [ GetTypeNameFromID(x) for x in self.skills ]
        return 'BrainLiteralAttribute value %s from skills %s' % (self.value, skills)
