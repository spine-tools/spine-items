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
:date:    2.4.2020
"""
from json import dump
from pathlib import Path
from spinedb_api.spine_io.exporters import gdx
from spine_engine.utils.serialization import deserialize_path
from spine_engine.utils.returning_process import ReturningProcess
from spine_engine.spine_engine import ItemExecutionFinishState
from spine_items.utils import Database, EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX
from ..exporter_executable_item_base import ExporterExecutableItemBase
from .do_work import do_work
from .item_info import ItemInfo
from .settings_pack import SettingsPack


class ExecutableItem(ExporterExecutableItemBase):
    def __init__(
        self, name, settings_pack, databases, output_time_stamps, cancel_on_error, gams_path, project_dir, logger
    ):
        """
        Args:
            name (str): item's name
            settings_pack (SettingsPack): export settings
            databases (list of Database): database export settings
            output_time_stamps (bool): if True append output directories with time stamps
            cancel_on_error (bool): if True execution fails on all errors else some errors can be ignored
            gams_path (str): GAMS path from Toolbox settings
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, databases, output_time_stamps, cancel_on_error, gams_path, project_dir, logger)
        self._settings_pack = settings_pack

    @staticmethod
    def item_type():
        """Returns GdxExporter's type identifier string."""
        return ItemInfo.item_type()

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return ItemExecutionFinishState.FAILURE
        if self._settings_pack.settings is None:
            self._logger.msg_warning.emit(f"<b>{self.name}</b>: No export settings configured. Skipping.")
            return ItemExecutionFinishState.SKIPPED
        database_urls = [r.url for r in forward_resources if r.type_ == "database"]
        gams_system_directory = self._resolve_gams_system_directory()
        if gams_system_directory is None:
            self._logger.msg_error.emit(f"<b>{self.name}</b>: Cannot proceed. No GAMS installation found.")
            return ItemExecutionFinishState.FAILURE
        databases, self._forks = self._databases_and_forks(database_urls)
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
        result = self._process.run_until_complete()
        # result contains only the success flag if execution was forcibly stopped.
        if len(result) > 1:
            self._result_files = result[1]
            file_name = (
                (EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX + self.filter_id)
                if self.filter_id
                else EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX
            ) + ".json"
            with open(Path(self._data_dir, file_name), "w") as manifest:
                dump(self._result_files, manifest)
        self._process = None
        return ItemExecutionFinishState.SUCCESS if result[0] else ItemExecutionFinishState.FAILURE

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
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        return cls(name, settings_pack, databases, output_time_stamps, cancel_on_error, gams_path, project_dir, logger)
