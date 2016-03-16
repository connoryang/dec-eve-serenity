#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\fittingGhost\ghostFittingEffectCompiler.py
import dogma.const as dogmaConst
from dogma.effects import Effect
from eve.client.script.dogma.clientEffectCompiler import ClientEffectCompiler

class GhostFittingEffectCompiler(ClientEffectCompiler):
    __guid__ = 'svc.ghostFittingEffectCompiler'

    def GetDogmaStaticMgr(self):
        return sm.GetService('clientDogmaStaticSvc')

    def GetPythonForOperand(self, operand, arg1, arg2, val):
        if 'env' not in self.evalDict:

            class Env:

                def __getattr__(self, attrName):
                    return 'env.%s' % attrName

            self.evalDict['env'] = Env()

    def SetupEffects(self):
        ClientEffectCompiler.SetupEffects(self)
        for item in pythonEffects:
            if hasattr(item, '__effectIDs__'):
                inst = item()
                for effectID in inst.__effectIDs__:
                    if type(effectID) is str:
                        effectName = effectID
                        effectID = getattr(const, effectName, None)
                        if effectID is None:
                            print 'Namespace item ' + item + ' has non-existant effect name reference ' + effectName
                            continue
                    self.effects[effectID] = inst


class Attack(Effect):
    __guid__ = 'testAttack'
    __effectIDs__ = ['effectTargetAttack',
     'effectTargetAttackForStructures',
     'effectProjectileFired',
     'effectProjectileFiredForEntities']

    def __init__(self, *args):
        pass


class OnlineEffect(Effect):
    __guid__ = 'OnlineEffect'
    __effectIDs__ = ['effectOnline']
    __modifier_only__ = 0

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogma = sm.GetService('dogma')
        dogma.SkillCheck(env, 'OnlineHasSkillPrerequisites', None)
        cpuOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuOutput)
        cpuLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributeCpuLoad)
        cpu = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeCpu)
        if cpuOutput >= cpuLoad + cpu:
            powerOutput = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerOutput)
            powerLoad = dogmaLM.GetAttributeValue(shipID, dogmaConst.attributePowerLoad)
            power = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributePower)
            if powerOutput >= powerLoad + power:
                dogmaLM.SetAttributeValue(itemID, dogmaConst.attributeIsOnline, 1)
                dogmaLM.AddModifier(2, shipID, dogmaConst.attributeCpuLoad, itemID, dogmaConst.attributeCpu)
                dogmaLM.AddModifier(2, shipID, dogmaConst.attributePowerLoad, itemID, dogmaConst.attributePower)
            else:
                dogma.UserError(env, 'NotEnoughPower', None)
        else:
            dogma.UserError(env, 'NotEnoughCpu', None)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeCpuLoad, itemID, const.attributeCpu)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributePowerLoad, itemID, const.attributePower)
        dogmaLM.SetAttributeValue(itemID, const.attributeIsOnline, 0)


class Powerboost(Effect):
    __guid__ = 'dogmaXP.Effect_48'
    __effectIDs__ = [48]
    isPythonEffect = True

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        weaponID = env.itemID
        shipID = env.shipID
        item = dogmaLM.dogmaItems[weaponID]
        chargeKey = dogmaLM.GetSubLocation(shipID, item.flagID)
        if chargeKey is None:
            raise UserError('NoCharges', {'launcher': (const.UE_TYPEID, item.typeID)})
        chargeQuantity = dogmaLM.GetAttributeValue(chargeKey, const.attributeQuantity)
        if chargeQuantity is None or chargeQuantity < 1:
            raise UserError('NoCharges', {'launcher': (const.UE_TYPEID, item.typeID)})
        capacitorBonus = dogmaLM.GetAttributeValue(chargeKey, const.attributeCapacitorBonus)
        if capacitorBonus != 0:
            new, old = dogmaLM.IncreaseItemAttributeEx(env.shipID, const.attributeCharge, capacitorBonus, alsoReturnOldValue=True)
        return 1

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        return 1


class Mine(Effect):
    __guid__ = 'dogmaXP.Mining'
    __effectIDs__ = ['effectMining', 'effectMiningLaser', 'effectMiningClouds']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, asteroidID):
        durationAttributeID = cfg.dgmeffects.Get(env.effectID).durationAttributeID
        duration = dogmaLM.GetAttributeValue(itemID, durationAttributeID)
        env.miningDuration = duration
        env.startedEffect = blue.os.GetSimTime()

    def GetClamp(self, env, preferredDuration):
        timePassed = blue.os.GetSimTime() - env.startedEffect
        millisecondsPassed = timePassed / 10000L
        return float(millisecondsPassed) / preferredDuration


pythonEffects = [Attack,
 OnlineEffect,
 Powerboost,
 Mine]
