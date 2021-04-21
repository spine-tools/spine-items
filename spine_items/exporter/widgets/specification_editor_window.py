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
Contains :class:`SpecificationEditorWindow`.

:author: A. Soininen (VTT)
:date:   11.12.2020
"""
from copy import deepcopy
from PySide2.QtCore import QItemSelectionModel, QModelIndex, QSortFilterProxyModel, Qt, Signal, Slot
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QAction, QHeaderView, QMainWindow, QMessageBox, QUndoStack
from spinedb_api.export_mapping import (
    alternative_export,
    feature_export,
    object_export,
    object_group_export,
    object_group_parameter_export,
    object_parameter_default_value_export,
    object_parameter_export,
    parameter_value_list_export,
    relationship_export,
    relationship_parameter_default_value_export,
    relationship_parameter_export,
    scenario_alternative_export,
    scenario_export,
    tool_export,
    tool_feature_export,
    tool_feature_method_export,
)
from spinedb_api.export_mapping.settings import (
    set_parameter_dimensions,
    set_parameter_default_value_dimensions,
    set_relationship_dimensions,
)
from spinedb_api.export_mapping.export_mapping import FixedValueMapping, Position
from spinedb_api.export_mapping.group_functions import (
    GROUP_FUNCTION_DISPLAY_NAMES,
    group_function_name_from_display,
    group_function_display_from_name,
)
from spinetoolbox.widgets.notification import ChangeNotifier
from ...commands import RenameMapping
from ...widgets import prompt_to_save_changes, restore_ui, save_ui, SpecNameDescriptionToolbar
from .preview_updater import PreviewUpdater
from ..commands import (
    ChangeWriteOrder,
    CompactMapping,
    DisableAllMappings,
    EnableAllMappings,
    NewMapping,
    RemoveMapping,
    SetAlwaysExportHeader,
    SetMappingEnabled,
    SetMappingType,
    SetExportFormat,
    SetMapping,
    SetUseFixedTableNameFlag,
)
from ..mvcmodels.mappings_table_model import MappingsTableModel
from ..mvcmodels.mapping_editor_table_model import EditorColumn, MappingEditorTableModel
from ..specification import MappingSpecification, MappingType, OutputFormat, Specification
from .filter_edit_delegate import FilterEditDelegate
from .position_edit_delegate import PositionEditDelegate, position_section_width


mapping_type_to_combo_box_label = {
    MappingType.alternatives: "Alternative",
    MappingType.features: "Feature",
    MappingType.objects: "Object class",
    MappingType.object_groups: "Object group",
    MappingType.object_group_parameter_values: "Object group",
    MappingType.object_parameter_default_values: "Object class",
    MappingType.object_parameter_values: "Object class",
    MappingType.parameter_value_lists: "Parameter value list",
    MappingType.relationships: "Relationship class",
    MappingType.relationship_parameter_default_values: "Relationship class",
    MappingType.relationship_parameter_values: "Relationship class",
    MappingType.scenario_alternatives: "Scenario alternative",
    MappingType.scenarios: "Scenario",
    MappingType.tool_feature_methods: "Tool feature method",
    MappingType.tool_features: "Tool feature",
    MappingType.tools: "Tool",
}

mapping_type_to_parameter_type_label = {
    MappingType.alternatives: "None",
    MappingType.features: "None",
    MappingType.objects: "None",
    MappingType.object_groups: "None",
    MappingType.object_group_parameter_values: "Value",
    MappingType.object_parameter_default_values: "Default value",
    MappingType.object_parameter_values: "Value",
    MappingType.parameter_value_lists: "None",
    MappingType.relationships: "None",
    MappingType.relationship_parameter_default_values: "Default value",
    MappingType.relationship_parameter_values: "Value",
    MappingType.scenario_alternatives: "None",
    MappingType.scenarios: "None",
    MappingType.tool_feature_methods: "None",
    MappingType.tool_features: "None",
    MappingType.tools: "None",
}


class SpecificationEditorWindow(QMainWindow):
    """Interface to edit exporter specifications."""

    current_mapping_about_to_change = Signal()
    current_mapping_changed = Signal()

    _APP_SETTINGS_GROUP = "exportSpecificationEditorWindow"

    def __init__(self, toolbox, specification=None, item=None, url_model=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (ProjectItemSpecification, optional): exporter specification
            item (ProjectItem, optional): invoking project item, if window was opened from its properties tab
            url_model (QAbstractListModel): model that provides URLs of connected databases
        """
        super().__init__(parent=toolbox)
        self.specification = specification
        self.item = item
        self._toolbox = toolbox
        self._original_spec_name = None if specification is None else specification.name
        self._new_spec = deepcopy(specification) if specification is not None else Specification()
        self._undo_stack = QUndoStack(self)
        self._change_notifier = ChangeNotifier(self, self._undo_stack, toolbox.qsettings(), "appSettings/specShowUndo")
        self._undo_action = self._undo_stack.createUndoAction(self)
        self._undo_action.setShortcut(QKeySequence.Undo)
        self.addAction(self._undo_action)
        self._redo_action = self._undo_stack.createRedoAction(self)
        self._redo_action.setShortcut(QKeySequence.Redo)
        self.addAction(self._redo_action)
        self._activated_mapping_name = None
        self._mappings_table_model = MappingsTableModel(self._new_spec.mapping_specifications(), self)
        self._mappings_table_model.dataChanged.connect(self._update_ui_after_mapping_change)
        self._mappings_table_model.rename_requested.connect(self._rename_mapping)
        self._mappings_table_model.mapping_enabled_state_change_requested.connect(self._set_mapping_enabled)
        self._mappings_table_model.set_all_mappings_enabled_requested.connect(self._enable_disable_all_mappings)
        self._mappings_table_model.write_order_about_to_change.connect(
            lambda: self._expect_current_mapping_change(True)
        )
        self._mappings_table_model.write_order_changed.connect(lambda: self._expect_current_mapping_change(False))
        self._mapping_editor_model = MappingEditorTableModel("", None, self._undo_stack, self, self)
        self._sort_mappings_table_model = QSortFilterProxyModel(self)
        self._sort_mappings_table_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._sort_mappings_table_model.setSourceModel(self._mappings_table_model)
        self._sort_mappings_table_model.rowsInserted.connect(self._select_inserted_row)
        self._sort_mappings_table_model.rowsRemoved.connect(self._check_for_empty_mappings_list)

        from ..ui.specification_editor import Ui_MainWindow

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self.setWindowTitle(specification.name if specification else "")
        central_widget = self.takeCentralWidget()
        central_widget.deleteLater()
        self._specification_toolbar = SpecNameDescriptionToolbar(self, self._new_spec, self._undo_stack)
        self.addToolBar(Qt.TopToolBarArea, self._specification_toolbar)
        self._populate_toolbar_menu()
        self._apply_default_dock_layout()
        restore_ui(self, self._toolbox.qsettings(), self._APP_SETTINGS_GROUP)
        self._ui.export_format_combo_box.addItems([format.value for format in OutputFormat])
        self._ui.export_format_combo_box.setCurrentText(self._new_spec.output_format.value)
        self._ui.export_format_combo_box.currentTextChanged.connect(self._change_format)
        self._add_mapping_action = QAction("Add Mapping", self)
        self._add_mapping_action.triggered.connect(self._new_mapping)
        self._ui.add_mapping_button.clicked.connect(self._add_mapping_action.trigger)
        self._remove_mapping_action = QAction("Remove mappings", self)
        self._remove_mapping_action.setShortcut(QKeySequence(QKeySequence.Delete))
        self._remove_mapping_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._remove_mapping_action.triggered.connect(self._delete_mapping)
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
        self._ui.mappings_table.addAction(self._add_mapping_action)
        self._ui.mappings_table.addAction(self._remove_mapping_action)
        self._ui.mappings_table.setModel(self._sort_mappings_table_model)
        self._ui.mappings_table.setSortingEnabled(True)
        self._ui.mappings_table.sortByColumn(0, Qt.AscendingOrder)
        self._expect_current_mapping_change(False)
        self._ui.mappings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._ui.group_fn_combo_box.addItems(GROUP_FUNCTION_DISPLAY_NAMES)
        self._ui.item_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._ui.parameter_type_combo_box.currentTextChanged.connect(self._change_mapping_type)
        self._ui.parameter_dimensions_spin_box.valueChanged.connect(self._change_parameter_dimensions)
        self._ui.always_export_header_check_box.stateChanged.connect(self._change_always_export_header)
        self._ui.relationship_dimensions_spin_box.valueChanged.connect(self._change_relationship_dimensions)
        self._ui.fix_table_name_check_box.stateChanged.connect(self._change_fix_table_name_flag)
        self._ui.group_fn_combo_box.currentTextChanged.connect(self._change_root_mapping_group_fn)
        self._compact_mapping_action = QAction("Compact mapping", self)
        self._compact_mapping_action.triggered.connect(self._compact_mapping)
        self._ui.compact_button.clicked.connect(self._compact_mapping_action.trigger)
        self._ui.mapping_table_view.setModel(self._mapping_editor_model)
        self._position_edit_delegate = PositionEditDelegate(self)
        self._ui.mapping_table_view.setItemDelegateForColumn(1, self._position_edit_delegate)
        self._filter_edit_delegate = FilterEditDelegate(self)
        self._ui.mapping_table_view.setItemDelegateForColumn(4, self._filter_edit_delegate)
        table_header = self._ui.mapping_table_view.horizontalHeader()
        table_header.setSectionResizeMode(EditorColumn.ROW_LABEL, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(EditorColumn.POSITION, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(EditorColumn.PIVOTED, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(EditorColumn.NULLABLE, QHeaderView.ResizeToContents)
        table_header.setSectionResizeMode(EditorColumn.HEADER, QHeaderView.ResizeToContents)
        table_header.setMinimumSectionSize(position_section_width())
        self._enable_mapping_specification_editing()
        self._specification_toolbar.save_action.triggered.connect(self._save)
        self._specification_toolbar.close_action.triggered.connect(self.close)
        if specification is None:
            self._mappings_table_model.extend(_new_mapping_specification(MappingType.objects))
        self._undo_stack.cleanChanged.connect(self._update_window_modified)
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

    @Slot(bool)
    def _update_window_modified(self, clean):
        self.setWindowModified(not clean)
        self._specification_toolbar.save_action.setEnabled(not clean)
        self.windowTitleChanged.emit(self.windowTitle())

    def _restore_dock_widgets(self):
        """Docks all floating and or hidden QDockWidgets back to the window."""
        docks = {
            Qt.LeftDockWidgetArea: (
                self._ui.export_options_dock,
                self._ui.mappings_dock,
                self._ui.mapping_options_dock,
                self._ui.mapping_spec_dock,
            ),
            Qt.RightDockWidgetArea: (
                self._ui.preview_tables_dock,
                self._ui.preview_contents_dock,
                self._ui.preview_controls_dock,
            ),
        }
        for area, area_docks in docks.items():
            for dock in area_docks:
                dock.setVisible(True)
                dock.setFloating(False)
                self.addDockWidget(area, dock)

    def _apply_default_dock_layout(self):
        """Applies default layout for dock windows."""
        size = self.size()
        self._restore_dock_widgets()
        # Left side
        self.splitDockWidget(self._ui.export_options_dock, self._ui.mappings_dock, Qt.Vertical)
        self.splitDockWidget(self._ui.mappings_dock, self._ui.mapping_spec_dock, Qt.Vertical)
        some_docks = (self._ui.mappings_dock, self._ui.mapping_options_dock, self._ui.mapping_spec_dock)
        height = sum(d.height() for d in some_docks)
        self.resizeDocks(some_docks, [height * x for x in (0.1, 0.3, 0.6)], Qt.Vertical)
        self.splitDockWidget(self._ui.mappings_dock, self._ui.mapping_options_dock, Qt.Horizontal)
        # Right side
        some_docks = (self._ui.preview_tables_dock, self._ui.preview_controls_dock)
        self.splitDockWidget(*some_docks, Qt.Vertical)
        height = sum(d.height() for d in some_docks)
        self.resizeDocks(some_docks, [height * x for x in (0.9, 0.1)], Qt.Vertical)
        some_docks = (self._ui.preview_tables_dock, self._ui.preview_contents_dock)
        self.splitDockWidget(*some_docks, Qt.Horizontal)
        width = sum(d.width() for d in some_docks)
        self.resizeDocks(some_docks, [width * x for x in (0.3, 0.7)], Qt.Horizontal)

        qApp.processEvents()  # pylint: disable=undefined-variable
        self.resize(size)

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
            self._ui.mapping_spec_contents.setEnabled(False)
            return
        self.current_mapping_about_to_change.emit()
        current = self._sort_mappings_table_model.mapToSource(current)
        mapping_type = current.data(MappingsTableModel.MAPPING_TYPE_ROLE)
        self._set_mapping_type_silently(mapping_type_to_combo_box_label[mapping_type])
        self._set_parameter_type_silently(mapping_type_to_parameter_type_label[mapping_type])
        self._set_always_export_header_silently(current.data(MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE))
        if mapping_type in (
            MappingType.relationships,
            MappingType.relationship_parameter_values,
            MappingType.relationship_parameter_default_values,
        ):
            self._set_relationship_dimensions_silently(current.data(MappingsTableModel.RELATIONSHIP_DIMENSIONS_ROLE))
        else:
            self._set_relationship_dimensions_silently(1)
        if mapping_type in (
            MappingType.object_parameter_values,
            MappingType.object_parameter_default_values,
            MappingType.relationship_parameter_values,
            MappingType.relationship_parameter_default_values,
        ):
            self._set_parameter_dimensions_silently(current.data(MappingsTableModel.PARAMETER_DIMENSIONS_ROLE))
        else:
            self._set_parameter_dimensions_silently(0)
        self._set_use_fixed_table_name_flag_silently(current.data(MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE))
        root_mapping = current.data(MappingsTableModel.MAPPING_ROOT_ROLE)
        self._set_root_mapping_group_fn_silently(group_function_display_from_name(root_mapping.group_fn))
        mapping_name = self._mappings_table_model.index(current.row(), 0).data()
        self._mapping_editor_model.set_mapping(mapping_name, root_mapping)
        self._enable_relationship_controls()
        self._enable_parameter_controls()
        self._ui.mapping_spec_contents.setEnabled(True)
        self.current_mapping_changed.emit()

    def _expect_current_mapping_change(self, expect_change):
        """Connects and disconnects signals depending of if current mapping is expected to change or not

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

        Args:
            top_left (QModelIndex): top index of modified mappings
            bottom_right (QModelIndex): bottom index of modified mappings
            roles (list of int):
        """
        if Qt.DisplayRole in roles:
            self._sort_mappings_table_model.invalidate()
        if max(roles) < Qt.UserRole:
            return
        sorted_index = self._sort_mappings_table_model.mapFromSource(top_left)
        if sorted_index != self._ui.mappings_table.currentIndex():
            self._ui.mappings_table.selectionModel().setCurrentIndex(sorted_index, QItemSelectionModel.ClearAndSelect)
            return
        if MappingsTableModel.MAPPING_ROOT_ROLE in roles:
            root_mapping = top_left.data(MappingsTableModel.MAPPING_ROOT_ROLE)
            self._mapping_editor_model.set_mapping(top_left.data(Qt.DisplayRole), root_mapping)
            self._set_relationship_dimensions_silently(top_left.data(MappingsTableModel.RELATIONSHIP_DIMENSIONS_ROLE))
            self._set_parameter_dimensions_silently(top_left.data(MappingsTableModel.PARAMETER_DIMENSIONS_ROLE))
            self._set_root_mapping_group_fn_silently(group_function_display_from_name(root_mapping.group_fn))
        if MappingsTableModel.MAPPING_TYPE_ROLE in roles:
            mapping_type = top_left.data(MappingsTableModel.MAPPING_TYPE_ROLE)
            self._set_mapping_type_silently(mapping_type_to_combo_box_label[mapping_type])
            self._set_parameter_type_silently(mapping_type_to_parameter_type_label[mapping_type])
        if MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE in roles:
            self._set_always_export_header_silently(top_left.data(MappingsTableModel.ALWAYS_EXPORT_HEADER_ROLE))
        if MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE in roles:
            self._set_use_fixed_table_name_flag_silently(
                top_left.data(MappingsTableModel.USE_FIXED_TABLE_NAME_FLAG_ROLE)
            )
        self._enable_relationship_controls()
        self._enable_parameter_controls()

    @Slot(bool)
    def _new_mapping(self, _=True):
        """Pushes an add mapping command to the undo stack."""
        type_ = MappingType.objects
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

    @Slot()
    def _toggle_all_enabled(self):
        """Pushes a command that enables or disables all mappings to undo stack."""
        for row in range(self._mappings_table_model.rowCount()):
            if self._mappings_table_model.index(row, 0).data(Qt.CheckStateRole) == Qt.Unchecked:
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
        row = self._sort_mappings_table_model.mapToSource(self._sort_mappings_table_model.index(row, 0)).row()
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
        if type_label == "Object class":
            if parameter_type_label == "None":
                mapping_type = MappingType.objects
            elif parameter_type_label == "Value":
                mapping_type = MappingType.object_parameter_values
            else:
                mapping_type = MappingType.object_parameter_default_values
        elif type_label == "Relationship class":
            if parameter_type_label == "None":
                mapping_type = MappingType.relationships
            elif parameter_type_label == "Value":
                mapping_type = MappingType.relationship_parameter_values
            else:
                mapping_type = MappingType.relationship_parameter_default_values
        elif type_label == "Object group":
            if parameter_type_label == "None":
                mapping_type = MappingType.object_groups
            else:
                mapping_type = MappingType.object_group_parameter_values
        else:
            mapping_type = {
                "Alternative": MappingType.alternatives,
                "Scenario": MappingType.scenarios,
                "Scenario alternative": MappingType.scenario_alternatives,
                "Parameter value list": MappingType.parameter_value_lists,
                "Feature": MappingType.features,
                "Tool": MappingType.tools,
                "Tool feature": MappingType.tool_features,
                "Tool feature method": MappingType.tool_feature_methods,
            }[type_label]
        mapping_specification = _new_mapping_specification(mapping_type)
        if self._ui.fix_table_name_check_box.isChecked():
            mapping_specification.root = _add_fixed_table_name(mapping_specification.root)
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
        self._enable_relationship_controls()
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
        self._undo_stack.push(SetAlwaysExportHeader(index, checked == Qt.Checked))

    def _set_always_export_header_silently(self, always_export_header):
        """
        Changes the always export header check box  without any side effects.

        Args:
            always_export_header (bool): True to check the box, false otherwise
        """
        if always_export_header == self._ui.always_export_header_check_box.isChecked():
            return
        self._ui.always_export_header_check_box.stateChanged.disconnect(self._change_always_export_header)
        self._ui.always_export_header_check_box.setCheckState(Qt.Checked if always_export_header else Qt.Unchecked)
        self._ui.always_export_header_check_box.stateChanged.connect(self._change_always_export_header)

    @Slot(int)
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
            MappingType.object_parameter_values,
            MappingType.relationship_parameter_values,
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
        Pushes commands to undo stack to to change enable/disable fixed table name.

        Args:
            checked (int): check box state
        """
        index = self._ui.mappings_table.currentIndex()
        if not index.isValid():
            return
        flag = checked == Qt.Checked
        self._undo_stack.beginMacro(("check" if flag else "uncheck") + " fix table name checkbox")
        self._undo_stack.push(SetUseFixedTableNameFlag(index, flag))
        mapping = index.data(MappingsTableModel.MAPPING_ROOT_ROLE)
        mapping = deepcopy(mapping)
        mapping = _add_fixed_table_name(mapping) if flag else _remove_fixed_table_name(mapping)
        self._undo_stack.push(SetMapping(index, mapping))
        self._undo_stack.endMacro()

    def _set_use_fixed_table_name_flag_silently(self, flag):
        """
        Changes the fixed table name check box without touching the undo stack.

        Args:
            flag (bool): True if the box should be checked, False otherwise
        """
        if flag == self._ui.fix_table_name_check_box.isChecked():
            return
        self._ui.fix_table_name_check_box.stateChanged.disconnect(self._change_fix_table_name_flag)
        self._ui.fix_table_name_check_box.setCheckState(Qt.Checked if flag else Qt.Unchecked)
        self._ui.fix_table_name_check_box.stateChanged.connect(self._change_fix_table_name_flag)

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
        self._undo_stack.beginMacro("change mapping's group function")
        mapping = index.data(MappingsTableModel.MAPPING_ROOT_ROLE)
        mapping = deepcopy(mapping)
        mapping.group_fn = group_function_name_from_display(text)
        self._undo_stack.push(SetMapping(index, mapping))
        self._undo_stack.endMacro()

    def _set_root_mapping_group_fn_silently(self, group_fn):
        """
        Sets group function in combo box without emitting signals.

        Args:
            group_fn (str): group function name
        """
        if group_fn != self._ui.group_fn_combo_box.currentText():
            self._ui.group_fn_combo_box.currentTextChanged.disconnect(self._change_root_mapping_group_fn)
            self._ui.group_fn_combo_box.setCurrentText(group_fn)
            self._ui.group_fn_combo_box.currentTextChanged.connect(self._change_root_mapping_group_fn)

    @Slot(int)
    def _change_relationship_dimensions(self, dimensions):
        """
        Pushes a command to undo stack.

        Args:
            dimensions (int): dimensions
        """
        index = self._sort_mappings_table_model.mapToSource(self._ui.mappings_table.currentIndex())
        mapping = self._mappings_table_model.data(index, MappingsTableModel.MAPPING_ROOT_ROLE)
        modified = deepcopy(mapping)
        set_relationship_dimensions(modified, dimensions)
        self._undo_stack.beginMacro("change relationship dimensions")
        self._undo_stack.push(SetMapping(self._ui.mappings_table.currentIndex(), modified))
        self._undo_stack.endMacro()

    def _set_relationship_dimensions_silently(self, dimensions):
        """
        Sets relationship dimensions spin box without emitting signals.

        Args:
            dimensions (int): dimensions
        """
        self._ui.relationship_dimensions_spin_box.valueChanged.disconnect(self._change_relationship_dimensions)
        self._ui.relationship_dimensions_spin_box.setValue(dimensions)
        self._ui.relationship_dimensions_spin_box.valueChanged.connect(self._change_relationship_dimensions)

    def _enable_mapping_specification_editing(self):
        """Enables and disables mapping specification editing controls."""
        have_mappings = self._mappings_table_model.rowCount() > 0
        self._ui.mapping_options_contents.setEnabled(have_mappings)
        self._ui.mapping_spec_contents.setEnabled(have_mappings)
        self._ui.remove_mapping_button.setEnabled(have_mappings)

    def _enable_relationship_controls(self):
        """Enables and disables controls related to relationship export."""
        self._ui.relationship_dimensions_spin_box.setEnabled(
            self._ui.item_type_combo_box.currentText() == "Relationship class"
        )

    def _enable_parameter_controls(self):
        """Enables and disables controls related to relationship export."""
        mapping_type = self._ui.item_type_combo_box.currentText()
        if mapping_type in ("Object class", "Object group", "Relationship class"):
            self._ui.parameter_type_combo_box.setEnabled(True)
            model = self._ui.parameter_type_combo_box.model()
            default_value_item = model.item(1)
            if mapping_type == "Object group":
                default_value_item.setFlags(default_value_item.flags() & ~Qt.ItemIsEnabled)
            else:
                default_value_item.setFlags(default_value_item.flags() | Qt.ItemIsEnabled)
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

    def _save(self):
        """
        Saves the specification.

        Returns:
            bool: True if specification was saved, False otherwise
        """
        specification_name = self._specification_toolbar.name()
        if not specification_name:
            QMessageBox.information(self, "Specification name missing", "Please enter a name for the specification.")
            return False
        description = self._specification_toolbar.description()
        self._new_spec.name = specification_name
        self._new_spec.description = description
        update_existing = self._new_spec.name == self._original_spec_name
        if not self._toolbox.add_specification(self._new_spec, update_existing, self):
            return False
        self._undo_stack.setClean()
        if self.item:
            self.item.set_specification(self._new_spec)
        self.specification = self._new_spec
        self.setWindowTitle(self.specification.name)
        return True

    def _populate_toolbar_menu(self):
        menu = self._specification_toolbar.menu
        before = self._specification_toolbar.save_action
        menu.insertActions(before, [self._undo_action, self._redo_action])
        menu.insertSeparator(before)

    def closeEvent(self, event):
        """Handles close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        if self.focusWidget():
            self.focusWidget().clearFocus()
        if not self._undo_stack.isClean() and not prompt_to_save_changes(self, self._toolbox.qsettings(), self._save):
            event.ignore()
            return
        self._undo_stack.cleanChanged.disconnect(self._update_window_modified)
        self._preview_updater.tear_down()
        save_ui(self, self._toolbox.qsettings(), self._APP_SETTINGS_GROUP)
        event.accept()


def _new_mapping_specification(mapping_type):
    """
    Creates a new export mapping.

    Args:
        mapping_type (MappingType): mapping's type

    Returns:
        MappingSpecification: an export mapping specification
    """
    if mapping_type == MappingType.objects:
        return MappingSpecification(mapping_type, True, True, False, object_export(0, 1))
    if mapping_type == MappingType.object_groups:
        return MappingSpecification(mapping_type, True, True, False, object_group_export(0, 1, 2))
    if mapping_type == MappingType.object_group_parameter_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            False,
            object_group_parameter_export(0, 1, Position.hidden, 2, 3, 4, Position.hidden, 5, None),
        )
    if mapping_type == MappingType.object_parameter_default_values:
        return MappingSpecification(mapping_type, True, True, False, object_parameter_default_value_export(0, 1, 2))
    if mapping_type == MappingType.object_parameter_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            False,
            object_parameter_export(0, 2, Position.hidden, 1, 3, Position.hidden, 4, None),
        )
    if mapping_type == MappingType.parameter_value_lists:
        return MappingSpecification(mapping_type, True, True, False, parameter_value_list_export(0, 1))
    if mapping_type == MappingType.relationships:
        return MappingSpecification(mapping_type, True, True, False, relationship_export(0, Position.hidden, [1], [2]))
    if mapping_type == MappingType.relationship_parameter_default_values:
        return MappingSpecification(
            mapping_type, True, True, False, relationship_parameter_default_value_export(0, 1, 2)
        )
    if mapping_type == MappingType.relationship_parameter_values:
        return MappingSpecification(
            mapping_type,
            True,
            True,
            False,
            relationship_parameter_export(
                0, 3, Position.hidden, Position.hidden, [1], [2], 4, Position.hidden, 5, None
            ),
        )
    if mapping_type == MappingType.alternatives:
        return MappingSpecification(mapping_type, True, True, False, alternative_export(0))
    if mapping_type == MappingType.scenario_alternatives:
        return MappingSpecification(mapping_type, True, True, False, scenario_alternative_export(0, 1))
    if mapping_type == MappingType.scenarios:
        return MappingSpecification(mapping_type, True, True, False, scenario_export(0, 1))
    if mapping_type == MappingType.features:
        return MappingSpecification(mapping_type, True, True, False, feature_export(0, 1))
    if mapping_type == MappingType.tools:
        return MappingSpecification(mapping_type, True, True, False, tool_export(0))
    if mapping_type == MappingType.tool_features:
        return MappingSpecification(mapping_type, True, True, False, tool_feature_export(0, 1, 2, 3))
    if mapping_type == MappingType.tool_feature_methods:
        return MappingSpecification(mapping_type, True, True, False, tool_feature_method_export(0, 1, 2, 3))
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
    return mapping_root.child
