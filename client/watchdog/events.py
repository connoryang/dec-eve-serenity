#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\events.py
import os.path
import logging
import re
from pathtools.patterns import match_any_paths
from watchdog.utils import has_attribute
from watchdog.utils import unicode_paths
EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'

class FileSystemEvent(object):
    event_type = None
    is_directory = False

    def __init__(self, src_path):
        self._src_path = src_path

    @property
    def src_path(self):
        return self._src_path

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%(class_name)s: event_type=%(event_type)s, src_path=%(src_path)r, is_directory=%(is_directory)s>' % dict(class_name=self.__class__.__name__, event_type=self.event_type, src_path=self.src_path, is_directory=self.is_directory)

    @property
    def key(self):
        return (self.event_type, self.src_path, self.is_directory)

    def __eq__(self, event):
        return self.key == event.key

    def __ne__(self, event):
        return self.key != event.key

    def __hash__(self):
        return hash(self.key)


class FileSystemMovedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MOVED

    def __init__(self, src_path, dest_path):
        super(FileSystemMovedEvent, self).__init__(src_path)
        self._dest_path = dest_path

    @property
    def dest_path(self):
        return self._dest_path

    @property
    def key(self):
        return (self.event_type,
         self.src_path,
         self.dest_path,
         self.is_directory)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r, dest_path=%(dest_path)r, is_directory=%(is_directory)s>' % dict(class_name=self.__class__.__name__, src_path=self.src_path, dest_path=self.dest_path, is_directory=self.is_directory)


class FileDeletedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_DELETED

    def __init__(self, src_path):
        super(FileDeletedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class FileModifiedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MODIFIED

    def __init__(self, src_path):
        super(FileModifiedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class FileCreatedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_CREATED

    def __init__(self, src_path):
        super(FileCreatedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class FileMovedEvent(FileSystemMovedEvent):

    def __init__(self, src_path, dest_path):
        super(FileMovedEvent, self).__init__(src_path, dest_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r, dest_path=%(dest_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path, dest_path=self.dest_path)


class DirDeletedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_DELETED
    is_directory = True

    def __init__(self, src_path):
        super(DirDeletedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class DirModifiedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_MODIFIED
    is_directory = True

    def __init__(self, src_path):
        super(DirModifiedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class DirCreatedEvent(FileSystemEvent):
    event_type = EVENT_TYPE_CREATED
    is_directory = True

    def __init__(self, src_path):
        super(DirCreatedEvent, self).__init__(src_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path)


class DirMovedEvent(FileSystemMovedEvent):
    is_directory = True

    def __init__(self, src_path, dest_path):
        super(DirMovedEvent, self).__init__(src_path, dest_path)

    def __repr__(self):
        return '<%(class_name)s: src_path=%(src_path)r, dest_path=%(dest_path)r>' % dict(class_name=self.__class__.__name__, src_path=self.src_path, dest_path=self.dest_path)


class FileSystemEventHandler(object):

    def dispatch(self, event):
        self.on_any_event(event)
        _method_map = {EVENT_TYPE_MODIFIED: self.on_modified,
         EVENT_TYPE_MOVED: self.on_moved,
         EVENT_TYPE_CREATED: self.on_created,
         EVENT_TYPE_DELETED: self.on_deleted}
        event_type = event.event_type
        _method_map[event_type](event)

    def on_any_event(self, event):
        pass

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        pass


class PatternMatchingEventHandler(FileSystemEventHandler):

    def __init__(self, patterns = None, ignore_patterns = None, ignore_directories = False, case_sensitive = False):
        super(PatternMatchingEventHandler, self).__init__()
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive

    @property
    def patterns(self):
        return self._patterns

    @property
    def ignore_patterns(self):
        return self._ignore_patterns

    @property
    def ignore_directories(self):
        return self._ignore_directories

    @property
    def case_sensitive(self):
        return self._case_sensitive

    def dispatch(self, event):
        if self.ignore_directories and event.is_directory:
            return
        paths = []
        if has_attribute(event, 'dest_path'):
            paths.append(unicode_paths.decode(event.dest_path))
        if event.src_path:
            paths.append(unicode_paths.decode(event.src_path))
        if match_any_paths(paths, included_patterns=self.patterns, excluded_patterns=self.ignore_patterns, case_sensitive=self.case_sensitive):
            self.on_any_event(event)
            _method_map = {EVENT_TYPE_MODIFIED: self.on_modified,
             EVENT_TYPE_MOVED: self.on_moved,
             EVENT_TYPE_CREATED: self.on_created,
             EVENT_TYPE_DELETED: self.on_deleted}
            event_type = event.event_type
            _method_map[event_type](event)


class RegexMatchingEventHandler(FileSystemEventHandler):

    def __init__(self, regexes = ['.*'], ignore_regexes = [], ignore_directories = False, case_sensitive = False):
        super(RegexMatchingEventHandler, self).__init__()
        if case_sensitive:
            self._regexes = [ re.compile(r) for r in regexes ]
            self._ignore_regexes = [ re.compile(r) for r in ignore_regexes ]
        else:
            self._regexes = [ re.compile(r, re.I) for r in regexes ]
            self._ignore_regexes = [ re.compile(r, re.I) for r in ignore_regexes ]
        self._ignore_directories = ignore_directories
        self._case_sensitive = case_sensitive

    @property
    def regexes(self):
        return self._regexes

    @property
    def ignore_regexes(self):
        return self._ignore_regexes

    @property
    def ignore_directories(self):
        return self._ignore_directories

    @property
    def case_sensitive(self):
        return self._case_sensitive

    def dispatch(self, event):
        if self.ignore_directories and event.is_directory:
            return
        paths = []
        if has_attribute(event, 'dest_path'):
            paths.append(unicode_paths.decode(event.dest_path))
        if event.src_path:
            paths.append(unicode_paths.decode(event.src_path))
        if any((r.match(p) for r in self.ignore_regexes for p in paths)):
            return
        if any((r.match(p) for r in self.regexes for p in paths)):
            self.on_any_event(event)
            _method_map = {EVENT_TYPE_MODIFIED: self.on_modified,
             EVENT_TYPE_MOVED: self.on_moved,
             EVENT_TYPE_CREATED: self.on_created,
             EVENT_TYPE_DELETED: self.on_deleted}
            event_type = event.event_type
            _method_map[event_type](event)


class LoggingEventHandler(FileSystemEventHandler):

    def on_moved(self, event):
        super(LoggingEventHandler, self).on_moved(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info('Moved %s: from %s to %s', what, event.src_path, event.dest_path)

    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info('Created %s: %s', what, event.src_path)

    def on_deleted(self, event):
        super(LoggingEventHandler, self).on_deleted(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info('Deleted %s: %s', what, event.src_path)

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        what = 'directory' if event.is_directory else 'file'
        logging.info('Modified %s: %s', what, event.src_path)


class LoggingFileSystemEventHandler(LoggingEventHandler):
    pass


def generate_sub_moved_events(src_dir_path, dest_dir_path):
    for root, directories, filenames in os.walk(dest_dir_path):
        for directory in directories:
            full_path = os.path.join(root, directory)
            renamed_path = full_path.replace(dest_dir_path, src_dir_path) if src_dir_path else None
            yield DirMovedEvent(renamed_path, full_path)

        for filename in filenames:
            full_path = os.path.join(root, filename)
            renamed_path = full_path.replace(dest_dir_path, src_dir_path) if src_dir_path else None
            yield FileMovedEvent(renamed_path, full_path)


def generate_sub_created_events(src_dir_path):
    for root, directories, filenames in os.walk(src_dir_path):
        for directory in directories:
            yield DirCreatedEvent(os.path.join(root, directory))

        for filename in filenames:
            yield FileCreatedEvent(os.path.join(root, filename))
