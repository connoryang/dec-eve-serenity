#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\annotate.py
import os, re
from coverage.report import Reporter

class AnnotateReporter(Reporter):

    def __init__(self, coverage, config):
        super(AnnotateReporter, self).__init__(coverage, config)
        self.directory = None

    blank_re = re.compile('\\s*(#|$)')
    else_re = re.compile('\\s*else\\s*:\\s*(#|$)')

    def report(self, morfs, directory = None):
        self.report_files(self.annotate_file, morfs, directory)

    def annotate_file(self, cu, analysis):
        if not cu.relative:
            return
        filename = cu.filename
        source = cu.source_file()
        if self.directory:
            dest_file = os.path.join(self.directory, cu.flat_rootname())
            dest_file += '.py,cover'
        else:
            dest_file = filename + ',cover'
        dest = open(dest_file, 'w')
        statements = analysis.statements
        missing = analysis.missing
        excluded = analysis.excluded
        lineno = 0
        i = 0
        j = 0
        covered = True
        while True:
            line = source.readline()
            if line == '':
                break
            lineno += 1
            while i < len(statements) and statements[i] < lineno:
                i += 1

            while j < len(missing) and missing[j] < lineno:
                j += 1

            if i < len(statements) and statements[i] == lineno:
                covered = j >= len(missing) or missing[j] > lineno
            if self.blank_re.match(line):
                dest.write('  ')
            elif self.else_re.match(line):
                if i >= len(statements) and j >= len(missing):
                    dest.write('! ')
                elif i >= len(statements) or j >= len(missing):
                    dest.write('> ')
                elif statements[i] == missing[j]:
                    dest.write('! ')
                else:
                    dest.write('> ')
            elif lineno in excluded:
                dest.write('- ')
            elif covered:
                dest.write('> ')
            else:
                dest.write('! ')
            dest.write(line)

        source.close()
        dest.close()
