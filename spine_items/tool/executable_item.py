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
Contains Tool's executable item and support functionality.

:authors: A. Soininen (VTT)
:date:   30.3.2020
"""

import datetime
import fnmatch
import glob
import os
import os.path
import sys
import pathlib
import shutil
import time
import uuid
from contextlib import ExitStack
from spine_engine.config import TOOL_OUTPUT_DIR
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.spine_engine import ItemExecutionFinishState
from spine_engine.project_item.project_item_resource import (
    cmd_line_arg_from_dict,
    expand_cmd_line_args,
    labelled_resource_args,
)
from spine_engine.utils.helpers import resolve_julia_executable, resolve_gams_executable, write_filter_id_file
from .item_info import ItemInfo
from .utils import file_paths_from_resources, find_file, flatten_file_path_duplicates, is_pattern, make_dir_if_necessary
from .output_resources import scan_for_resources
from ..utils import generate_filter_subdirectory_name


class ExecutableItem(ExecutableItemBase):
    """Tool project item's executable parts."""

    _MAX_RETRIES = 3

    def __init__(self, name, work_dir, tool_specification, cmd_line_args, options, group_id, project_dir, logger):
        """
        Args:
            name (str): item's name
            work_dir (str): an absolute path to Spine Toolbox work directory
                or None if the Tool should not execute in work directory
            tool_specification (ToolSpecification): a tool specification
            cmd_line_args (list): a list of command line argument to pass to the tool instance
            options (dict): misc tool options. See ``Tool`` for details.
            group_id (str or None): execution group identifier
            project_dir (str): absolute path to project directory
            logger (LoggerInterface): a logger
        """
        super().__init__(name, project_dir, logger, group_id=group_id)
        self._work_dir = work_dir
        self._output_dir = str(pathlib.Path(self._data_dir, TOOL_OUTPUT_DIR))
        self._tool_specification = tool_specification
        self._cmd_line_args = cmd_line_args
        self._options = options
        self._tool_instance = None
        self._retry_count = 0

    @property
    def options(self):
        return self._options

    @staticmethod
    def item_type():
        """Returns the item's type identifier string."""
        return ItemInfo.item_type()

    def stop_execution(self):
        """Stops executing this Tool."""
        super().stop_execution()
        if self._tool_instance is not None and self._tool_instance.is_running():
            self._tool_instance.terminate_instance()
            self._tool_instance = None

    def _copy_input_files(self, paths, execution_dir):
        """
        Copies input files from given paths to work or source directory, depending on
        where the Tool specification requires them to be.

        Args:
            paths (dict): key is path to destination file, value is path to source file
            execution_dir (str): absolute path to the execution directory

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        n_copied_files = 0
        # Make sure that execution_dir (work dir) exists if there's something to copy.
        # Needed by Executable tools running a shell command
        if not make_dir_if_necessary(paths, execution_dir):
            self._logger.msg_error.emit(f"Creating directory <b>{execution_dir}</b> failed")
            return False
        for dst, src_path in paths.items():
            file_anchor = (
                f"<a style='color:#BB99FF;' title='{src_path}' href='file:///{src_path}'>"
                + f"{os.path.basename(src_path)}</a>"
            )
            if not os.path.exists(src_path):
                self._logger.msg_error.emit(f"\tFile <b>{file_anchor}</b> does not exist")
                return False
            # Join work directory path to dst (dst is the filename including possible subfolders, e.g. 'input/f.csv')
            dst_path = os.path.abspath(os.path.join(execution_dir, dst))
            # Create subdirectories if necessary
            dst_subdir, _ = os.path.split(dst)
            if not dst_subdir:
                # No subdirectories to create
                self._logger.msg.emit(f"\tCopying <b>{file_anchor}</b>")
            else:
                # Create subdirectory structure to work or source directory
                work_subdir_path = os.path.abspath(os.path.join(execution_dir, dst_subdir))
                if not os.path.exists(work_subdir_path):
                    try:
                        os.makedirs(work_subdir_path, exist_ok=True)
                    except OSError:
                        self._logger.msg_error.emit(f"[OSError] Creating directory <b>{work_subdir_path}</b> failed.")
                        return False
                self._logger.msg.emit(f"\tCopying <b>{file_anchor}</b> into <b>{dst_subdir}{os.path.sep}</b>")
            try:
                shutil.copyfile(src_path, dst_path)
                n_copied_files += 1
            except shutil.SameFileError:
                # Happens in source dir exec mode when DC is passing a file as reference from the main program dir to
                # source dir, which are equal
                self._logger.msg_warning.emit("\tNo need to copy. File already available.")
            except OSError as e:
                self._logger.msg_error.emit(f"Copying file <b>{file_anchor}</b> to <b>{dst_path}</b> failed")
                self._logger.msg_error.emit(f"{e}")
                if e.errno == 22:
                    msg = (
                        "The reason might be:\n"
                        "[1] The destination file already exists and it cannot be "
                        "overwritten because it is locked by Julia or some other application.\n"
                        "[2] You don't have the necessary permissions to overwrite the file.\n"
                        "To solve the problem, you can try the following:\n[1] Execute the Tool in work "
                        "directory.\n[2] If you are executing a Julia Tool with Julia 0.6.x, upgrade to "
                        "Julia 0.7 or newer.\n"
                        "[3] Close any other background application(s) that may have locked the file.\n"
                        "And try again.\n"
                    )
                    self._logger.msg_warning.emit(msg)
                return False
        self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> input file(s)")
        return True

    def _copy_optional_input_files(self, paths, execution_dir):
        """
        Copies optional input files from given paths to work or source directory, depending on
        where the Tool specification requires them to be.

        Args:
            paths (dict): key is the source path, value is the destination path
            execution_dir (str): Absolute path to work or source directory

        Returns:
            bool: False if creating the execution directory failed, True otherwise
        """
        n_copied_files = 0
        # Make sure that execution_dir (work dir) exists if there's something to copy.
        # Needed by Executable tools running a shell command
        if not make_dir_if_necessary(paths, execution_dir):
            self._logger.msg_error.emit(f"Creating directory <b>{execution_dir}</b> failed")
            return False
        for src_path, dst_path in paths.items():
            try:
                shutil.copyfile(src_path, dst_path)
                n_copied_files += 1
            except shutil.SameFileError:
                # Happens in source dir exec mode when DC is passing a file as reference from the main program dir to
                # source dir, which are equal
                self._logger.msg_warning.emit("\tNo need to copy. File already available.")
            except OSError as e:
                self._logger.msg_error.emit(f"Copying optional file <b>{src_path}</b> to <b>{dst_path}</b> failed")
                self._logger.msg_error.emit(f"{e}")
                if e.errno == 22:
                    msg = (
                        "The reason might be:\n"
                        "[1] The destination file already exists and it cannot be "
                        "overwritten because it is locked by Julia or some other application.\n"
                        "[2] You don't have the necessary permissions to overwrite the file.\n"
                        "To solve the problem, you can try the following:\n[1] Execute the Tool in work "
                        "directory.\n[2] If you are executing a Julia Tool with Julia 0.6.x, upgrade to "
                        "Julia 0.7 or newer.\n"
                        "[3] Close any other background application(s) that may have locked the file.\n"
                        "And try again.\n"
                    )
                    self._logger.msg_warning.emit(msg)
        self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> optional input file(s)")
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
        for pattern in self._tool_specification.outputfiles:
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

    def _copy_program_files(self, execution_dir):
        """Copies Tool specification source files to base directory.

        Args:
            execution_dir (str): path to execution directory

        Returns:
            bool: True if operation was successful, False otherwise
        """
        n_copied_files = 0
        for source_pattern in self._tool_specification.includes:
            dir_name, file_pattern = os.path.split(source_pattern)
            src_dir = os.path.join(self._tool_specification.path, dir_name)
            dst_dir = os.path.join(execution_dir, dir_name)
            # Create the destination directory
            try:
                os.makedirs(dst_dir, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"Creating directory <b>{dst_dir}</b> failed")
                return False
            # Copy file if necessary
            if file_pattern:
                for src_file in glob.glob(os.path.abspath(os.path.join(src_dir, file_pattern))):
                    dst_file = os.path.abspath(os.path.join(dst_dir, os.path.basename(src_file)))
                    try:
                        shutil.copyfile(src_file, dst_file)
                        n_copied_files += 1
                    except OSError:
                        self._logger.msg_error.emit(f"\tCopying file <b>{src_file}</b> to <b>{dst_file}</b> failed")
                        return False
        if n_copied_files == 0:
            self._logger.msg_warning.emit("Warning: No files copied")
        else:
            self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> file(s)")
        return True

    def _create_input_dirs(self, execution_dir):
        """Iterates items in required input files and check
        if there are any directories to create. Create found
        directories directly to work or source directory.

        Args:
            execution_dir (str): the execution directory

        Returns:
            bool: True if the operation was successful, False otherwiseBoolean variable depending on success
        """
        for required_path in self._tool_specification.inputfiles:
            path, filename = os.path.split(required_path)
            if filename:
                continue
            path_to_create = os.path.join(execution_dir, path)
            try:
                os.makedirs(path_to_create, exist_ok=True)
            except OSError:
                self._logger.msg_error.emit(f"[OSError] Creating directory {path_to_create} failed. Check permissions.")
                return False
            self._logger.msg.emit(f"\tDirectory <b>{os.path.sep}{path}</b> created")
        return True

    def _create_output_dirs(self, execution_dir):
        """Makes sure that work directory has the necessary output directories for Tool output files.
        Checks only "outputfiles" list. Alternatively you can add directories to "inputfiles" list
        in the tool definition file.

        Args:
            execution_dir (str): a path to the execution directory

        Returns:
            bool: True for success, False otherwise.

        Raises:
            OSError: If creating an output directory to work fails.
        """
        for out_file_path in self._tool_specification.outputfiles:
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

    def ready_to_execute(self, settings):
        """See base class.

        Returns False when
        1. Tool has no specification
        2. Python or Julia Kernel spec not selected (jupyter kernel mode)
        3. Julia executable not set and not found in PATH (subprocess mode)
        4. Trying to execute an Executable Tool Spec using a shell that is not supported
        by the user's OS.

        Returns True otherwise.
        """
        if self._tool_specification is None:
            self._logger.msg_warning.emit(f"Tool <b>{self.name}</b> not ready for execution. No specification.")
            return False
        if self._tool_specification.tooltype.lower() == "python":
            use_python_kernel = settings.value("appSettings/usePythonKernel", defaultValue="0")
            python_kernel = settings.value("appSettings/pythonKernel", defaultValue="")
            if use_python_kernel == "2" and python_kernel == "":
                self._logger.msg_error.emit("No Python kernel spec selected. Please select one in Settings->Tools.")
                return False
            # Note: no check for python path == "" because this should never happen
        elif self._tool_specification.tooltype.lower() == "julia":
            use_julia_kernel = settings.value("appSettings/useJuliaKernel", defaultValue="0")
            julia_kernel = settings.value("appSettings/juliaKernel", defaultValue="")
            julia_path = resolve_julia_executable(settings.value("appSettings/juliaPath", defaultValue=""))
            if use_julia_kernel == "2" and julia_kernel == "":
                self._logger.msg_error.emit("No Julia kernel spec selected. Please select one in Settings->Tools.")
                return False
            if use_julia_kernel == "0" and julia_path == "":
                self._logger.msg_error.emit(
                    "Julia not found in PATH. Please select the Julia you want to use in Settings->Tools."
                )
                return False
        elif self._tool_specification.tooltype.lower() == "gams":
            gams_path = resolve_gams_executable(settings.value("appSettings/gamsPath", defaultValue=""))
            if not gams_path:
                self._logger.msg_error.emit(
                    "Gams not found in PATH. Please select the Gams you want to use in Settings->Tools."
                )
                return False
        elif self._tool_specification.tooltype.lower() == "executable":
            if not self._tool_specification.main_prgm:
                shell = self._tool_specification.execution_settings["shell"]
                if sys.platform == "win32" and shell == "bash":
                    self._logger.msg_error.emit("Bash shell is not supported on Windows. Please select another shell.")
                    return False
                if sys.platform != "win32" and (shell in ("cmd.exe", "powershell.exe")):
                    self._logger.msg_error.emit(
                        f"Selected shell is not supported on your platform [{sys.platform}]. "
                        f"Please select another shell."
                    )
                    return False
        return True

    def execute(self, forward_resources, backward_resources):
        """See base class.

        Before launching the tool script in a separate instance,
        prepares the execution environment by creating all necessary directories
        and copying input files where needed.
        After execution archives the output files.
        """
        if not super().execute(forward_resources, backward_resources):
            return ItemExecutionFinishState.FAILURE
        execution_dir = _execution_directory(self._work_dir, self._tool_specification)
        if execution_dir is None:
            return ItemExecutionFinishState.FAILURE
        work_or_source = "work" if self._work_dir is not None else "source"
        # Make work/source directory anchor with path as tooltip
        anchor = (
            f"<a style='color:#99CCFF;' title='{execution_dir}'"
            f"href='file:///{execution_dir}'>{work_or_source} directory</a>"
        )
        self._logger.msg.emit(
            f"*** Executing Tool specification <b>{self._tool_specification.name}</b> in {anchor} ***"
        )
        if work_or_source == "work":
            self._logger.msg.emit(f"*** Copying program files ***")
            if not self._copy_program_files(execution_dir):
                self._logger.msg_error.emit("Copying program files failed")
                return ItemExecutionFinishState.FAILURE
        # Find required input files for ToolInstance (if any)
        if self._tool_specification.inputfiles:
            self._logger.msg.emit("*** Checking Tool specification requirements ***")
            n_dirs, n_files = _count_files_and_dirs(self._tool_specification.inputfiles)
            if n_files > 0:
                self._logger.msg.emit("*** Searching for required input files ***")
                file_paths = flatten_file_path_duplicates(
                    self._find_input_files(forward_resources), self._logger, log_duplicates=True
                )
                not_found = [k for k, v in file_paths.items() if v is None]
                if not_found:
                    self._logger.msg_error.emit(f"Required file(s) <b>{', '.join(not_found)}</b> not found")
                    return ItemExecutionFinishState.FAILURE
                self._logger.msg.emit(f"*** Copying input files to {work_or_source} directory ***")
                # Copy input files to ToolInstance work or source directory
                if not self._copy_input_files(file_paths, execution_dir):
                    self._logger.msg_error.emit("Copying input files failed. Tool execution aborted.")
                    return ItemExecutionFinishState.FAILURE
            if n_dirs > 0:
                self._logger.msg.emit(f"*** Creating input subdirectories to {work_or_source} directory ***")
                if not self._create_input_dirs(execution_dir):
                    # Creating directories failed -> abort
                    self._logger.msg_error.emit("Creating input subdirectories failed. Tool execution aborted.")
                    return ItemExecutionFinishState.FAILURE
        if self._tool_specification.inputfiles_opt:
            self._logger.msg.emit("*** Searching for optional input files ***")
            optional_file_paths = self._find_optional_input_files(forward_resources)
            for k, v in optional_file_paths.items():
                self._logger.msg.emit(f"\tFound <b>{len(v)}</b> files matching pattern <b>{k}</b>")
            optional_file_copy_paths = self._optional_output_destination_paths(optional_file_paths, execution_dir)
            if not self._copy_optional_input_files(optional_file_copy_paths, execution_dir):
                return False
        if not self._create_output_dirs(execution_dir):
            self._logger.msg_error.emit("Creating output subdirectories failed. Tool execution aborted.")
            return ItemExecutionFinishState.FAILURE
        if not os.path.isdir(execution_dir):
            self._logger.msg_warning.emit(
                f"Work directory was not created because Tool Specification "
                f"<b>{self._tool_specification.name}</b> does not contain any "
                f"program files nor (optional) input files. Please <b>execute the "
                f"Tool in source execution mode</b> or include files to the "
                f"specification."
            )
            return ItemExecutionFinishState.FAILURE
        self._tool_instance = self._tool_specification.create_tool_instance(execution_dir, self._logger, self)
        resources = forward_resources + backward_resources
        with ExitStack() as stack:
            labelled_args = labelled_resource_args(resources, stack, db_checkin=True, db_checkout=True)
            expanded_args = expand_cmd_line_args(self._cmd_line_args, labelled_args, self._logger)
            try:
                self._tool_instance.prepare(expanded_args)
            except RuntimeError as error:
                if str(error):
                    self._logger.msg_error.emit(f"Failed to prepare Tool instance: {error}")
                return ItemExecutionFinishState.FAILURE
            return_code = self._tool_instance.execute()
            if return_code != 0 and self._tool_instance is not None and self._tool_instance.killed:
                # NOTE: return_code will be 0 if the instance was killed by e.g. `exit(0)` in julia
                # In this case we want to consider the tool successfull and not retry it
                if self._retry_count < self._MAX_RETRIES:
                    # Try again
                    self._retry_count += 1
                    self._logger.msg_warning.emit("The Tool process was found dead. Retrying...")
                    return self.execute(forward_resources, backward_resources)
                self._logger.msg_warning.emit("Maximum amount of retries reached.")
        self._handle_output_files(return_code, self._filter_id, forward_resources, execution_dir)
        self._tool_instance = None
        # TODO: Check what return code is 'stopped' and return ItemExecutionFinishState.STOPPED in this case
        return ItemExecutionFinishState.SUCCESS if return_code == 0 else ItemExecutionFinishState.FAILURE

    def _find_input_files(self, resources):
        """
        Iterates required input  files in tool specification and looks for them in the given resources.

        Args:
            resources (list): resources available

        Returns:
            Dictionary mapping required files to path where they are found, or to None if not found
        """
        file_paths = dict()
        for required_path in self._tool_specification.inputfiles:
            _, filename = os.path.split(required_path)
            if not filename:
                # It's a directory
                continue
            file_paths[required_path] = find_file(filename, resources)
        return file_paths

    def _find_optional_input_files(self, resources):
        """
        Tries to find optional input files from previous project items in the DAG.

        Args:
            resources (list): resources available

        Returns:
            dict: Dictionary of optional input file paths or an empty dictionary if no files found. Key is the
                optional input item and value is a list of paths that matches the item.
        """
        file_paths = dict()
        paths_in_resources = file_paths_from_resources(resources)
        for file_path in self._tool_specification.inputfiles_opt:
            _, pattern = os.path.split(file_path)
            if not pattern:
                # It's a directory -> skip
                continue
            found_files = _find_files_in_pattern(pattern, paths_in_resources)
            if not found_files:
                self._logger.msg_warning.emit(f"\tNo files matching pattern <b>{pattern}</b> found")
            else:
                file_paths[file_path] = found_files
        return file_paths

    def _handle_output_files(self, return_code, filter_id, forward_resources, execution_dir):
        """Copies Tool specification output files from work directory to result directory.

        Args:
            return_code (int): Tool specification process return value
            filter_id (str): filter identifier
            forward_resources (Iterable of ProjectItemResource): forward resources
            execution_dir (str): path to the execution directory
        """
        if filter_id:
            filter_output_dir = os.path.join(
                self._output_dir, generate_filter_subdirectory_name(forward_resources, self.hash_filter_id())
            )
            try:
                os.makedirs(filter_output_dir, exist_ok=True)
                self._output_dir = filter_output_dir
            except OSError:
                self._logger.msg_error.emit(f"[OSError] Creating directory <b>{filter_output_dir}</b> failed.")
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
            f"<a style='color:#BB99FF;' title='{result_path}' href='file:///{result_path}'>results directory</a>"
        )
        if filter_id:
            write_filter_id_file(filter_id, os.path.dirname(result_path))
        self._logger.msg.emit(f"*** Archiving output files to {result_anchor} ***")
        if self._tool_specification.outputfiles:
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

    def _optional_output_destination_paths(self, paths, execution_dir):
        """
        Returns a dictionary telling where optional output files should be copied to before execution.

        Args:
            paths (dict): key is the optional file name pattern, value is a list of paths to source files
            execution_dir (str): a path to the execution directory

        Returns:
            dict: a map from source path to destination path
        """
        destination_paths = dict()
        for dst, src_paths in paths.items():
            for src_path in src_paths:
                if not os.path.exists(src_path):
                    self._logger.msg_error.emit(f"\tFile <b>{src_path}</b> does not exist")
                    continue
                # Get file name that matched the search pattern
                _, dst_fname = os.path.split(src_path)
                # Check if the search pattern included subdirectories (e.g. 'input/*.csv')
                # This means that /input/ directory should be created to work (or source) directory
                # before copying the files
                dst_subdir, _search_pattern = os.path.split(dst)
                if not dst_subdir:
                    # No subdirectories to create
                    self._logger.msg.emit(f"\tCopying optional file <b>{dst_fname}</b>")
                    dst_path = os.path.abspath(os.path.join(execution_dir, dst_fname))
                else:
                    # Create subdirectory structure to work or source directory
                    work_subdir_path = os.path.abspath(os.path.join(execution_dir, dst_subdir))
                    if not os.path.exists(work_subdir_path):
                        try:
                            os.makedirs(work_subdir_path, exist_ok=True)
                        except OSError:
                            self._logger.msg_error.emit(
                                f"[OSError] Creating directory <b>{work_subdir_path}</b> failed."
                            )
                            continue
                    self._logger.msg.emit(
                        f"\tCopying optional file <b>{dst_fname}</b> into subdirectory <b>{os.path.sep}{dst_subdir}</b>"
                    )
                    dst_path = os.path.abspath(os.path.join(work_subdir_path, dst_fname))
                destination_paths[src_path] = dst_path
        return destination_paths

    def _output_resources_forward(self):
        """See base class"""
        return scan_for_resources(self, self._tool_specification, self._output_dir)

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
        specification_name = item_dict["specification"]
        specification = ExecutableItemBase._get_specification(
            name, ItemInfo.item_type(), specification_name, specifications, logger
        )
        cmd_line_args = [cmd_line_arg_from_dict(arg) for arg in item_dict["cmd_line_args"]]
        options = item_dict.get("options", {})
        group_id = item_dict.get("group_id")
        return cls(name, work_dir, specification, cmd_line_args, options, group_id, project_dir, logger)


def _count_files_and_dirs(paths):
    """
    Counts the number of files and directories in given paths.

    Args:
        paths (list): list of paths

    Returns:
        Tuple containing the number of required files and directories.
    """
    n_dir = 0
    n_file = 0
    for path in paths:
        _, filename = os.path.split(path)
        if not filename:
            n_dir += 1
        else:
            n_file += 1
    return n_dir, n_file


def _create_output_dir_timestamp():
    """Creates a new timestamp string that is used as Tool output
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


def _execution_directory(work_dir, tool_specification):
    """
    Returns the path to the execution directory, depending on ``execute_in_work``.

    If ``execute_in_work`` is ``True``, a new unique path will be returned.
    If a main program file does not exist, Tool spec definition file path is
    returned. Otherwise, the main program file path from tool specification
    is returned.

    Returns:
        str: a full path to next basedir
    """
    if work_dir is not None:
        basedir = os.path.join(work_dir, _unique_dir_name(tool_specification))
        return basedir
    if not tool_specification.path:
        return tool_specification.default_execution_dir
    return tool_specification.path


def _find_files_in_pattern(pattern, available_file_paths):
    """
    Returns a list of files that match the given pattern.

    Args:
        pattern (str): file pattern
        available_file_paths (list): list of available file paths from upstream items
    Returns:
        list: List of (full) paths
    """
    extended_pattern = os.path.join("*", pattern)  # Match all absolute paths.
    return fnmatch.filter(available_file_paths, extended_pattern)


def _unique_dir_name(tool_specification):
    """Builds a unique name for Tool's work directory."""
    return tool_specification.short_name + "__" + uuid.uuid4().hex + "__toolbox"
