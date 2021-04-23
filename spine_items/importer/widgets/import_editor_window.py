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
Contains ImportPreviewWindow class.

:authors: P. Savolainen (VTT), A. Soininen (VTT), P. Vennström (VTT)
:date:    10.6.2019
"""

import os
import json
import fnmatch
from copy import deepcopy
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtWidgets import QFileDialog, QDockWidget, QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
from spinetoolbox.project_item.specification_editor_window import SpecificationEditorWindowBase
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from spinetoolbox.config import APPLICATION_PATH
from spinedb_api.spine_io.importers.csv_reader import CSVConnector
from spinedb_api.spine_io.importers.excel_reader import ExcelConnector
from spinedb_api.spine_io.importers.gdx_connector import GdxConnector
from spinedb_api.spine_io.importers.json_reader import JSONConnector
from spinedb_api.spine_io.importers.datapackage_reader import DataPackageConnector
from spinedb_api.spine_io.importers.sqlalchemy_connector import SqlAlchemyConnector
from spinedb_api.spine_io.importers.reader import SourceConnection
from spinedb_api.spine_io.gdx_utils import find_gams_directory
from ..connection_manager import ConnectionManager
from ..commands import RestoreMappingsFromDict
from .import_sources import ImportSources
from .import_mapping_options import ImportMappingOptions
from .import_mappings import ImportMappings


_CONNECTOR_NAME_TO_CLASS = {
    "CSVConnector": CSVConnector,
    "ExcelConnector": ExcelConnector,
    "GdxConnector": GdxConnector,
    "JSONConnector": JSONConnector,
    "DataPackageConnector": DataPackageConnector,
    "SqlAlchemyConnector": SqlAlchemyConnector,
}


class ImportEditorWindow(SpecificationEditorWindowBase):
    """A QMainWindow to let users define Mappings for an Importer item."""

    connection_failed = Signal(str)

    _FILE_LESS = "anonymous file"
    """Name of the 'file-less' entry in the file path combobox."""

    class _FileLessConnector(SourceConnection):
        """A connector that has no tables or contents, used for the file-less mode."""

        FILE_EXTENSIONS = ""
        OPTIONS = {}

        def connect_to_source(self, _source):
            pass

        def disconnect(self):
            pass

        def get_tables(self):
            return []

        def get_data_iterator(self, table, options, max_rows=-1):
            return iter([]), ()

    def __init__(self, toolbox, specification, item=None, filepath=None):
        """
        Args:
            toolbox (QMainWindow): ToolboxUI class
            specification (ImporterSpecification)
            filepath (str, optional): Importee path
        """
        super().__init__(toolbox, specification, item)
        self.takeCentralWidget().deleteLater()
        self._filepath = filepath
        self._import_sources = None
        self._connection_manager = None
        self._memoized_connectors = {}
        self._copied_mappings = {}
        self._import_mappings = ImportMappings(self)
        self._import_mapping_options = ImportMappingOptions(self)
        self._import_mappings.mapping_selection_changed.connect(
            self._import_mapping_options.set_mapping_specification_model
        )
        self._import_mapping_options.about_to_undo.connect(self._import_mappings.focus_on_changing_specification)
        self._ui.comboBox_source_file.addItem(self._FILE_LESS)
        if filepath:
            self._ui.comboBox_source_file.addItem(filepath)
        self._ui.comboBox_source_file.setCurrentIndex(-1)
        self._ui.comboBox_source_file.currentTextChanged.connect(self.start_ui)
        self._ui.toolButton_browse_source_file.clicked.connect(self._show_open_file_dialog)
        self._ui.import_mappings_action.triggered.connect(self.import_mapping_from_file)
        self._ui.export_mappings_action.triggered.connect(self.export_mapping_to_file)
        self._ui.actionSwitch_connector.triggered.connect(self._switch_connector)
        self.connection_failed.connect(self._show_error)

    def showEvent(self, ev):
        """Select file path in the combobox, which calls the ``start_ui`` slot."""
        super().showEvent(ev)
        if self._filepath:
            self._ui.comboBox_source_file.setCurrentText(self._filepath)

    def is_file_less(self):
        return self._ui.comboBox_source_file.currentText() == self._FILE_LESS

    @property
    def settings_group(self):
        return "mappingPreviewWindow"

    def _make_ui(self):
        from ..ui.import_editor_window import Ui_MainWindow  # pylint: disable=import-outside-toplevel

        return Ui_MainWindow()

    def _restore_dock_widgets(self):
        """Applies the classic UI style."""
        size = self.size()
        for dock in self.findChildren(QDockWidget):
            dock.setVisible(True)
            dock.setFloating(False)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
        docks = (self._ui.dockWidget_source_files, self._ui.dockWidget_mappings)
        self.splitDockWidget(*docks, Qt.Horizontal)
        width = sum(d.size().width() for d in docks)
        self.resizeDocks(docks, [0.9 * width, 0.1 * width], Qt.Horizontal)
        docks = (self._ui.dockWidget_source_files, self._ui.dockWidget_source_tables, self._ui.dockWidget_source_data)
        self.splitDockWidget(*docks[:-1], Qt.Vertical)
        self.splitDockWidget(*docks[1:], Qt.Vertical)
        height = sum(d.size().height() for d in docks)
        self.resizeDocks(docks, [0.1 * height, 0.2 * height, 0.7 * height], Qt.Vertical)
        self.splitDockWidget(self._ui.dockWidget_source_tables, self._ui.dockWidget_source_options, Qt.Horizontal)
        self.splitDockWidget(self._ui.dockWidget_mappings, self._ui.dockWidget_mapping_options, Qt.Vertical)
        self.splitDockWidget(self._ui.dockWidget_mapping_options, self._ui.dockWidget_mapping_spec, Qt.Vertical)
        docks = (self._ui.dockWidget_mapping_options, self._ui.dockWidget_mapping_spec)
        height = sum(d.size().height() for d in docks)
        self.resizeDocks(docks, [0.1 * height, 0.9 * height], Qt.Vertical)
        qApp.processEvents()  # pylint: disable=undefined-variable
        self.resize(size)

    def _make_new_specification(self, spec_name):
        mapping = self._import_sources.get_mapping_dict() if self._import_sources else {}
        description = self._spec_toolbar.description()
        spec_dict = {"name": spec_name, "mapping": mapping, "description": description, "item_type": "Importer"}
        return self._toolbox.load_specification(spec_dict)

    def _populate_main_menu(self):
        super()._populate_main_menu()
        menu = self._spec_toolbar.menu
        before = self._spec_toolbar.save_action
        menu.insertAction(before, self._ui.actionSwitch_connector)
        menu.insertSeparator(before)
        menu.insertActions(before, [self._ui.import_mappings_action, self._ui.export_mappings_action])
        menu.insertSeparator(before)

    @Slot(bool)
    def _show_open_file_dialog(self, _=False):
        filter_ = ";;".join([conn.FILE_EXTENSIONS for conn in _CONNECTOR_NAME_TO_CLASS.values()])
        key = f"selectInputDataFileFor{self.specification.name if self.specification else None}"
        filepath, _ = get_open_file_name_in_last_dir(
            self._toolbox.qsettings(),
            key,
            self,
            "Select an input data file to define the specification",
            APPLICATION_PATH,
            filter_=filter_,
        )
        if not filepath:
            return
        self._ui.comboBox_source_file.addItem(filepath)
        self._ui.comboBox_source_file.setCurrentText(filepath)

    @Slot(bool)
    def _switch_connector(self, _=False):
        filepath = self._connection_manager.source
        if self.specification:
            self.specification.mapping.pop("source_type", None)
        self._memoized_connectors.pop(filepath, None)
        self.start_ui(filepath)

    def _get_connector_from_mapping(self, filepath):
        if not self.specification:
            return None
        mapping = self.specification.mapping
        source_type = mapping.get("source_type")
        if source_type is None:
            return None
        connector = _CONNECTOR_NAME_TO_CLASS[source_type]
        file_extensions = connector.FILE_EXTENSIONS.split(";;")
        if not any(fnmatch.fnmatch(filepath, ext) for ext in file_extensions):
            return None
        return connector

    def start_ui(self, filepath):
        """
        Args:
            filepath (str): Importee path
        """
        connector = self._get_connector_from_mapping(filepath)
        if connector is None:
            # Ask user
            connector = self._get_connector(filepath)
            if not connector:
                return
        if filepath == self._FILE_LESS:
            self._FileLessConnector.__name__ = connector.__name__
            self._FileLessConnector.OPTIONS = connector.OPTIONS
            connector = self._FileLessConnector
        self._ui.actionSwitch_connector.setEnabled(True)
        connector_settings = {"gams_directory": _gams_system_directory(self._toolbox)}
        if self._connection_manager:
            self._connection_manager.close_connection()
        self._connection_manager = ConnectionManager(connector, connector_settings)
        self._connection_manager.source = filepath
        mapping = self.specification.mapping if self.specification else {}
        self._import_sources = ImportSources(self, mapping)
        self._connection_manager.connection_failed.connect(self.connection_failed.emit)
        self._connection_manager.error.connect(self._show_error)
        self._ui.source_data_table.set_undo_stack(self._undo_stack, self._import_sources.select_table)
        self._import_mappings.mapping_selection_changed.connect(self._import_sources.set_model)
        self._import_mappings.mapping_selection_changed.connect(self._import_sources.set_mapping)
        self._import_mappings.mapping_data_changed.connect(self._import_sources.set_mapping)
        self._import_mappings.about_to_undo.connect(self._import_sources.select_table)
        self._import_sources.source_table_selected.connect(self._import_mappings.set_mappings_model)
        for header in (self._ui.source_data_table.horizontalHeader(), self._ui.source_data_table.verticalHeader()):
            self._import_sources.source_table_selected.connect(header.set_source_table)
        self._import_sources.preview_data_updated.connect(self._import_mapping_options.set_num_available_columns)
        self._connection_manager.connection_ready.connect(self._handle_connection_ready)
        self._connection_manager.init_connection()

    @Slot()
    def _handle_connection_ready(self):
        self._ui.export_mappings_action.setEnabled(True)
        self._ui.import_mappings_action.setEnabled(True)

    def _get_connector(self, filepath):
        """Shows a QDialog to select a connector for the given source file.

        Args:
            filepath (str): Path of the file acting as an importee

        Returns:
            Asynchronous data reader class for the given importee
        """
        if filepath in self._memoized_connectors:
            return self._memoized_connectors[filepath]
        connector_list = list(_CONNECTOR_NAME_TO_CLASS.values())
        connector_names = [c.DISPLAY_NAME for c in connector_list]
        dialog = QDialog(self)
        dialog.setLayout(QVBoxLayout())
        connector_list_wg = QListWidget()
        connector_list_wg.addItems(connector_names)
        # Set current item in `connector_list_wg` based on file extension
        row = None
        for k, conn in enumerate(connector_list):
            file_extensions = conn.FILE_EXTENSIONS.split(";;")
            if any(fnmatch.fnmatch(filepath, ext) for ext in file_extensions):
                row = k
        if row is not None:
            connector_list_wg.setCurrentRow(row)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).clicked.connect(dialog.accept)
        button_box.button(QDialogButtonBox.Cancel).clicked.connect(dialog.reject)
        connector_list_wg.doubleClicked.connect(dialog.accept)
        dialog.layout().addWidget(connector_list_wg)
        dialog.layout().addWidget(button_box)
        spec_name = self._spec_toolbar.name()
        if not spec_name:
            spec_name = "unnamed specification"
        dialog.setWindowTitle(f"Select connector for {spec_name}")
        answer = dialog.exec_()
        if not answer:
            return None
        row = connector_list_wg.currentIndex().row()
        connector = self._memoized_connectors[filepath] = connector_list[row]
        return connector

    @Slot()
    def import_mapping_from_file(self):
        """Imports mapping spec from a user selected .json file to the preview window."""
        start_dir = self._toolbox.project().project_dir
        # noinspection PyCallByClass
        filename = QFileDialog.getOpenFileName(
            self, "Import mapping specification", start_dir, "Import mapping (*.json)"
        )
        if not filename[0]:
            return
        with open(filename[0]) as file_p:
            try:
                settings = json.load(file_p)
            except json.JSONDecodeError:
                self._show_status_bar_msg(f"Could not open {filename[0]}", 10000)
                return
        expected_options = ("table_mappings", "table_types", "table_row_types", "table_options", "selected_tables")
        if not isinstance(settings, dict) or not any(key in expected_options for key in settings.keys()):
            self._show_status_bar_msg(f"{filename[0]} does not contain and import mapping", 10000)
        self._undo_stack.push(RestoreMappingsFromDict(self._import_sources, settings))
        self._show_status_bar_msg(f"Mapping loaded from {filename[0]}", 10000)

    @Slot()
    def export_mapping_to_file(self):
        """Exports all mapping specs in current preview window to .json file."""
        start_dir = self._toolbox.project().project_dir
        # noinspection PyCallByClass
        filename = QFileDialog.getSaveFileName(
            self, "Export mapping spec to a file", start_dir, "Import mapping (*.json)"
        )
        if not filename[0]:
            return
        with open(filename[0], 'w') as file_p:
            settings = self._import_sources.get_mapping_dict()
            json.dump(settings, file_p)
        self._show_status_bar_msg(f"Mapping saved to: {filename[0]}", 10000)

    def paste_mappings(self, table, mappings):
        """
        Pastes mappings to given table

        Args:
            table (str): source table name
            mappings (dict): mappings to paste
        """
        self._import_sources._table_mappings[table].reset(deepcopy(mappings), table)
        index = self._ui.source_list.selectionModel().currentIndex()
        current_table = index.data()
        if table == current_table:
            self._import_sources.source_table_selected.emit(table, self._import_sources._table_mappings[table])
        else:
            self._import_sources.select_table(table)

    def tear_down(self):
        if not super().tear_down():
            return False
        if self._import_sources:
            self._import_sources.close_connection()
        return True


def _gams_system_directory(toolbox):
    """Returns GAMS system path from Toolbox settings or None if GAMS default is to be used."""
    path = toolbox.qsettings().value("appSettings/gamsPath", defaultValue=None)
    if not path:
        path = find_gams_directory()
    if path is not None and os.path.isfile(path):
        path = os.path.dirname(path)
    return path
