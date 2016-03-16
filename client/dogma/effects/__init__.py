#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\__init__.py
import evetypes
from dogma import const
EXPRESSIONS = {'LocationRequiredSkillModifier': 'on all items located in {domain} requiring skill {skillTypeID}',
 'LocationGroupModifier': 'on all items located in {domain} in group {groupID}',
 'OwnerRequiredSkillModifier': 'on all items owned by {domain} that require skill {skillTypeID}',
 'ItemModifier': '{domain}',
 'GangItemModifier': 'on ships in gang',
 'GangRequiredSkillModifier': 'on items fitted to ships in gang that require skill {skillTypeID}'}

def _GetModifierDict(realDict):
    ret = {}
    for key, value in realDict.iteritems():
        if key in ('modifiedAttributeID', 'modifyingAttributeID'):
            newValue = cfg.dgmattribs.Get(value).attributeName
        elif key == 'domain':
            if value is None:
                newValue = 'self'
            else:
                newValue = value.replace('ID', '')
        elif key == 'skillTypeID':
            newValue = evetypes.GetName(value)
        elif key == 'groupID':
            newValue = evetypes.GetGroupNameByGroup(value)
        else:
            newValue = value
        ret[key] = newValue

    ret['domainInfo'] = EXPRESSIONS.get(ret['func'], ' UNKNOWN {func}').format(**ret)
    return ret


def IterReadableModifierStrings(modifiers):
    for modifierDict in modifiers:
        yield 'modifies {modifiedAttributeID} on {domainInfo} with attribute {modifyingAttributeID}'.format(**_GetModifierDict(modifierDict))


def IsCloakingEffect(effectID):
    return effectID in [const.effectCloaking, const.effectCloakingWarpSafe, const.effectCloakingPrototype]


class Effect:
    __guid__ = 'dogmaXP.Effect'
    isPythonEffect = True
    __modifier_only__ = False
    __modifies_character__ = False
    __modifies_ship__ = False
    __modifier_domain_other__ = False

    def RestrictedStop(self, *args):
        pass

    def PreStartChecks(self, *args):
        pass

    def StartChecks(self, *args):
        pass

    def Start(self, *args):
        pass

    def Stop(self, *args):
        pass


def GetName(effectID):
    return cfg.dgmeffects.Get(effectID).effectName


def IsDefault(typeID, effectID):
    for effectRow in cfg.dgmtypeeffects[typeID]:
        if effectID == effectRow.effectID:
            if effectRow.isDefault:
                return True
            else:
                return False

    raise KeyError()


def GetEwarTypeByEffectID(effectID):
    effect = cfg.dgmeffects.Get(effectID)
    if effect.electronicChance:
        return 'electronic'
    if effect.propulsionChance:
        return 'propulsion'
    ewarType = ALLEWARTYPES.get(effectID, None)
    return ewarType


ALLEWARTYPES = {const.effectEwTargetPaint: 'ewTargetPaint',
 const.effectTargetMaxTargetRangeAndScanResolutionBonusHostile: 'ewRemoteSensorDamp',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedBonusHostile: 'ewTrackingDisrupt',
 const.effectTargetGunneryMaxRangeAndTrackingSpeedAndFalloffBonusHostile: 'ewTrackingDisrupt',
 const.effectTurretWeaponRangeFalloffTrackingSpeedMultiplyTargetHostile: 'ewTrackingDisrupt',
 const.effectEntitySensorDampen: 'ewRemoteSensorDamp',
 const.effectSensorBoostTargetedHostile: 'ewRemoteSensorDamp',
 const.effectEntityTrackingDisrupt: 'ewTrackingDisrupt',
 const.effectGuidanceDisrupt: 'ewGuidanceDisrupt',
 const.effectEntityTargetPaint: 'ewTargetPaint'}
SERVEREWARTYPES = {const.effectWarpScramble: 'warpScrambler',
 const.effectDecreaseTargetSpeed: 'webify',
 const.effectWarpScrambleForEntity: 'warpScrambler',
 const.effectModifyTargetSpeed2: 'webify',
 const.effectConcordWarpScramble: 'warpScrambler',
 const.effectConcordModifyTargetSpeed: 'webify',
 const.effectWarpScrambleBlockMWDWithNPCEffect: 'warpScramblerMWD',
 const.effectWarpDisruptSphere: 'focusedWarpScrambler',
 const.effectLeech: 'ewEnergyVampire',
 const.effectEnergyDestabilizationNew: 'ewEnergyNeut',
 const.effectEntityCapacitorDrain: 'ewEnergyNeut',
 const.effectEnergyDestabilizationForStructure: 'ewEnergyNeut',
 const.effectEnergyNeutralizerFalloff: 'ewEnergyNeut',
 const.effectEnergyNosferatuFalloff: 'ewEnergyVampire',
 const.effectWarpScrambleForStructure: 'warpScrambler',
 const.effectDecreaseTargetSpeedForStructures: 'webify',
 const.effectEssWarpScramble: 'warpScrambler',
 const.effectWarpScrambleTargetMWDBlockActivationForEntity: 'warpScramblerMWD'}
ALLEWARTYPES.update(SERVEREWARTYPES)
