#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\turboshield.py
import logging
from dogma.const import attributeShieldCharge, attributeShieldCapacity
from dogma.const import attributeShieldExplosiveDamageResonance, attributeShieldEmDamageResonance
from dogma.const import attributeShieldKineticDamageResonance, attributeShieldThermalDamageResonance
from dogma.const import attributeDisallowOffensiveModifiers
from spacecomponents.common.componentConst import TURBO_SHIELD_CLASS
from spacecomponents.common.components.component import Component
from spacecomponents.common.components.turboshield import TURBO_SHIELD_STATE_ACTIVE, TURBO_SHIELD_STATE_INVULNERABLE
from spacecomponents.common.components.turboshield import TURBO_SHIELD_STATE_DEPLETED, TURBO_SHIELD_STATE_RESISTIVE
from spacecomponents.server.messages import MSG_ON_DAMAGE_STATE_CHANGE, MSG_ON_TURBO_SHIELD_STATE_CHANGED, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
import uthread2
logger = logging.getLogger(__name__)
SHIELD_RESONANCE_ATTRIBUTES = [attributeShieldExplosiveDamageResonance,
 attributeShieldEmDamageResonance,
 attributeShieldKineticDamageResonance,
 attributeShieldThermalDamageResonance]
SUPER_RESISTANCE = 1e-07

