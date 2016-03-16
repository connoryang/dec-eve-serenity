#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\observers\kqueue.py
from __future__ import with_statement
from watchdog.utils import platform
import threading
import errno
import sys
import stat
import os
if sys.version_info < (2, 7, 0):
    import select_backport as select
else:
    import select
from pathtools.path import absolute_path
from watchdog.observers.api import BaseObserver, EventEmitter, DEFAULT_OBSERVER_TIMEOUT, DEFAULT_EMITTER_TIMEOUT
from watchdog.utils.dirsnapshot import DirectorySnapshot
from watchdog.events import DirMovedEvent, DirDeletedEvent, DirCreatedEvent, DirModifiedEvent, FileMovedEvent, FileDeletedEvent, FileCreatedEvent, FileModifiedEvent, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED
MAX_EVENTS = 4096
O_EVTONLY = 32768
if platform.is_darwin():
    WATCHDOG_OS_OPEN_FLAGS = O_EVTONLY
else:
    WATCHDOG_OS_OPEN_FLAGS = os.O_RDONLY | os.O_NONBLOCK
WATCHDOG_KQ_FILTER = select.KQ_FILTER_VNODE
WATCHDOG_KQ_EV_FLAGS = select.KQ_EV_ADD | select.KQ_EV_ENABLE | select.KQ_EV_CLEAR
WATCHDOG_KQ_FFLAGS = select.KQ_NOTE_DELETE | select.KQ_NOTE_WRITE | select.KQ_NOTE_EXTEND | select.KQ_NOTE_ATTRIB | select.KQ_NOTE_LINK | select.KQ_NOTE_RENAME | select.KQ_NOTE_REVOKE

def is_deleted(kev):
    return kev.fflags & select.KQ_NOTE_DELETE


def is_modified(kev):
    fflags = kev.fflags
    return fflags & select.KQ_NOTE_EXTEND or fflags & select.KQ_NOTE_WRITE


def is_attrib_modified(kev):
    return kev.fflags & select.KQ_NOTE_ATTRIB


def is_renamed(kev):
    return kev.fflags & select.KQ_NOTE_RENAME


class KeventDescriptorSet(object):

    def __init__(self):
        self._descriptors = set()
        self._descriptor_for_path = dict()
        self._descriptor_for_fd = dict()
        self._kevents = list()
        self._lock = threading.Lock()

    @property
    def kevents(self):
        with self._lock:
            return self._kevents

    @property
    def paths(self):
        with self._lock:
            return list(self._descriptor_for_path.keys())

    def get_for_fd(self, fd):
        with self._lock:
            return self._descriptor_for_fd[fd]

    def get(self, path):
        with self._lock:
            path = absolute_path(path)
            return self._get(path)

    def __contains__(self, path):
        with self._lock:
            path = absolute_path(path)
            return self._has_path(path)

    def add(self, path, is_directory):
        with self._lock:
            path = absolute_path(path)
            if not self._has_path(path):
                self._add_descriptor(KeventDescriptor(path, is_directory))

    def remove(self, path):
        with self._lock:
            path = absolute_path(path)
            if self._has_path(path):
                self._remove_descriptor(self._get(path))

    def clear(self):
        with self._lock:
            for descriptor in self._descriptors:
                descriptor.close()

            self._descriptors.clear()
            self._descriptor_for_fd.clear()
            self._descriptor_for_path.clear()
            self._kevents = []

    def _get(self, path):
        return self._descriptor_for_path[path]

    def _has_path(self, path):
        return path in self._descriptor_for_path

    def _add_descriptor(self, descriptor):
        self._descriptors.add(descriptor)
        self._kevents.append(descriptor.kevent)
        self._descriptor_for_path[descriptor.path] = descriptor
        self._descriptor_for_fd[descriptor.fd] = descriptor

    def _remove_descriptor(self, descriptor):
        self._descriptors.remove(descriptor)
        del self._descriptor_for_fd[descriptor.fd]
        del self._descriptor_for_path[descriptor.path]
        self._kevents.remove(descriptor.kevent)
        descriptor.close()


class KeventDescriptor(object):

    def __init__(self, path, is_directory):
        self._path = absolute_path(path)
        self._is_directory = is_directory
        self._fd = os.open(path, WATCHDOG_OS_OPEN_FLAGS)
        self._kev = select.kevent(self._fd, filter=WATCHDOG_KQ_FILTER, flags=WATCHDOG_KQ_EV_FLAGS, fflags=WATCHDOG_KQ_FFLAGS)

    @property
    def fd(self):
        return self._fd

    @property
    def path(self):
        return self._path

    @property
    def kevent(self):
        return self._kev

    @property
    def is_directory(self):
        return self._is_directory

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass

    @property
    def key(self):
        return (self.path, self.is_directory)

    def __eq__(self, descriptor):
        return self.key == descriptor.key

    def __ne__(self, descriptor):
        return self.key != descriptor.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        return '<KeventDescriptor: path=%s, is_directory=%s>' % (self.path, self.is_directory)


