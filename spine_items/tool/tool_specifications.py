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

"""Contains Tool specification classes."""
from collections import OrderedDict
import copy
import os.path
from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from spine_engine.utils.command_line_arguments import split_cmdline_args
from .item_info import ItemInfo
from .tool_instance import GAMSToolInstance, JuliaToolInstance, PythonToolInstance, ExecutableToolInstance


# Tool types
TOOL_TYPES = ["Julia", "Python", "GAMS", "Executable"]

# Required and optional keywords for Tool specification dictionaries
REQUIRED_KEYS = ["name", "tooltype", "includes"]
OPTIONAL_KEYS = [
    "description",
    "short_name",
    "inputfiles",
    "inputfiles_opt",
    "outputfiles",
    "cmdline_args",
    "execution_settings",
]
LIST_REQUIRED_KEYS = ["includes", "inputfiles", "inputfiles_opt", "outputfiles"]  # These should be lists


def make_specification(definition, app_settings, logger):
    """Deserializes and constructs a tool specification from definition.

    Args:
        definition (dict): a dictionary containing the serialized specification.
        app_settings (QSettings): Toolbox settings
        logger (LoggerInterface): a logger

    Returns:
        ToolSpecification: a tool specification constructed from the given definition,
            or None if there was an error
    """
    if not definition["includes_main_path"]:
        path = None
    else:
        definition["includes_main_path"] = path = definition.setdefault("includes_main_path", ".").replace(
            "/", os.path.sep
        )
        if not os.path.isabs(path):
            definition_file_path = definition["definition_file_path"]
            path = os.path.normpath(os.path.join(os.path.dirname(definition_file_path), path))
        definition["includes"] = [src_file.replace("/", os.path.sep) for src_file in definition["includes"]]
    try:
        _tooltype = definition["tooltype"].lower()
    except KeyError:
        logger.msg_error.emit(
            "No tool type defined in tool definition file. Supported types "
            "are 'python', 'gams', 'julia' and 'executable'"
        )
        return None
    if _tooltype == "julia":
        spec = JuliaTool.load(path, definition, app_settings, logger)
    elif _tooltype == "python":
        spec = PythonTool.load(path, definition, app_settings, logger)
    elif _tooltype == "gams":
        spec = GAMSTool.load(path, definition, app_settings, logger)
    elif _tooltype == "executable":
        spec = ExecutableTool.load(path, definition, app_settings, logger)
    else:
        logger.msg_warning.emit(f"Tool type <b>{_tooltype}</b> not available")
        return None
    return spec


