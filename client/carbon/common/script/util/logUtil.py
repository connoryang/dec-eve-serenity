#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\logUtil.py
import logging
import logmodule
import sys
from stdlogutils import LineWrap
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

def supersafestr(o):
    try:
        return strx(o)
    except Exception as ex:
        default = '<UNFORMATABLE>'
        logger.exception('Error formatting an argument to strx2. Obviously it cannot be printed but you should be able to figure it out from the stacktrace. Returning %s', default)
        return default


class LogMixin():

    def __init__(self, logChannel = None, bindObject = None):
        logChannelName = self.GetLogChannelName(logChannel, bindObject)
        self.__logname__ = self.GetLogName(logChannelName)
        self.logChannel = logmodule.GetChannel(logChannelName)
        self.LoadPrefs()
        self.logContexts = {}
        for each in ('Info', 'Notice', 'Warn', 'Error'):
            self.logContexts[each] = 'Logging::' + each

    def GetLogChannelName(self, logChannelName = None, bindObject = None):
        if type(logChannelName) not in [str, type(None)]:
            raise Exception('logChannelName must be a string!')
        if logChannelName and bindObject:
            raise Exception('Conflicting log channel, provide logChannelName or bindObject, not both')
        bindguid = getattr(bindObject, '__guid__', None)
        bindLogName = getattr(bindObject, '__logname__', None)
        selfguid = getattr(self, '__guid__', None)
        return logChannelName or bindguid or bindLogName or selfguid or 'nonsvc.General'

    def GetLogName(self, logChannelName):
        tokens = logChannelName.split('.')
        if len(tokens) == 1:
            return tokens[0]
        else:
            return tokens[1]

    def ArrangeArguments(self, *args, **keywords):
        self.DeprecateKeywords(**keywords)
        argsList = []
        prefix = self.GetLogPrefix()
        if prefix:
            argsList.append(prefix)
        for item in args:
            argsList.append(item)

        return argsList

    def DeprecateKeywords(self, **keywords):
        if len(keywords):
            self.LogError('ERROR: keyword arguements passed into a log function')
            logmodule.LogTraceback()

    def GetLogPrefix(self):
        return None

    def DudLogger(self, *args, **keywords):
        pass

    def ShouldLogMethodCalls(self):
        if not getattr(self, 'isLogInfo', 0):
            return False
        if not prefs.GetValue('logMethodCalls', boot.role != 'client'):
            return False
        return self.logChannel.IsLogChannelOpen(logmodule.LGINFO)

    def LogMethodCall(self, *args, **keywords):
        argsList = self.ArrangeArguments(*args, **keywords)
        logChannel = logmodule.methodcalls
        try:
            if len(argsList) == 1:
                s = supersafestr(argsList[0])
            else:
                s = ' '.join(map(supersafestr, argsList))
            logChannel.Log(s, logmodule.LGINFO, 1, force=True)
        except TypeError:
            logChannel.Log('[X]'.join(map(supersafestr, argsList)).replace('\x00', '\\0'), logmodule.LGINFO, 1, force=True)
            sys.exc_clear()
        except UnicodeEncodeError:
            logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, argsList))), logmodule.LGINFO, 1, force=True)
            sys.exc_clear()

    def LogInfo(self, *args, **keywords):
        argsList = self.ArrangeArguments(*args, **keywords)
        if getattr(self, 'isLogInfo', 0) and self.logChannel.IsLogChannelOpen(logmodule.LGINFO):
            try:
                if len(argsList) == 1:
                    s = supersafestr(argsList[0])
                else:
                    s = ' '.join(map(supersafestr, argsList))
                self.logChannel.Log(s, logmodule.LGINFO, 1, force=True)
            except TypeError:
                self.logChannel.Log('[X]'.join(map(supersafestr, argsList)).replace('\x00', '\\0'), logmodule.LGINFO, 1, force=True)
                sys.exc_clear()
            except UnicodeEncodeError:
                self.logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, argsList))), logmodule.LGINFO, 1, force=True)
                sys.exc_clear()

    def LogWarn(self, *args, **keywords):
        argsList = self.ArrangeArguments(*args, **keywords)
        if self.isLogWarning and self.logChannel.IsLogChannelOpen(logmodule.LGWARN) or charsession and not boot.role == 'client':
            try:
                if len(argsList) == 1:
                    s = supersafestr(argsList[0])
                else:
                    s = ' '.join(map(supersafestr, argsList))
                if self.logChannel.IsOpen(logmodule.LGWARN):
                    self.logChannel.Log(s, logmodule.LGWARN, 1, force=True)
                for x in LineWrap(s, 10):
                    if charsession and not boot.role == 'client':
                        charsession.LogSessionHistory(x, None, 1)

            except TypeError:
                sys.exc_clear()
                x = '[X]'.join(map(supersafestr, argsList)).replace('\x00', '\\0')
                if self.logChannel.IsOpen(logmodule.LGWARN):
                    self.logChannel.Log(x, logmodule.LGWARN, 1, force=True)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)
            except UnicodeEncodeError:
                sys.exc_clear()
                x = '[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, argsList)))
                if self.logChannel.IsOpen(logmodule.LGWARN):
                    self.logChannel.Log(x, logmodule.LGWARN, 1, force=True)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)

    def LogError(self, *args, **keywords):
        argsList = self.ArrangeArguments(*args, **keywords)
        if self.logChannel.IsOpen(logmodule.LGERR) or charsession:
            try:
                if len(argsList) == 1:
                    s = supersafestr(argsList[0])
                else:
                    s = ' '.join(map(supersafestr, argsList))
                if self.logChannel.IsOpen(logmodule.LGERR):
                    self.logChannel.Log(s, logmodule.LGERR, 1)
                for x in LineWrap(s, 40):
                    if charsession:
                        charsession.LogSessionHistory(x, None, 1)

            except TypeError:
                sys.exc_clear()
                x = '[X]'.join(map(supersafestr, argsList)).replace('\x00', '\\0')
                if self.logChannel.IsOpen(logmodule.LGERR):
                    self.logChannel.Log(x, logmodule.LGERR, 1)
                if charsession:
                    charsession.LogSessionHistory(x, None, 1)
            except UnicodeEncodeError:
                sys.exc_clear()
                x = '[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, argsList)))
                if self.logChannel.IsOpen(logmodule.LGERR):
                    self.logChannel.Log(x, logmodule.LGERR, 1)
                if charsession and not boot.role == 'client':
                    charsession.LogSessionHistory(x, None, 1)

    def LogNotice(self, *args, **keywords):
        argsList = self.ArrangeArguments(*args, **keywords)
        if getattr(self, 'isLogInfo', 0) and self.logChannel.IsLogChannelOpen(logmodule.LGNOTICE):
            try:
                if len(argsList) == 1:
                    s = supersafestr(argsList[0])
                else:
                    s = ' '.join(map(supersafestr, argsList))
                self.logChannel.Log(s, logmodule.LGNOTICE, 1, force=True)
            except TypeError:
                self.logChannel.Log('[X]'.join(map(supersafestr, argsList)).replace('\x00', '\\0'), logmodule.LGNOTICE, 1, force=True)
                sys.exc_clear()
            except UnicodeEncodeError:
                self.logChannel.Log('[U]'.join(map(lambda x: x.encode('ascii', 'replace'), map(unicode, argsList))), logmodule.LGNOTICE, 1, force=True)
                sys.exc_clear()

    def LoadPrefs(self):
        self.isLogInfo = bool(prefs.GetValue('logInfo', 1))
        self.isLogWarning = bool(prefs.GetValue('logWarning', 1))
        self.isLogNotice = bool(prefs.GetValue('logNotice', 1))

    def SetLogInfo(self, b):
        if not b and self.isLogInfo:
            self.LogInfo('*** LogInfo stopped for ', self.__guid__)
        old = self.isLogInfo
        self.isLogInfo = b
        if b and not old:
            self.LogInfo('*** LogInfo started for ', self.__guid__)

    def SetLogNotice(self, b):
        if not b and self.isLogNotice:
            self.LogInfo('*** LogNotice stopped for ', self.__guid__)
        old = self.isLogNotice
        self.isLogNotice = b
        if b and not old:
            self.LogInfo('*** LogNotice started for ', self.__guid__)

    def SetLogWarning(self, b):
        if not b and self.isLogWarning:
            self.LogWarn('*** LogWarn stopped for ', self.__guid__)
        old = self.isLogWarning
        self.isLogWarning = b
        if b and not old:
            self.LogWarn('*** LogWarn started for ', self.__guid__)


def _Log(severity, what):
    try:
        s = ' '.join(map(str, what))
    except UnicodeEncodeError:

        def conv(what):
            if isinstance(what, unicode):
                return what.encode('ascii', 'replace')
            return str(what)

        s = ' '.join(map(conv, what))

    logmodule.general.Log(s.replace('\x00', '\\0'), severity)


def LogInfo(*what):
    _Log(logmodule.LGINFO, what)


def LogNotice(*what):
    _Log(logmodule.LGNOTICE, what)


def LogWarn(*what):
    _Log(logmodule.LGWARN, what)


def LogError(*what):
    _Log(logmodule.LGERR, what)


LogException = logmodule.LogException
import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('log', locals())
