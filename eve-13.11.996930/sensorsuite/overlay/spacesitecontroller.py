#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\spacesitecontroller.py
from sensorsuite.error import InvalidClientStateError
import carbonui.const as uiconst
from sensorsuite.overlay.sitestore import SiteMapStore
from sensorsuite.overlay.spacelocations import SpaceLocations
import sensorsuite.overlay.const as overlayConst
import uthread2

class SpaceSiteController:

    def __init__(self, sensorSuiteService, michelle):
        self.sensorSuiteService = sensorSuiteService
        self.michelle = michelle
        self.siteMaps = SiteMapStore()
        self.spaceLocations = SpaceLocations()
        self.siteHandlers = {}

    def Clear(self):
        self.siteMaps.Clear()
        self.spaceLocations.Clear()

    def GetVisibleSiteTypes(self):
        return [ handler.siteType for handler in self.siteHandlers.itervalues() if handler.IsFilterEnabled() ]

    def GetVisibleSiteMap(self):
        return {siteData.siteID:siteData for siteData in self.siteMaps.IterSitesByKeys(*self.GetVisibleSiteTypes()) if self.GetSiteHandler(siteData.siteType).IsVisible(siteData)}

    def GetVisibleSites(self):
        return [ siteData for siteData in self.siteMaps.IterSitesByKeys(*self.GetVisibleSiteTypes()) if self.GetSiteHandler(siteData.siteType).IsVisible(siteData) ]

    def IsSiteVisible(self, siteData):
        handler = self.GetSiteHandler(siteData.siteType)
        return handler.IsFilterEnabled() and handler.IsVisible(siteData)

    def AddSiteHandler(self, siteType, handler):
        handler.SetSiteController(self)
        self.siteHandlers[siteType] = handler

    def GetSiteHandler(self, siteType):
        return self.siteHandlers[siteType]

    def UpdateSiteVisibility(self):
        for location in self.spaceLocations.GetLocations():
            siteData = location.siteData
            removeResult = False
            if not self.IsSiteVisible(siteData):
                removeResult = True
            elif not (self.sensorSuiteService.IsOverlayActive() or self.sensorSuiteService.sensorSweepActive):
                removeResult = True
            if removeResult:
                self.RemoveResult(siteData)

        for siteData in self.GetVisibleSites():
            if not self.spaceLocations.ContainsSite(siteData.siteID):
                self.AddSiteToSpace(siteData)

    def NotifySiteChanged(self, siteData):
        self.sensorSuiteService.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SITE_CHANGED, siteData)

    def RemoveResult(self, siteData):
        if self.spaceLocations.ContainsSite(siteData.siteID):
            locData = self.spaceLocations.GetBySiteID(siteData.siteID)
            self.spaceLocations.RemoveLocation(siteData.siteID)
            locData.bracket.state = uiconst.UI_DISABLED
            locData.bracket.DoExitAnimation(callback=lambda timeoutSeconds: self.ClearBracketAfterTimeout(timeoutSeconds, locData.bracket, locData.ballRef()))
        self.NotifySiteChanged(siteData)

    def ClearBracketAfterTimeout(self, timeoutSeconds, bracket, ball):
        uthread2.StartTasklet(self._ClearBracketAfterTimeout_Thread, timeoutSeconds, bracket, ball)

    def _ClearBracketAfterTimeout_Thread(self, timeoutSeconds, bracket, ball):
        uthread2.SleepSim(timeoutSeconds)
        self.CloseBracketAndBall(bracket, ball)

    def AddSiteToSpace(self, siteData, animate = True):
        if not self.sensorSuiteService.IsSolarSystemReady():
            return
        if not self.IsSiteVisible(siteData):
            return
        if self.sensorSuiteService.IsOverlayActive() or self.sensorSuiteService.sensorSweepActive:
            bracket = self.MakeSiteLocationMarker(siteData)
            if animate:
                bracket.DoEntryAnimation(enable=True)
        self.NotifySiteChanged(siteData)

    def MakeSiteLocationMarker(self, siteData):
        ballpark = self.michelle.GetBallpark()
        if ballpark is None:
            raise InvalidClientStateError('ballpark has gone missing')
        ball = ballpark.AddClientSideBall(siteData.position, isGlobal=True)
        siteData.ballID = ball.id
        bracketClass = siteData.GetBracketClass()
        bracket = bracketClass(name=str(siteData.siteID), parent=uicore.layer.sensorSuite, data=siteData)
        tracker = bracket.projectBracket
        tracker.trackBall = ball
        tracker.name = str(siteData.siteID)
        self.spaceLocations.AddLocation(ball, bracket, siteData)
        if self.sensorSuiteService.IsOverlayActive():
            bracket.state = uiconst.UI_NORMAL
        else:
            bracket.state = uiconst.UI_DISABLED
        return bracket

    def CloseBracketAndBall(self, bracket, ball):
        bracket.Close()
        if ball is not None:
            ballpark = self.michelle.GetBallpark()
            if ball.id in ballpark.balls:
                ballpark.RemoveClientSideBall(ball.id)

    def ClearFromBallpark(self):
        ballpark = self.michelle.GetBallpark()
        if ballpark is not None:
            for data in self.spaceLocations.IterLocations():
                ball = data.ballRef()
                if ball is not None:
                    if ball.id in ballpark.balls:
                        ballpark.RemoveClientSideBall(ball.id)

    def ProcessSiteDataUpdate(self, addedSites, removedSites, siteType, addSiteDataMethod):
        removedSiteData = []
        sitesById = self.siteMaps.GetSiteMapByKey(siteType)
        for siteID in removedSites:
            if siteID in sitesById:
                siteData = sitesById.pop(siteID)
                removedSiteData.append(siteData)
                self.RemoveResult(siteData)

        for siteID, rawSiteData in addedSites.iteritems():
            siteData = addSiteDataMethod(siteID, *rawSiteData)
            self.siteMaps.AddSiteToMap(siteType, siteID, siteData)
            try:
                self.AddSiteToSpace(siteData)
            except InvalidClientStateError:
                continue

        if removedSiteData:
            self.sensorSuiteService.UpdateScanner(removedSiteData)
