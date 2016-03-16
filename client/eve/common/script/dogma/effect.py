#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\effect.py
ApplyBrainEffect = {'M': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.AddModifierWithSource(operation, targetID, toAttribID, fromAttrib),
 'LG': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, groupID: dogmaLM.AddLocationGroupModifierWithSource(operation, targetID, groupID, toAttribID, fromAttrib),
 'LRS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.AddLocationRequiredSkillModifierWithSource(operation, targetID, skillID, toAttribID, fromAttrib),
 'ORS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.AddOwnerRequiredSkillModifierWithSource(operation, targetID, skillID, toAttribID, fromAttrib),
 'L': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.AddLocationModifierWithSource(operation, targetID, toAttribID, fromAttrib),
 'GRS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.AddGangRequiredSkillModifierWithSource(targetID, operation, skillID, toAttribID, fromAttrib),
 'GSM': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.AddGangShipModifierWithSource(targetID, operation, toAttribID, fromAttrib),
 'GGM': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, groupID: dogmaLM.AddGangGroupModifierWithSource(targetID, operation, groupID, toAttribID, fromAttrib)}
RemoveBrainEffect = {'M': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.RemoveModifierWithSource(operation, targetID, toAttribID, fromAttrib),
 'LG': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, groupID: dogmaLM.RemoveLocationGroupModifierWithSource(operation, targetID, groupID, toAttribID, fromAttrib),
 'LRS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.RemoveLocationRequiredSkillModifierWithSource(operation, targetID, skillID, toAttribID, fromAttrib),
 'ORS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.RemoveOwnerRequiredSkillModifierWithSource(operation, targetID, skillID, toAttribID, fromAttrib),
 'L': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.RemoveLocationModifierWithSource(operation, targetID, toAttribID, fromAttrib),
 'GRS': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, skillID: dogmaLM.RemoveGangRequiredSkillModifierWithSource(targetID, operation, skillID, toAttribID, fromAttrib),
 'GSM': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation: dogmaLM.RemoveGangShipModifierWithSource(targetID, operation, toAttribID, fromAttrib),
 'GGM': lambda dogmaLM, targetID, fromAttrib, toAttribID, operation, groupID: dogmaLM.RemoveGangGroupModifierWithSource(targetID, operation, groupID, toAttribID, fromAttrib)}
import dogma.const as dgmconst
CombineModifiers = {dgmconst.dgmAssPreAssignment: lambda mod1, mod2: mod2,
 dgmconst.dgmAssPostAssignment: lambda mod1, mod2: mod2,
 dgmconst.dgmAssPreMul: lambda mod1, mod2: mod1 * mod2,
 dgmconst.dgmAssPostMul: lambda mod1, mod2: mod1 * mod2,
 dgmconst.dgmAssPreDiv: lambda mod1, mod2: mod1 * mod2,
 dgmconst.dgmAssPostDiv: lambda mod1, mod2: mod1 * mod2,
 dgmconst.dgmAssModAdd: lambda mod1, mod2: mod1 + mod2,
 dgmconst.dgmAssModSub: lambda mod1, mod2: mod1 + mod2,
 dgmconst.dgmAssPostPercent: lambda mod1, mod2: (100 + mod1) / 100.0 * ((100 + mod2) / 100.0) * 100 - 100}

class Effect:
    __guid__ = 'dogmaXP.Effect'
    isPythonEffect = True
    __modifier_only__ = False
    __modifies_character__ = False
    __modifies_ship__ = False

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


class BrainEffect(object):

    def __init__(self, fromAttrib, toItemID, modifierType, toAttribID, operation, extras = tuple()):
        self.fromAttrib = fromAttrib
        self.value = None
        self.toItemID = toItemID
        self.modifierType = modifierType
        self.toAttribID = toAttribID
        self.operation = operation
        self.extras = extras
        self.skills = [fromAttrib.invItem.typeID]

    def GetLiteralKey(self):
        return (tuple(self.skills), self.value)

    def CombineWithEffect(self, effect):
        self.value = CombineModifiers[effect.operation](self.value, effect.value)
        self.skills.extend(effect.skills)

    def ResolveValue(self):
        self.value = self.fromAttrib.GetValue()
        self.fromAttrib = None

    def GetTargetKey(self):
        return (self.toItemID,
         self.toAttribID,
         self.modifierType,
         self.operation,
         self.extras)

    def GetApplicationArgs(self):
        return (self.toAttribID, self.operation) + self.extras
