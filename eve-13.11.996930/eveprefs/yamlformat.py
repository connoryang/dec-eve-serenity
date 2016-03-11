#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveprefs\yamlformat.py
import yamlext
from . import strip_spaces
from .filebased import FileBasedIniFile

class YamlIniFile(FileBasedIniFile):

    def __init__(self, shortname, root = None, readOnly = False):
        FileBasedIniFile.__init__(self, shortname, '.yaml', root, readOnly)
        obj = yamlext.loads(self._Read()) or {}
        self.keyval = strip_spaces(obj)

    def _GetKeySet(self):
        return self.keyval

    def _GetValue(self, key):
        return self.keyval[key]

    def _SetValue(self, key, value, forcePickle):
        if self.keyval.get(key) == value:
            return
        self.keyval[key] = value
        self._FlushToDisk()

    def _DeleteValue(self, key):
        del self.keyval[key]
        self._FlushToDisk()

    def _GetSaveStr(self):
        return yamlext.dumps(self.keyval)


class YamlIniFileTester(YamlIniFile):

    def __init__(self, shortname, root = None, readOnly = False, forceReload = False):
        import os, osutils
        from .iniformat import IniIniFile
        ini = IniIniFile(shortname, root, readOnly)
        output = osutils.ChangeExt(ini.filename, '.yaml')
        if not os.path.exists(output) or forceReload:
            keyvals = {k:ini.GetValue(k) for k in ini.GetKeys()}
            yamlext.dumpfile(keyvals, output)
        YamlIniFile.__init__(self, shortname, root, readOnly)
