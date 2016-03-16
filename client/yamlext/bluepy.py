#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\yamlext\bluepy.py
from collections import OrderedDict
import yaml
from . import PyIO
cyaml_supported = hasattr(yaml, 'CLoader')

def isNumber(string):
    try:
        int(string)
        return True
    except ValueError:
        try:
            float(string)
            return True
        except ValueError:
            pass

    return False


class BlueRepresenter(yaml.representer.Representer):

    def __init__(self, default_style = None, default_flow_style = None):
        yaml.representer.Representer.__init__(self, default_style, default_flow_style)

    def represent_sequence(self, tag, sequence, flow_style = None):
        node = yaml.representer.Representer.represent_sequence(self, tag, sequence, flow_style)
        firstElement = sequence[0]
        if not isinstance(firstElement, (dict, OrderedDict, list)):
            node.flow_style = True
        for listItem in node.value:
            if isinstance(listItem.value, (str, unicode)) and not isNumber(listItem.value):
                listItem.style = '"'

        return node

    def represent_mapping(self, tag, mapping, flow_style = None):
        node = yaml.representer.Representer.represent_mapping(self, tag, mapping, flow_style)
        for nodeKey, nodeValue in node.value:
            keyValue = nodeKey.value
            valueValue = nodeValue.value
            if keyValue != 'type' and isinstance(valueValue, (str, unicode)) and not isNumber(valueValue):
                nodeValue.style = '"'

        return node


if cyaml_supported:
    from _yaml import CEmitter

    class BlueDumper(CEmitter, yaml.serializer.Serializer, BlueRepresenter, yaml.resolver.Resolver):

        def __init__(self, stream, default_style = None, default_flow_style = None, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None, encoding = None, explicit_start = None, explicit_end = None, version = None, tags = None):
            CEmitter.__init__(self, stream, canonical=canonical, indent=indent, width=width, encoding=encoding, allow_unicode=allow_unicode, line_break=line_break, explicit_start=explicit_start, explicit_end=explicit_end, version=version, tags=tags)
            BlueRepresenter.__init__(self, default_style=default_style, default_flow_style=False)
            yaml.resolver.Resolver.__init__(self)


    class BlueLoader(yaml.CLoader):
        pass


else:

    class BlueDumper(yaml.emitter.Emitter, yaml.serializer.Serializer, BlueRepresenter, yaml.resolver.Resolver):

        def __init__(self, stream, default_style = None, default_flow_style = None, canonical = None, indent = None, width = None, allow_unicode = None, line_break = None, encoding = None, explicit_start = None, explicit_end = None, version = None, tags = None):
            yaml.emitter.Emitter.__init__(self, stream, canonical=canonical, indent=indent, width=width, allow_unicode=allow_unicode, line_break=line_break)
            yaml.serializer.Serializer.__init__(self, encoding=encoding, explicit_start=explicit_start, explicit_end=explicit_end, version=version, tags=tags)
            BlueRepresenter.__init__(self, default_style=default_style, default_flow_style=True)
            yaml.resolver.Resolver.__init__(self)


    class BlueLoader(yaml.Loader):
        pass


def _construct_mapping(loader, node):
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


def _dict_representer(dumper, d):
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, d.items())


BlueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)
BlueDumper.add_representer(OrderedDict, _dict_representer)

class _BlueIO(PyIO):

    def __init__(self):
        PyIO.__init__(self)
        self._loader = self._dumper = None
        self._loader = BlueLoader
        self._dumper = BlueDumper


def loads(s):
    return _BlueIO().loads(s)


def loadfile(path):
    return _BlueIO().loadfile(path)


def load(stream):
    return _BlueIO().load(stream)


def dumps(obj, **kwargs):
    return _BlueIO().dumps(obj, **kwargs)


def dump(obj, stream, **kwargs):
    return _BlueIO().dump(obj, stream, **kwargs)


def dumpfile(obj, path, **kwargs):
    return _BlueIO().dumpfile(obj, path, **kwargs)
