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
Contains base class for project items.

:author: A. Soininen (VTT)
:date:   15.12.2020
"""

from PySide2.QtCore import Qt, Slot
from spinetoolbox.project_item.project_item import ProjectItem
from .commands import UpdateCancelOnErrorCommand, UpdateOutputTimeStampsFlag
from .models import FullUrlListModel


class ExporterBase(ProjectItem):
    """A base class for exporter project items."""

    def __init__(self, name, description, x, y, toolbox, project, output_time_stamps=False, cancel_on_error=True):
        """
        Args:
            name (str): item name
            description (str): item description
            x (float): initial X coordinate of item icon
            y (float): initial Y coordinate of item icon
            toolbox (ToolboxUI): a ToolboxUI instance
            project (SpineToolboxProject): the project this item belongs to
            output_time_stamps (bool): True if time stamps should be appended to output directory names,
                False otherwise
            cancel_on_error (bool): True if execution should fail on all export errors,
                False to ignore certain error cases; optional to provide backwards compatibility
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self._append_output_time_stamps = output_time_stamps
        self._cancel_on_error = cancel_on_error
        self._output_filenames = dict()
        self._export_list_items = dict()
        self._full_url_model = FullUrlListModel()
        self._exported_files = None

    @staticmethod
    def item_type():
        """See base class."""
        raise NotImplementedError()

    @staticmethod
    def item_category():
        """See base class."""
        raise NotImplementedError()

    @property
    def executable_class(self):
        raise NotImplementedError()

    def handle_execution_successful(self, execution_direction, engine_state):
        """See base class."""
        if execution_direction != "FORWARD":
            return
        self._resources_to_successors_changed()

    def full_url_model(self):
        """
        Returns the full URL model held by the exporter.

        Returns:
            FullUrlListModel: full URL model
        """
        return self._full_url_model

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.open_directory_button.clicked] = lambda _: self.open_directory()
        s[self._properties_ui.output_time_stamps_check_box.stateChanged] = self._change_output_time_stamps_flag
        s[self._properties_ui.cancel_on_error_check_box.stateChanged] = self._cancel_on_error_option_changed
        return s

    def restore_selections(self):
        """Restores selections and connects signals."""
        self._update_properties_tab()

    @Slot(int)
    def _change_output_time_stamps_flag(self, checkbox_state):
        """
        Pushes a command that changes the output time stamps flag value.

        Args:
            checkbox_state (int): setting's checkbox state on properties tab
        """
        flag = checkbox_state == Qt.Checked
        if flag == self._append_output_time_stamps:
            return
        self._toolbox.undo_stack.push(UpdateOutputTimeStampsFlag(self, flag))

    def set_output_time_stamps_flag(self, flag):
        """
        Sets the output time stamps flag.

        Args:
            flag (bool): flag value
        """
        self._append_output_time_stamps = flag

    @Slot(int)
    def _cancel_on_error_option_changed(self, checkbox_state):
        """Handles changes to the Cancel export on error option."""
        cancel = checkbox_state == Qt.Checked
        if self._cancel_on_error == cancel:
            return
        self._toolbox.undo_stack.push(UpdateCancelOnErrorCommand(self, cancel))

    def set_cancel_on_error(self, cancel):
        """Sets the Cancel export on error option."""
        self._cancel_on_error = cancel
        if not self._active:
            return
        # This does not trigger the stateChanged signal.
        self._properties_ui.cancel_on_error_check_box.setCheckState(Qt.Checked if cancel else Qt.Unchecked)

    def item_dict(self):
        """Returns a dictionary corresponding to this item's configuration."""
        d = super().item_dict()
        d["output_time_stamps"] = self._append_output_time_stamps
        d["cancel_on_error"] = self._cancel_on_error
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class"""
        raise NotImplementedError()

    def tear_down(self):
        super().tear_down()
        self._full_url_model.deleteLater()
