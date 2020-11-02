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
Contains Importer's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   1.4.2020
"""

import os
import pathlib
import multiprocessing as mp
import spinedb_api
from spinetoolbox.spine_io.type_conversion import value_to_convert_spec
from spinetoolbox.spine_io.gdx_utils import find_gams_directory
from spinetoolbox.spine_io.importers.csv_reader import CSVConnector
from spinetoolbox.spine_io.importers.excel_reader import ExcelConnector
from spinetoolbox.spine_io.importers.gdx_connector import GdxConnector
from spinetoolbox.spine_io.importers.json_reader import JSONConnector
from spinetoolbox.project_item.executable_item_base import ExecutableItemBase
from spinetoolbox.helpers_qt_free import (
    shorten,
    create_log_file_timestamp,
    deserialize_checked_states,
    QueueLogger,
    QueueLoggerSignalHandler,
)
from .item_info import ItemInfo


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, mapping, selected_files, logs_dir, gams_path, cancel_on_error, logger):
        """
        Args:
            name (str): Importer's name
            mapping (dict): import mapping
            selected_files (list): selected_files
            logs_dir (str): path to the directory where logs should be stored
            gams_path (str): path to system's GAMS executable or empty string for the default path
            cancel_on_error (bool): if True, revert changes on error and quit
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._mapping = mapping
        self._selected_files = selected_files
        self._logs_dir = logs_dir
        self._gams_path = gams_path
        self._cancel_on_error = cancel_on_error
        self._resources_from_downstream = list()

    @staticmethod
    def item_type():
        """Returns ImporterExecutable's type identifier string."""
        return ItemInfo.item_type()

    def _execute_backward(self, resources):
        """See base class."""
        self._resources_from_downstream = resources.copy()
        return True

    def _execute_forward(self, resources):
        """See base class."""
        if not self._mapping:
            return True
        absolute_paths = _files_from_resources(resources)
        checked_files = list()
        for label in self._selected_files:
            absolute_path = absolute_paths.get(label)
            if absolute_path is not None:
                checked_files.append(absolute_path)
        all_source_settings = {"GdxConnector": {"gams_directory": self._gams_system_directory()}}
        urls_downstream = [r.url for r in self._resources_from_downstream if r.type_ == "database"]
        queue = mp.Queue()
        p = mp.Process(
            target=_do_work,
            args=(
                self._mapping,
                self._cancel_on_error,
                self._logs_dir,
                checked_files,
                all_source_settings,
                urls_downstream,
                queue,
            ),
        )
        handler = QueueLoggerSignalHandler(queue, self._logger)
        p.start()
        while not handler.is_the_job_done():
            pass
        p.join()
        success = handler.process_exitcode == 0
        self._logger.msg_success.emit(f"Executing Importer {self.name} {'finished' if success else 'failed'}")
        return success

    def _gams_system_directory(self):
        """Returns GAMS system path or None if GAMS default is to be used."""
        path = self._gams_path
        if not path:
            path = find_gams_directory()
        if path is not None and os.path.isfile(path):
            path = os.path.dirname(path)
        return path

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        mapping = specification.mapping if specification else {}
        file_selection = item_dict.get("file_selection")
        file_selection = deserialize_checked_states(file_selection, project_dir)
        selected_files = [filepath for filepath, selected in file_selection.items() if selected]
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        logs_dir = os.path.join(data_dir, "logs")
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        cancel_on_error = item_dict["cancel_on_error"]
        return cls(name, mapping, selected_files, logs_dir, gams_path, cancel_on_error, logger)


def _files_from_resources(resources):
    """Returns a list of files available in given resources."""
    files = dict()
    for resource in resources:
        if resource.type_ == "file":
            files[resource.path] = resource.path
        elif resource.type_ == "transient_file":
            files[resource.metadata["label"]] = resource.path
    return files


