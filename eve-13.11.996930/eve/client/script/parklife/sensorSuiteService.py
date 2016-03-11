#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\sensorSuiteService.py
import math
from brennivin.messenger import Messenger
from carbon.common.lib import telemetry
from carbon.common.lib.const import SEC
from carbon.common.script.sys import service
from carbon.common.script.util.logUtil import LogException
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import IsUnder
from eve.common.lib.appConst import AU
from locks import RLock
from sensorsuite.overlay.const import SWEEP_CYCLE_TIME, SWEEP_START_GRACE_TIME_SEC, SWEEP_START_GRACE_TIME, SUPPRESS_GFX_WARPING, SUPPRESS_GFX_NO_UI
import sensorsuite.overlay.const as overlayConst
from sensorsuite.overlay.gfxhandler import GfxHandler
from sensorsuite.overlay.sitetype import *
from sensorsuite.overlay.anomalies import AnomalyHandler
from sensorsuite.overlay.bookmarks import BookmarkHandler, CorpBookmarkHandler
from sensorsuite.overlay.spacesitecontroller import SpaceSiteController
from sensorsuite.overlay.staticsites import StaticSiteHandler
from sensorsuite.overlay.controllers.probescanner import ProbeScannerController
from sensorsuite.overlay.missions import MissionHandler
from sensorsuite.overlay.signatures import SignatureHandler
import uthread
import carbonui.const as uiconst
import audio2
import trinity
from sensorsuite import common
from sensorsuite.error import InvalidClientStateError
import gametime
import uthread2
SENSOR_SUITE_ENABLED = 'sensorSuiteEnabled'
MAX_MOUSEOVER_RANGE = 40.0
MAX_MOUSEOVER_RANGE_SQUARED = MAX_MOUSEOVER_RANGE ** 2
MAX_OVERLAPPING_RANGE_SQUARED = 900.0
MAX_RTPC_VALUE = 99
AUDIO_STATE_BY_DIFFICULTY = {common.SITE_DIFFICULTY_EASY: 'ui_scanner_state_difficulty_easy',
 common.SITE_DIFFICULTY_MEDIUM: 'ui_scanner_state_difficulty_medium',
 common.SITE_DIFFICULTY_HARD: 'ui_scanner_state_difficulty_hard'}
BRACKET_OVERLAP_DISTANCE = 8
SWEEP_CYCLE_TIME_SEC = float(SWEEP_CYCLE_TIME) / SEC

