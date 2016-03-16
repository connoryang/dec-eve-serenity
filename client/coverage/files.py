#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\files.py
from coverage.backward import to_string
from coverage.misc import CoverageException
import fnmatch, os, os.path, re, sys
import ntpath, posixpath

class FileLocator(object):

    def __init__(self):
        self.relative_dir = os.path.normcase(abs_file(os.curdir) + os.sep)
        self.canonical_filename_cache = {}

    def relative_filename(self, filename):
        fnorm = os.path.normcase(filename)
        if fnorm.startswith(self.relative_dir):
            filename = filename[len(self.relative_dir):]
        return filename

    def canonical_filename(self, filename):
        if filename not in self.canonical_filename_cache:
            if not os.path.isabs(filename):
                for path in [os.curdir] + sys.path:
                    if path is None:
                        continue
                    f = os.path.join(path, filename)
                    if os.path.exists(f):
                        filename = f
                        break

            cf = abs_file(filename)
            self.canonical_filename_cache[filename] = cf
        return self.canonical_filename_cache[filename]

    def get_zip_data(self, filename):
        import zipimport
        markers = ['.zip' + os.sep, '.egg' + os.sep]
        for marker in markers:
            if marker in filename:
                parts = filename.split(marker)
                try:
                    zi = zipimport.zipimporter(parts[0] + marker[:-1])
                except zipimport.ZipImportError:
                    continue

                try:
                    data = zi.get_data(parts[1])
                except IOError:
                    continue

                return to_string(data)


if sys.platform == 'win32':

    def actual_path(path):
        if path in actual_path.cache:
            return actual_path.cache[path]
        head, tail = os.path.split(path)
        if not tail:
            actpath = head
        elif not head:
            actpath = tail
        else:
            head = actual_path(head)
            if head in actual_path.list_cache:
                files = actual_path.list_cache[head]
            else:
                try:
                    files = os.listdir(head)
                except OSError:
                    files = []

                actual_path.list_cache[head] = files
            normtail = os.path.normcase(tail)
            for f in files:
                if os.path.normcase(f) == normtail:
                    tail = f
                    break

            actpath = os.path.join(head, tail)
        actual_path.cache[path] = actpath
        return actpath


    actual_path.cache = {}
    actual_path.list_cache = {}
else:

    def actual_path(filename):
        return filename


def abs_file(filename):
    path = os.path.expandvars(os.path.expanduser(filename))
    path = os.path.abspath(os.path.realpath(path))
    path = actual_path(path)
    return path


def isabs_anywhere(filename):
    return ntpath.isabs(filename) or posixpath.isabs(filename)


def prep_patterns(patterns):
    prepped = []
    for p in patterns or []:
        if p.startswith('*') or p.startswith('?'):
            prepped.append(p)
        else:
            prepped.append(abs_file(p))

    return prepped


class TreeMatcher(object):

    def __init__(self, directories):
        self.dirs = directories[:]

    def __repr__(self):
        return '<TreeMatcher %r>' % self.dirs

    def info(self):
        return self.dirs

    def add(self, directory):
        self.dirs.append(directory)

    def match(self, fpath):
        for d in self.dirs:
            if fpath.startswith(d):
                if fpath == d:
                    return True
                if fpath[len(d)] == os.sep:
                    return True

        return False


class FnmatchMatcher(object):

    def __init__(self, pats):
        self.pats = pats[:]

    def __repr__(self):
        return '<FnmatchMatcher %r>' % self.pats

    def info(self):
        return self.pats

    def match(self, fpath):
        for pat in self.pats:
            if fnmatch.fnmatch(fpath, pat):
                return True

        return False


def sep(s):
    sep_match = re.search('[\\\\/]', s)
    if sep_match:
        the_sep = sep_match.group(0)
    else:
        the_sep = os.sep
    return the_sep


class PathAliases(object):

    def __init__(self, locator = None):
        self.aliases = []
        self.locator = locator

    def add(self, pattern, result):
        pattern = pattern.rstrip('\\/')
        if pattern.endswith('*'):
            raise CoverageException('Pattern must not end with wildcards.')
        pattern_sep = sep(pattern)
        if not pattern.startswith('*') and not isabs_anywhere(pattern):
            pattern = abs_file(pattern)
        pattern += pattern_sep
        regex_pat = fnmatch.translate(pattern).replace('\\Z(', '(')
        if regex_pat.endswith('$'):
            regex_pat = regex_pat[:-1]
        regex_pat = regex_pat.replace('\\/', '[\\\\/]')
        regex = re.compile('(?i)' + regex_pat)
        result_sep = sep(result)
        result = result.rstrip('\\/') + result_sep
        self.aliases.append((regex,
         result,
         pattern_sep,
         result_sep))

    def map(self, path):
        for regex, result, pattern_sep, result_sep in self.aliases:
            m = regex.match(path)
            if m:
                new = path.replace(m.group(0), result)
                if pattern_sep != result_sep:
                    new = new.replace(pattern_sep, result_sep)
                if self.locator:
                    new = self.locator.canonical_filename(new)
                return new

        return path


def find_python_files(dirname):
    for i, (dirpath, dirnames, filenames) in enumerate(os.walk(dirname)):
        if i > 0 and '__init__.py' not in filenames:
            del dirnames[:]
            continue
        for filename in filenames:
            if re.match('^[^.#~!$@%^&*()+=,]+\\.pyw?$', filename):
                yield os.path.join(dirpath, filename)
