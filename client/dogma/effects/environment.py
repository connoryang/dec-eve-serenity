#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\environment.py
from dogma.const import effectUseMissiles, effectWarpDisruptSphere, effectOrbitalStrike
from inventorycommon.const import orbitalStrikeAmmo
from dogma.effects import GetEwarTypeByEffectID

class Environment:
    itemID = None
    charID = None
    shipID = None
    targetID = None
    targetIDs = None
    otherID = None
    effectID = None
    startTime = None
    currentStartTime = None
    currentSeed = None
    iterationSuccess = None
    random = None
    shipGroupID = None
    shipCategoryID = None
    targetTypeID = None
    otherTypeID = None
    itemTypeID = None
    graphicInfo = None
    unexpectedStop = False
    actualEffectID = None

    def __init__(self, itemID, charID, shipID, targetID, otherID, effectID, dogmaLM, expressionID):
        self.effectID = effectID
        self.dogmaLM = dogmaLM
        self.expressionID = expressionID
        self.slaves = None
        self.graphicInfo = None
        if itemID:
            self.itemID = itemID
            if type(itemID) is tuple:
                self.itemTypeID = itemID[2]
            elif isinstance(itemID, basestring):
                self.itemTypeID = int(itemID.split('_')[1])
            else:
                self.itemTypeID = dogmaLM.GetItem(itemID).typeID
        if charID:
            self.charID = charID
        if shipID:
            self.shipID = shipID
            item = dogmaLM.GetItem(shipID)
            self.shipGroupID = item.groupID
            self.shipCategoryID = item.categoryID
        if targetID:
            self.targetID = targetID
            self.targetTypeID = dogmaLM.GetItem(targetID).typeID
        if otherID:
            self.otherID = otherID
            if type(otherID) is tuple:
                self.otherTypeID = otherID[2]
            elif isinstance(otherID, basestring):
                self.itemTypeID = otherID.split('_')[1]
            else:
                self.otherTypeID = dogmaLM.GetItem(otherID).typeID
        self.actualEffectID = effectID
        if effectID in (effectUseMissiles, effectWarpDisruptSphere) and self.otherTypeID is not None:
            defEffectID = dogmaLM.dogmaStaticMgr.defaultEffectByType.get(self.otherTypeID)
            if defEffectID is not None:
                self.actualEffectID = defEffectID
        if self.otherTypeID in orbitalStrikeAmmo:
            self.actualEffectID = effectOrbitalStrike

    def Line(self):
        return [self.itemID,
         self.charID,
         self.shipID,
         self.targetID,
         self.otherID,
         [],
         self.effectID]

    def UpdateOtherID(self, otherID):
        self.otherID = otherID
        if type(otherID) is tuple:
            self.otherTypeID = otherID[2]
        else:
            self.otherTypeID = self.dogmaLM.inventory2.GetItem(otherID).typeID

    def Effect(self):
        return self.dogmaLM.broker.effects[self.effectID]

    def OnStart(self, effect, t):
        if self.currentStartTime is None:
            if effect.rangeChance or effect.electronicChance or effect.propulsionChance:
                self.jammingType = GetEwarTypeByEffectID(self.effectID)
        self.currentStartTime = t

    def __repr__(self):
        return ' ItemID: %s, EffectID: %s, CharID: %s, ShipID: %s, TargetID: %s, OtherID: %s' % (self.itemID,
         self.effectID,
         self.charID,
         self.shipID,
         self.targetID,
         self.otherID)


class BrainEnvironment(Environment):

    def __init__(self, itemID, charID, shipID, targetID, otherID, effectID, dogmaLM, expressionID):
        self.effectID = effectID
        self.dogmaLM = dogmaLM
        self.expressionID = expressionID
        self.slaves = None
        self.graphicInfo = None
        self.itemID = itemID
        self.itemTypeID = dogmaLM.GetItem(itemID).typeID
        if charID:
            self.charID = charID
        if shipID:
            self.shipID = shipID
            item = dogmaLM.GetItem(shipID)
            self.shipGroupID = item.groupID
            self.shipCategoryID = item.categoryID
        if targetID:
            self.targetID = targetID
            self.targetTypeID = dogmaLM.GetItem(targetID).typeID
        if otherID:
            self.otherID = otherID
            if type(otherID) is tuple:
                self.otherTypeID = otherID[2]
            else:
                self.otherTypeID = dogmaLM.GetItem(otherID).typeID
        self.actualEffectID = effectID
