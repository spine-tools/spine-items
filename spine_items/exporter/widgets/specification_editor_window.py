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

""" Contains :class:`SpecificationEditorWindow`. """
from copy import deepcopy
import json
from PySide6.QtCore import QItemSelectionModel, QMimeData, QModelIndex, QPoint, Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtWidgets import QApplication, QHeaderView, QMenu
from spinedb_api.mapping import unflatten
from spinedb_api.export_mapping import (
    alternative_export,
    entity_group_export,
    parameter_value_list_export,
    entity_export,
    entity_dimension_parameter_default_value_export,
    entity_dimension_parameter_value_export,
    entity_parameter_default_value_export,
    entity_parameter_value_export,
    scenario_alternative_export,
    scenario_export,
)
from spinedb_api.export_mapping.settings import (
    set_parameter_dimensions,
    set_parameter_default_value_dimensions,
    set_entity_dimensions,
)
from spinedb_api.export_mapping.export_mapping import FixedValueMapping, Position
from spinedb_api.export_mapping.group_functions import (
    GROUP_FUNCTION_DISPLAY_NAMES,
    group_function_name_from_display,
    group_function_display_from_name,
    NoGroup,
)
from spinetoolbox.project_item.specification_editor_window import SpecificationEditorWindowBase
from spinetoolbox.helpers import SealCommand
from .preview_updater import PreviewUpdater
from ..commands import (
    ChangeWriteOrder,
    ClearFixedTableName,
    CompactMapping,
    DisableAllMappings,
    EnableAllMappings,
    NewMapping,
    RemoveMapping,
    RenameMapping,
    SetAlwaysExportHeader,
    SetMappingEnabled,
    SetMappingType,
    SetExportFormat,
    SetMapping,
    SetUseFixedTableNameFlag,
    SetFixedTableName,
    SetGroupFunction,
    SetHighlightDimension,
)
from ..mvcmodels.mappings_table_model import MappingsTableModel
from ..mvcmodels.mapping_editor_table_model import EditorColumn, MappingEditorTableModel, POSITION_DISPLAY_TEXT
from ..mvcmodels.mappings_table_proxy import MappingsTableProxy
from ..specification import MappingSpecification, MappingType, OutputFormat, Specification
from .filter_edit_delegate import FilterEditDelegate
from .position_edit_delegate import PositionEditDelegate
from ...widgets import combo_box_width

mapping_type_to_combo_box_label = {
    MappingType.alternatives: "Alternative",
    MappingType.entities: "Entity class",
    MappingType.entity_groups: "Entity group",
    MappingType.entity_parameter_default_values: "Entity class",
    MappingType.entity_parameter_values: "Entity class",
    MappingType.parameter_value_lists: "Parameter value list",
    MappingType.entity_dimension_parameter_default_values: "Entity class with dimension parameter",
    MappingType.entity_dimension_parameter_values: "Entity class with dimension parameter",
    MappingType.scenario_alternatives: "Scenario alternative",
    MappingType.scenarios: "Scenario",
}

mapping_type_to_parameter_type_label = {
    MappingType.alternatives: "None",
    MappingType.entities: "None",
    MappingType.entity_groups: "None",
    MappingType.entity_parameter_default_values: "Default value",
    MappingType.entity_parameter_values: "Value",
    MappingType.entity_dimension_parameter_default_values: "Default value",
    MappingType.entity_dimension_parameter_values: "Value",
    MappingType.parameter_value_lists: "None",
    MappingType.scenario_alternatives: "None",
    MappingType.scenarios: "None",
}


_MAPPINGS_MIME_TYPE = "application/spine_items-exportmappings"


