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
Contains NotebookInstance class.

:authors: P. Savolainen (VTT), E. Rinne (VTT), R. Brady (UCD)
:date:   05.02.2021
"""
import os
import papermill as pm
from spine_engine.utils.helpers import python_interpreter
from spine_engine.execution_managers import StandardExecutionManager, KernelExecutionManager


class NotebookInstance:
    """Notebook instance base class."""

    def __init__(self, notebook_specification, basedir, settings, logger, owner):
        """

        Args:
            notebook_specification (NotebookSpecification): the notebook specification for this instance
            basedir (str): the path to the directory where this instance should run
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): a logger instance
            owner (ExecutableItemBase): The item that owns the instance
        """
        self.notebook_specification = notebook_specification
        self.basedir = basedir
        self._settings = settings
        self._logger = logger
        self._owner = owner
        self._input_vars = self.notebook_specification.input_vars
        self._output_vars = self.notebook_specification.output_vars
        self.exec_manager = None
        self.program = None
        self._nb_path = None
        self._nb_out_path = None
        self._nb_parameters = {}
        self.args = list()  # List of command line arguments for the program

    @property
    def owner(self):
        return self._owner

    def is_running(self):
        return self.exec_manager is not None

    def terminate_instance(self):
        """Terminates Notebook instance execution."""
        if not self.exec_manager:
            return
        self.exec_manager.stop_execution()
        self.exec_manager = None

    def prepare(self, nb_src_dst_mapping, args):
        """See base class."""
        append_out = "_out"
        if nb_src_dst_mapping:
            nb_src_name = self.notebook_specification.includes[0]
            self._nb_path = nb_src_dst_mapping[nb_src_name]
        else:
            self._nb_path = self.notebook_specification.includes[0]
        for i, name in enumerate(self._input_vars):
            self._nb_parameters[name] = args[i]
        nb_filename_split = os.path.splitext(self.notebook_specification.includes[0])
        nb_out_filename = nb_filename_split[0] + append_out + nb_filename_split[1]
        self._nb_out_path = os.path.join(self.basedir, nb_out_filename)
        if len(self.notebook_specification.output_files) > 0:
            for i, name in enumerate(self._output_vars):
                filename = self.notebook_specification.output_files[i]
                self._nb_parameters[name] = os.path.join(self.basedir, filename)

    def execute(self):
        """Executes a prepared instance."""
        # if self._settings.value("appSettings/useEmbeddedPython", defaultValue="0") == "2":
        #     return self._console_execute()
        return self._console_execute()

    def _console_execute(self):
        """Executes in console.
        """
        kernel_name = self._settings.value("appSettings/pythonKernel", defaultValue="")

        pm.execute_notebook(
            self._nb_path,
            self._nb_out_path,
            kernel_name=kernel_name,
            parameters=self._nb_parameters
        )
        # inspect new_book for
        return 0

    def _cmd_line_execute(self):
        """Executes in cmd line
        """
        self.exec_manager = StandardExecutionManager(self._logger, self.program, *self.args, workdir=self.basedir)
        ret = self.exec_manager.run_until_complete()
        if ret != 0:
            try:
                return_msg = self.notebook_specification.return_codes[ret]
                self._logger.msg_error.emit(f"\t<b>{return_msg}</b> [exit code:{ret}]")
            except KeyError:
                self._logger.msg_error.emit(f"\tUnknown return code ({ret})")
        self.exec_manager = None
        return ret

