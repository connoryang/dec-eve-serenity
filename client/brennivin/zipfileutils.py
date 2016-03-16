#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\zipfileutils.py
import os as _os
import zipfile as _zipfile
from zipfile import ZipFile
if not hasattr(ZipFile, '__enter__'):

    class ZipFile27(ZipFile):

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.close()


    ZipFile = ZipFile27
from . import dochelpers, osutils

class FileComparisonError(Exception):
    pass


ALL = dochelpers.pretty_func(lambda _: True, 'ALL')
NONE = dochelpers.pretty_func(lambda _: False, 'NONE')

def write_files(fullpaths, zfile, include = ALL, exclude = NONE, subdir = None, rootpath = None):
    for path in fullpaths:
        if include(path) and not exclude(path):
            arcname = None
            if rootpath:
                arcname = _os.path.relpath(path, rootpath)
                if subdir:
                    arcname = _os.path.join(subdir, arcname)
            zfile.write(path, arcname)


def write_dir(rootpath, zfile, include = ALL, exclude = NONE, subdir = None):
    write_files(osutils.iter_files(rootpath), zfile, include, exclude, subdir, rootpath)


def zip_dir(rootdir, outfile, include = ALL, exclude = NONE, subdir = None):
    outdir = _os.path.dirname(outfile)
    if not _os.path.exists(outdir):
        _os.makedirs(outdir)
    with ZipFile(outfile, 'w', _zipfile.ZIP_DEFLATED) as zfile:
        write_dir(rootdir, zfile, include, exclude, subdir)


def is_inside_zipfile(filepath):
    folderpath, filename = _os.path.split(filepath)
    is_zip = False
    while folderpath and filename:
        if _os.path.exists(folderpath):
            if _zipfile.is_zipfile(folderpath):
                is_zip = True
            break
        folderpath, filename = _os.path.split(folderpath)

    return is_zip


def _sorted_infolist(zippath):
    return sorted(_zipfile.ZipFile(zippath).infolist(), key=lambda zi: zi.filename)


def compare_zip_files(z1, z2):
    f1infos = _sorted_infolist(z1)
    f2infos = _sorted_infolist(z2)
    f1names = [ f.filename for f in f1infos ]
    f2names = [ f.filename for f in f2infos ]
    if f1names != f2names:
        raise FileComparisonError('File lists differ: %s, %s' % (f1names, f2names))
    for f1i, f2i in zip(f1infos, f2infos):
        if f1i.CRC != f2i.CRC:
            raise FileComparisonError('%s CRCs different.' % f1i.filename)
