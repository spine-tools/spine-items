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
Contains the :class:`Exporter` project item.

:authors: A. Soininen (VTT)
:date:    10.12.2020
"""
from itertools import zip_longest
from pathlib import Path

from PySide2.QtCore import Slot
from spinetoolbox.project_item.project_item import ProjectItem
from spine_engine.utils.serialization import deserialize_path
from spinedb_api import clear_filter_configs
from ..utils import (
    Database,
    EXPORTED_PATHS_FILE_NAME,
    EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX,
    _write_exported_files_file,
)
from ..item_base import ExporterBase
from .item_info import ItemInfo
from .executable_item import ExecutableItem


class Exporter(ExporterBase):
    """Exporter project item."""

    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        specification_name=None,
        databases=None,
        output_time_stamps=False,
        cancel_on_error=True,
    ):
        """
        Args:
            name (str): item's name
            description (str): item's description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (QWidget): parent window
            project (SpineToolboxProject): the project this item belongs to
            specification_name (str, optional): exporter specification
        """
        super().__init__(name, description, x, y, toolbox, project, databases, output_time_stamps, cancel_on_error)
        self._specification_name = specification_name
        self._specification = self._project.get_specification(specification_name)
        if specification_name and not self._specification:
            self._toolbox.msg_error.emit(
                f"Exporter <b>{self.name}</b> should have a specification <b>{specification_name}</b> but it was not found"
            )
        self.do_set_specification(self._specification)

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @staticmethod
    def item_category():
        """See base class."""
        return ItemInfo.item_category()

    @property
    def executable_class(self):
        return ExecutableItem

    def item_dict(self):
        """See base class."""
        serialized = super().item_dict()
        serialized["specification"] = self._specification_name
        return serialized

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        databases = list()
        for db_dict in item_dict.get("databases", []):
            db = Database.from_dict(db_dict)
            db.url = clear_filter_configs(deserialize_path(db_dict["database_url"], project.project_dir))
            databases.append(db)
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        specification_name = item_dict.get("specification", "")
        specification = project.get_specification(specification_name)
        if specification_name and not specification:
            toolbox.msg_error.emit(f"Exporter <b>{name}</b> specification <b>{specification_name}</b> not found")
        return Exporter(
            name,
            description,
            x,
            y,
            toolbox,
            project,
            specification_name,
            databases,
            output_time_stamps,
            cancel_on_error,
        )

    def rename(self, new_name, rename_data_dir_message):
        """See base class."""
        if not super().rename(new_name, rename_data_dir_message):
            return False
        try:
            Path(self.data_dir, EXPORTED_PATHS_FILE_NAME).unlink()
        except FileNotFoundError:
            pass
        for path in Path(self.data_dir).iterdir():
            if path.name.startswith(EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX) and path.suffix == ".json":
                path.unlink()
        if self._exported_files is not None:
            data_dir_parts = Path(self.data_dir).parts
            for label, file_list in self._exported_files.items():
                new_file_list = list()
                for file_path in file_list:
                    new_file_path = Path()
                    for old_part, new_part in zip_longest(Path(file_path).parts, data_dir_parts):
                        if new_part is None:
                            new_file_path = new_file_path / old_part
                        else:
                            new_file_path = new_file_path / new_part
                    new_file_list.append(str(new_file_path))
                self._exported_files[label] = new_file_list
            exported_file_path = Path(self.data_dir, EXPORTED_PATHS_FILE_NAME)
            _write_exported_files_file(exported_file_path, self._exported_files, self.data_dir)
        return True

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.specification_button.clicked] = self.show_specification_window
        s[self._properties_ui.specification_combo_box.textActivated] = self._change_specification
        return s

    def _check_missing_specification(self):
        """Checks specification's status."""
        self._notifications.missing_specification = not self._specification_name

    def do_set_specification(self, specification):
        """see base class"""
        if not super().do_set_specification(specification):
            return False
        if specification is None:
            if self._active:
                self._properties_ui.specification_combo_box.setCurrentIndex(-1)
            return True
        self._specification_name = specification.name
        self._check_notifications()
        if self._active:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        return True

    @Slot(bool)
    def show_specification_window(self, _=True):
        """Opens the settings window."""
        self._toolbox.show_specification_form(self.item_type(), self.specification(), self)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._toolbox.msg.emit(
                "Link established. You can now export the database in "
                f"<b>{source_item.name}</b> in <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Data Transformer":
            self._toolbox.msg.emit(
                f"Link established. You can now export the database transformed by <b>{source_item.name}</b> "
                f"in <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    @Slot(str)
    def _change_specification(self, specification_name):
        """
        Pushes a set specification command to the undo stack.

        Args:
            specification_name (str): new specification name
        """
        specification = self._project.get_specification(specification_name)
        self.set_specification(specification)

    def restore_selections(self):
        """See base class."""
        super().restore_selections()
        if self._specification_name:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        else:
            self._properties_ui.specification_combo_box.setCurrentIndex(-1)
