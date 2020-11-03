######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
The ImporterFactory class.

:author: M. Marin (KTH)
:date:   15.4.2020
"""

import os
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialogButtonBox, QDialog, QVBoxLayout, QListWidget, QFileDialog
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from spinetoolbox.import_editor.widgets.import_editor_window import ImportEditorWindow
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from spinetoolbox.config import APPLICATION_PATH
from spine_engine.utils.helpers import shorten
from spine_engine.spine_io.importers.csv_reader import CSVConnector
from spine_engine.spine_io.importers.excel_reader import ExcelConnector
from spine_engine.spine_io.importers.gdx_connector import GdxConnector
from spine_engine.spine_io.importers.json_reader import JSONConnector
from spine_engine.spine_io.gdx_utils import find_gams_directory
from .importer import Importer
from .importer_icon import ImporterIcon
from .importer_specification import ImporterSpecification
from .widgets.importer_properties_widget import ImporterPropertiesWidget
from .widgets.add_importer_widget import AddImporterWidget
from .widgets.custom_menus import SpecificationMenu

_CONNECTOR_NAME_TO_CLASS = {
    "CSVConnector": CSVConnector,
    "ExcelConnector": ExcelConnector,
    "GdxConnector": GdxConnector,
    "JSONConnector": JSONConnector,
}

_import_editors = {}  # Key is (spec_name, filepath), value is the ImportEditorWindow instance


class ImporterFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return Importer

    @staticmethod
    def icon():
        return ":/icons/item_icons/database-import.svg"

    @staticmethod
    def supports_specifications():
        return True

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddImporterWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return ImporterIcon(toolbox, ImporterFactory.icon())

    @staticmethod
    def make_item(name, item_dict, toolbox, project, logger):
        return Importer.from_dict(name, item_dict, toolbox, project, logger)

    @staticmethod
    def make_properties_widget(toolbox):
        return ImporterPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        return SpecificationMenu(parent, index)

    @staticmethod
    def show_specification_widget(toolbox, specification=None, filepath=None):
        """See base class."""
        if specification is None:
            specification = ImporterSpecification("NewImporterSpec", dict())
        if filepath is None:
            filter_ = ";;".join([conn.FILE_EXTENSIONS for conn in _CONNECTOR_NAME_TO_CLASS.values()])
            key = f"selectInputDataFileFor{specification.name}"
            filepath, _ = get_open_file_name_in_last_dir(
                toolbox.qsettings(),
                key,
                toolbox,
                "Select an input data file to define the specification",
                APPLICATION_PATH,
                filter_=filter_,
            )
            if not filepath:
                return
        # TODO: Try and set unambiguous spec name from filepath
        mapping = specification.mapping
        # Try and get connector from mapping
        source_type = mapping.get("source_type", None)
        if source_type is not None:
            connector = _CONNECTOR_NAME_TO_CLASS[source_type]
        else:
            # Ask user
            connector = _get_connector(toolbox, filepath)
            if not connector:
                return
        connector_settings = {"gams_directory": _gams_system_directory(toolbox)}
        key = (specification.name, filepath)
        import_editor = _import_editors.get(key, None)
        if import_editor:
            if import_editor.windowState() & Qt.WindowMinimized:
                # Remove minimized status and restore window with the previous state (maximized/normal state)
                import_editor.setWindowState(import_editor.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
                import_editor.activateWindow()
            else:
                import_editor.raise_()
            return
        toolbox.msg.emit(f"Opening Import editor for specification {specification.name} on file {filepath}")
        import_editor = _import_editors[key] = ImportEditorWindow(
            toolbox, specification, filepath, connector, connector_settings
        )
        import_editor.connection_failed.connect(
            lambda msg, toolbox=toolbox, key=key: _connection_failed(toolbox, key, msg)
        )
        import_editor.specification_updated.connect(
            lambda definition, toolbox=toolbox, original_specification=specification: _add_or_update_specification(
                toolbox, original_specification, definition
            )
        )
        import_editor.destroyed.connect(lambda o=None, key=key: _import_editors.pop(key, None))
        import_editor.start_ui()

    @staticmethod
    def tear_down():
        """Closes all preview widgets."""
        for widget in _import_editors.values():
            widget.close()


def _add_or_update_specification(toolbox, original_specification, definition):
    new_specification = toolbox.load_specification(definition)
    if new_specification is None:
        # Happens when toolbox doesn't find the spec factory (should never happen)
        return
    if new_specification.is_equivalent(original_specification):
        return
    new_specification.definition_file_path = original_specification.definition_file_path
    if not new_specification.definition_file_path or new_specification.name != original_specification.name:
        # The user is creating a new spec, either from scratch (no definition file path set)
        # or by chaning the name of an existing one
        start_dir = toolbox.project().project_dir
        proposed_def_file_path = os.path.join(start_dir, shorten(new_specification.name) + ".json")
        answer = QFileDialog.getSaveFileName(
            toolbox, "Save Importer specification file", proposed_def_file_path, "JSON (*.json)"
        )
        if answer[0] == "":  # Cancel button clicked
            return
        new_specification.definition_file_path = os.path.abspath(answer[0])
        new_specification.save()
        toolbox.add_specification(new_specification)
    else:
        # The user is modifying an existing spec, while conserving the name
        toolbox.update_specification(new_specification)


def _connection_failed(toolbox, key, msg):
    toolbox.msg_error.emit(msg)
    import_editor = _import_editors.pop(key, None)
    if import_editor:
        import_editor.close()


def _get_connector(toolbox, filepath):
    """Shows a QDialog to select a connector for the given source file.

    Args:
        filepath (str): Path of the file acting as an importee

    Returns:
        Asynchronous data reader class for the given importee
    """
    connector_list = [CSVConnector, ExcelConnector, GdxConnector, JSONConnector]  # add others as needed
    connector_names = [c.DISPLAY_NAME for c in connector_list]
    dialog = QDialog(toolbox)
    dialog.setLayout(QVBoxLayout())
    connector_list_wg = QListWidget()
    connector_list_wg.addItems(connector_names)
    # Set current item in `connector_list_wg` based on file extension
    _filename, file_extension = os.path.splitext(filepath)
    file_extension = file_extension.lower()
    if file_extension.startswith(".xls"):
        row = connector_list.index(ExcelConnector)
    elif file_extension in (".csv", ".dat", ".txt"):
        row = connector_list.index(CSVConnector)
    elif file_extension == ".gdx":
        row = connector_list.index(GdxConnector)
    elif file_extension == ".json":
        row = connector_list.index(JSONConnector)
    else:
        row = None
    if row is not None:
        connector_list_wg.setCurrentRow(row)
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.button(QDialogButtonBox.Ok).clicked.connect(dialog.accept)
    button_box.button(QDialogButtonBox.Cancel).clicked.connect(dialog.reject)
    connector_list_wg.doubleClicked.connect(dialog.accept)
    dialog.layout().addWidget(connector_list_wg)
    dialog.layout().addWidget(button_box)
    _dirname, filename = os.path.split(filepath)
    dialog.setWindowTitle("Select connector for '{}'".format(filename))
    answer = dialog.exec_()
    if answer:
        row = connector_list_wg.currentIndex().row()
        return connector_list[row]


def _gams_system_directory(toolbox):
    """Returns GAMS system path from Toolbox settings or None if GAMS default is to be used."""
    path = toolbox.qsettings().value("appSettings/gamsPath", defaultValue=None)
    if not path:
        path = find_gams_directory()
    if path is not None and os.path.isfile(path):
        path = os.path.dirname(path)
    return path
