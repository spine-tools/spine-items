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
from time import monotonic
from PySide2.QtCore import QModelIndex, QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide2.QtWidgets import QFileDialog
from spinedb_api.spine_io.exporters.writer import write
from spinedb_api import DatabaseMapping
from spinetoolbox.helpers import busy_effect
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
        self._stamps = dict()
        self._thread_pool = QThreadPool()
        self._mapping_tables = dict()
        self._ui.preview_tree_view.setModel(self._preview_tree_model)
        self._ui.preview_tree_view.selectionModel().currentChanged.connect(self._change_table)
        self._ui.preview_table_view.setModel(self._preview_table_model)
        self._ui.database_url_combo_box.currentTextChanged.connect(self._reload_preview)
        self._ui.live_preview_check_box.clicked.connect(self._reload_preview)
        self._ui.max_preview_rows_spin_box.valueChanged.connect(self._reload_preview)
        self._ui.max_preview_tables_spin_box.valueChanged.connect(self._reload_preview)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._enable_controls()
        if self._url_model.rowCount() > 0:
            self._reload_preview()

    def _reload_preview(self):
        """Sets the current url and reloads preview."""
        self._current_url = self._ui.database_url_combo_box.currentText()
        self._stamps.clear()
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
            self._stamps.pop((self._current_url, removed_name), None)

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
        self._stamps.pop((self._current_url, old_name), None)

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
        urls_available = self._url_model.rowCount() > 0
        self._ui.live_preview_check_box.setEnabled(urls_available)
        self._ui.max_preview_rows_spin_box.setEnabled(urls_available)
        self._ui.max_preview_tables_spin_box.setEnabled(urls_available)

    def _load_preview_data(self, mapping_name):
        """
        Loads preview data from database into the preview tables if the url is set and live previews are enabled.

        Args:
            mapping_name (str): mapping's name
        """
        if self._current_url is None or not self._ui.live_preview_check_box.isChecked():
            return
        mapping = self._mapping_list_model.mapping(mapping_name)
        max_tables = self._ui.max_preview_tables_spin_box.value()
        max_rows = self._ui.max_preview_rows_spin_box.value()
        id_ = (self._current_url, mapping_name)
        stamp = monotonic()
        self._stamps[id_] = stamp
        worker = _Worker(self._current_url, mapping_name, deepcopy(mapping), stamp, max_tables, max_rows)
        worker.signals.table_written.connect(self._add_or_update_data)
        self._thread_pool.start(worker)

    @Slot(tuple, str, dict, float)
    def _add_or_update_data(self, worker_id, mapping_name, data, stamp):
        """
        Sets preview data.

        Args:
            worker_id (tuple): a worker identifier
            mapping_name (str): mapping's name
            data (dict): mapping from table name to table
            stamp (float): worker's time stamp
        """
        current_stamp = self._stamps.pop(worker_id, None)
        if stamp != current_stamp:
            if current_stamp is not None:
                self._stamps[worker_id] = current_stamp
            return
        self._preview_tree_model.add_or_update_tables(mapping_name, data)

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
        self._stamps.clear()
        self._thread_pool.clear()
        self._thread_pool.deleteLater()


class _Worker(QRunnable):
    class Signals(QObject):
        table_written = Signal(tuple, str, dict, float)

    def __init__(self, url, mapping_name, mapping, stamp, max_tables=20, max_rows=20):
        super().__init__()
        self._url = url
        self._mapping_name = mapping_name
        self._mapping = mapping
        self._max_tables = max_tables
        self._max_rows = max_rows
        self._stamp = stamp
        self.signals = self.Signals()

    @busy_effect
    def run(self):
        db_map = DatabaseMapping(self._url)
        try:
            writer = TableWriter(self._max_tables, self._max_rows)
            write(db_map, writer, self._mapping)
            self.signals.table_written.emit(
                (self._url, self._mapping_name), self._mapping_name, writer.tables, self._stamp
            )
        finally:
            db_map.connection.close()
            self.signals.deleteLater()
