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
Contains GdxExporter's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   2.4.2020
"""
import os.path
import pathlib
from spine_engine.spine_io import gdx_utils
from spine_engine.spine_io.exporters import gdx
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.helpers import shorten
from spine_engine.utils.serialization import deserialize_path
from spine_engine.utils.returning_process import ReturningProcess
from spinedb_api import clear_filter_configs, load_filters
from spinedb_api.filters.tools import filter_configs, name_from_dict
from .database import Database
from .do_work import do_work
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from .settings_pack import SettingsPack


class ExecutableItem(ExecutableItemBase):
    def __init__(
        self, name, settings_pack, databases, output_time_stamps, cancel_on_error, data_dir, gams_path, logger
    ):
        """
        Args:
            name (str): item's name
            settings_pack (SettingsPack): export settings
            databases (list of Database): database export settings
            output_time_stamps (bool): if True append output directories with time stamps
            cancel_on_error (bool): if True execution fails on all errors else some errors can be ignored
            data_dir (str): absolute path to exporter's data directory
            gams_path (str): GAMS path from Toolbox settings
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._settings_pack = settings_pack
        self._databases = databases
        self._output_time_stamps = output_time_stamps
        self._cancel_on_error = cancel_on_error
        self._data_dir = data_dir
        self._gams_path = gams_path
        self._forks = dict()
        self._process = None

    @staticmethod
    def item_type():
        """Returns GdxExporter's type identifier string."""
        return ItemInfo.item_type()

    def stop_execution(self):
        """Stops executing this Gimlet."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return False
        if self._settings_pack.settings is None:
            self._logger.msg_warning.emit(f"<b>{self.name}</b>: No export settings configured. Skipping.")
            return True
        database_urls = [r.url for r in forward_resources if r.type_ == "database"]
        gams_system_directory = self._resolve_gams_system_directory()
        if gams_system_directory is None:
            self._logger.msg_error.emit(f"<b>{self.name}</b>: Cannot proceed. No GAMS installation found.")
            return False
        databases, forks = self._databases_and_forks(database_urls)
        self._forks.update(forks)
        self._process = ReturningProcess(
            target=do_work,
            args=(
                self._settings_pack,
                self._output_time_stamps,
                self._cancel_on_error,
                self._data_dir,
                gams_system_directory,
                databases,
                self._forks,
                self._logger,
            ),
        )
        return_value = self._process.run_until_complete()
        self._process = None
        return return_value[0]

    def skip_execution(self, forward_resources, backward_resources):
        """See base class."""
        database_urls = [r.url for r in forward_resources if r.type_ == "database"]
        _, forks = self._databases_and_forks(database_urls)
        self._forks.update(forks)

    def _databases_and_forks(self, database_urls):
        databases = {}
        forks = {}
        for full_url in database_urls:
            url = clear_filter_configs(full_url)
            database = next((db for db in self._databases if db.url == url), None)
            if database is None:
                self._logger.msg_warning.emit(f"<b>{self.name}</b>: No settings for database {url}. Skipping.")
                continue
            if not database.output_file_name:
                self._logger.msg_warning.emit(
                    f"<b>{self.name}</b>: No file name given to export database {url}. Skipping."
                )
                continue
            databases[full_url] = database.output_file_name
            forks[url] = url_forks = set()
            for config in load_filters(filter_configs(full_url)):
                url_forks.add(name_from_dict(config))
            if not url_forks:
                url_forks.add(None)
        return databases, forks

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._databases, self._data_dir, self._forks)

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
            logger.msg_error.emit(f"Failed to fully restore GdxExporter settings: {error}")
            settings_pack = SettingsPack()
        databases = list()
        for db_dict in item_dict["databases"]:
            db = Database.from_dict(db_dict)
            db.url = deserialize_path(db_dict["database_url"], project_dir)
            databases.append(db)
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        return cls(
            name, settings_pack, databases, output_time_stamps, cancel_on_error, str(data_dir), gams_path, logger
        )
