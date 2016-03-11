#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\codeunit.py
import glob, os
from coverage.backward import open_source, string_class, StringIO
from coverage.misc import CoverageException

def code_unit_factory(morfs, file_locator):
    if not isinstance(morfs, (list, tuple)):
        morfs = [morfs]
    globbed = []
    for morf in morfs:
        if isinstance(morf, string_class) and ('?' in morf or '*' in morf):
            globbed.extend(glob.glob(morf))
        else:
            globbed.append(morf)

    morfs = globbed
    code_units = [ CodeUnit(morf, file_locator) for morf in morfs ]
    return code_units


class CodeUnit(object):

    def __init__(self, morf, file_locator):
        self.file_locator = file_locator
        if hasattr(morf, '__file__'):
            f = morf.__file__
        else:
            f = morf
        if f.endswith('.pyc') or f.endswith('.pyo'):
            f = f[:-1]
        elif f.endswith('$py.class'):
            f = f[:-9] + '.py'
        self.filename = self.file_locator.canonical_filename(f)
        if hasattr(morf, '__name__'):
            n = modname = morf.__name__
            self.relative = True
        else:
            n = os.path.splitext(morf)[0]
            rel = self.file_locator.relative_filename(n)
            if os.path.isabs(n):
                self.relative = rel != n
            else:
                self.relative = True
            n = rel
            modname = None
        self.name = n
        self.modname = modname

    def __repr__(self):
        return '<CodeUnit name=%r filename=%r>' % (self.name, self.filename)

    def __lt__(self, other):
        return self.name < other.name

    def __le__(self, other):
        return self.name <= other.name

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return self.name != other.name

    def __gt__(self, other):
        return self.name > other.name

    def __ge__(self, other):
        return self.name >= other.name

    def flat_rootname(self):
        if self.modname:
            return self.modname.replace('.', '_')
        else:
            root = os.path.splitdrive(self.name)[1]
            return root.replace('\\', '_').replace('/', '_').replace('.', '_')

    def source_file(self):
        if os.path.exists(self.filename):
            return open_source(self.filename)
        source = self.file_locator.get_zip_data(self.filename)
        if source is not None:
            return StringIO(source)
        raise CoverageException("No source for code '%s'." % self.filename)

    def should_be_python(self):
        _, ext = os.path.splitext(self.filename)
        if ext.startswith('.py'):
            return True
        if not ext:
            return True
        return False
