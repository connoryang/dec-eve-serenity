#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveprefs\iniformat.py
from cPickle import Unpickler, dumps
import cStringIO
import re
import types
from . import DEFAULT_ENCODING
from .filebased import FileBasedIniFile

class IniIniFile(FileBasedIniFile):
    nopickles = [types.IntType,
     types.FloatType,
     types.LongType,
     types.StringType,
     types.UnicodeType]
    number = re.compile('[\\-]?[\\d.]+')

    def __init__(self, shortname, root = None, readOnly = False):
        FileBasedIniFile.__init__(self, shortname, '.ini', root, readOnly)
        self.keyval = {}
        self.lines = self._Read().splitlines()
        oldLines = self.lines
        self.lines = []
        for newLine in oldLines:
            try:
                self.lines.append(unicode(newLine, DEFAULT_ENCODING).encode(DEFAULT_ENCODING))
            except:
                print 'Unencodable data discovered in ini file. Removing offending data.'

        for line in self.lines:
            sline = line.strip()
            if sline and sline[0] not in '[;#':
                sep = sline.find('=')
                if sep >= 0:
                    key = sline[:sep].strip()
                    self.keyval[key] = line

    def _GetKeySet(self):
        return self.keyval

    def _GetValue(self, key):
        value = self.keyval[key]
        sep = value.find('=')
        value = value[sep + 1:].strip()
        if not len(value):
            return value
        if value.startswith('"') and value.endswith('"'):
            return unicode(value[1:-1])
        if value[:7] == 'pickle:':
            io = cStringIO.StringIO(value[7:].replace('\x1f', '\n'))
            return Unpickler(io).load()
        if self.number.match(value):
            try:
                return int(value)
            except ValueError:
                pass

            try:
                return float(value)
            except ValueError:
                pass

        return unicode(value)

    def _SetValue(self, key, value, forcePickle):
        line = self._GetLineFromFixedKeyAndValue(key, value, forcePickle)
        if key in self.keyval:
            old = self.keyval[key]
            if line == self.keyval[key]:
                return
            lineno = self.lines.index(old)
            self.lines.remove(old)
            self.lines.insert(lineno, line)
        else:
            self.lines.append(line)
        self.keyval[key] = line
        self._FlushToDisk()

    def _SpoofKey(self, key, value):
        key = self.FixKey(key)
        self.keyval[key] = self._GetLineFromFixedKeyAndValue(key, value)

    def FixKey(self, key):
        key = FileBasedIniFile.FixKey(self, key)
        return key.strip().replace('|', '||').replace('=', '-|-')

    def _GetLineFromFixedKeyAndValue(self, fixedKey, value, forcePickle = False):
        if type(value) in types.StringTypes:
            try:
                value = value.encode(DEFAULT_ENCODING)
            except UnicodeEncodeError:
                forcePickle = True
            except UnicodeDecodeError:
                forcePickle = True

        if forcePickle or type(value) not in self.nopickles:
            value = 'pickle:' + dumps(value).replace('\n', '\x1f')
        else:
            value = unicode(value).strip()
        return '%s=%s' % (fixedKey, value)

    def _DeleteValue(self, key):
        self.lines.remove(self.keyval[key])
        del self.keyval[key]
        self._FlushToDisk()

    def _GetSaveStr(self):
        sortlines = [ (line.lower()[:3], line) for line in self.lines ]
        sortlines.sort()
        lines = [ line[1] for line in sortlines ]
        savestr = '\r\n'.join(lines).encode('cp1252')
        return savestr
