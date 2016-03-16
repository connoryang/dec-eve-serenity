#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\data.py
import os
from coverage.backward import iitems, pickle, sorted
from coverage.files import PathAliases
from coverage.misc import file_be_gone

class CoverageData(object):

    def __init__(self, basename = None, collector = None, debug = None):
        self.collector = collector or 'unknown'
        self.debug = debug
        self.use_file = True
        self.filename = basename or '.coverage'
        self.filename = os.path.abspath(self.filename)
        self.lines = {}
        self.arcs = {}

    def usefile(self, use_file = True):
        self.use_file = use_file

    def read(self):
        if self.use_file:
            self.lines, self.arcs = self._read_file(self.filename)
        else:
            self.lines, self.arcs = {}, {}

    def write(self, suffix = None):
        if self.use_file:
            filename = self.filename
            if suffix:
                filename += '.' + suffix
            self.write_file(filename)

    def erase(self):
        if self.use_file:
            if self.filename:
                file_be_gone(self.filename)
        self.lines = {}
        self.arcs = {}

    def line_data(self):
        return dict([ (f, sorted(lmap.keys())) for f, lmap in iitems(self.lines) ])

    def arc_data(self):
        return dict([ (f, sorted(amap.keys())) for f, amap in iitems(self.arcs) ])

    def write_file(self, filename):
        data = {}
        data['lines'] = self.line_data()
        arcs = self.arc_data()
        if arcs:
            data['arcs'] = arcs
        if self.collector:
            data['collector'] = self.collector
        if self.debug and self.debug.should('dataio'):
            self.debug.write('Writing data to %r' % (filename,))
        fdata = open(filename, 'wb')
        try:
            pickle.dump(data, fdata, 2)
        finally:
            fdata.close()

    def read_file(self, filename):
        self.lines, self.arcs = self._read_file(filename)

    def raw_data(self, filename):
        if self.debug and self.debug.should('dataio'):
            self.debug.write('Reading data from %r' % (filename,))
        fdata = open(filename, 'rb')
        try:
            data = pickle.load(fdata)
        finally:
            fdata.close()

        return data

    def _read_file(self, filename):
        lines = {}
        arcs = {}
        try:
            data = self.raw_data(filename)
            if isinstance(data, dict):
                lines = dict([ (f, dict.fromkeys(linenos, None)) for f, linenos in iitems(data.get('lines', {})) ])
                arcs = dict([ (f, dict.fromkeys(arcpairs, None)) for f, arcpairs in iitems(data.get('arcs', {})) ])
        except Exception:
            pass

        return (lines, arcs)

    def combine_parallel_data(self, aliases = None):
        aliases = aliases or PathAliases()
        data_dir, local = os.path.split(self.filename)
        localdot = local + '.'
        for f in os.listdir(data_dir or '.'):
            if f.startswith(localdot):
                full_path = os.path.join(data_dir, f)
                new_lines, new_arcs = self._read_file(full_path)
                for filename, file_data in iitems(new_lines):
                    filename = aliases.map(filename)
                    self.lines.setdefault(filename, {}).update(file_data)

                for filename, file_data in iitems(new_arcs):
                    filename = aliases.map(filename)
                    self.arcs.setdefault(filename, {}).update(file_data)

                if f != local:
                    os.remove(full_path)

    def add_line_data(self, line_data):
        for filename, linenos in iitems(line_data):
            self.lines.setdefault(filename, {}).update(linenos)

    def add_arc_data(self, arc_data):
        for filename, arcs in iitems(arc_data):
            self.arcs.setdefault(filename, {}).update(arcs)

    def touch_file(self, filename):
        self.lines.setdefault(filename, {})

    def measured_files(self):
        return list(self.lines.keys())

    def executed_lines(self, filename):
        return self.lines.get(filename) or {}

    def executed_arcs(self, filename):
        return self.arcs.get(filename) or {}

    def add_to_hash(self, filename, hasher):
        hasher.update(self.executed_lines(filename))
        hasher.update(self.executed_arcs(filename))

    def summary(self, fullpath = False):
        summ = {}
        if fullpath:
            filename_fn = lambda f: f
        else:
            filename_fn = os.path.basename
        for filename, lines in iitems(self.lines):
            summ[filename_fn(filename)] = len(lines)

        return summ

    def has_arcs(self):
        return bool(self.arcs)


if __name__ == '__main__':
    import pprint, sys
    covdata = CoverageData()
    if sys.argv[1:]:
        fname = sys.argv[1]
    else:
        fname = covdata.filename
    pprint.pprint(covdata.raw_data(fname))
