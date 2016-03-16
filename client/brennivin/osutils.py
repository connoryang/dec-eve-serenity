#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\osutils.py
import binascii as _binascii
import contextlib as _contextlib
import errno as _errno
import fnmatch as _fnmatch
import ntpath
import os as _os
import shutil as _shutil
import stat as _stat
import tempfile as _tempfile
import threading as _threading
altsep = _os.altsep
if altsep is None:
    altsep = _os.sep

def abspathex(path, relative_to, _ignore_this = False):
    absRelativeTo = _os.path.abspath(relative_to)
    with change_cwd(absRelativeTo):
        if _ignore_this:
            raise ArithmeticError
        return _os.path.abspath(path)


_changecwd_lock = _threading.Lock()

@_contextlib.contextmanager
def change_cwd(cwd):
    orig = None
    _changecwd_lock.acquire()
    try:
        orig = _os.getcwd()
        _os.chdir(cwd)
        yield
    finally:
        if orig is not None:
            _os.chdir(orig)
        _changecwd_lock.release()


@_contextlib.contextmanager
def change_environ(key, newvalue):
    oldvalue = _os.environ.get(key, None)
    if newvalue is None:
        _os.environ.pop(key, None)
    else:
        _os.environ[key] = newvalue
    try:
        yield
    finally:
        if oldvalue is None:
            _os.environ.pop(key, None)
        else:
            _os.environ[key] = oldvalue


def change_ext(path, ext):
    root, ext_ = _os.path.splitext(path)
    ext_ = ext
    return root + ext_


def copy(src, dst):
    dirname = _os.path.dirname(dst)
    if not _os.path.isdir(dirname):
        _os.makedirs(dirname)
    _shutil.copy(src, dst)


def crc_from_filename(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return _binascii.crc32(data) & 4294967295L


def iter_files(directory, pattern = '*'):
    for root, dirs, files in _os.walk(directory):
        for basename in files:
            if _fnmatch.fnmatch(basename, pattern):
                filename = _os.path.join(root, basename)
                yield filename


def listdirex(path, pattern = '*.*'):
    return [ _os.path.join(path, fn) for fn in _os.listdir(path) if _fnmatch.fnmatch(fn, pattern) ]


def makedirs(path, mode = 511):
    try:
        _os.makedirs(path, mode)
    except OSError as err:
        if err.errno != _errno.EEXIST:
            raise

    return path


def mktemp(*args, **kwargs):
    handle, filename = _tempfile.mkstemp(*args, **kwargs)
    _os.close(handle)
    return filename


def path_components(path):
    parts = []
    while True:
        newpath, tail = ntpath.split(path)
        if newpath == path:
            if path:
                parts.append(path)
            break
        parts.append(tail)
        path = newpath

    parts.reverse()
    return parts


def purename(filename):
    if filename is None:
        raise TypeError('filename cannot be None.')
    f = _os.path.basename(filename)
    return _os.path.splitext(f)[0]


def set_readonly(path, state):
    mode = _stat.S_IREAD if state else _stat.S_IWRITE
    _os.chmod(path, mode)


def split3(path):
    dirname, filename = _os.path.split(path)
    filename, ext = _os.path.splitext(filename)
    return (dirname, filename, ext)
