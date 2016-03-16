#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\stdlogutils\__init__.py
import __builtin__
import cStringIO
import logging
import os
import sys
import traceback2
import zlib
from brennivin.logutils import *
from stringutil import strx
try:
    import devenv
except ImportError:
    devenv = None

def GetStack(traceback_list, caughtAt_list = None, show_locals = 0, show_lines = True):
    stackText = GetStackDescriptionText(traceback_list, caughtAt_list, show_locals, show_lines)
    stackID = GetStackID(traceback_list, caughtAt_list)
    cleanStackText = CleanupStack(stackText)
    return (cleanStackText, stackID)


def GetStackID(traceback_list, caughtAt_list = None):
    miniStack = GetStackDescriptionText(traceback_list, caughtAt_list, show_locals=0, show_lines=False)
    miniStack = ''.join(miniStack)[-4000:]
    stackHash = zlib.adler32(miniStack)
    return (stackHash, miniStack)


def GetStackDescriptionText(traceback_list, caughtAt_list = None, show_locals = 0, show_lines = True):
    if caughtAt_list is not None:
        stack = [' \nCaught at:\n']
        stack += FormatList(caughtAt_list, show_locals=0, show_lines=show_lines)
        stack.append(' \nThrown at:\n')
    else:
        stack = [' \nTraced at:\n']
    stack += FormatList(traceback_list, show_locals=show_locals, show_lines=show_lines)
    return stack


def FormatList(traceback_list, show_locals = 0, show_lines = True):
    cleaned_list = []
    for line in traceback_list:
        l2 = list(line)
        l2[0] = GetFriendlyPathName(l2[0])
        if not show_lines:
            l2[3] = ''
        cleaned_list.append(l2)

    lines = traceback2.format_list(cleaned_list, show_locals, format=traceback2.FORMAT_LOGSRV | traceback2.FORMAT_SINGLE)
    return lines


traceID = 0L
cachedFriendlyPathNames = {}

def GetFriendlyPathName(pathName):
    if pathName not in cachedFriendlyPathNames:
        friendlyName = os.path.normpath(pathName)
        friendlyName = friendlyName.replace('\\', '/')
        cachedFriendlyPathNames[pathName] = strx(friendlyName)
    return cachedFriendlyPathNames[pathName]


def CleanupStack(stack):
    pathLines = [ line.lower() for line in stack if isWorthPrefixing(line) ]
    prefix = os.path.commonprefix(pathLines)
    prefix = prefix.rstrip('/')
    out = ['Common path prefix = %s\n' % prefix]
    trimFrom = len(prefix)
    out += [ ('<pre>' + line[trimFrom:] if isWorthPrefixing(line) else line) for line in stack ]
    return out


def isWorthPrefixing(line):
    return isPathy(line) and '/cache/effectCode.py' not in line


def isPathy(line):
    return len(line) > 1 and line[1] == ':'


def NextTraceID():
    global traceID
    traceID += 1
    return traceID


class EveExceptionsFormatter(logging.Formatter):

    def _LogThreadLocals(self, file):
        file.write('Thread Locals:')
        if hasattr(__builtin__, 'session'):
            file.write('  session was ')
            file.write(str(session) + '\n')
        else:
            file.write('No session information available.\n')

    def _LogServerInfo(self, file):
        if hasattr(__builtin__, 'boot'):
            if boot.role != 'client':
                try:
                    import blue
                    ram = blue.sysinfo.GetMemory().pageFile / 1024 / 1024
                    cpuLoad = sm.GetService('machoNet').GetCPULoad()
                    memLeft = blue.sysinfo.GetMemory().availablePhysical / 1024 / 1024
                    txt = 'System Information: '
                    txt += ' Node ID: %s' % sm.GetService('machoNet').GetNodeID()
                    if boot.role == 'server':
                        txt += ' | Node Name: %s' % sm.GetService('machoNet').GetLocalHostName()
                    txt += ' | Total CPU load: %s%%%%' % int(cpuLoad)
                    txt += ' | Process memory in use: %s MB' % ram
                    txt += ' | Physical memory left: %s MB' % memLeft
                    file.write(txt + '\n')
                except Exception:
                    sys.exc_clear()

        else:
            file.write('No boot role available.\n')

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self._fmt % record.__dict__
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            try:
                record.asctime = self.formatTime(record, self.datefmt)
                traceID = NextTraceID()
                sys.stderr.write('#nolog: An exception has occurred. It will be logged in the log server as exception #{}\n'.format(traceID))
                exceptionString = 'EXCEPTION #%d' % traceID + ' logged at %(asctime)s : %(message)s\n%(exc_text)s\nReported from: ' + __name__ + '\nEXCEPTION END'
                s = exceptionString % record.__dict__
            except UnicodeError:
                s += record.exc_text.decode(sys.getfilesystemencoding(), 'replace')

        return s

    def formatException(self, ei):
        exctype, exc, tb = ei
        exception_list = traceback2.extract_tb(tb, extract_locals=True)
        if tb:
            caughtAt_list = traceback2.extract_stack(tb.tb_frame)
        else:
            caughtAt_list = traceback2.extract_stack(up=2)
        stack, stackID = GetStack(exception_list, caughtAt_list, show_locals=True)
        sio = cStringIO.StringIO()
        formatted_exception = traceback2.format_exception_only(exctype, exc)
        sio.write(' \n')
        sio.write('Formatted exception info:\n')
        for line in formatted_exception:
            sio.write(line)

        sio.write(' \n')
        for line in stack:
            sio.write(line)

        sio.write(' \n')
        self._LogThreadLocals(sio)
        self._LogServerInfo(sio)
        try:
            sio.write('Stackhash: {}\n'.format(stackID[0]))
        except Exception:
            pass

        s = sio.getvalue()
        sio.close()
        return s


