#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsdlite\monitor.py
import os
import logging
try:
    from watchdog.utils import platform
    if platform.is_windows():
        import watchdog.observers.winapi
        import watchdog.observers.read_directory_changes

        def read_events(*args, **kwargs):
            try:
                return watchdog.observers.winapi.read_events(*args, **kwargs)
            except WindowsError:
                return []


        watchdog.observers.read_directory_changes.read_events = read_events
    import atexit
    import weakref
    if platform.is_darwin():
        from watchdog.observers.kqueue import KqueueObserver as Observer
    else:
        from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    observers = weakref.WeakSet()

    class FileHandler(FileSystemEventHandler):

        def __init__(self, callback):
            self.callback = callback

        def on_any_event(self, event):
            if not event.is_directory:
                try:
                    self.callback(event.event_type, event.src_path)
                except Exception:
                    logging.exception('Error handling file monitor event')


    def start_file_monitor(path, callback):
        if os.path.exists(path):
            handler = FileHandler(callback)
            observer = Observer()
            observer.schedule(handler, path, recursive=True)
            observer.start()
            observers.add(observer)
            return observer


    def stop_file_monitor(observer):
        if observer:
            observer.unschedule_all()
            observer.stop()
            observer.join()


    def stop_observers():
        for observer in observers:
            stop_file_monitor(observer)


    atexit.register(stop_observers)
except (ImportError, AttributeError):

    def start_file_monitor(path, callback):
        return None


    def stop_file_monitor(observer):
        pass