def _do_work(mapping, cancel_on_error, logs_dir, checked_files, all_source_settings, urls_downstream, queue):
    logger = QueueLogger(queue)
    all_data = []
    all_errors = []
    source_type = mapping["source_type"]
    source_settings = all_source_settings.get(source_type)
    connector = {
        "CSVConnector": CSVConnector,
        "ExcelConnector": ExcelConnector,
        "GdxConnector": GdxConnector,
        "JSONConnector": JSONConnector,
    }[source_type](source_settings)
    table_mappings = {
        name: m for name, m in mapping.get("table_mappings", {}).items() if name in mapping["selected_tables"]
    }
    table_options = {
        name: options
        for name, options in mapping.get("table_options", {}).items()
        if name in mapping["selected_tables"]
    }
    table_types = {
        tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
        for tn, cols in mapping.get("table_types", {}).items()
    }
    table_row_types = {
        tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
        for tn, cols in mapping.get("table_row_types", {}).items()
    }
    for source in checked_files:
        try:
            connector.connect_to_source(source)
        except IOError as error:
            logger.msg_error.emit(f"Failed to connect to source: {error}")
            logger.job_done.emit(-1)
            return
        try:
            data, errors = connector.get_mapped_data(
                table_mappings, table_options, table_types, table_row_types, max_rows=-1
            )
        except spinedb_api.InvalidMapping as error:
            logger.msg_error.emit(f"Failed to import '{source}': {error}")
            if cancel_on_error:
                logger.msg_error.emit("Cancel import on error has been set. Bailing out.")
                logger.job_done.emit(-1)
                return
            logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
            continue
        if not errors:
            logger.msg.emit(f"Successfully read {sum(len(d) for d in data.values())} data from {source}")
        else:
            logger.msg_warning.emit(
                f"Read {sum(len(d) for d in data.values())} data from {source} with {len(errors)} errors."
            )
        all_data.append(data)
        all_errors.extend(errors)
    if all_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_read_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_errors:
                f.write(f"{err}\n")
        # Make error log file anchor with path as tooltip
        logfile_anchor = (
            "<a style='color:#BB99FF;' title='" + logfilepath + "' href='file:///" + logfilepath + "'>Error log</a>"
        )
        logger.msg_error.emit(logfile_anchor)
        if cancel_on_error:
            logger.msg_error.emit("Cancel import on error has been set. Bailing out.")
            logger.job_done.emit(-1)
            return
        logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
    if all_data:
        for url in urls_downstream:
            success = _import_data_to_url(cancel_on_error, logs_dir, all_data, url, logger)
            if not success and cancel_on_error:
                logger.job_done.emit(-1)
                return
    logger.job_done.emit(0)


def _import_data_to_url(cancel_on_error, logs_dir, all_data, url, logger):
    try:
        db_map = spinedb_api.DiffDatabaseMapping(url, upgrade=False, username="Mapper")
    except (spinedb_api.SpineDBAPIError, spinedb_api.SpineDBVersionError) as err:
        logger.msg_error.emit(f"Unable to create database mapping, all import operations will be omitted: {err}")
        return False
    all_import_errors = []
    for data in all_data:
        import_num, import_errors = spinedb_api.import_data(db_map, **data)
        all_import_errors += import_errors
        if import_errors:
            logger.msg_error.emit("Errors while importing a table.")
            if cancel_on_error:
                logger.msg_error.emit("Cancel import on error is set. Bailing out.")
                if db_map.has_pending_changes():
                    logger.msg_error.emit("Rolling back changes.")
                    db_map.rollback_session()
                break
            logger.msg_warning.emit("Ignoring errors. Set Cancel import on error to bail out instead.")
        if import_num:
            db_map.commit_session("Import data by Spine Toolbox Importer")
            logger.msg_success.emit(f"Inserted {import_num} data with {len(import_errors)} errors into {url}")
        elif import_num == 0:
            logger.msg_warning.emit("No new data imported")
    db_map.connection.close()
    if all_import_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_import_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_import_errors:
                f.write(str(err) + "\n")
        # Make error log file anchor with path as tooltip
        logfile_anchor = (
            "<a style='color:#BB99FF;' title='" + logfilepath + "' href='file:///" + logfilepath + "'>Error log</a>"
        )
        logger.msg_error.emit(logfile_anchor)
        return False
    return True
