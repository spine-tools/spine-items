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
import fnmatch
import json
from operator import attrgetter
import os
from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog, QListWidget, QMessageBox, QVBoxLayout
from spinedb_api.helpers import remove_credentials_from_url
from spinedb_api.spine_io.gdx_utils import find_gams_directory
from spinedb_api.spine_io.importers.reader import Reader
from spinedb_api.spine_io.importers.sqlalchemy_reader import SQLAlchemyReader
from spinetoolbox.config import APPLICATION_PATH
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from spinetoolbox.project_item.specification_editor_window import SpecificationEditorWindowBase
from ...utils import convert_to_sqlalchemy_url
from ...widgets import UrlSelectorDialog
from ..commands import RestoreMappingsFromDict
from ..connection_manager import ConnectionManager
from ..executable_item import READER_NAME_TO_CLASS
from ..importer_specification import ImporterSpecification
from ..mvcmodels.mappings_model import MappingsModel
from ..mvcmodels.source_list_selection_model import SourceListSelectionModel
from .import_mapping_options import ImportMappingOptions
from .import_mappings import ImportMappings
from .import_sources import ImportSources


class _ReaderProblemInMapping(Exception):
    """Raised when mapping has no reader or the reader looks different to file type."""

    def __init__(self, reader_in_mapping):
        """
        Args:
            reader_in_mapping (type, optional): reader class defined in mapping
        """
        self.reader_in_mapping = reader_in_mapping


