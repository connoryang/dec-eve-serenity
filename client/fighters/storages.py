#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fighters\storages.py
import collections
import fsdlite

def AbilityStorage():
    try:
        return AbilityStorage._storage
    except AttributeError:
        abilityAttributes = ['displayNameID', 'iconID', 'targetMode']
        mapping = [('$', collections.namedtuple('fighterAbilityTuple', abilityAttributes))]
        AbilityStorage._storage = fsdlite.EveStorage(data='fighters/abilities', cache='fighterAbilities.static', mapping=mapping, coerce=int)
        return AbilityStorage._storage


def TypeStorage():
    try:
        return TypeStorage._storage
    except AttributeError:
        abilitySlotAttributes = ['abilityID', 'cooldownSeconds', 'chargeCount']
        typeAttributes = ['abilitySlot0', 'abilitySlot1', 'abilitySlot2']
        mapping = [('abilitySlot[0-2]$', collections.namedtuple('abilitySlotTuple', abilitySlotAttributes)), ('$', collections.namedtuple('typeTuple', typeAttributes))]
        TypeStorage._storage = fsdlite.EveStorage(data='fighters/abilitiesByType', cache='fighterAbilitiesByType.static', mapping=mapping, coerce=int)
        return TypeStorage._storage


def CloseStorage():
    AbilityStorage().cache.close()
    TypeStorage().cache.close()
