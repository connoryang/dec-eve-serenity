#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsdlite\storage.py
import os
import time
import fnmatch
import fsdlite
import weakref
import collections
import contextlib
try:
    import P4
except ImportError:
    P4 = None

class Storage(collections.MutableMapping):

    def __init__(self, data = None, cache = None, mapping = None, indexes = None, monitor = False, coerce = None):
        self.extension = '.staticdata'
        self.cache_path = cache
        self.coerce = coerce or str
        self.immutable = True
        self.file_monitor = None
        self.files = None
        self.objects = {}
        self._path = os.path.abspath(data) if data else None
        self._cache = None
        self._mapping = mapping
        self._indexes = indexes
        self._file_init()
        self.monitor = monitor
        self.waiting = False

    def __getitem__(self, key):
        if key is None:
            raise KeyError
        try:
            return self._object_load(key)
        except KeyError:
            pass

        try:
            if self.monitor:
                file_time = self._file_time(key)
                cache_time = self._cache_time(key)
            else:
                file_time = cache_time = 0
            if cache_time >= file_time:
                return self._cache_load(key)
        except KeyError:
            pass

        return self._file_load(key)

    def __setitem__(self, key, item):
        if self.immutable:
            raise RuntimeError('FSD Storage is Immutable')
        old_monitor, self.monitor = self.monitor, False
        self._file_save(key, item)
        self._cache_save(key, item)
        self._object_save(key, item)
        self.monitor = old_monitor

    def __delitem__(self, key):
        if self.immutable:
            raise RuntimeError('FSD Storage is Immutable')

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        return iter(self.keys())

    def __enter__(self):
        self.immutable = False

    def __exit__(self, *args):
        self.immutable = True

    def __contains__(self, key):
        try:
            key = self.coerce(key)
        except TypeError:
            return False

        if key in self.objects:
            return True
        elif self.files:
            return key in self.files
        elif self.cache:
            return key in self.cache
        else:
            return False

    @property
    def path(self):
        return self._path

    @property
    def mapping(self):
        return self._mapping

    @property
    def indexes(self):
        return self._indexes

    @path.setter
    def path(self, value):
        if self.objects:
            self.objects.clear()
        if self.cache:
            self.cache.clear()
        self._path = os.path.abspath(value)
        self.files = None
        self._file_init()
        self.monitor = self.monitor

    def keys(self):
        if self.files:
            return [ self.coerce(key) for key in self.files.keys() ]
        if self.cache:
            return [ self.coerce(key) for key in self.cache.keys() ]
        return []

    def Get(self, key):
        return self[key]

    def prime(self, path = None):
        keys = set(self.keys())
        for key, (filename, timestamp) in self.files.iteritems():
            if path is None or fnmatch.fnmatch(filename, path):
                keys.add(self.coerce(key))

        for key in keys:
            self[key]

    def filter_keys(self, name, key):
        if self.cache:
            return [ self.coerce(key) for key in self.cache.index('{}.{}'.format(name, key)) ]
        return []

    def filter(self, name, key):
        return [ self[key] for key in self.filter_keys(name, key) ]

    def index(self, name, key):
        try:
            return self.filter(name, key)[0]
        except IndexError:
            raise KeyError

    def key_path(self, key):
        return self._file_path(key)

    def _object_load(self, key):
        return self.objects[self.coerce(key)]

    def _object_save(self, key, obj):
        key = self.coerce(key)
        self.objects[key] = obj

    def _object_discard(self, key):
        key = self.coerce(key)
        self.objects.pop(key, None)

    def _cache_load(self, key):
        if self.cache:
            data = self.cache[self.coerce(key)]
            obj = fsdlite.decode(data, mapping=self.mapping, json=True)
            self._object_save(key, obj)
            return obj
        raise KeyError('No Cache')

    def _cache_save(self, key, obj):
        if self.cache:
            key = self.coerce(key)
            self.cache[key] = fsdlite.encode(obj, json=True)
            self.cache.index_clear(key)
            for indexName, indexKeys in fsdlite.index(obj, self.indexes).iteritems():
                for indexKey in indexKeys:
                    self.cache.index_set('{}.{}'.format(indexName, indexKey), key)

    def _cache_discard(self, key):
        if self.cache:
            try:
                del self.cache[self.coerce(key)]
            except KeyError:
                pass

    def _cache_time(self, key):
        if self.cache:
            try:
                return self.cache.time(self.coerce(key))
            except KeyError:
                pass

        return 0

    def _set_cache(self, value):
        if value is not None and not isinstance(value, str):
            raise ValueError('Cache path must be a string')
        self.cache_path = value
        self._cache = None

    def _get_cache(self):
        if self.cache_path and self._cache is None:
            self._cache = fsdlite.Cache(self.cache_path)
        return self._cache

    cache = property(_get_cache, _set_cache)

    def _file_init(self):
        if self.files is None:
            self.files = {}
            if self.path and os.path.isdir(self.path):
                for base, directories, files in os.walk(self.path):
                    for filename in files:
                        self._file_index(os.path.join(base, filename))

    def _file_index(self, filename):
        if fnmatch.fnmatch(filename, '*' + self.extension):
            key = self.coerce(self._file_key(filename))
            if os.path.exists(filename):
                modified = os.path.getmtime(filename)
                self.files[key] = (filename, modified)
            else:
                self.files.pop(key, None)
            return key

    def _file_changed(self, event, filename):
        key = self._file_index(filename)
        if key:
            self._object_discard(key)
            self._cache_discard(key)
            self.waiting = False

    def _file_load(self, key):
        if self.path:
            try:
                filepath, modified = self.files[self.coerce(key)]
                with open(filepath, 'r') as stream:
                    data = fsdlite.load(stream.read())
                    self._cache_save(key, data)
                    obj = fsdlite.decode(data, mapping=self.mapping)
                    self._object_save(key, obj)
                    return obj
            except IOError as exception:
                raise KeyError(exception)

        raise KeyError('No Static Data')

    def _file_save(self, key, obj):
        if self.path:
            try:
                filepath = self._file_path(key)
                with Checkout(filepath):
                    with open(filepath, 'w') as stream:
                        stream.write(fsdlite.dump(fsdlite.strip(obj)))
                self._file_index(filepath)
                return
            except IOError as exception:
                raise KeyError(exception)

        raise KeyError('No Static Data')

    def _file_time(self, key):
        if self.path:
            try:
                return self.files[self.coerce(key)][1]
            except KeyError:
                return time.time()

        return 0

    def _file_path(self, key):
        if self.path:
            return os.path.abspath(os.path.join(self.path, str(key) + self.extension))
        raise RuntimeError('Unable to determine file path, no data path provided')

    def _file_key(self, path):
        if self.path:
            key, _ = os.path.splitext(os.path.relpath(path, self.path))
            return key.replace('\\', '/')
        raise RuntimeError('Unable to determine file key, no data path provided')

    def _get_monitor(self):
        return self.file_monitor is not None

    def _set_monitor(self, value):
        monitor = getattr(self, 'file_monitor', None)
        if monitor:
            fsdlite.stop_file_monitor(monitor)
        if value and self.path:
            self.file_monitor = fsdlite.start_file_monitor(self.path, fsdlite.WeakMethod(self._file_changed))

    monitor = property(_get_monitor, _set_monitor)

    def wait(self):
        self.waiting = True
        while self.waiting:
            pass


