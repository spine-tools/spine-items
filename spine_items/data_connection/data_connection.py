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

"""Module for data connection class."""
import os
import shutil
import logging
from PySide6.QtCore import Slot, Qt, QFileInfo, QModelIndex, QItemSelection, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel, QBrush
from PySide6.QtWidgets import QFileDialog, QGraphicsItem, QFileIconProvider, QInputDialog, QMessageBox
from spine_engine.utils.serialization import deserialize_path, serialize_path
from spinedb_api.helpers import remove_credentials_from_url
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.widgets.custom_qwidgets import ToolBarWidget
from spinetoolbox.helpers import open_url, same_path
from spinetoolbox.config import INVALID_FILENAME_CHARS
from .commands import AddDCReferencesCommand, RemoveDCReferencesCommand, MoveReferenceToData
from .custom_file_system_watcher import CustomFileSystemWatcher
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from .utils import restore_database_references
from ..database_validation import DatabaseConnectionValidator
from ..widgets import UrlSelectorDialog
from ..utils import convert_to_sqlalchemy_url, convert_url_to_safe_string


class _Role:
    """Extra reference model data roles."""

    DATA_FILE_PATH = Qt.ItemDataRole.UserRole + 1
    MISSING = Qt.ItemDataRole.UserRole + 2
    FILE_REFERENCE = Qt.ItemDataRole.UserRole + 3
    DB_URL_REFERENCE = Qt.ItemDataRole.UserRole + 4


_MISSING_ITEM_FOREGROUND = QBrush(Qt.red)