class ToolSpecification(ProjectItemSpecification):
    """Super class for all tool specifications."""

    def __init__(
        self,
        name,
        tooltype,
        path,
        includes,
        settings,
        logger,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
    ):
        """

        Args:
            name (str): Tool specification name
            tooltype (str): Type of Tool Specification (e.g. Python, Julia, ..)
            path (str): Path to Tool specification
            includes (list): List of files belonging to the tool specification (relative to 'path')
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
            description (str): Description of the Tool specification
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (list, optional): Tool Specification command line arguments
        """
        super().__init__(name, description, item_type=ItemInfo.item_type())
        self._settings = settings
        self._logger = logger
        self.tooltype = tooltype
        self.path = path
        self.includes = includes
        if cmdline_args is not None:
            if isinstance(cmdline_args, str):
                # Old tool spec files may have the command line arguments as plain strings.
                self.cmdline_args = split_cmdline_args(cmdline_args)
            else:
                self.cmdline_args = cmdline_args
        else:
            self.cmdline_args = []
        self.inputfiles = set(inputfiles) if inputfiles else set()
        self.inputfiles_opt = set(inputfiles_opt) if inputfiles_opt else set()
        self.outputfiles = set(outputfiles) if outputfiles else set()
        self.return_codes = {}

    def _includes_main_path_relative(self):
        return os.path.relpath(self.path, os.path.dirname(self.definition_file_path)).replace(os.path.sep, "/")

    def clone(self):
        spec_dict = copy.deepcopy(self.to_dict())
        spec_dict["definition_file_path"] = self.definition_file_path
        return make_specification(spec_dict, self._settings, self._logger)

    def to_dict(self):
        return {
            "name": self.name,
            "tooltype": self.tooltype,
            "includes": [src_file.replace(os.path.sep, "/") for src_file in self.includes],
            "description": self.description,
            "inputfiles": sorted(self.inputfiles),
            "inputfiles_opt": sorted(self.inputfiles_opt),
            "outputfiles": sorted(self.outputfiles),
            "cmdline_args": self.cmdline_args,
            "includes_main_path": self._includes_main_path_relative(),
        }

    @staticmethod
    def _definition_local_entries():
        """See base class"""
        return [("execution_settings",)]

    def init_execution_settings(self):
        """Updates Tool specifications by adding the default execution settings dict for this specification."""

    def is_equivalent(self, other):
        """See base class."""
        for k, v in other.__dict__.items():
            if k in LIST_REQUIRED_KEYS:
                if set(self.__dict__[k]) != set(v):
                    return False
            else:
                if self.__dict__[k] != v:
                    return False
        return True

    def set_return_code(self, code, description):
        """Sets a return code and an associated text description for the tool specification.

        Args:
            code (int): Return code
            description (str): Description
        """
        self.return_codes[code] = description

    @staticmethod
    def check_definition(data, logger):
        """Checks that a tool specification contains
        the required keys and that it is in correct format.

        Args:
            data (dict): Tool specification
            logger (LoggerInterface): A logger instance

        Returns:
            dict: definition or None if there was a problem in the tool definition.
        """
        kwargs = dict()
        for p in REQUIRED_KEYS + OPTIONAL_KEYS:
            try:
                kwargs[p] = data[p]
            except KeyError:
                if p in REQUIRED_KEYS:
                    logger.msg_error.emit("Required keyword '{0}' missing".format(p))
                    return None
            # Check that some values are lists
            if p in LIST_REQUIRED_KEYS:
                try:
                    if not isinstance(data[p], list):
                        logger.msg_error.emit("Keyword '{0}' value must be a list".format(p))
                        return None
                except KeyError:
                    pass
        return kwargs

    def create_tool_instance(self, basedir, kill_completed_processes, logger, owner):
        """Returns an instance of this tool specification that is configured to run in the given directory.

        Args:
            basedir (str): Path to the directory where the instance will run
            kill_completed_processes (bool): whether to kill completed persistent processes
            logger (LoggerInterface): Logger
            owner (ExecutableItemBase): Project item that owns the instance
        """
        raise NotImplementedError()