class SensorSuiteService(service.Service):
    __guid__ = 'svc.sensorSuite'
    __notifyevents__ = ['OnSessionChanged',
     'OnSignalTrackerFullState',
     'OnSignalTrackerAnomalyUpdate',
     'OnSignalTrackerSignatureUpdate',
     'OnUpdateWindowPosition',
     'OnReleaseBallpark',
     'DoBallClear',
     'OnWarpStarted',
     'OnWarpFinished',
     'OnSystemScanDone',
     'OnSpecialFX',
     'OnShowUI',
     'OnHideUI',
     'OnRefreshBookmarks',
     'OnAgentMissionChanged']
    __dependencies__ = ['sceneManager',
     'michelle',
     'audio',
     'scanSvc',
     'viewState',
     'bookmarkSvc']
    __startupdependencies__ = []

    def Run(self, *args):
        service.Service.Run(self)
        self.isOverlayActive = True
        self.toggleLock = RLock()
        self.messenger = Messenger()
        self.gfxHandler = GfxHandler(self, self.sceneManager, self.michelle)
        self.siteController = SpaceSiteController(self, self.michelle)
        self.siteController.AddSiteHandler(ANOMALY, AnomalyHandler())
        self.siteController.AddSiteHandler(SIGNATURE, SignatureHandler())
        self.siteController.AddSiteHandler(STATIC_SITE, StaticSiteHandler())
        self.siteController.AddSiteHandler(BOOKMARK, BookmarkHandler(self, self.bookmarkSvc))
        self.siteController.AddSiteHandler(CORP_BOOKMARK, CorpBookmarkHandler(self, self.bookmarkSvc))
        self.siteController.AddSiteHandler(MISSION, MissionHandler(self.bookmarkSvc))
        self.Initialize()

    def IsSweepDone(self):
        return self.systemReadyTime and not self.sensorSweepActive

    def IsSolarSystemReady(self):
        return self.systemReadyTime is not None

    def NotifySweepStartedIfRequired(self, handler, messageName):
        if messageName is overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED and self.sweepStartedData is not None:
            uthread.new(handler, *self.sweepStartedData)

    def Subscribe(self, messageName, handler):
        self.NotifySweepStartedIfRequired(handler, messageName)
        self.messenger.SubscribeToMessage(messageName, handler)

    def Unsubscribe(self, messageName, handler):
        self.messenger.UnsubscribeFromMessage(messageName, handler)

    def SendMessage(self, messageName, *args, **kwargs):
        self.messenger.SendMessage(messageName, *args, **kwargs)

    def Initialize(self):
        self.siteController.Clear()
        self.probeScannerController = ProbeScannerController(self.scanSvc, self.michelle, self.siteController)
        self.locatorFadeInTimeSec = 0.25
        self.doMouseTrackingUpdates = False
        self.systemReadyTime = None
        self.sitesUnderCursor = set()
        leftPush, rightPush = uicore.layer.sidePanels.GetSideOffset()
        self.OnUpdateWindowPosition(leftPush, rightPush)
        self.sensorSweepActive = False
        self.sweepStartedData = None

    def UpdateScanner(self, removedSites):
        targetIDs = []
        for siteData in removedSites:
            if siteData.GetSiteType() in (ANOMALY, SIGNATURE):
                targetIDs.append(siteData.targetID)

        if targetIDs:
            self.scanSvc.ClearResults(*targetIDs)

    def InjectScannerResults(self, siteType):
        sitesById = self.siteController.siteMaps.GetSiteMapByKey(siteType)
        self.probeScannerController.InjectSiteScanResults(sitesById.itervalues())

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, *args, **kw):
        if shipID == session.shipid:
            if guid is not None and 'effects.JumpOut' in guid:
                self.LogInfo('Jumping out, hiding the overlay')
                self._Hide()

    def OnSessionChanged(self, isRemote, session, change):
        if 'solarsystemid' in change:
            self.Reset()
            oldSolarSystemID, newSolarSystemID = change['solarsystemid']
            if newSolarSystemID is not None:
                self.Initialize()
                self._SetOverlayActive(settings.char.ui.Get(SENSOR_SUITE_ENABLED, True))
                self.LogInfo('Entered new system', newSolarSystemID)
                sm.RemoteSvc('scanMgr').SignalTrackerRegister()
                for siteType in (BOOKMARK, CORP_BOOKMARK, MISSION):
                    self.siteController.GetSiteHandler(siteType).LoadSites(newSolarSystemID)

    def OnReleaseBallpark(self):
        self.Reset()

    def DoBallClear(self, _):
        self.LogInfo('Ballpark is ready so we start the sweep timer')
        self.systemReadyTime = gametime.GetSimTime()
        self.StartSensorSweep()

    def Reset(self):
        self.siteController.ClearFromBallpark()
        self.siteController.Clear()
        uicore.layer.sensorSuite.Flush()
        self.gfxHandler.StopGfxSwipe()
        self.gfxHandler.StopSwipeThread()

    def IsOverlayActive(self):
        return self.isOverlayActive

    def ToggleOverlay(self):
        with self.toggleLock:
            self.LogInfo('Toggle Overlay')
            if self.IsOverlayActive():
                self.DisableSensorOverlay()
            else:
                self.EnableSensorOverlay()

    def DisableSensorOverlay(self):
        self.LogInfo('DisableSensorOverlay')
        if self.IsOverlayActive():
            self._SetOverlayActive(False)
            if not self.sensorSweepActive:
                self._Hide()
            self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_DISABLED)

    def EnableSensorOverlay(self):
        self.LogInfo('EnableSensorOverlay')
        if not self.IsOverlayActive():
            self._SetOverlayActive(True)
            if not self.sensorSweepActive:
                self._Show()
            self.messenger.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_ENABLED)

    def _SetOverlayActive(self, isActive):
        self.isOverlayActive = isActive
        settings.char.ui.Set(SENSOR_SUITE_ENABLED, isActive)

    def _Show(self):
        self.LogInfo('Showing overlay')
        try:
            if not self.sensorSweepActive:
                self.UpdateVisibleSites()
                self.audio.SendUIEvent('ui_scanner_stop')
                self.EnableMouseTracking()
        except InvalidClientStateError:
            pass

    def _Hide(self):
        self.LogInfo('Hiding overlay')
        self.gfxHandler.StopGfxSwipe()
        self.UpdateVisibleSites()
        self.audio.SendUIEvent('ui_scanner_stop')
        self.doMouseTrackingUpdates = False

    def EnableMouseTracking(self):
        if not self.doMouseTrackingUpdates:
            self.doMouseTrackingUpdates = True
            uthread.new(self.UpdateMouseTracking).context = 'sensorSuite::UpdateMouseTracking'

    def StartSensorSweep(self):
        uthread.new(self._DoSystemEnterScan)

    def TryFadeOutBracketAndReturnCurveSet(self, curveSet, points, siteData, totalDuration):
        try:
            locatorData = self.siteController.spaceLocations.GetBySiteID(siteData.siteID)
            curveSet = animations.FadeTo(locatorData.bracket, startVal=0.0, endVal=1.0, duration=totalDuration, curveType=points, curveSet=curveSet)
        except KeyError:
            pass

        return curveSet

    def GetSiteListOrderedByDelay(self, ballpark, sweepCycleTimeSec, viewAngleInPlane):
        myBall = ballpark.GetBall(ballpark.ego)
        mx, mz = myBall.x, myBall.z
        sitesOrdered = []
        pi2 = math.pi * 2
        for siteData in self.siteController.GetVisibleSites():
            self.LogInfo('checking site', siteData.siteID)
            if IsSiteInstantlyAccessible(siteData):
                sitesOrdered.append((0, siteData))
                continue
            x, y, z = siteData.position
            dx, dz = x - mx, z - mz
            angle = math.atan2(-dz, dx) - viewAngleInPlane
            angle %= pi2
            ratioOfCircle = angle / pi2
            delay = SWEEP_START_GRACE_TIME_SEC + sweepCycleTimeSec * ratioOfCircle
            sitesOrdered.append((delay, siteData))

        sitesOrdered.sort()
        return sitesOrdered

    def SetupSiteSweepAnimation(self, sitesOrdered):
        curveSet = animations.CreateCurveSet(useRealTime=False)
        for delay, siteData in sitesOrdered:
            points, totalDuration = self.GetLocationFlashCurve(delay)
            curveSet = self.TryFadeOutBracketAndReturnCurveSet(curveSet, points, siteData, totalDuration)

    def _DoSystemEnterScan(self):
        self.LogInfo('_DoSystemEnterScan entered')
        if session.solarsystemid is None:
            return
        self.sensorSweepActive = True
        try:
            self.CreateResults()
            viewAngleInPlane = self.gfxHandler.GetViewAngleInPlane()
        except InvalidClientStateError:
            self.sensorSweepActive = False
            return

        ballpark = self.michelle.GetBallpark()
        if ballpark is None:
            return
        self.LogInfo('Sensor sweep stating from angle', viewAngleInPlane)
        sitesOrdered = self.GetSiteListOrderedByDelay(ballpark, SWEEP_CYCLE_TIME_SEC, viewAngleInPlane)
        if self.IsOverlayActive():
            self.SetupSiteSweepAnimation(sitesOrdered)
            self.gfxHandler.StartGfxSwipeThread(viewAngleInPlane=viewAngleInPlane)
            self.audio.SendUIEvent('ui_scanner_start')
            uthread.new(self.PlayResultEffects, sitesOrdered)
        else:
            self.sensorSweepActive = False
            self._Hide()
        self.LogInfo('Sweep started observers notified')
        self.sweepStartedData = (self.systemReadyTime,
         SWEEP_CYCLE_TIME_SEC,
         viewAngleInPlane,
         sitesOrdered,
         SWEEP_START_GRACE_TIME_SEC)
        self.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_STARTED, *self.sweepStartedData)

    @telemetry.ZONE_METHOD
    def ShowSiteDuringSweep(self, locatorData, scene, siteData, sleepTimeSec, soundLocators, vectorCurve):
        ball = locatorData.ballRef()
        if ball is None:
            return
        audio = audio2.AudEmitter('sensor_overlay_site_%s' % str(siteData.siteID))
        obs = trinity.TriObserverLocal()
        obs.front = (0.0, -1.0, 0.0)
        obs.observer = audio
        vectorSequencer = trinity.TriVectorSequencer()
        vectorSequencer.operator = trinity.TRIOP_MULTIPLY
        vectorSequencer.functions.append(ball)
        vectorSequencer.functions.append(vectorCurve)
        tr = trinity.EveRootTransform()
        tr.name = 'sensorSuiteSoundLocator_%s' % str(siteData.siteID)
        tr.translationCurve = vectorSequencer
        tr.observers.append(obs)
        scene.objects.append(tr)
        soundLocators.append(tr)
        uthread2.SleepSim(sleepTimeSec)
        if siteData.GetSiteType() == ANOMALY:
            audio.SendEvent('ui_scanner_result_anomaly')
        elif siteData.GetSiteType() == SIGNATURE:
            audio.SendEvent('ui_scanner_result_signature')
        locatorData.bracket.DoEntryAnimation(enable=False)
        locatorData.bracket.state = uiconst.UI_DISABLED

    @telemetry.ZONE_METHOD
    def PlayResultEffects(self, sitesOrdered):
        self.LogInfo('PlayResultEffects')
        scene = self.sceneManager.GetRegisteredScene('default')
        soundLocators = []
        invAU = 1.0 / AU
        vectorCurve = trinity.TriVectorCurve()
        vectorCurve.value = (invAU, invAU, invAU)
        self.EnableMouseTracking()
        try:
            startTimeSec = float(self.systemReadyTime + SWEEP_START_GRACE_TIME) / SEC
            lastPlayTimeSec = startTimeSec
            for delaySec, siteData in sitesOrdered:
                locatorData = self.siteController.spaceLocations.GetBySiteID(siteData.siteID)
                if IsSiteInstantlyAccessible(siteData):
                    locatorData.bracket.state = uiconst.UI_NORMAL
                    locatorData.bracket.DoEntryAnimation(enable=True)
                    continue
                playTimeSec = startTimeSec + delaySec
                sleepTimeSec = playTimeSec - lastPlayTimeSec
                lastPlayTimeSec = playTimeSec
                self.ShowSiteDuringSweep(locatorData, scene, siteData, sleepTimeSec, soundLocators, vectorCurve)

            currentTimeSec = gametime.GetSimTime()
            endTimeSec = startTimeSec + SWEEP_CYCLE_TIME_SEC
            timeLeftSec = endTimeSec - currentTimeSec
            if timeLeftSec > 0:
                uthread2.SleepSim(timeLeftSec)
            self.audio.SendUIEvent('ui_scanner_stop')
            self.sensorSweepActive = False
            if not self.IsOverlayActive():
                self._Hide()
            else:
                for locatorData in self.siteController.spaceLocations.IterLocations():
                    if not IsSiteInstantlyAccessible(locatorData.siteData):
                        locatorData.bracket.DoEnableAnimation()
                        locatorData.bracket.state = uiconst.UI_NORMAL

            uthread2.SleepSim(1.0)
            self.DoScanEnded(sitesOrdered)
        except (InvalidClientStateError, KeyError):
            pass
        finally:
            self.sensorSweepActive = False
            if scene is not None:
                for tr in soundLocators:
                    if tr in scene.objects:
                        scene.objects.remove(tr)

            self.audio.SendUIEvent('ui_scanner_stop')
            self.SendMessage(overlayConst.MESSAGE_ON_SENSOR_OVERLAY_SWEEP_ENDED)

        self.UpdateVisibleSites()

    def DoScanEnded(self, sitesOrdered):
        self.LogInfo('DoScanEnded')
        if len(sitesOrdered) > 0:
            self.audio.SendUIEvent('ui_scanner_result_positive')
        else:
            self.audio.SendUIEvent('ui_scanner_result_negative')

    def CreateResults(self):
        self.LogInfo('CreateResults')
        self.gfxHandler.WaitForSceneReady()
        for siteData in self.siteController.GetVisibleSites():
            self.siteController.AddSiteToSpace(siteData, animate=False)

    def GetLocationFlashCurve(self, delay):
        totalDuration = delay + self.locatorFadeInTimeSec
        points = []
        totalTime = 0
        for keyDuration, keyValue in ((delay, 0.0), (self.locatorFadeInTimeSec, 1.0)):
            totalTime += keyDuration
            points.append((totalTime / totalDuration, keyValue))

        return (points, totalDuration)

    def GetBracketByBallID(self, ballID):
        return self.siteController.spaceLocations.GetBracketByBallID(ballID)

    def GetBracketBySiteID(self, siteID):
        return self.siteController.spaceLocations.GetBracketBySiteID(siteID)

    def OnRefreshBookmarks(self):
        self.LogInfo('OnRefreshBookmarks')
        for siteType in (BOOKMARK, CORP_BOOKMARK):
            self.siteController.GetSiteHandler(siteType).UpdateSites(session.solarsystemid)

    def OnAgentMissionChanged(self, *args, **kwargs):
        self.siteController.GetSiteHandler(MISSION).UpdateSites(session.solarsystemid)

    def OnSignalTrackerFullState(self, solarSystemID, fullState):
        self.LogInfo('OnSignalTrackerFullState', solarSystemID, fullState)
        anomalies, signatures, staticSites = fullState
        for siteType, rawSites in ((ANOMALY, anomalies), (SIGNATURE, signatures), (STATIC_SITE, staticSites)):
            self.siteController.GetSiteHandler(siteType).ProcessSiteUpdate(rawSites, set())

        self.probeScannerController.InjectSiteScanResults(self.siteController.siteMaps.IterSitesByKeys(ANOMALY, SIGNATURE))

    def OnSignalTrackerAnomalyUpdate(self, solarSystemID, addedAnomalies, removedAnomalies):
        self.LogInfo('OnSignalTrackerAnomalyUpdate', solarSystemID, addedAnomalies, removedAnomalies)
        self.siteController.GetSiteHandler(ANOMALY).ProcessSiteUpdate(addedAnomalies, removedAnomalies)

    def OnSignalTrackerSignatureUpdate(self, solarSystemID, addedSignatures, removedSignatures):
        self.LogInfo('OnSignalTrackerSignatureUpdate', solarSystemID, addedSignatures, removedSignatures)
        self.siteController.GetSiteHandler(SIGNATURE).ProcessSiteUpdate(addedSignatures, removedSignatures)

    def OnUpdateWindowPosition(self, leftPush, rightPush):
        uicore.layer.sensorsuite.padLeft = -leftPush
        uicore.layer.sensorsuite.padRight = -rightPush

    def IsMouseInSpaceView(self):
        if self.viewState.IsViewActive('inflight'):
            mouseOver = uicore.uilib.mouseOver
            for uiContainer in (uicore.layer.inflight, uicore.layer.sensorsuite, uicore.layer.bracket):
                if mouseOver is uiContainer or IsUnder(mouseOver, uiContainer):
                    return True

        return False

    @telemetry.ZONE_METHOD
    def UpdateMouseHoverSound(self, activeBracket, bestProximity, closestBracket, lastSoundStrength):
        soundStrength = bestProximity or 0
        if closestBracket is not None:
            if soundStrength != 0 or lastSoundStrength != 0:
                if lastSoundStrength == 0 or activeBracket != closestBracket:
                    signalStrength = MAX_RTPC_VALUE
                    difficulty = common.SITE_DIFFICULTY_EASY
                    self.audio.SendUIEvent(closestBracket.data.hoverSoundEvent)
                    self.audio.SetGlobalRTPC('scanner_signal_strength', min(signalStrength, MAX_RTPC_VALUE))
                    self.audio.SendUIEvent(AUDIO_STATE_BY_DIFFICULTY[difficulty])
                    self.audio.SendUIEvent('ui_scanner_mouseover')
                    activeBracket = closestBracket
                self.audio.SetGlobalRTPC('scanner_mouseover', soundStrength)
        elif soundStrength == 0 and lastSoundStrength > 0:
            self.DisableMouseOverSound()
            activeBracket = None
        lastSoundStrength = soundStrength
        return (activeBracket, lastSoundStrength)

    @telemetry.ZONE_METHOD
    def UpdateMouseTracking(self):
        self.LogInfo('Mouse tracking update thread started')
        lastSoundStrength = 0.0
        activeBracket = None
        self.sitesUnderCursor = set()
        self.audio.SetGlobalRTPC('scanner_mouseover', 0)
        while self.doMouseTrackingUpdates:
            try:
                if not self.IsMouseInSpaceView():
                    if activeBracket is not None:
                        self.DisableMouseOverSound()
                        activeBracket = None
                        lastSoundStrength = 0.0
                    continue
                desktopWidth = uicore.desktop.width
                desktopHeight = uicore.desktop.height
                mouseX = uicore.uilib.x
                mouseY = uicore.uilib.y
                self.currentOverlapCoordinates = (mouseX, mouseY)
                closestBracket = None
                bestProximity = None
                for data in self.siteController.spaceLocations.IterLocations():
                    self.sitesUnderCursor.discard(data.siteData)
                    bracket = data.bracket
                    if bracket is None or bracket.destroyed:
                        continue
                    if bracket.state == uiconst.UI_DISABLED:
                        continue
                    centerX = bracket.left + bracket.width / 2
                    centerY = bracket.top + bracket.height / 2
                    if centerX < 0:
                        continue
                    if centerX > desktopWidth:
                        continue
                    if centerY < 0:
                        continue
                    if centerY > desktopHeight:
                        continue
                    if mouseX < centerX - MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseX > centerX + MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseY < centerY - MAX_MOUSEOVER_RANGE:
                        continue
                    if mouseY > centerY + MAX_MOUSEOVER_RANGE:
                        continue
                    dx = centerX - mouseX
                    dy = centerY - mouseY
                    if -BRACKET_OVERLAP_DISTANCE <= dx <= BRACKET_OVERLAP_DISTANCE and -BRACKET_OVERLAP_DISTANCE <= dy <= BRACKET_OVERLAP_DISTANCE:
                        self.sitesUnderCursor.add(data.siteData)
                    if data.siteData.hoverSoundEvent is None:
                        continue
                    distanceSquared = dx * dx + dy * dy
                    if distanceSquared >= MAX_MOUSEOVER_RANGE_SQUARED:
                        continue
                    proximity = MAX_RTPC_VALUE - distanceSquared / MAX_MOUSEOVER_RANGE_SQUARED * MAX_RTPC_VALUE
                    if closestBracket is not None:
                        if proximity < bestProximity:
                            closestBracket = bracket
                            bestProximity = proximity
                    else:
                        closestBracket = bracket
                        bestProximity = proximity

                activeBracket, lastSoundStrength = self.UpdateMouseHoverSound(activeBracket, bestProximity, closestBracket, lastSoundStrength)
            except (ValueError, OverflowError):
                pass
            except Exception:
                LogException('The sound update loop errored out')
            finally:
                uthread2.Sleep(0.025)

        if activeBracket is not None:
            self.DisableMouseOverSound()
        self.LogInfo('Mouse tracking update thread ended')

    def DisableMouseOverSound(self):
        self.audio.SendUIEvent('ui_scanner_mouseover_stop')
        self.audio.SetGlobalRTPC('scanner_mouseover', 0)

    def OnWarpStarted(self):
        self.LogInfo('OnWarpStarted hiding the sweep gfx')
        self.gfxHandler.DisableGfx(SUPPRESS_GFX_WARPING)

    def OnWarpFinished(self):
        self.LogInfo('OnWarpFinished showing the sweep gfx')
        self.gfxHandler.EnableGfx(SUPPRESS_GFX_WARPING)

    def OnShowUI(self):
        self.LogInfo('OnShowUI showing the sweep gfx')
        uicore.layer.sensorsuite.display = True
        self.gfxHandler.EnableGfx(SUPPRESS_GFX_NO_UI)

    def OnHideUI(self):
        self.LogInfo('OnHideUI hiding the sweep gfx')
        uicore.layer.sensorsuite.display = False
        self.gfxHandler.DisableGfx(SUPPRESS_GFX_NO_UI)

    def OnSystemScanDone(self):
        self.probeScannerController.UpdateProbeResultBrackets()

    def GetOverlappingSites(self):
        overlappingBrackets = []
        for siteData in self.sitesUnderCursor:
            bracket = self.siteController.spaceLocations.GetBracketBySiteID(siteData.siteID)
            if bracket:
                overlappingBrackets.append(bracket)

        return overlappingBrackets

    def GetCosmicAnomalyItemIDFromTargetID(self, targetID):
        return self.probeScannerController.GetCosmicAnomalyItemIDFromTargetID(targetID)

    def SetSiteFilter(self, siteType, enabled):
        handler = self.siteController.GetSiteHandler(siteType)
        handler.SetFilterEnabled(enabled)
        self.UpdateVisibleSites()

    def UpdateVisibleSites(self):
        setattr(self, 'updateVisibleSitesTimerThread', AutoTimer(200, self._UpdateVisibleSites))

    @telemetry.ZONE_METHOD
    def _UpdateVisibleSites(self):
        self.LogInfo('UpdateVisibleSites')
        try:
            if session.solarsystemid is None:
                return
            if not self.IsSolarSystemReady():
                return
            self.siteController.UpdateSiteVisibility()
        finally:
            self.updateVisibleSitesTimerThread = None
