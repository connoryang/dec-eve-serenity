#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsdlite\encoder.py
import re
import yaml
try:
    import ujson
except ImportError:
    import json as ujson

try:
    from yaml import CSafeLoader as Loader
    from yaml import CSafeDumper as Dumper
except ImportError:
    from yaml import SafeLoader as Loader
    from yaml import SafeDumper as Dumper

def dump(obj, json = False):
    if json:
        return ujson.dumps(obj)
    else:
        return yaml.dump(obj, Dumper=Dumper, default_flow_style=False, indent=4, allow_unicode=True)


def load(obj, json = False):
    if json:
        return ujson.loads(obj)
    else:
        return yaml.load(obj, Loader=Loader)


def encode(obj, json = False):
    return dump(to_primitives(obj), json=json)


def decode(obj, json = False, mapping = None):
    if isinstance(obj, basestring):
        obj = load(obj, json=json)
    return from_primitives(obj, compile_mapping(mapping))


def strip(obj):
    if hasattr(obj, 'iteritems'):
        values = {}
        for key, value in obj.iteritems():
            value = strip(value)
            if value is not None:
                values[key] = value

        return values
    if hasattr(obj, '__iter__'):
        values = []
        for value in obj:
            value = strip(value)
            if value is not None:
                values.append(value)

        return values
    if obj is not None:
        return obj


def compile_mapping(mapping):
    return [ (re.compile(r[0]), r[1]) for r in mapping or [] ]


def to_primitives(obj):
    if isinstance(obj, tuple) and hasattr(obj, '_fields'):
        state = {key:getattr(obj, key) for key in obj._fields if hasattr(obj, key)}
    elif hasattr(obj, '__getstate__'):
        state = obj.__getstate__()
    elif hasattr(obj, '__dict__'):
        state = obj.__dict__
    elif hasattr(obj, '__slots__'):
        state = {key:getattr(obj, key) for key in obj.__slots__ if hasattr(obj, key)}
    else:
        state = obj
    if hasattr(state, 'iteritems'):
        state = {key:to_primitives(value) for key, value in state.iteritems() if not str(key).startswith('__')}
    elif hasattr(state, 'itervalues'):
        state = [ to_primitives(value) for value in state.itervalues() ]
    elif hasattr(state, '__iter__'):
        state = [ to_primitives(value) for value in state ]
    return state


def from_primitives(data, mapping, path = None):
    if isinstance(data, dict):
        for key, value in data.iteritems():
            if isinstance(value, (dict, list)):
                data[key] = from_primitives(value, mapping, path + '.' + str(key) if path else str(key))

        for pattern, cls in mapping:
            if pattern.match(path or '') is not None:
                try:
                    obj = cls.__new__(cls)
                except TypeError:
                    if issubclass(cls, tuple) and hasattr(cls, '_fields'):
                        return cls.__new__(cls, **{key:data.get(key) for key in cls._fields})
                    raise
                except AttributeError:
                    try:
                        obj = object.__new__(cls)
                    except TypeError:
                        obj = cls()

                if hasattr(obj, '__enter__'):
                    with obj:
                        set_state(obj, data)
                else:
                    set_state(obj, data)
                return obj

    elif isinstance(data, list):
        for key, value in enumerate(data):
            if isinstance(value, (dict, list)):
                data[key] = from_primitives(value, mapping, path)

    return data


def set_state(obj, data):
    if hasattr(obj, '__setstate__'):
        obj.__setstate__(data)
    else:
        for key, value in data.iteritems():
            setattr(obj, key, value)
