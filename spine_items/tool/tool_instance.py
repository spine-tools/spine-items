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

"""Contains ToolInstance classes."""
import os
import sys
from spine_engine.utils.helpers import (
    resolve_python_interpreter,
    resolve_gams_executable,
    resolve_conda_executable,
)
from spine_engine.execution_managers.kernel_execution_manager import KernelExecutionManager
from spine_engine.execution_managers.process_execution_manager import ProcessExecutionManager
from spine_engine.execution_managers.persistent_execution_manager import (
    JuliaPersistentExecutionManager,
    PythonPersistentExecutionManager,
)
from spine_items.utils import escape_backward_slashes
from spine_items.tool.utils import get_julia_path_and_project


class ToolInstance:
    """Tool instance base class."""

    def __init__(self, tool_specification, basedir, settings, logger, owner):
        """
        Args:
            tool_specification (ToolSpecification): the tool specification for this instance
            basedir (str): the path to the directory where this instance should run
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
            owner (ExecutableItemBase): The item that owns the instance
        """
        self.tool_specification = tool_specification
        self.basedir = basedir
        self._settings = settings
        self._logger = logger
        self._owner = owner
        self.exec_mngr = None
        self.program = None  # Program to start in the subprocess
        self.args = list()  # List of command line arguments for the program
        self.killed = False

    def _update_killed(self):
        try:
            self.killed = self.exec_mngr.killed
        except AttributeError:
            pass

    @property
    def owner(self):
        return self._owner

    def is_running(self):
        return self.exec_mngr is not None

    def terminate_instance(self):
        """Terminates Tool instance execution."""
        if not self.exec_mngr:
            return
        self.exec_mngr.stop_execution()
        self.exec_mngr = None

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
        self.program = resolve_gams_executable(gams_path)
        self.args.append(self.tool_specification.main_prgm)
        self.args.append(f"curDir={self.basedir}")  # Set gams current working directory
        self.args.append("logoption=3")  # This could be an option in Settings
        self.append_cmdline_args(args)
        # Note: workdir=self.basedir sets the working directory for the subprocess.Popen process.
        self.exec_mngr = ProcessExecutionManager(self._logger, self.program, self.args, workdir=self.basedir)

    def execute(self):
        """Executes a prepared instance."""
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"Unknown return code ({ret})")
            debug_anchor = self.tool_specification.make_debug_project(self.basedir)
            if debug_anchor is not None:
                self._logger.msg.emit(f"{debug_anchor}")
        self._update_killed()
        self.exec_mngr = None
        return ret


