#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\localstorage\__init__.py
from stackless import getcurrent
import weakref
import __builtin__

class Sissy:

    def __init__(self, what):
        self.__dict__['__sissywhat__'] = what

    def _Obj(self):
        try:
            obj = GetLocalStorage()[self.__sissywhat__]
            if type(obj) is weakref.ref:
                obj = obj()
            return obj
        except (KeyError, ReferenceError):
            return None

    def __nonzero__(self):
        return bool(self._Obj())

    def __repr__(self):
        return '<Sissy: ' + repr(self._Obj()) + ' >'

    def __getattr__(self, k):
        try:
            obj = GetLocalStorage()[self.__sissywhat__]
            if type(obj) is weakref.ref:
                obj = obj()
        except (KeyError, ReferenceError):
            obj = None

        return getattr(obj, k)

    def __setattr__(self, k, v):
        return setattr(self._Obj(), k, v)


mainLocalStorage = {}

def GetLocalStorage():
    global mainLocalStorage
    return getattr(getcurrent(), 'localStorage', mainLocalStorage)


def GetOtherLocalStorage(t):
    return getattr(t, 'localStorage', mainLocalStorage)


def SetLocalStorage(s):
    global mainLocalStorage
    try:
        getcurrent().localStorage = s
    except AttributeError:
        mainLocalStorage = s


def UpdateLocalStorage(props):
    try:
        ls = getcurrent().localStorage
    except AttributeError:
        ls = mainLocalStorage

    ret = dict(ls)
    ls.update(props)
    return ret


class UpdatedLocalStorage(object):

    def __init__(self, updatedDict):
        self.__store = updatedDict

    def __enter__(self):
        self.__store = UpdateLocalStorage(self.__store)

    def __exit__(self, e, v, tb):
        SetLocalStorage(self.__store)


__builtin__.charsession = Sissy('base.charsession')
__builtin__.currentcall = Sissy('base.currentcall')
__builtin__.session = Sissy('base.session')
__builtin__.caller = Sissy('base.caller')
