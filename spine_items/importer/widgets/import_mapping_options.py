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

"""ImportMappingOptions widget."""
from PySide6.QtCore import Qt, Slot, QModelIndex
from .custom_menus import SimpleFilterMenu
from ..commands import (
    SetImportEntitiesFlag,
    SetItemMappingDimensionCount,
    SetItemMappingType,
    SetMapCompressFlag,
    SetMapDimensionCount,
    SetParameterType,
    SetValueType,
    SetSkipColumns,
    SetReadStartRow,
    SetTimeSeriesRepeatFlag,
    SetUseBeforeAlternativeFlag,
)
from ..flattened_mappings import MappingType
from ..mvcmodels.mappings_model import Role


class ImportMappingOptions:
    """
    Controls the 'Mapping options' part of the window.
    """

    def __init__(self, mappings_model, ui, undo_stack):
        """
        Args:
            mappings_model (MappingsModel): mappings model
            ui (Any): import editor's UI
            undo_stack (QUndoStack): undo stack
        """
        # state
        self._mappings_model = mappings_model
        self._list_index = QModelIndex()
        self._ui = ui
        self._undo_stack = undo_stack
        self._block_signals = False
        ## ui
        self._ui_ignore_columns_filtermenu = SimpleFilterMenu(self._ui.ignore_columns_button, show_empty=False)
        self._ui.ignore_columns_button.setMenu(self._ui_ignore_columns_filtermenu)
        ## connect signals
        self._mappings_model.dataChanged.connect(self._update_options)
        self._ui.mapping_list.selectionModel().currentChanged.connect(self.reload_options)
        self._ui.dimension_spin_box.valueChanged.connect(self._change_dimension_count)
        self._ui.class_type_combo_box.currentTextChanged.connect(self._change_item_mapping_type)
        self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_parameter_type)
        self._ui.value_type_combo_box.currentTextChanged.connect(self._change_value_type)
        self._ui.before_alternative_check_box.stateChanged.connect(self._change_use_before_alternative)
        self._ui.import_entities_check_box.stateChanged.connect(self._change_import_entities)
        self._ui_ignore_columns_filtermenu.filterChanged.connect(self._change_skip_columns)
        self._ui.start_read_row_spin_box.valueChanged.connect(self._change_read_start_row)
        self._ui.time_series_repeat_check_box.stateChanged.connect(self._change_time_series_repeat_flag)
        self._ui.map_dimension_spin_box.valueChanged.connect(self._change_map_dimension_count)
        self._ui.map_compression_check_box.stateChanged.connect(self._change_map_compression_flag)
        self._update_ui()

    @Slot(int)
    def set_num_available_columns(self, num):
        mapping_index = self._ui.mapping_list.selectionModel().currentIndex()
        if mapping_index.isValid():
            selected = mapping_index.data(Role.ITEM).flattened_mappings.root_mapping.skip_columns
        else:
            selected = []
        # The filter menu is 1-based
        self._ui_ignore_columns_filtermenu._filter._filter_model.set_list(set(range(1, num + 1)))
        self._update_ignore_columns_button(selected)

    def _has_current_mappings(self):
        """Checks if mappings list has current mappings.

        Returns:
            bool: True if mappings list has current selected, False otherwise
        """
        if not self._list_index.isValid():
            return False
        table_index = self._ui.source_list.selectionModel().currentIndex()
        if not table_index.isValid() or table_index.row() < 1:
            return False
        return self._mappings_model.rowCount(table_index) > 0

    @Slot(QModelIndex, QModelIndex, int)
    def _update_options(self, top_left, bottom_right, roles):
        """Updates widget contents when flattened mappings change.

        Args:
            top_left (QModelIndex): top left index
            bottom_right (QModelIndex): bottom right index
            roles (list of int): Qt's data roles
        """
        if bottom_right.column() > 0 and top_left.parent() == self._list_index:
            flattened_mappings = self._list_index.data(Role.FLATTENED_MAPPINGS)
            self._ui.ignore_columns_button.setEnabled(flattened_mappings.root_mapping.is_pivoted())
            self._ui.ignore_columns_label.setEnabled(flattened_mappings.root_mapping.is_pivoted())
            return
        if top_left != self._list_index or Role.FLATTENED_MAPPINGS not in roles:
            return
        self._update_ui()

    @Slot(QModelIndex, QModelIndex)
    def reload_options(self, current, previous):
        """Reloads widget contents.

        Args:
            current (QModelIndex): currently selected mapping list index
            previous (QModelIndex): previously selected mapping list index
        """
        self._list_index = current
        self._update_ui()

    def _update_ui(self):
        """
        Updates ui according to the current mapping type.
        """
        has_mapping = self._has_current_mappings()
        self._ui.mapping_options_contents.setEnabled(has_mapping)
        for i in range(self._ui.mapping_options_contents.count()):
            self._ui.mapping_options_contents.itemAt(i).widget().setEnabled(has_mapping)
        if not has_mapping:
            return
        flattened_mappings = self._list_index.data(Role.FLATTENED_MAPPINGS)
        self._block_signals = True
        try:
            class_type_index = [
                MappingType.EntityClass,
                MappingType.EntityGroup,
                MappingType.Alternative,
                MappingType.Scenario,
                MappingType.ScenarioAlternative,
                MappingType.ParameterValueList,
            ].index(flattened_mappings.map_type)
        except ValueError:
            class_type_index = -1
        self._ui.class_type_combo_box.setCurrentIndex(class_type_index)

        # update item mapping settings
        if flattened_mappings.may_import_entities():
            self._ui.import_entities_check_box.setEnabled(True)
            check_state = Qt.CheckState.Checked if flattened_mappings.import_entities() else Qt.CheckState.Unchecked
            self._ui.import_entities_check_box.setCheckState(check_state)
        else:
            self._ui.import_entities_check_box.setEnabled(False)
        can_have_dimensions = flattened_mappings.can_have_dimensions()
        self._ui.dimension_label.setEnabled(can_have_dimensions)
        self._ui.dimension_spin_box.setEnabled(can_have_dimensions)
        if can_have_dimensions:
            self._ui.dimension_spin_box.setValue(flattened_mappings.dimension_count())

        # update parameter mapping settings
        has_parameters = flattened_mappings.has_parameters()
        self._ui.parameter_type_label.setEnabled(has_parameters)
        self._ui.parameter_type_combo_box.setEnabled(has_parameters)
        if has_parameters:
            self._ui.parameter_type_combo_box.setCurrentText(flattened_mappings.display_parameter_type())
        has_value_component = flattened_mappings.has_value_component()
        self._ui.value_type_label.setEnabled(has_value_component)
        self._ui.value_type_combo_box.setEnabled(has_value_component)
        if has_value_component:
            self._ui.value_type_combo_box.setCurrentText(flattened_mappings.value_type)
            self._ui.value_type_label.setText(flattened_mappings.value_type_label())

        # update before alternative settings
        is_scenario_alternative_mapping = flattened_mappings.map_type == MappingType.ScenarioAlternative
        self._ui.before_alternative_check_box.setEnabled(is_scenario_alternative_mapping)
        if is_scenario_alternative_mapping:
            self._ui.before_alternative_check_box.setChecked(flattened_mappings.uses_before_alternative())

        # update ignore columns filter
        self._ui.ignore_columns_button.setEnabled(flattened_mappings.root_mapping.is_pivoted())
        self._ui.ignore_columns_label.setEnabled(flattened_mappings.root_mapping.is_pivoted())
        self._update_ignore_columns_button(flattened_mappings.root_mapping.skip_columns)

        self._ui.start_read_row_spin_box.setValue(flattened_mappings.root_mapping.read_start_row + 1)

        self._update_time_series_options()
        self._update_map_options()
        self._block_signals = False

    @Slot(list)
    def _update_ignore_columns_button(self, skip_cols):
        """
        Args:
            skip_cols (list of int): 0-based list of ignored columns
        """
        # NOTE: We go from 0-based to 1-based, for visualization
        skip_cols = [c + 1 for c in skip_cols]
        self._ui_ignore_columns_filtermenu._filter._filter_model.set_selected(skip_cols)
        skip_button_text = ", ".join(str(c) for c in skip_cols)
        if len(skip_button_text) > 20:
            skip_button_text = skip_button_text[:20] + "..."
        self._ui.ignore_columns_button.setText(skip_button_text)

    @Slot(str)
    def _change_item_mapping_type(self, new_type):
        """
        Pushes a SetItemMappingType command to the undo stack

        Args:
            new_type (str): item's new type
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_mapping = self._list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._undo_stack.push(
            SetItemMappingType(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                new_type,
                previous_mapping,
            )
        )

    @Slot(int)
    def _change_dimension_count(self, dimension_count):
        """
        Pushes a SetItemMappingDimensionCount command to the undo stack.

        Args:
            dimension_count (int): mapping's dimension
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_mapping = self._list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._undo_stack.push(
            SetItemMappingDimensionCount(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                dimension_count,
                previous_mapping,
            )
        )

    @Slot(str)
    def _change_parameter_type(self, new_type):
        """
        Pushes a SetParameterType command to undo stack.

        Args:
            new_type (str): new parameter type's name
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_mapping = self._list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._undo_stack.push(
            SetParameterType(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                new_type,
                previous_mapping,
            )
        )

    @Slot(str)
    def _change_value_type(self, new_type):
        """
        Pushes a SetValueType command to undo stack.

        Args:
            new_type (str): new value type's name
        """
        if self._block_signals or not self._has_current_mappings():
            return
        old_type = self._list_index.data(Role.ITEM).flattened_mappings.value_type
        self._undo_stack.push(
            SetValueType(
                self._list_index.parent().row(), self._list_index.row(), self._mappings_model, new_type, old_type
            )
        )

    @Slot(int)
    def _change_use_before_alternative(self, state):
        """
        Pushes SetUseBeforeAlternative command to the undo stack.

        Args:
            state (int): New state value
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_mapping = self._list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._undo_stack.push(
            SetUseBeforeAlternativeFlag(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                state == Qt.CheckState.Checked.value,
                previous_mapping,
            )
        )

    @Slot(int)
    def _change_import_entities(self, state):
        """
        Pushes SetImportEntitiesFlag command to the undo stack.

        Args:
            state (int): New state value
        """
        if self._block_signals or not self._has_current_mappings():
            return
        self._undo_stack.push(
            SetImportEntitiesFlag(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                state == Qt.CheckState.Checked.value,
            )
        )

    @Slot(int)
    def _change_read_start_row(self, row):
        """
        Pushes :class:`SetReadStartRow` to the undo stack.

        Args:
            row (int): new read start row
        """
        if self._block_signals or not self._has_current_mappings():
            return
        row -= 1
        previous_row = self._list_index.data(Role.ITEM).flattened_mappings.read_start_row()
        self._undo_stack.push(
            SetReadStartRow(
                self._list_index.parent().row(), self._list_index.row(), self._mappings_model, row, previous_row
            )
        )

    def _change_skip_columns(self, skip_cols):
        """Pushes :class:`SetSkipColumns` to the undo stack.

        Args:
            skip_cols (list): list of columns or column names
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_skip_cols = self._list_index.data(Role.ITEM).flattened_mappings.skip_columns().copy()
        # NOTE: The columns in the filter menu are 1-based, for visualization. Here we need them 0-based
        skip_cols = [c - 1 for c in skip_cols]
        self._undo_stack.push(
            SetSkipColumns(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                skip_cols,
                previous_skip_cols,
            )
        )

    @Slot(int)
    def _change_time_series_repeat_flag(self, repeat):
        """
        Pushes :class:`SetTimeSeriesRepeatFlag` to the undo stack.

        Args:
            repeat (int): True if repeat is enabled, False otherwise
        """
        if self._block_signals or not self._has_current_mappings():
            return
        self._undo_stack.push(
            SetTimeSeriesRepeatFlag(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                repeat == Qt.CheckState.Checked.value,
            )
        )

    @Slot(int)
    def _change_map_dimension_count(self, dimension_count):
        """
        Pushes :class:`SetMapDimensionCount` to the undo stack.

        Args:
            dimension_count (int): new map dimension_count
        """
        if self._block_signals or not self._has_current_mappings():
            return
        previous_mapping_root = self._list_index.data(Role.FLATTENED_MAPPINGS).root_mapping
        self._undo_stack.push(
            SetMapDimensionCount(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                dimension_count,
                previous_mapping_root,
            )
        )

    @Slot(int)
    def _change_map_compression_flag(self, compress):
        """
        Pushes :class:`SetMapCompressFlag` to the undo stack.

        Args:
            compress (int): if ``Qt.CheckState.Checked.value``, Maps will be compressed
        """
        if self._block_signals or not self._has_current_mappings():
            return
        self._undo_stack.push(
            SetMapCompressFlag(
                self._list_index.parent().row(),
                self._list_index.row(),
                self._mappings_model,
                compress == Qt.CheckState.Checked.value,
            )
        )

    def _update_time_series_options(self):
        """Updates widgets that concern time series type parameters"""
        if not self._has_current_mappings():
            return
        flattened_mappings = self._list_index.data(Role.ITEM).flattened_mappings
        value_mapping = flattened_mappings.value_mapping()
        if value_mapping is None:
            self._ui.time_series_repeat_check_box.setEnabled(False)
            return
        is_time_series = flattened_mappings.is_time_series_value()
        self._ui.time_series_repeat_check_box.setEnabled(is_time_series)
        self._ui.time_series_repeat_check_box.setCheckState(
            Qt.CheckState.Checked if is_time_series and value_mapping.options.get("repeat") else Qt.CheckState.Unchecked
        )

    def _update_map_options(self):
        """Updates widgets that concern map type parameters."""
        if not self._has_current_mappings():
            return
        flattened_mappings = self._list_index.data(Role.ITEM).flattened_mappings
        value_mapping = flattened_mappings.value_mapping()
        if value_mapping is None:
            self._ui.map_dimensions_label.setEnabled(False)
            self._ui.map_dimension_spin_box.setEnabled(False)
            self._ui.map_compression_check_box.setEnabled(False)
            return
        is_map = flattened_mappings.is_map_value()
        dimension_count = flattened_mappings.map_dimension_count()
        self._ui.map_dimensions_label.setEnabled(is_map)
        self._ui.map_dimension_spin_box.setEnabled(is_map)
        self._ui.map_dimension_spin_box.setValue(dimension_count)
        self._ui.map_compression_check_box.setEnabled(is_map)
        self._ui.map_compression_check_box.setChecked(True if is_map and value_mapping.compress else False)
