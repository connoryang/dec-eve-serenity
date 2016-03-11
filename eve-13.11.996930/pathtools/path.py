#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\pathtools\path.py
import os.path
import os.path
from functools import partial
__all__ = ['get_dir_walker',
 'walk',
 'listdir',
 'list_directories',
 'list_files',
 'absolute_path',
 'real_absolute_path',
 'parent_dir_path']

def get_dir_walker(recursive, topdown = True, followlinks = False):
    if recursive:
        walk = partial(os.walk, topdown=topdown, followlinks=followlinks)
    else:

        def walk(path, topdown = topdown, followlinks = followlinks):
            try:
                yield next(os.walk(path, topdown=topdown, followlinks=followlinks))
            except NameError:
                yield os.walk(path, topdown=topdown, followlinks=followlinks).next()

    return walk


def walk(dir_pathname, recursive = True, topdown = True, followlinks = False):
    walk_func = get_dir_walker(recursive, topdown, followlinks)
    for root, dirnames, filenames in walk_func(dir_pathname):
        yield (root, dirnames, filenames)


def listdir(dir_pathname, recursive = True, topdown = True, followlinks = False):
    for root, dirnames, filenames in walk(dir_pathname, recursive, topdown, followlinks):
        for dirname in dirnames:
            yield absolute_path(os.path.join(root, dirname))

        for filename in filenames:
            yield absolute_path(os.path.join(root, filename))


def list_directories(dir_pathname, recursive = True, topdown = True, followlinks = False):
    for root, dirnames, filenames in walk(dir_pathname, recursive, topdown, followlinks):
        for dirname in dirnames:
            yield absolute_path(os.path.join(root, dirname))


def list_files(dir_pathname, recursive = True, topdown = True, followlinks = False):
    for root, dirnames, filenames in walk(dir_pathname, recursive, topdown, followlinks):
        for filename in filenames:
            yield absolute_path(os.path.join(root, filename))


def absolute_path(path):
    return os.path.abspath(os.path.normpath(path))


def real_absolute_path(path):
    return os.path.realpath(absolute_path(path))


def parent_dir_path(path):
    return absolute_path(os.path.dirname(path))
