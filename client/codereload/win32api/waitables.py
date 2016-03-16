#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\codereload\win32api\waitables.py
import ctypes
from ctypes.wintypes import BOOL, DWORD, HANDLE
import weakref
QS_ALLEVENTS = 1215
QS_ALLINPUT = 1279
QS_RAWINPUT = 1024
MWMO_ALERTABLE = 2
STATUS_WAIT_0 = 0L
STATUS_ABANDONED_WAIT_0 = 128L
WAIT_OBJECT_0 = STATUS_WAIT_0 + 0
WAIT_IO_COMPLETION = 192L
WAIT_ABANDONED_0 = STATUS_ABANDONED_WAIT_0 + 0
WAIT_FAILED = 4294967295L
INFINITE = 4294967295L
WAIT_TIMEOUT = 258L

class Waitables(object):

    def __init__(self):
        self.waitables = weakref.WeakValueDictionary()

    def InsertHandle(self, handle, callback):
        if handle is None:
            CreateEventW = ctypes.windll.kernel32.CreateEventW
            CreateEventW.restype = HANDLE
            handle = CreateEventW(None, BOOL(), BOOL(), None)
            if not handle:
                raise ctypes.WinError()
        self.waitables[handle] = callback
        return handle

    def RemoveHandle(self, handle, close = False):
        del self.waitables[handle]
        if close:
            if not ctypes.windll.kernel32.CloseHandle(HANDLE(handle)):
                raise ctypes.WinError()

    def Wait(self, milliseconds = 1000):
        handles, callbacks = self.waitables.keys(), self.waitables.values()
        HandleArray = ctypes.c_void_p * len(handles)
        handles = HandleArray(*handles)
        MsgWaitForMultipleObjectsEx = ctypes.windll.user32.MsgWaitForMultipleObjectsEx
        MsgWaitForMultipleObjectsEx.restype = DWORD
        ret = MsgWaitForMultipleObjectsEx(len(handles), handles, milliseconds, QS_ALLINPUT, MWMO_ALERTABLE)
        if WAIT_OBJECT_0 <= ret <= WAIT_OBJECT_0 + len(handles) - 1:
            idx = ret - WAIT_OBJECT_0
            if handles[idx] in self.waitables:
                callbacks[idx].OnObjectSignaled(handles[idx], False)
            return self.Wait(0)
        if ret == WAIT_OBJECT_0 + len(handles):
            return ret
        if WAIT_ABANDONED_0 <= ret <= WAIT_ABANDONED_0 + len(handles) - 1:
            idx = ret - WAIT_OBJECT_0
            if handles[idx] in self.waitables:
                callbacks[idx].OnObjectSignaled(handles[idx], True)
            return self.Wait(0)
        if ret == WAIT_IO_COMPLETION:
            return ret
        if ret == WAIT_TIMEOUT:
            return ret
        if ret == WAIT_FAILED:
            raise ctypes.WinError()
        else:
            raise RuntimeError('Wait: Unknown return value from MsgWaitForMultipleObjectsEx:', ret)


def WaitForSingleObject(handle, milliseconds = 0):
    ret = ctypes.windll.kernel32.WaitForSingleObject(handle, milliseconds)
    if ret == WAIT_OBJECT_0:
        return True
    if ret == WAIT_TIMEOUT:
        return False
    if ret == WAIT_FAILED:
        raise ctypes.WinError()
    else:
        raise RuntimeError('WaitForSingleObject: Unknown return value from wait:', ret)


def WaitForMultipleObjects(handles, waitAll, milliseconds):
    HandleArray = ctypes.c_void_p * len(handles)
    handles = HandleArray(*handles)
    ctypes.WaitForMultipleObjects(len(handles), handles, bool(waitAll), milliseconds)


FILE_NOTIFY_CHANGE_FILE_NAME = 1
FILE_NOTIFY_CHANGE_DIR_NAME = 2
FILE_NOTIFY_CHANGE_ATTRIBUTES = 4
FILE_NOTIFY_CHANGE_SIZE = 8
FILE_NOTIFY_CHANGE_LAST_WRITE = 16
FILE_NOTIFY_CHANGE_LAST_ACCESS = 32
FILE_NOTIFY_CHANGE_CREATION = 64
FILE_NOTIFY_CHANGE_SECURITY = 256

def FindFirstChangeNotification(pathName, watchSubTree, notifyFilter):
    FindFirstChangeNotificationW = ctypes.windll.kernel32.FindFirstChangeNotificationW
    FindFirstChangeNotificationW.restype = HANDLE
    return FindFirstChangeNotificationW(unicode(pathName), bool(watchSubTree), notifyFilter)


def FindNextChangeNotification(handle):
    if not ctypes.windll.kernel32.FindNextChangeNotification(HANDLE(handle)):
        raise ctypes.WinError()


def FindCloseChangeNotification(handle):
    if not ctypes.windll.kernel32.FindCloseChangeNotification(HANDLE(handle)):
        raise ctypes.WinError()
