#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\whitelistpickle\__init__.py
import cPickle
import cStringIO
try:
    import blue
except ImportError:
    blue = None

cPickleUnpickler = cPickle.Unpickler

def get_whitelist():
    return blue.marshal.globalsWhitelist


def find_global(moduleName, className, getwhitelist = None):
    fromlist = []
    if '.' in moduleName:
        fromlist.append(moduleName[moduleName.index('.'):])
    mod = __import__(moduleName, globals(), locals(), fromlist)
    obj = getattr(mod, className)
    if obj in (getwhitelist or get_whitelist)():
        return obj
    raise cPickle.UnpicklingError('%s.%s not in whitelist' % (moduleName, className))


def Unpickler(file):
    u = cPickleUnpickler(file)
    u.find_global = find_global
    return u


def load(fileObj):
    return cPickle.Unpickler(fileObj).load()


def loads(blob):
    return load(cStringIO.StringIO(blob))


def patch_cPickle():
    cPickle.Unpickler = Unpickler
    cPickle.load = load
    cPickle.loads = loads
