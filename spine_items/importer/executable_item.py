######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains Importer's executable item as well as support utilities."""
import os
from contextlib import ExitStack
from spinedb_api.spine_io.gdx_utils import find_gams_directory
from spinedb_api.spine_io.importers.csv_reader import CSVConnector
from spinedb_api.spine_io.importers.excel_reader import ExcelConnector
from spinedb_api.spine_io.importers.gdx_connector import GdxConnector
from spinedb_api.spine_io.importers.json_reader import JSONConnector
from spinedb_api.spine_io.importers.datapackage_reader import DataPackageConnector
from spinedb_api.spine_io.importers.sqlalchemy_connector import SqlAlchemyConnector
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.project_item.project_item_resource import get_labelled_source_resources
from spine_engine.utils.returning_process import ReturningProcess
from spine_engine.spine_engine import ItemExecutionFinishState
from ..db_writer_executable_item_base import DBWriterExecutableItemBase
from .item_info import ItemInfo
from .do_work import do_work


class ExecutableItem(DBWriterExecutableItemBase):
    def __init__(self, name, mapping, selected_files, gams_path, cancel_on_error, on_conflict, project_dir, logger):
        """
        Args:
            name (str): Importer's name
            mapping (dict): import mapping
            selected_files (list): selected_files
            gams_path (str): path to system's GAMS executable or empty string for the default path
            cancel_on_error (bool): if True, revert changes on error and quit
            on_conflict (str): conflict resolution strategy for spinedb_api.import_data
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger)
        self._mapping = mapping
        self._selected_files = selected_files
        self._gams_path = gams_path
        self._cancel_on_error = cancel_on_error
        self._on_conflict = on_conflict
        self._process = None

    @staticmethod
    def item_type():
        """Returns ImporterExecutable's type identifier string."""
        return ItemInfo.item_type()

    def stop_execution(self):
        """Stops executing this Importer."""
        super().stop_execution()
        if self._process is not None:
            self._process.terminate()
            self._process = None

    def execute(self, forward_resources, backward_resources, lock):
        """See base class."""
        if not super().execute(forward_resources, backward_resources, lock):
            return ItemExecutionFinishState.FAILURE
        if not self._mapping:
            self._logger.msg_warning.emit(f"<b>{self.name}</b>: No mappings configured. Skipping.")
            return ItemExecutionFinishState.SKIPPED
        labelled_resources = get_labelled_source_resources(forward_resources)
        selected_resources = []
        for label in self._selected_files:
            selected_resources += labelled_resources.get(label, [])
        to_resources = [r for r in backward_resources if r.type_ == "database"]
        if not selected_resources or not to_resources:
            return ItemExecutionFinishState.SUCCESS
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
            "DataPackageConnector": DataPackageConnector,
            "SqlAlchemyConnector": SqlAlchemyConnector,
        }[source_type](source_settings)
        with ExitStack() as stack:
            to_server_urls = [stack.enter_context(resource.open()) for resource in to_resources]
            self._process = ReturningProcess(
                target=do_work,
                args=(
                    self._mapping,
                    self._cancel_on_error,
                    self._on_conflict,
                    self._logs_dir,
                    selected_resources,
                    connector,
                    to_server_urls,
                    lock,
                    self._logger,
                ),
            )
            return_value = self._process.run_until_complete()
            self._process = None
            return ItemExecutionFinishState.SUCCESS if return_value[0] else ItemExecutionFinishState.FAILURE

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
        file_selection = {label: selected for label, selected in item_dict.get("file_selection", list())}
        selected_files = [filepath for filepath, selected in file_selection.items() if selected]
        gams_path = app_settings.value("appSettings/gamsPath", defaultValue=None)
        cancel_on_error = item_dict["cancel_on_error"]
        on_conflict = item_dict["on_conflict"]
        return cls(name, mapping, selected_files, gams_path, cancel_on_error, on_conflict, project_dir, logger)
