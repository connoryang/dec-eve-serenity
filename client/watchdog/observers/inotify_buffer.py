#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\observers\inotify_buffer.py
import logging
from watchdog.utils import BaseThread
from watchdog.utils.delayed_queue import DelayedQueue
from watchdog.observers.inotify_c import Inotify
logger = logging.getLogger(__name__)

class InotifyBuffer(BaseThread):
    delay = 0.5

    def __init__(self, path, recursive = False):
        BaseThread.__init__(self)
        self._queue = DelayedQueue(self.delay)
        self._inotify = Inotify(path, recursive)
        self.start()

    def read_event(self):
        return self._queue.get()

    def on_thread_stop(self):
        self._inotify.close()
        self._queue.close()

    def close(self):
        self.stop()
        self.join()

    def run(self):
        while self.should_keep_running():
            inotify_events = self._inotify.read_events()
            for inotify_event in inotify_events:
                logger.debug('in-event %s', inotify_event)
                if inotify_event.is_moved_to:

                    def matching_from_event(event):
                        return not isinstance(event, tuple) and event.is_moved_from and event.cookie == inotify_event.cookie

                    from_event = self._queue.remove(matching_from_event)
                    if from_event is not None:
                        self._queue.put((from_event, inotify_event))
                    else:
                        logger.debug('could not find matching move_from event')
                        self._queue.put(inotify_event)
                else:
                    self._queue.put(inotify_event)