class DataConnection(ProjectItem):
    """Data connection project item."""

    def __init__(self, name, description, x, y, toolbox, project, file_references=None, db_references=None):
        """
        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            file_references (list, optional): a list of file paths
            db_references (list of dict, optional): a list of db urls
        """
        super().__init__(name, description, x, y, project)
        if file_references is None:
            file_references = list()
        if db_references is None:
            db_references = list()
        self._toolbox = toolbox
        self.reference_model = QStandardItemModel()  # References
        self.data_model = QStandardItemModel()  # Paths of project internal files. These are found in DC data directory
        self.file_system_watcher = None
        self.file_references = list(file_references)
        self._file_ref_root = QStandardItem("File paths")
        self._file_ref_root.setFlags(self._file_ref_root.flags() & ~Qt.ItemIsEditable)
        self._db_ref_root = QStandardItem("URLs")
        self._db_ref_root.setFlags(self._file_ref_root.flags() & ~Qt.ItemIsEditable)
        self.file_refs_selected = False
        self.any_refs_selected = False
        self.any_data_selected = False
        self.current_is_file_ref = False
        self.populate_reference_list(db_references)
        self.populate_data_list()
        self._database_validator = DatabaseConnectionValidator()

    def set_up(self):
        super().set_up()
        self.file_system_watcher = CustomFileSystemWatcher(self)
        self.file_system_watcher.add_persistent_file_paths(ref for ref in self.file_references if os.path.exists(ref))
        self._watch_sqlite_file(*self.db_reference_iter())
        self.file_system_watcher.add_persistent_dir_path(self.data_dir)
        self.file_system_watcher.file_removed.connect(self._handle_file_removed)
        self.file_system_watcher.file_renamed.connect(self._handle_file_renamed)
        self.file_system_watcher.file_added.connect(self._handle_file_added)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @property
    def executable_class(self):
        return ExecutableItem

    def db_reference_iter(self):
        """Iterates over database references.

        Yields:
            dict: database URL
        """
        for row in range(self._db_ref_root.rowCount()):
            yield self._db_ref_root.child(row).data(_Role.DB_URL_REFERENCE)

    def has_db_references(self):
        return self._db_ref_root.rowCount() != 0

    @Slot(QItemSelection, QItemSelection)
    def _update_selection_state(self, _selected, _deselected):
        self._do_update_selection_state()

    def _do_update_selection_state(self):
        ref_indexes = self._properties_ui.treeView_dc_references.selectionModel().selectedIndexes()
        data_indexes = self._properties_ui.treeView_dc_data.selectionModel().selectedIndexes()
        self.file_refs_selected = any(ind.parent().row() == 0 for ind in ref_indexes)
        self.any_refs_selected = any(ind.parent().row() in (0, 1) for ind in ref_indexes)
        self.current_is_file_ref = self._properties_ui.treeView_dc_references.currentIndex().parent().row() == 0
        self.any_data_selected = bool(data_indexes)
        self._properties_ui.toolButton_minus.setEnabled(self.any_refs_selected)
        self._properties_ui.toolButton_add.setEnabled(self.file_refs_selected)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.toolButton_minus.clicked] = self.remove_references
        s[self._properties_ui.toolButton_add.clicked] = self.copy_to_project
        s[self._properties_ui.treeView_dc_references.doubleClicked] = self.open_reference
        s[self._properties_ui.treeView_dc_data.doubleClicked] = self.open_data_file
        s[self._properties_ui.treeView_dc_references.files_dropped] = self._add_file_references
        s[self._properties_ui.treeView_dc_data.files_dropped] = self.add_data_files
        s[self.get_icon().files_dropped_on_icon] = self.receive_files_dropped_on_icon
        s[self._properties_ui.treeView_dc_references.del_key_pressed] = lambda b=False: self.remove_references(b)
        s[self._properties_ui.treeView_dc_data.del_key_pressed] = self.remove_files
        s[self._properties_ui.treeView_dc_references.selectionModel().selectionChanged] = self._update_selection_state
        s[self._properties_ui.treeView_dc_data.selectionModel().selectionChanged] = self._update_selection_state
        s[self._properties_ui.action_new_file_reference.triggered] = self.show_add_file_references_dialog
        s[self._properties_ui.action_new_db_reference.triggered] = self.show_add_db_reference_dialog
        return s

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._properties_ui.treeView_dc_references.setModel(self.reference_model)
        self._properties_ui.treeView_dc_data.setModel(self.data_model)
        self._do_update_selection_state()
        self._properties_ui.treeView_dc_references.expandAll()
        file_ref_root_widget = ToolBarWidget("File paths")
        file_ref_root_widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        file_ref_root_widget.tool_bar.addAction(self._properties_ui.action_new_file_reference)
        self._properties_ui.treeView_dc_references.setIndexWidget(
            self.reference_model.indexFromItem(self._file_ref_root), file_ref_root_widget
        )
        db_ref_root_widget = ToolBarWidget("URLs")
        db_ref_root_widget.tool_bar.setToolButtonStyle(Qt.ToolButtonIconOnly)
        db_ref_root_widget.tool_bar.addAction(self._properties_ui.action_new_db_reference)
        self._properties_ui.treeView_dc_references.setIndexWidget(
            self.reference_model.indexFromItem(self._db_ref_root), db_ref_root_widget
        )

    @Slot(QGraphicsItem, list)
    def receive_files_dropped_on_icon(self, icon, file_paths):
        """Called when files are dropped onto a data connection graphics item.
        If the item is this Data Connection's graphics item, add the files to data."""
        if icon == self.get_icon():
            self.add_data_files(file_paths)

    @Slot(list)
    def add_data_files(self, file_paths):
        """Add files to data directory"""
        for file_path in file_paths:
            filename = os.path.split(file_path)[1]
            self._logger.msg.emit(f"Copying file <b>{filename}</b> to <b>{self.name}</b>")
            try:
                shutil.copy(file_path, self.data_dir)
            except OSError:
                self._logger.msg_error.emit("[OSError] Copying failed")

    @Slot(bool)
    def show_add_file_references_dialog(self, _=False):
        """Opens a file browser where user can select files to be added as references for this Data Connection."""
        answer = QFileDialog.getOpenFileNames(self._toolbox, "Add file references", self._project.project_dir, "*.*")
        file_paths = answer[0]
        if not file_paths:  # Cancel button clicked
            return
        self._add_file_references(file_paths)

    @Slot(list)
    def _add_file_references(self, paths):
        """Add multiple file paths to reference list.

        Args:
            paths (list): A list of paths to files
        """
        repeated_paths = []
        new_paths = []
        existing_references = (reference for reference in self.file_references if os.path.isfile(reference))
        for path in paths:
            if not os.path.isfile(path):
                continue
            if any(os.path.samefile(path, ref) for ref in existing_references):
                repeated_paths.append(path)
            else:
                new_paths.append(path)
        repeated_paths = ", ".join(repeated_paths)
        if repeated_paths:
            self._logger.msg_warning.emit(f"Reference to file(s) <b>{repeated_paths}</b> already exists")
        if new_paths:
            self._toolbox.undo_stack.push(AddDCReferencesCommand(self.name, new_paths, [], self._project))

    @Slot(bool)
    def show_add_db_reference_dialog(self, _=False):
        """Opens a dialog where user can select a url to be added as reference for this Data Connection."""
        selector = UrlSelectorDialog(self._toolbox.qsettings(), False, self._toolbox, self._toolbox)
        result = selector.exec()
        if result == UrlSelectorDialog.DialogCode.Rejected:
            return
        url = selector.url_dict()
        if self._has_db_reference(url):
            self._logger.msg_warning.emit(f"Reference to database <b>{url}</b> already exists")
            return
        sa_url = convert_to_sqlalchemy_url(url, self.name, self._logger)
        self._database_validator.validate_url(
            url["dialect"], sa_url, self._log_database_reference_error, success_slot=None
        )
        self._toolbox.undo_stack.push(AddDCReferencesCommand(self.name, [], [url], self._project))

    def _has_db_reference(self, url):
        """Checks if given database URL exists already.

        Ignores usernames and passwords.

        Args:
            url (dict): URL to check

        Returns:
            bool: True if db reference exists, False otherwise
        """
        significant_keys = ("dialect", "host", "port", "database")
        for row in range(self._db_ref_root.rowCount()):
            existing_url = self._db_ref_root.child(row).data(_Role.DB_URL_REFERENCE)
            if all(url[key] == existing_url[key] for key in significant_keys):
                return True
        return False

    @Slot(str, object)
    def _log_database_reference_error(self, error, url):
        """Logs final database validation error messages.

        Args:
            error (str): message
            url (URL): SqlAlchemy URL of the database
        """
        url_text = remove_credentials_from_url(str(url))
        for row in range(self._db_ref_root.rowCount()):
            item = self._db_ref_root.child(row)
            if url_text == item.text():
                self._mark_as_missing(item)
                break
        self._logger.msg_error.emit(f"<b>{self.name}</b>: invalid database URL: {error}")

    def do_add_references(self, file_refs, db_refs):
        """Adds file and databases references to DC and starts watching the files.

        Args:
            file_refs (list of str): file reference paths
            db_refs (list of dict): database reference URLs
        """
        file_refs = [os.path.abspath(ref) for ref in file_refs]
        self.file_references += file_refs
        self.file_system_watcher.add_persistent_file_paths(ref for ref in file_refs if os.path.exists(ref))
        self._append_file_references_to_model(*file_refs)
        self._watch_sqlite_file(*db_refs)
        self._append_db_references_to_model(*db_refs)
        self._check_notifications()
        self._resources_to_successors_changed()

    @Slot(bool)
    def remove_references(self, _=False):
        """Pushes a remove references command to undo stack"""
        indexes = self._properties_ui.treeView_dc_references.selectedIndexes()
        if not indexes:  # Nothing selected
            self._logger.msg.emit("Please select references to remove")
            return
        file_ref_root_index = self.reference_model.indexFromItem(self._file_ref_root)
        db_ref_root_index = self.reference_model.indexFromItem(self._db_ref_root)
        file_references = []
        db_references = []
        for index in indexes:
            parent = index.parent()
            if not parent.isValid():
                continue
            if parent == file_ref_root_index:
                file_references.append(index.data(Qt.ItemDataRole.DisplayRole))
            elif parent == db_ref_root_index:
                db_references.append(index.data(_Role.DB_URL_REFERENCE))
        self._toolbox.undo_stack.push(
            RemoveDCReferencesCommand(self.name, file_references, db_references, self._project)
        )
        self._logger.msg.emit("Selected references removed")

    def do_remove_references(self, file_refs, db_refs):
        """Removes given paths from references.

        Args:
            file_refs (list of str): List of removed file paths.
            db_refs (list of dict): List of removed urls.
        """
        self.file_system_watcher.remove_persistent_file_paths(file_refs)
        self._unwatch_sqlite_file(*db_refs)
        refs_removed = self._remove_file_references(*file_refs)
        refs_removed |= self._remove_db_references(*db_refs)
        if refs_removed:
            self._check_notifications()
            self._resources_to_successors_changed()

    def _remove_file_references(self, *refs):
        result = False
        for k in reversed(range(self._file_ref_root.rowCount())):
            if any(same_path(self._file_ref_root.child(k).text(), ref) for ref in refs):
                self.file_references.pop(k)
                self._file_ref_root.removeRow(k)
                result = True
        return result

    def _remove_db_references(self, *refs):
        result = False
        matches = {convert_url_to_safe_string(url) for url in refs}
        for k in reversed(range(self._db_ref_root.rowCount())):
            if self._db_ref_root.child(k).text() in matches:
                self._db_ref_root.removeRow(k)
                result = True
        return result

    def _remove_data_file(self, path):
        for k in reversed(range(self.data_model.rowCount())):
            data_filepath = self.data_model.item(k).data(_Role.DATA_FILE_PATH)
            if same_path(data_filepath, path):
                self.data_model.removeRow(k)
                return True
        return False

    def _rename_data_file(self, old_path, new_path):
        for k in range(self.data_model.rowCount()):
            item = self.data_model.item(k)
            if same_path(item.data(_Role.DATA_FILE_PATH), old_path):
                item.setText(os.path.basename(new_path))
                item.setData(new_path, _Role.DATA_FILE_PATH)
                return True
        return False

    def copy_local_data(self, item_dict):
        """See base class."""
        original_data_dir = item_dict.get("original_data_dir")  # (str) original dir of duplicated ProjectItem
        duplicate_files = item_dict.get("duplicate_files")  # (bool) Flag indicating if linked files should be copied
        if not original_data_dir and not duplicate_files:
            return
        if duplicate_files:
            try:
                os.makedirs(self.data_dir, exist_ok=True)  # Make data dir
            except OSError as e:
                self._logger.msg_error.emit(f"Creating directory {self.data_dir} failed. {e}.")
                return
            for f in os.listdir(original_data_dir):
                src_file = os.path.join(original_data_dir, f)
                if os.path.isfile(src_file):
                    dst_file = os.path.join(self.data_dir, f)
                    try:
                        shutil.copy(src_file, dst_file)  # Copy file
                    except OSError as e:
                        self._logger.msg_error.emit(f"Copying file <b>{f}</b> to <b>{self.data_dir}</b> failed. [{e}]")
                        continue
                    self._logger.msg.emit(f"File <b>{f}</b> copied to <b>{self.data_dir}</b>")
        self.populate_data_list()

    @Slot(str)
    def _handle_file_removed(self, path):
        """Marks file reference missing or removes data reference.

        Args:
            path (str): file path
        """
        resources_changed = self._try_to_mark_file_reference_missing(path) or self._remove_data_file(path)
        if resources_changed:
            self._check_notifications()
            self._resources_to_successors_changed()

    def _try_to_mark_file_reference_missing(self, path):
        """Marks a file reference as missing if given path is in references.

        Args:
            path (str): file path

        Returns:
            bool: True if references was marked missing successfully, False otherwise
        """
        for row in range(self._file_ref_root.rowCount()):
            item = self._file_ref_root.child(row)
            if same_path(item.text(), path):
                self._mark_as_missing(item)
                return True
        for row in range(self._db_ref_root.rowCount()):
            item = self._db_ref_root.child(row)
            url = item.data(_Role.DB_URL_REFERENCE)
            if url["dialect"] != "sqlite":
                continue
            if same_path(url["database"], path):
                self._mark_as_missing(item)
                return True
        return False

    @Slot(str, str)
    def _handle_file_renamed(self, old_path, new_path):
        """Marks file reference missing or renames data file.

        Args:
            old_path (str): original path
            new_path (str): renamed path
        """

        def replace_new_path(paths):
            for i, path in enumerate(paths):
                if path == new_path:
                    paths[i] = old_path
                    return True
            return False

        if self._try_to_mark_file_reference_missing(old_path):
            self._refresh_file_reference_delayed(old_path)
            self._check_notifications()
            self._resources_to_successors_changed()
            return
        if not self._rename_data_file(old_path, new_path):
            return
        self._check_notifications()
        file_refs = list(self.file_references)
        data_files = [os.path.join(self.data_dir, f) for f in self.data_files()]
        new_resources = scan_for_resources(
            self, file_refs + data_files, list(self.db_reference_iter()), self._project.project_dir
        )
        if not replace_new_path(file_refs):
            replace_new_path(data_files)
        old_resources = scan_for_resources(
            self, file_refs + data_files, list(self.db_reference_iter()), self._project.project_dir
        )
        self._resources_to_successors_replaced(old_resources, new_resources)

    def _refresh_file_reference_delayed(self, path):
        """Checks if given file exists after certain delay.

        Args:
            path (str): file path
        """

        # Some software saves files by renaming them and then creating
        # a new file with the same name for safety reasons.
        # So, sometimes a file goes "missing" for a moment and then comes back.
        # We'll try to refresh the file reference a couple times in this case.
        def refresh(retry_count):
            if not os.path.exists(path):
                if retry_count < 5:
                    QTimer.singleShot(1000, lambda: refresh(retry_count + 1))
                return
            fixed_references = []
            for row in range(self._file_ref_root.rowCount()):
                item = self._file_ref_root.child(row, 0)
                if not same_path(path, item.text()):
                    continue
                fixed_references.append(path)
                self._mark_as_found(item)
            if not fixed_references:
                return
            self.file_system_watcher.add_persistent_file_paths(ref for ref in fixed_references)
            self._check_notifications()
            self._resources_to_successors_changed()

        QTimer.singleShot(1000, lambda: refresh(0))

    @Slot(str)
    def _handle_file_added(self, path):
        if same_path(os.path.dirname(path), self.data_dir):
            self._append_data_files_to_model(path)
            self._check_notifications()
            self._resources_to_successors_changed()

    @Slot(bool)
    def copy_to_project(self, _=False):
        """Copy selected file references to this Data Connection's data directory."""
        selected_indexes = self._properties_ui.treeView_dc_references.selectedIndexes()
        if not selected_indexes:
            self._logger.msg_warning.emit("No files to copy")
            return
        self._toolbox.undo_stack.push(
            MoveReferenceToData(self.name, [index.data() for index in selected_indexes], self._project)
        )

    def do_copy_to_project(self, paths):
        """Copies given files to item's data directory.

        Args:
            paths (Iterable of str): paths to copy
        """
        for path in paths:
            if not os.path.exists(path):
                self._logger.msg_error.emit(f"File <b>{path}</b> does not exist")
                continue
            filename = os.path.basename(path)
            self._logger.msg.emit(f"Copying file <b>{filename}</b> to Data Connection <b>{self.name}</b>")
            try:
                shutil.copy(path, self.data_dir)
            except OSError:
                self._logger.msg_error.emit("[OSError] Copying failed")

    def refresh_references(self):
        """Checks if missing file references have somehow come back to life."""
        selected_indexes = self._properties_ui.treeView_dc_references.selectedIndexes()
        if not selected_indexes:
            return
        for index in selected_indexes:
            item = self.reference_model.itemFromIndex(index)
            if self.reference_model.itemFromIndex(index.parent()) is self._db_ref_root:
                self.refresh_db_references(item)
            else:
                self.refresh_file_references(item)

    def refresh_file_references(self, item):
        file_path = item.data(Qt.ItemDataRole.DisplayRole)
        if item.data(_Role.MISSING) and os.path.exists(file_path):
            self._mark_as_found(item)
        else:
            return
        self.file_system_watcher.add_persistent_file_path(file_path)
        self._check_notifications()
        self._resources_to_successors_changed()

    def refresh_db_references(self, item):
        """Checks if the db reference is valid"""
        url = item.data(_Role.DB_URL_REFERENCE)
        self._database_validator.validate_url(
            url["dialect"],
            convert_to_sqlalchemy_url(url),
            self._log_database_reference_error,
            success_slot=self._revive_db_reference,
        )

    @Slot(object)
    def _revive_db_reference(self, url):
        """Colors the db reference back to black.

        Args:
            url (URL): SqlAlchemy URL
        """
        url_text = remove_credentials_from_url(str(url))
        for row in range(self._db_ref_root.rowCount()):
            item = self._db_ref_root.child(row)
            if url_text == item.text():
                self._mark_as_found(item)
                url_dict = item.data(_Role.DB_URL_REFERENCE)
                if url_dict["dialect"] == "sqlite":
                    self.file_system_watcher.add_persistent_file_path(url_dict["database"])
                break
        else:
            return
        self._check_notifications()
        self._resources_to_successors_changed()

    @Slot(QModelIndex)
    def open_reference(self, index):
        """Open reference in default program."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        parent_item = self.reference_model.itemFromIndex(index.parent())
        if parent_item is not self._file_ref_root:
            return
        reference = self.file_references[index.row()]
        url = "file:///" + reference
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Failed to open reference:<b>{reference}</b>")

    @Slot(QModelIndex)
    def open_data_file(self, index):
        """Open data file in default program."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        data_file = index.data(_Role.DATA_FILE_PATH)
        url = "file:///" + data_file
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Opening file <b>{data_file}</b> failed")

    def make_new_file(self):
        """Create a new blank file to this Data Connections data directory."""
        msg = "File name"
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QInputDialog.getText(
            self._toolbox, "Create new file", msg, flags=Qt.WindowTitleHint | Qt.WindowCloseButtonHint
        )
        file_name = answer[0]
        if not file_name.strip():
            return
        # Check that file name has no invalid chars
        if any(True for x in file_name if x in INVALID_FILENAME_CHARS):
            msg = f"File name <b>{file_name}</b> contains invalid characters."
            self._logger.information_box.emit("Creating file failed", msg)
            return
        file_path = os.path.join(self.data_dir, file_name)
        if os.path.exists(file_path):
            msg = f"File <b>{file_name}</b> already exists."
            self._logger.information_box.emit("Creating file failed", msg)
            return
        try:
            with open(file_path, "w"):
                self._logger.msg.emit(f"File <b>{file_name}</b> created to Data Connection <b>{self.name}</b>")
        except OSError:
            msg = "Please check directory permissions."
            self._logger.information_box.emit("Creating file failed", msg)

    @Slot()
    def remove_files(self):
        """Remove selected files from data directory."""
        indexes = self._properties_ui.treeView_dc_data.selectedIndexes()
        if not indexes:  # Nothing selected
            self._logger.msg.emit("Please select files to remove")
            return
        file_list = [index.data() for index in indexes]
        files = "\n".join(file_list)
        msg = "The following files will be removed permanently from the project\n\n" f"{files}\n\n" "Are you sure?"
        title = f"Remove {len(file_list)} File(s)"
        message_box = QMessageBox(
            QMessageBox.Icon.Question,
            title,
            msg,
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            parent=self._toolbox,
        )
        message_box.button(QMessageBox.StandardButton.Ok).setText("Remove Files")
        answer = message_box.exec()
        if answer == QMessageBox.StandardButton.Cancel:
            return
        self.delete_files_from_project(file_list)

    def delete_files_from_project(self, file_names):
        """Deletes given files from item's data directory.

        Args:
            file_names (Iterable of str): files to delete
        """
        for filename in file_names:
            path_to_remove = os.path.join(self.data_dir, filename)
            try:
                os.remove(path_to_remove)
                self._logger.msg.emit(f"File <b>{path_to_remove}</b> removed")
            except OSError:
                self._logger.msg_error.emit(f"Removing file {path_to_remove} failed.\nCheck permissions.")

    def populate_reference_list(self, db_references):
        """List references in QTreeView.

        Args:
            db_references (list of dict): database URLs
        """
        self.reference_model.clear()
        self.reference_model.setHorizontalHeaderItem(0, QStandardItem("References"))  # Add header
        self._file_ref_root.removeRows(0, self._file_ref_root.rowCount())
        self.reference_model.appendRow(self._file_ref_root)
        self._db_ref_root.removeRows(0, self._db_ref_root.rowCount())
        self.reference_model.appendRow(self._db_ref_root)
        self._append_file_references_to_model(*self.file_references)
        self._append_db_references_to_model(*db_references)

    def _append_file_references_to_model(self, *paths):
        non_existent_paths = []
        for path in paths:
            item = QStandardItem(path)
            item.setFlags(~Qt.ItemIsEditable)
            if not os.path.exists(path):
                non_existent_paths.append(path)
                self._mark_as_missing(item)
            self._file_ref_root.appendRow(item)
        if non_existent_paths:
            msg = f"<b>{self.name}:</b> Could not find file references:"
            for path in non_existent_paths:
                msg += f"<br><b>{os.path.basename(path)}</b>"
            self._logger.msg_error.emit(msg)

    @staticmethod
    def _mark_as_missing(item):
        """Modifies given model item to appear as missing reference.

        Args:
            item (QStandardItem): item to modify
        """
        item.setData("The file is missing.", Qt.ItemDataRole.ToolTipRole)
        item.setData(_MISSING_ITEM_FOREGROUND, Qt.ItemDataRole.ForegroundRole)
        item.setData(True, _Role.MISSING)

    @staticmethod
    def _mark_as_found(item):
        """Modifies given model item to appear as existing reference.

        Args:
            item (QStandardItem): item to modify
        """
        item.setData(None, Qt.ItemDataRole.ToolTipRole)
        item.setData(None, Qt.ItemDataRole.ForegroundRole)
        item.setData(False, _Role.MISSING)

    def _append_db_references_to_model(self, *urls):
        """Appends given database URLs to the model.

        Args:
            *urls: dict-style URLs to add
        """
        for url in urls:
            item = QStandardItem(convert_url_to_safe_string(url))
            item.setData(url, _Role.DB_URL_REFERENCE)
            item.setFlags(~Qt.ItemIsEditable)
            self._db_ref_root.appendRow(item)

    def _watch_sqlite_file(self, *urls):
        """Adds sqlite files to file system watcher's watched paths.

        Args:
            *urls: dict-style URLs to watch
        """
        for url in urls:
            if url["dialect"] == "sqlite":
                path = url["database"]
                if os.path.exists(path):
                    self.file_system_watcher.add_persistent_file_path(path)

    def _unwatch_sqlite_file(self, *urls):
        """Removes sqlite files from file system watcher's watched paths.

        Args:
            *urls: dict-style URLs to watch

        Returns:
            list of str: list of removed paths
        """
        paths = []
        for url in urls:
            if url["dialect"] == "sqlite":
                path = url["database"]
                if os.path.exists(path):
                    paths.append(path)
        return self.file_system_watcher.remove_persistent_file_paths(paths)

    def populate_data_list(self):
        """List project internal data (files) in QTreeView."""
        self.data_model.clear()
        self.data_model.setHorizontalHeaderItem(0, QStandardItem("Data"))  # Add header
        self._append_data_files_to_model(*self.data_files())

    def _append_data_files_to_model(self, *paths):
        for path in paths:
            item = QStandardItem(os.path.basename(path))
            item.setFlags(~Qt.ItemIsEditable)
            icon = QFileIconProvider().icon(QFileInfo(path))
            item.setData(icon, Qt.ItemDataRole.DecorationRole)
            item.setData(path, _Role.DATA_FILE_PATH)
            self.data_model.appendRow(item)

    def resources_for_direct_successors(self):
        """see base class"""
        data_files = [os.path.join(self.data_dir, f) for f in self.data_files()]
        resources = scan_for_resources(
            self, self.file_references + data_files, list(self.db_reference_iter()), self._project.project_dir
        )
        return resources

    def _check_notifications(self):
        """Sets or clears the exclamation mark icon."""
        self.clear_notifications()
        if not self.file_references and not self.has_db_references() and not self.data_files():
            self.add_notification(
                "This Data Connection does not have any references or data. "
                "Add some in the Data Connection Properties panel."
            )
        missing_file_references = [ref for ref in self.file_references if not os.path.exists(ref)]
        if missing_file_references:
            self.add_notification("Cannot find some file references. Please, check that the files exist.")

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["file_references"] = [serialize_path(ref, self._project.project_dir) for ref in self.file_references]
        db_references = []
        db_credentials = {}
        for url in self.db_reference_iter():
            serialized_url = dict(url)
            username = serialized_url.pop("username")
            password = serialized_url.pop("password")
            if username:
                db_credentials[convert_url_to_safe_string(serialized_url)] = username, password
            if serialized_url["dialect"] == "sqlite":
                serialized_url["database"] = serialize_path(serialized_url["database"], self._project.project_dir)
            db_references.append(serialized_url)
        d["db_references"] = db_references
        d["db_credentials"] = db_credentials
        return d

    @staticmethod
    def item_dict_local_entries():
        """See base class."""
        return [("db_credentials",)]

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        # FIXME: Do we want to convert references to file_references via upgrade?
        file_references = item_dict.get("file_references", list()) or item_dict.get("references", list())
        file_references = [deserialize_path(r, project.project_dir) for r in file_references]
        db_references = restore_database_references(
            item_dict.get("db_references", []), item_dict.get("db_credentials", {}), project.project_dir
        )
        return DataConnection(name, description, x, y, toolbox, project, file_references, db_references)

    def rename(self, new_name, rename_data_dir_message):
        """See base class."""
        old_data_dir = self.data_dir
        if not super().rename(new_name, rename_data_dir_message):
            return False
        self.file_system_watcher.remove_persistent_dir_path(old_data_dir)
        self.file_system_watcher.add_persistent_dir_path(self.data_dir)
        self.populate_data_list()
        return True

    def tear_down(self):
        """Tears down this item. Called by toolbox just before closing."""
        super().tear_down()
        self.file_system_watcher.tear_down()
        self._database_validator.wait_for_finish()

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Tool":
            self._logger.msg.emit(
                f"Link established. Tool <b>{source_item.name}</b> output files will be "
                f"passed as references to item <b>{self.name}</b> after execution."
            )
        elif source_item.item_type() in ["Data Store", "Importer"]:
            # Does this type of link do anything?
            self._logger.msg.emit("Link established")
        else:
            super().notify_destination(source_item)
