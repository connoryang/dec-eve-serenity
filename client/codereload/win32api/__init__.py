#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\codereload\win32api\__init__.py
try:
    import ctypes.wintypes
    _IS_NT = True
except (ImportError, ValueError):
    _IS_NT = False

if _IS_NT:
    import ctypes
    from ctypes.wintypes import HANDLE, POINT
    INVALID_HANDLE_VALUE = HANDLE(-1).value
    ctypes.windll.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    ctypes.windll.user32 = ctypes.WinDLL('user32', use_last_error=True)
    ctypes.windll.shell32 = ctypes.WinDLL('shell32', use_last_error=True)
    ctypes.windll.version = ctypes.WinDLL('version', use_last_error=True)

    def SetConsoleTitle(title):
        if not ctypes.windll.kernel32.SetConsoleTitleW(unicode(title)):
            raise ctypes.WinError()


    from .fs import CloseHandle, CreateFile, CreateHardLink, DefineDosDevice, GetFileInformationByHandle, GetLogicalDrives, QueryDosDevice, Constants as Win32FileConstants
    from .process import getppid
    from .waitables import FindFirstChangeNotification, FindNextChangeNotification, FindCloseChangeNotification, WaitForSingleObject, WaitForMultipleObjects, Waitables, FILE_NOTIFY_CHANGE_LAST_WRITE
