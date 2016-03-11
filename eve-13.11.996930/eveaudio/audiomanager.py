#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveaudio\audiomanager.py
import audio2
import blue
import remotefilecache
import uthread2
from eveaudio import LANGUAGE_ID_TO_BANK
import logging
L = logging.getLogger(__name__)

class AudioManager(object):

    def __init__(self, audio2Manager, banksToKeepActive):
        self.manager = audio2Manager
        self.defaultBanks = banksToKeepActive
        uthread2.StartTasklet(self.LoadDefaultBanks)

    def LoadDefaultBanks(self):
        prefetch = set()
        for bank in self.defaultBanks:
            filename = 'res:/Audio/' + bank
            if blue.paths.exists(filename) and not blue.paths.FileExistsLocally(filename):
                prefetch.add(filename)

        remotefilecache.prefetch_files(prefetch)
        map(self.manager.LoadBank, self.defaultBanks)

    def LoadedBanks(self):
        return self.manager.GetLoadedSoundBanks()

    def Disable(self):
        self.manager.SetEnabled(False)

    def Enable(self):
        self.manager.SetEnabled(True)

    def SwapBanks(self, banks):
        loadedBanks = self.LoadedBanks()
        self._UnloadUnusedBanks(banks, loadedBanks)
        self._LoadNeededBanks(banks, loadedBanks)

    def _UnloadUnusedBanks(self, banks, loadedBanks):
        defaultsExcluded = set(loadedBanks).difference(self.defaultBanks)
        banksToUnload = defaultsExcluded.difference(banks)
        for each in banksToUnload:
            L.debug('Unloading %s' % each)
            self.manager.UnloadBank(each)
            uthread2.Yield()

    def _LoadNeededBanks(self, banks, loadedBanks):
        banksToLoad = set(banks).difference(loadedBanks)
        for each in banksToLoad:
            L.debug('Loading %s' % each)
            self.manager.LoadBank(each)
            uthread2.Yield()


def InitializeAudioManager(languageID):
    manager = audio2.GetManager()
    io = audio2.AudLowLevelIO(u'res:/Audio/', LANGUAGE_ID_TO_BANK.get(languageID, u''))
    initConf = audio2.AudConfig()
    initConf.lowLevelIO = io
    initConf.numRefillsInVoice = 8
    initConf.asyncFileOpen = True
    manager.config = initConf
    return manager
