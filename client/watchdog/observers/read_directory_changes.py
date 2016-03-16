#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\observers\read_directory_changes.py
from __future__ import with_statement
import ctypes
import threading
import os.path
import time
from watchdog.events import DirCreatedEvent, DirDeletedEvent, DirMovedEvent, DirModifiedEvent, FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent, generate_sub_moved_events, generate_sub_created_events
from watchdog.observers.api import EventEmitter, BaseObserver, DEFAULT_OBSERVER_TIMEOUT, DEFAULT_EMITTER_TIMEOUT
from watchdog.observers.winapi import read_events, get_directory_handle, close_directory_handle
WATCHDOG_TRAVERSE_MOVED_DIR_DELAY = 1

class WindowsApiEmitter(EventEmitter):

    def __init__(self, event_queue, watch, timeout = DEFAULT_EMITTER_TIMEOUT):
        EventEmitter.__init__(self, event_queue, watch, timeout)
        self._lock = threading.Lock()
        self._handle = None

    def on_thread_start(self):
        self._handle = get_directory_handle(self.watch.path)

    def on_thread_stop(self):
        if self._handle:
            close_directory_handle(self._handle)

    def queue_events(self, timeout):
        winapi_events = read_events(self._handle, self.watch.is_recursive)
        with self._lock:
            last_renamed_src_path = ''
            for winapi_event in winapi_events:
                src_path = os.path.join(self.watch.path, winapi_event.src_path)
                if winapi_event.is_renamed_old:
                    last_renamed_src_path = src_path
                elif winapi_event.is_renamed_new:
                    dest_path = src_path
                    src_path = last_renamed_src_path
                    if os.path.isdir(dest_path):
                        event = DirMovedEvent(src_path, dest_path)
                        if self.watch.is_recursive:
                            time.sleep(WATCHDOG_TRAVERSE_MOVED_DIR_DELAY)
                            for sub_moved_event in generate_sub_moved_events(src_path, dest_path):
                                self.queue_event(sub_moved_event)

                        self.queue_event(event)
                    else:
                        self.queue_event(FileMovedEvent(src_path, dest_path))
                elif winapi_event.is_modified:
                    cls = DirModifiedEvent if os.path.isdir(src_path) else FileModifiedEvent
                    self.queue_event(cls(src_path))
                elif winapi_event.is_added:
                    isdir = os.path.isdir(src_path)
                    cls = DirCreatedEvent if isdir else FileCreatedEvent
                    self.queue_event(cls(src_path))
                    if isdir:
                        time.sleep(WATCHDOG_TRAVERSE_MOVED_DIR_DELAY)
                        sub_events = generate_sub_created_events(src_path)
                        for sub_created_event in sub_events:
                            self.queue_event(sub_created_event)

                elif winapi_event.is_removed:
                    self.queue_event(FileDeletedEvent(src_path))


class WindowsApiObserver(BaseObserver):

    def __init__(self, timeout = DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=WindowsApiEmitter, timeout=timeout)
