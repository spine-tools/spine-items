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

"""Contains the :class:`DataTransformer` project item."""
from json import dump
from PySide6.QtCore import Slot
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.widgets.custom_menus import ItemSpecificationMenu
from .item_info import ItemInfo
from .executable_item import ExecutableItem
from .filter_config_path import filter_config_path
from .output_resources import scan_for_resources


class DataTransformer(ProjectItem):
    """Data transformer project item."""

    def __init__(self, name, description, x, y, toolbox, project, specification_name=""):
        """
        Args:
            name (str): item's name
            description (str): item's description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (QWidget): parent window
            project (SpineToolboxProject): the project this item belongs to
            specification_name (str, optional): transformer specification
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self._specification_name = specification_name
        self._specification = self._project.get_specification(specification_name)
        if specification_name and not self._specification:
            self._logger.msg_error.emit(
                f"Data Transformer <b>{self.name}</b> should have a specification <b>{specification_name}</b> but it was not found"
            )
        self._db_resources = []

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

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
        specification_name = item_dict["specification"]
        return DataTransformer(name, description, x, y, toolbox, project, specification_name)

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.specification_button.clicked] = self.show_specification_window
        s[self._properties_ui.specification_combo_box.textActivated] = self._change_specification
        return s

    def do_set_specification(self, specification):
        """see base class"""
        self._dump_filter_configs()
        old_resources = scan_for_resources(
            self, self.specification(), self._db_resources, filter_config_path(self.data_dir)
        )
        if not super().do_set_specification(specification):
            return False
        self._specification_name = specification.name if specification is not None else ""
        if self._active:
            self._update_ui()
        self._dump_filter_configs()
        new_resources = scan_for_resources(
            self, self.specification(), self._db_resources, filter_config_path(self.data_dir)
        )
        self._resources_to_successors_replaced(old_resources, new_resources)
        self._check_notifications()
        return True

    def _dump_filter_configs(self):
        """writes filter configs to disk."""
        if self._specification is not None and self._specification.settings is not None:
            path = filter_config_path(self.data_dir)
            with open(path, "w") as filter_config_file:
                dump(self._specification.settings.filter_config(), filter_config_file)

    @Slot(bool)
    def show_specification_window(self, _=True):
        """Opens the settings window."""
        self._toolbox.show_specification_form(
            self.item_type(), self.specification(), item=self, urls=[r.url for r in self._db_resources]
        )

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

    @Slot(str)
    def _change_specification(self, specification_name):
        """
        Pushes a set specification command to the undo stack.

        Args:
            specification_name (str): new specification name
        """
        specification = self._project.get_specification(specification_name)
        self.set_specification(specification)

    def upstream_resources_updated(self, resources):
        """See base class."""
        self._db_resources = [r for r in resources if r.type_ == "database"]
        self._resources_to_successors_changed()

    def replace_resources_from_upstream(self, old, new):
        """See base class."""
        old_resources = scan_for_resources(
            self, self.specification(), self._db_resources, filter_config_path(self.data_dir)
        )
        for old_resource, new_resource in zip(old, new):
            for i, resource in enumerate(self._db_resources):
                if resource == old_resource:
                    self._db_resources[i] = new_resource
                    break
        new_resources = scan_for_resources(
            self, self.specification(), self._db_resources, filter_config_path(self.data_dir)
        )
        self._resources_to_successors_replaced(old_resources, new_resources)

    def resources_for_direct_successors(self):
        """See base class."""
        return scan_for_resources(self, self.specification(), self._db_resources, filter_config_path(self.data_dir))

    def restore_selections(self):
        """See base class."""
        self._update_ui()

    def _update_ui(self):
        if self._specification_name:
            self._properties_ui.specification_combo_box.setCurrentText(self._specification_name)
            spec_model_index = self._toolbox.specification_model.specification_index(self._specification_name)
            specification_options_popup_menu = ItemSpecificationMenu(self._toolbox, spec_model_index, self)
            self._properties_ui.specification_button.setMenu(specification_options_popup_menu)
        else:
            self._properties_ui.specification_combo_box.setCurrentIndex(-1)
            self._properties_ui.specification_button.setMenu(None)

    def _check_notifications(self):
        self.clear_notifications()
        if self._specification is not None:
            report = self._specification.settings.report_inconsistencies()
            for message in report:
                self.add_notification(message)
