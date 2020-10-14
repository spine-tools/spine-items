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
Contains the :class:`SignallingSettingsPack` class.

:author: A. Soininen (VTT)
:date:   14.10.2020
"""
from PySide2.QtCore import QObject, Signal, Slot
from spinedb_api import SpineDBAPIError
from spinetoolbox.spine_io.exporters import gdx
from .db_utils import scenario_filtered_database_map
from .notifications import Notifications
from .settings_pack import SettingsPack
from .settings_state import SettingsState


class SignallingSettingsPack(SettingsPack, QObject):
    """
    This settings pack uses Qt signals to communicate state changes.

    Attributes:
        settings_window (GdxExportSettings): settings editor window
        notifications (Notifications): current error conditions
    """

    state_changed = Signal(object)
    """Emitted when the pack's state changes."""

    def __init__(self, output_file_name):
        """
        Args:
            output_file_name (str): name of the export file
        """
        SettingsPack.__init__(self, output_file_name)
        QObject.__init__(self)
        self.settings_window = None
        self.notifications = Notifications()
        self.state_changed.connect(self.notifications.update_settings_state)

    @SettingsPack.state.setter
    def state(self, state):
        self._state = state
        self.state_changed.emit(state)

    def to_nonsignalling(self):
        """
        Returns a vanilla :class:`SettingsPack` instance.

        Returns:
            SettingsPack: a cloned settings pack
        """
        pack = SettingsPack(self.output_file_name)
        pack.settings = self.settings
        pack.indexing_settings = self.indexing_settings
        pack.merging_settings = self.merging_settings
        pack.none_fallback = self.none_fallback
        pack.none_export = self.none_export
        pack.scenario = self.scenario
        pack.last_database_commit = self.last_database_commit
        pack.state = self._state

        return pack

    @classmethod
    def _indexing_settings_from_dict(cls, pack_dict, pack, database_url, logger):
        """Restores indexing settings from dict."""
        try:
            db_map = scenario_filtered_database_map(database_url, pack.scenario)
        except SpineDBAPIError as error:
            logger.msg_error.emit(
                f"Failed to fully restore Exporter settings. Error while reading database '{database_url}': {error}"
            )
            pack.state = SettingsState.ERROR
            return False
        try:
            value_type_logger = _UnsupportedValueTypeLogger(
                f"Exporter settings ignoring some parameters from database '{database_url}':", logger
            )
            pack.indexing_settings = gdx.indexing_settings_from_dict(
                pack_dict["indexing_settings"], db_map, pack.none_fallback, value_type_logger
            )
        except SpineDBAPIError as error:
            logger.msg_error.emit(
                f"Failed to fully restore Exporter settings. Error while reading database '{database_url}': {error}"
            )
            pack.state = SettingsState.ERROR
            return False
        finally:
            db_map.connection.close()
        return True


class _UnsupportedValueTypeLogger(QObject):
    msg = Signal(str)
    msg_warning = Signal(str)
    msg_error = Signal(str)

    def __init__(self, preample, real_logger):
        super().__init__()
        self._preample = preample
        self._logger = real_logger
        self.msg.connect(self.relay_message)
        self.msg_warning.connect(self.relay_warning)
        self.msg_error.connect(self.relay_error)

    @Slot(str)
    def relay_message(self, text):
        self._logger.msg.emit(self._preample + " " + text)

    @Slot(str)
    def relay_warning(self, text):
        self._logger.msg_warning.emit(self._preample + " " + text)

    @Slot(str)
    def relay_error(self, text):
        self._logger.msg_error.emit(self._preample + " " + text)
