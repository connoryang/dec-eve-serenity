#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\eveAudioService.py
import service
import eveaudio
from eveaudio.dynamicmusicsystem import DynamicMusicSystem

class DungeonCheckerService(service.Service):
    __guid__ = 'svc.dungeonChecker'
    __exportedcalls__ = {'AccelerationGateUpdate': [],
     'WarpFinishedUpdate': [],
     'IsInDungeon': []}
    __notifyevents__ = ['OnSessionChanged',
     'OnWarpFinished',
     'OnDistributionDungeonEntered',
     'OnEscalatingPathDungeonEntered',
     'OnIncomingTransmission']

    def __init__(self):
        service.Service.__init__(self)
        self.isInDungeon = False
        self.enteringDungeon = False

    def Run(self, *args):
        service.Service.Run(self, *args)
        sm.FavourMe(self.OnWarpFinished)

    def AccelerationGateUpdate(self):
        self.isInDungeon = True
        self.enteringDungeon = True

    def WarpFinishedUpdate(self):
        if self.enteringDungeon:
            self.isInDungeon = True
            self.enteringDungeon = False
        else:
            self.isInDungeon = False

    def IsInDungeon(self):
        return self.isInDungeon or self.enteringDungeon

    def OnSessionChanged(self, *args):
        self.isInDungeon = False
        self.enteringDungeon = False

    def OnWarpFinished(self, *args):
        self.WarpFinishedUpdate()

    def OnDistributionDungeonEntered(self, *args):
        self.enteringDungeon = True

    def OnEscalatingPathDungeonEntered(self, *args):
        self.enteringDungeon = True

    def OnIncomingTransmission(self, *args):
        self.enteringDungeon = True


class DynamicMusicService(service.Service):
    __guid__ = 'svc.dynamicMusic'
    __notifyevents__ = ['OnSessionChanged', 'OnChannelsJoined', 'OnWarpFinished']
    __dependencies__ = ['audio', 'dungeonChecker']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.dynamicMusicSystem = DynamicMusicSystem(self.audio.SendWiseEvent)

    def MusicVolumeChangedByUser(self, volume):
        if volume == 0.0 and self.dynamicMusicSystem.IsMusicEnabled():
            self.dynamicMusicSystem.DisableMusic()
        elif volume != 0.0 and not self.dynamicMusicSystem.IsMusicEnabled():
            self.dynamicMusicSystem.EnableMusic()
            self.UpdateDynamicMusic()

    def StopLocationMusic(self, location):
        self.dynamicMusicSystem.StopLocationMusic(location)

    def PlayLocationMusic(self, location):
        self.dynamicMusicSystem.PlayLocationMusic(location)

    def OnSessionChanged(self, *args):
        if session.solarsystemid2:
            self.UpdateDynamicMusic()

    def UpdateDynamicMusic(self):
        self.dynamicMusicSystem.oldJukeboxOverride = self.audio.GetOldJukeboxOverride()
        self.dynamicMusicSystem.UpdateDynamicMusic(uicore, session.solarsystemid2, self._GetSecurityStatus())

    def OnWarpFinished(self, *args):
        if not self.dungeonChecker.IsInDungeon():
            self.UpdateDynamicMusic()

    def OnChannelsJoined(self, channelIDs):
        if self.dungeonChecker.IsInDungeon():
            return
        if (('solarsystemid2', session.solarsystemid2),) in channelIDs:
            pilotsInChannel = eveaudio.GetPilotsInSystem()
            self._SetDynamicMusicSwitchPopularity(pilotsInChannel)
            self.UpdateDynamicMusic()

    def _SetDynamicMusicSwitchPopularity(self, pilotsInChannel = None):
        if not session.solarsystemid2:
            return
        if pilotsInChannel is None:
            pilotsInChannel = eveaudio.GetPilotsInSystem()
        self.dynamicMusicSystem.SetDynamicMusicSwitchPopularity(pilotsInChannel, self._GetSecurityStatus())

    def _GetSecurityStatus(self):
        securityStatus = 1.0
        if session.solarsystemid2:
            securityStatus = sm.GetService('map').GetSecurityClass(session.solarsystemid2)
        return securityStatus