class GAMSTool(ToolSpecification):
    """Class for GAMS tool specifications."""

    def __init__(
        self,
        name,
        tooltype,
        path,
        includes,
        settings,
        logger,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
    ):
        """

        Args:
            name (str): GAMS Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path').
                First file in the list is the main GAMS program.
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
            description (str): GAMS Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (list, optional): GAMS Tool Specification command line arguments
        """
        super().__init__(
            name,
            tooltype,
            path,
            includes,
            settings,
            logger,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
        )
        main_file = includes[0]
        # Add .lst file to list of output files
        self.lst_file = os.path.splitext(main_file)[0] + ".lst"
        self.outputfiles.add(self.lst_file)
        self.main_prgm = main_file
        self.gams_options = OrderedDict()
        self.return_codes = {
            0: "Normal return",
            1: "Solver is to be called the system should never return this number",  # ??
            2: "There was a compilation error",
            3: "There was an execution error",
            4: "System limits were reached",
            5: "There was a file error",
            6: "There was a parameter error",
            7: "There was a licensing error",
            8: "There was a GAMS system error",
            9: "GAMS could not be started",
            10: "Out of memory",
            11: "Out of disk",
            62097: "Simulation interrupted by user",  # Not official
        }

    def make_debug_project(self, basedir):
        """Make a GAMS project file and return an anchor for the execution item log.

        Args:
            basedir (str): Full path to work or source dir depending on execution mode

        Returns:
            Anchor to gamside project anchor or None if operation failed
        """
        prj_file_path = os.path.abspath(os.path.join(self.path, self.short_name + "_autocreated.gpr"))
        try:
            self.make_gamside_project_file(prj_file_path, basedir)
        except OSError:
            return None
        anchor = (
            "<a style='color:#99CCFF;' title='"
            + prj_file_path
            + "' href='file:///"
            + prj_file_path
            + "'>Click here to debug in GAMSIDE</a>"
        )
        return anchor

    def make_gamside_project_file(self, prj_file_path, basedir):
        """Make a GAMSIDE project file for debugging.

        Args:
            prj_file_path (str): Full path to GAMSIDE project file
            basedir (str): Full path to work or source dir depending on execution mode

        Returns:
            Full path to GAMSIDE project file or None if operation failed
        """
        lst_file_path = os.path.join(basedir, self.lst_file)  # We need the latest from work dir or from source dir
        main_prgm_path = os.path.join(self.path, self.main_prgm)  # Always get the one from source dir
        try:
            with open(prj_file_path, "w") as f:
                f.write("[PROJECT]\n\n")
                f.write("[MRUFILES]\n")  # Most Recently Used (MRU)
                f.write("1=" + lst_file_path + "\n\n")
                f.write("[OPENWINDOW_1]\n")
                f.write("FILE0=" + main_prgm_path + "\n")
                f.write("FILE1=" + lst_file_path + "\n")
                f.write("FILE2=" + main_prgm_path + "\n")
                f.write("MAXIM=0\n")
                f.write("TOP=0\n")
                f.write("LEFT=0\n")
                f.write("HEIGHT=600\n")
                f.write("WIDTH=1000\n")
        except OSError:
            raise

    @staticmethod
    def load(path, data, settings, logger):
        """Creates a GAMSTool according to a tool specification file.

        Args:
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance

        Returns:
            GAMSTool instance or None if there was a problem in the tool specification file.
        """
        kwargs = GAMSTool.check_definition(data, logger)
        if kwargs is not None:
            # Return an executable model instance
            return GAMSTool(path=path, settings=settings, logger=logger, **kwargs)
        return None

    def create_tool_instance(self, basedir, kill_completed_processes, logger, owner):
        """See base class."""
        return GAMSToolInstance(self, basedir, self._settings, logger, owner)


class JuliaTool(ToolSpecification):
    """Class for Julia tool specifications."""

    def __init__(
        self,
        name,
        tooltype,
        path,
        includes,
        settings,
        logger,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execution_settings=None,
    ):
        """
        Args:
            name (str): Julia Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path')
                First file in the list is the main Julia program.
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance
            description (str): Julia Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (list, optional): Julia Tool Specification command line arguments
            execution_settings (dict, optional): Julia tool spec execution settings
        """
        super().__init__(
            name,
            tooltype,
            path,
            includes,
            settings,
            logger,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
        )
        self.main_prgm = includes[0]
        self.julia_options = OrderedDict()
        self.execution_settings = execution_settings if execution_settings is not None else {}
        self.return_codes = {0: "Normal return", -1: "Failure"}

    def to_dict(self):
        """Adds execution settings dict to Tool spec dict."""
        d = super().to_dict()
        d["execution_settings"] = self.execution_settings
        return d

    def set_execution_settings(self, use_julia_jupyter_console, julia_exe, julia_project, julia_kernel):
        """Sets execution settings.

        Args:
            use_julia_jupyter_console (bool): True for Jupyter Console, False for Basic Console
            julia_exe (str): Abs. path to Julia executable
            julia_project (str): Julia project
            julia_kernel (str): Julia kernel for Jupyter Console
        """
        d = dict()
        d["kernel_spec_name"] = julia_kernel
        d["env"] = ""
        d["use_jupyter_console"] = use_julia_jupyter_console
        d["executable"] = julia_exe
        d["project"] = julia_project
        self.execution_settings = d

    def init_execution_settings(self):
        """Initializes execution_setting instance attribute to default settings."""
        if not self.execution_settings:
            # Use global (default) execution settings from Settings->Tools
            # This part is for providing support for Julia Tool specs that do not have
            # the execution_settings dict yet
            d = dict()
            d["kernel_spec_name"] = self._settings.value("appSettings/juliaKernel", defaultValue="")
            d["env"] = ""
            d["use_jupyter_console"] = bool(
                int(self._settings.value("appSettings/useJuliaKernel", defaultValue="0"))
            )  # bool(int(str))
            d["executable"] = self._settings.value("appSettings/juliaPath", defaultValue="")
            d["project"] = self._settings.value("appSettings/juliaProjectPath", defaultValue="")
            self.execution_settings = d

    @staticmethod
    def load(path, data, settings, logger):
        """Creates a JuliaTool according to a tool specification file.

        Args:
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions
            settings (QSetting): Toolbox settings
            logger (LoggerInterface): A logger instance

        Returns:
            JuliaTool instance or None if there was a problem in the tool definition file.
        """
        kwargs = JuliaTool.check_definition(data, logger)
        if kwargs is not None:
            # Return an executable model instance
            return JuliaTool(path=path, settings=settings, logger=logger, **kwargs)
        return None

    def create_tool_instance(self, basedir, kill_completed_processes, logger, owner):
        """See base class."""
        return JuliaToolInstance(self, basedir, self._settings, kill_completed_processes, logger, owner)


