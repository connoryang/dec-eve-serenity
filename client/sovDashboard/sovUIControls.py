#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sovDashboard\sovUIControls.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
import carbonui.const as uiconst
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.graphs import GraphSegmentParams
from eve.client.script.ui.graphs.bargraph import BarGraphBarHorizontal
from eve.client.script.ui.graphs.circulargraph import CircularGraph
from sovDashboard import dashboardConst, CalculateStructureStatusFromStructureInfo, GetStructureStatusString
import blue
import uthread

class SovStructureStatusBase(Container):
    default_name = 'SovStructureStatusBase'
    default_align = uiconst.TOPLEFT
    statusLabel = None
    statusBar = None
    barBgColor = (0.0, 0.0, 0.0, 0.25)
    animateChange = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.barBgColor = attributes.Get('barBgColor', self.barBgColor)
        self.structureInfo = attributes.structureInfo
        self.sovSvc = sm.GetService('sov')
        self.PrepareStatusLabel()
        self.PrepareStatusBar()
        uthread.new(self.LoadStructureState)

    def PrepareStatusLabel(self):
        pass

    def PrepareStatusBar(self):
        pass

    def UpdateLabel(self):
        pass

    def UpdateStructureInfo(self, structureInfo, animate = True):
        self.structureInfo = structureInfo
        self.LoadStructureState(fullLoad=False, animate=animate)

    def LoadStructureState(self, fullLoad = True, animate = True):
        if self.destroyed:
            return
        self.UpdateLabel()
        structureStatus = CalculateStructureStatusFromStructureInfo(self.structureInfo)
        statusColor = dashboardConst.PRIMARYCOLOR_BY_STATUS[structureStatus]
        if structureStatus in (dashboardConst.STATUS_VULNERABLE, dashboardConst.STATUS_VULNERABLE_OVERTIME):
            self.statusBar.lineWidth = 1.0
            self.statusBar.display = True
            graphData = []
            proportion = 1.0 / float(self.vulnerableSegments)
            for i in xrange(self.vulnerableSegments):
                if i % 2:
                    graphData.append(GraphSegmentParams(proportion, (0.0, 0.0, 0.0, 0.0)))
                else:
                    graphData.append(GraphSegmentParams(proportion, statusColor))

            self.statusBar.LoadGraphData(graphData, animateIn=self.animateChange)
        elif structureStatus == dashboardConst.STATUS_REINFORCED:
            self.statusBar.lineWidth = 1.0
            self.statusBar.display = True
            graphData = []
            proportion = 1.0 / float(self.reinforcedSegments)
            for i in xrange(self.reinforcedSegments):
                if i % 2:
                    graphData.append(GraphSegmentParams(proportion, (0.0, 0.0, 0.0, 0.0)))
                else:
                    graphData.append(GraphSegmentParams(proportion, statusColor))

            self.statusBar.LoadGraphData(graphData, animateIn=self.animateChange)
        elif structureStatus == dashboardConst.STATUS_NODEFIGHT:
            self.statusBar.lineWidth = 2.0
            self.statusBar.display = True
            campaignState = self.structureInfo.get('campaignState', None)
            graphData = self.GetGraphData(campaignState)
            if isinstance(self, SovStructureStatusCircular):
                graphData.reverse()
            if fullLoad or len(self.statusBar.segments) != len(graphData):
                self.statusBar.LoadGraphData(graphData, animateIn=self.animateChange)
            else:
                self.statusBar.UpdateGraphData(graphData, animate=animate)
            if self.statusLabel and not self.statusLabel.display:
                self.statusBar.padTop = (self.height - self.statusBar.height) / 2
            self.statusBar.display = True
        else:
            self.statusBar.display = False

    def GetSortedScoresAndTeamIDs(self, scoreByTeamID):

        def SortTeam(teamID, score):
            if teamID == session.allianceid:
                return 1
            return score

        sortedScoreAndTeamIDs = sorted([ (x, y) for x, y in scoreByTeamID.iteritems() ], key=lambda d: SortTeam(d[0], d[1]))
        return sortedScoreAndTeamIDs

    def GetGraphData(self, campaignState):
        eventType, defenderID, startTime, scoreByTeamID = campaignState
        graphData = []
        defendingGraphData = None
        evenOdd = False
        teamIDs = [ teamID for teamID in scoreByTeamID.iterkeys() if teamID > 0 ]
        cfg.eveowners.Prime(teamIDs)
        sortedScoreAndTeamIDs = self.GetSortedScoresAndTeamIDs(scoreByTeamID)
        for teamID, proportion in sortedScoreAndTeamIDs:
            isMine = teamID == session.allianceid
            if teamID > 0:
                teamName = cfg.eveowners.Get(teamID).name
            else:
                teamName = None
            if defenderID and teamID == defenderID:
                defendingGraphData = GraphSegmentParams(proportion, dashboardConst.COLOR_DEFENDING, showMarker=isMine, tooltip=teamName)
                continue
            elif evenOdd:
                color = dashboardConst.COLOR_ATTACKING_ODD
                evenOdd = not evenOdd
            else:
                color = dashboardConst.COLOR_ATTACKING
                evenOdd = not evenOdd
            graphData.append(GraphSegmentParams(proportion, color, showMarker=isMine, tooltip=teamName))

        if defendingGraphData:
            graphData.append(defendingGraphData)
        return graphData


