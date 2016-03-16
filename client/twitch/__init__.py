#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\twitch\__init__.py
import trinity
import urllib
import _twitch as api
__all__ = ['api',
 'login',
 'login_with_token',
 'start_stream',
 'stop_stream',
 'set_mic_volume',
 'set_playback_volume',
 'get_api_state',
 'is_recording',
 'is_valid_windowsize',
 'get_login_token']

def login(username, password, clientID, clientSecret):
    try:
        api.Login(username.encode('utf8'), password.encode('utf8'), str(clientID), str(clientSecret))
    except:
        password = '********'
        raise


def login_with_token(clientID, token):
    api.LoginWithToken(str(clientID), str(token))


def start_stream(streamTitle, gameName, targetFps = 30, includeAudio = True):
    api.SetGameName(gameName)
    api.StartStream(streamTitle.encode('utf8'), targetFps, includeAudio, trinity.device)


def stop_stream():
    api.StopStream()


def set_mic_volume(value):
    api.SetVolume(api.AUDIO_DEVICE.RECORDER, value)


def set_playback_volume(value):
    api.SetVolume(api.AUDIO_DEVICE.PLAYBACK, value)


def get_api_state():
    state = api.GetState()
    name = api.STATE.GetNameFromValue(state)
    return (state, name)


def is_recording():
    return api.GetRecordingState()[0]


def is_streaming():
    return api.GetState() >= api.STATE.STREAMING


def is_valid_windowsize(size = None):
    if size is None:
        params = trinity.device.GetPresentParameters()
        size = (params['BackBufferWidth'], params['BackBufferHeight'])
    width, height = size
    if width % 32 or height % 16:
        return False
    if width > 1920:
        return False
    if height > 1200:
        return False
    return True


def set_state_change_callback(callback):
    api.SetStateChangeCallback(callback)


def get_login_token():
    return api.GetLoginToken()
