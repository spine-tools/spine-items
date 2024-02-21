######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains CustomFileSystemWatcher."""
import os
from PySide6.QtCore import QFileSystemWatcher, Signal, Slot


class CustomFileSystemWatcher(QFileSystemWatcher):
    """A file system watcher that keeps track of renamed files."""

    file_renamed = Signal(str, str)
    file_removed = Signal(str)
    file_added = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._watched_files = {}
        self._watched_dirs = set()
        self._directory_snapshots = {}
        self.directoryChanged.connect(self._handle_dir_changed)

    @Slot(str)
    def _handle_dir_changed(self, dirname):
        """Adds, removes or renames watched files and emits corresponding signals.

        Args:
            dirname (str): path to changed directory
        """
        is_watched_dir = dirname in self._watched_dirs
        watched_files = self._watched_files.setdefault(dirname, set())
        if not is_watched_dir and not watched_files:
            raise RuntimeError("Watching directory that should not be watched.")
        snapshot = self._directory_snapshots[dirname]
        new_snapshot = self._directory_snapshots[dirname] = self._take_snapshot(dirname)
        removed_paths = snapshot - new_snapshot
        added_paths = new_snapshot - snapshot
        for old_path, new_path in zip(list(removed_paths), list(added_paths)):
            # Assume files were renamed.
            # If there was more than one rename, we choose the new name blindly but
            # there doesn't seem to be a better way to do it.
            # Maybe it doesn't even matter? In any case, usually there is just a single rename and nothing else.
            removed_paths.remove(old_path)
            added_paths.remove(new_path)
            if is_watched_dir:
                self.file_renamed.emit(old_path, new_path)
            elif old_path in watched_files:
                watched_files.remove(old_path)
                watched_files.add(new_path)
                self.file_renamed.emit(old_path, new_path)
        for path in removed_paths:
            if is_watched_dir:
                self.file_removed.emit(path)
            elif path in watched_files:
                watched_files.remove(path)
                self.file_removed.emit(path)
        if is_watched_dir:
            for path in added_paths:
                self.file_added.emit(path)
        if not watched_files:
            del self._watched_files[dirname]
            if dirname not in self._watched_dirs:
                self.removePath(dirname)

    def add_persistent_file_path(self, path):
        if not os.path.isfile(path):
            return False
        dirname = os.path.dirname(path)
        self._watched_files.setdefault(dirname, set()).add(path)
        if dirname not in self._directory_snapshots:
            self._directory_snapshots.setdefault(dirname, self._take_snapshot(dirname))
        return self.addPath(dirname)

    def add_persistent_file_paths(self, paths):
        for path in paths:
            self.add_persistent_file_path(path)

    def remove_persistent_file_path(self, path):
        dirname = os.path.dirname(path)
        watched_files = self._watched_files.get(dirname)
        if not watched_files:
            return False
        watched_files.discard(path)
        if watched_files:
            return True
        del self._watched_files[dirname]
        if dirname in self._watched_dirs:
            return True
        del self._directory_snapshots[dirname]
        return self.removePath(dirname)

    def remove_persistent_file_paths(self, paths):
        removed_paths = []
        for path in paths:
            if self.remove_persistent_file_path(path):
                removed_paths.append(path)
        return removed_paths

    def add_persistent_dir_path(self, path):
        if not os.path.isdir(path):
            return False
        self._watched_dirs.add(path)
        self._directory_snapshots.setdefault(path, self._take_snapshot(path))
        return self.addPath(path)

    def remove_persistent_dir_path(self, path):
        self._watched_dirs.discard(path)
        if path in self._watched_files:
            return True
        del self._directory_snapshots[path]
        return self.removePath(path)

    def tear_down(self):
        directories = self.directories()
        if directories:
            self.removePaths(directories)
        self.deleteLater()

    def _take_snapshot(self, dirname):
        return set(self._absfilepaths(dirname))

    @staticmethod
    def _absfilepaths(dirname):
        with os.scandir(dirname) as scan_iterator:
            for entry in scan_iterator:
                if entry.is_file():
                    yield entry.path
