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
Contains Exporter's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   2.4.2020
"""
import os.path
import pathlib
from spinedb_api import SpineDBAPIError
from spinetoolbox.spine_io import gdx_utils
from spinetoolbox.spine_io.exporters import gdx
from spinetoolbox.project_item.executable_item_base import ExecutableItemBase
from spinetoolbox.helpers_qt_free import shorten, deserialize_path
from spinetoolbox.project_item.project_item_resource import ProjectItemResource
from .database import Database
from .db_utils import scenario_filtered_database_map
from .item_info import ItemInfo
from .settings_pack import SettingsPack


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, settings_pack, databases, cancel_on_error, data_dir, gams_path, logger):
        """
        Args:
            name (str): item's name
            settings_pack (SettingsPack): export settings
            databases (list of Database): database export settings
            cancel_on_error (bool): True if execution should fail on all errors, False if certain errors can be ignored
            data_dir (str): absolute path to exporter's data directory
            gams_path (str): GAMS path from Toolbox settings
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._settings_pack = settings_pack
        self._databases = databases
        self._cancel_on_error = cancel_on_error
        self._data_dir = data_dir
        self._gams_path = gams_path

    @staticmethod
    def item_type():
        """Returns Exporter's type identifier string."""
        return ItemInfo.item_type()

    def _execute_forward(self, resources):
        """See base class."""
        if self._settings_pack.settings is None:
            self._logger.msg_warning.emit(f"<b>{self.name}</b>: No export settings configured. Skipping.")
            return True
        database_urls = [r.url for r in resources if r.type_ == "database"]
        gams_system_directory = self._resolve_gams_system_directory()
        if gams_system_directory is None:
            self._logger.msg_error.emit(f"<b>{self.name}</b>: Cannot proceed. No GAMS installation found.")
            return False
        for url in database_urls:
            database = None
            for db in self._databases:
                if url == db.url:
                    database = db
                    break
            if database is None:
                self._logger.msg_error.emit(f"<b>{self.name}</b>: No settings for database {url}.")
                return False
            if not database.output_file_name:
                self._logger.msg_error.emit(f"<b>{self.name}</b>: No file name given to export database {url}.")
                return False
            out_path = os.path.join(self._data_dir, database.output_file_name)
            try:
                database_map = scenario_filtered_database_map(url, database.scenario)
            except SpineDBAPIError as error:
                self._logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
                return False
            export_logger = self._logger if not self._cancel_on_error else None
            try:
                gdx.to_gdx_file(
                    database_map,
                    out_path,
                    self._settings_pack.settings,
                    self._settings_pack.indexing_settings,
                    self._settings_pack.merging_settings,
                    self._settings_pack.none_fallback,
                    self._settings_pack.none_export,
                    gams_system_directory,
                    export_logger,
                )
            except gdx.GdxExportException as error:
                self._logger.msg_error.emit(f"Failed to export <b>{url}</b> to .gdx: {error}")
                return False
            finally:
                database_map.connection.close()
            self._logger.msg_success.emit(f"File <b>{out_path}</b> written")
        return True

    def _output_resources_forward(self):
        """See base class."""
        resources = list()
        for db in self._databases:
            path = pathlib.Path(self._data_dir, db.output_file_name)
            if path.exists():
                resource = ProjectItemResource(self, "transient_file", path.as_uri(), {"label": db.output_file_name})
                resources.append(resource)
        return resources

    def _resolve_gams_system_directory(self):
        """Returns GAMS system path from Toolbox settings or None if GAMS default is to be used."""
        path = self._gams_path
        if not path:
            path = gdx_utils.find_gams_directory()
        if path is not None and os.path.isfile(path):
            path = os.path.dirname(path)
        return path

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        try:
            settings_pack = SettingsPack.from_dict(item_dict["settings_pack"], logger)
        except gdx.GdxExportException as error:
            logger.msg_error.emit(f"Failed to fully restore Exporter settings: {error}")
            settings_pack = SettingsPack()
        databases = dict()
        for db_dict in item_dict["databases"]:
            url = deserialize_path(db_dict["database_url"], project_dir)
            databases[url] = Database.from_dict(db_dict)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        return cls(name, settings_pack, databases, cancel_on_error, str(data_dir), gams_path, logger)
