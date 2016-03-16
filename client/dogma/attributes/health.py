#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\attributes\health.py
from dogma.const import attributeArmorHP, attributeArmorDamage, attributeShieldCharge, attributeShieldCapacity

def GetCurrentArmorRatio(dogmaLM, itemId):
    maxArmorHP = GetMaxArmorAmount(dogmaLM, itemId)
    currentArmorHP = GetCurrentArmorDamage(dogmaLM, itemId)
    currentArmorRatio = (maxArmorHP - currentArmorHP) / maxArmorHP
    return currentArmorRatio


def GetCurrentArmorDamage(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeArmorDamage)


def GetMaxArmorAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeArmorHP)


def GetCurrentShieldAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeShieldCharge)


def GetMaxShieldAmount(dogmaLM, itemId):
    return dogmaLM.GetAttributeValue(itemId, attributeShieldCapacity)


def GetCurrentShieldRatio(dogmaLM, itemId):
    return GetCurrentShieldAmount(dogmaLM, itemId) / GetMaxShieldAmount(dogmaLM, itemId)
