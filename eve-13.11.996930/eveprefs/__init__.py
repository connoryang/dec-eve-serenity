#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveprefs\__init__.py
import abc
import types
DEFAULT_ENCODING = 'cp1252'
_unsupplied = object()

def get_filename(blue, shortname, ext, root = None):
    if root is None:
        root = blue.paths.ResolvePath(u'settings:/')
    if root[-1] not in ('\\', '/'):
        root += '\\'
    if shortname[-len(ext):] != ext:
        filename = root + shortname + ext
    else:
        filename = root + shortname
    return filename


def strip_spaces(d):
    result = {}
    for k, v in d.iteritems():
        realv = v
        if isinstance(v, types.StringTypes):
            realv = v.strip()
        result[k.strip()] = realv

    return result


class BaseIniFile(object):
    __metaclass__ = abc.ABCMeta

    def HasKey(self, key):
        return self.FixKey(key) in self._GetKeySet()

    @abc.abstractmethod
    def _GetKeySet(self):
        pass

    def GetKeys(self, beginWith = None):
        if beginWith is None:
            keys = list(self._GetKeySet())
        else:
            beginWith = self.FixKey(beginWith)
            keys = [ key for key in self._GetKeySet() if key[:len(beginWith)] == beginWith ]
        return keys

    @abc.abstractmethod
    def _GetValue(self, key):
        pass

    def GetValue(self, key, default = _unsupplied, flushDef = False):
        key = self.FixKey(key)
        if key not in self._GetKeySet():
            if default is _unsupplied:
                raise KeyError(key)
            if flushDef:
                self.SetValue(key, default)
            return default
        return self._GetValue(key)

    @abc.abstractmethod
    def _SetValue(self, key, value, forcePickle):
        pass

    def SetValue(self, key, value, forcePickle = False):
        key = self.FixKey(key)
        self._SetValue(key, value, forcePickle)

    def _SpoofKey(self, key, value):
        raise NotImplementedError()

    def SpoofKey(self, key, value):
        key = self.FixKey(key)
        self._SpoofKey(key, value)

    def FixKey(self, key):
        try:
            key.decode('ascii')
        except UnicodeDecodeError:
            raise ValueError('key must be ascii')

        return str(key).strip()

    @abc.abstractmethod
    def _DeleteValue(self, key):
        pass

    def DeleteValue(self, key):
        key = self.FixKey(key)
        if key in self._GetKeySet():
            self._DeleteValue(key)


class Handler(object):

    def __init__(self, inifile):
        self.__dict__['ini'] = inifile

    def __getattr__(self, key):
        if hasattr(self.__dict__['ini'], key):
            return getattr(self.__dict__['ini'], key)
        try:
            return self.__dict__['ini'].GetValue(key)
        except KeyError:
            raise AttributeError, key

    def __setattr__(self, key, value):
        self.__dict__['ini'].SetValue(key, value)

    def __str__(self):
        ini = self.__dict__['ini']
        clsname = type(ini).__name__
        filename = ''
        if hasattr(ini, 'filename'):
            filename = ini.filename + ' '
        count = len(ini.GetKeys())
        return '%(clsname)s %(filename)swith %(count)s entries' % locals()

    def __eq__(self, _):
        return NotImplemented
