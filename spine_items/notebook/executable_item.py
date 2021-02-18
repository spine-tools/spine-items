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
Contains Notebook's executable item and support functionality.

:authors: A. Soininen (VTT), R. Brady (UCD)
:date:   05.02.2021
"""

import datetime
import glob
import os
import pathlib
import shutil
import time
import uuid

from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.utils.helpers import shorten
from spine_engine.utils.serialization import deserialize_path
from .item_info import ItemInfo
from .output_resources import scan_for_resources
from .utils import is_pattern
from ..utils import labelled_resource_args, is_label


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, work_dir, output_dir, notebook_specification, cmd_line_args, logger):
        """
        Args:
            name (str): item's name
            work_dir (str): an absolute path to Spine Toolbox work directory
                or None if the Notebook should not execute in work directory
            output_dir (str): path to the directory where output files should be archived
            notebook_specification (NotebookSpecification): a notebook specification
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

    def _copy_output_files(self, target_dir, execution_dir):
        """Copies Tool specification output files from work directory to given target directory.

        Args:
            target_dir (str): Destination directory for Tool specification output files
            execution_dir (str): path to the execution directory

        Returns:
            tuple: Contains two lists. The first list contains paths to successfully
            copied files. The second list contains paths (or patterns) of Tool specification
            output files that were not found.

        Raises:
            OSError: If creating a directory fails.
        """
        failed_files = list()
        saved_files = list()
        for pattern in self._notebook_specification.output_files:
            # Create subdirectories if necessary
            dst_subdir, fname_pattern = os.path.split(pattern)
            target = os.path.abspath(os.path.join(target_dir, dst_subdir))
            if not os.path.exists(target):
                try:
                    os.makedirs(target, exist_ok=True)
                except OSError:
                    self._logger.msg_error.emit(f"[OSError] Creating directory <b>{target}</b> failed.")
                    continue
                self._logger.msg.emit(f"\tCreated result subdirectory <b>{os.path.sep}{dst_subdir}</b>")
            # Check for wildcards in pattern
            if is_pattern(pattern):
                for fname_path in glob.glob(os.path.abspath(os.path.join(execution_dir, pattern))):
                    # fname_path is a full path
                    fname = os.path.split(fname_path)[1]  # File name (no path)
                    dst = os.path.abspath(os.path.join(target, fname))
                    full_fname = os.path.join(dst_subdir, fname)
                    try:
                        shutil.copyfile(fname_path, dst)
                        saved_files.append((full_fname, dst))
                    except OSError:
                        self._logger.msg_error.emit(f"[OSError] Copying pattern {fname_path} to {dst} failed")
                        failed_files.append(full_fname)
            else:
                output_file = os.path.abspath(os.path.join(execution_dir, pattern))
                if not os.path.isfile(output_file):
                    failed_files.append(pattern)
                    continue
                dst = os.path.abspath(os.path.join(target, fname_pattern))
                try:
                    shutil.copyfile(output_file, dst)
                    saved_files.append((pattern, dst))
                except OSError:
                    self._logger.msg_error.emit(f"[OSError] Copying output file {output_file} to {dst} failed")
                    failed_files.append(pattern)
        return saved_files, failed_files

    def _output_resources_forward(self):
        """See base class."""
        return scan_for_resources(self, self._notebook_specification, self._output_dir, False)

    def stop_execution(self):
        return NotImplementedError

    def execute(self, forward_resources, backward_resources):
        """Setup and execute the Notebook instance
        Returns:
            bool: True for success, False otherwise.
        """
        # execute notebook with papermill
        if not super().execute(forward_resources, backward_resources):
            return False
        if self._notebook_specification is None:
            self._logger.msg_warning.emit(f"Notebook <b>{self.name}</b> has no Notebook specification to "
                                          f"execute")
            return False
        execution_dir = _execution_directory(self._work_dir, self._notebook_specification)
        if execution_dir is None:
            return False
        anchor = f"<a style='color:#99CCFF;' title='{execution_dir}' href='file:///{execution_dir}'>work directory</a>"
        if self._work_dir is not None:
            work_or_source = "work"
            self._logger.msg.emit(
                f"*** Copying Notebook specification <b>{self._notebook_specification.name}"
                f"</b> source files to {anchor} ***"
            )
            if not self._map_program_files(execution_dir):
                self._logger.msg_error.emit("Copying program files to work directory failed.")
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
        if not self._create_output_dirs(execution_dir):
            self._logger.msg_error.emit("Creating output subdirectories failed. Notebook execution aborted.")
            return False
        self._notebook_instance = self._notebook_specification.create_instance(execution_dir, self._logger, self)
        with labelled_resource_args(forward_resources + backward_resources, False) as labelled_args:
            for k, arg in enumerate(self._cmd_line_args):
                if is_label(arg):
                    if arg not in labelled_args:
                        self._logger.msg_warning.emit(
                            f"The argument '{k}: {arg}' does not match any available resources."
                        )
                        continue
                    arg = labelled_args[arg]
                self._cmd_line_args[k] = arg
            try:
                self._notebook_instance.prepare(self._nb_io_path_mapping, self._cmd_line_args)
            except RuntimeError as error:
                self._logger.msg_error.emit(f"Failed to prepare notebook instance: {error}")
                return False
            self._logger.msg.emit(
                f"*** Starting instance of Notebook specification <b>{self._notebook_specification.name}</b> ***")
            return_code = self._notebook_instance.execute()
        self._handle_output_files(return_code, execution_dir)
        self._notebook_instance = None
        return return_code == 0

    def _handle_output_files(self, return_code, execution_dir):
        """Copies Tool specification output files from work directory to result directory.

        Args:
            return_code (int): Tool specification process return value
            execution_dir (str): path to the execution directory
        """
        output_dir_timestamp = _create_output_dir_timestamp()  # Get timestamp when tool finished
        # Create an output folder with timestamp and copy output directly there
        if return_code != 0:
            result_path = os.path.abspath(os.path.join(self._output_dir, "failed", output_dir_timestamp))
        else:
            result_path = os.path.abspath(os.path.join(self._output_dir, output_dir_timestamp))
        try:
            os.makedirs(result_path, exist_ok=True)
        except OSError:
            self._logger.msg_error.emit(
                "\tError creating timestamped output directory. "
                "Tool specification output files not copied. Please check directory permissions."
            )
            return
        # Make link to output folder
        result_anchor = (
            f"<a style='color:#BB99FF;' title='{result_path}'" f"href='file:///{result_path}'>results directory</a>"
        )
        self._logger.msg.emit(f"*** Archiving output files to {result_anchor} ***")
        if self._notebook_specification.output_files:
            saved_files, failed_files = self._copy_output_files(result_path, execution_dir)
            if not saved_files:
                # If no files were saved
                self._logger.msg_error.emit("\tNo files saved")
            else:
                # If there are saved files
                # Split list into filenames and their paths
                filenames, _ = zip(*saved_files)
                self._logger.msg.emit("\tThe following output files were saved to results directory")
                for filename in filenames:
                    self._logger.msg.emit(f"\t\t<b>{filename}</b>")
            if failed_files:
                # If saving some or all files failed
                self._logger.msg_warning.emit("\tThe following output files were not found")
                for failed_file in failed_files:
                    failed_fname = os.path.split(failed_file)[1]
                    self._logger.msg_warning.emit(f"\t\t<b>{failed_fname}</b>")
        else:
            tip_anchor = (
                "<a style='color:#99CCFF;' title='When you add output files to the Tool specification,\n "
                "they will be archived into results directory. Also, output files are passed to\n "
                "subsequent project items.' href='#'>Tip</a>"
            )
            self._logger.msg_warning.emit(f"\tNo output files defined for this Tool specification. {tip_anchor}")

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
    if work_dir is not None:
        basedir = os.path.join(work_dir, _unique_dir_name(notebook_specification))
        try:
            os.makedirs(basedir, exist_ok=True)
        except OSError:
            return None
        return basedir
    return notebook_specification.path


def _unique_dir_name(notebook_specification):
    """Builds a unique name for Notebook's work directory."""
    return notebook_specification.short_name + "__" + uuid.uuid4().hex + "__toolbox"
