#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fighters\__init__.py
from .storages import AbilityStorage, TypeStorage
ABILITY_SLOT_0 = 0
ABILITY_SLOT_1 = 1
ABILITY_SLOT_2 = 2
ABILITY_SLOT_IDS = (ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2)
TARGET_MODE_UNTARGETED = 'untargeted'
TARGET_MODE_ITEMTARGETED = 'itemTargeted'
TARGET_MODE_POINTTARGETED = 'pointTargeted'
SQUADRON_SIZE_SLIMITEM_NAME = 'fighter.squadronSize'

def GetAbilityIDForSlot(fighterTypeID, abilitySlotID):
    for slotID, typeAbility in IterTypeAbilities(fighterTypeID):
        if abilitySlotID == slotID and typeAbility is not None:
            return typeAbility.abilityID


def IterTypeAbilities(fighterTypeID):
    typeStorage = TypeStorage()
    typeAbilities = typeStorage.get(fighterTypeID)
    if typeAbilities is not None:
        yield (ABILITY_SLOT_0, typeAbilities.abilitySlot0)
        yield (ABILITY_SLOT_1, typeAbilities.abilitySlot1)
        yield (ABILITY_SLOT_2, typeAbilities.abilitySlot2)


def CheckAbilitySlotIDIsValid(abilitySlotID):
    if abilitySlotID not in ABILITY_SLOT_IDS:
        raise ValueError('Invalid ability slot ID')


def GetAbilityTargetMode(abilityID):
    abilityStorage = AbilityStorage()
    try:
        ability = abilityStorage[abilityID]
    except KeyError:
        raise ValueError('Invalid abilityID')

    if ability is not None:
        return ability.targetMode
