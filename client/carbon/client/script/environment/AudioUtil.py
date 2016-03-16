#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\environment\AudioUtil.py


def CheckAudioFileForEnglish(audioPath):
    if settings.user.ui.Get('forceEnglishVoice', False):
        audioPath = audioPath[:-3] + 'EN.' + audioPath[-3:]
    return audioPath


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('audioUtil', locals())
