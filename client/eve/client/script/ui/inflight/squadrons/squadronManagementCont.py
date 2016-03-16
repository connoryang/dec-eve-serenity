#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronManagementCont.py
from carbon.common.lib.const import SEC
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.buttons import ButtonIcon
from eve.client.script.ui.control.eveLabel import EveHeaderSmall, EveLabelSmall
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.inflight.squadrons.fightersHealthGaugeCont import FightersHealthGauge
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.client.script.ui.inflight.squadrons.squadronManagementController import SquadronMgmtController
from eve.common.script.mgt.fighterConst import TUBE_STATE_EMPTY, COLOR_BY_STATE, LABEL_BY_STATE, TUBE_STATE_SCOOPING, TUBE_STATE_LAUNCHING, COLOR_INSPACE, COLOR_RETURNING, TUBE_STATE_READY, TUBE_STATE_INSPACE
import gametime
from localization import GetByLabel
SLOTNUMBER_BY_TUBEFLAG = {const.flagFighterTube0: 1,
 const.flagFighterTube1: 2,
 const.flagFighterTube2: 3,
 const.flagFighterTube3: 4,
 const.flagFighterTube4: 5}

class FighterLaunchControlCont(Container):
    default_height = 214
    default_width = 86
    default_align = uiconst.TOLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = SquadronMgmtController()
        self.shipFighterState = GetShipFighterState()
        self.tubeFlagID = attributes.tubeFlagID
        inSpaceCont = Container(parent=self, height=86, align=uiconst.TOTOP, bgColor=(0, 0, 0, 0.4))
        inSpaceCont.OnDropData = self.OnDropToSpace
        self.squadronNumber = SquadronNumber(parent=inSpaceCont, top=1, left=1)
        self.squadronNumber.SetText(self.tubeFlagID)
        self.stateCont = Container(parent=self, height=24, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.stateContBG = Fill(bgParent=self.stateCont, color=(0, 0, 0, 0))
        deckCont = Container(parent=self, height=86, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, bgColor=(0, 0, 0, 0.4))
        deckCont.OnDropData = self.OnDropToTube
        deckCont.GetMenu = self.GetLaunchMenu
        self.tubeStatusLabel = EveHeaderSmall(parent=self.stateCont, align=uiconst.CENTER, text='')
        self.loadingGauge = Gauge(parent=self.stateCont, align=uiconst.CENTERBOTTOM, backgroundColor=(0, 0, 0, 1), color=(0.2, 0.2, 0.2, 0.5), padLeft=1, padRight=1, top=1, width=75, value=0.0)
        self.loadingGauge.display = False
        spaceColor = Color(*COLOR_INSPACE)
        spaceColor.a = 1.0
        self.launchIcon = ButtonIcon(parent=inSpaceCont, align=uiconst.CENTER, width=44, height=44, iconSize=44, texturePath='res:/UI/Texture/classes/CarrierBay/tubeLaunch_Up.png', downTexture='res:/UI/Texture/classes/CarrierBay/tubeLaunch_Down.png', hoverTexture='res:/UI/Texture/classes/CarrierBay/tubeLaunch_Over.png', iconColor=spaceColor.GetRGBA(), showGlow=False)
        self.launchIcon.OnClick = self.LaunchFightersFromTube
        self.launchIcon.OnDropData = self.OnDropToSpace
        returnColor = Color(*COLOR_RETURNING)
        returnColor.a = 1.0
        self.scoopIcon = ButtonIcon(parent=deckCont, align=uiconst.CENTER, width=44, height=44, iconSize=44, texturePath='res:/UI/Texture/classes/CarrierBay/tubeRecall_Up.png', downTexture='res:/UI/Texture/classes/CarrierBay/tubeRecall_Down.png', hoverTexture='res:/UI/Texture/classes/CarrierBay/tubeRecall_Over.png', iconColor=returnColor.GetRGBA(), showGlow=False)
        self.scoopIcon.OnClick = self.ScoopFightersToTube
        self.scoopIcon.OnDropData = self.OnDropToTube
        self.landingStrip = LandingStrip(parent=deckCont)
        self.landingStrip.display = False
        self.launchingStrip = LaunchingStrip(parent=inSpaceCont)
        self.launchingStrip.display = False
        self.emptyTubeIcon = ButtonIcon(parent=deckCont, align=uiconst.CENTER, width=44, height=44, iconSize=44, texturePath='res:/UI/Texture/classes/CarrierBay/tubeOpen_Up.png', downTexture='res:/UI/Texture/classes/CarrierBay/tubeOpen_Down.png', hoverTexture='res:/UI/Texture/classes/CarrierBay/tubeOpen_Over.png', showGlow=False)
        self.emptyTubeIcon.OnDropData = self.OnDropToTube
        self.squadronInSpace = FightersHealthGauge(name='squadronInSpace', parent=inSpaceCont, align=uiconst.CENTER, width=86, height=86, state=TUBE_STATE_INSPACE, tubeFlagID=self.tubeFlagID)
        self.squadronInSpace.display = False
        self.squadronInTube = FightersHealthGauge(name='squadronInTube', parent=deckCont, align=uiconst.CENTER, width=86, height=86, state=TUBE_STATE_READY, tubeFlagID=self.tubeFlagID)
        self.squadronInTube.OnDropData = self.OnDropToTube
        self.squadronInTube.display = False
        self.squadronInTube.GetMenu = self.GetLaunchMenu
        self.UpdateLaunchTubeContentUI()
        self.UpdateLaunchTubeStateUI()
        self.UpdateInSpaceUI()
        self.shipFighterState.signalOnFighterTubeStateUpdate.connect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.connect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.connect(self.OnFighterInSpaceUpdate)

    def Close(self):
        self.shipFighterState.signalOnFighterTubeStateUpdate.disconnect(self.OnFighterTubeStateUpdate)
        self.shipFighterState.signalOnFighterTubeContentUpdate.disconnect(self.OnFighterTubeContentUpdate)
        self.shipFighterState.signalOnFighterInSpaceUpdate.disconnect(self.OnFighterInSpaceUpdate)

    def LaunchFightersFromTube(self):
        self.controller.LaunchFightersFromTube(self.tubeFlagID)

    def ScoopFightersToTube(self):
        fighterInSpace = self.shipFighterState.GetFightersInSpace(self.tubeFlagID)
        self.controller.ScoopFightersToTube(fighterInSpace.itemID, self.tubeFlagID)

    def OnDropToSpace(self, dragSource, dragData):
        data = dragData[0]
        if data.tubeFlagID == self.tubeFlagID and data.squadronState == TUBE_STATE_READY:
            self.LaunchFightersFromTube()

    def OnDropToTube(self, dragSource, dragData):
        data = dragData[0]
        if data.__guid__ == 'uicls.FightersHealthGauge':
            if data.tubeFlagID == self.tubeFlagID and data.squadronState == TUBE_STATE_INSPACE:
                self.ScoopFightersToTube()
        elif data.__guid__ in ('xtriui.InvItem', 'listentry.InvItem'):
            tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
            if tubeStatus.statusID in (TUBE_STATE_EMPTY, TUBE_STATE_READY):
                fighterID = data.itemID
                self.controller.LoadFightersToTube(fighterID, self.tubeFlagID)

    def UnloadTubeToFighterBay(self):
        self.controller.UnloadTubeToFighterBay(self.tubeFlagID)

    def UpdateLaunchTubeContentUI(self):
        fighterInTube = self.shipFighterState.GetFightersInTube(self.tubeFlagID)
        if fighterInTube is not None:
            self.squadronInTube.display = True
            self.launchIcon.display = True
            self.squadronInTube.LoadFighterIcon(fighterInTube.typeID)
            self.squadronInTube.SetSquadronSize(fighterInTube.squadronSize)
        else:
            self.squadronInTube.display = False
            self.launchIcon.display = False

    def UpdateLaunchTubeStateUI(self):
        tubeStatus = self.shipFighterState.GetTubeStatus(self.tubeFlagID)
        self.UpdateStatusUI(tubeStatus)
        if tubeStatus.endTime:
            if tubeStatus.statusID == TUBE_STATE_SCOOPING:
                self.landingStrip.display = True
                self.scoopIcon.display = False
            elif tubeStatus.statusID == TUBE_STATE_LAUNCHING:
                self.launchingStrip.display = True
                self.launchIcon.display = False
            else:
                self.loadingGauge.display = True
                now = gametime.GetSimTime()
                duration = tubeStatus.endTime - tubeStatus.startTime
                loadingProgress = max(0.0, min(1.0, (now - tubeStatus.startTime) / duration))
                self.loadingGauge.SetValue(loadingProgress, animate=False)
                remainingTime = tubeStatus.endTime - now
                remainingTimeSeconds = max(float(remainingTime) / SEC, 0.1)
                self.loadingGauge.SetValueTimed(1.0, remainingTimeSeconds)
                self.tubeStatusLabel.top = -2
        else:
            self.loadingGauge.SetValue(0)
            self.loadingGauge.display = False
            self.landingStrip.display = False
            self.launchingStrip.display = False
            self.tubeStatusLabel.top = 0
        if tubeStatus.statusID == TUBE_STATE_EMPTY:
            self.emptyTubeIcon.display = True
        else:
            self.emptyTubeIcon.display = False

    def UpdateStatusUI(self, tubeStatus):
        stateText = LABEL_BY_STATE[tubeStatus.statusID]
        self.tubeStatusLabel.text = GetByLabel(stateText)
        stateColor = Color(*COLOR_BY_STATE[tubeStatus.statusID])
        stateColor.a = 0.1
        self.stateContBG.color = stateColor.GetRGBA()
        stateColor.a = 0.8
        self.tubeStatusLabel.SetTextColor(stateColor.GetRGBA())

    def UpdateInSpaceUI(self):
        fighterInSpace = self.shipFighterState.GetFightersInSpace(self.tubeFlagID)
        if fighterInSpace is not None:
            self.scoopIcon.display = True
            self.squadronInSpace.display = True
            self.squadronInSpace.LoadFighterIcon(fighterInSpace.typeID)
            self.squadronInSpace.SetSquadronSize(fighterInSpace.squadronSize)
        else:
            self.scoopIcon.display = False
            self.squadronInSpace.display = False

    def GetLaunchMenu(self):
        return [('Unload from launch tube', self.UnloadTubeToFighterBay)]

    def OnFighterTubeStateUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            self.UpdateLaunchTubeStateUI()

    def OnFighterTubeContentUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            self.UpdateLaunchTubeContentUI()

    def OnFighterInSpaceUpdate(self, tubeFlagID):
        if tubeFlagID == self.tubeFlagID:
            self.UpdateInSpaceUI()


class StripCont(Container):
    default_height = 86
    default_width = 86
    default_align = uiconst.TOPLEFT
    default_lightTexture = None
    default_gradientTexture = None
    default_startVal = (0.0, -1.0)
    default_endVal = (0.0, 1.0)
    default_textureAlign = uiconst.CENTERTOP

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        stripHeight = 9
        top = 6
        for i in xrange(8):
            sprite = Sprite(parent=self, align=self.default_textureAlign, width=35, height=stripHeight, top=top, texturePath=self.default_lightTexture, state=uiconst.UI_DISABLED)
            offset = 0.1 * i
            uicore.animations.SpMaskTo(sprite, startVal=self.default_startVal, endVal=self.default_endVal, texturePath=self.default_gradientTexture, duration=1.0, loops=uiconst.ANIM_REPEAT, timeOffset=offset)
            top += stripHeight


class LandingStrip(StripCont):
    default_lightTexture = 'res:/UI/Texture/classes/CarrierBay/animLightsLanding.png'
    default_gradientTexture = 'res:/UI/Texture/Classes/Animations/maskToGradientDown.png'
    default_startVal = (0.0, -1.0)
    default_endVal = (0.0, 1.0)
    default_textureAlign = uiconst.CENTERTOP


class LaunchingStrip(StripCont):
    default_lightTexture = 'res:/UI/Texture/classes/CarrierBay/animLightsLaunch.png'
    default_gradientTexture = 'res:/UI/Texture/Classes/Animations/maskToGradientUp.png'
    default_startVal = (0.0, 1.0)
    default_endVal = (0.0, -1.0)
    default_textureAlign = uiconst.CENTERBOTTOM


class SquadronNumber(Container):
    default_width = 14
    default_height = 14
    default_align = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.squadNrText = EveLabelSmall(parent=self, left=4, top=2)
        squadNrSprite = Sprite(parent=self, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ShipUI/Fighters/squadNumberFlag.png', pos=(1, 1, 14, 14))

    def SetText(self, tubeFlagID):
        squadronNumber = SLOTNUMBER_BY_TUBEFLAG[tubeFlagID]
        self.squadNrText.text = squadronNumber
