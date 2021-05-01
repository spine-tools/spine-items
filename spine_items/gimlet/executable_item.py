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
Contains Gimlet ExecutableItem class.

:author: P. Savolainen (VTT)
:date:   15.4.2020
"""

import os
import sys
import shutil
import uuid
from spine_engine.project_item.executable_item_base import ExecutableItemBase
from spine_engine.config import GIMLET_WORK_DIR_NAME
from spine_engine.utils.helpers import shorten
from spine_engine.utils.command_line_arguments import split_cmdline_args
from spine_engine.execution_managers.process_execution_manager import ProcessExecutionManager
from spine_engine.spine_engine import ItemExecutionFinishState
from .item_info import ItemInfo
from .utils import SHELLS
from ..utils import (
    CmdLineArg,
    cmd_line_arg_from_dict,
    expand_cmd_line_args,
    labelled_resource_filepaths,
    labelled_resource_args,
)


class ExecutableItem(ExecutableItemBase):
    def __init__(self, name, shell, cmd, work_dir, selected_files, project_dir, logger):
        """

        Args:
            name (str): Project item name
            shell (str): Shell name or empty string if no shell should be used
            cmd (list): Command to execute
            work_dir (str, optional): Full path to work directory
            selected_files (list): List of file paths that were selected
            project_dir (str): Absolute path to project directory
            logger (LoggerInterface): Logger instance
        """
        super().__init__(name, project_dir, logger)
        self.shell_name = shell
        self.cmd_list = cmd
        if work_dir is None:
            work_dir = os.path.join(self._data_dir, GIMLET_WORK_DIR_NAME)
        else:
            unique_dir_name = shorten(name) + "__" + uuid.uuid4().hex + "__toolbox"
            work_dir = os.path.join(work_dir, unique_dir_name)
        self._work_dir = work_dir
        self._resources = list()
        self._selected_files = selected_files
        self._exec_mngr = None

    @staticmethod
    def item_type():
        """Returns Gimlet's type identifier string."""
        return ItemInfo.item_type()

    @classmethod
    def from_dict(cls, item_dict, name, project_dir, app_settings, specifications, logger):
        """See base class."""
        if not item_dict["use_shell"]:
            shell = ""
        else:
            shell_index = item_dict["shell_index"]
            try:
                shell = SHELLS[shell_index]
            except IndexError:
                logger.msg_error.emit(f"Error: Unsupported shell_index in project item {name}")
                shell = ""
        cmd_list = [CmdLineArg(arg) for arg in split_cmdline_args(item_dict["cmd"])]
        cmd_list += [cmd_line_arg_from_dict(arg) for arg in item_dict["cmd_line_args"]]
        if item_dict["work_dir_mode"]:
            work_dir = None
        else:
            work_dir = app_settings.value("appSettings/workDir")
            if not work_dir:
                logger.msg_error.emit(f"Error: Work directory not set for project item {name}")
                work_dir = None
        selections = [label for label, selected in item_dict.get("file_selection", list()) if selected]
        return cls(name, shell, cmd_list, work_dir, selections, project_dir, logger)

    def stop_execution(self):
        """Stops executing this Gimlet."""
        super().stop_execution()
        if self._exec_mngr is not None:
            self._exec_mngr.stop_execution()
            self._exec_mngr = None

    def execute(self, forward_resources, backward_resources):
        """See base class."""
        if not super().execute(forward_resources, backward_resources):
            return ItemExecutionFinishState.FAILURE
        if not self._work_dir:
            self._logger.msg_warning.emit("Work directory not set.")
            return ItemExecutionFinishState.FAILURE
        if not self.cmd_list:
            self._logger.msg_warning.emit("No command to execute.")
            return ItemExecutionFinishState.FAILURE
        if sys.platform == "win32" and self.shell_name == "bash":
            self._logger.msg_warning.emit("Sorry, Bash shell is not supported on Windows.")
            return ItemExecutionFinishState.FAILURE
        if sys.platform != "win32" and (self.shell_name == "cmd.exe" or self.shell_name == "powershell.exe"):
            self._logger.msg_warning.emit(f"Sorry, selected shell is not supported on your platform [{sys.platform}]")
            return ItemExecutionFinishState.FAILURE
        with labelled_resource_args(forward_resources + backward_resources) as labelled_args:
            cmd_list = expand_cmd_line_args(self.cmd_list, labelled_args, self._logger)
        if not self.shell_name or self.shell_name == "bash":
            prgm = cmd_list.pop(0)
            self._exec_mngr = ProcessExecutionManager(self._logger, prgm, *cmd_list, workdir=self._work_dir)
        else:
            if self.shell_name == "cmd.exe":
                shell_prgm = "cmd.exe"
                cmd_list = ["/C"] + cmd_list
            elif self.shell_name == "powershell.exe":
                shell_prgm = "powershell.exe"
            else:
                self._logger.msg_error.emit(f"Unsupported shell: '{self.shell_name}'")
                return ItemExecutionFinishState.FAILURE
            self._exec_mngr = ProcessExecutionManager(self._logger, shell_prgm, *cmd_list, workdir=self._work_dir)
        # Copy selected files to work_dir
        selected_files = self._selected_files.copy()
        labelled_filepaths = labelled_resource_filepaths(forward_resources + backward_resources)
        for k, label in enumerate(selected_files):
            filepath = labelled_filepaths.get(label)
            if filepath is not None:
                selected_files[k] = filepath
        if not self._copy_files(selected_files, self._work_dir):
            return ItemExecutionFinishState.FAILURE
        # Make work directory anchor with path as tooltip
        work_anchor = (
            "<a style='color:#99CCFF;' title='"
            + self._work_dir
            + "' href='file:///"
            + self._work_dir
            + "'>work directory</a>"
        )
        self._logger.msg.emit(f"*** Executing in <b>{work_anchor}</b> ***")
        ret = self._exec_mngr.run_until_complete()
        if ret != 0:
            self._logger.msg_error.emit(f"Return code:{ret}")
        finish_state = ItemExecutionFinishState.SUCCESS if ret == 0 else ItemExecutionFinishState.FAILURE
        # Copy predecessor's resources so they can be passed to Gimlet's successors
        self._resources = forward_resources.copy()
        self._exec_mngr = None
        return finish_state

    def _output_resources_forward(self):
        """Returns output resources for forward execution.

        Returns:
            (list) List of ProjectItemResources.
        """
        return self._resources

    def _copy_files(self, files, work_dir):
        """Copies selected resources (files) to work directory.

        Args:
            files (list): List of full paths to files that will be copied to work dir
            work_dir (str): Full path to selected work dir

        Returns:
            bool: True when files were copied successfully, False when something went wrong
        """
        try:
            # Creates work_dir if it does not exist. Note: work_dir will be empty if len(files)==0.
            os.makedirs(work_dir, exist_ok=True)
        except OSError:
            self._logger.msg_error.emit(f"Creating directory <b>{work_dir}</b> failed")
            return False
        n_copied_files = 0
        for f in files:
            name = os.path.basename(f)
            dst_file = os.path.abspath(os.path.join(work_dir, name))
            try:
                # Copy file
                shutil.copyfile(f, dst_file)
                n_copied_files += 1
            except OSError:
                self._logger.msg_error.emit(f"\tCopying file <b>{f}</b> to <b>{dst_file}</b> failed")
                return False
        if n_copied_files == 0:
            self._logger.msg_warning.emit("\tNote: No files were copied")
        else:
            self._logger.msg.emit(f"\tCopied <b>{n_copied_files}</b> file(s)")
        return True
