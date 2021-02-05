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
Contains Notebook Executor's executable item and support functionality.

:authors: A. Soininen (VTT), R. Brady (UCD)
:date:   05.02.2021
"""

import datetime
import os
import pathlib
import time
import uuid

from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.utils.helpers import shorten
from spine_engine.utils.serialization import deserialize_path
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from ..utils import labelled_resource_args


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, work_dir, output_dir, notebook_specification, cmd_line_args, logger):
        """
        Args:
            name (str): item's name
            work_dir (str): an absolute path to Spine Toolbox work directory
                or None if the Notebook should not execute in work directory
            output_dir (str): path to the directory where output files should be archived
            notebook_specification (NotebookExecutorSpecification): a notebook specification
            logger (LoggerInterface): a logger
        """
        super().__init__(name, logger)
        self._name = name
        self._work_dir = work_dir
        self._output_dir = output_dir
        self._notebook_specification = notebook_specification
        self._cmd_line_args = cmd_line_args
        self._nb_parameters = None
        self._logger = logger
        self._valid_nb_output = None
        self._notebook_instance = None
        self._nb_io_path_mapping = {}

    @ExecutableItemBase.filter_id.setter
    def filter_id(self, filter_id):
        self._filter_id = filter_id
        self._logger.set_filter_id(filter_id)
        filter_output_dir = os.path.join(self._output_dir, filter_id)
        try:
            os.makedirs(filter_output_dir, exist_ok=True)
            self._output_dir = filter_output_dir
        except OSError:
            self._logger.msg_error.emit(f"[OSError] Creating directory <b>{filter_output_dir}</b> failed.")

    @staticmethod
    def item_type():
        return ItemInfo.item_type()

    def _map_program_files(self, execution_dir):
        """Maps .ipynb file to its source path and maps its execution directory to be passed to this items instance"""
        for source_pattern in self._notebook_specification.includes:
            dir_name, file_pattern = os.path.split(source_pattern)
            if not dir_name:
                src_dir = os.path.join(self._notebook_specification.path, file_pattern)
                self._nb_io_path_mapping[source_pattern] = src_dir
                self._nb_io_path_mapping["execution_output_dir"] = execution_dir  # FIXME overwrite for each source_pattern
            else:
                src_dir = os.path.join(self._notebook_specification.path, dir_name, file_pattern)
                dst_dir = os.path.join(execution_dir, dir_name)
                self._nb_io_path_mapping[source_pattern] = src_dir
                self._nb_io_path_mapping["execution_output_dir"] = dst_dir
        return True

    def _create_output_dirs(self, execution_dir):
        """Makes sure that work directory has the necessary output directories for Notebook output files.
        Checks only "output_files" list. Alternatively you can add directories to "input_files" list
        in the notebook definition file.

        Args:
            execution_dir (str): a path to the execution directory

        Returns:
            bool: True for success, False otherwise.

        Raises:
            OSError: If creating an output directory to work fails.
        """
        for out_file_path in self._notebook_specification.output_files:
            dirname = os.path.split(out_file_path)[0]
            if not dirname:
                continue
            dst_dir = os.path.join(execution_dir, dirname)
            try:
                os.makedirs(dst_dir, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"Creating work output directory '{dst_dir}' failed")
                return False
        return True

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._notebook_specification, self._output_dir, False)

    def stop_execution(self):
        return NotImplementedError

    def expand_cmd_line_args(self, forward_resources, backward_resources):
        labelled_args = labelled_resource_args(forward_resources + backward_resources)
        for k, label in enumerate(self._cmd_line_args):
            arg = labelled_args.get(label)
            if arg is not None:
                self._cmd_line_args[k] = arg

    def execute(self, forward_resources, backward_resources):
        """Setup and execute the Notebook Executor instance
        Returns:
            bool: True for success, False otherwise.
        """
        # execute notebook with papermill
        if not super().execute(forward_resources, backward_resources):
            return False
        if self._notebook_specification is None:
            self._logger.msg_warning.emit(f"Notebook executor <b>{self.name}</b> has no Notebook specification to "
                                          f"execute")
            print(f"Notebook executor <b>{self.name}</b> has no Notebook specification to execute")
            return False
        execution_dir = _execution_directory(self._work_dir, self._notebook_specification)
        if execution_dir is None:
            return False
        anchor = f"<a style='color:#99CCFF;' title='{execution_dir}' href='file:///{execution_dir}'>work directory</a>"
        if self._work_dir is not None:
            work_or_source = "work"
            self._logger.msg.emit(
                f"*** Copying Notebook executor specification <b>{self._notebook_specification.name}"
                f"</b> source files to {anchor} ***"
            )
            if not self._map_program_files(execution_dir):
                self._logger.msg_error.emit("Copying program files to work directory failed.")
                print("Copying program files to work directory failed.")
                return False
        else:
            work_or_source = "source"
        # Make source directory anchor with path as tooltip
        anchor = (
            f"<a style='color:#99CCFF;' title='{execution_dir}'"
            f"href='file:///{execution_dir}'>{work_or_source} directory</a>"
        )
        self._logger.msg.emit(
            f"*** Executing Notebook specification <b>{self._notebook_specification.name}</b> in {anchor} ***"
        )
        print(f"*** Executing Notebook specification <b>{self._notebook_specification.name}</b> in {anchor} ***")
        if not self._create_output_dirs(execution_dir):
            self._logger.msg_error.emit("Creating output subdirectories failed. Notebook execution aborted.")
            print("Creating output subdirectories failed. Notebook execution aborted.")
            return False
        self._notebook_instance = self._notebook_specification.create_instance(execution_dir, self._logger, self)
        self.expand_cmd_line_args(forward_resources, backward_resources)
        self._nb_io_path_mapping["source_output_dir"] = self._create_source_output_dir()
        try:
            self._notebook_instance.prepare(self._nb_io_path_mapping, self._cmd_line_args)
        except RuntimeError as error:
            self._logger.msg_error.emit(f"Failed to prepare notebook instance: {error}")
            print(f"Failed to prepare notebook instance: {error}")
            return False
        self._logger.msg.emit(
            f"*** Starting instance of Notebook specification <b>{self._notebook_specification.name}</b> ***")
        print(f"*** Starting instance of Notebook specification <b>{self._notebook_specification.name}</b> ***")
        return_code = self._notebook_instance.execute()
        self._notebook_instance = None
        return return_code == 0

    def _create_source_output_dir(self):
        """Generates output directory in source
        """
        output_dir_timestamp = _create_output_dir_timestamp()  # Get timestamp when Notebook finished
        # Create an output folder with timestamp
        result_path = os.path.abspath(os.path.join(self._output_dir, output_dir_timestamp))
        try:
            os.makedirs(result_path, exist_ok=True)
        except OSError:
            self._logger.msg_error.emit("\tError creating timestamped output directory.")
            return None
        return result_path

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        execute_in_work = item_dict["execute_in_work"]
        if execute_in_work:
            work_dir = app_settings.value("appSettings/workDir")
            if not work_dir:
                logger.msg_error.emit(f"Error: Work directory not set for project item {name}")
                work_dir = None
        else:
            work_dir = None
        data_dir = pathlib.Path(project_dir, ".spinetoolbox", "items", shorten(name))
        output_dir = pathlib.Path(data_dir, TOOL_OUTPUT_DIR)
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        cmd_line_args = item_dict["cmd_line_args"]
        cmd_line_args = [deserialize_path(arg, project_dir) for arg in cmd_line_args]
        return cls(name, work_dir, output_dir, specification, cmd_line_args, logger)


def _create_output_dir_timestamp():
    """ Creates a new timestamp string that is used as Notebook output
    directory.

    Returns:
        Timestamp string or empty string if failed.
    """
    try:
        # Create timestamp
        stamp = datetime.datetime.fromtimestamp(time.time())
    except OverflowError:
        return ""
    extension = stamp.strftime("%Y-%m-%dT%H.%M.%S")
    return extension


def _execution_directory(work_dir, notebook_specification):
    """
    Returns the path to the execution directory, depending on ``execute_in_work``.

    If ``execute_in_work`` is ``True``, a new unique path will be returned.
    Otherwise, the main program file path from notebook specification is returned.

    Returns:
        str: a full path to next basedir
    """
    # print(notebook_specification.path)
    if work_dir is not None:
        basedir = os.path.join(work_dir, _unique_dir_name(notebook_specification))
        try:
            os.makedirs(basedir, exist_ok=True)
        except OSError:
            print(f"Creating execution directory '{basedir}' failed")
            return None
        return basedir
    return notebook_specification.path


def _unique_dir_name(notebook_specification):
    """Builds a unique name for Notebook's work directory."""
    return notebook_specification.short_name + "__" + uuid.uuid4().hex + "__toolbox"
