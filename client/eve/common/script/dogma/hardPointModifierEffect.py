#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\hardPointModifierEffect.py
from dogma.effects import Effect

class HardpointModifierEffect(Effect):
    __guid__ = 'dogmaXP.HardPointModifier'
    __effectIDs__ = ['effectHardPointModifier']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeLauncherSlotsLeft, itemID, const.attributeLauncherHardPointModifier)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeTurretSlotsLeft, itemID, const.attributeTurretHardpointModifier)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeLauncherSlotsLeft, itemID, const.attributeLauncherHardPointModifier)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeTurretSlotsLeft, itemID, const.attributeTurretHardpointModifier)

    RestrictedStop = Stop