class TurboShield(Component):

    def __init__(self, itemID, typeID, attributes, componentRegistry):
        super(TurboShield, self).__init__(itemID, typeID, attributes, componentRegistry)
        self.turboShieldState = TURBO_SHIELD_STATE_ACTIVE
        self.lastShieldLevel = None
        self.turboShieldActivationLevel = 0.01
        self.shieldModeTasklet = None
        self.SubscribeToMessage(MSG_ON_ADDED_TO_SPACE, self.OnAddedToSpace)
        self.SubscribeToMessage(MSG_ON_REMOVED_FROM_SPACE, self.OnRemovedFromSpace)
        self.SubscribeToMessage(MSG_ON_DAMAGE_STATE_CHANGE, self.OnDamageStateChange)

    def OnAddedToSpace(self, ballpark, spaceComponentDB):
        logger.debug('TurboShield.OnAddedToSpace %d', self.itemID)
        self.ballpark = ballpark
        self.dogmaLM = ballpark.dogmaLM
        UpdateSlimItemFromComponent(self, ballpark)

    def OnRemovedFromSpace(self, ballpark, spaceComponentDB):
        logger.debug('TurboShield.OnRemovedFromSpace %d', self.itemID)
        if self.shieldModeTasklet is not None:
            self.shieldModeTasklet.kill()

    def OnDamageStateChange(self, oldDamageState, newDamageState):
        newShieldLevel = newDamageState[0][0]
        if oldDamageState is not None:
            oldShieldLevel = oldDamageState[0][0]
        else:
            oldShieldLevel = self.lastShieldLevel
        if oldShieldLevel is None:
            self.lastShieldLevel = newShieldLevel
        elif oldShieldLevel >= self.turboShieldActivationLevel > newShieldLevel:
            self.shieldModeTasklet = uthread2.StartTasklet(self.DepleteTurboShield)
        else:
            self.lastShieldLevel = newShieldLevel

    def CanEnterReinforce(self, shieldLevel):
        if not self.IsActive():
            return False
        return shieldLevel > self.turboShieldActivationLevel

    def DepleteTurboShield(self):
        if not self.IsActive():
            return
        self._EnableInvulnerableShieldMode()
        uthread2.SleepSim(self.attributes.invulnerablePeriodSeconds)
        self._EnableResistiveShieldMode()
        uthread2.SleepSim(self.attributes.resistivePeriodSeconds)
        self._EnableDepletedShieldMode()
        uthread2.SleepSim(self.attributes.cooldownPeriodSeconds)
        self._EnableActiveShieldMode()

    def _SetBallInvulnerability(self, isInvulnerable):
        if isInvulnerable:
            self.ballpark.MakeInvulnerablePermanently(self.itemID, 'TurboShield')
        else:
            self.ballpark.CancelCurrentInvulnerability(self.itemID)

    def _StopTargetedEffectsOnHost(self):
        targeters = self.dogmaLM.GetTargetersEx(self.itemID)
        for targetID in targeters:
            self.dogmaLM.StopTargetEffectsOnTargetLoss(targetID, [self.itemID], forced=True)

    def _ChargeTurboShield(self):
        maxShieldCapacity = self.dogmaLM.GetAttributeValue(self.itemID, attributeShieldCapacity)
        self.dogmaLM.SetAttributeValue(self.itemID, attributeShieldCharge, maxShieldCapacity)

    def _EnableInvulnerableShieldMode(self):
        logger.debug('Activating turbo shield. Invulnerable mode.')
        self._StopTargetedEffectsOnHost()
        self._SetBallInvulnerability(True)
        self.SetShieldState(TURBO_SHIELD_STATE_INVULNERABLE)

    def _EnableResistiveShieldMode(self):
        logger.debug('Activating turbo shield. Resistive mode.')
        self._SetBallInvulnerability(False)
        self._SetTurboResistances()
        self.SetShieldState(TURBO_SHIELD_STATE_RESISTIVE)

    def _EnableDepletedShieldMode(self):
        logger.debug('Activating turbo shield. Turbo shield depleted.')
        self._ChargeTurboShield()
        self._RestoreTypeResistances()
        self.SetShieldState(TURBO_SHIELD_STATE_DEPLETED)

    def _EnableActiveShieldMode(self):
        logger.debug('Reactivating turbo shield.')
        self.SetShieldState(TURBO_SHIELD_STATE_ACTIVE)

    def _SetTurboResistances(self):
        for attributeID in SHIELD_RESONANCE_ATTRIBUTES:
            self.dogmaLM.SetAttributeValue(self.itemID, attributeID, SUPER_RESISTANCE)

        self._SetEwarImmunity(True)

    def _RestoreTypeResistances(self):
        for attributeID in SHIELD_RESONANCE_ATTRIBUTES:
            typeValue = self.dogmaLM.dogmaStaticMgr.GetTypeAttribute2(self.typeID, attributeID)
            self.dogmaLM.SetAttributeValue(self.itemID, attributeID, typeValue)

        self._SetEwarImmunity(False)

    def _SetEwarImmunity(self, isImmune):
        self.dogmaLM.SetAttributeValue(self.itemID, attributeDisallowOffensiveModifiers, 1.0 if isImmune else 0.0)

    def IsInvulnerable(self):
        return self.turboShieldState == TURBO_SHIELD_STATE_INVULNERABLE

    def IsActive(self):
        return self.turboShieldState == TURBO_SHIELD_STATE_ACTIVE

    def IsDepleted(self):
        return self.turboShieldState == TURBO_SHIELD_STATE_DEPLETED

    def IsResistive(self):
        return self.turboShieldState == TURBO_SHIELD_STATE_RESISTIVE

    def IsShieldState(self, shieldState):
        return self.turboShieldState == shieldState

    def SetShieldState(self, shieldState):
        self.turboShieldState = shieldState
        UpdateSlimItemFromComponent(self, self.ballpark)
        self.SendMessage(MSG_ON_TURBO_SHIELD_STATE_CHANGED, shieldState)


def UpdateSlimItemFromComponent(component, ballpark):
    logger.debug('TurboShield.UpdateSlimItemFromComponent %d %s', component.itemID, component.turboShieldState)
    ballpark.UpdateSlimItemField(component.itemID, 'component_turboshield', component.turboShieldState)


def HandleSlashCommand(itemID, action, ballpark, componentRegistry, spaceComponentDB):
    component = componentRegistry.GetComponentsByItemID(itemID)[TURBO_SHIELD_CLASS]
    component.HandleSlashCommand(action, ballpark, spaceComponentDB)
