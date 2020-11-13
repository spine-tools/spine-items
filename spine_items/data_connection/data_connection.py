######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Module for data connection class.

:author: P. Savolainen (VTT)
:date:   19.12.2017
"""

import os
import shutil
import logging
import pathlib
from PySide2.QtCore import Slot, Qt, QFileInfo
from PySide2.QtGui import QStandardItem, QStandardItemModel, QIcon, QPixmap
from PySide2.QtWidgets import QFileDialog, QStyle, QFileIconProvider, QInputDialog, QMessageBox
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.custom_file_system_watcher import CustomFileSystemWatcher
from spinetoolbox.helpers import busy_effect, open_url
from spinetoolbox.config import INVALID_FILENAME_CHARS
from spine_engine.project_item.project_item_resource import ProjectItemResource
from spine_engine.utils.serialization import deserialize_path, serialize_path
from .commands import AddDCReferencesCommand, RemoveDCReferencesCommand
from .executable_item import ExecutableItem
from .item_info import ItemInfo


class DataConnection(ProjectItem):
    def __init__(self, name, description, x, y, toolbox, project, logger, references=None):
        """Data Connection class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            references (list, optional): a list of file paths
        """
        super().__init__(name, description, x, y, project, logger)
        if references is None:
            references = list()
        self._toolbox = toolbox
        self.reference_model = QStandardItemModel()  # References to files
        self.data_model = QStandardItemModel()  # Paths of project internal files. These are found in DC data directory
        self.datapackage_icon = QIcon(QPixmap(":/icons/datapkg.png"))
        self.file_system_watcher = None
        self.references = [ref for ref in references if os.path.isfile(ref)]
        self.populate_reference_list()
        # Populate data (files) model
        self.populate_data_list()
        self.spine_datapackage_form = None
        self._updated_from = {}

    def set_up(self):
        self.file_system_watcher = CustomFileSystemWatcher(self)
        self.file_system_watcher.add_persistent_file_paths(self.references)
        self.file_system_watcher.add_persistent_dir_path(self.data_dir)
        self.file_system_watcher.file_removed.connect(self._handle_file_removed)
        self.file_system_watcher.file_renamed.connect(self._handle_file_renamed)
        self.file_system_watcher.file_added.connect(self._handle_file_added)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    def execution_item(self):
        """Creates DataConnection's execution counterpart."""
        data_files = [os.path.join(self.data_dir, f) for f in self.data_files()]
        return ExecutableItem(self.name, self.file_references(), data_files, self._logger)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        # pylint: disable=unnecessary-lambda
        s[self._properties_ui.toolButton_dc_open_dir.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.toolButton_plus.clicked] = self.show_add_references_dialog
        s[self._properties_ui.toolButton_minus.clicked] = self.remove_references
        s[self._properties_ui.toolButton_add.clicked] = self.copy_to_project
        s[self._properties_ui.pushButton_datapackage.clicked] = self.show_spine_datapackage_form
        s[self._properties_ui.treeView_dc_references.doubleClicked] = self.open_reference
        s[self._properties_ui.treeView_dc_data.doubleClicked] = self.open_data_file
        s[self._properties_ui.treeView_dc_references.files_dropped] = self.add_references
        s[self._properties_ui.treeView_dc_data.files_dropped] = self.add_data_files
        s[self.get_icon().files_dropped_on_icon] = self.receive_files_dropped_on_icon
        s[self._properties_ui.treeView_dc_references.del_key_pressed] = lambda: self.remove_references()
        s[self._properties_ui.treeView_dc_data.del_key_pressed] = lambda: self.remove_files()
        return s

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._properties_ui.label_dc_name.setText(self.name)
        self._properties_ui.treeView_dc_references.setModel(self.reference_model)
        self._properties_ui.treeView_dc_data.setModel(self.data_model)

    @Slot("QGraphicsItem", list)
    def receive_files_dropped_on_icon(self, icon, file_paths):
        """Called when files are dropped onto a data connection graphics item.
        If the item is this Data Connection's graphics item, add the files to data."""
        if icon == self.get_icon():
            self.add_data_files(file_paths)

    @Slot("QVariant")
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
    def show_add_references_dialog(self, checked=False):
        """Opens a file browser where user can select the files to be
        added as references for this Data Connection."""
        # noinspection PyCallByClass, PyTypeChecker, PyArgumentList
        answer = QFileDialog.getOpenFileNames(self._toolbox, "Add file references", self._project.project_dir, "*.*")
        file_paths = answer[0]
        if not file_paths:  # Cancel button clicked
            return
        self.add_references(file_paths)

    @Slot("QVariant")
    def add_references(self, paths):
        """Add multiple file paths to reference list.

        Args:
            paths (list): A list of paths to files
        """
        repeated_paths = []
        new_paths = []
        for path in paths:
            if not os.path.isfile(path):
                continue
            if any(os.path.samefile(path, ref) for ref in self.references):
                repeated_paths.append(path)
            else:
                new_paths.append(path)
        repeated_paths = ", ".join(repeated_paths)
        if repeated_paths:
            self._logger.msg_warning.emit(f"Reference to file(s) <b>{repeated_paths}</b> already available")
        if new_paths:
            self._toolbox.undo_stack.push(AddDCReferencesCommand(self, new_paths))

    def do_add_references(self, paths):
        paths = [os.path.abspath(path) for path in paths]
        self.references += paths
        self.file_system_watcher.add_persistent_file_paths(paths)
        self._append_references_to_model(*paths)

    @Slot(bool)
    def remove_references(self, checked=False):
        """Pushes a remove references command to undo stack"""
        indexes = self._properties_ui.treeView_dc_references.selectedIndexes()
        if not indexes:  # Nothing selected
            self._logger.msg.emit("Please select references to remove")
            return
        references = [ind.data(Qt.DisplayRole) for ind in indexes]
        self._toolbox.undo_stack.push(RemoveDCReferencesCommand(self, references))
        self._logger.msg.emit("Selected references removed")

    def do_remove_references(self, paths):
        """Removes given paths from references.

        Args:
            paths (list): List of removed paths.
        """
        self.file_system_watcher.remove_persistent_file_paths(paths)
        if self._remove_references(*paths):
            self.item_changed.emit()

    def _remove_references(self, *paths):
        result = False
        for k in reversed(range(self.reference_model.rowCount())):
            ref = self.reference_model.item(k).text()
            if any(_samepath(ref, path) for path in paths):
                self.references.pop(k)
                self.reference_model.removeRow(k)
                result = True
        return result

    def _rename_reference(self, old_path, new_path):
        for k in range(self.reference_model.rowCount()):
            item = self.reference_model.item(k)
            if _samepath(item.text(), old_path):
                item.setText(new_path)
                self.references[k] = new_path
                return True

    def _remove_data_file(self, path):
        for k in reversed(range(self.data_model.rowCount())):
            data_filepath = self.data_model.item(k).text()
            if _samepath(data_filepath, path):
                self.data_model.removeRow(k)
                return True

    def _rename_data_file(self, old_path, new_path):
        for k in range(self.data_model.rowCount()):
            item = self.data_model.item(k)
            if _samepath(item.text(), old_path):
                item.setText(new_path)
                return True

    @Slot(str)
    def _handle_file_removed(self, path):
        if self._remove_references(path) or self._remove_data_file(path):
            self.item_changed.emit()

    @Slot(str, str)
    def _handle_file_renamed(self, old_path, new_path):
        if self._rename_reference(old_path, new_path) or self._rename_data_file(old_path, new_path):
            self._updated_from[new_path] = old_path
            self.item_changed.emit()

    @Slot(str)
    def _handle_file_added(self, path):
        if _samepath(os.path.dirname(path), self.data_dir):
            self._append_data_files_to_model(path)
            self.item_changed.emit()

    @Slot(bool)
    def copy_to_project(self, checked=False):
        """Copy selected file references to this Data Connection's data directory."""
        selected_indexes = self._properties_ui.treeView_dc_references.selectedIndexes()
        if not selected_indexes:
            self._logger.msg_warning.emit("No files to copy")
            return
        for index in selected_indexes:
            file_path = self.reference_model.itemFromIndex(index).data(Qt.DisplayRole)
            if not os.path.exists(file_path):
                self._logger.msg_error.emit(f"File <b>{file_path}</b> does not exist")
                continue
            filename = os.path.split(file_path)[1]
            self._logger.msg.emit(f"Copying file <b>{filename}</b> to Data Connection <b>{self.name}</b>")
            try:
                shutil.copy(file_path, self.data_dir)
            except OSError:
                self._logger.msg_error.emit("[OSError] Copying failed")

    @Slot("QModelIndex")
    def open_reference(self, index):
        """Open reference in default program."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        reference = self.references[index.row()]
        url = "file:///" + reference
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Failed to open reference:<b>{reference}</b>")

    @Slot("QModelIndex")
    def open_data_file(self, index):
        """Open data file in default program."""
        if not index:
            return
        if not index.isValid():
            logging.error("Index not valid")
            return
        data_file = self.data_files()[index.row()]
        url = "file:///" + os.path.join(self.data_dir, data_file)
        # noinspection PyTypeChecker, PyCallByClass, PyArgumentList
        res = open_url(url)
        if not res:
            self._logger.msg_error.emit(f"Opening file <b>{data_file}</b> failed")

    @busy_effect
    def show_spine_datapackage_form(self):
        """Show spine_datapackage_form widget."""
        if self.spine_datapackage_form:
            if self.spine_datapackage_form.windowState() & Qt.WindowMinimized:
                # Remove minimized status and restore window with the previous state (maximized/normal state)
                self.spine_datapackage_form.setWindowState(
                    self.spine_datapackage_form.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
                )
                self.spine_datapackage_form.activateWindow()
            else:
                self.spine_datapackage_form.raise_()
            return
        self.spine_datapackage_form = self._toolbox.create_spine_datapackage_form(self)
        self.spine_datapackage_form.destroyed.connect(self.datapackage_form_destroyed)
        self.spine_datapackage_form.show()

    @Slot()
    def datapackage_form_destroyed(self):
        """Notify a connection that datapackage form has been destroyed."""
        self.spine_datapackage_form = None

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

    def remove_files(self):
        """Remove selected files from data directory."""
        indexes = self._properties_ui.treeView_dc_data.selectedIndexes()
        if not indexes:  # Nothing selected
            self._logger.msg.emit("Please select files to remove")
            return
        file_list = list()
        for index in indexes:
            file_at_index = self.data_model.itemFromIndex(index).data(Qt.DisplayRole)
            file_list.append(file_at_index)
        files = "\n".join(file_list)
        msg = (
            "The following files will be removed permanently from the project\n\n"
            "{0}\n\n"
            "Are you sure?".format(files)
        )
        title = "Remove {0} File(s)".format(len(file_list))
        message_box = QMessageBox(
            QMessageBox.Question, title, msg, QMessageBox.Ok | QMessageBox.Cancel, parent=self._toolbox
        )
        message_box.button(QMessageBox.Ok).setText("Remove Files")
        answer = message_box.exec_()
        if answer == QMessageBox.Cancel:
            return
        for filename in file_list:
            path_to_remove = os.path.join(self.data_dir, filename)
            try:
                os.remove(path_to_remove)
                self._logger.msg.emit(f"File <b>{path_to_remove}</b> removed")
            except OSError:
                self._logger.msg_error.emit(f"Removing file {path_to_remove} failed.\nCheck permissions.")

    def file_references(self):
        """Returns a list of paths to files that are in this item as references."""
        return self.references

    def data_files(self):
        """Returns a list of files that are in the data directory."""
        if not os.path.isdir(self.data_dir):
            return []
        files = list()
        with os.scandir(self.data_dir) as scan_iterator:
            for entry in scan_iterator:
                if entry.is_file():
                    files.append(entry.path)
        return files

    def populate_reference_list(self):
        """List file references in QTreeView.
        """
        self.reference_model.clear()
        self.reference_model.setHorizontalHeaderItem(0, QStandardItem("References"))  # Add header
        self._append_references_to_model(*self.references)

    def _append_references_to_model(self, *paths):
        for path in paths:
            item = QStandardItem(path)
            item.setFlags(~Qt.ItemIsEditable)
            item.setData(path, Qt.ToolTipRole)
            item.setData(self._toolbox.style().standardIcon(QStyle.SP_FileLinkIcon), Qt.DecorationRole)
            self.reference_model.appendRow(item)

    def populate_data_list(self):
        """List project internal data (files) in QTreeView.
        """
        self.data_model.clear()
        self.data_model.setHorizontalHeaderItem(0, QStandardItem("Data"))  # Add header
        self._append_data_files_to_model(*self.data_files())

    def _append_data_files_to_model(self, *paths):
        for path in paths:
            item = QStandardItem(path)
            item.setFlags(~Qt.ItemIsEditable)
            if path == "datapackage.json":
                item.setData(self.datapackage_icon, Qt.DecorationRole)
            else:
                item.setData(QFileIconProvider().icon(QFileInfo(path)), Qt.DecorationRole)
            full_path = os.path.join(self.data_dir, path)  # For drag and drop
            item.setData(full_path, Qt.UserRole)
            self.data_model.appendRow(item)

    def update_name_label(self):
        """Update Data Connection tab name label. Used only when renaming project items."""
        self._properties_ui.label_dc_name.setText(self.name)

    def resources_for_direct_successors(self):
        """see base class"""
        refs = self.file_references()
        data_files = [os.path.join(self.data_dir, f) for f in self.data_files()]
        resources = []
        for path in refs + data_files:
            updated_from = self._updated_from.pop(path, None)
            metadata = {"updated_from": updated_from} if updated_from else {}
            resource = ProjectItemResource(self, "file", url=pathlib.Path(path).as_uri(), metadata=metadata)
            resources.append(resource)
        return resources

    def _do_handle_dag_changed(self, resources, _):
        """See base class."""
        if not self.file_references() and not self.data_files():
            self.add_notification(
                "This Data Connection does not have any references or data. "
                "Add some in the Data Connection Properties panel."
            )

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        # Convert paths to relative before saving
        d["references"] = [serialize_path(f, self._project.project_dir) for f in self.file_references()]
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project, logger):
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        references = [deserialize_path(r, project.project_dir) for r in item_dict.get("references", list())]
        return DataConnection(name, description, x, y, toolbox, project, logger, references)

    def rename(self, new_name):
        """Rename this item.

        Args:
            new_name (str): New name
        Returns:
            bool: True if renaming succeeded, False otherwise
        """
        self.file_system_watcher.remove_persistent_dir_path(self.data_dir)
        if not super().rename(new_name):
            return False
        self.file_system_watcher.add_persistent_dir_path(self.data_dir)
        self.populate_data_list()
        return True

    def tear_down(self):
        """Tears down this item. Called by toolbox just before closing.
        Closes the SpineDatapackageWidget instances opened."""
        if self.spine_datapackage_form:
            self.spine_datapackage_form.close()
        self.file_system_watcher.tear_down()

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

    @staticmethod
    def default_name_prefix():
        """See base class."""
        return "Data Connection"


def _samepath(path1, path2):
    return os.path.normcase(path1) == os.path.normcase(path2)
