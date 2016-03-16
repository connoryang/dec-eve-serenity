#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecamera\targetTrackingService.py
import evecamera
import service
import carbonui.const as uiconst
from eve.client.script.ui.inflight.bracketsAndTargets.trackingLocator import TrackingLocator
import state
import uthread
import trackingUtils

class TargetTrackingService(service.Service):
    __guid__ = 'svc.targetTrackingService'
    __servicename__ = 'targetTrackingService'
    __displayname__ = 'Target Tracking Service'
    __notifyevents__ = ['OnSetDevice', 'OnLookAt', 'OnStateChange']
    __dependencies__ = ['sceneManager']
    __startupdependencies__ = ['sceneManager']

    def Run(self, *args):
        self.trackingLocator = None
        self.isCentered = settings.char.ui.Get('track_is_centered', False)
        self.isActiveTracking = settings.char.ui.Get('track_selected_item', False)
        self.normalizedCustomScreenPoint = settings.char.ui.Get('tracking_cam_location_n', (0.3, 0.3))
        self.isPaused = False
        self.selectedItemForTracking = None
        self.MakeNormalizedBoundaries()
        self.SetCenteredTrackingState(self.isCentered)
        self.isInitialized = False
        self.waitSelectThread = None

    def GetTargetTracker(self):
        return sm.GetService('sceneManager').GetRegisteredCamera(evecamera.CAM_SPACE_PRIMARY).targetTracker

    def InitIfNeeded(self):
        if not self.isInitialized:
            self.SetActiveTrackingState(on=self.isActiveTracking)
            self.isInitialized = True

    def OnStateChange(self, itemID, flag, beingSelected, *args):
        if flag == state.selected:
            if beingSelected:
                self.InitIfNeeded()
                self.SetSelectedItem(itemID)
            if not beingSelected and self.selectedItemForTracking == itemID:
                self.selectedItemForTracking = None
                self.deselectThread = uthread.new(self.RunDeselectIfNonSelect)

    def RunDeselectIfNonSelect(self):
        if self.selectedItemForTracking is None:
            self.SetSelectedItem(None)
            self.deselectThread = None

    def MakeNormalizedBoundaries(self):
        self.normalizedBoundaries = (0.05, 0.05, 0.9, 0.9)

    def ConformTrackPointToNormalizedBoundaries(self):
        self.normalizedCustomScreenPoint = trackingUtils.ClampPoint(self.normalizedBoundaries, self.normalizedCustomScreenPoint)

    def ConformTrackPointToBoundaries(self):
        self.customOnScreenPoint = trackingUtils.ClampPoint(self.trackerBoundaries, self.customOnScreenPoint)

    def OnSetDevice(self):
        if self.isActiveTracking:
            self.SetCenteredTrackingState(self.isCentered)

    def IsTargetKeyBeingPressed(self):
        lockSC = uicore.cmd.GetShortcutByFuncName('CmdLockTargetItem')
        if lockSC and uicore.uilib.Key(lockSC[0]):
            return True
        else:
            return False

    def SetSelectedItem(self, itemID):
        self.SetSelectedItems([itemID])

    def SetSelectedItems(self, itemIds):
        if self.IsTargetKeyBeingPressed() or len(itemIds) <= 0:
            return
        self.selectedItemForTracking = itemIds[0]
        if self.isActiveTracking:
            self._TrackSelectedItem()
        elif self.isActiveTracking is None:
            self.SetActiveTrackingState(on=True, persist=False)
        self.NotifyTrackingState()

    def GetActiveTrackingState(self):
        return self.isActiveTracking

    def GetCenteredState(self):
        return self.isCentered

    def MouseTrackInterrupt(self):
        if not self.isPaused and self.isActiveTracking:
            self._PauseActiveTracking()

    def _PauseActiveTracking(self):
        self.isPaused = True
        self.SetActiveTrackingState(None, persist=False)

    def ToggleActiveTracking(self):
        self.SetActiveTrackingState(self.isActiveTracking is False, persist=True)

    def ToggleCenteredTracking(self):
        self.SetCenteredTrackingState(not self.isCentered)

    def SetCenteredTrackingState(self, center):
        self.isCentered = center
        self.DestroyLocatorIfExisting()
        if center:
            self.SetTrackingToCenter()
        else:
            self.SetTrackingToCustom()
        settings.char.ui.Set('track_is_centered', center)
        sm.ScatterEvent('OnCenterTrackingChange', self.isCentered)

    def SetTrackerToNormalizedPoint(self, p):
        self.GetTargetTracker().SetTrackingPointNormalized(p)

    def SetTrackingToCustom(self):
        self.SetTrackerToNormalizedPoint(self.normalizedCustomScreenPoint)

    def SetTrackingToCenter(self):
        self.GetTargetTracker().SetCenteredTrackingPoint()

    def _TrackSelectedItem(self):
        self.isPaused = False
        self.GetTargetTracker().TrackItem(self.selectedItemForTracking)

    def _StopTrackingItem(self):
        self.GetTargetTracker().TrackItem(None)

    def OnLookAt(self, itemID):
        if self.isActiveTracking:
            self.GetTargetTracker().TrackItem(None)
            self.GetTargetTracker().TrackItem(self.selectedItemForTracking)

    def NotifyTrackingState(self):
        isReallyTracking = self.isActiveTracking
        if isReallyTracking and self.selectedItemForTracking is None:
            isReallyTracking = None
        sm.ScatterEvent('OnActiveTrackingChange', isReallyTracking)

    def EnableTrackingCamera(self):
        self.SetActiveTrackingState(on=True, persist=True)

    def DisableTrackingCamera(self):
        self.SetActiveTrackingState(on=False, persist=True)

    def SetActiveTrackingState(self, on, persist = False):
        self.isActiveTracking = on
        if on:
            self._TrackSelectedItem()
            self.ShowOnScreenPositionPicker(interactive=not self.isCentered)
        else:
            self._StopTrackingItem()
        if on is not None and persist:
            previouslyOn = settings.char.ui.Get('track_selected_item', False)
            if on and previouslyOn is False:
                sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEvenTrackingCameraEnabled, itemID=session.charid, int_1=1, int_2=1 if self.isCentered else 0)
            settings.char.ui.Set('track_selected_item', on)
        self.NotifyTrackingState()

    def SetCustomTrackingPoint(self, x, y, persist = True):
        self.normalizedCustomScreenPoint = self.normalizePoint((x, y))
        self.ConformTrackPointToNormalizedBoundaries()
        if persist:
            settings.char.ui.Set('tracking_cam_location_n', self.normalizedCustomScreenPoint)
        if not self.isCentered and self.isActiveTracking:
            self.SetTrackerToNormalizedPoint(self.normalizedCustomScreenPoint)

    def ShowOnScreenPositionPicker(self, interactive = True):
        if sm.GetService('viewState').GetCurrentView().name != 'inflight':
            return
        self.CreateLocatorIfNotExisting(interactive)

    def GetCenterPosition(self):
        return trackingUtils.GetCameraOffsetDesktopCenter()

    def GetNormalizedCenterPosition(self):
        return trackingUtils.GetNormalizedCenter()

    def CreateLocatorIfNotExisting(self, interactive):
        if not self.trackingLocator or self.trackingLocator.destroyed:
            pos = None
            callback = None
            if interactive:
                callback = self.SetCustomTrackingPoint
                pos = self.normalizedCustomScreenPoint
            else:
                pos = self.GetNormalizedCenterPosition()
            self.trackingLocator = TrackingLocator(align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, parent=uicore.layer.abovemain, idx=0, desiredPosition=pos, interactive=interactive, positionCallback=callback, boundary=self.normalizedBoundaries)

    def DestroyLocatorIfExisting(self):
        if self.trackingLocator and not self.trackingLocator.destroyed:
            self.trackingLocator.Close()

    def GetInflightDisplayRect(self):
        return uicore.layer.inflight.displayRect

    def normalizePoint(self, absolutePoint):
        return trackingUtils.NormalizePointToInflight(absolutePoint)

    def normalizedPointToAbsolute(self, normalizedPoint):
        return trackingUtils.NormalizedPointToAbsoluteInflight(normalizedPoint)
