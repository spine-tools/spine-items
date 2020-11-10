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
Contains ToolInstance class.

:authors: P. Savolainen (VTT), E. Rinne (VTT)
:date:   1.2.2018
"""

import os
import sys
import shutil
from spine_engine.config import GAMS_EXECUTABLE, JULIA_EXECUTABLE
from spine_engine.utils.helpers import python_interpreter
from spine_engine.execution_managers import StandardExecutionManager, KernelExecutionManager


class ToolInstance:
    """Tool instance base class."""

    def __init__(self, tool_specification, basedir, settings, logger):
        """

        Args:
            tool_specification (ToolSpecification): the tool specification for this instance
            basedir (str): the path to the directory where this instance should run
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
        """
        self.tool_specification = tool_specification
        self.basedir = basedir
        self._settings = settings
        self._logger = logger
        self.exec_mngr = None
        self.program = None  # Program to start in the subprocess
        self.args = list()  # List of command line arguments for the program

    def is_running(self):
        return self.exec_mngr is not None

    def terminate_instance(self):
        """Terminates Tool instance execution."""
        if not self.exec_mngr:
            return
        self.exec_mngr.stop_execution()
        self.exec_mngr = None

    def remove(self):
        """[Obsolete] Removes Tool instance files from work directory."""
        shutil.rmtree(self.basedir, ignore_errors=True)

    def prepare(self, args):
        """Prepares this instance for execution.

        Implement in subclasses to perform specific initialization.

        Args:
            args (list): Tool cmd line args
        """
        raise NotImplementedError()

    def execute(self):
        """Executes a prepared instance. Implement in subclasses."""
        raise NotImplementedError()

    def append_cmdline_args(self, tool_args):
        """
        Appends Tool specification command line args into instance args list.

        Args:
            tool_args (list): List of Tool cmd line args
        """
        self.args += self.tool_specification.cmdline_args
        if tool_args:
            self.args += tool_args


class GAMSToolInstance(ToolInstance):
    """Class for GAMS Tool instances."""

    def prepare(self, args):
        """See base class."""
        gams_path = self._settings.value("appSettings/gamsPath", defaultValue="")
        if gams_path != "":
            gams_exe = gams_path
        else:
            gams_exe = GAMS_EXECUTABLE
        self.program = gams_exe
        self.args.append(self.tool_specification.main_prgm)
        self.args.append("curDir=")
        self.args.append(self.basedir)
        self.args.append("logoption=3")  # TODO: This should be an option in Settings
        self.append_cmdline_args(args)

    def execute(self):
        """Executes a prepared instance."""
        # TODO: Check if the below sets the curDir argument. Is the curDir arg now useless?
        self.exec_mngr = StandardExecutionManager(self._logger, self.program, *self.args, workdir=self.basedir)
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret


class JuliaToolInstance(ToolInstance):
    """Class for Julia Tool instances."""

    def prepare(self, args):
        """See base class."""
        work_dir = self.basedir
        use_embedded_julia = self._settings.value("appSettings/useEmbeddedJulia", defaultValue="2")
        if use_embedded_julia == "2":
            # Prepare Julia REPL command
            work_dir = repr(work_dir).strip("'")
            cmdline_args = self.tool_specification.cmdline_args + args
            cmdline_args = '["' + repr('", "'.join(cmdline_args)).strip("'") + '"]'
            self.args = []
            if work_dir:
                self.args += [f'cd("{work_dir}");']
            self.args += [
                f"empty!(ARGS); append!(ARGS, {cmdline_args});",
                f'include("{self.tool_specification.main_prgm}")',
            ]
        else:
            # Prepare command "julia --project={PROJECT_DIR} script.jl"
            julia_path = self._settings.value("appSettings/juliaPath", defaultValue="")
            if julia_path != "":
                julia_exe = julia_path
            else:
                julia_exe = JULIA_EXECUTABLE
            script_path = os.path.join(work_dir, self.tool_specification.main_prgm)
            julia_project_path = self._settings.value("appSettings/juliaProjectPath", defaultValue="")
            self.program = julia_exe
            self.args.append(f"--project={julia_project_path}")
            self.args.append(script_path)
            self.append_cmdline_args(args)

    def execute(self):
        """Executes a prepared instance."""
        if self._settings.value("appSettings/useEmbeddedJulia", defaultValue="2") == "2":
            return self._console_execute()
        return self._cmd_line_execute()

    def _console_execute(self):
        """Executes in console.
        """
        kernel_name = self._settings.value("appSettings/juliaKernel", defaultValue="")
        self.exec_mngr = KernelExecutionManager(self._logger, "julia", kernel_name, *self.args)
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret

    def _cmd_line_execute(self):
        """Executes in command line.
        """
        # On Julia the QProcess workdir must be set to the path where the main script is
        # Otherwise it doesn't find input files in subdirectories
        self.exec_mngr = StandardExecutionManager(self._logger, self.program, *self.args, workdir=self.basedir)
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret


class PythonToolInstance(ToolInstance):
    """Class for Python Tool instances."""

    def prepare(self, args):
        """See base class."""
        work_dir = self.basedir
        use_embedded_python = self._settings.value("appSettings/useEmbeddedPython", defaultValue="0")
        if use_embedded_python == "2":
            # Prepare a command list (FIFO queue) with two commands for Python Console
            # 1st cmd: Change current work directory
            # 2nd cmd: Run script with given args
            cd_work_dir_cmd = f"%cd -q {work_dir}"  # -q: quiet
            run_script_cmd = f'%run "{self.tool_specification.main_prgm}"'
            cmdline_args = self.tool_specification.cmdline_args + args
            if cmdline_args:
                run_script_cmd = run_script_cmd + " " + '"' + '" "'.join(cmdline_args) + '"'
            # Populate FIFO command queue
            self.args = [cd_work_dir_cmd, run_script_cmd]
        else:
            # Prepare command "python <script.py> <script_arguments>"
            script_path = os.path.join(work_dir, self.tool_specification.main_prgm)
            self.program = python_interpreter(self._settings)
            self.args.append(script_path)  # First argument for the Python interpreter is path to the tool script
            self.append_cmdline_args(args)

    def execute(self):
        """Executes a prepared instance."""
        if self._settings.value("appSettings/useEmbeddedPython", defaultValue="0") == "2":
            return self._console_execute()
        return self._cmd_line_execute()

    def _console_execute(self):
        """Executes in console.
        """
        kernel_name = self._settings.value("appSettings/pythonKernel", defaultValue="")
        self.exec_mngr = KernelExecutionManager(self._logger, "python", kernel_name, *self.args)
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret

    def _cmd_line_execute(self):
        """Executes in cmd line
        """
        self.exec_mngr = StandardExecutionManager(self._logger, self.program, *self.args, workdir=self.basedir)
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret


class ExecutableToolInstance(ToolInstance):
    """Class for Executable Tool instances."""

    def prepare(self, args):
        """See base class."""
        batch_path = os.path.join(self.basedir, self.tool_specification.main_prgm)
        if sys.platform != "win32":
            self.program = "sh"
            self.args.append(batch_path)
        else:
            self.program = batch_path
        self.append_cmdline_args(args)

    def execute(self):
        """Executes a prepared instance."""
        self.exec_mngr = StandardExecutionManager(self._logger, self.program, *self.args)
        ret = self.exec_mngr.run_until_complete(workdir=self.basedir)
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_mngr = None
        return ret