class KqueueEmitter(EventEmitter):

    def __init__(self, event_queue, watch, timeout = DEFAULT_EMITTER_TIMEOUT):
        EventEmitter.__init__(self, event_queue, watch, timeout)
        self._kq = select.kqueue()
        self._lock = threading.RLock()
        self._descriptors = KeventDescriptorSet()

        def walker_callback(path, stat_info, self = self):
            self._register_kevent(path, stat.S_ISDIR(stat_info.st_mode))

        self._snapshot = DirectorySnapshot(watch.path, watch.is_recursive, walker_callback)

    def _register_kevent(self, path, is_directory):
        try:
            self._descriptors.add(path, is_directory)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

    def _unregister_kevent(self, path):
        self._descriptors.remove(path)

    def queue_event(self, event):
        EventEmitter.queue_event(self, event)
        if event.event_type == EVENT_TYPE_CREATED:
            self._register_kevent(event.src_path, event.is_directory)
        elif event.event_type == EVENT_TYPE_MOVED:
            self._unregister_kevent(event.src_path)
            self._register_kevent(event.dest_path, event.is_directory)
        elif event.event_type == EVENT_TYPE_DELETED:
            self._unregister_kevent(event.src_path)

    def _queue_dirs_modified(self, dirs_modified, ref_snapshot, new_snapshot):
        if dirs_modified:
            for dir_modified in dirs_modified:
                self.queue_event(DirModifiedEvent(dir_modified))

            diff_events = new_snapshot - ref_snapshot
            for file_created in diff_events.files_created:
                self.queue_event(FileCreatedEvent(file_created))

            for directory_created in diff_events.dirs_created:
                self.queue_event(DirCreatedEvent(directory_created))

    def _queue_events_except_renames_and_dir_modifications(self, event_list):
        files_renamed = set()
        dirs_renamed = set()
        dirs_modified = set()
        for kev in event_list:
            descriptor = self._descriptors.get_for_fd(kev.ident)
            src_path = descriptor.path
            if is_deleted(kev):
                if descriptor.is_directory:
                    self.queue_event(DirDeletedEvent(src_path))
                else:
                    self.queue_event(FileDeletedEvent(src_path))
            elif is_attrib_modified(kev):
                if descriptor.is_directory:
                    self.queue_event(DirModifiedEvent(src_path))
                else:
                    self.queue_event(FileModifiedEvent(src_path))
            elif is_modified(kev):
                if descriptor.is_directory:
                    dirs_modified.add(src_path)
                else:
                    self.queue_event(FileModifiedEvent(src_path))
            elif is_renamed(kev):
                if descriptor.is_directory:
                    dirs_renamed.add(src_path)
                else:
                    files_renamed.add(src_path)

        return (files_renamed, dirs_renamed, dirs_modified)

    def _queue_renamed(self, src_path, is_directory, ref_snapshot, new_snapshot):
        try:
            ref_stat_info = ref_snapshot.stat_info(src_path)
        except KeyError:
            if is_directory:
                self.queue_event(DirCreatedEvent(src_path))
                self.queue_event(DirDeletedEvent(src_path))
            else:
                self.queue_event(FileCreatedEvent(src_path))
                self.queue_event(FileDeletedEvent(src_path))
            return

        try:
            dest_path = absolute_path(new_snapshot.path_for_inode(ref_stat_info.st_ino))
            if is_directory:
                event = DirMovedEvent(src_path, dest_path)
                if self.watch.is_recursive:
                    for sub_event in event.sub_moved_events():
                        self.queue_event(sub_event)

                self.queue_event(event)
            else:
                self.queue_event(FileMovedEvent(src_path, dest_path))
        except KeyError:
            if is_directory:
                self.queue_event(DirDeletedEvent(src_path))
            else:
                self.queue_event(FileDeletedEvent(src_path))

    def _read_events(self, timeout = None):
        return self._kq.control(self._descriptors.kevents, MAX_EVENTS, timeout)

    def queue_events(self, timeout):
        with self._lock:
            try:
                event_list = self._read_events(timeout)
                files_renamed, dirs_renamed, dirs_modified = self._queue_events_except_renames_and_dir_modifications(event_list)
                new_snapshot = DirectorySnapshot(self.watch.path, self.watch.is_recursive)
                ref_snapshot = self._snapshot
                self._snapshot = new_snapshot
                if files_renamed or dirs_renamed or dirs_modified:
                    for src_path in files_renamed:
                        self._queue_renamed(src_path, False, ref_snapshot, new_snapshot)

                    for src_path in dirs_renamed:
                        self._queue_renamed(src_path, True, ref_snapshot, new_snapshot)

                    self._queue_dirs_modified(dirs_modified, ref_snapshot, new_snapshot)
            except OSError as e:
                if e.errno == errno.EBADF:
                    pass
                else:
                    raise

    def on_thread_stop(self):
        with self._lock:
            self._descriptors.clear()
            self._kq.close()


class KqueueObserver(BaseObserver):

    def __init__(self, timeout = DEFAULT_OBSERVER_TIMEOUT):
        BaseObserver.__init__(self, emitter_class=KqueueEmitter, timeout=timeout)
