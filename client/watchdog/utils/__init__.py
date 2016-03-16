#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\__init__.py
import os
import sys
import threading
import watchdog.utils.platform
from watchdog.utils.compat import Event
from collections import namedtuple
if sys.version_info[0] == 2 and platform.is_windows():
    import win32stat
    stat = win32stat.stat
else:
    stat = os.stat

def has_attribute(ob, attribute):
    return getattr(ob, attribute, None) is not None


class UnsupportedLibc(Exception):
    pass


class BaseThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        if has_attribute(self, 'daemon'):
            self.daemon = True
        else:
            self.setDaemon(True)
        self._stopped_event = Event()
        if not has_attribute(self._stopped_event, 'is_set'):
            self._stopped_event.is_set = self._stopped_event.isSet

    @property
    def stopped_event(self):
        return self._stopped_event

    def should_keep_running(self):
        return not self._stopped_event.is_set()

    def on_thread_stop(self):
        pass

    def stop(self):
        self._stopped_event.set()
        self.on_thread_stop()

    def on_thread_start(self):
        pass

    def start(self):
        self.on_thread_start()
        threading.Thread.start(self)


def load_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        raise ImportError('No module named %s' % module_name)

    return sys.modules[module_name]


def load_class(dotted_path):
    dotted_path_split = dotted_path.split('.')
    if len(dotted_path_split) > 1:
        klass_name = dotted_path_split[-1]
        module_name = '.'.join(dotted_path_split[:-1])
        module = load_module(module_name)
        if has_attribute(module, klass_name):
            klass = getattr(module, klass_name)
            return klass
        raise AttributeError('Module %s does not have class attribute %s' % (module_name, klass_name))
    else:
        raise ValueError('Dotted module path %s must contain a module name and a classname' % dotted_path)
