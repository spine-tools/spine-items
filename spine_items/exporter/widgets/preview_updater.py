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

"""Contains :class:`PreviewUpdater`."""
from copy import deepcopy
from time import monotonic
from PySide6.QtCore import QItemSelectionModel, QModelIndex, QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtWidgets import QFileDialog
from spinedb_api.export_mapping.group_functions import NoGroup
from spinedb_api.spine_io.exporters.writer import write
from spinedb_api import DatabaseMapping, SpineDBVersionError, SpineDBAPIError
from spinetoolbox.helpers import busy_effect
from ..mvcmodels.full_url_list_model import FullUrlListModel
from ..mvcmodels.mappings_table_model import MappingsTableModel
from ..mvcmodels.preview_tree_model import PreviewTreeModel
from ..mvcmodels.preview_table_model import PreviewTableModel
from ..preview_table_writer import TableWriter


class PreviewUpdater:
    def __init__(
        self, window, ui, url_model, mappings_table_model, mappings_proxy_model, mapping_editor_table_model, project_dir
    ):
        """
        Args:
            window (SpecificationEditorWindow): specification editor's window
            ui (Ui_Form): specification editor's UI
            url_model (FullUrlListModel, optional): URL model
            mappings_table_model (MappingsTableModel): mappings table model
            mappings_proxy_model (QAbstractProxyModel): proxy model for mappings table
            mapping_editor_table_model (MappingEditorTableModel): mapping table model
            project_dir (str): path to initial directory from which to load databases
        """
        self._current_url = None
        self._window = window
        self._ui = ui
        self._project_dir = project_dir
        if url_model is None:
            url_model = FullUrlListModel(self._ui.database_url_combo_box)
        self._url_model = url_model
        self._url_model.rowsInserted.connect(self._enable_controls_after_url_insertion)
        self._url_model.modelReset.connect(self._enable_controls)
        self._url_model.destroyed.connect(self._forget_url_model)
        self._ui.database_url_combo_box.setModel(self._url_model)
        self._mappings_table_model = mappings_table_model
        self._set_expect_removals_and_inserts(False)
        self._mappings_table_model.write_order_about_to_change.connect(
            lambda: self._set_expect_removals_and_inserts(True)
        )
        self._mappings_table_model.write_order_changed.connect(lambda: self._set_expect_removals_and_inserts(False))
        self._mappings_table_model.dataChanged.connect(self._rename_mapping)
        self._mappings_table_model.dataChanged.connect(self._enable_mapping)
        self._mappings_table_model.dataChanged.connect(self._update_changed_tables)
        self._mappings_proxy_model = mappings_proxy_model
        self._mapping_editor_table_model = mapping_editor_table_model
        self._mapping_editor_table_model.dataChanged.connect(lambda *_: self._update_current_mappings_tables())
        self._expect_mapping_editor_resets(False)
        self._window.current_mapping_about_to_change.connect(lambda: self._expect_mapping_editor_resets(True))
        self._window.current_mapping_changed.connect(lambda: self._expect_mapping_editor_resets(False))
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
        self._ui.live_preview_check_box.stateChanged.connect(self._ui.frame_preview.setEnabled)
        self._ui.live_preview_check_box.clicked.connect(self._reload_preview)
        self._ui.max_preview_rows_spin_box.valueChanged.connect(self._reload_preview)
        self._ui.max_preview_tables_spin_box.valueChanged.connect(self._reload_preview)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.mappings_table.selectionModel().currentChanged.connect(self._change_selected_table)
        self._enable_controls()
        if self._url_model.rowCount() > 0:
            self._reload_preview()

    @Slot()
    def _reload_preview(self):
        """Sets the current url and reloads preview."""
        current_url = self._ui.database_url_combo_box.currentText()
        if not current_url:
            return
        self._current_url = current_url
        self._stamps.clear()
        for row in range(self._mappings_table_model.rowCount()):
            index = self._mappings_table_model.index(row, 0)
            if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked:
                self._load_preview_data(index.data())

    @Slot(QModelIndex, QModelIndex)
    def _change_table(self, current, previous):
        """
        Changes preview table data.

        Args:
            current (QModelIndex): index to the currently selected table on the list
            previous (QModelIndex): index to the previously selected table on the list
        """
        current_parent = self._preview_tree_model.parent(current)
        if not current_parent.isValid():
            current_parent = current
        previous_parent = self._preview_tree_model.parent(previous)
        if not previous_parent.isValid():
            previous_parent = previous
        if current_parent != previous_parent:
            name = self._preview_tree_model.data(current_parent)
            index = self._mappings_proxy_model.mapFromSource(self._mappings_table_model.index_of(name))
            self._ui.mappings_table.selectionModel().currentChanged.disconnect(self._change_selected_table)
            self._ui.mappings_table.setCurrentIndex(index)
            self._ui.mappings_table.selectionModel().currentChanged.connect(self._change_selected_table)
        table = current.data(PreviewTreeModel.TABLE_ROLE)
        if table is not None:
            table_name = current.data()
            mapping_name = current.parent().data()
            mapping_colors = self._mapping_editor_table_model.mapping_colors()
            self._preview_table_model.reset(mapping_name, table_name, table, mapping_colors)
        else:
            self._preview_table_model.clear()

    @Slot(QModelIndex, QModelIndex)
    def _change_selected_table(self, current, previous):
        """
        Changes selected table on the tree view after user has selected another mapping.

        Args:
            current (QModelIndex): index to selected mapping on mapping list
            previous (QModelIndex): index to previously selected mapping on mapping list
        """
        if not current.isValid():
            return
        current = self._mappings_proxy_model.mapToSource(current)
        mappings_index = self._mappings_table_model.index(current.row(), 0)
        if mappings_index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value:
            return
        current_preview = self._ui.preview_tree_view.selectionModel().currentIndex()
        if current_preview.parent().row() >= self._preview_tree_model.rowCount():
            # May happen when mappings at the end of the list are removed.
            return
        mapping_name = mappings_index.data()
        if current_preview.parent().data() == mapping_name:
            return
        self._set_current_table(mapping_name)

    def _set_current_table(self, name):
        """Sets the current index of preview tree.

        Args:
            name (str): mapping's name
        """
        for row in range(self._preview_tree_model.rowCount()):
            index = self._preview_tree_model.index(row, 0)
            if index.data() == name:
                if self._preview_tree_model.rowCount(index) > 0:
                    table_index = self._preview_tree_model.index(0, 0, index)
                    self._ui.preview_tree_view.selectionModel().setCurrentIndex(
                        table_index, QItemSelectionModel.ClearAndSelect
                    )
                    return
                self._ui.preview_tree_view.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)
                return

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
            table = index.data(PreviewTreeModel.TABLE_ROLE)
            mapping_colors = self._mapping_editor_table_model.mapping_colors()
            self._preview_table_model.reset(mapping_name, table_name, table, mapping_colors)
            break

    def _set_expect_removals_and_inserts(self, except_removals):
        """Connects and disconnects signals with regarding mapping removals.

        Args:
            except_removals (bool): True means that a mapping removal is expected
        """
        if except_removals:
            self._mappings_table_model.rowsAboutToBeRemoved.disconnect(self._remove_mappings)
            self._mappings_table_model.rowsInserted.disconnect(self._add_mappings)
        else:
            self._mappings_table_model.rowsAboutToBeRemoved.connect(self._remove_mappings)
            self._mappings_table_model.rowsInserted.connect(self._add_mappings)

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
        for row in range(last, first - 1, -1):
            index = self._mappings_table_model.index(row, 0)
            if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value:
                continue
            removed_name = index.data()
            self._preview_tree_model.remove_mapping(removed_name)
            self._stamps.pop((self._current_url, removed_name), None)

    @Slot(QModelIndex, QModelIndex, list)
    def _rename_mapping(self, top_left, bottom_right, roles):
        """
        Renames preview models' mappings.

        Args:
            top_left (QModelIndex): top left corner of modified mappings' in mapping list model
            bottom_right (QModelIndex): bottom right corner of modified mappings' in mapping list model
            roles (list of int): changed data's role
        """
        if Qt.ItemDataRole.DisplayRole not in roles or self._current_url is None:
            return
        make_index = self._mappings_table_model.index
        indexes = [make_index(row, 0) for row in range(self._mappings_table_model.rowCount())]
        names = [
            index.data() for index in indexes if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
        ]
        old_name, new_name = self._preview_tree_model.rename_mappings(names)
        if not old_name:
            return
        self._stamps.pop((self._current_url, old_name), None)
        self._set_current_table(new_name)

    @Slot(QModelIndex, QModelIndex, list)
    def _enable_mapping(self, top_left, bottom_right, roles):
        """
        Removes/adds mappings as they are enabled or disabled.

        Args:
            top_left (QModelIndex): top left corner of modified mappings' in mapping list model
            bottom_right (QModelIndex): bottom right corner of modified mappings' in mapping list model
            roles (list of int): changed data's role
        """
        if Qt.ItemDataRole.CheckStateRole.value not in roles or self._current_url is None:
            return
        first = top_left.row()
        last = bottom_right.row()
        for row in range(first, last + 1):
            index = self._mappings_table_model.index(row, 0)
            enabled = index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
            name = index.data()
            if not enabled and self._preview_tree_model.has_name(name):
                self._preview_tree_model.remove_mapping(name)
                self._stamps.pop((self._current_url, name), None)
            elif not self._preview_tree_model.has_name(name):
                self._load_preview_data(name)

    @Slot(QModelIndex, QModelIndex, list)
    def _update_changed_tables(self, top_left, bottom_right, roles):
        """
        Updates mappings whenever the always write header flag or fixed table name changes.

        Args:
            top_left (QModelIndex): top left corner of modified mappings' in mapping list model
            bottom_right (QModelIndex): bottom right corner of modified mappings' in mapping list model
            roles (list of int): changed data's role
        """
        if (
            not {
                MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE,
                MappingsTableModel.FIXED_TABLE_NAME_ROLE,
                MappingsTableModel.GROUP_FN_ROLE,
            }
            & set(roles)
        ):
            return
        row = self._mappings_proxy_model.mapToSource(self._ui.mappings_table.currentIndex()).row()
        index = self._mappings_table_model.index(row, 0)
        if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value:
            return
        name = index.data()
        self._load_preview_data(name)

    @Slot()
    def _update_current_mappings_tables(self):
        """Reloads mapping that is currently selected on mapping list."""
        if self._current_url is None:
            return
        current_index = self._ui.mappings_table.currentIndex()
        if not current_index.isValid():
            return
        row = self._mappings_proxy_model.mapToSource(current_index).row()
        index = self._mappings_table_model.index(row, 0)
        if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value:
            return
        mapping_name = index.data()
        self._load_preview_data(mapping_name)

    @Slot(QModelIndex, int, int)
    def _add_mappings(self, parent, first, last):
        """Adds new mapping for preview.

        Args:
            parent (QModelIndex): parent index - unused
            first (int): first row added to mappings table
            last (int): last row added to mappings table
        """
        if self._current_url is None:
            return
        for row in range(first, last + 1):
            index = self._mappings_table_model.index(first, 0)
            if index.data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value:
                continue
            mapping_name = index.data()
            self._load_preview_data(mapping_name)

    def _expect_mapping_editor_resets(self, expect_resets):
        """Connects and disconnects signals that handle mapping editor resets.

        Args:
            expect_resets (bool): True to except editor resets
        """
        if expect_resets:
            self._mapping_editor_table_model.modelReset.disconnect(self._update_current_mappings_tables)
        else:
            self._mapping_editor_table_model.modelReset.connect(self._update_current_mappings_tables)

    @Slot(QModelIndex, int, int)
    def _enable_controls_after_url_insertion(self, parent, first, last):
        """Enables controls after new preview database URL has been inserted."""
        self._enable_controls()

    @Slot()
    def _enable_controls(self):
        """Enables and disables widgets as needed."""
        urls_available = self._url_model.rowCount() > 0
        self._ui.max_preview_rows_spin_box.setEnabled(urls_available)
        self._ui.max_preview_tables_spin_box.setEnabled(urls_available)

    def _load_preview_data(self, mapping_name):
        """
        Loads preview data from database into the preview tables if the url is set and live previews are enabled.

        Args:
            mapping_name (str): mapping's name
        """
        if self._current_url is None or not self._ui.live_preview_check_box.isChecked() or not mapping_name:
            return
        mapping_spec = self._mappings_table_model.mapping_specification(mapping_name)
        max_tables = self._ui.max_preview_tables_spin_box.value()
        max_rows = self._ui.max_preview_rows_spin_box.value()
        id_ = (self._current_url, mapping_name)
        stamp = monotonic()
        self._stamps[id_] = stamp
        worker = _Worker(
            self._current_url,
            mapping_name,
            deepcopy(mapping_spec.root),
            mapping_spec.always_export_header,
            stamp,
            max_tables,
            max_rows,
            mapping_spec.group_fn,
        )
        worker.signals.table_written.connect(self._add_or_update_data)
        self._thread_pool.start(worker)

    @Slot(tuple, str, object, float)
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
        mapping_index = self._ui.mappings_table.selectionModel().currentIndex()
        self._change_selected_table(mapping_index, mapping_index)

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

    @Slot()
    def _forget_url_model(self):
        """Replaces current URL model with a mock one."""
        self._url_model = FullUrlListModel(self._ui.database_url_combo_box)
        self._url_model.rowsInserted.connect(self._enable_controls_after_url_insertion)
        self._url_model.modelReset.connect(self._enable_controls)
        self._url_model.destroyed.connect(self._forget_url_model)
        self._ui.database_url_combo_box.setModel(self._url_model)
        self._reload_preview()

    def tear_down(self):
        """Stops all workers."""
        self._stamps.clear()
        self._thread_pool.clear()
        self._thread_pool.deleteLater()
        self._url_model.rowsInserted.disconnect(self._enable_controls_after_url_insertion)
        self._url_model.modelReset.disconnect(self._enable_controls)
        self._url_model.destroyed.disconnect(self._forget_url_model)


