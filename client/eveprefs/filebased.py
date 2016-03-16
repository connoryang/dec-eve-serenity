#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveprefs\filebased.py
import abc
import logging
import blue
from . import BaseIniFile, get_filename
L = logging.getLogger(__name__)

class FileBasedIniFile(BaseIniFile):

    def __init__(self, shortname, ext, root = None, readOnly = False):
        self.filename = get_filename(blue, shortname, ext, root)
        self.readOnly = readOnly

    def _Read(self):
        try:
            result = blue.AtomicFileRead(self.filename)
        except WindowsError:
            result = ''

        return result

    @abc.abstractmethod
    def _GetSaveStr(self):
        pass

    def _FlushToDisk(self):
        if self.readOnly or not self.filename:
            return
        s = self._GetSaveStr()
        try:
            blue.AtomicFileWrite(self.filename, s)
        except Exception:
            L.error('Failed writing %s, switching to read-only', self.filename)
            self.readOnly = True
