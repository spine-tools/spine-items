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
Contains Importer project item class.

:authors: P. Savolainen (VTT), P. Vennström (VTT), A. Soininen (VTT)
:date:   10.6.2019
"""

from collections import Counter
import os
from PySide2.QtCore import QModelIndex, Qt, Slot
from spinetoolbox.helpers import create_dir
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import serialize_path, deserialize_checked_states, serialize_checked_states
from spine_engine.spine_io.importers.csv_reader import CSVConnector
from spine_engine.spine_io.importers.excel_reader import ExcelConnector
from spine_engine.spine_io.importers.gdx_connector import GdxConnector
from spine_engine.spine_io.importers.json_reader import JSONConnector
from spine_engine import ExecutionDirection
from ..commands import UpdateCancelOnErrorCommand, ChangeItemSelectionCommand
from ..models import FileListModel
from .executable_item import ExecutableItem
from .item_info import ItemInfo

_CONNECTOR_NAME_TO_CLASS = {
    "CSVConnector": CSVConnector,
    "ExcelConnector": ExcelConnector,
    "GdxConnector": GdxConnector,
    "JSONConnector": JSONConnector,
}


class Importer(ProjectItem):
    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        logger,
        specification_name="",
        cancel_on_error=True,
        file_selection=None,
    ):
        """Importer class.

        Args:
            name (str): Project item name
            description (str): Project item description
            x (float): Initial icon scene X coordinate
            y (float): Initial icon scene Y coordinate
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            specification_name (str, optional): a spec name
            cancel_on_error (bool): if True the item's execution will stop on import error
            file_selection (dict): a map from label to a bool indicating if the file item is checked
       """
        super().__init__(name, description, x, y, project, logger)
        # Make logs subdirectory for this item
        self._toolbox = toolbox
        self.logs_dir = os.path.join(self.data_dir, "logs")
        try:
            create_dir(self.logs_dir)
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory {self.logs_dir} failed. Check permissions.")
        # Variables for saving selections when item is (de)activated
        self._specification = self._toolbox.specification_model.find_specification(specification_name)
        if specification_name and not self._specification:
            self._logger.msg_error.emit(
                f"Importer <b>{self.name}</b> should have a specification <b>{specification_name}</b> but it was not found"
            )
        self.do_set_specification(self._specification)
        self.cancel_on_error = cancel_on_error
        self._file_model = FileListModel(invalid_resource_types=("database",), header_label="Source files")
        self._file_model.set_initial_state(file_selection if file_selection is not None else dict())
        self._file_model.selected_state_changed.connect(self._push_file_selection_change_to_undo_stack)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    def execution_item(self):
        """Creates project item's execution counterpart."""
        mapping = self.specification().mapping if self.specification() is not None else dict()
        selected_files = [file_item.label for file_item in self._file_model.files if file_item.selected]
        gams_path = self._project.settings.value("appSettings/gamsPath", defaultValue=None)
        executable = ExecutableItem(
            self.name, mapping, selected_files, self.logs_dir, gams_path, self.cancel_on_error, self._logger
        )
        return executable

    @Slot(object, object)
    def handle_execution_successful(self, execution_direction, engine_state):
        """Notifies Toolbox of successful database import."""
        if execution_direction != ExecutionDirection.FORWARD:
            return
        successors = self._project.direct_successors(self)
        committed_db_maps = set()
        for successor in successors:
            if successor.item_type() == "Data Store":
                url = successor.sql_alchemy_url()
                committed_db_maps |= set(self._project.db_mngr.open_db_maps(url))
        if committed_db_maps:
            cookie = self
            self._project.db_mngr.session_committed.emit(committed_db_maps, cookie)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.toolButton_open_dir.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.toolButton_edit_specification.clicked] = self._edit_specification
        s[self._properties_ui.treeView_files.doubleClicked] = self._handle_files_double_clicked
        s[self._properties_ui.comboBox_specification.currentTextChanged] = self._change_specification
        s[self._properties_ui.cancel_on_error_checkBox.stateChanged] = self._handle_cancel_on_error_changed
        return s

    @Slot(str)
    def _change_specification(self, specification_name):
        """
        Pushes a set specification command to the undo stack.

        Args:
            specification_name (str): new specification name
        """
        specification = self._toolbox.specification_model.find_specification(specification_name)
        self.set_specification(specification)

    @Slot(int)
    def _handle_cancel_on_error_changed(self, _state):
        cancel_on_error = self._properties_ui.cancel_on_error_checkBox.isChecked()
        if self.cancel_on_error == cancel_on_error:
            return
        self._toolbox.undo_stack.push(UpdateCancelOnErrorCommand(self, cancel_on_error))

    def set_cancel_on_error(self, cancel_on_error):
        self.cancel_on_error = cancel_on_error
        if not self._active:
            return
        check_state = Qt.Checked if self.cancel_on_error else Qt.Unchecked
        self._properties_ui.cancel_on_error_checkBox.blockSignals(True)
        self._properties_ui.cancel_on_error_checkBox.setCheckState(check_state)
        self._properties_ui.cancel_on_error_checkBox.blockSignals(False)

    def set_file_selected(self, label, selected):
        self._file_model.set_selected(label, selected)

    def restore_selections(self):
        """Restores selections into shared widgets when this project item is selected."""
        self._properties_ui.cancel_on_error_checkBox.setCheckState(Qt.Checked if self.cancel_on_error else Qt.Unchecked)
        self._properties_ui.label_name.setText(self.name)
        self._properties_ui.treeView_files.setModel(self._file_model)
        if self._specification:
            self._properties_ui.comboBox_specification.setCurrentText(self._specification.name)
        else:
            self._properties_ui.comboBox_specification.setCurrentIndex(-1)

    def save_selections(self):
        """Saves selections in shared widgets for this project item into instance variables."""
        self._properties_ui.treeView_files.setModel(None)

    def update_name_label(self):
        """Update Importer properties tab name label. Used only when renaming project items."""
        self._properties_ui.label_name.setText(self.name)

    def do_set_specification(self, specification):
        """see base class"""
        super().do_set_specification(specification)
        if self._active:
            if specification is None:
                self._properties_ui.comboBox_specification.setCurrentIndex(-1)
                return
            self._properties_ui.comboBox_specification.setCurrentText(specification.name)
        self.item_changed.emit()

    @Slot(bool)
    def _edit_specification(self, checked=False):
        """Opens Import editor for the file selected in list view."""
        index = self._properties_ui.treeView_files.currentIndex()
        if not index.isValid():
            for row, item in enumerate(self._file_model.files):
                if item.exists():
                    index = self._file_model.index(row, 0)
                    self._properties_ui.treeView_files.setCurrentIndex(index)
                    break
        self.open_import_editor(index)

    @Slot(QModelIndex)
    def _handle_files_double_clicked(self, index):
        """Opens Import editor for the double clicked index."""
        self.open_import_editor(index)

    def open_import_editor(self, index):
        """Opens Import editor for the given index."""
        label = index.data()
        if label is None:
            filepath = None
        else:
            file_item = self._file_model.find_file(label)
            filepath = file_item.path
            if not file_item.exists():
                self._logger.msg_error.emit("File does not exist yet.")
                self._file_model.mark_as_nonexistent(index)
                filepath = None
            elif not os.path.exists(filepath):
                self._logger.msg_error.emit(f"Cannot find file '{filepath}'.")
                self._file_model.mark_as_nonexistent(index)
                filepath = None
        self._toolbox.show_specification_form(self.item_type(), self.specification(), filepath=filepath)

    def select_connector_type(self, index):
        """Opens dialog to select connector type for the given index."""
        # FIXME: Move this to a file menu option in Import editor maybe
        importee = index.data()
        connector = self.get_connector(importee)
        if not connector:
            # Aborted by the user
            return
        settings = self.get_settings(importee)
        settings["source_type"] = connector.__name__

    @Slot(bool, str)
    def _push_file_selection_change_to_undo_stack(self, selected, label):
        """Makes changes to file selection undoable."""
        self._toolbox.undo_stack.push(ChangeItemSelectionCommand(self, selected, label))

    def _do_handle_dag_changed(self, resources, _):
        """See base class."""
        if not self.specification():
            self.add_notification(
                "This Importer does not have a specification. Set it in the Importer Properties Panel."
            )
        self._file_model.update(resources)
        self._notify_if_duplicate_file_paths()
        if self._file_model.rowCount() == 0:
            self.add_notification(
                "This Importer does not have any input data. "
                "Connect Data Connections to this Importer to use their data as input."
            )

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        if not self.specification():
            d["specification"] = ""
        else:
            d["specification"] = self.specification().name
        d["cancel_on_error"] = self.cancel_on_error
        d["file_selection"] = serialize_checked_states(self._file_model.files, self._project.project_dir)
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project, logger):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        specification_name = item_dict.get("specification", "")
        cancel_on_error = item_dict.get("cancel_on_error", False)
        file_selection = item_dict.get("file_selection")
        file_selection = deserialize_checked_states(file_selection, project.project_dir)
        return Importer(
            name, description, x, y, toolbox, project, logger, specification_name, cancel_on_error, file_selection
        )

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Connection":
            self._logger.msg.emit(
                "Link established. You can define mappings on data from "
                f"<b>{source_item.name}</b> using item <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Tool":
            self._logger.msg.emit(
                "Link established. You can define mappings on output files from "
                f"<b>{source_item.name}</b> using item <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Data Store":
            self._logger.msg.emit("Link established")
        elif source_item.item_type() == "Gimlet":
            self._logger.msg.emit(
                "Link established. You can define mappings on output files from "
                f"<b>{source_item.name}</b> using item <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    @staticmethod
    def default_name_prefix():
        """see base class"""
        return "Importer"

    def _notify_if_duplicate_file_paths(self):
        """Adds a notification if file_list contains duplicate entries."""
        labels = list()
        for item in self._file_model.files:
            labels.append(item.label)
        file_counter = Counter(labels)
        duplicates = list()
        for label, count in file_counter.items():
            if count > 1:
                duplicates.append(label)
        if duplicates:
            self.add_notification("Duplicate input files from upstream items:<br>{}".format("<br>".join(duplicates)))

    @staticmethod
    def upgrade_from_no_version_to_version_1(item_name, old_item_dict, old_project_dir):
        """Converts mappings to a list, where each element contains two dictionaries,
        the serialized path dictionary and the mapping dictionary for the file in that
        path."""
        new_importer = dict(old_item_dict)
        mappings = new_importer.get("mappings", {})
        list_of_mappings = list()
        paths = list(mappings.keys())
        for path in paths:
            mapping = mappings[path]
            if "source_type" in mapping and mapping["source_type"] == "CSVConnector":
                _fix_csv_connector_settings(mapping)
            new_path = serialize_path(path, old_project_dir)
            if new_path["relative"]:
                new_path["path"] = os.path.join(".spinetoolbox", "items", new_path["path"])
            list_of_mappings.append([new_path, mapping])
        new_importer["mappings"] = list_of_mappings
        return new_importer

    @staticmethod
    def upgrade_v1_to_v2(item_name, item_dict):
        """Upgrades item's dictionary from v1 to v2.

        Changes:
        - if file_selection does not exist or if it
        is a list of booleans, reset file_selection
        to an empty list.

        Args:
            item_name (str): item's name
            item_dict (dict): Version 1 item dictionary

        Returns:
            dict: Version 2 Exporter dictionary
        """
        try:
            file_selection = item_dict["file_selection"]
        except KeyError:
            item_dict["file_selection"] = list()
            return item_dict
        if len(file_selection) == 0:
            return item_dict
        if isinstance(file_selection[0], bool):
            item_dict["file_selection"] = list()
        return item_dict

    @staticmethod
    def upgrade_v2_to_v3(item_name, item_dict, project_upgrader):
        """
        Upgrades item's dictionary from v2 to v3.

        1. Get rid of "mappings" in favor of "specification".
           The "mappings" are being turned into specifications by the project_upgrader
        2. Rename "mapping_selection" to "file_selection"

        Args:
            item_name (str): item's name
            item_dict (dict): Version 1 item dictionary
            project_upgrader (ProjectUpgrader)

        Returns:
            dict: Version 2 item dictionary
        """
        mappings = item_dict["mappings"]
        mapping = next(iter(mappings), None)
        if mapping is None:
            specification_name = ""
        else:
            label, _ = mapping
            specification_name = project_upgrader.make_unique_importer_specification_name(item_name, label, 0)
        new_item_dict = {k: v for k, v in item_dict.items() if k != "mappings"}
        new_item_dict["specification"] = specification_name
        new_item_dict["file_selection"] = item_dict.pop("mapping_selection")
        return new_item_dict


def _fix_csv_connector_settings(settings):
    """CSVConnector saved the table names as the filepath, change that
    to 'csv' instead. This function will mutate the dictionary.

    Args:
        settings (dict): Mapping settings that should be updated
    """
    table_mappings = settings.get("table_mappings", {})
    k = list(table_mappings)
    if len(k) == 1 and k[0] != "csv":
        table_mappings["csv"] = table_mappings.pop(k[0])

    table_types = settings.get("table_types", {})
    k = list(table_types.keys())
    if len(k) == 1 and k[0] != "csv":
        table_types["csv"] = table_types.pop(k[0])

    table_row_types = settings.get("table_row_types", {})
    k = list(table_row_types.keys())
    if len(k) == 1 and k[0] != "csv":
        table_row_types["csv"] = table_row_types.pop(k[0])

    table_options = settings.get("table_options", {})
    k = list(table_options.keys())
    if len(k) == 1 and k[0] != "csv":
        table_options["csv"] = table_options.pop(k[0])

    selected_tables = settings.get("selected_tables", [])
    if len(selected_tables) == 1 and selected_tables[0] != "csv":
        selected_tables.pop(0)
        selected_tables.append("csv")