class WeakStorage(Storage):

    def __init__(self, *args, **kwargs):
        Storage.__init__(self, *args, **kwargs)
        self.objects = weakref.WeakValueDictionary()


class EveStorage(Storage):

    def __init__(self, data, cache, *args, **kwargs):
        monitor = kwargs.get('monitor', True)
        try:
            import blue
            if blue.pyos.packaged:
                monitor = False
                data = None
                if boot.role == 'client':
                    import remotefilecache
                    cache = remotefilecache.prefetch_single_file('res:/staticdata/' + cache, verify=True)
                else:
                    cache = os.path.join(blue.paths.ResolvePath(u'res:/staticdata'), cache)
            elif os.path.exists(blue.paths.ResolvePath(u'root:/staticData')):
                data = os.path.join(blue.paths.ResolvePath(u'root:/staticData'), data)
                cache = os.path.join(blue.paths.ResolvePath(u'root:/autobuild/staticData/server'), cache)
            elif os.path.exists(blue.paths.ResolvePath(u'res:/staticdata')):
                data = None
                cache = os.path.join(blue.paths.ResolvePath(u'res:/staticdata'), cache)
            else:
                raise ImportError
        except ImportError:
            data = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eve/staticData/', data))
            cache = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../eve/autobuild/staticData/server', cache))
            if not os.path.exists(data):
                data = None
            if not os.path.exists(os.path.dirname(cache)):
                cache = None

        kwargs['monitor'] = monitor
        Storage.__init__(self, data, cache, *args, **kwargs)


@contextlib.contextmanager
def Checkout(path):
    if P4:
        if not hasattr(Checkout, 'connection'):
            Checkout.connection = P4.P4()
            Checkout.connection.connect()
        try:
            Checkout.connection.run_edit(path)
        except P4.P4Exception:
            pass

    yield
