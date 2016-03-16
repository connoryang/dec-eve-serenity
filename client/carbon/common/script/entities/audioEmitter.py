#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\audioEmitter.py
INITIAL_EVENT_NAME = 'initialEventName'
INITIAL_SOUND_ID = 'initialSoundID'
EMITTER_GROUP_NAME = 'groupName'

class AudioEmitterComponent:
    __guid__ = 'audio.AudioEmitterComponent'

    def __init__(self):
        self.initialEventName = None
        self.initialSoundID = None
        self.groupName = None


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('audio', locals())
