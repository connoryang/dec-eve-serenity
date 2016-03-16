#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\win32stat.py
import ctypes
import ctypes.wintypes
import stat as stdstat
from collections import namedtuple
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
OPEN_EXISTING = 3
FILE_READ_ATTRIBUTES = 128
FILE_ATTRIBUTE_NORMAL = 128
FILE_ATTRIBUTE_READONLY = 1
FILE_ATTRIBUTE_DIRECTORY = 16
FILE_FLAG_BACKUP_SEMANTICS = 33554432
FILE_FLAG_OPEN_REPARSE_POINT = 2097152

class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', ctypes.wintypes.DWORD), ('dwHighDateTime', ctypes.wintypes.DWORD)]


class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [('dwFileAttributes', ctypes.wintypes.DWORD),
     ('ftCreationTime', FILETIME),
     ('ftLastAccessTime', FILETIME),
     ('ftLastWriteTime', FILETIME),
     ('dwVolumeSerialNumber', ctypes.wintypes.DWORD),
     ('nFileSizeHigh', ctypes.wintypes.DWORD),
     ('nFileSizeLow', ctypes.wintypes.DWORD),
     ('nNumberOfLinks', ctypes.wintypes.DWORD),
     ('nFileIndexHigh', ctypes.wintypes.DWORD),
     ('nFileIndexLow', ctypes.wintypes.DWORD)]


CreateFile = ctypes.windll.kernel32.CreateFileW
CreateFile.restype = ctypes.wintypes.HANDLE
CreateFile.argtypes = (ctypes.c_wchar_p,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD,
 ctypes.c_void_p,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.DWORD,
 ctypes.wintypes.HANDLE)
GetFileInformationByHandle = ctypes.windll.kernel32.GetFileInformationByHandle
GetFileInformationByHandle.restype = ctypes.wintypes.BOOL
GetFileInformationByHandle.argtypes = (ctypes.wintypes.HANDLE, ctypes.wintypes.POINTER(BY_HANDLE_FILE_INFORMATION))
CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.restype = ctypes.wintypes.BOOL
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
StatResult = namedtuple('StatResult', 'st_dev st_ino st_mode st_mtime')

def _to_mode(attr):
    m = 0
    if attr & FILE_ATTRIBUTE_DIRECTORY:
        m |= stdstat.S_IFDIR | 73
    else:
        m |= stdstat.S_IFREG
    if attr & FILE_ATTRIBUTE_READONLY:
        m |= 292
    else:
        m |= 438
    return m


def _to_unix_time(ft):
    t = ft.dwHighDateTime << 32 | ft.dwLowDateTime
    return t / 10000000 - 11644473600L


def stat(path):
    hfile = CreateFile(path, FILE_READ_ATTRIBUTES, 0, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, None)
    if hfile == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    info = BY_HANDLE_FILE_INFORMATION()
    r = GetFileInformationByHandle(hfile, info)
    CloseHandle(hfile)
    if not r:
        raise ctypes.WinError()
    return StatResult(st_dev=info.dwVolumeSerialNumber, st_ino=(info.nFileIndexHigh << 32) + info.nFileIndexLow, st_mode=_to_mode(info.dwFileAttributes), st_mtime=_to_unix_time(info.ftLastWriteTime))