class PythonTool(ToolSpecification):
    """Class for Python tool specifications."""

    def __init__(
        self,
        name,
        tooltype,
        path,
        includes,
        settings,
        logger,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execution_settings=None,
    ):
        """
        Args:

            name (str): Python Tool name
            tooltype (str): Tool specification type
            path (str): Path to model main file
            includes (list): List of files belonging to the tool (relative to 'path').
                First file in the list is the main Python program.
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance
            description (str): Python Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (list, optional): Python Tool Specification command line arguments
            execution_settings (dict, optional): Python tool spec execution settings
        """
        super().__init__(
            name,
            tooltype,
            path,
            includes,
            settings,
            logger,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
        )
        self.main_prgm = includes[0]
        self.python_options = OrderedDict()
        self.execution_settings = execution_settings if execution_settings is not None else {}
        self.return_codes = {0: "Normal return", -1: "Failure"}  # Not official

    def to_dict(self):
        """Adds kernel spec settings dict to Tool spec dict."""
        d = super().to_dict()
        d["execution_settings"] = self.execution_settings
        return d

    def set_execution_settings(self, use_python_jupyter_console, python_exe, python_kernel, env):
        """Sets execution settings.

        Args:
            use_python_jupyter_console (bool): True for Jupyter Console, False for Basic Console
            python_exe (str): Abs. path to Python executable
            python_kernel (str): Julia kernel for Jupyter Console
            env (str): empty string for regular kernels, 'conda' for Conda kernels
        """
        d = dict()
        d["kernel_spec_name"] = python_kernel
        d["env"] = env
        d["use_jupyter_console"] = use_python_jupyter_console
        d["executable"] = python_exe
        self.execution_settings = d

    def init_execution_settings(self):
        """Sets the execution_setting instance attribute to defaults if this
        Python Tool spec has not been updated yet.

        Returns:
            void
        """
        if not self.execution_settings:
            # Use global (default) execution settings from Settings->Tools
            # This part is for providing support for Python Tool specs that do not have
            # the execution_settings dict yet
            d = dict()
            d["kernel_spec_name"] = self._settings.value("appSettings/pythonKernel", defaultValue="")
            d["env"] = ""
            d["use_jupyter_console"] = bool(
                int(self._settings.value("appSettings/usePythonKernel", defaultValue="0"))
            )  # bool(int(str))
            d["executable"] = self._settings.value("appSettings/pythonPath", defaultValue="")
            self.execution_settings = d

    @staticmethod
    def load(path, data, settings, logger):
        """Creates a PythonTool according to a tool specification file.

        Args:
            path (str): Base path to tool files
            data (dict): Dictionary of tool definitions
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance

        Returns:
            PythonTool instance or None if there was a problem in the tool definition file.
        """
        kwargs = PythonTool.check_definition(data, logger)
        if kwargs is not None:
            # Return an executable model instance
            return PythonTool(path=path, settings=settings, logger=logger, **kwargs)
        return None

    def create_tool_instance(self, basedir, kill_completed_processes, logger, owner):
        """See base class."""
        return PythonToolInstance(self, basedir, self._settings, kill_completed_processes, logger, owner)


