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
Contains the SettingsPack class.

:author: A. Soininen (VTT)
:date:   6.5.2020
"""
from spine_engine.spine_io.exporters import gdx
from .notifications import Notifications


class SettingsPack:
    """
    Keeper of all settings and stuff needed for exporting a database.

    Attributes:
        settings (gdx.SetSettings): export settings
        indexing_settings (dict): parameter indexing settings
        merging_settings (dict): parameter merging settings
        none_fallback (NoneFallback): fallback for None parameter values
        none_export (NoneExport): how to handle None values while exporting
    """

    def __init__(self):
        self.settings = None
        self.indexing_settings = None
        self.merging_settings = dict()
        self.none_fallback = gdx.NoneFallback.USE_IT
        self.none_export = gdx.NoneExport.DO_NOT_EXPORT
        self.notifications = Notifications()

    def to_dict(self):
        """Stores the settings pack into a JSON compatible dictionary."""
        d = dict()
        d["settings"] = self.settings.to_dict() if self.settings is not None else None
        d["indexing_settings"] = (
            gdx.indexing_settings_to_dict(self.indexing_settings) if self.indexing_settings is not None else None
        )
        d["merging_settings"] = {
            parameter_name: [s.to_dict() for s in setting_list]
            for parameter_name, setting_list in self.merging_settings.items()
        }
        d["none_fallback"] = self.none_fallback.value
        d["none_export"] = self.none_export.value
        return d

    @staticmethod
    def from_dict(pack_dict, logger):
        """Restores the settings pack from a dictionary."""
        pack = SettingsPack()
        value = pack_dict.get("none_fallback")
        if value is not None:
            pack.none_fallback = gdx.NoneFallback(value)
        value = pack_dict.get("none_export")
        if value is not None:
            pack.none_export = gdx.NoneExport(value)
        set_settings_dict = pack_dict.get("settings")
        if set_settings_dict is not None:
            try:
                pack.settings = gdx.SetSettings.from_dict(set_settings_dict)
            except gdx.GdxExportException as error:
                logger.msg_error.emit(f"Failed to fully restore Exporter settings: {error}")
                return pack
        indexing_settings_dict = pack_dict.get("indexing_settings")
        if indexing_settings_dict is not None:
            try:
                pack.indexing_settings = gdx.indexing_settings_from_dict(indexing_settings_dict)
            except gdx.GdxExportException as error:
                logger.msg_error.emit(f"Failed to fully restore Exporter's indexing settings: {error}")
                return pack
        merging_settings_dict = pack_dict.get("merging_settings", dict())
        pack.merging_settings = {
            parameter_name: setting_list for parameter_name, setting_list in merging_settings_dict.items()
        }
        for name, setting_list in pack.merging_settings.items():
            # For 0.5 compatibility
            if not isinstance(setting_list, list):
                pack.merging_settings[name] = [setting_list]
        pack.merging_settings = {
            parameter_name: [gdx.MergingSetting.from_dict(setting_dict) for setting_dict in setting_list]
            for parameter_name, setting_list in pack.merging_settings.items()
        }
        return pack
