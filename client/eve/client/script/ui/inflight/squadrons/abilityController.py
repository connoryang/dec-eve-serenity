#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilityController.py
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
import fighters
import log

class AbilityController(object):

    def __init__(self, abilityID, fighterID, slotID):
        self.abilityID = abilityID
        self.fighterID = fighterID
        self.slotID = slotID
        self.shipFighterState = GetShipFighterState()

    def GetAbilityInfo(self):
        return fighters.AbilityStorage()[self.abilityID]

    def OnAbilityClick(self, targetMode):
        if self.IsAbilityActive():
            self.DeactivateAbility()
        else:
            self.ActivateAbility(targetMode)

    def IsAbilityActive(self):
        return self.shipFighterState.IsAbilityActive(self.fighterID, self.slotID)

    def ActivateAbility(self, targetMode):
        if self.fighterID is None:
            return
        if targetMode == fighters.TARGET_MODE_UNTARGETED:
            self._OnActivateAbilityOnSelf()
        elif targetMode == fighters.TARGET_MODE_ITEMTARGETED:
            targetID = sm.GetService('target').GetActiveTargetID()
            if targetID:
                self._OnActivateAbilityOnTarget(targetID)
            else:
                eve.Message('CustomNotify', {'notify': 'You need to target something'})
        elif targetMode == fighters.TARGET_MODE_POINTTARGETED:
            log.LogWarn('Not yet implemented')
        else:
            log.LogTraceback('unexpected targetmode')

    def DeactivateAbility(self):
        self._OnDeactivateAbility()

    def _OnActivateAbilityOnTarget(self, targetID):
        sm.GetService('fighters').ActivateAbilitySlot(self.fighterID, self.slotID, targetID)

    def _OnActivateAbilityOnSelf(self):
        sm.GetService('fighters').ActivateAbilitySlot(self.fighterID, self.slotID)

    def _OnDeactivateAbility(self):
        sm.GetService('fighters').DeactivateAbilitySlot(self.fighterID, self.slotID)