class ExecutableTool(ToolSpecification):
    """Class for Executable tool specifications."""

    def __init__(
        self,
        name,
        tooltype,
        path,
        includes,
        settings,
        logger,
        description=None,
        inputfiles=None,
        inputfiles_opt=None,
        outputfiles=None,
        cmdline_args=None,
        execution_settings=None,
        definition_file_path=None,
    ):
        """
        Args:

            name (str): Tool name
            tooltype (str): Tool specification type
            path (str): Path to main script file
            includes (list): List of files belonging to the tool (relative to 'path')
                First file in the list is the main program file.
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance
            description (str): Tool description
            inputfiles (list): List of required data files
            inputfiles_opt (list, optional): List of optional data files (wildcards may be used)
            outputfiles (list, optional): List of output files (wildcards may be used)
            cmdline_args (list, optional): Executable Tool Specification command line arguments
            execution_settings (dict): Settings for executing a (shell) command instead of a file
            definition_file_path (str): Absolute path to spec definition file. Only used when running a (shell) command
                in 'source' execution mode
        """
        super().__init__(
            name,
            tooltype,
            path,
            includes,
            settings,
            logger,
            description,
            inputfiles,
            inputfiles_opt,
            outputfiles,
            cmdline_args,
        )
        try:
            self.main_prgm = includes[0]
        except IndexError:
            self.main_prgm = None
        self.execution_settings = execution_settings
        if definition_file_path and not path:
            # Set the default execution dir in source execution mode when running a command (no program files)
            # This part is processed when Tool Specs are loaded at app startup or when Spine Engine loads them
            # Note: When a Tool Spec is saved in Tool Spec Editor, definition_file_path == None
            # Default execution dir is the directory of the definition file path
            self.default_execution_dir, _ = os.path.split(definition_file_path)
        self.options = OrderedDict()
        self.return_codes = {0: "Normal exit", 1: "Error happened"}

    def to_dict(self):
        """Adds execution settings dict to Executable Tool spec dicts."""
        d = super().to_dict()
        d["execution_settings"] = self.execution_settings
        return d

    def _includes_main_path_relative(self):
        if not self.path:
            return None
        return super()._includes_main_path_relative()

    def init_execution_settings(self):
        """Updates old Executable Tool specifications by adding the
        default execution settings dict for this specification.

        Returns:
            void
        """
        if not self.execution_settings:
            d = dict()
            d["cmd"] = ""
            d["shell"] = ""
            self.execution_settings = d

    @staticmethod
    def load(path, data, settings, logger):
        """Creates an ExecutableTool according to a tool specification file.

        Args:
            path (str): Base path to tool files
            data (dict): Tool specification
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance

        Returns:
            ExecutableTool instance or None if there was a problem in the tool specification.
        """
        kwargs = ExecutableTool.check_definition(data, logger)
        if kwargs is not None:
            # Add definition_file_path. 'data' does not have definition_file_path
            # when creating a new Tool spec or editing an existing one in Tool Spec Editor.
            kwargs["definition_file_path"] = data.get("definition_file_path", None)
            # Return an executable model instance
            return ExecutableTool(path=path, settings=settings, logger=logger, **kwargs)
        return None

    def create_tool_instance(self, basedir, kill_completed_processes, logger, owner):
        """See base class."""
        return ExecutableToolInstance(self, basedir, self._settings, logger, owner)
