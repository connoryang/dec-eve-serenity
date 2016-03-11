#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveSpaceObject\spaceobjaudio.py
import logging
import audio2
import trinity
from inventorycommon import const
import eveaudio
import shipmode.data as stancedata
L = logging.getLogger(__name__)
__all__ = ['BOOSTER_AUDIO_LOCATOR_NAME',
 'SetupAudioEntity',
 'SendEvent',
 'PlayAmbientAudio',
 'GetBoosterEmitterAndEvent']
BOOSTER_AUDIO_LOCATOR_NAME = 'locator_audio_booster'

def SetupAudioEntity(model):
    triObserver = trinity.TriObserverLocal()
    result = audio2.AudEmitter('spaceObject_%s_general' % id(model))
    triObserver.observer = result
    model.observers.append(triObserver)
    return result


def SendEvent(audEntity, eventName):
    if eventName.startswith('wise:/'):
        eventName = eventName[6:]
    L.debug('playing audio event %s on emitter %s', eventName, id(audEntity))
    audEntity.SendEvent(unicode(eventName))


def PlayAmbientAudio(audEntity, soundUrl = None):
    if soundUrl is not None:
        SendEvent(audEntity, soundUrl)


def GetSoundUrl(slimItem = None, defaultSoundUrl = None):
    soundUrl = None
    if slimItem:
        soundUrl = eveaudio.GetSoundUrlForType(slimItem)
    if soundUrl is None:
        soundUrl = defaultSoundUrl
    return soundUrl


def GetBoosterSizeStr(groupID):
    boosterMappings = {const.groupCapDrainDrone: 'd',
     const.groupCombatDrone: 'd',
     const.groupElectronicWarfareDrone: 'd',
     const.groupFighterBomber: 'd',
     const.groupFighterDrone: 'd',
     const.groupLogisticDrone: 'd',
     const.groupMiningDrone: 'd',
     const.groupProximityDrone: 'd',
     const.groupRepairDrone: 'd',
     const.groupSalvageDrone: 'd',
     const.groupStasisWebifyingDrone: 'd',
     const.groupUnanchoringDrone: 'd',
     const.groupWarpScramblingDrone: 'd',
     const.groupCapsule: 'd',
     const.groupRookieship: 'f',
     const.groupFrigate: 'f',
     const.groupShuttle: 'f',
     const.groupAssaultShip: 'f',
     const.groupCovertOps: 'f',
     const.groupInterceptor: 'f',
     const.groupStealthBomber: 'f',
     const.groupElectronicAttackShips: 'f',
     const.groupPrototypeExplorationShip: 'f',
     const.groupExpeditionFrigate: 'f',
     const.groupLogisticsFrigate: 'f',
     const.groupDestroyer: 'c',
     const.groupCruiser: 'c',
     const.groupStrategicCruiser: 'c',
     const.groupAttackBattlecruiser: 'c',
     const.groupBattlecruiser: 'c',
     const.groupInterdictor: 'c',
     const.groupHeavyAssaultShip: 'c',
     const.groupLogistics: 'c',
     const.groupForceReconShip: 'c',
     const.groupCombatReconShip: 'c',
     const.groupCommandShip: 'c',
     const.groupHeavyInterdictors: 'c',
     const.groupMiningBarge: 'c',
     const.groupExhumer: 'c',
     const.groupTacticalDestroyer: 'c',
     const.groupCommandDestroyer: 'c',
     const.groupIndustrial: 'bs',
     const.groupIndustrialCommandShip: 'bs',
     const.groupTransportShip: 'bs',
     const.groupBlockadeRunner: 'bs',
     const.groupBattleship: 'bs',
     const.groupEliteBattleship: 'bs',
     const.groupMarauders: 'bs',
     const.groupBlackOps: 'bs',
     const.groupFreighter: 'dr',
     const.groupJumpFreighter: 'dr',
     const.groupDreadnought: 'dr',
     const.groupCarrier: 'dr',
     const.groupSupercarrier: 'dr',
     const.groupCapitalIndustrialShip: 'dr',
     const.groupTitan: 't'}
    return boosterMappings.get(groupID, 'f')


def GetBoosterAudioEventName(sizeStr, boosterSoundName):
    audioService = sm.GetService('audio')
    if audioService.GetDopplerEmittersUsage() and sizeStr in ('f', 'c', 'bs'):
        parts = [boosterSoundName, sizeStr, 'doppler_play']
    else:
        parts = [boosterSoundName, sizeStr, 'play']
    return '_'.join(parts)


def CreateEmitterForBooster(model, boosterSize, isAudioBoosterLocator = lambda n: n.name == BOOSTER_AUDIO_LOCATOR_NAME):
    locs = filter(isAudioBoosterLocator, model.locators)
    if not locs:
        return None
    if len(locs) > 1:
        L.error('Found %s locs, needed 1. Content should be validated against this!', len(locs))
    audLocator = locs[0]
    observer = trinity.TriObserverLocal()
    transform = audLocator.transform
    observer.front = (-transform[2][0], -transform[2][1], -transform[2][2])
    observer.position = (transform[3][0], transform[3][1], transform[3][2])
    audioService = sm.GetService('audio')
    if audioService.GetDopplerEmittersUsage() and boosterSize in ('f', 'c', 'bs'):
        rtpcChangeDuration = 17
        emitterName = 'ship_%s_booster' % id(model)
        rtpcName = 'doppler_shift_booster_' + boosterSize
        emitter = audio2.AudEmitterDoppler(emitterName, rtpcName, rtpcChangeDuration)
    else:
        emitter = audio2.AudEmitter('ship_%s_booster' % id(model))
    audparam = audio2.AudParameter()
    audparam.name = u'ship_speed'
    emitter.parameters.append(audparam)
    observer.observer = emitter
    model.observers.append(observer)
    model.audioSpeedParameter = audparam
    return emitter


def GetBoosterEmitterAndEvent(model, groupID, boosterSoundName):
    boosterSize = GetBoosterSizeStr(groupID)
    emitter = CreateEmitterForBooster(model, boosterSize)
    if emitter is None:
        return (None, None)
    boosterAudioEvent = GetBoosterAudioEventName(boosterSize, boosterSoundName)
    return (emitter, boosterAudioEvent)


def GetSharedAudioEmitter(eventName):
    audMan = audio2.GetManager()
    if eventName.startswith('wise:/'):
        eventName = eventName[6:]
    emitter = audMan.GetEmitterForEventName(eventName)
    return emitter


def SetupSharedEmitterForAudioEvent(model, eventName):
    triObserver = trinity.TriObserverLocal()
    emitter = GetSharedAudioEmitter(eventName)
    triObserver.observer = emitter
    model.observers.append(triObserver)
