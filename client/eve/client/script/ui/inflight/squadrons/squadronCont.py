#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronCont.py
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.inflight.squadrons.fightersHealthGaugeCont import FightersHealthGauge
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import SquadronNumber

class SquadronCont(Container):
    default_width = 86
    default_height = 116
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fighterTypeID = attributes.fighterTypeID
        self.fighterItemID = attributes.fighterItemID
        self.controller = attributes.controller
        tubeFlagID = attributes.tubeFlagID
        textCont = Container(parent=self, align=uiconst.TOBOTTOM, top=10, height=30)
        self.squadronNumber = SquadronNumber(parent=self, top=1, left=1)
        self.squadronNumber.SetText(tubeFlagID)
        self.fighterHealthCont = FightersHealthGauge(parent=self, align=uiconst.TOTOP, height=86)
        self.actionLabel = EveLabelSmall(parent=textCont, align=uiconst.CENTERBOTTOM, top=2)
        self.speedLabel = EveLabelSmall(parent=textCont, align=uiconst.CENTERTOP, top=2)
        self.SetSquadronSpeed()
        self.SetSquadronAction()
        self.SetSquadronHealth()
        self.SetSquadronIcon(self.fighterTypeID)

    def SetSquadronSpeed(self):
        speed = self.controller.GetSquadronSpeed()
        self.speedLabel.text = speed

    def SetSquadronAction(self):
        action = self.controller.GetSquadronAction()
        self.actionLabel.text = action

    def SetSquadronHealth(self):
        total, damaged, dead = self.controller.GetSquadronHealth()

    def SetSquadronIcon(self, typeID):
        self.fighterHealthCont.LoadFighterIcon(typeID)

    def SetSquadronSize(self, squadronSize):
        self.fighterHealthCont.SetSquadronSize(squadronSize)


class SquadronContEmpty(Container):
    default_width = 86
    default_height = 116
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        tubeFlagID = attributes.tubeFlagID
        textCont = Container(parent=self, align=uiconst.TOBOTTOM, height=30, top=10)
        self.squadronNumber = SquadronNumber(parent=self, top=1, left=1)
        self.squadronNumber.SetText(tubeFlagID)
        self.actionLabel = EveLabelSmall(parent=textCont, align=uiconst.CENTERBOTTOM, top=2)
        self.fighterCont = Container(parent=self, align=uiconst.TOTOP, height=86)
        Sprite(parent=self.fighterCont, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/fighterOpenOverlay.png', align=uiconst.CENTER, height=86, width=86)
        self.SetSquadronAction()

    def SetSquadronAction(self):
        action = self.controller.GetSquadronAction()
        self.actionLabel.text = action
