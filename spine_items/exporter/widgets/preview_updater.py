######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains :class:`PreviewUpdater`.

:author: A. Soininen (VTT)
:date:   5.1.2021
"""
from copy import deepcopy
from PySide2.QtCore import QModelIndex, QObject, Qt, QThread, QTimer, Signal, Slot
from PySide2.QtWidgets import QFileDialog
from spinedb_api.spine_io.exporters.writer import write
from spinedb_api import DatabaseMapping
from ...models import FullUrlListModel
from ..mvcmodels.preview_tree_model import PreviewTreeModel
from ..mvcmodels.preview_table_model import PreviewTableModel
from ..preview_table_writer import TableWriter


class PreviewUpdater:
    def __init__(self, window, ui, url_model, mapping_list_model, mapping_table_model, project_dir):
        """
        Args:
            window (QMainWindow): specification editor's window
            ui (Ui_Form): specification editor's UI
            url_model (FullUrlListModel, optional): URL model
            mapping_list_model (MappingListModel): mapping list model
            mapping_table_model (MappingTableModel): mapping table model
            project_dir (str): path to initial directory from which to load databases
        """
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.setInterval(100)
        self._update_timer.timeout.connect(self._start_workers)
        self._current_url = None
        self._window = window
        self._ui = ui
        self._project_dir = project_dir
        if url_model is None:
            url_model = FullUrlListModel()
        self._url_model = url_model
        self._url_model.rowsInserted.connect(lambda *_: self._enable_controls())
        self._ui.database_url_combo_box.setModel(self._url_model)
        self._mapping_list_model = mapping_list_model
        self._mapping_list_model.rowsAboutToBeRemoved.connect(self._remove_mappings)
        self._mapping_list_model.rowsInserted.connect(self._add_mappings)
        self._mapping_list_model.dataChanged.connect(self._rename_mapping)
        self._mapping_table_model = mapping_table_model
        self._mapping_table_model.dataChanged.connect(lambda *_: self._reload_current_mapping())
        self._mapping_table_model.modelReset.connect(lambda: self._reload_current_mapping())
        self._preview_tree_model = PreviewTreeModel()
        self._preview_tree_model.dataChanged.connect(self._update_table)
        self._preview_tree_model.dataChanged.connect(self._expand_tree_after_table_change)
        self._preview_tree_model.rowsInserted.connect(self._expand_tree_after_table_insert)
        self._preview_table_model = PreviewTableModel()
        self._workers = dict()
        self._mapping_tables = dict()
        self._ui.preview_tree_view.setModel(self._preview_tree_model)
        self._ui.preview_tree_view.selectionModel().currentChanged.connect(self._change_table)
        self._ui.preview_table_view.setModel(self._preview_table_model)
        self._ui.load_data_button.clicked.connect(self._enable_current_url)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._enable_controls()

    @Slot(bool)
    def _enable_current_url(self, _=True):
        """Reads the URL from the combo box and enables live updates."""
        self._current_url = self._ui.database_url_combo_box.currentText()
        for worker in self._workers.values():
            worker.thread.requestInterruption()
        self._workers.clear()
        for row in range(self._mapping_list_model.rowCount()):
            index = self._mapping_list_model.index(row, 0)
            self._load_preview_data(index.data())

    @Slot(QModelIndex, QModelIndex)
    def _change_table(self, current, previous):
        """
        Changes preview table data.

        Args:
            current (QModelIndex): index to the currently selected table on the list
            previous (QModelIndex): index to the previously selected table on the list
        """
        table = current.data(PreviewTreeModel.TABLE_ROLE)
        if table is not None:
            table_name = current.data()
            mapping_name = current.parent().data()
            self._preview_table_model.reset(mapping_name, table_name, table)

    @Slot(QModelIndex, QModelIndex, list)
    def _expand_tree_after_table_change(self, top_left, bottom_right, roles):
        """
        Expands preview tree's root items if their tables have received updates.

        Args:
            top_left (QModelIndex): top left corner of changed preview tree data
            bottom_right (QModelIndex): bottom right corner of changed preview tree data
            roles (list of int): roles
        """
        if PreviewTreeModel.TABLE_ROLE not in roles:
            return
        root_index = top_left.parent()
        if not root_index.isValid():
            return
        self._ui.preview_tree_view.setExpanded(root_index, True)

    @Slot(QModelIndex, QModelIndex, list)
    def _expand_tree_after_table_insert(self, parent, first, last):
        """
        Expands preview tree's root items if tables have been added/removed.

        Args:
            parent (QModelIndex): parent index of items that have been added/removed
            first (int): first row index of affected items
            last (int): last row index of affected items
        """
        if not parent.isValid():
            return
        self._ui.preview_tree_view.setExpanded(parent, True)

    @Slot(QModelIndex, QModelIndex, list)
    def _update_table(self, top_left, bottom_right, roles):
        """
        Updates the preview table if its data has changed.

        Args:
            top_left (QModelIndex): top left corner of changed preview tree data
            bottom_right (QModelIndex): bottom right corner of changed preview tree data
            roles (list of int): roles
        """
        if PreviewTreeModel.TABLE_ROLE not in roles:
            return
        current_parent = top_left.parent()
        current_table_name = self._preview_table_model.table_name()
        current_mapping_name = self._preview_table_model.mapping_name()
        for row in range(top_left.row(), bottom_right.row() + 1):
            index = self._preview_tree_model.index(row, 0, current_parent)
            table_name = index.data()
            mapping_name = index.parent().data()
            if current_table_name != table_name or current_mapping_name != mapping_name:
                continue
            self._preview_table_model.reset(mapping_name, table_name, index.data(PreviewTreeModel.TABLE_ROLE))
            break

    @Slot(int, int, QModelIndex)
    def _remove_mappings(self, parent, first, last):
        """
        Removes mappings from the preview models.

        Args:
            parent (QModelIndex): parent index, ignored
            first (int): first mapping list row to be removed
            last (int): last mapping list row to be removed
        """
        if self._current_url is None:
            return
        for row in range(first, last + 1):
            removed_name = self._mapping_list_model.index(row, 0).data()
            self._preview_tree_model.remove_mapping(removed_name)
            worker = self._workers.pop((self._current_url, removed_name), None)
            if worker is not None:
                worker.thread.requestInterruption()

    @Slot(QModelIndex, int, int)
    def _add_mappings(self, parent, first, last):
        """
        Adds mappings to the preview models.

        Args:
            parent (QModelIndex): parent index, ignored
            first (int): first mapping list row that has been added
            last (int): last mapping list row that has been added
        """
        if self._current_url is None:
            return
        for row in range(first, last + 1):
            new_name = self._mapping_list_model.index(row, 0).data()
            self._load_preview_data(new_name)

    @Slot(QModelIndex, QModelIndex, list)
    def _rename_mapping(self, top_left, bottom_right, roles):
        """
        Renames preview models' mappings.

        Args:
            top_left (QModelIndex): top left corner of modified mappings' in mapping list model
            bottom_right (QModelIndex): top left corner of modified mappings' in mapping list model
            roles (list of int): changed data's role
        """
        if Qt.DisplayRole not in roles or self._current_url is None:
            return
        mapping_list_model = self._ui.mapping_list.model()
        make_index = mapping_list_model.index
        names = [make_index(row, 0).data() for row in range(mapping_list_model.rowCount())]
        old_name, new_name = self._preview_tree_model.rename_mappings(names)
        worker = self._workers.pop((self._current_url, old_name), None)
        if worker is not None:
            worker.thread.requestInterruption()
            self._load_preview_data(new_name)

    def _reload_current_mapping(self):
        """Reloads mapping that is currently selected on mapping list."""
        if self._current_url is None:
            return
        index = self._ui.mapping_list.currentIndex()
        if not index.isValid():
            return
        mapping_name = index.data()
        self._load_preview_data(mapping_name)

    def _enable_controls(self):
        """Enables and disables widgets as needed."""
        self._ui.load_data_button.setEnabled(self._url_model.rowCount() > 0)

    def _load_preview_data(self, mapping_name):
        """
        Loads preview data from database to be shown on the preview table.

        Args:
            mapping_name (str): mapping's name
        """
        self._update_timer.stop()
        if self._current_url is None:
            return
        existing_worker = self._workers.pop((self._current_url, mapping_name), None)
        if existing_worker is not None:
            existing_worker.thread.requestInterruption()
        mapping = self._mapping_list_model.mapping(mapping_name)
        worker = _Worker(self._current_url, mapping_name, deepcopy(mapping))
        self._workers[(self._current_url, mapping_name)] = worker
        worker.table_written.connect(self._add_or_update_data)
        worker.finished.connect(self._tear_down_worker)
        self._update_timer.start()

    @Slot()
    def _start_workers(self):
        """Starts worker threads."""
        for worker in self._workers.values():
            if not worker.thread.isRunning():
                worker.thread.start()

    @Slot(QObject, str, str, dict)
    def _add_or_update_data(self, worker, url, mapping_name, data):
        """
        Sets preview data.

        Args:
            worker (QObject): a worker
            url (str): database url
            mapping_name (str): mapping's name
            data (dict): mapping from table name to table
        """
        if (url, mapping_name) not in self._workers or worker is not self._workers[(url, mapping_name)]:
            return
        del self._workers[(url, mapping_name)]
        self._preview_tree_model.add_or_update_tables(mapping_name, data)

    @Slot(QObject)
    def _tear_down_worker(self, worker):
        """Cleans up worker thread.

        Args:
            worker (_Worker): worker to clean up
        """
        worker.thread.quit()
        worker.thread.wait()
        worker.thread.deleteLater()
        worker.deleteLater()

    @Slot(bool)
    def _load_url_from_filesystem(self, _):
        """Shows a file dialog and opens selected database in the preview widget."""
        path = self._browse_database()
        if not path:
            return
        url = "sqlite:///" + path
        self._url_model.append(url)
        self._ui.database_url_combo_box.setCurrentText(url)

    def _browse_database(self):
        """
        Queries a database file from the user.

        Returns:
            str: path to database file
        """
        return QFileDialog.getOpenFileName(self._window, "Select database", self._project_dir, "sqlite (*.sqlite)")[0]

    def tear_down(self):
        """Stops all workers."""
        for worker in self._workers:
            worker.thread.requestInterruption()


class _Worker(QObject):

    table_written = Signal(QObject, str, str, dict)
    """Emitted with exported tables when worker has written them."""
    finished = Signal(QObject)
    """Emitted when worker finishes."""

    def __init__(self, url, mapping_name, mapping):
        """
        Args:
            url (str): database URL
            mapping_name (str): mapping's name
            mapping (Mapping): export mapping
        """
        super().__init__()
        self._url = url
        self._mapping_name = mapping_name
        self._mapping = mapping
        self.thread = QThread()
        self.thread.started.connect(self._load_data)

    @Slot()
    def _load_data(self):
        """Exports data to tabular form and emits ``finished``."""
        db_map = DatabaseMapping(self._url)
        try:
            writer = TableWriter(self.thread)
            write(db_map, writer, self._mapping)
            self.table_written.emit(self, self._url, self._mapping_name, writer.tables)
        finally:
            db_map.connection.close()
        self.finished.emit(self)
