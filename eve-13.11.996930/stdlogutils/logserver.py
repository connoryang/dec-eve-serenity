#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\stdlogutils\logserver.py
import logging
import stdlogutils
from blue import LogChannel
LGINFO = 1
LGNOTICE = 32
LGWARN = 2
LGERR = 4
LOG_MAXMESSAGE = 252
INDENT_PREFIX = '  '
LEVEL_MAP = {logging.CRITICAL: LGERR,
 logging.ERROR: LGERR,
 logging.WARNING: LGWARN,
 logging.INFO: LGNOTICE,
 logging.DEBUG: LGINFO,
 logging.NOTSET: LGINFO}

def _LogChannelIsOpen(logChannel, flag):
    return LogChannel.IsOpen(logChannel, flag)


class ChannelWrapper(LogChannel):
    channelDict = {LGINFO: 1,
     LGNOTICE: 1,
     LGWARN: 1,
     LGERR: 1}

    @classmethod
    def Suppress(cls, logflag):
        cls.channelDict[logflag] = 0

    @classmethod
    def Unsuppress(cls, logflag):
        cls.channelDict[logflag] = 1

    @classmethod
    def SuppressAllChannels(cls):
        for k in cls.channelDict.keys():
            cls.Suppress(k)

    @classmethod
    def UnsuppressAllChannels(cls):
        for k in cls.channelDict.keys():
            cls.Unsuppress(k)

    @classmethod
    def Initialize(cls, prefs):

        def setif(prefskey, level):
            if prefs.HasKey(prefskey):
                cls.channelDict.update({level: prefs.GetValue(prefskey)})

        setif('logInfo', LGINFO)
        setif('logNotice', LGNOTICE)
        setif('logWarning', LGWARN)
        setif('logError', LGERR)

    def IsOpen(self, logflag):
        return ChannelWrapper.channelDict.get(logflag, 1) and self.IsLogChannelOpen(logflag)

    def IsLogChannelOpen(self, logflag):
        return _LogChannelIsOpen(self, logflag)

    def Log(self, value, flag = LGINFO, backstack = 0, force = False):
        if ChannelWrapper.channelDict.get(flag, 1) or force:
            LogChannel.Log(self, value, flag, backstack)

    def open(self, flag = LGINFO, bufsize = -1):
        return LogChannelStream(self, flag, bufsize)


class LogChannelStream(object):
    encoding = 'utf8'

    def __init__(self, channel, mode, bufsize = -1):
        self.channel, self.mode, self.bufsize = channel, mode, bufsize
        self.buff = []

    def __del__(self):
        self.close()

    def write(self, text):
        self.buff.append(text)
        if self.bufsize == 1 and '\n' in text:
            self.lineflush()
        elif self.bufsize == 0:
            self.flush()

    def writelines(self, lines):
        for each in lines:
            self.write(each)

    def close(self):
        if self.buff is not None:
            self.flush()
            self.buff = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def flush(self):
        out = ''.join(self.buff)
        self.buff = []
        if out:
            self.outputlines(out)

    def lineflush(self):
        out = ''.join(self.buff)
        lines = out.split('\n')
        self.buff = lines[-1:]
        self.outputlines(lines[:-1])

    def outputlines(self, lines):
        mode = self.mode
        self.channel.Log(lines, mode)


def GetLoggingLevelFromPrefs():
    logLevelPrefsNameToLoggingLevel = {'ERROR': logging.ERROR,
     'WARNING': logging.WARNING,
     'NOTICE': logging.INFO,
     'INFO': logging.DEBUG}
    prefsname = prefs.ini.GetValue('pythonLogLevel', 'INFO')
    level = logLevelPrefsNameToLoggingLevel.get(prefsname, logging.DEBUG)
    return level


class LogServerHandler(logging.Handler):

    def __init__(self):
        super(LogServerHandler, self).__init__()
        self.channels = {}

    def _makeChannel(self, record):
        if '.' in record.name:
            channel, object = record.name.split('.', 1)
        else:
            channel, object = record.name, 'General'
        return ChannelWrapper(channel, object)

    def emit(self, record):
        try:
            ch = self.channels.get(record.name)
            if ch is None:
                ch = self._makeChannel(record)
                self.channels[record.name] = ch
            severity = LEVEL_MAP.get(record.levelno, LEVEL_MAP[logging.INFO])
            msg = self.format(record)
            ch.Log(msg, severity)
        except Exception:
            self.handleError(record)


def InitLoggingToLogserver(logLevel):
    if hasattr(InitLoggingToLogserver, '_hasBeenInit'):
        raise RuntimeError('Already initialized.')
    logserver = LogServerHandler()
    logserver.setFormatter(stdlogutils.Fmt.FMT_EVE)
    logging.root.addHandler(logserver)
    logging.root.setLevel(logLevel)
    InitLoggingToLogserver._hasBeenInit = True