class FmtExt(Fmt):
    EVETIME = '%d/%m/%y %H:%M:%S'
    FMT_EVE = EveExceptionsFormatter(None, EVETIME)


Fmt = FmtExt

def getLoggerExt(name = None, defaultHandler = None, defaultFormatter = None):
    lo = logging.getLogger(name)
    if not lo.handlers and defaultHandler:
        if defaultFormatter:
            defaultHandler.setFormatter(defaultFormatter)
        lo.addHandler(defaultHandler)
    return lo


GetTimestampedFilename = timestamped_filename
GetTimestamp = timestamp

def GetTimestampedFilename2(appname, basename = None, ext = '.log', fmt = '%Y-%m-%d-%H-%M-%S', timestruct = None, _getpid = os.getpid):
    if basename is None:
        basename = appname
    folder = devenv.GetAppFolder(appname, makedirs=True)
    return get_timestamped_logfilename(folder, basename, ext, fmt, timestruct, _getpid)


class _LogLevelDisplayInfo(object):

    def __init__(self):
        self.nameToLevel = {'Not Set': logging.NOTSET,
         'Debug': logging.DEBUG,
         'Info': logging.INFO,
         'Warn': logging.WARN,
         'Error': logging.ERROR,
         'Critical': logging.CRITICAL}
        self.levelToName = dict(zip(self.nameToLevel.values(), self.nameToLevel.keys()))
        sortedByLevel = sorted(self.nameToLevel.items(), key=lambda kvp: kvp[1])
        self.namesSortedByLevel = map(lambda kvp: kvp[0], sortedByLevel)


LogLevelDisplayInfo = _LogLevelDisplayInfo()
GetFilenamesFromLoggers = get_filenames_from_loggers
RemoveOldFiles = remove_old_files
_sentinel = object()

def AppLogConfig(appname, prefs = None, defaultUseStdOut = False, defaultLogLevelName = 'INFO'):
    if getattr(AppLogConfig, '__called', False):
        raise AssertionError('Should only be called once!')

    def getValue(reg, key):
        if prefs:
            return prefs.GetValue(reg, key, _sentinel)
        return _sentinel

    useStdOut = getValue('logging', 'usestdout')
    if useStdOut == _sentinel:
        useStdOut = defaultUseStdOut
        if prefs:
            prefs.SetValue('logging', 'usestdout', useStdOut)
    if useStdOut:
        sh = logging.StreamHandler()
        sh.setFormatter(Fmt.FMT_LM)
        logging.root.addHandler(sh)
    loglevelname = getValue('logging', 'loglevelname')
    if loglevelname == _sentinel:
        loglevelname = defaultLogLevelName
        if prefs:
            prefs.SetValue('logging', 'loglevelname', loglevelname)
    loglevel = getattr(logging, loglevelname)
    logging.root.setLevel(loglevel)
    logfilename = GetTimestampedFilename2(appname)
    fh = logging.FileHandler(logfilename)
    fh.setFormatter(Fmt.FMT_NTLM)
    logging.root.addHandler(fh)
    AppLogConfig.__called = True


LineWrap = wrap_line