class SpecificationEditorWindow(SpecificationEditorWindowBase):
    """Interface to edit exporter specifications."""

    current_mapping_about_to_change = Signal()
    current_mapping_changed = Signal()

    def __init__(self, toolbox, specification=None, item=None, url_model=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (Specification, optional): exporter specification
            item (ProjectItem, optional): invoking project item, if window was opened from its properties tab
            url_model (QAbstractListModel): model that provides URLs of connected databases
        """
        super().__init__(toolbox, specification, item)
        if specification is None:
            output_format = self._sniff_export_format() if item is not None else OutputFormat.default()
        else:
            output_format = specification.output_format
        self._new_spec = (
            deepcopy(specification) if specification is not None else Specification(output_format=output_format)
        )
        self._mappings_table_model = MappingsTableModel(self._new_spec.mapping_specifications(), self)
        self._mappings_table_model.dataChanged.connect(self._update_ui_after_mapping_change)
        self._mappings_table_model.rename_requested.connect(self._rename_mapping)
        self._mappings_table_model.mapping_enabled_state_change_requested.connect(self._set_mapping_enabled)
        self._mappings_table_model.set_all_mappings_enabled_requested.connect(self._enable_disable_all_mappings)
        self._mappings_table_model.write_order_about_to_change.connect(
            lambda tr=True: self._expect_current_mapping_change(tr)
        )
        self._mappings_table_model.write_order_changed.connect(lambda tr=False: self._expect_current_mapping_change(tr))
        self._mapping_editor_model = MappingEditorTableModel("", None, self._undo_stack, self, self)
        self._mapping_editor_model.dataChanged.connect(self._validate_fixed_table_name)
        self._sort_mappings_table_model = MappingsTableProxy(self)
        self._sort_mappings_table_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._sort_mappings_table_model.setSourceModel(self._mappings_table_model)
        self._mappings_table_model.rowsInserted.connect(self._select_inserted_row)
        self._mappings_table_model.rowsRemoved.connect(self._check_for_empty_mappings_list)
        self._ui.export_format_combo_box.addItems([output_format.value for output_format in OutputFormat])
        self._ui.export_format_combo_box.setCurrentText(self._new_spec.output_format.value)
        self._ui.export_format_combo_box.currentTextChanged.connect(self._change_format)
        self._add_mapping_action = QAction("Add Mapping", self)
        self._add_mapping_action.triggered.connect(self._new_mapping)
        self._ui.add_mapping_button.clicked.connect(self._add_mapping_action.trigger)
        self._remove_mapping_action = QAction("Remove mappings", self)
        self._remove_mapping_action.setShortcut(QKeySequence(QKeySequence.Delete))
        self._remove_mapping_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._remove_mapping_action.triggered.connect(self._delete_mapping)
        self._copy_mappings_action = QAction("Copy", self)
        self._copy_mappings_action.setShortcut(QKeySequence(QKeySequence.Copy))
        self._copy_mappings_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._copy_mappings_action.triggered.connect(self._copy_mappings_to_clipboard)
        self._paste_mappings_action = QAction("Paste", self)
        self._paste_mappings_action.setShortcut(QKeySequence(QKeySequence.Paste))
        self._paste_mappings_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._paste_mappings_action.triggered.connect(self._paste_mappings_from_clipboard)
        self._duplicate_mappings_action = QAction("Duplicate", self)
        self._duplicate_mappings_action.triggered.connect(self._duplicate_mappings)
        self._ui.remove_mapping_button.clicked.connect(self._remove_mapping_action.trigger)
        self._toggle_all_enabled_action = QAction("Toggle all mappings enabled", self)
        self._toggle_all_enabled_action.triggered.connect(self._toggle_all_enabled)
        self._ui.toggle_enabled_button.clicked.connect(self._toggle_all_enabled_action.trigger)
        self._write_earlier_action = QAction("Write earlier", self)
        self._write_earlier_action.triggered.connect(self._write_earlier)
        self._ui.write_earlier_button.clicked.connect(self._write_earlier_action.trigger)
        self._write_later_action = QAction("Write later", self)
        self._write_later_action.triggered.connect(self._write_later)
        self._ui.write_later_button.clicked.connect(self._write_later_action.trigger)
        self._mappings_table_menu = self._make_mappings_table_menu()
        self._ui.mappings_table.addAction(self._add_mapping_action)
        self._ui.mappings_table.addAction(self._remove_mapping_action)
        self._ui.mappings_table.addAction(self._copy_mappings_action)
        self._ui.mappings_table.addAction(self._paste_mappings_action)
        self._ui.mappings_table.setModel(self._sort_mappings_table_model)
        self._ui.mappings_table.setSortingEnabled(True)
        self._ui.mappings_table.sortByColumn(0, Qt.AscendingOrder)
        self._ui.mappings_table.customContextMenuRequested.connect(self._show_mappings_table_context_menu)
        self._expect_current_mapping_change(False)
        self._ui.mappings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._ui.group_fn_combo_box.addItems(GROUP_FUNCTION_DISPLAY_NAMES)
        self._ui.item_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._ui.parameter_dimensions_spin_box.valueChanged.connect(self._change_parameter_dimensions)
        self._ui.always_export_header_check_box.stateChanged.connect(self._change_always_export_header)
        self._ui.entity_dimensions_spin_box.valueChanged.connect(self._change_entity_dimensions)
        self._ui.highlight_dimension_spin_box.valueChanged.connect(self._change_highlight_dimension)
        self._ui.fix_table_name_check_box.stateChanged.connect(self._change_fix_table_name_flag)
        self._ui.fix_table_name_line_edit.textEdited.connect(self._change_fix_table_name)
        self._ui.fix_table_name_line_edit.editingFinished.connect(self._finish_editing_fix_table_name)
        self._ui.group_fn_combo_box.currentTextChanged.connect(self._change_root_mapping_group_fn)
        self._compact_mapping_action = QAction("Compact mapping", self)
        self._compact_mapping_action.triggered.connect(self._compact_mapping)
        self._ui.compact_button.clicked.connect(self._compact_mapping_action.trigger)
        self._ui.mapping_table_view.setModel(self._mapping_editor_model)
        self._position_edit_delegate = PositionEditDelegate(self)
        self._ui.mapping_table_view.setItemDelegateForColumn(EditorColumn.POSITION, self._position_edit_delegate)
        self._filter_edit_delegate = FilterEditDelegate(self)
        self._ui.mapping_table_view.setItemDelegateForColumn(EditorColumn.FILTER, self._filter_edit_delegate)
        table_header = self._ui.mapping_table_view.horizontalHeader()
        table_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        table_header.setSectionResizeMode(EditorColumn.POSITION, QHeaderView.ResizeMode.Fixed)
        table_header.resizeSection(EditorColumn.POSITION, combo_box_width(self, POSITION_DISPLAY_TEXT.values()))
        self._enable_mapping_specification_editing()
        if specification is None:
            self._mappings_table_model.extend(_new_mapping_specification(MappingType.entities))
        self._preview_updater = PreviewUpdater(
            self,
            self._ui,
            url_model,
            self._mappings_table_model,
            self._sort_mappings_table_model,
            self._mapping_editor_model,
            self._toolbox.project().project_dir,
        )
        self._ui.mappings_table.setCurrentIndex(self._sort_mappings_table_model.index(0, 0))

    @property
    def settings_group(self):
        return "exportSpecificationEditorWindow"

    def _make_ui(self):
        from ..ui.specification_editor import Ui_MainWindow

        return Ui_MainWindow()

    def _make_new_specification(self, spec_name):
        """See base class."""
        description = self._spec_toolbar.description()
        mapping_specification = deepcopy(self._new_spec.mapping_specifications())
        output_format = self._new_spec.output_format
        return Specification(spec_name, description, mapping_specification, output_format)

    @Slot(str)
    def _change_format(self, current):
        """
        Pusher ``SetExportFormat`` command to undo stack.

        Args:
            current (str): new export format
        """
        output_format = OutputFormat(current)
        self._undo_stack.push(SetExportFormat(self, output_format, self._new_spec.output_format))

    def set_export_format_silently(self, export_format):
        """
        Sets export format.

        Args:
            export_format (ExportFormat): new format
        """
        self._new_spec.output_format = export_format
        if export_format.value != self._ui.export_format_combo_box.currentText():
            self._ui.export_format_combo_box.currentTextChanged.disconnect(self._change_format)
            self._ui.export_format_combo_box.setCurrentText(export_format.value)
            self._ui.export_format_combo_box.currentTextChanged.connect(self._change_format)

    def _sniff_export_format(self):
        """Tries to guess the export file format from user given export label.

        Returns:
            OutputFormat: export file format
        """
        if self.item.has_out_url():
            return OutputFormat.SQL
        out_labels = self.item.get_out_labels()
        for label in out_labels:
            name, separator, extension = label.rpartition(".")
            if not separator:
                continue
            output_format = OutputFormat.output_format_from_extension(extension)
            if output_format is None:
                return OutputFormat.default()
            return output_format if output_format is not None else OutputFormat.default()
        return OutputFormat.default()

    def show_on_table(self, mapping_name):
        """
        Changes the current mapping.

        Args:
            mapping_name (str): mapping's name
        """
        index = self._sort_mappings_table_model.mapFromSource(self._mappings_table_model.index_of(mapping_name))
        self._ui.mappings_table.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    @Slot(QModelIndex, QModelIndex)
    def change_current_mapping(self, current, previous):
        """
        Changes the current mapping.

        Args:
            current (QModelIndex): current mapping on mapping name list
            previous (QModelIndex): previous mapping name
        """
        if current.row() == previous.row():
            return
        if not current.isValid():
            self._mapping_editor_model.set_mapping("", None)
            self._ui.mapping_table_view.setEnabled(False)
            return
        self.current_mapping_about_to_change.emit()
        current = self._sort_mappings_table_model.mapToSource(current)
        mapping_type = MappingType(current.data(MappingsTableModel.MAPPING_TYPE_ROLE))
        self._set_mapping_type_silently(mapping_type_to_combo_box_label[mapping_type])
        self._set_parameter_type_silently(mapping_type_to_parameter_type_label[mapping_type])
        self._set_always_export_header_silently(current.data(MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE))
        if mapping_type in {
            MappingType.entities,
            MappingType.entity_parameter_values,
            MappingType.entity_parameter_default_values,
            MappingType.entity_dimension_parameter_values,
            MappingType.entity_dimension_parameter_default_values,
        }:
            self._set_entity_dimensions_silently(current.data(MappingsTableModel.ENTITY_DIMENSIONS_ROLE))
        else:
            self._set_entity_dimensions_silently(0)
        if mapping_type in {
            MappingType.entity_dimension_parameter_values,
            MappingType.entity_dimension_parameter_default_values,
        }:
            self._set_highlight_dimension_silently(current.data(MappingsTableModel.HIGHLIGHT_POSITION_ROLE))
            self._ui.highlight_dimension_spin_box.setMaximum(current.data(MappingsTableModel.ENTITY_DIMENSIONS_ROLE))
        else:
            self._set_highlight_dimension_silently(0)
        if mapping_type in {
            MappingType.entity_parameter_values,
            MappingType.entity_parameter_default_values,
            MappingType.entity_dimension_parameter_values,
            MappingType.entity_dimension_parameter_default_values,
        }:
            self._set_parameter_dimensions_silently(current.data(MappingsTableModel.PARAMETER_DIMENSIONS_ROLE))
        else:
            self._set_parameter_dimensions_silently(0)
        root_mapping = current.data(MappingsTableModel.MAPPING_ROOT_ROLE)
        self._set_use_fixed_table_name_flag_silently(current.data(MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE))
        self._set_fixed_table_name_silently(current.data(MappingsTableModel.FIXED_TABLE_NAME_ROLE))
        if any(
            m.position == Position.table_name for m in root_mapping.flatten() if not isinstance(m, FixedValueMapping)
        ):
            self._ui.fix_table_name_check_box.setEnabled(False)
            self._ui.fix_table_name_line_edit.setEnabled(False)
        self._set_group_fn_silently(group_function_display_from_name(current.data(MappingsTableModel.GROUP_FN_ROLE)))
        mapping_name = self._mappings_table_model.index(current.row(), 0).data()
        self._mapping_editor_model.set_mapping(mapping_name, root_mapping)
        self._enable_entity_controls()
        self._enable_parameter_controls()
        self._ui.mapping_table_view.setEnabled(True)
        self.current_mapping_changed.emit()

    @Slot(bool)
    def _expect_current_mapping_change(self, expect_change):
        """Connects and disconnects signals depending on if current mapping is expected to change.

        Args:
            expect_change (bool): True to expect changes
        """
        if expect_change:
            self._ui.mappings_table.selectionModel().currentChanged.disconnect(self.change_current_mapping)
        else:
            self._ui.mappings_table.selectionModel().currentChanged.connect(self.change_current_mapping)

    @Slot(QModelIndex, QModelIndex, list)
    def _update_ui_after_mapping_change(self, top_left, bottom_right, roles):
        """
        Makes sure we show the correct mapping data on the window.
        Receiver for ``self._mappings_table_model``'s dataChanged signal

        Args:
            top_left (QModelIndex): top index of modified mappings
            bottom_right (QModelIndex): bottom index of modified mappings
            roles (list of int):
        """
        if Qt.ItemDataRole.DisplayRole in roles:
            self._sort_mappings_table_model.invalidate()
        if max(roles) < Qt.ItemDataRole.UserRole:
            return
        sorted_index = self._sort_mappings_table_model.mapFromSource(top_left)
        if sorted_index != self._ui.mappings_table.currentIndex():
            self._ui.mappings_table.selectionModel().setCurrentIndex(sorted_index, QItemSelectionModel.ClearAndSelect)
            return
        enable_controls = False
        if MappingsTableModel.MAPPING_ROOT_ROLE in roles:
            root_mapping = top_left.data(MappingsTableModel.MAPPING_ROOT_ROLE)
            self._mapping_editor_model.set_mapping(top_left.data(Qt.ItemDataRole.DisplayRole), root_mapping)
            self._set_entity_dimensions_silently(top_left.data(MappingsTableModel.ENTITY_DIMENSIONS_ROLE))
            self._set_parameter_dimensions_silently(top_left.data(MappingsTableModel.PARAMETER_DIMENSIONS_ROLE))
            enable_controls = True
        if MappingsTableModel.MAPPING_TYPE_ROLE in roles:
            mapping_type = MappingType(top_left.data(MappingsTableModel.MAPPING_TYPE_ROLE))
            self._set_mapping_type_silently(mapping_type_to_combo_box_label[mapping_type])
            self._set_parameter_type_silently(mapping_type_to_parameter_type_label[mapping_type])
            enable_controls = True
        if MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE in roles:
            self._set_always_export_header_silently(top_left.data(MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE))
        if MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE in roles:
            self._set_use_fixed_table_name_flag_silently(
                top_left.data(MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)
            )
        if {MappingsTableModel.MAPPING_ROOT_ROLE, MappingsTableModel.FIXED_TABLE_NAME_ROLE} & set(roles):
            self._set_fixed_table_name_silently(top_left.data(MappingsTableModel.FIXED_TABLE_NAME_ROLE))
        if MappingsTableModel.GROUP_FN_ROLE in roles:
            self._set_group_fn_silently(
                group_function_display_from_name(top_left.data(MappingsTableModel.GROUP_FN_ROLE))
            )
        if MappingsTableModel.HIGHLIGHT_POSITION_ROLE in roles:
            self._set_highlight_dimension_silently(top_left.data(MappingsTableModel.HIGHLIGHT_POSITION_ROLE))
        if enable_controls:
            self._enable_entity_controls()
            self._enable_parameter_controls()

    @Slot(QPoint)
    def _show_mappings_table_context_menu(self, position):
        """Shows Mappings table context menu.

        Args:
            position (QPoint): requested menu position
        """
        self._mappings_table_menu.exec(self._ui.mappings_table.mapToGlobal(position))

    def _make_mappings_table_menu(self):
        """Creates context menu for Mappings table.

        Returns:
            QMenu: context menu
        """
        menu = QMenu(self)
        menu.addAction(self._add_mapping_action)
        menu.addAction(self._copy_mappings_action)
        menu.addAction(self._paste_mappings_action)
        menu.addAction(self._duplicate_mappings_action)
        menu.addAction(self._remove_mapping_action)
        return menu

    @Slot(bool)
    def _new_mapping(self, _=True):
        """Pushes an add mapping command to the undo stack."""
        type_ = MappingType.entities
        mapping_specification = _new_mapping_specification(type_)
        self._undo_stack.push(NewMapping(self._mappings_table_model, mapping_specification))
        self._sort_mappings_table_model.invalidate()

    @Slot(QModelIndex, int, int)
    def _select_inserted_row(self, parent_index, first_row, last_row):
        """
        Selects newly inserted mapping.

        Args:
            parent_index (QModelIndex): ignored
            first_row (int): index of first inserted row
            last_row (int): index of last inserted row
        """
        index = self._sort_mappings_table_model.index(first_row, 0)
        self._ui.mappings_table.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)
        self._enable_mapping_specification_editing()

    @Slot()
    def _delete_mapping(self):
        """Pushes remove mapping commands for selected mappings to undo stack."""
        selection_model = self._ui.mappings_table.selectionModel()
        if not selection_model.hasSelection():
            return
        indexes = [
            self._sort_mappings_table_model.mapToSource(index)
            for index in selection_model.selectedIndexes()
            if index.column() == 0
        ]
        if len(indexes) == 1:
            row = indexes[0].row()
            self._undo_stack.push(RemoveMapping(row, self._mappings_table_model))
        else:
            self._undo_stack.beginMacro("remove mappings")
            names = [index.data() for index in indexes]
            for name in names:
                row = self._mappings_table_model.index_of(name).row()
                self._undo_stack.push(RemoveMapping(row, self._mappings_table_model))
            self._undo_stack.endMacro()

    @Slot(bool)
    def _copy_mappings_to_clipboard(self, checked):
        """Copies selected mappings to system clipboard.

        Args:
            checked (bool): unused
        """
        selection_model = self._ui.mappings_table.selectionModel()
        indices = [self._sort_mappings_table_model.mapToSource(i) for i in selection_model.selectedIndexes()]
        if not indices:
            return
        specifications = []
        for index in indices:
            if index.column() != 0:
                continue
            specification = self._mappings_table_model.data(index, MappingsTableModel.MAPPING_SPECIFICATION_ROLE)
            serialized = specification.to_dict()
            serialized["name"] = self._mappings_table_model.data(index)
            specifications.append(serialized)
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setData(_MAPPINGS_MIME_TYPE, bytes(json.dumps(specifications), "utf-8"))
        clipboard.setMimeData(mime_data)

    @Slot(bool)
    def _paste_mappings_from_clipboard(self, checked):
        """Pastes mappings from system clipboard.

        Args:
            checked (bool): unused
        """
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if not mime_data.hasFormat(_MAPPINGS_MIME_TYPE):
            return
        serialized = json.loads(str(mime_data.data(_MAPPINGS_MIME_TYPE), "utf-8"))
        names = [d.pop("name") for d in serialized]
        mappings = [MappingSpecification.from_dict(d) for d in serialized]
        command_text = "paste mapping" + ("s" if len(mappings) > 1 else "")
        self._undo_stack.beginMacro(command_text)
        for mapping, name in zip(mappings, names):
            self._undo_stack.push(NewMapping(self._mappings_table_model, mapping, name))
        self._undo_stack.endMacro()

    @Slot(bool)
    def _duplicate_mappings(self, checked):
        """Duplicates selected mappings.

        Args:
            checked (bool): unused
        """
        selection_model = self._ui.mappings_table.selectionModel()
        indices = [self._sort_mappings_table_model.mapToSource(i) for i in selection_model.selectedIndexes()]
        if not indices:
            return
        specifications = []
        names = []
        for index in indices:
            if index.column() != 0:
                continue
            specification = self._mappings_table_model.data(index, MappingsTableModel.MAPPING_SPECIFICATION_ROLE)
            specifications.append(deepcopy(specification))
            names.append(self._mappings_table_model.data(index))
        text = "duplicate mapping" + ("s" if len(specifications) > 1 else "")
        self._undo_stack.beginMacro(text)
        for name, specification in zip(names, specifications):
            self._undo_stack.push(NewMapping(self._mappings_table_model, specification, name))
        self._undo_stack.endMacro()

    @Slot()
    def _toggle_all_enabled(self):
        """Pushes a command that enables or disables all mappings to undo stack."""
        for row in range(self._mappings_table_model.rowCount()):
            if (
                self._mappings_table_model.index(row, 0).data(Qt.ItemDataRole.CheckStateRole)
                == Qt.CheckState.Unchecked.value
            ):
                self._undo_stack.push(EnableAllMappings(self._mappings_table_model))
                return
        self._undo_stack.push(DisableAllMappings(self._mappings_table_model))

    @Slot()
    def _write_earlier(self):
        """Pushes a command that modifies mapping's write order."""
        index = self._ui.mappings_table.selectionModel().currentIndex()
        row = self._sort_mappings_table_model.mapToSource(index).row()
        if row == 0:
            return
        self._undo_stack.push(ChangeWriteOrder(row, True, self._mappings_table_model))

    @Slot()
    def _write_later(self):
        """Pushes a command that modifies mapping's write order."""
        index = self._ui.mappings_table.selectionModel().currentIndex()
        row = self._sort_mappings_table_model.mapToSource(index).row()
        if row == self._mappings_table_model.rowCount() - 1:
            return
        self._undo_stack.push(ChangeWriteOrder(row, False, self._mappings_table_model))

    @Slot(QModelIndex, int, int)
    def _check_for_empty_mappings_list(self, parent_index, first_row, last_row):
        """
        Checks if mappings list has become empty and disables controls accordingly.

        Args:
            parent_index (QModelIndex): ignored
            first_row (int): first removed row
            last_row (int): last removed row
        """
        self._enable_mapping_specification_editing()

    @Slot(int, str)
    def _rename_mapping(self, row, new_name):
        """
        Pushes a ``RenameMapping`` command to undo stack.

        Args:
            row (int): row index in mapping list model
            new_name (str): mapping's new name
        """
        self._undo_stack.push(RenameMapping(row, self._mappings_table_model, new_name))
        self._sort_mappings_table_model.invalidate()

    @Slot(int)
    def _set_mapping_enabled(self, row):
        """
        Pushes a ``SetMappingEnabled`` command to undo stack.

        Args:
            row (int): row index in mapping list model
        """
        self._undo_stack.push(SetMappingEnabled(row, self._mappings_table_model))

    @Slot(bool)
    def _enable_disable_all_mappings(self, enabled):
        """
        Pushes a ``EnableAllMappings`` or ``DisableAllMappings`` command to undo stack.

        Args:
            enabled (bool): True to enable all mapping, False to disable
        """
        make_command = EnableAllMappings if enabled else DisableAllMappings
        self._undo_stack.push(make_command(self._mappings_table_model))

    @Slot(str)
    def _change_mapping_type(self, _):
        """
        Pushes ``SetMappingType`` command to undo stack.

        Args:
            _ (str): ignored
        """
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        if not index.isValid():
            return
        type_label = self._ui.item_type_combo_box.currentText()
        parameter_type_label = self._ui.parameter_type_combo_box.currentText()
        if type_label == "Entity class":
            if parameter_type_label == "None":
                mapping_type = MappingType.entities
            elif parameter_type_label == "Value":
                mapping_type = MappingType.entity_parameter_values
            else:
                mapping_type = MappingType.entity_parameter_default_values
        elif type_label == "Entity class with dimension parameter":
            if parameter_type_label == "Default value":
                mapping_type = MappingType.entity_dimension_parameter_default_values
            else:
                mapping_type = MappingType.entity_dimension_parameter_values
        elif type_label == "Entity group":
            mapping_type = MappingType.entity_groups
        else:
            mapping_type = {
                "Alternative": MappingType.alternatives,
                "Scenario": MappingType.scenarios,
                "Scenario alternative": MappingType.scenario_alternatives,
                "Parameter value list": MappingType.parameter_value_lists,
            }[type_label]
        mapping_specification = _new_mapping_specification(mapping_type)
        if self._ui.fix_table_name_check_box.isChecked():
            mapping_specification.root = _add_fixed_table_name(mapping_specification.root)
            mapping_specification.root.value = self._ui.fix_table_name_line_edit.text()
        self._undo_stack.beginMacro("change mapping type")
        self._undo_stack.push(SetMappingType(index, mapping_type))
        self._undo_stack.push(SetMapping(index, mapping_specification.root))
        self._undo_stack.endMacro()

    def _set_mapping_type_silently(self, type_name):
        """
        Changes mapping type in the combo box without any other side effects.

        Args:
            type_name (str): mapping's type
        """
        if type_name == self._ui.item_type_combo_box.currentText():
            return
        self._ui.item_type_combo_box.currentTextChanged.disconnect(self._change_mapping_type)
        self._ui.item_type_combo_box.setCurrentText(type_name)
        self._ui.item_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._enable_entity_controls()
        self._enable_parameter_controls()

    def _set_parameter_type_silently(self, type_name):
        """
        Changes parameter type in the combo box without any side effects.

        Args:
            type_name (str): parameter type
        """
        if type_name == self._ui.parameter_type_combo_box.currentText():
            return
        self._ui.parameter_type_combo_box.currentTextChanged.disconnect(self._change_mapping_type)
        self._ui.parameter_type_combo_box.setCurrentText(type_name)
        self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._enable_parameter_controls()

    @Slot(int)
    def _change_always_export_header(self, checked):
        """Pushes corresponding command to undo stack.

        Args:
            checked (int): checked state
        """
        index = self._ui.mappings_table.currentIndex()
        self._undo_stack.push(SetAlwaysExportHeader(index, checked == Qt.CheckState.Checked.value))

    def _set_always_export_header_silently(self, always_export_header):
        """
        Changes the always export header check box  without any side effects.

        Args:
            always_export_header (bool): True to check the box, false otherwise
        """
        if always_export_header == self._ui.always_export_header_check_box.isChecked():
            return
        self._ui.always_export_header_check_box.stateChanged.disconnect(self._change_always_export_header)
        self._ui.always_export_header_check_box.setCheckState(
            Qt.CheckState.Checked if always_export_header else Qt.CheckState.Unchecked
        )
        self._ui.always_export_header_check_box.stateChanged.connect(self._change_always_export_header)

    def _change_parameter_dimensions(self, dimensions):
        """
        Pushes a command to undo stack.

        Args:
            dimensions (int): parameter dimensions
        """
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        mapping = self._mappings_table_model.data(index, MappingsTableModel.MAPPING_ROOT_ROLE)
        modified = deepcopy(mapping)
        if self._mappings_table_model.data(index, MappingsTableModel.MAPPING_TYPE_ROLE) in (
            MappingType.entity_parameter_values.value,
            MappingType.entity_dimension_parameter_values.value,
        ):
            set_parameter_dimensions(modified, dimensions)
        else:
            set_parameter_default_value_dimensions(modified, dimensions)
        self._undo_stack.beginMacro("change parameter dimensions")
        self._undo_stack.push(SetMapping(index, modified))
        self._undo_stack.endMacro()

    def _set_parameter_dimensions_silently(self, dimensions):
        """
        Sets parameter dimensions spin box without emitting signals.

        Args:
            dimensions (int): parameter dimensions
        """
        self._ui.parameter_dimensions_spin_box.valueChanged.disconnect(self._change_parameter_dimensions)
        self._ui.parameter_dimensions_spin_box.setValue(dimensions)
        self._ui.parameter_dimensions_spin_box.valueChanged.connect(self._change_parameter_dimensions)

    @Slot(int)
    def _change_fix_table_name_flag(self, checked):
        """
        Pushes commands to undo stack to change enable/disable fixed table name.

        Args:
            checked (int): check box state
        """
        index = self._ui.mappings_table.currentIndex()
        if not index.isValid():
            return
        flag = checked == Qt.CheckState.Checked.value
        self._undo_stack.beginMacro(("check" if flag else "uncheck") + " fix table name checkbox")
        self._undo_stack.push(SetUseFixedTableNameFlag(index, flag))
        mapping = index.data(MappingsTableModel.MAPPING_ROOT_ROLE)
        mapping = deepcopy(mapping)
        mapping = _add_fixed_table_name(mapping) if flag else _remove_fixed_table_name(mapping)
        self._undo_stack.push(SetMapping(index, mapping))
        self._undo_stack.endMacro()

    @Slot(str)
    def _change_fix_table_name(self, name):
        """
        Pushes commands to undo stack to change fixed table name to text in corresponding line edit.

        Args:
            name (str): fixed table name
        """
        index = self._ui.mappings_table.currentIndex()
        if not index.isValid():
            return
        old_name = index.data(MappingsTableModel.FIXED_TABLE_NAME_ROLE)
        self._undo_stack.push(SetFixedTableName(index, old_name, name))

    @Slot()
    def _finish_editing_fix_table_name(self):
        """Seals the latest undo command if it changed the fixed table name."""
        self._undo_stack.push(SealCommand(SetFixedTableName.ID))

    def _set_use_fixed_table_name_flag_silently(self, flag):
        """
        Changes the fixed table name check box without touching the undo stack.

        Args:
            flag (bool): True if the box should be checked, False otherwise
        """
        self._ui.fix_table_name_line_edit.setEnabled(flag)
        if flag == self._ui.fix_table_name_check_box.isChecked():
            return
        self._ui.fix_table_name_check_box.stateChanged.disconnect(self._change_fix_table_name_flag)
        self._ui.fix_table_name_check_box.setCheckState(Qt.CheckState.Checked if flag else Qt.CheckState.Unchecked)
        self._ui.fix_table_name_check_box.stateChanged.connect(self._change_fix_table_name_flag)

    def _set_fixed_table_name_silently(self, name):
        """
        Changes the fixed table name line edit without touching the undo stack.

        Args:
            name (str): text to go in the line edit
        """
        if name == self._ui.fix_table_name_line_edit.text():
            return
        self._ui.fix_table_name_line_edit.editingFinished.disconnect(self._finish_editing_fix_table_name)
        self._ui.fix_table_name_line_edit.setText(name)
        self._ui.fix_table_name_line_edit.editingFinished.connect(self._finish_editing_fix_table_name)

    @Slot(QModelIndex, QModelIndex, list)
    def _validate_fixed_table_name(self, top_left, bottom_right, roles):
        """Checks if any mapping position is set to Table name and disables fixed table name accordingly.

        Args:
            top_left (QModelIndex): top left of changed mapping table model index
            bottom_right (QModelIndex): bottom right of changed mapping table model index
            roles (list of int): model roles
        """
        if (
            Qt.ItemDataRole.DisplayRole not in roles
            or top_left.column() > EditorColumn.POSITION
            or bottom_right.column() < EditorColumn.POSITION
        ):
            return
        for row in range(top_left.row(), bottom_right.row() + 1):
            mapping_item = self._mapping_editor_model.index(row, EditorColumn.POSITION).data(
                MappingEditorTableModel.MAPPING_ITEM_ROLE
            )
            if mapping_item.position == Position.table_name:
                if self._ui.fix_table_name_check_box.isChecked():
                    index = self._ui.mappings_table.currentIndex()
                    mapping_root = index.data(MappingsTableModel.MAPPING_ROOT_ROLE)
                    mapping_root = deepcopy(mapping_root)
                    mapping_root = _remove_fixed_table_name(mapping_root)
                    command = ClearFixedTableName(
                        self,
                        self._ui.fix_table_name_check_box.isChecked(),
                        self._ui.fix_table_name_line_edit.text(),
                        index,
                        mapping_root,
                    )
                    self._undo_stack.push(command)
                else:
                    self._ui.fix_table_name_check_box.setEnabled(False)
                    self._ui.fix_table_name_line_edit.setEnabled(False)
                return
        for row in range(top_left.model().rowCount()):
            mapping_item = self._mapping_editor_model.index(row, EditorColumn.POSITION).data(
                MappingEditorTableModel.MAPPING_ITEM_ROLE
            )
            if mapping_item.position == Position.table_name:
                self._ui.fix_table_name_check_box.setEnabled(False)
                self._ui.fix_table_name_line_edit.setEnabled(False)
                return
        self._ui.fix_table_name_check_box.setEnabled(True)

    def clear_fixed_table_name(self):
        """Clears and disable fixed table name widgets."""
        self._set_fixed_table_name_silently("")
        self._set_use_fixed_table_name_flag_silently(False)
        self._ui.fix_table_name_check_box.setEnabled(False)

    def enable_fixed_table_name(self, checked, name):
        """Enables and sets fixed table name widgets.

        Args:
            checked (bool): fixed table name checkbox state
            name (str): fixed table name
        """
        self._set_use_fixed_table_name_flag_silently(checked)
        self._ui.fix_table_name_check_box.setEnabled(True)
        self._set_fixed_table_name_silently(name)
        self._ui.fix_table_name_line_edit.setEnabled(True)

    @Slot(str)
    def _change_root_mapping_group_fn(self, text):
        """
        Pushes commands to undo stack to change group function of root mapping.

        Args:
            text (str): combo box text
        """
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        if not index.isValid():
            return
        old = index.data(MappingsTableModel.GROUP_FN_ROLE)
        self._undo_stack.push(SetGroupFunction(index, old, group_function_name_from_display(text)))

    def _set_group_fn_silently(self, group_fn_display_name):
        """
        Sets group function in combo box without emitting signals.

        Args:
            group_fn_display_name (str): group function's display name
        """
        if group_fn_display_name != self._ui.group_fn_combo_box.currentText():
            self._ui.group_fn_combo_box.currentTextChanged.disconnect(self._change_root_mapping_group_fn)
            self._ui.group_fn_combo_box.setCurrentText(group_fn_display_name)
            self._ui.group_fn_combo_box.currentTextChanged.connect(self._change_root_mapping_group_fn)

    def _change_highlight_dimension(self, dimension):
        """Pushes a command to change highlight dimension to undo stack.

        Args:
            dimension (int): highlight dimension
        """
        if self._ui.item_type_combo_box.currentText() != "Entity class with dimension parameter":
            return
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        if not index.isValid():
            return
        old = index.data(MappingsTableModel.HIGHLIGHT_POSITION_ROLE)
        new = dimension - 1
        if old == new:
            return
        self._undo_stack.push(SetHighlightDimension(index, old, new))

    def _set_highlight_dimension_silently(self, highlight_dimension):
        """Sets highlight dimension without emitting signals.

        Args:
            highlight_dimension (int, optional): highlight dimension
        """
        self._ui.highlight_dimension_spin_box.valueChanged.disconnect(self._change_highlight_dimension)
        if highlight_dimension is not None:
            self._ui.highlight_dimension_spin_box.setValue(highlight_dimension + 1)
            self._ui.highlight_dimension_spin_box.setEnabled(True)
        else:
            self._ui.highlight_dimension_spin_box.setValue(1)
            self._ui.highlight_dimension_spin_box.setEnabled(False)
        self._ui.highlight_dimension_spin_box.valueChanged.connect(self._change_highlight_dimension)

    def _change_entity_dimensions(self, dimensions):
        """
        Pushes a command to undo stack.

        Args:
            dimensions (int): dimensions
        """
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        mapping = self._mappings_table_model.data(index, MappingsTableModel.MAPPING_ROOT_ROLE)
        modified = deepcopy(mapping)
        set_entity_dimensions(modified, dimensions)
        current_mapping_type = self._ui.item_type_combo_box.currentText()
        self._undo_stack.beginMacro("change entity dimensions")
        self._undo_stack.push(SetMapping(self._ui.mappings_table.currentIndex(), modified))
        if current_mapping_type == "Entity class with dimension parameter":
            highlight_dimension = self._mappings_table_model.data(index, MappingsTableModel.HIGHLIGHT_POSITION_ROLE)
            if highlight_dimension is None:
                self._undo_stack.push(SetHighlightDimension(index, highlight_dimension, 0))
            elif highlight_dimension >= dimensions:
                new_highlight_dimension = dimensions - 1 if dimensions > 0 else None
                self._undo_stack.push(SetHighlightDimension(index, highlight_dimension, new_highlight_dimension))
        self._undo_stack.endMacro()

    def _set_entity_dimensions_silently(self, dimensions):
        """
        Sets entity dimensions spin box without emitting signals.

        Args:
            dimensions (int): dimensions
        """
        self._ui.entity_dimensions_spin_box.valueChanged.disconnect(self._change_entity_dimensions)
        self._ui.entity_dimensions_spin_box.setValue(dimensions)
        self._ui.entity_dimensions_spin_box.valueChanged.connect(self._change_entity_dimensions)
        self._ui.highlight_dimension_spin_box.setMaximum(max(dimensions, 1))

    def _enable_mapping_specification_editing(self):
        """Enables and disables mapping specification editing controls."""
        have_mappings = self._mappings_table_model.rowCount() > 0
        self._ui.mapping_options_contents.setEnabled(have_mappings)
        self._ui.mapping_table_view.setEnabled(have_mappings)
        self._ui.remove_mapping_button.setEnabled(have_mappings)

    def _enable_entity_controls(self):
        """Enables and disables controls related to entity export."""
        current_mapping_type = self._ui.item_type_combo_box.currentText()
        self._ui.entity_dimensions_spin_box.setEnabled(current_mapping_type.startswith("Entity class"))
        self._ui.highlight_dimension_spin_box.setEnabled(
            current_mapping_type == "Entity class with dimension parameter"
        )

    def _enable_parameter_controls(self):
        """Enables and disables controls related to entity export."""
        mapping_type = self._ui.item_type_combo_box.currentText()
        types_with_parameters = {"Entity class", "Entity class with dimension parameter"}
        if mapping_type in types_with_parameters:
            self._ui.parameter_type_combo_box.setEnabled(True)
            self._ui.parameter_type_combo_box.currentTextChanged.disconnect(self._change_mapping_type)
            model = self._ui.parameter_type_combo_box.model()
            default_value_item = model.item(1)
            default_value_item.setFlags(default_value_item.flags() | Qt.ItemIsEnabled)
            no_value_item = model.item(2)
            if mapping_type == "Entity class with dimension parameter":
                no_value_item.setFlags(default_value_item.flags() & ~Qt.ItemIsEnabled)
            else:
                no_value_item.setFlags(default_value_item.flags() | Qt.ItemIsEnabled)
            self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
            self._ui.parameter_dimensions_spin_box.setEnabled(self._ui.parameter_type_combo_box.currentText() != "None")
        else:
            self._ui.parameter_type_combo_box.setEnabled(False)
            self._ui.parameter_dimensions_spin_box.setEnabled(False)

    @Slot()
    def _compact_mapping(self):
        """Pushes a CompactMapping command to the undo stack."""
        if not self._mapping_editor_model.can_compact():
            return
        row = self._ui.mappings_table.selectionModel().currentIndex().row()
        mapping_name = self._sort_mappings_table_model.mapToSource(self._sort_mappings_table_model.index(row, 0)).data()
        self._undo_stack.push(CompactMapping(self._mapping_editor_model, mapping_name))

    def tear_down(self):
        if not super().tear_down():
            return False
        self._preview_updater.tear_down()
        return True


def _new_mapping_specification(mapping_type):
    """
    Creates a new export mapping.

    Args:
        mapping_type (MappingType): mapping's type

    Returns:
        MappingSpecification: an export mapping specification
    """
    if mapping_type == MappingType.entities:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, entity_export(0, 1))
    if mapping_type == MappingType.entity_groups:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, entity_group_export(0, 1, 2))
    if mapping_type == MappingType.entity_parameter_default_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            NoGroup.NAME,
            False,
            entity_parameter_default_value_export(0, 1, Position.hidden, 2, None, None),
        )
    if mapping_type == MappingType.entity_parameter_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            NoGroup.NAME,
            False,
            entity_parameter_value_export(0, 2, Position.hidden, 1, None, None, 3, Position.hidden, 4, None, None),
        )
    if mapping_type == MappingType.parameter_value_lists:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, parameter_value_list_export(0, 1))
    if mapping_type == MappingType.entity_dimension_parameter_default_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            NoGroup.NAME,
            False,
            entity_dimension_parameter_default_value_export(0, 1, None, Position.hidden, 2, None, None, 0),
        )
    if mapping_type == MappingType.entity_dimension_parameter_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            NoGroup.NAME,
            False,
            entity_dimension_parameter_value_export(
                0, 3, Position.hidden, Position.hidden, [1], [2], 4, Position.hidden, 5, None, None, 0
            ),
        )
    if mapping_type == MappingType.alternatives:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, alternative_export(0))
    if mapping_type == MappingType.scenario_alternatives:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, scenario_alternative_export(0, 1))
    if mapping_type == MappingType.scenarios:
        return MappingSpecification(mapping_type, True, True, NoGroup.NAME, False, scenario_export(0, 1))
    raise NotImplementedError()


def _add_fixed_table_name(mapping_root):
    """
    Adds a fixed table name to given mapping.

    Args:
        mapping_root (Mapping): a root mapping

    Returns:
        Mapping: new mapping hierarchy
    """
    for mapping in mapping_root.flatten():
        if mapping.position == Position.table_name:
            mapping.position = Position.hidden
    new_root = FixedValueMapping(Position.table_name, "table")
    new_root.child = mapping_root
    return new_root


def _remove_fixed_table_name(mapping_root):
    """
    Removes fixed table name from mapping.

    Args:
        mapping_root (Mapping): a root mapping

    Returns:
        Mapping: new mapping hierarchy
    """
    return unflatten(mapping_root.flatten()[1:])
