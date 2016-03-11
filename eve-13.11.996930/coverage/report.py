#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\report.py
import fnmatch, os
from coverage.codeunit import code_unit_factory
from coverage.files import prep_patterns
from coverage.misc import CoverageException, NoSource, NotPython

class Reporter(object):

    def __init__(self, coverage, config):
        self.coverage = coverage
        self.config = config
        self.code_units = []
        self.directory = None

    def find_code_units(self, morfs):
        morfs = morfs or self.coverage.data.measured_files()
        file_locator = self.coverage.file_locator
        self.code_units = code_unit_factory(morfs, file_locator)
        if self.config.include:
            patterns = prep_patterns(self.config.include)
            filtered = []
            for cu in self.code_units:
                for pattern in patterns:
                    if fnmatch.fnmatch(cu.filename, pattern):
                        filtered.append(cu)
                        break

            self.code_units = filtered
        if self.config.omit:
            patterns = prep_patterns(self.config.omit)
            filtered = []
            for cu in self.code_units:
                for pattern in patterns:
                    if fnmatch.fnmatch(cu.filename, pattern):
                        break
                else:
                    filtered.append(cu)

            self.code_units = filtered
        self.code_units.sort()

    def report_files(self, report_fn, morfs, directory = None):
        self.find_code_units(morfs)
        if not self.code_units:
            raise CoverageException('No data to report.')
        self.directory = directory
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory)
        for cu in self.code_units:
            try:
                report_fn(cu, self.coverage._analyze(cu))
            except NoSource:
                if not self.config.ignore_errors:
                    raise
            except NotPython:
                if cu.should_be_python() and not self.config.ignore_errors:
                    raise
