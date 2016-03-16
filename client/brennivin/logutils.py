#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\logutils.py
import fnmatch as _fnmatch
import logging as _logging
import os as _os
import time as _time
try:
    NullHandler = _logging.NullHandler
except AttributeError:

    class NullHandler(_logging.Handler):

        def emit(self, record):
            pass


    _logging.NullHandler = NullHandler

class Fmt(object):
    NTLM = '%(name)s %(asctime)s %(levelname)s:  %(message)s'
    FMT_NTLM = _logging.Formatter(NTLM)
    LM = '%(levelname)s: %(message)s'
    FMT_LM = _logging.Formatter(LM)


class MultiLineIndentFormatter(_logging.Formatter):

    def __init__(self, fmt = None, datefmt = None, sep = ' '):
        _logging.Formatter.__init__(self, fmt, datefmt)
        self.sep = sep

    def format(self, record):
        formattedRecord = _logging.Formatter.format(self, record)
        header, footer = formattedRecord.split(record.msg)
        s = formattedRecord.replace('\n', '\n' + self.sep * len(header))
        return s


def timestamped_filename(filename, fmt = '%Y-%m-%d-%H-%M-%S', timestruct = None, sep = '_'):
    head, ext = _os.path.splitext(filename)
    timestr = timestamp(fmt, timestruct)
    return '%s%s%s%s' % (head,
     sep,
     timestr,
     ext)


def timestamp(fmt, timestruct = None):
    return _time.strftime(fmt, timestruct or _time.gmtime())


def get_timestamped_logfilename(folder, basename = None, ext = '.log', fmt = '%Y-%m-%d-%H-%M-%S', timestruct = None, _getpid = _os.getpid):
    if basename is None:
        basename = _os.path.basename(folder)
    timestamped = timestamp(fmt, timestruct)
    pid = _getpid()
    logname = '{basename}_{timestamped}_pid{pid}{ext}'.format(**locals())
    logfilename = _os.path.join(folder, logname)
    try:
        remove_old_files(folder, '*{basename}_*{ext}'.format(**locals()), 15)
    except OSError:
        pass

    return logfilename


def get_filenames_from_loggers(loggers = None, _loggingmodule = None):
    _loggingmodule = _loggingmodule or _logging
    if loggers is None:
        loggers = [_loggingmodule.root]
        loggers.extend(_loggingmodule.Logger.manager.loggerDict.values())
    allfilenames = set()
    for logger in filter(lambda lo: hasattr(lo, 'handlers'), loggers):
        filenames = [ getattr(h, 'baseFilename', None) for h in logger.handlers ]
        for f in filter(None, filenames):
            allfilenames.add(_os.path.abspath(f))

    return tuple(allfilenames)


def remove_old_files(root, namepattern = '*', maxfiles = 1):
    if maxfiles < 0:
        raise ValueError('maxfiles must be >= 0, got %s' % maxfiles)
    lstFiles = []
    for f in _os.listdir(root):
        if _fnmatch.fnmatch(f, namepattern):
            fileName = _os.path.join(root, f)
            lstFiles.append(fileName)

    lstFiles.sort(key=_os.path.getmtime, reverse=True)
    for f in lstFiles[maxfiles:]:
        try:
            _os.remove(f)
        except (OSError, IOError):
            pass


def wrap_line(s, maxlines, maxlen = 254, pfx = '- '):
    e = len(s)
    if e <= maxlen:
        yield s
    else:
        i = maxlen
        maxlen -= len(pfx)
        maxlines -= 1
        yield s[:i]
        while i < e and maxlines:
            yield pfx + s[i:i + maxlen]
            i += maxlen
            maxlines -= 1
