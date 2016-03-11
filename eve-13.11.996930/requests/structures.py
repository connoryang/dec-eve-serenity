#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\structures.py
import os
import collections
from itertools import islice

class IteratorProxy(object):

    def __init__(self, i):
        self.i = i

    def __iter__(self):
        return self.i

    def __len__(self):
        if hasattr(self.i, '__len__'):
            return len(self.i)
        if hasattr(self.i, 'len'):
            return self.i.len
        if hasattr(self.i, 'fileno'):
            return os.fstat(self.i.fileno()).st_size

    def read(self, n):
        return ''.join(islice(self.i, None, n))


class CaseInsensitiveDict(collections.MutableMapping):

    def __init__(self, data = None, **kwargs):
        self._store = dict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, mappedvalue in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        return ((lowerkey, keyval[1]) for lowerkey, keyval in self._store.items())

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        return dict(self.lower_items()) == dict(other.lower_items())

    def copy(self):
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))


class LookupDict(dict):

    def __init__(self, name = None):
        self.name = name
        super(LookupDict, self).__init__()

    def __repr__(self):
        return "<lookup '%s'>" % self.name

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default = None):
        return self.__dict__.get(key, default)
