#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\fighterInvCont.py
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
from eve.client.script.ui.inflight.squadrons.squadronManagementCont import FighterLaunchControlCont
import invCont
import carbonui.const as uiconst

class FighterInvCont(invCont._InvContBase):
    __guid__ = 'invCont.FighterInvCont'
    __invControllerClass__ = None

    def ApplyAttributes(self, attributes):
        invCont._InvContBase.ApplyAttributes(self, attributes)

    def ConstructUI(self):
        topCont = Container(parent=self, align=uiconst.TOTOP, height=236)
        inSpace = Container(parent=topCont, align=uiconst.TOTOP, height=18)
        launchDeck = Container(parent=topCont, align=uiconst.TOBOTTOM, height=18)
        self.squadronsCont = Container(parent=topCont, align=uiconst.TOALL)
        inSpaceLabel = EveLabelSmall(parent=inSpace, align=uiconst.CENTERLEFT, text='Launch Deck (2)')
        launchDeckLabel = EveLabelSmall(parent=launchDeck, align=uiconst.CENTERLEFT, text='Hangar Deck (2)')
        self.ConstructSquadrons()
        invCont._InvContBase.ConstructUI(self)
        BumpedUnderlay(parent=topCont, name='background')

    def ConstructSquadrons(self):
        left = 0
        for tubeFlagID in const.fighterTubeFlags:
            FighterLaunchControlCont(parent=self.squadronsCont, tubeFlagID=tubeFlagID, left=left)
            left += 2
