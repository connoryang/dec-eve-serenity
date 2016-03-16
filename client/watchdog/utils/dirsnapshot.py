#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\dirsnapshot.py
import errno
import os
from stat import S_ISDIR
from watchdog.utils import platform
from watchdog.utils import stat as default_stat

class DirectorySnapshotDiff(object):

    def __init__(self, ref, snapshot):
        created = snapshot.paths - ref.paths
        deleted = ref.paths - snapshot.paths
        for path in ref.paths & snapshot.paths:
            if ref.inode(path) != snapshot.inode(path):
                created.add(path)
                deleted.add(path)

        moved = set()
        for path in set(deleted):
            inode = ref.inode(path)
            new_path = snapshot.path(inode)
            if new_path:
                deleted.remove(path)
                moved.add((path, new_path))

        for path in set(created):
            inode = snapshot.inode(path)
            old_path = ref.path(inode)
            if old_path:
                created.remove(path)
                moved.add((old_path, path))

        modified = set()
        for path in ref.paths & snapshot.paths:
            if ref.inode(path) == snapshot.inode(path):
                if ref.mtime(path) != snapshot.mtime(path):
                    modified.add(path)

        for old_path, new_path in moved:
            if ref.mtime(old_path) != snapshot.mtime(new_path):
                modified.add(old_path)

        self._dirs_created = [ path for path in created if snapshot.isdir(path) ]
        self._dirs_deleted = [ path for path in deleted if ref.isdir(path) ]
        self._dirs_modified = [ path for path in modified if ref.isdir(path) ]
        self._dirs_moved = [ (frm, to) for frm, to in moved if ref.isdir(frm) ]
        self._files_created = list(created - set(self._dirs_created))
        self._files_deleted = list(deleted - set(self._dirs_deleted))
        self._files_modified = list(modified - set(self._dirs_modified))
        self._files_moved = list(moved - set(self._dirs_moved))

    @property
    def files_created(self):
        return self._files_created

    @property
    def files_deleted(self):
        return self._files_deleted

    @property
    def files_modified(self):
        return self._files_modified

    @property
    def files_moved(self):
        return self._files_moved

    @property
    def dirs_modified(self):
        return self._dirs_modified

    @property
    def dirs_moved(self):
        return self._dirs_moved

    @property
    def dirs_deleted(self):
        return self._dirs_deleted

    @property
    def dirs_created(self):
        return self._dirs_created


class DirectorySnapshot(object):

    def __init__(self, path, recursive = True, walker_callback = lambda p, s: None, stat = default_stat, listdir = os.listdir):
        self._stat_info = {}
        self._inode_to_path = {}
        st = stat(path)
        self._stat_info[path] = st
        self._inode_to_path[st.st_ino, st.st_dev] = path

        def walk(root):
            try:
                paths = [ os.path.join(root, name) for name in listdir(root) ]
            except OSError as e:
                if e.errno == errno.ENOENT:
                    return
                raise

            entries = []
            for p in paths:
                try:
                    entries.append((p, stat(p)))
                except OSError:
                    continue

            for _ in entries:
                yield _

            if recursive:
                for path, st in entries:
                    if S_ISDIR(st.st_mode):
                        for _ in walk(path):
                            yield _

        for p, st in walk(path):
            i = (st.st_ino, st.st_dev)
            self._inode_to_path[i] = p
            self._stat_info[p] = st
            walker_callback(p, st)

    @property
    def paths(self):
        return set(self._stat_info.keys())

    def path(self, id):
        return self._inode_to_path.get(id)

    def inode(self, path):
        st = self._stat_info[path]
        return (st.st_ino, st.st_dev)

    def isdir(self, path):
        return S_ISDIR(self._stat_info[path].st_mode)

    def mtime(self, path):
        return self._stat_info[path].st_mtime

    def stat_info(self, path):
        return self._stat_info[path]

    def __sub__(self, previous_dirsnap):
        return DirectorySnapshotDiff(previous_dirsnap, self)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str(self._stat_info)