class _Worker(QRunnable):
    class Signals(QObject):
        table_written = Signal(tuple, str, object, float)

    def __init__(
        self, url, mapping_name, mapping, always_export_header, stamp, max_tables=20, max_rows=20, group_fn=NoGroup.NAME
    ):
        super().__init__()
        self._url = url
        self._mapping_name = mapping_name
        self._mapping = mapping
        self._always_export_header = always_export_header
        self._max_tables = max_tables
        self._max_rows = max_rows
        self._group_fn = group_fn
        self._stamp = stamp
        self.signals = self.Signals()

    @busy_effect
    def run(self):
        try:
            db_map = DatabaseMapping(self._url)
        except SpineDBVersionError:
            tables = {"error": [["unsupported database version"]]}
            self.signals.table_written.emit((self._url, self._mapping_name), self._mapping_name, tables, self._stamp)
            return
        except SpineDBAPIError as error:
            tables = {"error": [[str(error)]]}
            self.signals.table_written.emit((self._url, self._mapping_name), self._mapping_name, tables, self._stamp)
            return
        try:
            writer = TableWriter()
            write(
                db_map,
                writer,
                self._mapping,
                empty_data_header=self._always_export_header,
                max_tables=self._max_tables,
                max_rows=self._max_rows,
                group_fns=self._group_fn,
            )
            self.signals.table_written.emit(
                (self._url, self._mapping_name), self._mapping_name, writer.tables, self._stamp
            )
        except SpineDBAPIError as error:
            tables = {"error": [[str(error)]]}
            self.signals.table_written.emit((self._url, self._mapping_name), self._mapping_name, tables, self._stamp)
            return
        finally:
            db_map.close()
            self.signals.deleteLater()
