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

"""Module for Merger class."""
import os
from PySide6.QtCore import Qt, Slot
from spinetoolbox.helpers import create_dir
from ..commands import UpdateCancelOnErrorCommand
from ..db_writer_item_base import DBWriterItemBase
from .executable_item import ExecutableItem
from .item_info import ItemInfo


class Merger(DBWriterItemBase):
    def __init__(self, name, description, x, y, toolbox, project, cancel_on_error=False):
        """Data Store class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            cancel_on_error (bool): if True, changes will be reverted on errors
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self.logs_dir = os.path.join(self.data_dir, "logs")
        try:
            create_dir(self.logs_dir)
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory {self.logs_dir} failed. Check permissions.")
        self.cancel_on_error = cancel_on_error

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @property
    def executable_class(self):
        return ExecutableItem

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.cancel_on_error_checkBox.stateChanged] = self._handle_cancel_on_error_changed
        return s

    def restore_selections(self):
        """Load url into selections."""
        self._properties_ui.cancel_on_error_checkBox.setCheckState(
            Qt.CheckState.Checked if self.cancel_on_error else Qt.CheckState.Unchecked
        )

    def project(self):
        """Returns current project or None if no project open."""
        return self._project

    @Slot(int)
    def _handle_cancel_on_error_changed(self, _state):
        cancel_on_error = self._properties_ui.cancel_on_error_checkBox.isChecked()
        if self.cancel_on_error == cancel_on_error:
            return
        self._toolbox.undo_stack.push(UpdateCancelOnErrorCommand(self.name, cancel_on_error, self._project))

    def set_cancel_on_error(self, cancel_on_error):
        self.cancel_on_error = cancel_on_error
        if not self._active:
            return
        check_state = Qt.CheckState.Checked if self.cancel_on_error else Qt.CheckState.Unchecked
        self._properties_ui.cancel_on_error_checkBox.blockSignals(True)
        self._properties_ui.cancel_on_error_checkBox.setCheckState(check_state)
        self._properties_ui.cancel_on_error_checkBox.blockSignals(False)

    def predecessor_data_stores(self):
        for name in self._project.predecessor_names(self.name):
            item = self._project.get_item(name)
            if item.item_type() == "Data Store":
                yield item

    def predecessor_data_transformers(self):
        for name in self._project.predecessor_names(self.name):
            item = self._project.get_item(name)
            if item.item_type() == "Data Transformer":
                yield item

    def upstream_resources_updated(self, resources):
        self._check_notifications()

    def downstream_resources_updated(self, resources):
        self._check_notifications()

    def _check_notifications(self):
        self.clear_notifications()
        self._check_write_index()
        if not (list(self.predecessor_data_stores()) or list(self.predecessor_data_transformers())):
            self.add_notification(
                "This Merger does not have any input Data Stores or Data Transformers. "
                "Connect Data Stores/Transformers to this to merge their data into output Data Stores/Transformers."
            )
        if not list(self.successor_data_stores()):
            self.add_notification(
                "This Merger does not have any output Data Stores. "
                "Connect this to Data Stores to merge input Data Stores/Transformers data into them."
            )

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["cancel_on_error"] = self.cancel_on_error
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = DBWriterItemBase.parse_item_dict(item_dict)
        cancel_on_error = item_dict.get("cancel_on_error", False)
        return Merger(name, description, x, y, toolbox, project, cancel_on_error)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            dst_ds_names = ", ".join(x.name for x in self.successor_data_stores())
            if dst_ds_names:
                self._logger.msg.emit(
                    "Link established. "
                    f"Data from <b>{source_item.name}</b> will be merged into <b>{dst_ds_names}</b> upon execution."
                )
            else:
                self._logger.msg.emit("Link established. " f"<b>{self.name} is missing output database, though.</b>")
        else:
            super().notify_destination(source_item)
