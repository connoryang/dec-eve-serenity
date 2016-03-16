#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsdlite\__init__.py
try:
    from _fsdlite import dump, load, encode, decode, strip
except:
    from .encoder import dump, load, encode, decode, strip

from .util import repr, Immutable, WeakMethod, extend_class, Extendable
from .monitor import start_file_monitor, stop_file_monitor
from .indexer import index
from .cache import Cache
from .storage import Storage, WeakStorage, EveStorage
