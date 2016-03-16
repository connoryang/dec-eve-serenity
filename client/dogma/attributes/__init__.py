#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\__init__.py
import math

def GetAttribute(attributeID):
    return cfg.dgmattribs.Get(attributeID)


def GetDisplayName(attributeID):
    attribute = GetAttribute(attributeID)
    return attribute.displayName or attribute.attributeName


def GetIconID(attributeID):
    return GetAttribute(attributeID).iconID


def GetName(attributeID):
    return GetAttribute(attributeID).attributeName


def CalculateHeat(currentHeat, timeDiff, incomingHeat, dissipationRate, heatGenerationMul, heatCap):
    if incomingHeat < 5e-08:
        currentHeat *= math.exp(-timeDiff / 1000 * dissipationRate)
        if round(currentHeat, 0) <= 0:
            currentHeat = 0.0
    else:
        hgm = heatGenerationMul
        hc = heatCap
        currentHeat = hc - hc * math.exp(-timeDiff / 1000 * incomingHeat * hgm) + currentHeat * math.exp(-timeDiff / 1000 * incomingHeat * hgm)
    return currentHeat
