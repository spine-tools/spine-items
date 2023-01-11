######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
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
:date:    11.12.2020
"""
from json import dump
from pathlib import Path

from spine_engine.utils.returning_process import ReturningProcess
from spine_engine.utils.serialization import deserialize_path
from spine_engine.spine_engine import ItemExecutionFinishState
from spinedb_api import clear_filter_configs
from spine_items.utils import Database, EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX, generate_filter_subdirectory_name
from .do_work import do_work
from .output_channel import OutputChannel
from ..exporter_executable_item_base import ExporterExecutableItemBase
from .item_info import ItemInfo
from .specification import OutputFormat


class ExecutableItem(ExporterExecutableItemBase):
    def __init__(
        self, name, specification, output_channels, output_time_stamps, cancel_on_error, gams_path, project_dir, logger
    ):
        """
        Args:
            name (str): item's name
            specification (ExporterSpecification): export settings
            output_channels (list of OutputChannel): output labels
            output_time_stamps (bool): if True append output directories with time stamps
            cancel_on_error (bool): if True execution fails on all errors else some errors can be ignored
            gams_path (str): GAMS path from Toolbox settings
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, output_time_stamps, cancel_on_error, gams_path, project_dir, logger)
        self._specification = specification
        self._output_channels = output_channels

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    def _database_out_labels(self, resources):
        """
        Connects full database urls to output labels.

        Args:
            resources (Iterable of ProjectItemResource): forward database resources

        Returns:
            dict: a mapping from full database URL to output label
        """
        databases = {}
        for resource in resources:
            channel = next((channel for channel in self._output_channels if channel.in_label == resource.label), None)
            if channel is None:
                channel = self._find_legacy_output_channel(resource)
                if channel is None:
                    self._logger.msg_warning.emit(
                        f"<b>{self.name}</b>: No settings for database {resource.label}. Skipping."
                    )
                    continue
            if not channel.out_label:
                self._logger.msg_warning.emit(
                    f"<b>{self.name}</b>: No output label given to database {resource.label}. Skipping."
                )
                continue
            databases[resource.url] = channel.out_label
        return databases

    def _find_legacy_output_channel(self, resource):
        """
        Find legacy output channel that corresponds to given resource

        Args:
            resource (ProjectItemResource): database resource

        Returns:
            OutputChannel: output channel or None if not found
        """
        in_label = clear_filter_configs(resource.url)
        channel = next((c for c in self._output_channels if c.in_label == in_label), None)
        if channel is not None:
            channel.in_label = resource.label
        return channel

    def execute(self, forward_resources, backward_resources, lock):
        """See base class."""
        status = super().execute(forward_resources, backward_resources, lock)
        if status != ItemExecutionFinishState.SUCCESS:
            return status
        if self._specification is None:
            self._logger.msg_warning.emit(f"<b>{self.name}</b>: No export settings configured. Skipping.")
            return ItemExecutionFinishState.SKIPPED
        databases = self._database_out_labels(r for r in forward_resources if r.type_ == "database")
        if not databases:
            return ItemExecutionFinishState.SKIPPED
        gams_system_directory = ""
        if self._specification.output_format == OutputFormat.GDX:
            gams_system_directory = self._resolve_gams_system_directory()
            if gams_system_directory is None:
                self._logger.msg_error.emit(f"<b>{self.name}</b>: Cannot proceed. No GAMS installation found.")
                return ItemExecutionFinishState.FAILURE
        out_dir = Path(self._data_dir, "output")
        self._process = ReturningProcess(
            target=do_work,
            args=(
                self._specification.to_dict(),
                self._output_time_stamps,
                self._cancel_on_error,
                gams_system_directory,
                str(out_dir),
                databases,
                self._filter_id,
                generate_filter_subdirectory_name(forward_resources, self.hash_filter_id()),
                self._logger,
            ),
        )
        result = self._process.run_until_complete()
        # result contains only the success flag if execution was forcibly stopped.
        if len(result) > 1:
            self._result_files = result[1]
            file_name = (
                EXPORTER_EXECUTION_MANIFEST_FILE_PREFIX + (f"-{self.hash_filter_id()}" if self.filter_id else "")
            ) + ".json"
            with open(Path(self._data_dir, file_name), "w") as manifest:
                dump(
                    {
                        label: list(str(Path(file).relative_to(Path(self._data_dir))) for file in files)
                        for label, files in self._result_files.items()
                    },
                    manifest,
                )
        self._process = None
        return ItemExecutionFinishState.SUCCESS if result[0] else ItemExecutionFinishState.FAILURE

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        specification_name = item_dict["specification"]
        specification = ExporterExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        output_channels = [OutputChannel.from_dict(d) for d in item_dict.get("output_labels", [])]
        for db_dict in item_dict.get("databases", []):
            # legacy
            db = Database.from_dict(db_dict)
            db.url = clear_filter_configs(deserialize_path(db_dict["database_url"], project_dir))
            output_channels.append(OutputChannel(db.url, db.output_file_name))
        output_time_stamps = item_dict.get("output_time_stamps", False)
        cancel_on_error = item_dict.get("cancel_on_error", True)
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        return ExecutableItem(
            name, specification, output_channels, output_time_stamps, cancel_on_error, gams_path, project_dir, logger
        )
