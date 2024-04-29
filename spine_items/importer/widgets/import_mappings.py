######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""ImportMappings widget."""
import pickle
from PySide6.QtCore import QPoint, QItemSelectionModel, Slot, QModelIndex, QMimeData, QItemSelection
from PySide6.QtWidgets import QHeaderView, QStyledItemDelegate, QApplication
from spinedb_api.import_mapping.import_mapping_compat import unparse_named_mapping_spec
from spinetoolbox.widgets.custom_delegates import ComboBoxDelegate
from spinetoolbox.widgets.parameter_value_editor import ParameterValueEditor
from .custom_menus import MappingListMenu
from .filter_edit_delegate import FilterEditDelegate
from .mime_types import MAPPING_LIST_MIME_TYPE
from ..commands import CreateMapping, DeleteMapping, DuplicateMapping, PasteMappings
from ..mvcmodels.mappings_model_roles import Role
from ..mvcmodels.mappings_model import FlattenedColumn
from ...widgets import combo_box_width

SOURCE_TYPES = ("Constant", "Column", "Row", "Column Header", "Headers", "Table Name", "None")


class ImportMappings:
    """
    Controls the 'Mappings' and 'Mapping specifications' part of the window.
    """

    def __init__(self, mappings_model, ui, undo_stack, editor_window):
        """
        Args:
            mappings_model (MappingsModel): mappings model
            ui (Any): import editor window's UI
            undo_stack (QUndoStack): undo stack
            editor_window (ImportEditorWindow): import editor window
        """
        self._editor_window = editor_window
        self._ui = ui
        self._mappings_model = mappings_model
        self._undo_stack = undo_stack
        # initialize interface
        # NOTE: We make the delegate an attribute so it's never accidentally gc'ed
        self._src_type_delegate = ComboBoxDelegate(SOURCE_TYPES)
        self._parameter_constant_value_delegate = ParameterConstantValueDelegate(self._editor_window)
        self._filter_edit_delegate = FilterEditDelegate(self._editor_window)
        self._ui.mapping_spec_table.setItemDelegateForColumn(FlattenedColumn.POSITION_TYPE, self._src_type_delegate)
        self._ui.mapping_spec_table.setItemDelegateForColumn(
            FlattenedColumn.POSITION, self._parameter_constant_value_delegate
        )
        self._ui.mapping_spec_table.setItemDelegateForColumn(FlattenedColumn.REGEXP, self._filter_edit_delegate)
        self._ui.mapping_spec_table.horizontalHeader().sectionCountChanged.connect(self._resize_spec_table_columns)
        # connect signals
        self._mappings_model.modelReset.connect(self._dummify_root_indexes)
        self._mappings_model.dataChanged.connect(self._select_changed_mapping)
        self._mappings_model.rowsInserted.connect(self._update_current_after_mapping_insertion)
        self._mappings_model.rowsInserted.connect(self._set_mapping_list_buttons_enabled)
        self._mappings_model.rowsRemoved.connect(self._show_list_after_mapping_removal)
        self._mappings_model.rowsRemoved.connect(self._set_mapping_list_buttons_enabled)
        self._ui.source_list.selectionModel().currentChanged.connect(self._change_list)
        self._ui.mapping_list.selectionModel().currentChanged.connect(self._change_flattened_mappings)
        self._ui.mapping_list.selectionModel().selectionChanged.connect(self._update_buttons_enabled)
        self._ui.new_button.clicked.connect(self._new_mapping)
        self._ui.remove_button.clicked.connect(self._delete_selected_mapping)
        self._ui.duplicate_button.clicked.connect(self._duplicate_selected_mapping)
        self._ui.mapping_list.customContextMenuRequested.connect(self._show_mapping_list_context_menu)

    def specification_saved(self):
        """Notifies mappings model items that they have been stored into the specification."""
        self._mappings_model.set_source_table_items_into_specification()

    @Slot(QModelIndex, QModelIndex)
    def _change_list(self, current, previous):
        """Loads current source table's mapping list.

        Args:
            current (QModelIndex): currently selected source table index
            previous (QModelIndex): previously selected source table index
        """
        if not current.isValid():
            self._ui.mapping_list.setRootIndex(self._mappings_model.dummy_parent())
            self._ui.mapping_list.selectionModel().setCurrentIndex(QModelIndex(), QItemSelectionModel.ClearAndSelect)
            return
        self._ui.mapping_list.setRootIndex(current)
        if self._mappings_model.rowCount(current) > 0:
            self._ui.mapping_list.selectionModel().setCurrentIndex(
                self._mappings_model.index(0, 0, current), QItemSelectionModel.ClearAndSelect
            )
        else:
            self._ui.mapping_list.selectionModel().setCurrentIndex(QModelIndex(), QItemSelectionModel.ClearAndSelect)
        self._set_mapping_list_buttons_enabled(current)

    @Slot(QModelIndex, int, int)
    def _update_current_after_mapping_insertion(self, table_index, first, last):
        """Selects newly inserted rows in mapping list view.

        Args:
            table_index (QModelIndex): table index
            first (int): first inserted row index
            last (int): last inserted row index
        """
        if not self._mappings_model.is_table_index(table_index):
            return
        if table_index != self._ui.mapping_list.rootIndex():
            self._ui.source_list.selectionModel().setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)
        top_left = self._mappings_model.index(first, 0, table_index)
        bottom_right = self._mappings_model.index(last, 0, table_index)
        selection_model = self._ui.mapping_list.selectionModel()
        selection_model.select(QItemSelection(top_left, bottom_right), QItemSelectionModel.ClearAndSelect)
        selection_model.setCurrentIndex(self._mappings_model.index(last, 0, table_index), QItemSelectionModel.Select)

    @Slot(QModelIndex, int, int)
    def _show_list_after_mapping_removal(self, table_index, first, last):
        """Selects correct mapping list after new mappings have been inserted.

        Args:
            table_index (QModelIndex): table index
            first (int): first inserted row index
            last (int): last inserted row index
        """
        if not self._mappings_model.is_table_index(table_index):
            return
        if table_index != self._ui.mapping_list.rootIndex():
            self._ui.source_list.selectionModel().setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)

    @Slot(QModelIndex)
    def _set_mapping_list_buttons_enabled(self, table_index):
        """Sets New, Duplicate and Remove button enabled state when selecting a source table.

        Args:
            table_index (QModelIndex): table index
        """
        if not table_index.isValid() or self._mappings_model.is_mapping_list_index(table_index):
            return
        number_of_sources = len(self._ui.mapping_list.model())
        number_of_tables = len(self._mappings_model.real_table_names())
        selected_source = table_index.row()
        if table_index.row() == 1 and number_of_tables == 1:
            is_first_or_last = False
        elif number_of_sources - number_of_tables == 1 and selected_source == number_of_sources - 1:
            is_first_or_last = False
        else:
            is_first_or_last = selected_source in [0, number_of_sources - 1]
        self._ui.new_button.setEnabled(not is_first_or_last)

        has_entries = self._mappings_model.rowCount(table_index) > 0
        self._ui.remove_button.setEnabled(has_entries)
        self._ui.duplicate_button.setEnabled(has_entries)

    @Slot(QItemSelection, QItemSelection)
    def _update_buttons_enabled(self, _selected, _deselected):
        enabled = self._ui.mapping_list.selectionModel().hasSelection()
        self._ui.remove_button.setEnabled(enabled)
        self._ui.duplicate_button.setEnabled(enabled)

    @Slot(QModelIndex, QModelIndex)
    def _change_flattened_mappings(self, current, previous):
        """Loads current mapping to component editor.

        Args:
            current (QModelIndex): currently selected mapping list index
            previous (QModelIndex): previously selected mapping list index
        """
        self._ui.mapping_list.selectionModel().select(current, QItemSelectionModel.Select)
        if not current.isValid():
            self._ui.mapping_spec_table.setRootIndex(self._mappings_model.dummy_parent())
            return
        self._ui.mapping_spec_table.setRootIndex(current)

    @Slot()
    def _dummify_root_indexes(self):
        """Makes sure we don't show source table list in other widgets."""
        self._ui.mapping_list.setRootIndex(self._mappings_model.dummy_parent())
        self._ui.mapping_spec_table.setRootIndex(self._mappings_model.dummy_parent())

    @Slot(QModelIndex, QModelIndex, list)
    def _select_changed_mapping(self, top_left, bottom_right, roles):
        """Sets current indexes such that the previously changed mapping is shown on the window.

        Args:
            top_left (QModelIndex): top left index of changes
            bottom_right (QModelIndex): bottom right index of changes
            roles (list of int): Qt's data roles
        """
        if self._mappings_model.is_table_index(top_left):
            return
        if self._mappings_model.is_mapping_list_index(top_left):
            list_selection_model = self._ui.mapping_list.selectionModel()
            list_index = list_selection_model.currentIndex()
            list_selection = QItemSelection(top_left, bottom_right)
            if list_selection.contains(list_index):
                return
            table_index = top_left.parent()
            table_selection_model = self._ui.source_list.selectionModel()
            if table_index != table_selection_model.currentIndex():
                table_selection_model.setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)
            list_selection_model.select(list_selection, QItemSelectionModel.ClearAndSelect)
            list_selection_model.setCurrentIndex(bottom_right, QItemSelectionModel.Select)
            return
        list_index = top_left.parent()
        table_index = list_index.parent()
        table_selection_model = self._ui.source_list.selectionModel()
        if table_index != table_selection_model.currentIndex():
            table_selection_model.setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)
        list_selection_model = self._ui.mapping_list.selectionModel()
        if list_index != list_selection_model.currentIndex():
            list_selection_model.setCurrentIndex(list_index, QItemSelectionModel.ClearAndSelect)

    @Slot()
    def _new_mapping(self):
        """
        Pushes a CreateMapping command to the undo stack
        """
        table_index = self._ui.mapping_list.rootIndex()
        list_row = self._mappings_model.rowCount(table_index)
        command = CreateMapping(table_index.row(), self._mappings_model, list_row)
        self._undo_stack.push(command)

    @Slot()
    def _duplicate_selected_mapping(self):
        """
        Pushes a DuplicateMapping command to the undo stack.
        """
        selection_model = self._ui.mapping_list.selectionModel()
        if not selection_model.hasSelection():
            return
        indexes = selection_model.selectedIndexes()
        table_row = indexes[0].parent().row()
        list_rows = sorted(i.row() for i in indexes)
        self._undo_stack.beginMacro("duplicate mapping(s)")
        for list_row in reversed(list_rows):
            self._undo_stack.push(DuplicateMapping(table_row, self._mappings_model, list_row))
        self._undo_stack.endMacro()

    @Slot()
    def _delete_selected_mapping(self):
        """
        Pushes a DeleteMapping command to the undo stack.
        """
        selection_model = self._ui.mapping_list.selectionModel()
        if not selection_model.hasSelection():
            return
        indexes = selection_model.selectedIndexes()
        if len(indexes) == 1:
            index = indexes[0]
            self._undo_stack.push(DeleteMapping(index.parent().row(), self._mappings_model, index.row()))
        else:
            table_row = indexes[0].parent().row()
            rows = sorted(i.row() for i in indexes)
            self._undo_stack.beginMacro("remove mappings")
            for row in reversed(rows):
                self._undo_stack.push(DeleteMapping(table_row, self._mappings_model, row))
            self._undo_stack.endMacro()

    @Slot(QPoint)
    def _show_mapping_list_context_menu(self, pos):
        global_pos = self._ui.mapping_list.mapToGlobal(pos)
        indexes = self._ui.mapping_list.selectionModel().selectedRows()
        source_list_menu = MappingListMenu(self._ui.source_list, global_pos, bool(indexes), self._can_paste_mappings())
        option = source_list_menu.get_action()
        source_list_menu.deleteLater()
        if option == "Copy mapping(s)":
            self._copy_selected_mappings_to_clipboard()
            return
        if option == "Paste mapping(s)":
            table_index = self._ui.source_list.selectionModel().currentIndex()
            index = self._ui.mapping_list.selectionModel().currentIndex()
            target_row = index.row() + 1 if self._mappings_model.rowCount(table_index) > 0 else 0
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            mapping_dicts = pickle.loads(mime_data.data(MAPPING_LIST_MIME_TYPE))
            self._undo_stack.push(PasteMappings(table_index.row(), target_row, self._mappings_model, mapping_dicts))

    def _copy_selected_mappings_to_clipboard(self):
        """Copies selected mappings to system clipboard."""
        selection_model = self._ui.mapping_list.selectionModel()
        if not selection_model.hasSelection():
            return
        mapping_dicts = list()
        for index in selection_model.selectedIndexes():
            name = index.data()
            flattened_mappings = index.data(Role.FLATTENED_MAPPINGS)
            mapping_dicts.append(unparse_named_mapping_spec(name, flattened_mappings.root_mapping))
        mime_data = QMimeData()
        mime_data.setData(MAPPING_LIST_MIME_TYPE, pickle.dumps(mapping_dicts))
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data)

    def _can_paste_mappings(self):
        """Checks if it is possible to paste mappings.

        Returns:
            bool: True if mappings can be pasted, False otherwise
        """
        has_table = self._ui.source_list.selectionModel().currentIndex().isValid()
        has_target = self._ui.mapping_list.selectionModel().currentIndex().isValid()
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        return mime_data.hasFormat(MAPPING_LIST_MIME_TYPE) and has_table and has_target

    @Slot(int, int)
    def _resize_spec_table_columns(self, old_column_count, new_column_count):
        """Configures mapping specification table's column widths.

        Args:
            old_column_count (int): previous column count
            new_column_count (int): current column count
        """
        if new_column_count != len(FlattenedColumn):
            return
        spec_table_header = self._ui.mapping_spec_table.horizontalHeader()
        spec_table_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        spec_table_header.setSectionResizeMode(FlattenedColumn.POSITION_TYPE, QHeaderView.ResizeMode.Fixed)
        spec_table_header.resizeSection(
            FlattenedColumn.POSITION_TYPE, combo_box_width(self._editor_window, SOURCE_TYPES)
        )


class ParameterConstantValueDelegate(QStyledItemDelegate):
    """A delegate that shows a ParameterValueEditor for constant value mappings."""

    def __init__(self, parent):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if index.column() != 2:
            return super().createEditor(parent, option, index)
        target = index.siblingAtColumn(0).data()
        ref_type = index.siblingAtColumn(1).data()
        if target.endswith("values") and ref_type == "Constant":
            editor = ParameterValueEditor(index, parent)  # TODO: plain=True for parameter value lists
            editor.show()
            return None
        return super().createEditor(parent, option, index)
