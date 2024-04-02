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

""" Contains ImportPreviewWindow class. """
import os
import json
import fnmatch
from PySide6.QtCore import Qt, Signal, Slot, QModelIndex, QItemSelectionModel
from PySide6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QListWidget, QDialogButtonBox
from spinedb_api.helpers import remove_credentials_from_url
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
from ..importer_specification import ImporterSpecification
from ..mvcmodels.mappings_model import MappingsModel
from ..mvcmodels.source_list_selection_model import SourceListSelectionModel
from ...utils import convert_to_sqlalchemy_url
from ...widgets import UrlSelectorDialog

_CONNECTOR_NAME_TO_CLASS = {
    klass.__name__: klass
    for klass in (CSVConnector, ExcelConnector, GdxConnector, JSONConnector, DataPackageConnector, SqlAlchemyConnector)
}


class ImportEditorWindow(SpecificationEditorWindowBase):
    """A QMainWindow to let users define Mappings for an Importer item."""

    connection_failed = Signal(str)

    _FILE_LESS = "anonymous"
    """Name of the 'file-less' source."""

    class _FileLessConnector(SourceConnection):
        """A connector that has no tables or contents, used for the file-less mode."""

        FILE_EXTENSIONS = ""
        OPTIONS = {}

        def connect_to_source(self, source, **extras):
            pass

        def disconnect(self):
            pass

        def get_tables(self):
            return []

        def get_data_iterator(self, table, options, max_rows=-1):
            return iter([]), ()

    def __init__(self, toolbox, specification, item=None, source=None, source_extras=None):
        """
        Args:
            toolbox (QMainWindow): ToolboxUI class
            specification (ImporterSpecification, optional): Importer specification
            item (Importer, optional): Linked Importer item
            source (str, optional): Importee file path or URL; if None, work in file-less mode
            source_extras (dict, optional): Additional source settings such as database schema
        """
        super().__init__(toolbox, specification, item)
        self._source = source if source is not None else self._FILE_LESS
        self._source_extras = source_extras if source_extras is not None else {}
        self._mappings_model = MappingsModel(self._undo_stack, self)
        self._mappings_model.rowsInserted.connect(self._reselect_source_table)
        self._ui.source_list.setModel(self._mappings_model)
        self._ui.source_list.setSelectionModel(SourceListSelectionModel(self._mappings_model))
        self._ui.mapping_list.setModel(self._mappings_model)
        self._ui.mapping_list.setRootIndex(self._mappings_model.dummy_parent())
        self._ui.mapping_spec_table.setModel(self._mappings_model)
        self._ui.mapping_spec_table.setRootIndex(self._mappings_model.dummy_parent())
        self._connection_manager = None
        self._memoized_connector = None
        self._import_mappings = ImportMappings(self._mappings_model, self._ui, self._undo_stack, self)
        self._import_mapping_options = ImportMappingOptions(self._mappings_model, self._ui, self._undo_stack)
        self._import_sources = ImportSources(self._mappings_model, self._ui, self._undo_stack, self)
        self._set_source_text()
        self._ui.source_line_edit.editingFinished.connect(self._read_source_from_line)
        self._ui.source_line_edit.textEdited.connect(self._maybe_switch_to_file_less_mode)
        self._ui.browse_source_button.clicked.connect(self._show_open_file_dialog)
        self._ui.import_mappings_action.triggered.connect(self.import_mapping_from_file)
        self._ui.export_mappings_action.triggered.connect(self.export_mapping_to_file)
        self._ui.actionSwitch_connector.triggered.connect(self._switch_connector)
        self.connection_failed.connect(self.show_error)
        self._import_sources.preview_data_updated.connect(self._import_mapping_options.set_num_available_columns)
        self._mappings_model.restore(self.specification.mapping if self.specification is not None else {})
        self.start_ui()

    def is_file_less(self):
        return not self._ui.source_line_edit.text()

    @property
    def settings_group(self):
        return "mappingPreviewWindow"

    def _save(self, exiting=None):
        """See base class."""
        if super()._save(exiting):
            self._import_mappings.specification_saved()
            return True

    @property
    def _duplicate_kwargs(self):
        return dict(source=self._source)

    def _make_ui(self):
        from ..ui.import_editor_window import Ui_MainWindow  # pylint: disable=import-outside-toplevel

        return Ui_MainWindow()

    def _make_new_specification(self, spec_name):
        mappings_dict = self._mappings_model.store()
        mappings_dict.update(self._import_sources.store_connectors())
        description = self._spec_toolbar.description()
        return ImporterSpecification(spec_name, mappings_dict, description)

    def _populate_main_menu(self):
        super()._populate_main_menu()
        menu = self._spec_toolbar.menu
        before = self._spec_toolbar.save_action
        menu.insertAction(before, self._ui.actionSwitch_connector)
        menu.insertSeparator(before)
        menu.insertActions(before, [self._ui.import_mappings_action, self._ui.export_mappings_action])
        menu.insertSeparator(before)

    def _set_source_text(self):
        """Sets source path/URL to the source line edit cleaning credentials from URLs."""
        if self._source == self._FILE_LESS:
            self._ui.source_line_edit.clear()
            return
        label = remove_credentials_from_url(self._source) if self._is_url(self._source) else self._source
        self._ui.source_line_edit.setText(label)

    @Slot(bool)
    def _show_open_file_dialog(self, _=False):
        if self._is_database_connector(self._connection_manager.connection):
            url = self._get_source_url()
            if url is None:
                return
            self._source = str(convert_to_sqlalchemy_url(url, logger=self))
            schema = url["schema"]
            self._source_extras = {"schema": schema if schema else None}
        else:
            file_path = self._get_source_file_path()
            if file_path is None:
                return
            self._source = file_path
            self._source_extras = None
        self._set_source_text()
        self.start_ui()

    def _get_source_url(self):
        selector = UrlSelectorDialog(self._toolbox.qsettings(), False, self._toolbox, parent=self)
        selector.exec()
        if selector.result() != QDialog.DialogCode.Accepted:
            return None
        return selector.url_dict()

    def _get_source_file_path(self):
        filter_ = ";;".join(["*.*"] + [conn.FILE_EXTENSIONS for conn in _CONNECTOR_NAME_TO_CLASS.values()])
        key = f"selectInputDataFileFor{self.specification.name if self.specification else None}"
        filepath, _ = get_open_file_name_in_last_dir(
            self._toolbox.qsettings(),
            key,
            self,
            "Select an input data file to define the specification",
            APPLICATION_PATH,
            filter_=filter_,
        )
        return filepath

    @staticmethod
    def _is_database_connector(connector):
        """Tests if connector class works with database URLs.

        Args:
            connector (type): connector class to test
        """
        return connector.__name__ == SqlAlchemyConnector.__name__

    @Slot(bool)
    def _switch_connector(self, _=False):
        if self.specification:
            self.specification.mapping.pop("source_type", None)
        self._memoized_connector = None
        self.start_ui()

    def _get_connector_from_mapping(self, source):
        """Guesses connector for given source.

        Args:
            source (str): importee file path or URL

        Returns:
            type: connector class, or None if no suitable connector was found
        """
        if not self.specification:
            return None
        mapping = self.specification.mapping
        source_type = mapping.get("source_type")
        if source_type is None:
            return None
        connector = _CONNECTOR_NAME_TO_CLASS[source_type]
        file_extensions = connector.FILE_EXTENSIONS.split(";;")
        if source != self._FILE_LESS and not any(fnmatch.fnmatch(source, ext) for ext in file_extensions):
            if connector is SqlAlchemyConnector and self._is_url(source):
                return connector
            return None
        return connector

    @Slot()
    def _read_source_from_line(self):
        """Sets source from source line edit."""
        label = self._ui.source_line_edit.text()
        if self._source == self._FILE_LESS:
            if not label:
                return
            self._source = label
        else:
            if self._is_url(self._source):
                if label == remove_credentials_from_url(self._source):
                    return
                self._source_extras = None
            elif label == self._source:
                return
            self._source = label if label else self._FILE_LESS
        self.start_ui()

    @Slot(str)
    def _maybe_switch_to_file_less_mode(self, text):
        """Switches to file-less mode if text has been cleared.

        Args:
            text (str): text
        """
        if text or self._source == self._FILE_LESS:
            return
        self._source = self._FILE_LESS
        self._source_extras = None
        self.start_ui()

    def start_ui(self):
        """Connects to source and fills the tables and lists with data."""
        connector = self._get_connector_from_mapping(self._source)
        if connector is None:
            # Ask user
            connector = self._get_connector(self._source)
            if not connector:
                return
            is_db_connector = self._is_database_connector(connector)
            is_url_source = self._is_url(self._source)
            if (is_db_connector and not is_url_source) or (not is_db_connector and is_url_source):
                self._ui.source_line_edit.clear()
                self._source = self._FILE_LESS
                self._source_extras = None
        connector_name = connector.__name__
        if self._is_database_connector(connector):
            self._ui.source_label.setText("URL:")
        else:
            self._ui.source_label.setText("File path:")
        if self._source == self._FILE_LESS:
            self._FileLessConnector.__name__ = connector.__name__
            self._FileLessConnector.FILE_EXTENSIONS = connector.FILE_EXTENSIONS
            self._FileLessConnector.OPTIONS = connector.OPTIONS
            connector = self._FileLessConnector
            self._mappings_model.set_tables_editable(True)
        else:
            self._mappings_model.set_tables_editable(False)
        self._ui.actionSwitch_connector.setEnabled(True)
        connector_settings = {"gams_directory": _gams_system_directory(self._toolbox)}
        if self._connection_manager:
            self._connection_manager.close_connection()
        self._connection_manager = ConnectionManager(connector, connector_settings, self)
        self._connection_manager.connection_failed.connect(self.connection_failed.emit)
        self._connection_manager.error.connect(self.show_error)
        for header in (self._ui.source_data_table.horizontalHeader(), self._ui.source_data_table.verticalHeader()):
            self._ui.source_list.selectionModel().currentChanged.connect(header.set_source_table, Qt.UniqueConnection)
        self._connection_manager.connection_ready.connect(self._handle_connection_ready)
        mapping = self.specification.mapping if self.specification else {}
        self._import_sources.set_connector(self._connection_manager, mapping)
        self._display_connector_name(connector_name)
        extras = self._source_extras if self._source_extras is not None else {}
        self._connection_manager.init_connection(self._source, **extras)

    def _display_connector_name(self, name):
        """Shows connector's name on the ui.

        Args:
            name (str): connector's name
        """
        self._ui.connector_line_edit.setText(name)

    @Slot()
    def _handle_connection_ready(self):
        self._ui.export_mappings_action.setEnabled(True)
        self._ui.import_mappings_action.setEnabled(True)

    def _get_connector(self, source):
        """Shows a QDialog to select a connector for the given source file.

        Args:
            source (str): Path of the file acting as an importee

        Returns:
            Asynchronous data reader class for the given importee
        """
        if self._memoized_connector:
            return self._memoized_connector
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
            if any(fnmatch.fnmatch(source, ext) for ext in file_extensions):
                row = k
                break
        else:
            if self._is_url(source):
                row = connector_names.index(SqlAlchemyConnector.DISPLAY_NAME)
        if row is not None:
            connector_list_wg.setCurrentRow(row)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(dialog.accept)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(dialog.reject)
        connector_list_wg.doubleClicked.connect(dialog.accept)
        dialog.layout().addWidget(connector_list_wg)
        dialog.layout().addWidget(button_box)
        spec_name = self._spec_toolbar.name()
        if not spec_name:
            spec_name = "unnamed specification"
        dialog.setWindowTitle(f"Select connector for {spec_name}")
        answer = dialog.exec()
        if answer != QDialog.DialogCode.Accepted:
            return None
        row = connector_list_wg.currentIndex().row()
        if row < 0:
            return None
        connector = self._memoized_connector = connector_list[row]
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
                self._show_status_bar_msg(f"Could not open {filename[0]}")
                return
        expected_options = ("table_mappings", "table_types", "table_row_types", "table_options", "selected_tables")
        if not isinstance(settings, dict) or not any(key in expected_options for key in settings.keys()):
            self._show_status_bar_msg(f"{filename[0]} does not contain and import mapping")
        self._undo_stack.push(RestoreMappingsFromDict(self._import_sources, self._mappings_model, settings))
        self._show_status_bar_msg(f"Mapping loaded from {filename[0]}")

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
        with open(filename[0], "w") as file_p:
            mappings_dict = self._mappings_model.store()
            mappings_dict.update(self._import_sources.store_connectors())
            json.dump(mappings_dict, file_p)
        self._show_status_bar_msg(f"Mapping saved to: {filename[0]}")

    @Slot(QModelIndex, int, int)
    def _reselect_source_table(self, parent, first, last):
        """Selects added source table.

        This is a workaround to get the correct source table selected after a new one has been added
        since the source table view doesn't seem to update the current index correctly in this case.

        Args:
            parent (QModelIndex): parent index
            first (int): first new row
            last (int): last new row
        """
        if parent.isValid():
            return
        index = self._mappings_model.index(last, 0)
        self._ui.source_list.selectionModel().setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    @staticmethod
    def _is_url(string):
        """Tests if given string looks like a URL.

        Args:
            string (str): string to test

        Returns:
            bool: True if string looks like a URL, False otherwise
        """
        return "://" in string

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