class JuliaToolInstance(ToolInstance):
    """Class for Julia Tool instances."""

    def __init__(self, tool_specification, basedir, settings, kill_completed_processes, logger, owner):
        """
        Args:
            tool_specification (ToolSpecification): the tool specification for this instance
            basedir (str): the path to the directory where this instance should run
            settings (QSettings): Toolbox settings
            kill_completed_processes (bool): whether to kill completed persistent processes
            logger (LoggerInterface): a logger instance
            owner (ExecutableItemBase): The item that owns the instance
        """
        super().__init__(tool_specification, basedir, settings, logger, owner)
        self._kill_completed_processes = kill_completed_processes

    def prepare_sysimg_maker(self, julia_args, cmdline_args):
        """Prepare this instance for creating a sysimage.

        Args:
            julia_args (list): First item is the path to Julia executable, the remaining items
            are the initial args for Julia (ie. '--project=some/path')
            cmdline_args (list): Tool and Tool Spec cmd line args for the Julia script

        Returns:
            bool: True if making a sysimage has been enabled, False otherwise
        """
        make_sysimage = self._settings.value("appSettings/makeSysImage", defaultValue="false")
        if make_sysimage == "true":
            if self.tool_specification.main_prgm:
                julia_args.append(self.tool_specification.main_prgm)
            julia_args += cmdline_args
            self.exec_mngr = ProcessExecutionManager(self._logger, julia_args[0], julia_args[1:], workdir=self.basedir)
            return True
        return False

    def make_julia_commands(self, cmdline_args):
        """Returns a list of commands to execute in the Jupyter or in the Basic Console.
        Given cmdline_args (Tool and Tool Spec args) are embedded into the commands.

        Args:
            cmdline_args (list): Tool and Tool Spec cmd line args for the Julia script

        Returns:
            list of str: Commands to execute in the Julia Console
        """
        mod_work_dir = escape_backward_slashes(self.basedir)
        cmds = [f'cd("{mod_work_dir}");']
        if cmdline_args:
            fmt_cmdline_args = '["' + escape_backward_slashes('", "'.join(cmdline_args)) + '"]'
            cmds += [f"empty!(ARGS); append!(ARGS, {fmt_cmdline_args});"]
        cmds += [f'include("{self.tool_specification.main_prgm}")']
        return cmds

    def make_sysimage_arg(self):
        """Returns a '--sysimage=path/to/sysimage' arg for the Julia
        process or None if the sysimage path is missing or invalid."""
        sysimage_path = self._owner.options.get("julia_sysimage", "")
        if sysimage_path == "":
            return None
        if sysimage_path != "" and not os.path.isfile(sysimage_path):
            self._logger.msg_error.emit(f"Ignoring Sysimage <b>{sysimage_path}</b> because it does not exist")
            return None
        return f"--sysimage={sysimage_path}"

    def prepare(self, args):
        """See base class."""
        self.tool_specification.init_execution_settings()  # Set default execution settings if they are missing
        julia_args = get_julia_path_and_project(self.tool_specification.execution_settings, self._settings)
        if not julia_args:
            k_name = self.tool_specification.execution_settings["kernel_spec_name"]
            self._logger.msg_error(f"Invalid kernel '{k_name}'. Missing resource dir or corrupted kernel.json.")
            return
        cmdline_args = self.tool_specification.cmdline_args + args
        if self.prepare_sysimg_maker(julia_args, cmdline_args):
            return
        sysimage_arg = self.make_sysimage_arg()
        commands = self.make_julia_commands(cmdline_args)
        if self.tool_specification.execution_settings["use_jupyter_console"]:
            server_ip = "127.0.0.1"
            if self._settings.value("engineSettings/remoteExecutionEnabled", defaultValue="false") == "true":
                server_ip = self._settings.value("engineSettings/remoteHost", "")
            kernel_name = self.tool_specification.execution_settings["kernel_spec_name"]
            extra_switches = [sysimage_arg] if sysimage_arg else None
            self.exec_mngr = KernelExecutionManager(
                self._logger,
                kernel_name,
                commands,
                kill_completed=self._kill_completed_processes,
                group_id=self.owner.group_id,
                extra_switches=extra_switches,
                server_ip=server_ip,
            )
            return
        if sysimage_arg:
            julia_args.append(sysimage_arg)
        alias = f"julia {' '.join([self.tool_specification.main_prgm, *cmdline_args])}"
        self.exec_mngr = JuliaPersistentExecutionManager(
            self._logger, julia_args, commands, alias, self._kill_completed_processes, self.owner.group_id
        )

    def execute(self):
        """Executes a prepared instance."""
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self._update_killed()
        self.exec_mngr = None
        return ret


