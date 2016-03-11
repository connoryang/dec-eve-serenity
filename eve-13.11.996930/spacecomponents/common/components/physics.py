#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\components\physics.py
from spacecomponents.common.components.component import Component
from spacecomponents.common.componentConst import PHYSICS_CLASS

class Physics(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        Component.__init__(self, itemID, typeID, attributes, componentRegistry)
        self.isAlwaysGlobal = attributes.isAlwaysGlobal


def IsAlwaysGlobal(typeID):
    return cfg.spaceComponentStaticData.GetAttributes(typeID, PHYSICS_CLASS).isAlwaysGlobal
