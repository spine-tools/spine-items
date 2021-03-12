######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
ImportMappings widget.

:author: P. Vennström (VTT)
:date:   1.6.2019
"""

from copy import deepcopy
from PySide2.QtCore import QObject, QPoint, QItemSelectionModel, Signal, Slot, Qt
from spinetoolbox.widgets.custom_delegates import ComboBoxDelegate

# from spinedb_api import ConstantMapping
from .custom_menus import MappingListMenu
from .table_view_with_button_header import LineEditWithTypeButton
from ..commands import CreateMapping, DeleteMapping, DuplicateMapping, PasteMappings

SOURCE_TYPES = ("Constant", "Column", "Row", "Column Header", "Headers", "Table Name", "None")


class ImportMappings(QObject):
    """
    Provides methods for managing Mappings (add, remove, edit, visualize, and so on).
    """

    mapping_selection_changed = Signal(object)
    """Emitted with a new MappingSpecificationModel whenever a new mapping is selected from the Mappings list."""
    mapping_data_changed = Signal(object)
    """Emits the new MappingListModel."""
    about_to_undo = Signal(str)
    """Emitted before an undo/redo action."""

    def __init__(self, parent):
        """
        Args:
            parent (ImportEditorWindow): importer window's UI
        """
        super().__init__()
        self._parent = parent
        self._ui = parent._ui
        self._source_table = None
        self._mappings_model = None
        self._copied_mappings = parent._copied_mappings
        self._undo_stack = parent._undo_stack
        # initialize interface
        # NOTE: We make the delegate an attribute so it's never accidentally gc'ed
        self._src_type_delegate = ComboBoxDelegate(SOURCE_TYPES)
        self._ui.mapping_spec_table.setItemDelegateForColumn(1, self._src_type_delegate)

        # connect signals
        self._ui.new_button.clicked.connect(self.new_mapping)
        self._ui.remove_button.clicked.connect(self.delete_selected_mapping)
        self._ui.duplicate_button.clicked.connect(self.duplicate_selected_mapping)
        self._ui.mapping_list.customContextMenuRequested.connect(self._show_mapping_list_context_menu)
        self.mapping_selection_changed.connect(self._update_mapping_spec_table)

    @Slot(object)
    def _update_mapping_spec_table(self, mapping_spec_model):
        current_model = self._ui.mapping_spec_table.model()
        if current_model is not None:
            current_model.modelReset.disconnect(self._resize_table_view_mappings_columns)
        self._ui.mapping_spec_table.setModel(mapping_spec_model)
        self._resize_table_view_mappings_columns()
        mapping_spec_model.modelReset.connect(self._resize_table_view_mappings_columns)
        self._set_line_edit_with_type_button()
        mapping_spec_model.mapping_changed.connect(self._set_line_edit_with_type_button)

    @Slot()
    def _set_line_edit_with_type_button(self):
        """Sets a LineEditWithTypeButton for the value mapping index if it's a constant mapping.
        This is so the user can set the convert_spec for that mapping.
        """
        model = self._ui.mapping_spec_table.model()
        index = model.value_mapping_index()
        if not index.isValid():
            return
        m = model.component_mapping_from_index(index)
        if m.is_constant():
            widget = self._ui.mapping_spec_table.indexWidget(index)
            if widget is None:
                widget = LineEditWithTypeButton(self._ui.mapping_spec_table)
                widget.reference_changed.connect(lambda ref: model.setData(index, ref))
                widget.convert_spec_changed.connect(model.change_constant_value_convert_spec)
            widget.set_component_mapping(m)
            widget.set_background_color(index.data(Qt.BackgroundRole))
        else:
            widget = None
        self._ui.mapping_spec_table.setIndexWidget(index, widget)

    @Slot()
    def _resize_table_view_mappings_columns(self):
        self._ui.mapping_spec_table.resizeColumnsToContents()

    @Slot(str, object)
    def set_mappings_model(self, source_table_name, model):
        """
        Called when the user selects a new source table.
        Sets a new MappingListModel model.

        Args:
            source_table_name (str): newly selected source table's name
            model (MappingListModel): mapping list model attached to that source table.
        """
        self._source_table = source_table_name
        if self._mappings_model is not None:
            self._mappings_model.dataChanged.disconnect(self.data_changed)
        self._mappings_model = model
        self._ui.mapping_list.setModel(model)
        for specification in self._mappings_model.mapping_specifications:
            specification.about_to_undo.connect(self.focus_on_changing_specification)
        self._ui.mapping_list.selectionModel().currentChanged.connect(self.change_mapping)
        self._mappings_model.dataChanged.connect(self.data_changed)
        if self._mappings_model.rowCount() > 0:
            self._select_row(0)
        else:
            self._ui.mapping_list.clearSelection()
            self.mapping_selection_changed.emit(None)

    @Slot(str, str)
    def focus_on_changing_specification(self, source_table_name, mapping_name):
        """
        Selects the given mapping from the list and emits about_to_undo.

        Args:
            source_table_name (str): name of the source table
            mapping_name (str): name of the mapping specification
        """
        self.about_to_undo.emit(source_table_name)
        row = self._mappings_model.row_for_mapping(mapping_name)
        index = self._mappings_model.index(row, 0)
        self._ui.mapping_list.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    @Slot()
    def data_changed(self):
        """Emits the mappingDataChanged signal with the currently selected data mappings."""
        m = None
        indexes = self._ui.mapping_list.selectedIndexes()
        if self._mappings_model and indexes:
            m = self._mappings_model.data_mapping(indexes[0])
        self.mapping_data_changed.emit(m)

    @Slot()
    def new_mapping(self):
        """
        Pushes a CreateMapping command to the undo stack
        """
        if self._mappings_model is None:
            return
        row = self._mappings_model.rowCount()
        command = CreateMapping(self._source_table, self, row)
        self._undo_stack.push(command)

    def create_mapping(self):
        if self._mappings_model is None:
            return
        mapping_name = self._mappings_model.insert_mapping()
        specification = self._mappings_model.mapping_specification(mapping_name)
        row = self._mappings_model.rowCount() - 1

        def select_row_slot():
            # We want to select the mapping during undo/redo to show the user where the changes happen.
            self._select_row(row)

        specification.dataChanged.connect(select_row_slot)
        specification.about_to_undo.connect(self.focus_on_changing_specification)
        self._select_row(row)
        return mapping_name

    def insert_mapping_specification(self, source_table_name, name, row, mapping_specification):
        self.about_to_undo.emit(source_table_name)
        if self._mappings_model is None:
            return
        self._mappings_model.insert_mapping_specification(name, row, mapping_specification)
        self._select_row(row)

    @Slot()
    def duplicate_selected_mapping(self):
        """
        Pushes a DuplicateMapping command to the undo stack.
        """
        selection_model = self._ui.mapping_list.selectionModel()
        if self._mappings_model is None or not selection_model.hasSelection():
            return
        row = selection_model.currentIndex().row()
        command = DuplicateMapping(self._source_table, self, row)
        self._undo_stack.push(command)

    def duplicate_mapping(self, source_table_name, row):
        if self._mappings_model is None:
            return
        spec = self._mappings_model.mapping_specifications[row]
        dup_spec = spec.duplicate(source_table_name, self._undo_stack)
        prefix = self._mappings_model.mapping_name_at(row) + "--"
        name = self._mappings_model._make_new_mapping_name(prefix)
        self.insert_mapping_specification(source_table_name, name, row + 1, dup_spec)
        return name

    @Slot()
    def delete_selected_mapping(self):
        """
        Pushes a DeleteMapping command to the undo stack.
        """
        selection_model = self._ui.mapping_list.selectionModel()
        if self._mappings_model is None or not selection_model.hasSelection():
            return
        row = selection_model.currentIndex().row()
        mapping_name = self._mappings_model.mapping_name_at(row)
        self._undo_stack.push(DeleteMapping(self._source_table, self, mapping_name, row))

    def delete_mapping(self, source_table_name, name):
        self.about_to_undo.emit(source_table_name)
        if self._mappings_model is None:
            return None
        row = self._mappings_model.row_for_mapping(name)
        if row is None:
            return None
        mapping_specification = self._mappings_model.remove_mapping(row)
        mapping_count = self._mappings_model.rowCount()
        if mapping_count:
            if row == mapping_count:
                self._select_row(mapping_count - 1)
            else:
                self._select_row(row)
        else:
            self._ui.mapping_list.clearSelection()
        return mapping_specification

    def _select_row(self, row):
        selection_model = self._ui.mapping_list.selectionModel()
        if selection_model.hasSelection():
            current_row = selection_model.currentIndex().row()
            if row == current_row:
                return
        selection_model.setCurrentIndex(self._mappings_model.index(row, 0), QItemSelectionModel.ClearAndSelect)

    @Slot(object, object)
    def change_mapping(self, current, previous):
        row = current.row()
        index = self._mappings_model.index(row, 0)
        if index.isValid():
            self.mapping_selection_changed.emit(self._mappings_model.data_mapping(index))
        else:
            self.mapping_selection_changed.emit(None)

    @Slot(QPoint)
    def _show_mapping_list_context_menu(self, pos):
        global_pos = self._ui.mapping_list.mapToGlobal(pos)
        indexes = self._ui.mapping_list.selectionModel().selectedRows()
        source_list_menu = MappingListMenu(self._ui.source_list, global_pos, bool(indexes), bool(self._copied_mappings))
        option = source_list_menu.get_action()
        source_list_menu.deleteLater()
        if option == "Copy mapping(s)":
            self._copied_mappings = self._copy_mappings()
            return
        if option == "Paste mapping(s)":
            previous = self._copy_mappings()
            self._undo_stack.push(PasteMappings(self._parent, self._source_table, self._copied_mappings, previous))

    def _copy_mappings(self, indexes=None):
        if indexes is None:
            specs = self._mappings_model._mapping_specifications
        else:
            specs = [self._mappings_model.data_mapping(index) for index in indexes]
        return {spec.mapping_name: deepcopy(spec.mapping) for spec in specs}
