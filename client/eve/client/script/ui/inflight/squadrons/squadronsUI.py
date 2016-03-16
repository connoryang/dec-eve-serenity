#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronsUI.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.inflight.squadrons.effectsCont import EffectsCont
from eve.client.script.ui.inflight.squadrons.abilitiesCont import AbilitiesCont
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronCont import SquadronCont, SquadronContEmpty
from eve.client.script.ui.inflight.squadrons.squadronController import SquadronController
import carbonui.const as uiconst
from eve.common.script.mgt.fighterConst import TUBE_STATE_EMPTY, TUBE_STATE_READY, TUBE_STATE_UNLOADING

class SquadronsUI(ContainerAutoSize):
    default_width = 500

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        left = 0
        for tubeFlagID in const.fighterTubeFlags:
            squadron = SquadronUI(parent=self, align=uiconst.BOTTOMLEFT, tubeFlagID=tubeFlagID, left=left)
            left = squadron.left + squadron.width + 6


class SquadronUI(ContainerAutoSize):
    default_width = 80

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.inSpace = False
        self.shipFighterState = GetShipFighterState()
        self.tubeFlagID = attributes.tubeFlagID
        fighters = self.GetFightersState()
        if fighters:
            fighterID = fighters.itemID
            fighterTypeID = fighters.typeID
            squadronSize = fighters.squadronSize
        else:
            fighterID = None
            fighterTypeID = None
            squadronSize = None
        self.controller = SquadronController()
        self.squadronCont = SquadronCont(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, align=uiconst.BOTTOMLEFT, tubeFlagID=self.tubeFlagID)
        self.squadronCont.SetSquadronSize(squadronSize)
        self.squadronContEmpty = SquadronContEmpty(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, align=uiconst.BOTTOMLEFT, tubeFlagID=self.tubeFlagID)
        if not fighterID and not fighterTypeID:
            self.ShowEmpty()
        else:
            self.HideEmpty()
        self.effectsCont = EffectsCont(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, top=self.squadronCont.height, align=uiconst.BOTTOMLEFT)
        self.modulesCont = AbilitiesCont(parent=self, controller=self.controller, fighterID=fighterID, fighterTypeID=fighterTypeID, left=16, top=self.squadronCont.height, align=uiconst.BOTTOMLEFT)
        self.shipFighterState.signalOnFighterTubeStateUpdate.connect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.connect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.connect(self.OnFighterInSpaceUpdate)

    def ShowEmpty(self):
        self.squadronContEmpty.display = True
        self.squadronCont.display = False

    def HideEmpty(self):
        self.squadronContEmpty.display = False
        self.squadronCont.display = True

    def GetFightersInSpaceState(self):
        fighterInSpace = self.shipFighterState.GetFightersInSpace(self.tubeFlagID)
        if fighterInSpace is not None:
            self.inSpace = True
            return fighterInSpace

    def GetFightersInTubeState(self):
        fighterInTube = self.shipFighterState.GetFightersInTube(self.tubeFlagID)
        if fighterInTube is not None:
            self.inSpace = False
            return fighterInTube

    def GetFightersState(self):
        fightersInTube = self.GetFightersInTubeState()
        if fightersInTube:
            return fightersInTube
        fightersInSpace = self.GetFightersInSpaceState()
        if fightersInSpace:
            return fightersInSpace

    def OnFighterTubeStateUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            pass

    def OnFighterTubeContentUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID in (TUBE_STATE_EMPTY, TUBE_STATE_READY, TUBE_STATE_UNLOADING):
                self.ShowEmpty()
            else:
                self.HideEmpty()
                fightersInTube = self.GetFightersInTubeState()
                if fightersInTube:
                    self.squadronCont.SetSquadronIcon(fightersInTube.typeID)
                    self.squadronCont.SetSquadronSize(fightersInTube.squadronSize)

    def OnFighterInSpaceUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            pass

    def Close(self):
        self.shipFighterState.signalOnFighterTubeStateUpdate.disconnect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.disconnect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.disconnect(self.OnFighterInSpaceUpdate)
