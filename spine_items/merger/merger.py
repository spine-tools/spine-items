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
Module for Merger class.

:authors: P. Savolainen (VTT), M. Marin (KTH)
:date:   18.12.2017
"""

import os
from PySide2.QtCore import Qt, Slot, QObject
from PySide2.QtWidgets import QDialog

from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.helpers import create_dir
from ..commands import UpdateCancelOnErrorCommand, UpdatePurgeBeforeWritingCommand, UpdatePurgeSettings
from .executable_item import ExecutableItem
from .item_info import ItemInfo
from ..widgets import PurgeSettingsDialog


class Merger(ProjectItem):
    def __init__(
        self,
        name,
        description,
        x,
        y,
        toolbox,
        project,
        cancel_on_error=False,
        purge_before_writing=False,
        purge_settings=None,
    ):
        """Data Store class.

        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            toolbox (ToolboxUI): QMainWindow instance
            project (SpineToolboxProject): the project this item belongs to
            cancel_on_error (bool): if True, changes will be reverted on errors
            purge_before_writing (bool): if True the item will purge target dbs before running
            purge_settings (dict): mapping from database item name to purge flag
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self.logs_dir = os.path.join(self.data_dir, "logs")
        try:
            create_dir(self.logs_dir)
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory {self.logs_dir} failed. Check permissions.")
        self.cancel_on_error = cancel_on_error
        self._purge_before_writing = purge_before_writing
        self._purge_settings = purge_settings
        self._purge_settings_dialog = None

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

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.cancel_on_error_checkBox.stateChanged] = self._handle_cancel_on_error_changed
        s[self._properties_ui.checkBox_purge_before_writing.stateChanged] = self._handle_purge_before_writing_changed
        s[self._properties_ui.purge_settings_button.clicked] = self._open_purge_settings_dialog
        return s

    def restore_selections(self):
        """Load url into selections."""
        self._properties_ui.cancel_on_error_checkBox.setCheckState(Qt.Checked if self.cancel_on_error else Qt.Unchecked)
        self._properties_ui.checkBox_purge_before_writing.setCheckState(
            Qt.Checked if self._purge_before_writing else Qt.Unchecked
        )
        self._properties_ui.purge_settings_button.setEnabled(self._purge_before_writing)

    def project(self):
        """Returns current project or None if no project open."""
        return self._project

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

    @Slot(int)
    def _handle_purge_before_writing_changed(self, _state):
        purge_before_writing = self._properties_ui.checkBox_purge_before_writing.isChecked()
        if self._purge_before_writing == purge_before_writing:
            return
        self._toolbox.undo_stack.push(UpdatePurgeBeforeWritingCommand(self, purge_before_writing))
        self._properties_ui.purge_settings_button.setEnabled(purge_before_writing)

    def set_purge_before_writing(self, purge_before_writing):
        """Sets purge_before_writing setting.

        Args:
            purge_before_writing (bool): purge_before_writing flag
        """
        self._purge_before_writing = purge_before_writing
        if not self._active:
            return
        check_state = Qt.Checked if self._purge_before_writing else Qt.Unchecked
        self._properties_ui.checkBox_purge_before_writing.blockSignals(True)
        self._properties_ui.checkBox_purge_before_writing.setCheckState(check_state)
        self._properties_ui.checkBox_purge_before_writing.blockSignals(False)

    @Slot(bool)
    def _open_purge_settings_dialog(self, _=False):
        """Opens the purge settings dialog."""
        if self._purge_settings_dialog is not None:
            self._purge_settings_dialog.raise_()
            return
        self._purge_settings_dialog = PurgeSettingsDialog(self._purge_settings, self._toolbox)
        self._purge_settings_dialog.accepted.connect(self._handle_purge_settings_changed)
        self._purge_settings_dialog.destroyed.connect(self._clean_up_purge_settings_dialog)
        self._purge_settings_dialog.show()

    @Slot()
    def _handle_purge_settings_changed(self):
        """Pushes a command that sets new purge settings onto undo stack."""
        purge_settings = self._purge_settings_dialog.get_purge_settings()
        if purge_settings == self._purge_settings:
            return
        self._toolbox.undo_stack.push(UpdatePurgeSettings(self, purge_settings, self._purge_settings))

    @Slot(QObject)
    def _clean_up_purge_settings_dialog(self, _):
        """Cleans up purge settings dialog."""
        self._purge_settings_dialog = None

    def set_purge_settings(self, settings):
        """Sets purge settings.

        Args:
            settings (dict): purge settings; mapping from database item type to purge flag
        """
        self._purge_settings = settings

    def predecessor_data_stores(self):
        for name in self._project.predecessor_names(self.name):
            item = self._project.get_item(name)
            if item.item_type() == "Data Store":
                yield item

    def successor_data_stores(self):
        for name in self._project.successor_names(self.name):
            item = self._project.get_item(name)
            if item.item_type() == "Data Store":
                yield item

    @Slot(object, object)
    def handle_execution_successful(self, execution_direction, engine_state):
        """Notifies Toolbox of successful database import."""
        if execution_direction != "FORWARD":
            return
        committed_db_maps = set()
        for successor in self.successor_data_stores():
            url = successor.sql_alchemy_url()
            db_map = self._toolbox.db_mngr.db_map(url)
            if db_map:
                committed_db_maps.add(db_map)
        if committed_db_maps:
            cookie = self
            self._toolbox.db_mngr.session_committed.emit(committed_db_maps, cookie)

    def upstream_resources_updated(self, resources):
        self._check_notifications()

    def downstream_resources_updated(self, resources):
        self._check_notifications()

    def _check_notifications(self):
        self.clear_notifications()
        if not list(self.predecessor_data_stores()):
            self.add_notification(
                "This Merger does not have any input Data Stores. "
                "Connect Data Stores to this to merge their data into output Data Stores."
            )
        if not list(self.successor_data_stores()):
            self.add_notification(
                "This Merger does not have any output Data Stores. "
                "Connect this to Data Stores to merge input Data Stores data into them."
            )
        # FIXME

    def item_dict(self):
        """Returns a dictionary corresponding to this item."""
        d = super().item_dict()
        d["cancel_on_error"] = self.cancel_on_error
        d["purge_before_writing"] = self._purge_before_writing
        if self._purge_settings is not None:
            d["purge_settings"] = self._purge_settings
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        """See base class."""
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        cancel_on_error = item_dict.get("cancel_on_error", False)
        purge_before_writing = item_dict.get("purge_before_writing", False)
        purge_settings = item_dict.get("purge_settings")
        return Merger(name, description, x, y, toolbox, project, cancel_on_error, purge_before_writing, purge_settings)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Data Store":
            dst_ds_names = ", ".join(x.name for x in self.successor_data_stores())
            self._logger.msg.emit(
                "Link established. "
                f"Data from <b>{source_item.name}</b> will be merged into <b>{dst_ds_names}</b> upon execution."
            )
        else:
            super().notify_destination(source_item)
