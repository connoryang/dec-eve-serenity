#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\results.py
import os
from coverage.backward import iitems, set, sorted
from coverage.misc import format_lines, join_regex, NoSource
from coverage.parser import CodeParser

class Analysis(object):

    def __init__(self, cov, code_unit):
        self.coverage = cov
        self.code_unit = code_unit
        self.filename = self.code_unit.filename
        actual_filename, source = self.find_source(self.filename)
        self.parser = CodeParser(text=source, filename=actual_filename, exclude=self.coverage._exclude_regex('exclude'))
        self.statements, self.excluded = self.parser.parse_source()
        executed = self.coverage.data.executed_lines(self.filename)
        exec1 = self.parser.first_lines(executed)
        self.missing = sorted(set(self.statements) - set(exec1))
        if self.coverage.data.has_arcs():
            self.no_branch = self.parser.lines_matching(join_regex(self.coverage.config.partial_list), join_regex(self.coverage.config.partial_always_list))
            n_branches = self.total_branches()
            mba = self.missing_branch_arcs()
            n_partial_branches = sum([ len(v) for k, v in iitems(mba) if k not in self.missing ])
            n_missing_branches = sum([ len(v) for k, v in iitems(mba) ])
        else:
            n_branches = n_partial_branches = n_missing_branches = 0
            self.no_branch = set()
        self.numbers = Numbers(n_files=1, n_statements=len(self.statements), n_excluded=len(self.excluded), n_missing=len(self.missing), n_branches=n_branches, n_partial_branches=n_partial_branches, n_missing_branches=n_missing_branches)

    def find_source(self, filename):
        source = None
        base, ext = os.path.splitext(filename)
        TRY_EXTS = {'.py': ['.py', '.pyw'],
         '.pyw': ['.pyw']}
        try_exts = TRY_EXTS.get(ext)
        if not try_exts:
            return (filename, None)
        for try_ext in try_exts:
            try_filename = base + try_ext
            if os.path.exists(try_filename):
                return (try_filename, None)
            source = self.coverage.file_locator.get_zip_data(try_filename)
            if source:
                return (try_filename, source)

        raise NoSource("No source for code: '%s'" % filename)

    def missing_formatted(self):
        return format_lines(self.statements, self.missing)

    def has_arcs(self):
        return self.coverage.data.has_arcs()

    def arc_possibilities(self):
        arcs = self.parser.arcs()
        return arcs

    def arcs_executed(self):
        executed = self.coverage.data.executed_arcs(self.filename)
        m2fl = self.parser.first_line
        executed = [ (m2fl(l1), m2fl(l2)) for l1, l2 in executed ]
        return sorted(executed)

    def arcs_missing(self):
        possible = self.arc_possibilities()
        executed = self.arcs_executed()
        missing = [ p for p in possible if p not in executed and p[0] not in self.no_branch ]
        return sorted(missing)

    def arcs_unpredicted(self):
        possible = self.arc_possibilities()
        executed = self.arcs_executed()
        unpredicted = [ e for e in executed if e not in possible and e[0] != e[1] ]
        return sorted(unpredicted)

    def branch_lines(self):
        exit_counts = self.parser.exit_counts()
        return [ l1 for l1, count in iitems(exit_counts) if count > 1 ]

    def total_branches(self):
        exit_counts = self.parser.exit_counts()
        return sum([ count for count in exit_counts.values() if count > 1 ])

    def missing_branch_arcs(self):
        missing = self.arcs_missing()
        branch_lines = set(self.branch_lines())
        mba = {}
        for l1, l2 in missing:
            if l1 in branch_lines:
                if l1 not in mba:
                    mba[l1] = []
                mba[l1].append(l2)

        return mba

    def branch_stats(self):
        exit_counts = self.parser.exit_counts()
        missing_arcs = self.missing_branch_arcs()
        stats = {}
        for lnum in self.branch_lines():
            exits = exit_counts[lnum]
            try:
                missing = len(missing_arcs[lnum])
            except KeyError:
                missing = 0

            stats[lnum] = (exits, exits - missing)

        return stats


class Numbers(object):
    _precision = 0
    _near0 = 1.0
    _near100 = 99.0

    def __init__(self, n_files = 0, n_statements = 0, n_excluded = 0, n_missing = 0, n_branches = 0, n_partial_branches = 0, n_missing_branches = 0):
        self.n_files = n_files
        self.n_statements = n_statements
        self.n_excluded = n_excluded
        self.n_missing = n_missing
        self.n_branches = n_branches
        self.n_partial_branches = n_partial_branches
        self.n_missing_branches = n_missing_branches

    def set_precision(cls, precision):
        cls._precision = precision
        cls._near0 = 1.0 / 10 ** precision
        cls._near100 = 100.0 - cls._near0

    set_precision = classmethod(set_precision)

    def _get_n_executed(self):
        return self.n_statements - self.n_missing

    n_executed = property(_get_n_executed)

    def _get_n_executed_branches(self):
        return self.n_branches - self.n_missing_branches

    n_executed_branches = property(_get_n_executed_branches)

    def _get_pc_covered(self):
        if self.n_statements > 0:
            pc_cov = 100.0 * (self.n_executed + self.n_executed_branches) / (self.n_statements + self.n_branches)
        else:
            pc_cov = 100.0
        return pc_cov

    pc_covered = property(_get_pc_covered)

    def _get_pc_covered_str(self):
        pc = self.pc_covered
        if 0 < pc < self._near0:
            pc = self._near0
        elif self._near100 < pc < 100:
            pc = self._near100
        else:
            pc = round(pc, self._precision)
        return '%.*f' % (self._precision, pc)

    pc_covered_str = property(_get_pc_covered_str)

    def pc_str_width(cls):
        width = 3
        if cls._precision > 0:
            width += 1 + cls._precision
        return width

    pc_str_width = classmethod(pc_str_width)

    def __add__(self, other):
        nums = Numbers()
        nums.n_files = self.n_files + other.n_files
        nums.n_statements = self.n_statements + other.n_statements
        nums.n_excluded = self.n_excluded + other.n_excluded
        nums.n_missing = self.n_missing + other.n_missing
        nums.n_branches = self.n_branches + other.n_branches
        nums.n_partial_branches = self.n_partial_branches + other.n_partial_branches
        nums.n_missing_branches = self.n_missing_branches + other.n_missing_branches
        return nums

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented
