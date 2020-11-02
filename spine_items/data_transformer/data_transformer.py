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
Contains the :class:`DataTransformer` project item.

:authors: A. Soininen (VTT)
:date:    2.10.2020
"""
from json import dump
from pathlib import Path
from PySide2.QtCore import Slot
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.project_item.project_item_resource import ProjectItemResource
from spinedb_api import append_filter_config, config_to_shorthand
from .item_info import ItemInfo
from .executable_item import ExecutableItem
from .filter_config_path import filter_config_path
from .widgets.specification_editor_window import SpecificationEditorWindow


class DataTransformer(ProjectItem):
    """Data transformer project item."""

    def __init__(self, name, description, x, y, toolbox, project, logger, specification_name=None):
        """
        Args:
            name (str): item's name
            description (str): item's description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (QWidget): parent window
            project (SpineToolboxProject): the project this item belongs to
            logger (LoggerInterface): a logger instance
            specification_name (str, optional): transformer specification
        """
        super().__init__(name, description, x, y, project, logger)
        self._toolbox = toolbox
        self._specification_name = specification_name
        self._specification = self._toolbox.specification_model.find_specification(specification_name)
        if specification_name and not self._specification:
            self._logger.msg_error.emit(
                f"Data Transformer <b>{self.name}</b> should have a specification <b>{specification_name}</b> but it was not found"
            )
        self.do_set_specification(self._specification)
        self._urls = []

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
        specification = self._toolbox.specification_model.find_specification(self._specification_name)
        if specification is None:
            return ExecutableItem(self.name, None, "", self._logger)
        path = filter_config_path(self.data_dir)
        return ExecutableItem(self.name, specification, path, self._logger)

    def item_dict(self):
        """See base class."""
        serialized = super().item_dict()
        serialized["specification"] = self._specification_name
        return serialized

    @staticmethod
    def from_dict(name, item_dict, toolbox, project, logger):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        specification_name = item_dict["specification"]
        specification = toolbox.specification_model.find_specification(specification_name)
        if specification_name and not specification:
            logger.msg_error.emit(f"Data transformer <b>{name}</b> specification <b>{specification_name}</b> not found")
        return DataTransformer(name, description, x, y, toolbox, project, logger, specification_name)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.open_dir_button.clicked] = lambda checked=False: self.open_directory()
        s[self._properties_ui.specification_button.clicked] = self.show_specification_window
        s[self._properties_ui.specification_combo_box.currentTextChanged] = self._change_specification
        return s

    def do_set_specification(self, specification):
        """see base class"""
        super().do_set_specification(specification)
        if specification is None:
            if self._active:
                self._properties_ui.specification_combo_box.setCurrentIndex(-1)
            return
        self._specification_name = specification.name
        if self._active:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        path = filter_config_path(self.data_dir)
        if specification.settings is not None:
            with open(path, "w") as filter_config_file:
                dump(specification.settings.filter_config(), filter_config_file)
        self.item_changed.emit()

    def update_name_label(self):
        """Update properties tab name label. Used only when renaming project items."""
        self._properties_ui.item_name_label.setText(self.name)

    @Slot(bool)
    def show_specification_window(self, _=True):
        """Opens the settings window."""
        specification = self._toolbox.specification_model.find_specification(self._specification_name)
        specification_window = SpecificationEditorWindow(self._toolbox, specification, self._urls, self.name)
        specification_window.accepted.connect(self._change_specification)
        specification_window.show()

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            self._logger.msg.emit(
                "Link established. You can now define transformations for Data Store "
                f"<b>{source_item.name}</b> in Data Transformer <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Data Transformer":
            self._logger.msg.emit(
                "Link established. You can now define additional transformations "
                f"in Data Transformer <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    @staticmethod
    def default_name_prefix():
        """see base class"""
        return "Data Transformer"

    @Slot(str)
    def _change_specification(self, specification_name):
        """
        Pushes a set specification command to the undo stack.

        Args:
            specification_name (str): new specification name
        """
        specification = self._toolbox.specification_model.find_specification(specification_name)
        self.set_specification(specification)

    def _do_handle_dag_changed(self, resources):
        """See base class."""
        self._urls = [r.url for r in resources if r.type_ == "database"]

    def resources_for_direct_successors(self):
        """See base class."""
        specification = self._toolbox.specification_model.find_specification(self._specification_name)
        if specification is None or specification.settings is None:
            return [ProjectItemResource(self, "database", url) for url in self._urls]
        if specification.settings.use_shorthand:
            shorthand = config_to_shorthand(specification.settings.filter_config())
            return [ProjectItemResource(self, "database", append_filter_config(url, shorthand)) for url in self._urls]
        path = Path(filter_config_path(self.data_dir))
        with open(path, "w") as filter_config_file:
            dump(specification.settings.filter_config(), filter_config_file)
        return [ProjectItemResource(self, "database", append_filter_config(url, path)) for url in self._urls]

    def restore_selections(self):
        """See base class."""
        self._properties_ui.item_name_label.setText(self.name)
        if self._specification_name:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
        else:
            self._properties_ui.specification_combo_box.setCurrentIndex(-1)