class PythonToolInstance(ToolInstance):
    """Class for Python Tool instances."""

    def __init__(self, tool_specification, basedir, settings, kill_completed_processes, logger, owner):
        """
        Args:
            tool_specification (ToolSpecification): the tool specification for this instance
            basedir (str): the path to the directory where this instance should run
            settings (QSettings): Toolbox settings
            kill_completed_processes (bool): whether to kill completed persistent processes
            logger (LoggerInterface): a logger instance
            owner (ExecutableItemBase): The item that owns the instance
        """
        super().__init__(tool_specification, basedir, settings, logger, owner)
        self._kill_completed_processes = kill_completed_processes

    def make_python_jupyter_console_commands(self, cmdline_args):
        """Returns commands to execute in the Python Jupyter Console.

        Args:
            cmdline_args (list): Tool and Tool Spec cmd line args

        Returns:
            list: List of commands for the Python Jupyter Console
        """
        cd_command = f"%cd -q {self.basedir}"  # -q: quiet
        main_command = f'%run "{self.tool_specification.main_prgm}"'
        if cmdline_args:
            main_command += " " + '"' + '" "'.join(cmdline_args) + '"'
        return [cd_command, main_command]

    def make_python_basic_console_commands(self, cmdline_args):
        """Returns commands to execute in the Python Basic Console.

        Args:
            cmdline_args (list): Tool and Tool Spec cmd line args

        Returns:
            list: List of commands for the Python Basic Console
        """
        commands = list()
        fp = self.tool_specification.main_prgm
        full_fp = os.path.join(self.basedir, self.tool_specification.main_prgm).replace(os.sep, "/")
        commandline_args = [full_fp] + cmdline_args
        fmt_cmdline_args = '["' + escape_backward_slashes('", "'.join(commandline_args)) + '"]'
        commands.append(f"import sys; sys.argv = {fmt_cmdline_args};")
        commands.append(f"import os; os.chdir({repr(self.basedir)})")
        commands += self._make_exec_code(fp, full_fp)
        return commands

    def prepare(self, args):
        """See base class."""
        self.tool_specification.init_execution_settings()  # Initialize execution settings
        cmdline_args = self.tool_specification.cmdline_args + args
        if self.tool_specification.execution_settings["use_jupyter_console"]:
            server_ip = "127.0.0.1"
            if self._settings.value("engineSettings/remoteExecutionEnabled", defaultValue="false") == "true":
                server_ip = self._settings.value("engineSettings/remoteHost", "")
            kernel_name = self.tool_specification.execution_settings["kernel_spec_name"]
            commands = self.make_python_jupyter_console_commands(cmdline_args)
            env = self.tool_specification.execution_settings["env"]  # Activate environment if "conda"
            conda_exe = resolve_conda_executable(self._settings.value("appSettings/condaPath", defaultValue=""))
            self.exec_mngr = KernelExecutionManager(
                self._logger,
                kernel_name,
                commands,
                kill_completed=self._kill_completed_processes,
                group_id=self.owner.group_id,
                environment=env,
                conda_exe=conda_exe,
                server_ip=server_ip,
            )
        else:
            interpreter = self.tool_specification.execution_settings["executable"]
            python_exe = interpreter if interpreter else resolve_python_interpreter(self._settings)
            commands = self.make_python_basic_console_commands(cmdline_args)
            alias = f"python {' '.join([self.tool_specification.main_prgm] + cmdline_args)}"
            self.exec_mngr = PythonPersistentExecutionManager(
                self._logger, [python_exe], commands, alias, self._kill_completed_processes, self.owner.group_id
            )

    @staticmethod
    def _make_exec_code(fp, full_fp):
        """Returns a list of lines of code to run this tool instance in a Python interactive session.

        Args:
            fp (str): relative path to main Python file
            full_fp (str): absolute path to the main Python file

        Returns:
            list of str: lines of code
        """
        globals_dict = "globals_dict = globals()"
        update_globals_dict = f'globals_dict.update({{"__file__": "{full_fp}", "__name__": "__main__"}})'
        compile_and_exec = (
            f"with open('{fp}', 'rb') as f: exec(compile(f.read(), '{fp}', 'exec'), globals_dict, globals_dict)"
            + os.linesep
        )
        return [globals_dict, update_globals_dict, compile_and_exec]

    def execute(self):
        """Executes a prepared instance."""
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self._update_killed()
        self.exec_mngr = None
        return ret


class ExecutableToolInstance(ToolInstance):
    """Class for Executable Tool instances."""

    def prepare(self, args):
        """See base class."""
        if not self.tool_specification.main_prgm:  # Run command
            cmd = self.tool_specification.execution_settings["cmd"].split()  # Convert str to list
            shell = self.tool_specification.execution_settings["shell"]
            if not shell:
                # If shell is not given (empty str), The first item in cmd list will be considered as self.program.
                # The rest of the cmd list will be considered as cmd line args
                self.program = cmd.pop(0)
            else:
                # If shell is given, the shell will be set as self.program and the cmd list will be considered
                # as cmd line args
                if shell == "bash":
                    self.program = "sh"
                else:
                    self.program = shell
            if self.program == "cmd.exe" or self.program == "cmd":
                # If cmd.exe shell is not given the /C flag, it will just open cmd.exe in the Execution Log
                if "/C" not in cmd:
                    cmd = ["/C"] + cmd
            # The final command line args list (self.args) consists of three (3) parts:
            # 1. The first part is the cmd list
            # 2. The second part is the Tool Specification cmd line args
            # 3. The third part is the Tool cmd line args
            self.args = cmd + self.tool_specification.cmdline_args + args
        else:  # Run main program file
            main_program_file = os.path.join(self.basedir, self.tool_specification.main_prgm)
            if os.path.isfile(main_program_file):
                if sys.platform != "win32":
                    self.program = "sh"
                    self.args.append(main_program_file)
                else:
                    self.program = main_program_file
                self.append_cmdline_args(args)
            else:
                raise RuntimeError(f"main program file {main_program_file} does not exist.")
        self.exec_mngr = ProcessExecutionManager(self._logger, self.program, self.args, workdir=self.basedir)

    def execute(self):
        """Executes a prepared instance."""
        ret = self.exec_mngr.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.tool_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self._update_killed()
        self.exec_mngr = None
        return ret
