#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\environment\audioService.py
import service
import blue
import audio2
import trinity
import weakref
import funcDeco
import log
import sys
import eveaudio
from eveaudio.shiphealthnotification import ShipHealthNotifier
import eveaudio.audiomanager as audiomanager
from eveaudio.gameworldaudio import GameworldAudioMixin
from eveaudio.audiomanager import AudioManager
import evecamera
from eveSpaceObject.spaceobjaudio import GetBoosterSizeStr
import carbonui.const as uiconst
import evetypes
customSoundLevelsSettings = {'custom_master': 'custom_master',
 'custom_turrets': 'custom_turrets',
 'custom_jumpgates': 'custom_jumpgates',
 'custom_wormholes': 'custom_wormholes',
 'custom_jumpactivation': 'custom_jumpactivation',
 'custom_crimewatch': 'custom_crimewatch',
 'custom_explosions': 'custom_explosions',
 'custom_boosters': 'custom_boosters',
 'custom_stationext': 'custom_stationext',
 'custom_stationint': 'custom_stationint',
 'custom_modules': 'custom_modules',
 'custom_warping': 'custom_warping',
 'custom_mapisis': 'custom_mapisis',
 'custom_locking': 'custom_locking',
 'custom_shipsounds': 'custom_shipsounds',
 'custom_shipdamage': 'custom_shipdamage',
 'custom_store': 'custom_store',
 'custom_planets': 'custom_planets',
 'custom_uiclick': 'custom_uiclick',
 'custom_radialmenu': 'custom_radialmenu',
 'custom_impact': 'custom_impact',
 'custom_uiinteraction': 'custom_uiinteraction',
 'custom_aura': 'custom_aura',
 'custom_hacking': 'custom_hacking',
 'custom_shieldlow': 'custom_shieldlow',
 'custom_armorlow': 'custom_armorlow',
 'custom_hulllow': 'custom_hulllow',
 'custom_atmosphere': 'custom_atmosphere',
 'custom_dungeonmusic': 'custom_dungeonmusic',
 'custom_normalmusic': 'custom_normalmusic',
 'custom_warpeffect': 'custom_warpeffect'}
dampeningSettings = {'inactiveSounds_master': 'custom_damp_master',
 'inactiveSounds_music': 'custom_damp_music',
 'inactiveSounds_turrets': 'custom_damp_turrets',
 'inactiveSounds_shield': 'custom_damp_shield',
 'inactiveSounds_armor': 'custom_damp_armor',
 'inactiveSounds_hull': 'custom_damp_hull',
 'inactiveSounds_shipsound': 'custom_damp_shipsound',
 'inactiveSounds_jumpgates': 'custom_damp_jumpgates',
 'inactiveSounds_wormholes': 'custom_damp_wormholes',
 'inactiveSounds_jumping': 'custom_damp_jumping',
 'inactiveSounds_aura': 'custom_damp_aura',
 'inactiveSounds_modules': 'custom_damp_modules',
 'inactiveSounds_explosions': 'custom_damp_explosions',
 'inactiveSounds_warping': 'custom_damp_warping',
 'inactiveSounds_locking': 'custom_damp_locking',
 'inactiveSounds_planets': 'custom_damp_planets',
 'inactiveSounds_impacts': 'custom_damp_impacts',
 'inactiveSounds_deployables': 'custom_damp_deployables',
 'inactiveSounds_boosters': 'custom_damp_boosters',
 'inactiveSounds_pocos': 'custom_damp_pocos',
 'inactiveSounds_stationint': 'custom_damp_stationint',
 'inactiveSounds_stationext': 'custom_damp_stationext'}
industryLevels = {i:u'set_industry_level_%s_state' % (i,) for i in xrange(6)}
researchLevels = {i:u'set_research_level_%s_state' % (i,) for i in xrange(6)}

