#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\brennivin\yamlext.py
import yaml as _yaml
__all__ = ['dumps',
 'dumpfile',
 'dump',
 'loads',
 'loadfile',
 'load',
 'PyIO']

class PyIO(object):

    def __init__(self):
        self._loader = _yaml.Loader
        self._dumper = _yaml.Dumper

    def dumps(self, obj, **kwargs):
        return self.dump(obj, None, **kwargs)

    def dumpfile(self, obj, path, **kwargs):
        with open(path, 'w') as f:
            self.dump(obj, f, **kwargs)

    def dump(self, obj, stream, **kwargs):
        return _yaml.dump(obj, stream, Dumper=self._dumper, **kwargs)

    def loads(self, s):
        return self.load(s)

    def loadfile(self, path):
        with open(path) as f:
            return self.load(f)

    def load(self, stream):
        return _yaml.load(stream, Loader=self._loader)


class CIO(PyIO):

    @classmethod
    def is_supported(cls):
        return hasattr(_yaml, 'CLoader')

    def __init__(self):
        PyIO.__init__(self)
        self._loader = self._dumper = None
        if self.is_supported():
            self._loader = _yaml.CLoader
            self._dumper = _yaml.CDumper


def _preferred():
    if CIO.is_supported():
        return CIO()
    return PyIO()


def dumps(obj, **kwargs):
    return _preferred().dumps(obj, **kwargs)


def dumpfile(obj, path, **kwargs):
    return _preferred().dumpfile(obj, path, **kwargs)


def dump(obj, stream, **kwargs):
    return _preferred().dump(obj, stream, **kwargs)


def loads(s):
    return _preferred().loads(s)


def loadfile(path):
    return _preferred().loadfile(path)


def load(stream):
    return _preferred().load(stream)
