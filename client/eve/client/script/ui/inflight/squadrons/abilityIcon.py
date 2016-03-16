#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\abilityIcon.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from localization import GetByMessageID

class AbilityIcon(Container):
    default_width = 48
    default_height = 48
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.shipFighterState = GetShipFighterState()
        self.stateLabel = EveLabelSmall(parent=self, align=uiconst.CENTER)
        self.controller = attributes.controller
        self.slotID = self.controller.slotID
        self.fighterID = attributes.fighterID
        ability = self.GetAbilityInfo()
        nameID = ability.displayNameID
        iconID = ability.iconID
        self.abilityIcon = Icon(parent=self, align=uiconst.CENTER, width=32, height=32, icon=iconID)
        bgSprite = Sprite(parent=self, align=uiconst.CENTER, width=64, height=64, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/slotFighterAbility.png')
        self.abilityIcon.SetSize(32, 32)
        self.abilityIcon.OnClick = self.OnAbilityClick
        if not self.controller.IsAbilityActive():
            self.SetModuleDeactivated()
        self.targetMode = ability.targetMode
        self.abilityIcon.hint = GetByMessageID(nameID)
        self.shipFighterState.signalOnAbilityActivated.connect(self.OnAbilityActivated)
        self.shipFighterState.signalOnAbilityDeactivated.connect(self.OnAbilityDeactivated)

    def GetAbilityInfo(self):
        ability = self.controller.GetAbilityInfo()
        return ability

    def OnAbilityActivated(self, fighterID, slotID):
        if slotID == self.slotID and fighterID == self.fighterID:
            self.SetModuleActivated()

    def OnAbilityDeactivated(self, fighterID, slotID):
        if slotID == self.slotID and fighterID == self.fighterID:
            self.SetModuleDeactivated()

    def SetModuleActivated(self):
        self.abilityIcon.SetAlpha(1.0)

    def SetModuleDeactivated(self):
        self.abilityIcon.SetAlpha(0.5)

    def OnAbilityClick(self, *args):
        self.controller.OnAbilityClick(self.targetMode)

    def Close(self):
        self.shipFighterState.signalOnAbilityActivated.disconnect(self.OnAbilityActivated)
        self.shipFighterState.signalOnAbilityDeactivated.disconnect(self.OnAbilityDeactivated)
