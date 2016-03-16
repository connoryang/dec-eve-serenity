#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\careerAgentEntry.py
from carbonui import const as uiconst, const
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.common.lib import appConst as const, appConst
import localization
import uicontrols
import uiprimitives
import uiutil

class CareerAgentEntry(uicontrols.SE_BaseClassCore):

    def Startup(self, *etc):
        self.photoSvc = sm.StartService('photo')
        self.sr.cellContainer = uiprimitives.Container(name='CellContainer', parent=self, padding=(2, 2, 2, 2))
        self.sr.agentContainer = uiprimitives.Container(parent=self.sr.cellContainer, align=uiconst.TORIGHT, state=uiconst.UI_NORMAL, width=330)
        self.sr.careerContainer = uiprimitives.Container(parent=self.sr.cellContainer, align=uiconst.TOALL, padding=(const.defaultPadding * 2,
         const.defaultPadding,
         const.defaultPadding,
         const.defaultPadding))
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM)

    def Load(self, node):
        agent = node.agent
        agentID = agent.agentID
        career = node.career
        agentStation = node.agentStation
        agentStationID = agentStation.stationID
        agentSystemID = agentStation.solarSystemID
        agentConstellationID = sm.GetService('map').GetConstellationForSolarSystem(agentSystemID)
        agentRegionID = sm.GetService('map').GetRegionForSolarSystem(agentSystemID)
        agentNameText = cfg.eveowners.Get(agentID).name
        self.sr.agentContainer.Flush()
        agentSprite = uiprimitives.Sprite(name='AgentSprite', parent=self.sr.agentContainer, align=uiconst.RELATIVE, width=128, height=128, state=uiconst.UI_NORMAL, top=6)
        agentTextContainer = uiprimitives.Container(name='TextContainer', parent=self.sr.agentContainer, align=uiconst.TOPLEFT, width=190, height=77, left=140)
        uicontrols.EveLabelLarge(text=agentNameText, parent=agentTextContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, padTop=const.defaultPadding)
        self.photoSvc.GetPortrait(agentID, 128, agentSprite)
        menuContainer = agentSprite
        menuContainer.GetMenu = lambda *args: self.GetAgentMenu(agent, agentStation)
        menuContainer.id = agentID
        menuContainer.OnClick = self.TalkToAgent
        menuContainer.cursor = uiconst.UICURSOR_SELECT
        agentButton = uicontrols.Button(parent=self.sr.agentContainer, align=uiconst.BOTTOMRIGHT, label=localization.GetByLabel('UI/Generic/Unknown'), fixedwidth=196, left=const.defaultPadding, top=const.defaultPadding)
        agentButton.func = self.SetDestination
        agentButton.args = (agentStationID,)
        agentButton.SetLabel(localization.GetByLabel('UI/Commands/SetDestination'))
        agentButton.state = uiconst.UI_NORMAL
        if session.stationid is None and agentSystemID == session.solarsystemid:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameSystem')
            agentButton.func = self.DockAtStation
            agentButton.args = (agentStationID,)
            agentButton.SetLabel(localization.GetByLabel('UI/Tutorial/WarpToAgentStation'))
        elif session.stationid == agentStationID:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameStation')
            agentButton.func = self.TalkToAgent
            agentButton.args = (agentID,)
            agentButton.SetLabel(localization.GetByLabel('UI/Commands/StartConversation'))
        elif session.stationid is not None:
            hint = menuContainer.hint = localization.GetByLabel('UI/Tutorial/YouNeedToExitTheStation')
        else:
            hint = localization.GetByLabel('UI/Tutorial/ThisStationIsInADifferentSolarSystem', setDestination=localization.GetByLabel('UI/Commands/SetDestination'))
            if session.constellationid == agentConstellationID:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameConstellation')
            elif session.regionid == agentRegionID:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentInSameRegion')
            else:
                menuContainer.hint = localization.GetByLabel('UI/Tutorial/AgentNotInSameRegion')
        linktext = "<url=showinfo:%d//%d alt='%s'>%s</url>" % (agentStation.stationTypeID,
         agentStationID,
         hint,
         agentStation.stationName)
        linkObject = uicontrols.EveLabelMedium(text=linktext, parent=agentTextContainer, state=uiconst.UI_NORMAL, align=uiconst.TOTOP, padTop=const.defaultPadding, padLeft=const.defaultPadding, padRight=const.defaultPadding)
        uiutil.Flush(self.sr.careerContainer)
        careerText = localization.GetByLabel('UI/Generic/Unknown')
        careerDesc = localization.GetByLabel('UI/Generic/Unknown')
        if career == const.agentDivisionBusiness:
            careerText = localization.GetByLabel('UI/Tutorial/Business')
            careerDesc = localization.GetByLabel('UI/Tutorial/BusinessDesc')
        elif career == const.agentDivisionExploration:
            careerText = localization.GetByLabel('UI/Tutorial/Exploration')
            careerDesc = localization.GetByLabel('UI/Tutorial/ExplorationDesc')
        elif career == const.agentDivisionIndustry:
            careerText = localization.GetByLabel('UI/Tutorial/Industry')
            careerDesc = localization.GetByLabel('UI/Tutorial/IndustryDesc')
        elif career == const.agentDivisionMilitary:
            careerText = localization.GetByLabel('UI/Tutorial/Military')
            careerDesc = localization.GetByLabel('UI/Tutorial/MilitaryDesc')
        elif career == const.agentDivisionAdvMilitary:
            careerText = localization.GetByLabel('UI/Tutorial/AdvMilitary')
            careerDesc = localization.GetByLabel('UI/Tutorial/AdvMilitaryDesc')
        uicontrols.EveCaptionMedium(text=careerText, parent=self.sr.careerContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        uicontrols.EveLabelMedium(text=careerDesc, parent=self.sr.careerContainer, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)

    def GetHeight(self, *args):
        node, width = args
        node.height = 162
        return node.height

    def DockAtStation(self, *args):
        if len(args) > 0:
            stationID = args[0]
            sm.StartService('menu').Dock(stationID)

    def GetAgentMenu(self, agent, station):
        m = sm.StartService('menu').CharacterMenu(agent.agentID)
        if station.solarSystemID == session.solarsystemid:
            m += [None]
            m += [(uiutil.MenuLabel('UI/Tutorial/WarpToAgentStation'), self.DockAtStation, (station[0],))]
        return m

    def TalkToAgent(self, *args):
        if len(args) > 0:
            if hasattr(args[0], 'id'):
                agentID = args[0].id
            else:
                agentID = args[0]
            sm.StartService('agents').InteractWith(agentID)

    def SetDestination(self, stationID):
        if stationID is not None:
            sm.StartService('starmap').SetWaypoint(stationID, clearOtherWaypoints=True)
