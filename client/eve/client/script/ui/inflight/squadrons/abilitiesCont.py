#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilitiesCont.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.squadrons.abilityController import AbilityController
from eve.client.script.ui.inflight.squadrons.abilityIcon import AbilityIcon
from fighters import IterTypeAbilities

class AbilitiesCont(ContainerAutoSize):
    default_width = 64
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.fighterTypeID = attributes.fighterTypeID
        self.fighterID = attributes.fighterID
        self.controller = attributes.controller
        self.DrawModules()

    def DrawModules(self):
        abilities = self.controller.GetAbilities(self.fighterTypeID)
        if not abilities:
            return
        for slotID, typeAbility in abilities:
            if typeAbility is not None:
                abilityID = typeAbility.abilityID
                abilityController = AbilityController(abilityID, self.fighterID, slotID)
                self.AddAbility(abilityController)

    def AddAbility(self, controller):
        AbilityIcon(parent=self, controller=controller, fighterID=self.fighterID, align=uiconst.TOBOTTOM)
