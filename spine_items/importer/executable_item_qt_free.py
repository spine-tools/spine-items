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
import spinedb_api
from spine_engine.spine_io.gdx_utils import find_gams_directory
from spine_engine.spine_io.importers.csv_reader import CSVConnector
from spine_engine.spine_io.importers.excel_reader import ExcelConnector
from spine_engine.spine_io.importers.gdx_connector import GdxConnector
from spine_engine.spine_io.importers.json_reader import JSONConnector
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.utils.helpers import shorten
from spine_engine.utils.serialization import deserialize_checked_states
from spine_engine.utils.returning_process import ReturningProcess
from .item_info import ItemInfo
from .do_work import do_work
from ..utils import labelled_resource_filepaths


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
        self._process = None

    @staticmethod
    def item_type():
        """Returns ImporterExecutable's type identifier string."""
        return ItemInfo.item_type()

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

    def _execute_forward(self, resources):
        """See base class."""
        if not self._mapping:
            return True
        labelled_filepaths = labelled_resource_filepaths(resources)
        source_filepaths = list()
        for label in self._selected_files:
            filepath = labelled_filepaths.get(label)
            if filepath is not None:
                source_filepaths.append(filepath)
        urls_downstream = [r.url for r in self._resources_from_downstream if r.type_ == "database"]
        source_type = self._mapping["source_type"]
        if source_type == "GdxConnector":
            source_settings = {"gams_directory": self._gams_system_directory()}
        else:
            source_settings = None
        connector = {
            "CSVConnector": CSVConnector,
            "ExcelConnector": ExcelConnector,
            "GdxConnector": GdxConnector,
            "JSONConnector": JSONConnector,
        }[source_type](source_settings)
        self._process = ReturningProcess(
            target=do_work,
            args=(
                self._mapping,
                self._cancel_on_error,
                self._logs_dir,
                source_filepaths,
                connector,
                urls_downstream,
                self._logger,
            ),
        )
        self._process.run_until_complete()
        success = self._process.success if self._process is not None else False
        self._logger.msg_success.emit(f"Executing Importer {self.name} {'finished' if success else 'failed'}")
        self._process = None
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
