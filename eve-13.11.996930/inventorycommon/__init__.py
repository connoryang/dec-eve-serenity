#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\inventorycommon\__init__.py
from const import ixSingleton, flagHiddenModifers

def IsBecomingSingleton(change):
    if ixSingleton in change:
        old_singleton, new_singleton = change[ixSingleton]
        if not old_singleton and new_singleton:
            return True
    return False


def ItemIsVisible(item):
    return item.flagID != flagHiddenModifers
