#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\codereload\spy.py
import inspect
import logging
import os
import sys
import time
import osutils
import signals
import uthread2 as uthread
import win32api
import zipfileutils
from .xreload import xreload
log = logging.getLogger(__name__)

class FolderReloaderSpy(object):

    def __init__(self, waitables, paths, translationPaths = None):
        self.on_file_reloaded = signals.Signal()
        self.on_file_reload_failed = signals.Signal()
        self.runningCheckAt = 0
        self.startedAt = int(time.time())
        self.processed = {}
        self.waitables = waitables
        self.translationPaths = translationPaths or []
        if isinstance(paths, basestring):
            paths = [paths]
        self.handles = {}
        paths = map(os.path.abspath, paths)
        commonprefix = os.path.commonprefix(paths)
        if commonprefix:
            paths = [commonprefix]
        for path in paths:
            if not os.path.exists(path):
                log.warn("SpyFolder: Can't spy on non-existing folder %s" % path)
                continue
            handle = win32api.FindFirstChangeNotification(path, True, win32api.FILE_NOTIFY_CHANGE_LAST_WRITE)
            if handle == win32api.INVALID_HANDLE_VALUE:
                log.warn('SpyFolder: got invalid handle for  %s' % path)
                continue
            waitables.InsertHandle(handle, self)
            self.handles[handle] = path
            log.info('AutoCompiler: Now spying on %s using handle %s.', path, handle)

    def __del__(self):
        for handle in self.handles.keys():
            win32api.FindCloseChangeNotification(handle)

    def on_object_signaled(self, handle, abandoned):
        if abandoned:
            return
        win32api.FindNextChangeNotification(handle)
        self.process_folder(self.handles[handle])

    OnObjectSignaled = on_object_signaled

    def poll_for_changes(self):
        for handle, path in self.handles.items():
            if win32api.WaitForSingleObject(handle):
                win32api.FindNextChangeNotification(handle)
                self.process_folder(path)

    PollForChanges = poll_for_changes

    def reload_file(self, filename):
        filename = os.path.abspath(filename)
        filenameWoExt, extension = os.path.splitext(filename)
        filenameTargets = [filenameWoExt]
        for mapFrom, mapTo in self.translationPaths:
            if filenameWoExt.startswith(mapFrom):
                filenameTargets.append(filenameWoExt.replace(mapFrom, mapTo))

        for mname, module in sys.modules.items():
            if not module or not hasattr(module, '__file__'):
                continue
            try:
                modulefile = os.path.abspath(inspect.getfile(module)).rsplit('.', 1)[0]
            except TypeError:
                continue

            if modulefile in filenameTargets:
                with open(filename) as stream:
                    source = stream.read() + '\n'
                log.info('Compiling %s using source %s', module.__name__, filename)
                code = compile(source, filename, 'exec')
                log.info('Reloading %s', module)
                xreload(module, code)
                self.on_file_reloaded(filename, module)

    ReloadFile = reload_file

    def process_folder(self, path):
        toProcess = []
        filenames = []
        for modulename, moduleinfo in sys.modules.items():
            try:
                filenames.append(moduleinfo.__file__)
            except AttributeError:
                continue
            except ImportError as e:
                log.error('unable to monitor %s due to import error: %s', modulename, str(e))
                continue

        for filename in filenames:
            if not filename.lower().endswith('.py'):
                continue
            try:
                sourceFileDate = osutils.get_modified_time(filename)
            except WindowsError:
                if not zipfileutils.is_inside_zipfile(filename):
                    log.exception('Failed to find %s', filename)
                continue

            lastCompile = self.processed.get(filename, self.startedAt)
            if sourceFileDate > lastCompile:
                toProcess.append(filename)
                self.processed[filename] = sourceFileDate

        if toProcess:
            log.info('Reloading: %s', str(toProcess))
            for sourceFile in toProcess:
                try:
                    tstart = time.clock()
                    self.reload_file(sourceFile)
                    tdiff = time.clock() - tstart
                    log.info('Took %.3fs to reload %s', tdiff, os.path.basename(sourceFile))
                except Exception:
                    log.exception("ReloadFile failed for '%s'.", sourceFile)
                    self.on_file_reload_failed(sourceFile, sys.exc_info())

    ProcessFolder = process_folder


def __reload_update__(old_module_dict):
    log.info('autocompile module got reloaded. old dict keys: %s', old_module_dict.keys())


def spy(paths, delay = 0.5):
    if isinstance(paths, basestring):
        paths = [paths]
    waitables = win32api.Waitables()
    folderspy = FolderReloaderSpy(waitables, paths)
    tasklet = uthread.start_tasklet(_poll_spy, folderspy, delay)
    return (folderspy, tasklet)


def _poll_spy(spyfolder, delay):
    while True:
        spyfolder.waitables.Wait(0)
        uthread.sleep(delay)
