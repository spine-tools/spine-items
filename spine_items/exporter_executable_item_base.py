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
Contains base classes for executable items.

:authors: A. Soininen (VTT)
:date:    10.2.2021
"""
import json
import os.path
from pathlib import Path

from spine_engine.project_item.project_item_resource import file_resource_in_pack
from spinedb_api import clear_filter_configs, load_filters
from spinedb_api.filters.tools import filter_configs, name_from_dict
from spinedb_api.spine_io import gdx_utils
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from .utils import exported_files_as_resources, EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX


class ExporterExecutableItemBase(ExecutableItemBase):
    """Base class for exporter executable items."""

    def __init__(self, name, databases, output_time_stamps, cancel_on_error, gams_path, project_dir, logger):
        """
        Args:
            name (str): item's name
            databases (list of Database): database export settings
            output_time_stamps (bool): if True append output directories with time stamps
            cancel_on_error (bool): if True execution fails on all errors else some errors can be ignored
            gams_path (str): GAMS path from Toolbox settings
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._databases = databases
        self._output_time_stamps = output_time_stamps
        self._cancel_on_error = cancel_on_error
        self._gams_path = gams_path
        self._forks = dict()
        self._result_files = None
        self._process = None

    @staticmethod
    def item_type():
        """See base class."""
        raise NotImplementedError()

    def stop_execution(self):
        """Stops executing this item."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None

    def exclude_execution(self, forward_resources, backward_resources):
        """See base class."""
        manifest_file_name = (
            EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX + (f"-{self.hash_filter_id()}" if self._filter_id else "")
        ) + ".json"
        manifest_file_path = Path(self._data_dir, manifest_file_name)
        if not manifest_file_path.exists():
            return
        with open(Path(self._data_dir, manifest_file_name)) as manifest_file:
            manifest = json.load(manifest_file)
        self._result_files = {label: set(files) for label, files in manifest.items()}

    def _database_output_file_names(self, database_urls):
        """
        Connects full database urls to output file names.

        Args:
            database_urls (Iterable of str): full database URLs including filters

        Returns:
            dict: a mapping from full database URL to output file name
        """
        databases = {}
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
        return databases

    def _databases_and_forks(self, database_urls):
        """
        Connects output file names to scenario and tool filters.

        Args:
            database_urls (Iterable of str): database URLs.

        Returns:
            tuple: a mapping from full database URL to output file name and
                a mapping from URL to list of scenario/tool/etc. names
        """
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
            forks[url] = list()
            for config in load_filters(filter_configs(full_url)):
                filter_name = name_from_dict(config)
                if filter_name is not None:
                    forks[url].append(filter_name)
        return databases, forks

    def _output_resources_forward(self):
        """See base class."""
        if self._result_files is None:
            return []
        resources = list()
        for label, output_files in self._result_files.items():
            resources += [file_resource_in_pack(self.name, label, f) for f in output_files]
        return resources

    def _resolve_gams_system_directory(self):
        """Returns GAMS system path from Toolbox settings or None if GAMS default is to be used.

        Returns:
            str: GAMS system path
        """
        path = self._gams_path
        if not path:
            path = gdx_utils.find_gams_directory()
        if path is not None and os.path.isfile(path):
            path = os.path.dirname(path)
        return path

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        raise NotImplementedError()
