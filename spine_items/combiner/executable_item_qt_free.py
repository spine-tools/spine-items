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
Contains Combiner's executable item as well as support utilities.

:authors: A. Soininen (VTT)
:date:   2.4.2020
"""
import os
import pathlib
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.helpers_qt_free import shorten, create_log_file_timestamp, LoggingProcess, get_logger
from spinedb_api import (
    clear_filter_configs,
    export_data,
    import_data,
    SpineDBAPIError,
    SpineDBVersionError,
    DiffDatabaseMapping,
)

from .item_info import ItemInfo


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, logs_dir, cancel_on_error, logger):
        """
        Args:
            name (str): item's name
            logs_dir (str): path to the directory where logs should be stored
            cancel_on_error (bool): if True, revert changes on error and move on
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._resources_from_downstream = list()
        self._logs_dir = logs_dir
        self._cancel_on_error = cancel_on_error
        self._process = None

    @staticmethod
    def item_type():
        """Returns Combiner's type identifier string."""
        return ItemInfo.item_type()

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        logs_dir = os.path.join(data_dir, "logs")
        cancel_on_error = item_dict["cancel_on_error"]
        return cls(name, logs_dir, cancel_on_error, logger)

    def stop_execution(self):
        """Stops executing this Gimlet."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None

    def _execute_backward(self, resources):
        """See base class."""
        self._resources_from_downstream = resources.copy()
        return True

    @staticmethod
    def _urls_from_resources(resources):
        return [r.url for r in resources if r.type_ == "database"]

    def _execute_forward(self, resources):
        """See base class."""
        from_urls = self._urls_from_resources(resources)
        to_urls = self._urls_from_resources(self._resources_from_downstream)
        if not from_urls:
            self._logger.msg_warning.emit("No input database(s) available. Moving on...")
            return True
        if not to_urls:
            self._logger.msg_warning.emit("No output database available. Moving on...")
            return True
        self._process = LoggingProcess(
            self._logger, target=_do_work, args=(self._cancel_on_error, self._logs_dir, from_urls, to_urls),
        )
        self._process.run_until_complete()
        self._logger.msg_success.emit(f"Executing Combiner {self.name} finished")
        self._process = None
        return True


def _get_db_map(url):
    try:
        db_map = DiffDatabaseMapping(url)
    except (SpineDBAPIError, SpineDBVersionError) as err:
        logger = get_logger()
        logger.msg_error.emit(f"Skipping url <b>{url}</b>: {err}")
        logger.msg_error.emit(f"Skipping url <b>{clear_filter_configs(url)}</b>: {err}")
        return None
    return db_map


def _do_work(cancel_on_error, logs_dir, from_urls, to_urls):
    logger = get_logger()
    from_db_maps = [db_map for db_map in (_get_db_map(url) for url in from_urls) if db_map]
    to_db_maps = [db_map for db_map in (_get_db_map(url) for url in to_urls) if db_map]
    from_db_map_data = {from_db_map: export_data(from_db_map) for from_db_map in from_db_maps}
    all_errors = []
    for to_db_map in to_db_maps:
        to_db_map_import_count = 0
        to_db_map_error_count = 0
        for from_db_map, data in from_db_map_data.items():
            import_count, import_errors = import_data(to_db_map, **data)
            all_errors += import_errors
            if import_errors and cancel_on_error:
                if to_db_map.has_pending_changes():
                    to_db_map.rollback_session()
            elif import_count:
                to_db_map.commit_session(
                    f"Import {import_count} items from {from_db_map.db_url} by Spine Toolbox Combiner"
                )
            to_db_map_import_count += import_count
            to_db_map_error_count += len(import_errors)
        logger.msg_success.emit(
            "Merged {0} data with {1} errors into {2}".format(
                to_db_map_import_count, to_db_map_error_count, to_db_map.db_url
            )
        )
    for db_map in from_db_maps + to_db_maps:
        db_map.connection.close()
    if all_errors:
        # Log errors in a time stamped file into the logs directory
        timestamp = create_log_file_timestamp()
        logfilepath = os.path.abspath(os.path.join(logs_dir, timestamp + "_error.log"))
        with open(logfilepath, "w") as f:
            for err in all_errors:
                f.write("{0}\n".format(err))
        # Make error log file anchor with path as tooltip
        logfile_anchor = f"<a style='color:#BB99FF;' title='{logfilepath}' href='file:///{logfilepath}'>error log</a>"
        logger.msg_error.emit("Import errors. Logfile: {0}".format(logfile_anchor))
