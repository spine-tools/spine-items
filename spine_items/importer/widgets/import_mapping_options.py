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
ImportMappingOptions widget.

:author: P. Vennström (VTT)
:date:   12.5.2020
"""
from PySide2.QtCore import QObject, Qt, Signal, Slot
from PySide2.QtWidgets import QWidget
from spinetoolbox.widgets.custom_menus import SimpleFilterMenu
from ..commands import (
    SetImportObjectsFlag,
    SetItemMappingDimensionCount,
    SetItemMappingType,
    SetMapCompressFlag,
    SetMapDimensionCount,
    SetParameterType,
    SetValueType,
    SetReadStartRow,
    SetTimeSeriesRepeatFlag,
)
from ..mvcmodels.mapping_specification_model import MappingType


class ImportMappingOptions(QObject):
    """
    Provides methods for managing Mapping options (class type, dimension_count, parameter type, ignore columns, and so on).
    """

    about_to_undo = Signal(str, str)

    def __init__(self, parent):
        """
        Args:
            parent (ImportEditorWindow): importer window's UIk
        """
        # state
        super().__init__()
        self._ui = parent._ui
        self._undo_stack = parent._undo_stack
        self._mapping_specification_model = None
        self._block_signals = False
        self._executing_command = False
        self._ui_ignore_columns_filtermenu = None
        # ui
        self._ui_ignore_columns_filtermenu = SimpleFilterMenu(self._ui.ignore_columns_button, show_empty=False)
        self._ui.ignore_columns_button.setMenu(self._ui_ignore_columns_filtermenu)

        # connect signals
        self._ui.dimension_spin_box.valueChanged.connect(self._change_dimension_count)
        self._ui.class_type_combo_box.currentTextChanged.connect(self._change_item_mapping_type)
        self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_parameter_type)
        self._ui.value_type_combo_box.currentTextChanged.connect(self._change_value_type)
        self._ui.import_objects_check_box.stateChanged.connect(self._change_import_objects)
        self._ui_ignore_columns_filtermenu.filterChanged.connect(self.change_skip_columns)
        self._ui.start_read_row_spin_box.valueChanged.connect(self._change_read_start_row)
        self._ui.time_series_repeat_check_box.stateChanged.connect(self._change_time_series_repeat_flag)
        self._ui.map_dimension_spin_box.valueChanged.connect(self._change_map_dimension_count)
        self._ui.map_compression_check_box.stateChanged.connect(self._change_map_compression_flag)
        self.update_ui()

    @Slot(int)
    def set_num_available_columns(self, num):
        selected = self._ui_ignore_columns_filtermenu._filter._filter_model.get_selected()
        self._ui_ignore_columns_filtermenu._filter._filter_model.set_list(set(range(num)))
        self._ui_ignore_columns_filtermenu._filter._filter_model.set_selected(selected)

    def change_skip_columns(self, skip_cols):
        if self._mapping_specification_model:
            self._mapping_specification_model.set_skip_columns(skip_cols)

    @Slot(object)
    def set_mapping_specification_model(self, model):
        if self._mapping_specification_model is not None:
            self._mapping_specification_model.modelReset.disconnect(self.update_ui)
            self._mapping_specification_model.dataChanged.disconnect(self.update_ui)
            self._mapping_specification_model.mapping_read_start_row_changed.disconnect(
                self._ui.start_read_row_spin_box.setValue
            )
        self._mapping_specification_model = model
        if self._mapping_specification_model is not None:
            self._mapping_specification_model.modelReset.connect(self.update_ui)
            self._mapping_specification_model.dataChanged.connect(self.update_ui)
            self._mapping_specification_model.mapping_read_start_row_changed.connect(
                self._ui.start_read_row_spin_box.setValue
            )
        self.update_ui()

    def update_ui(self):
        """
        Updates ui according to the current mapping type.
        """
        for widget in self._ui.dockWidget_mapping_options.findChildren(QWidget):
            widget.setEnabled(bool(self._mapping_specification_model))
        if not self._mapping_specification_model:
            return

        self._block_signals = True
        class_type_index = [
            MappingType.ObjectClass,
            MappingType.RelationshipClass,
            MappingType.ObjectGroup,
            MappingType.Alternative,
            MappingType.Scenario,
            MappingType.ScenarioAlternative,
            MappingType.ParameterValueList,
            MappingType.Feature,
            MappingType.Tool,
            MappingType.ToolFeature,
            MappingType.ToolFeatureMethod,
        ].index(self._mapping_specification_model.map_type)
        self._ui.class_type_combo_box.setCurrentIndex(class_type_index)

        # update item mapping settings
        if self._mapping_specification_model.mapping_can_import_objects():
            self._ui.import_objects_check_box.setEnabled(True)
            check_state = Qt.Checked if self._mapping_specification_model.import_objects else Qt.Unchecked
            self._ui.import_objects_check_box.setCheckState(check_state)
        else:
            self._ui.import_objects_check_box.setEnabled(False)
        if self._mapping_specification_model.mapping_has_dimensions():
            self._ui.dimension_label.setEnabled(True)
            self._ui.dimension_spin_box.setEnabled(True)
            self._ui.dimension_spin_box.setValue(self._mapping_specification_model.dimension_count())
        else:
            self._ui.dimension_label.setEnabled(False)
            self._ui.dimension_spin_box.setEnabled(False)

        # update parameter mapping settings
        if self._mapping_specification_model.mapping_has_parameters():
            self._ui.parameter_type_combo_box.setEnabled(True)
            self._ui.parameter_type_combo_box.setCurrentText(self._mapping_specification_model.parameter_type)
        else:
            self._ui.parameter_type_combo_box.setEnabled(False)
        if self._mapping_specification_model.mapping_has_values():
            self._ui.value_type_combo_box.setEnabled(True)
            self._ui.value_type_combo_box.setCurrentText(self._mapping_specification_model.value_type)
            self._ui.value_type_label.setText(self._mapping_specification_model.value_type_label)
        else:
            self._ui.value_type_combo_box.setEnabled(False)

        # update ignore columns filter
        self._ui.ignore_columns_button.setEnabled(self._mapping_specification_model.is_pivoted)
        self._ui.ignore_columns_label.setEnabled(self._mapping_specification_model.is_pivoted)
        skip_cols = []
        if self._mapping_specification_model.mapping.skip_columns:
            skip_cols = self._mapping_specification_model.mapping.skip_columns
        self._ui_ignore_columns_filtermenu._filter._filter_model.set_selected(skip_cols)
        skip_text = ",".join(str(c) for c in skip_cols)
        if len(skip_text) > 20:
            skip_text = skip_text[:20] + "..."
        self._ui.ignore_columns_button.setText(skip_text)

        self._ui.start_read_row_spin_box.setValue(self._mapping_specification_model.read_start_row)

        self._update_time_series_options()
        self._update_map_options()
        self._block_signals = False

    @Slot(str)
    def _change_item_mapping_type(self, new_type):
        """
        Pushes a SetItemMappingType command to the undo stack

        Args:
            new_type (str): item's new type
        """
        if self._executing_command or self._block_signals or self._mapping_specification_model is None:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        previous_mapping = self._mapping_specification_model.mapping
        self._undo_stack.push(
            SetItemMappingType(source_table_name, specification_name, self, new_type, previous_mapping)
        )

    def set_item_mapping_type(self, source_table_name, mapping_specification_name, new_type):
        """
        Sets the type for an item mapping.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            new_type (str): name of the type
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.change_item_mapping_type(new_type)
        self._executing_command = False

    def set_item_mapping(self, source_table_name, mapping_specification_name, mapping):
        """
        Sets item mapping.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            mapping (ImportMapping): item mapping
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_mapping(mapping)
        self._executing_command = False

    @Slot(int)
    def _change_dimension_count(self, dimension_count):
        """
        Pushes a SetItemMappingDimensionCount command to the undo stack.

        Args:
            dimension_count (int): mapping's dimension
        """
        if self._executing_command or self._block_signals:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        previous_dimension_count = self._mapping_specification_model.mapping_dimension_count()
        self._undo_stack.push(
            SetItemMappingDimensionCount(
                source_table_name, specification_name, self, dimension_count, previous_dimension_count
            )
        )

    def set_dimension_count(
        self, source_table_name, mapping_specification_name, dimension_count, new_cls_mapping, new_obj_mapping
    ):
        """
        Changes the item mapping's dimension count and emits about_to_undo.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            dimension_count (int): new dimension value
            new_cls_mapping (RelationshipClassObjectClassMapping): mapping to undo previous dimension removal
            new_obj_mapping (RelationshipObjectMapping): mapping to undo previous dimension removal
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        new_cls_mapping, new_obj_mapping = self._mapping_specification_model.set_dimension_count(
            dimension_count, new_cls_mapping, new_obj_mapping
        )
        self._executing_command = False
        return new_cls_mapping, new_obj_mapping

    @Slot(str)
    def _change_parameter_type(self, new_type):
        """
        Pushes a SetParameterType command to undo stack.

        Args:
            new_type (str): new parameter type's name
        """
        if self._executing_command:
            return
        if self._block_signals:
            return
        if self._mapping_specification_model:
            source_table_name = self._mapping_specification_model.source_table_name
            specification_name = self._mapping_specification_model.mapping_name
            previous_mapping = self._mapping_specification_model.parameter_mapping
            self._undo_stack.push(
                SetParameterType(source_table_name, specification_name, self, new_type, previous_mapping)
            )

    @Slot(str)
    def _change_value_type(self, new_type):
        """
        Pushes a SetValueType command to undo stack.

        Args:
            new_type (str): new value type's name
        """
        if self._executing_command:
            return
        if self._block_signals:
            return
        if self._mapping_specification_model:
            source_table_name = self._mapping_specification_model.source_table_name
            specification_name = self._mapping_specification_model.mapping_name
            old_type = self._mapping_specification_model.value_type
            self._undo_stack.push(SetValueType(source_table_name, specification_name, self, new_type, old_type))

    def set_parameter_type(self, source_table_name, mapping_specification_name, new_type):
        """
        Sets parameter type for an item mapping.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            new_type (src): new parameter type's name
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.change_parameter_type(new_type)
        self._executing_command = False

    def set_value_type(self, source_table_name, mapping_specification_name, new_type):
        """
        Sets parameter value type for an item mapping.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            new_type (src): new parameter type's name
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.change_value_type(new_type)
        self._executing_command = False

    def set_parameter_mapping(self, source_table_name, mapping_specification_name, parameter_mapping):
        """
        Sets parameter mapping for an item mapping.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            parameter_mapping (ParameterDefinitionMapping): new parameter
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_parameter_mapping(parameter_mapping)
        self._executing_command = False

    @Slot(bool)
    def _change_import_objects(self, state):
        """
        Pushes SetImportObjectsFlag command to the undo stack.

        Args:
            state (bool): new flag value
        """
        if self._executing_command or self._block_signals:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        self._undo_stack.push(SetImportObjectsFlag(source_table_name, specification_name, self, state))

    def set_import_objects_flag(self, source_table_name, mapping_specification_name, import_objects):
        """
        Sets the import objects flag.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            import_objects (bool): flag value
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_import_objects(import_objects)
        self._ui.import_objects_check_box.setChecked(import_objects)
        self._executing_command = False

    @Slot(int)
    def _change_read_start_row(self, row):
        """
        Pushes :class:`SetReadStartRow` to the undo stack.

        Args:
            row (int): new read start row
        """
        if self._executing_command or self._block_signals:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        previous_row = self._mapping_specification_model.mapping.read_start_row
        self._undo_stack.push(SetReadStartRow(source_table_name, specification_name, self, row, previous_row))

    def set_read_start_row(self, source_table_name, mapping_specification_name, start_row):
        """
        Sets item's parameter's read start row.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            start_row (int): new read start row value
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_read_start_row(start_row)
        self._executing_command = False

    @Slot(bool)
    def _change_time_series_repeat_flag(self, repeat):
        """
        Pushes :class:`SetTimeSeriesRepeatFlag` to the undo stack.

        Args:
            repeat (bool): True is repeat is enable, False otherwise
        """
        if self._executing_command or self._block_signals:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        self._undo_stack.push(SetTimeSeriesRepeatFlag(source_table_name, specification_name, self, repeat))

    def set_time_series_repeat_flag(self, source_table_name, mapping_specification_name, repeat):
        """
        Sets the time series repeat flag to given value.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            repeat (bool): new repeat flag value
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_time_series_repeat(repeat)
        self._ui.time_series_repeat_check_box.setChecked(repeat)
        self._executing_command = False

    @Slot(int)
    def _change_map_dimension_count(self, dimension_count):
        """
        Pushes :class:`SetMapDimensionCount` to the undo stack.

        Args:
            dimension_count (int): new map dimension_count
        """
        if self._executing_command or self._block_signals:
            return
        if not self._mapping_specification_model.value_mapping:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        previous_dimension_count = self._mapping_specification_model.map_dimension_count()
        self._undo_stack.push(
            SetMapDimensionCount(source_table_name, specification_name, self, dimension_count, previous_dimension_count)
        )

    def set_map_dimension_count(
        self, source_table_name, mapping_specification_name, dimension_count, new_index_mapping
    ):
        """
        Sets map dimension_count.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            dimension_count (int): new map dimension_count
            new_index_mapping (...IndexMapping): Index mapping to undo previous dimension removing
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        new_index_mapping = self._mapping_specification_model.set_map_dimension_count(
            dimension_count, new_index_mapping
        )
        self._ui.map_dimension_spin_box.setValue(dimension_count)
        self._executing_command = False
        return new_index_mapping

    @Slot(bool)
    def _change_map_compression_flag(self, compress):
        """
        Pushes :class:`SetMapCompressFlag` to the undo stack.

        Args:
            compress (CheckState): if ``Qt.Checked``, Maps will be compressed
        """
        if self._executing_command or self._block_signals:
            return
        source_table_name = self._mapping_specification_model.source_table_name
        specification_name = self._mapping_specification_model.mapping_name
        self._undo_stack.push(SetMapCompressFlag(source_table_name, specification_name, self, compress == Qt.Checked))

    def set_map_compress(self, source_table_name, mapping_specification_name, compress):
        """
        Sets map compress flag.

        Args:
            source_table_name (str): name of the source table
            mapping_specification_name (str): name of the mapping specification
            compress (bool): new flag value
        """
        if self._mapping_specification_model is None:
            return
        self._executing_command = True
        self.about_to_undo.emit(source_table_name, mapping_specification_name)
        self._mapping_specification_model.set_map_compress_flag(compress)
        self._ui.map_compression_check_box.setChecked(Qt.Checked if compress else Qt.Unchecked)
        self._executing_command = False

    def _update_time_series_options(self):
        """Updates widgets that concern time series type parameters"""
        if self._mapping_specification_model is None:
            return
        value_mapping = self._mapping_specification_model.value_mapping
        if value_mapping is None:
            self._ui.time_series_repeat_check_box.setEnabled(False)
            return
        is_time_series = self._mapping_specification_model.is_time_series_value()
        self._ui.time_series_repeat_check_box.setEnabled(is_time_series)
        self._ui.time_series_repeat_check_box.setCheckState(
            Qt.Checked if is_time_series and value_mapping.options.get("repeat") else Qt.Unchecked
        )

    def _update_map_options(self):
        """Updates widgets that concern map type parameters."""
        if self._mapping_specification_model is None:
            return
        value_mapping = self._mapping_specification_model.value_mapping
        if value_mapping is None:
            self._ui.map_dimension_spin_box.setEnabled(False)
            return
        is_map = self._mapping_specification_model.is_map_value()
        dimension_count = self._mapping_specification_model.map_dimension_count()
        self._ui.map_dimension_spin_box.setEnabled(is_map)
        self._ui.map_dimension_spin_box.setValue(dimension_count)
        self._ui.map_compression_check_box.setEnabled(is_map)
        self._ui.map_compression_check_box.setChecked(Qt.Checked if is_map and value_mapping.compress else Qt.Unchecked)