class SovStructureStatusHorizontal(SovStructureStatusBase):
    default_name = 'SovStructureStatusHorizontal'
    default_align = uiconst.TOPLEFT
    default_width = 200
    default_height = 64
    reinforcedSegments = 21
    vulnerableSegments = 21

    def ApplyAttributes(self, attributes):
        self.showLabel = attributes.get('showLabel', True)
        self.centerLabel = attributes.get('centerLabel', False)
        self.autoHeight = attributes.get('autoHeight', False)
        SovStructureStatusBase.ApplyAttributes(self, attributes)

    def PrepareStatusLabel(self):
        if not self.showLabel:
            return
        self.statusLabel = EveLabelMedium(parent=self, align=uiconst.TOTOP, padding=(5, 5, 5, 5), state=uiconst.UI_NORMAL, bold=True)

    def PrepareStatusBar(self):
        self.statusBar = BarGraphBarHorizontal(parent=self, align=uiconst.TOTOP, pos=(0, 0, 0, 5), padding=(5, 0, 5, 5), bgColor=self.barBgColor)

    def UpdateLabel(self):
        if not self.statusLabel:
            return
        structureStatus = CalculateStructureStatusFromStructureInfo(self.structureInfo)
        structureStatusString = GetStructureStatusString(self.structureInfo)
        if structureStatusString:
            if self.centerLabel:
                structureStatusString = '<center>%s</center>' % structureStatusString
            textColor = dashboardConst.PRIMARYCOLOR_BY_STATUS.get(structureStatus)
            self.statusLabel.color = textColor
            self.statusLabel.text = structureStatusString
            self.statusLabel.display = True
        else:
            self.statusLabel.display = False

    def LoadStructureState(self, *args, **kwargs):
        SovStructureStatusBase.LoadStructureState(self, *args, **kwargs)
        if self.autoHeight:
            height = 0
            if self.statusLabel and self.statusLabel.display:
                height = self.statusLabel.height + self.statusLabel.padTop + self.statusLabel.padBottom
            if self.statusBar and self.statusBar.display:
                height += self.statusBar.height + self.statusBar.padTop + self.statusBar.padBottom
            self.height = height


class SovStructureStatusCircular(SovStructureStatusBase):
    default_name = 'SovStructureStatusCircular'
    default_align = uiconst.TOPLEFT
    default_width = 32
    default_height = 32
    reinforcedSegments = 40
    vulnerableSegments = 40

    def ApplyAttributes(self, attributes):
        SovStructureStatusBase.ApplyAttributes(self, attributes)

    def PrepareStatusBar(self):
        self.statusBar = CircularGraph(parent=self, align=uiconst.TOPLEFT, radius=self.width / 2, lineWidth=2, bgLineWidth=3, colorBg=self.barBgColor)


class SovStatusTimeLabel(EveLabelMedium):
    default_name = 'sovStatusTimeLabel'
    default_state = uiconst.UI_DISABLED

    def ApplyAttributes(self, attributes):
        EveLabelMedium.ApplyAttributes(self, attributes)
        self.structureInfo = attributes.structureInfo
        self.UpdateTime()
        self.timeThread = AutoTimer(500, self.UpdateTime_thread)

    def UpdateTime_thread(self):
        if self.destroyed:
            self.timeThread = None
            return
        if not self.parent or not self.parent.display or not self.display:
            return
        self.UpdateTime()

    def UpdateTime(self):
        currentStatus = CalculateStructureStatusFromStructureInfo(self.structureInfo)
        textColor = dashboardConst.PRIMARYCOLOR_BY_STATUS.get(currentStatus)
        self.color = textColor
        statusString, timeString = GetStructureStatusString(self.structureInfo, getTimeString=True)
        if self.align == uiconst.CENTER:
            timeString = '<center>%s</center>' % timeString
        self.text = timeString

    def Close(self):
        EveLabelMedium.Close(self)
        self.timeThread = None