class ImportEditorWindow(SpecificationEditorWindowBase):
    """A QMainWindow to let users define Mappings for an Importer item."""

    connection_failed = Signal(str)

    _FILE_LESS = "anonymous"
    """Name of the 'file-less' input."""

    class _FileLessReader(Reader):
        """A connector that has no tables or contents, used for the file-less mode."""

        DISPLAY_NAME = "<unspecified>"
        FILE_EXTENSIONS = ""
        OPTIONS = {}

        def connect_to_source(self, source, **extras):
            pass

        def disconnect(self):
            pass

        def get_tables_and_properties(self):
            return {}

        def get_data_iterator(self, table, options, max_rows=-1):
            return iter([]), ()

    def __init__(self, toolbox, specification, item=None, input=None, input_extras=None):
        """
        Args:
            toolbox (QMainWindow): ToolboxUI class
            specification (ImporterSpecification, optional): Importer specification
            item (Importer, optional): Linked Importer item
            input (str, optional): Importee file path or URL; if None, work in file-less mode
            input_extras (dict, optional): Additional input settings such as database schema
        """
        super().__init__(toolbox, specification, item)
        self._input = input if input is not None else self._FILE_LESS
        self._input_extras = input_extras if input_extras is not None else {}
        self._mappings_model = MappingsModel(self._undo_stack, self)
        self._mappings_model.rowsInserted.connect(self._reselect_source_table)
        self._ui.source_list.setModel(self._mappings_model)
        self._ui.source_list.setSelectionModel(SourceListSelectionModel(self._mappings_model))
        self._ui.mapping_list.setModel(self._mappings_model)
        self._ui.mapping_list.setRootIndex(self._mappings_model.dummy_parent())
        self._ui.mapping_spec_table.setModel(self._mappings_model)
        self._ui.mapping_spec_table.setRootIndex(self._mappings_model.dummy_parent())
        self._connection_manager = None
        self._memoized_reader = None
        self._import_mappings = ImportMappings(self._mappings_model, self._ui, self._undo_stack, self)
        self._import_mapping_options = ImportMappingOptions(self._mappings_model, self._ui, self._undo_stack)
        self._import_sources = ImportSources(self._mappings_model, self._ui, self._undo_stack, self)
        self._set_input_text()
        self._ui.input_path_line_edit.editingFinished.connect(self._read_input_path_from_line)
        self._ui.input_path_line_edit.textEdited.connect(self._maybe_switch_to_file_less_mode)
        self._ui.browse_inputs_button.clicked.connect(self._show_open_file_dialog)
        self._ui.import_mappings_action.triggered.connect(self.import_mapping_from_file)
        self._ui.export_mappings_action.triggered.connect(self.export_mapping_to_file)
        self._ui.switch_input_type_action.triggered.connect(self._switch_input_type)
        self.connection_failed.connect(self.show_error)
        self._import_sources.preview_data_updated.connect(self._import_mapping_options.set_num_available_columns)
        self._mappings_model.restore(self.specification.mapping if self.specification is not None else {})
        QTimer.singleShot(0, self.start_ui)

    def is_file_less(self):
        return not self._ui.input_path_line_edit.text()

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
        return {"input": self._input}

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
        menu.insertAction(before, self._ui.switch_input_type_action)
        menu.insertSeparator(before)
        menu.insertActions(before, [self._ui.import_mappings_action, self._ui.export_mappings_action])
        menu.insertSeparator(before)

    def _set_input_text(self):
        """Sets input path/URL to the input line edit cleaning credentials from URLs."""
        if self._input == self._FILE_LESS:
            self._ui.input_path_line_edit.clear()
            return
        label = remove_credentials_from_url(self._input) if self._is_url(self._input) else self._input
        self._ui.input_path_line_edit.setText(label)

    @Slot(bool)
    def _show_open_file_dialog(self, _=False):
        if self._is_database_reader(self._connection_manager.connection):
            url = self._get_input_url()
            if url is None:
                return
            self._input = str(convert_to_sqlalchemy_url(url, logger=self))
            schema = url["schema"]
            self._input_extras = {"schema": schema if schema else None}
        else:
            file_path = self._get_input_file_path()
            if not file_path:
                return
            self._input = file_path
            self._input_extras = None
        self._set_input_text()
        self.start_ui()

    def _get_input_url(self):
        selector = UrlSelectorDialog(self._toolbox.qsettings(), False, self._toolbox, parent=self)
        selector.exec()
        if selector.result() != QDialog.DialogCode.Accepted:
            return None
        return selector.url_dict()

    def _get_input_file_path(self):
        filter_ = ";;".join(["*.*"] + [conn.FILE_EXTENSIONS for conn in READER_NAME_TO_CLASS.values()])
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
    def _is_database_reader(reader):
        """Tests if reader class works with database URLs.

        Args:
            reader (type): reader class to test
        """
        return reader.__name__ == SQLAlchemyReader.__name__

    @Slot(bool)
    def _switch_input_type(self, _=False):
        if self.specification:
            self.specification.mapping.pop("source_type", None)
        self._memoized_reader = None
        self.start_ui()

    def _get_reader_from_mapping(self, input_path):
        """Reads reader for given input from mapping.

        Args:
            input_path (str): importee file path or URL

        Returns:
            type: reader class
        """
        if not self.specification:
            raise _ReaderProblemInMapping(None)
        mapping = self.specification.mapping
        source_type = mapping.get("source_type")
        if source_type is None:
            raise _ReaderProblemInMapping(None)
        reader = READER_NAME_TO_CLASS[source_type]
        file_extensions = reader.FILE_EXTENSIONS.split(";;")
        if input_path != self._FILE_LESS and not any(fnmatch.fnmatch(input_path, ext) for ext in file_extensions):
            if reader is SQLAlchemyReader and self._is_url(input_path):
                return reader
            raise _ReaderProblemInMapping(reader)
        return reader

    @Slot()
    def _read_input_path_from_line(self):
        """Sets input from input path line edit."""
        label = self._ui.input_path_line_edit.text()
        if self._input == self._FILE_LESS:
            if not label:
                return
            self._input = label
        else:
            if self._is_url(self._input):
                if label == remove_credentials_from_url(self._input):
                    return
                self._input_extras = None
            elif label == self._input:
                return
            self._input = label if label else self._FILE_LESS
        self.start_ui()

    @Slot(str)
    def _maybe_switch_to_file_less_mode(self, text):
        """Switches to file-less mode if text has been cleared.

        Args:
            text (str): text
        """
        if text or self._input == self._FILE_LESS:
            return
        self._input = self._FILE_LESS
        self._input_extras = None
        self.start_ui()

    def start_ui(self):
        """Connects to input and fills the tables and lists with data."""
        try:
            reader = self._get_reader_from_mapping(self._input)
        except _ReaderProblemInMapping as reader_problem:
            if reader_problem.reader_in_mapping is not None:
                QMessageBox.warning(
                    self,
                    "Verify input type",
                    f"Input type is set to {reader_problem.reader_in_mapping.DISPLAY_NAME} but the input looks incompatible. "
                    "You will be prompted to verify the type.",
                )
            reader = self._get_reader(self._input)
            if not reader:
                return
            is_db_reader = self._is_database_reader(reader)
            is_url_input = self._is_url(self._input)
            if (is_db_reader and not is_url_input) or (not is_db_reader and is_url_input):
                self._ui.input_path_line_edit.clear()
                self._input = self._FILE_LESS
                self._input_extras = None
            if reader_problem.reader_in_mapping is not None and reader is not reader_problem.reader_in_mapping:
                QMessageBox.information(
                    self,
                    "Input type changed",
                    f"Input type changed from {reader_problem.reader_in_mapping.DISPLAY_NAME} to {reader.DISPLAY_NAME}. "
                    "Don't forget to save the changes.",
                )
                self._undo_stack.resetClean()
        if self._input == self._FILE_LESS:
            self._FileLessReader.__name__ = reader.__name__
            self._FileLessReader.FILE_EXTENSIONS = reader.FILE_EXTENSIONS
            self._FileLessReader.OPTIONS = reader.OPTIONS
            reader = self._FileLessReader
            self._mappings_model.set_tables_editable(True)
        else:
            self._mappings_model.set_tables_editable(False)
        self._ui.switch_input_type_action.setEnabled(True)
        reader_settings = {"gams_directory": _gams_system_directory(self._toolbox)}
        if self._connection_manager:
            self._connection_manager.close_connection()
        self._connection_manager = ConnectionManager(reader, reader_settings, self)
        self._connection_manager.connection_failed.connect(self.connection_failed.emit)
        self._connection_manager.error.connect(self.show_error)
        for header in (self._ui.source_data_table.horizontalHeader(), self._ui.source_data_table.verticalHeader()):
            self._ui.source_list.selectionModel().currentChanged.connect(
                header.set_source_table, Qt.ConnectionType.UniqueConnection
            )
        self._connection_manager.connection_ready.connect(self._handle_connection_ready)
        mapping = self.specification.mapping if self.specification else {}
        self._import_sources.set_connector(self._connection_manager, mapping)
        self._display_input_type(reader.DISPLAY_NAME)
        extras = self._input_extras if self._input_extras is not None else {}
        self._connection_manager.init_connection(self._input, **extras)

    def _display_input_type(self, input_type):
        """Shows connector's name on the ui.

        Args:
            input_type (str): readers's display name
        """
        self._ui.input_type_line_edit.setText(input_type)

    @Slot()
    def _handle_connection_ready(self):
        self._ui.export_mappings_action.setEnabled(True)
        self._ui.import_mappings_action.setEnabled(True)

    def _get_reader(self, input_path):
        """Shows a QDialog to select a reader for the given data input.

        Args:
            input_path (str): Path of the file acting as an importee

        Returns:
            Asynchronous data reader class for the given importee
        """
        if self._memoized_reader:
            return self._memoized_reader
        reader_list = sorted(list(READER_NAME_TO_CLASS.values()), key=attrgetter("DISPLAY_NAME"))
        reader_names = [c.DISPLAY_NAME for c in reader_list]
        dialog = QDialog(self)
        dialog.setLayout(QVBoxLayout())
        reader_list_wg = QListWidget()
        reader_list_wg.addItems(reader_names)
        # Set current item in `reader_list_wg` based on file extension
        row = None
        for k, reader in enumerate(reader_list):
            file_extensions = reader.FILE_EXTENSIONS.split(";;")
            if any(fnmatch.fnmatch(input_path, ext) for ext in file_extensions):
                row = k
                break
        else:
            if self._is_url(input_path):
                row = reader_names.index(SQLAlchemyReader.DISPLAY_NAME)
        if row is not None:
            reader_list_wg.setCurrentRow(row)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(dialog.accept)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(dialog.reject)
        reader_list_wg.doubleClicked.connect(dialog.accept)
        dialog.layout().addWidget(reader_list_wg)
        dialog.layout().addWidget(button_box)
        spec_name = self._spec_toolbar.name()
        if not spec_name:
            spec_name = "unnamed specification"
        dialog.setWindowTitle(f"Select input type for {spec_name}")
        answer = dialog.exec()
        if answer != QDialog.DialogCode.Accepted:
            return None
        row = reader_list_wg.currentIndex().row()
        if row < 0:
            return None
        connector = self._memoized_reader = reader_list[row]
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
        self._ui.source_list.selectionModel().setCurrentIndex(index, QItemSelectionModel.SelectionFlag.ClearAndSelect)

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
