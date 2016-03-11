#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\notWantedDogmaItem.py
from dogma.items.baseDogmaItem import BaseDogmaItem
RESISTANCEMATRIX = {const.attributeShieldCharge: [0,
                               0,
                               0,
                               0],
 const.attributeArmorDamage: [0,
                              0,
                              0,
                              0],
 const.attributeDamage: [0,
                         0,
                         0,
                         0]}

class NotWantedDogmaItem(BaseDogmaItem):

    def CanAttributeBeModified(self):
        return False

    def GetResistanceMatrix(self):
        return RESISTANCEMATRIX
