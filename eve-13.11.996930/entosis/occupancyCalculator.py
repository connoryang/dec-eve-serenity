#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\occupancyCalculator.py
MIN_OCCUPANCY_BONUS = 1.0
MAX_OCCUPANCY_BONUS = 6.0
MILITARY_INDEX_TO_BONUS = {1: 0.6,
 2: 1.2,
 3: 1.7,
 4: 2.1,
 5: 2.5}
INDUSTRIAL_INDEX_TO_BONUS = {1: 0.6,
 2: 1.2,
 3: 1.7,
 4: 2.1,
 5: 2.5}
STRATEGIC_INDEX_TO_BONUS = {1: 0.4,
 2: 0.6,
 3: 0.8,
 4: 0.9,
 5: 1.0}
CAPITAL_BONUS = 2.0
BASE_BONUS = 1.0

def GetOccupancyMultiplier(militaryIndex, industrialIndex, strategicIndex, isCapital):
    militaryBonus = MILITARY_INDEX_TO_BONUS.get(militaryIndex, 0.0)
    industrialBonus = INDUSTRIAL_INDEX_TO_BONUS.get(industrialIndex, 0.0)
    strategicBonus = STRATEGIC_INDEX_TO_BONUS.get(strategicIndex, 0.0)
    capitalBonus = CAPITAL_BONUS if isCapital else 0.0
    totalBonus = BASE_BONUS + militaryBonus + industrialBonus + strategicBonus + capitalBonus
    return 1.0 / max(MIN_OCCUPANCY_BONUS, min(MAX_OCCUPANCY_BONUS, totalBonus))