class AudioService(service.Service, GameworldAudioMixin):
    __guid__ = 'svc.audio'
    __exportedcalls__ = {'Activate': [],
     'Deactivate': [],
     'GetMasterVolume': [],
     'SetMasterVolume': [],
     'GetUIVolume': [],
     'SetUIVolume': [],
     'GetWorldVolume': [],
     'SetWorldVolume': [],
     'SetMusicVolume': [],
     'GetVoiceVolume': [],
     'SetVoiceVolume': [],
     'MuteSounds': [],
     'UnmuteSounds': [],
     'IsActivated': [],
     'AudioMessage': [],
     'SendUIEvent': [],
     'StartSoundLoop': [],
     'StopSoundLoop': [],
     'GetTurretSuppression': [],
     'SetTurretSuppression': []}
    __startupdependencies__ = ['settings', 'sceneManager']
    __notifyevents__ = ['OnChannelsJoined',
     'OnDamageStateChange',
     'OnCapacitorChange',
     'OnSessionChanged',
     'OnBallparkSetState',
     'OnDogmaItemChange',
     'OnActiveCameraChanged']
    __componentTypes__ = ['audioEmitter']

    def __init__(self):
        service.Service.__init__(self)
        GameworldAudioMixin.__init__(self)
        self.soundLoops = {}
        self.lastLookedAt = None
        self.shipHealthNotifier = ShipHealthNotifier(self.SendWiseEvent, self.SetGlobalRTPC)
        self.firstStartup = True
        self.lastSystemID = None
        self.lastCameraID = None

    def Run(self, ms = None):
        self.active = False
        self.manager = AudioManager(audiomanager.InitializeAudioManager(session.languageID), eveaudio.EVE_COMMON_BANKS)
        self.banksLoaded = False
        enabled = self.AppGetSetting('audioEnabled', 1)
        self.uiPlayer = self.jukeboxPlayer = None
        self.busChannels = {}
        for i in xrange(8):
            self.busChannels[i] = None

        trinity.SetDirectSoundPtr(audio2.GetDirectSoundPtr())
        if self.AppGetSetting('forceEnglishVoice', False):
            io = audio2.AudLowLevelIO(u'res:/Audio/')
            self.manager.manager.config.lowLevelIO = io
        if enabled:
            self.Activate()

    def Stop(self, stream):
        self.uiPlayer = None
        self.jukeboxPlayer = None
        if blue.win32 and trinity.device:
            try:
                blue.win32.WTSUnRegisterSessionNotification(trinity.device.GetWindow())
            except:
                sys.exc_clear()

        if uicore.uilib:
            uicore.uilib.SessionChangeHandler = None

    def SetGlobalRTPC(self, rtpcName, value):
        if not self.IsActivated():
            return
        audio2.SetGlobalRTPC(unicode(rtpcName), value)

    def Activate(self):
        self.manager.Enable()
        if self.uiPlayer is None:
            self.uiPlayer = audio2.GetUIPlayer()
        self.active = True
        self.SetMasterVolume(self.GetMasterVolume())
        self.SetUIVolume(self.GetUIVolume())
        self.SetWorldVolume(self.GetWorldVolume())
        self.SetVoiceVolume(self.GetVoiceVolume())
        self._SetAmpVolume(self.GetMusicVolume())
        self.SetTurretSuppression(self.GetTurretSuppression())
        self.SetVoiceCountLimitation(self.GetVoiceCountLimitation())
        self.SetOldJukeboxOverride(self.GetOldJukeboxOverride())
        if not self.firstStartup:
            sm.GetService('dynamicMusic').dynamicMusicSystem.EnableMusic()
            sm.GetService('dynamicMusic').UpdateDynamicMusic()
        self.firstStartup = False
        sm.ScatterEvent('OnAudioActivated')

    def Deactivate(self):
        self.manager.Disable()
        sm.GetService('dynamicMusic').dynamicMusicSystem.DisableMusic()
        self.active = False
        sm.ScatterEvent('OnAudioDeactivated')

    def GetAudioBus(self, is3D = False):
        for outputChannel, emitterWeakRef in self.busChannels.iteritems():
            if emitterWeakRef is None:
                emitter = audio2.AudEmitter('Bus Channel: ' + str(outputChannel))
                if is3D:
                    emitter.SendEvent(unicode('Play_3d_audio_stream_' + str(outputChannel)))
                else:
                    emitter.SendEvent(unicode('Play_2d_audio_stream_' + str(outputChannel)))
                self.busChannels[outputChannel] = weakref.ref(emitter, self.AudioBusDeathCallback)
                return (emitter, outputChannel)

        self.LogError('Bus voice starvation!')
        return (None, -1)

    @funcDeco.CallInNewThread(context='^AudioService::AudioBusDeathCallback')
    def AudioBusDeathCallback(self, audioEmitter):
        blue.synchro.SleepWallclock(2000)
        for outputChannel, emitterWeakRef in self.busChannels.iteritems():
            if emitterWeakRef == audioEmitter:
                self.busChannels[outputChannel] = None

    def SetMasterVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_master'), vol)
        if persist:
            self.AppSetSetting('masterVolume', vol)

    def GetMasterVolume(self):
        return self.AppGetSetting('masterVolume', 0.4)

    def SetUIVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_ui'), vol)
        if persist:
            self.AppSetSetting('uiGain', vol)

    def GetUIVolume(self):
        return self.AppGetSetting('uiGain', 0.4)

    def SetWorldVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        self.SetGlobalRTPC(unicode('volume_world'), vol)
        if persist:
            self.AppSetSetting('worldVolume', vol)

    def SetCustomValue(self, vol, settingName, persist = True):
        rtpcConfigName = customSoundLevelsSettings.get(settingName)
        if not rtpcConfigName:
            return
        self.SetSoundVolumeBetween0and1(volume=vol, configNameRTPC=rtpcConfigName, configNameAppSetting=settingName, persist=persist)

    def SetSoundVolumeBetween0and1(self, volume, configNameRTPC, configNameAppSetting, persist):
        if volume is None:
            volume = settings.user.audio.Get(configNameAppSetting, 0.5)
        if volume < 0.0 or volume > 1.0:
            raise RuntimeError('Erroneous value received for volume, configName=', configNameAppSetting)
        self.SetGlobalRTPC(unicode(configNameRTPC), volume)
        if persist:
            settings.user.audio.Set(configNameAppSetting, volume)

    def EnableAdvancedSettings(self):
        for eachSettingName in customSoundLevelsSettings.iterkeys():
            self.SetCustomValue(vol=None, settingName=eachSettingName, persist=False)

    def DisableAdvancedSettings(self):
        for eachSettingName in customSoundLevelsSettings.iterkeys():
            self.SetCustomValue(vol=0.5, settingName=eachSettingName, persist=False)

    def LoadUpSavedAdvancedSettings(self):
        for eachSettingName in customSoundLevelsSettings.iterkeys():
            volume = settings.user.audio.Get(eachSettingName, 0.5)
            self.SetCustomValue(vol=volume, settingName=eachSettingName, persist=False)

    def SetDampeningValue(self, settingName, setOn = True):
        audioEvent = dampeningSettings.get(settingName)
        if not audioEvent:
            return
        if setOn:
            audioEvent += '_on'
        else:
            audioEvent += '_off'
        self.SendUIEvent(audioEvent)

    def SetDampeningValueSetting(self, settingName, setOn = True):
        settings.user.audio.Set(settingName, setOn)

    def DisableDampeningValues(self):
        for eachSettingName in dampeningSettings.iterkeys():
            self.SetDampeningValue(settingName=eachSettingName, setOn=False)

    def LoadUpSavedDampeningValues(self):
        for eachSettingName in dampeningSettings.iterkeys():
            setOn = settings.user.audio.Get(eachSettingName, False)
            self.SetDampeningValue(settingName=eachSettingName, setOn=setOn)

    def GetWorldVolume(self):
        return self.AppGetSetting('worldVolume', 0.4)

    def SetMusicVolume(self, volume = 1.0, persist = True):
        volume = min(1.0, max(0.0, volume))
        self.SetGlobalRTPC(unicode('volume_music'), volume)
        if persist:
            self.AppSetSetting('eveampGain', volume)

    def SetVoiceVolume(self, vol = 1.0, persist = True):
        if vol < 0.0 or vol > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        if not self.IsActivated():
            return
        self.SetGlobalRTPC('volume_voice', vol)
        if persist:
            self.AppSetSetting('evevoiceGain', vol)

    def GetVoiceVolume(self):
        return self.AppGetSetting('evevoiceGain', 0.9)

    def _SetAmpVolume(self, volume = 0.25, persist = True):
        if volume < 0.0 or volume > 1.0:
            raise RuntimeError('Erroneous value received for volume')
        if not self.IsActivated():
            return
        self.SetGlobalRTPC('volume_music', volume)
        if persist:
            self.AppSetSetting('eveampGain', volume)

    def UserSetAmpVolume(self, volume = 0.25, persist = True):
        self._SetAmpVolume(volume, persist)
        sm.GetService('dynamicMusic').MusicVolumeChangedByUser(volume)

    def GetMusicVolume(self):
        return self.AppGetSetting('eveampGain', 0.25)

    def IsActivated(self):
        return self.active

    def SendEntityEventBySoundID(self, entity, soundID):
        if not entity:
            self.LogError('Trying to play an audio on an entity but got None sent in instead of entity instance')
            return
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping sound id', soundID)
            return
        audioEmitterComponent = entity.GetComponent('audioEmitter')
        soundEventName = cfg.sounds.GetIfExists(soundID)
        if audioEmitterComponent and soundEventName:
            if soundEventName.startswith('wise:/'):
                soundEventName = soundEventName[6:]
            audioEmitterComponent.emitter.SendEvent(unicode(soundEventName))
        elif not audioEmitterComponent:
            self.LogError('Trying to play audio', soundID, 'on entity', entity.entityID, 'that does not have an audioEmitter component')
        else:
            self.LogError('Could not find audio resource with ID', soundID)

    def SendEntityEvent(self, entity, event):
        if not entity:
            self.LogError('Trying to play an audio on an entity but got None sent in instead of entity instance')
            return
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping sound event', event)
            return
        if event.startswith('wise:/'):
            event = event[6:]
        audioEmitterComponent = entity.GetComponent('audioEmitter')
        if audioEmitterComponent:
            audioEmitterComponent.emitter.SendEvent(unicode(event))
        else:
            self.LogError('Trying to play audio on entity', entity.entityID, 'that does not have an audioEmitter component')

    def SendUIEvent(self, event):
        if not self.IsActivated():
            self.LogInfo('Audio inactive - skipping UI event', event)
            return
        if event.startswith('wise:/'):
            event = event[6:]
        self.LogInfo('Sending UI event to WWise:', event)
        self.uiPlayer.SendEvent(unicode(event))

    def SendUIEventByTypeID(self, typeID):
        soundID = evetypes.GetSoundID(typeID)
        if not soundID:
            log.LogException('No soundID assigned to typeID: %s' % typeID)
            return
        soundFile = cfg.sounds.Get(soundID).soundFile
        if not soundFile:
            log.LogException('No soundFile assigned to soundID: %s' % soundID)
            return
        self.SendUIEvent('ui_' + soundFile.replace('wise:/', ''))

    def AppGetSetting(self, setting, default):
        try:
            return settings.public.audio.Get(setting, default)
        except (AttributeError, NameError):
            return default

    def AppSetSetting(self, setting, value):
        try:
            settings.public.audio.Set(setting, value)
        except (AttributeError, NameError):
            pass

    def AudioMessage(self, msg):
        if not self.IsActivated():
            return
        if msg.audio:
            audiomsg = msg.audio
        else:
            return
        if audiomsg.startswith('wise:/'):
            audiomsg = audiomsg[6:]
            self.SendUIEvent(audiomsg)
        else:
            raise RuntimeError('OLD UI SOUND BEING PLAYED: %s' % msg)

    def StartSoundLoop(self, rootLoopMsg):
        if not self.IsActivated():
            return
        try:
            if rootLoopMsg not in self.soundLoops:
                self.LogInfo('StartSoundLoop starting loop with root %s' % rootLoopMsg)
                self.soundLoops[rootLoopMsg] = 1
                self.SendUIEvent('wise:/msg_%s_play' % rootLoopMsg)
            else:
                self.soundLoops[rootLoopMsg] += 1
                self.LogInfo('StartSoundLoop incrementing %s loop to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StartSoundLoop failed - halting loop with root', rootLoopMsg)
            self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()

    def StopSoundLoop(self, rootLoopMsg, eventMsg = None):
        if rootLoopMsg not in self.soundLoops:
            self.LogInfo('StopSoundLoop told to halt', rootLoopMsg, 'but that message is not playing!')
            return
        try:
            self.soundLoops[rootLoopMsg] -= 1
            if self.soundLoops[rootLoopMsg] <= 0:
                self.LogInfo('StopSoundLoop halting message with root', rootLoopMsg)
                del self.soundLoops[rootLoopMsg]
                self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            else:
                self.LogInfo('StopSoundLoop decremented count of loop with root %s to %d' % (rootLoopMsg, self.soundLoops[rootLoopMsg]))
        except:
            self.LogWarn('StopSoundLoop failed due to an exception - forcibly halting', rootLoopMsg)
            self.SendUIEvent('wise:/msg_%s_stop' % rootLoopMsg)
            sys.exc_clear()

        if eventMsg is not None:
            self.SendUIEvent(eventMsg)

    def GetTurretSuppression(self):
        return self.AppGetSetting('suppressTurret', 0)

    def SetTurretSuppression(self, suppress, persist = True):
        if not self.IsActivated():
            return
        if suppress:
            self.SetGlobalRTPC('turret_muffler', 0.0)
            suppress = 1
        else:
            self.SetGlobalRTPC('turret_muffler', 1.0)
            suppress = 0
        if persist:
            self.AppSetSetting('suppressTurret', suppress)

    def GetVoiceCountLimitation(self):
        return self.AppGetSetting('limitVoiceCount', 0)

    def SetVoiceCountLimitation(self, limit, persist = True):
        if not self.IsActivated():
            return
        if limit:
            self.SetGlobalRTPC('voice_count_limit', 1.0)
            limit = 1
        else:
            self.SetGlobalRTPC('voice_count_limit', 0.0)
            limit = 0
        if persist:
            self.AppSetSetting('limitVoiceCount', limit)

    def GetDopplerEmittersUsage(self):
        return self.AppGetSetting('useDopplerEmitters', 0)

    def SetDopplerEmittersUsage(self, useDopplerEmitters):
        self.AppSetSetting('useDopplerEmitters', useDopplerEmitters)
        self.manager.manager.useDoppler = useDopplerEmitters

    def GetMissileBoostersUsage(self):
        return self.AppGetSetting('useMissileBoosters', 0)

    def SetMissileBoostersUsage(self, useMissileBoosters):
        self.AppSetSetting('useMissileBoosters', useMissileBoosters)

    def GetOldJukeboxOverride(self):
        return self.AppGetSetting('useOldJukeboxOverride', 0)

    def SetOldJukeboxOverride(self, overrideWithOldJukebox):
        self.AppSetSetting('useOldJukeboxOverride', overrideWithOldJukebox)
        if sm.IsServiceRunning('dynamicMusic'):
            sm.GetService('dynamicMusic').UpdateDynamicMusic()

    def MuteSounds(self):
        self.SetMasterVolume(0.0, False)

    def UnmuteSounds(self):
        self.SetMasterVolume(self.GetMasterVolume(), False)

    def SendWiseEvent(self, event):
        if event:
            self.SendUIEvent(event)

    def OnChannelsJoined(self, channelIDs):
        if not session.stationid2:
            return
        if (('solarsystemid2', session.solarsystemid2),) in channelIDs:
            pilotsInChannel = eveaudio.GetPilotsInSystem()
            self.SetHangarPopulationSwitch(pilotsInChannel)

    def SetHangarPopulationSwitch(self, pilotsInChannel):
        self.SendUIEvent(eveaudio.GetHangarPopulationSwitch(pilotsInChannel))

    def SwapBanks(self, banks):
        self.manager.SwapBanks(banks)

    def OnDamageStateChange(self, *args, **kwargs):
        return self.shipHealthNotifier.OnDamageStateChange(*args, **kwargs)

    def OnCapacitorChange(self, *args, **kwargs):
        return self.shipHealthNotifier.OnCapacitorChange(*args, **kwargs)

    def OnSessionChanged(self, isRemote, session, change):
        if session.stationid2:
            self.SwapBanks(eveaudio.EVE_INCARNA_BANKS)
            eveaudio.SetTheraSystemHangarSwitch(session.solarsystemid2, self.uiPlayer)
        elif session.solarsystemid2:
            self.SwapBanks(eveaudio.EVE_SPACE_BANKS)
        if 'userid' in change and session.userid:
            uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, self.CheckAppFocus)
            if settings.user.audio.Get('soundLevel_advancedSettings', False):
                self.LoadUpSavedAdvancedSettings()
            if settings.user.audio.Get('inactiveSounds_advancedSettings', False) and not uicore.registry.GetFocus():
                self.LoadUpSavedDampeningValues()
        self.lastSystemID = eveaudio.PlaySystemSpecificEntrySound(self.lastSystemID, session.solarsystemid2, self.uiPlayer)

    def CheckAppFocus(self, wnd, msgID, vkey):
        if not settings.user.audio.Get('inactiveSounds_advancedSettings', False):
            return 1
        focused = vkey[0]
        if focused in (1, 2):
            self.DisableDampeningValues()
        else:
            self.LoadUpSavedDampeningValues()
        return 1

    def OnBallparkSetState(self):
        self.SetResearchAndIndustryLevel()

    def SetResearchAndIndustryLevel(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        industryLevel = ballpark.industryLevel
        researchLevel = ballpark.researchLevel
        if industryLevel in industryLevels.keys():
            self.SendUIEvent(industryLevels.get(industryLevel))
        if researchLevel in researchLevels.keys():
            self.SendUIEvent(researchLevels.get(researchLevel))

    def OnDogmaItemChange(self, *args, **kwargs):
        if session.solarsystemid:
            shipid = session.shipid
            ship = sm.StartService('godma').GetItem(shipid)
            if shipid and ship:
                cargoHoldState = ship.GetCapacity()
                return self.shipHealthNotifier.OnCargoHoldChange(shipid, cargoHoldState, *args, **kwargs)

    def OnActiveCameraChanged(self, cameraID):
        if session is None or self.lastCameraID == cameraID:
            return
        self.SendUIEvent('ship_camera_sounds_stop')
        if cameraID == evecamera.CAM_TACTICAL:
            self.SendUIEvent('ship_overview_zoom_play')
            self.SendUIEvent('state_camera_set_overview')
        elif cameraID == evecamera.CAM_SHIPPOV:
            if hasattr(session, 'shipid') and session.shipid is not None:
                ship = sm.GetService('michelle').GetItem(session.shipid)
                sizeStr = GetBoosterSizeStr(ship.grouID)
                eventStr = 'ship_interior_%s_play' % sizeStr
                self.SendUIEvent(eventStr)
                self.SendUIEvent('state_camera_set_cockpit')
        else:
            self.SendUIEvent('state_camera_set_normal')
