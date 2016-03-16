#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\characterskills\attribute.py
import dogma.const
import gametime
ATTRIBUTEBONUS_BY_ATTRIBUTEID = {dogma.const.attributePerception: dogma.const.attributePerceptionBonus,
 dogma.const.attributeMemory: dogma.const.attributeMemoryBonus,
 dogma.const.attributeWillpower: dogma.const.attributeWillpowerBonus,
 dogma.const.attributeIntelligence: dogma.const.attributeIntelligenceBonus,
 dogma.const.attributeCharisma: dogma.const.attributeCharismaBonus}

def IsBoosterExpiredThen(timeOffset, boosterExpiryTime):
    return boosterExpiryTime <= gametime.GetWallclockTime() + timeOffset


def FindAttributeBooster(dogmaIM, boosters):
    for b in boosters:
        boosterness = dogmaIM.GetTypeAttribute2(b.typeID, dogma.const.attributeBoosterness)
        if boosterness == 4.0:
            return b


def GetBoosterlessValue(dogmaIM, typeID, attributeID, currentValue):
    effectID = ATTRIBUTEBONUS_BY_ATTRIBUTEID[attributeID]
    boosterEffect = dogmaIM.GetTypeAttribute2(typeID, effectID)
    newValue = currentValue - boosterEffect
    return newValue
