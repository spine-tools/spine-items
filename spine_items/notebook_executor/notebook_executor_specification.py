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
Contains Notebook Executor specification classes.

:authors: P. Savolainen (VTT), E. Rinne (VTT), M. Marin (KTH), R. Brady (UCD)
:date:   05.02.2021
"""

import os
import json

from spine_engine.project_item.project_item_specification import ProjectItemSpecification
from .item_info import ItemInfo
from .notebook_executor_instance import NoteBookExecutorInstance

REQUIRED_KEYS = ["name", "includes"]
OPTIONAL_KEYS = [
    "description",
    "short_name",
    "input_files",
    "input_vars",
    "output_vars",
    "cmdline_args",
    "output_files"
]
LIST_REQUIRED_KEYS = ["includes", "input_files", "output_files"]  # These should be lists


def make_specification(definition, app_settings, logger):
    """
    Deserializes and constructs a Notebook Executor specification from definition.

    Args:
        definition (dict): a dictionary containing the serialized specification.
        app_settings (QSettings): Toolbox settings
        logger (LoggerInterface): a logger
    Returns:
        NotebookExecutorSpecification: a Notebook Executor specification constructed from the given definition,
            or None if there was an error
    """
    path = definition["includes_main_path"]

    return NotebookExecutorSpecification.load(path, definition, app_settings, logger)


class NotebookExecutorSpecification(ProjectItemSpecification):
    """notebook executors specification"""
    def __init__(
            self,
            name,
            path,
            includes,
            settings,
            logger,
            description,
            input_vars=None,
            output_vars=None,
            cmdline_args=None,
            input_files=None,
            output_files=None
    ):
        """
        Args:

            name (str): Notebook Executor name
            path (str): Path to main script file
            includes (list): List of files belonging to the notebook executor (relative to 'path').
            First file in the list is the .ipynb file.
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance
            description (str): Notebook Executor description
            input_vars (str): Name of variables in parameter tagged cell of .ipynb file corresponding to inputs
            output_vars (str): Name of variables in parameter tagged cell of .ipynb file corresponding to outputs
            input_files (list): List of required data files
            output_files (list, optional): List of output files (wildcards may be used)
        """
        super().__init__(name, description, item_type=ItemInfo.item_type(), item_category=ItemInfo.item_category())
        self._settings = settings
        self._logger = logger
        if not os.path.exists(path):
            pass
        else:
            self.path = path
        notebook_ipynb = includes[0]
        self.main_dir, self.main_program = os.path.split(notebook_ipynb)
        self.includes = includes
        self.input_vars = input_vars
        self.output_vars = output_vars
        self.input_files = list(input_files) if input_files else list()
        self.output_files = list(output_files) if output_files else list()
        self.cmdline_args = cmdline_args

    def to_dict(self):
        return {
            "name": self.name,
            "includes": self.includes,
            "description": self.description,
            "input_vars": self.input_vars,
            "output_vars": self.output_vars,
            "cmdline_args": self.cmdline_args,
            "input_files": self.input_files,
            "output_files": self.output_files,
            "includes_main_path": self.path.replace(os.sep, "/"),
        }

    @staticmethod
    def check_definition(data, logger):
        """Checks that a Notebook Executor specification contains
        the required keys and that it is in correct format.

        Args:
            data (dict): Notebook Executor specification
            logger (LoggerInterface): A logger instance

        Returns:
            Dictionary or None if there was a problem in the Notebook Executor definition.
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

    def save(self):
        definition = self.to_dict()
        with open(self.definition_file_path, "w") as fp:
            try:
                json.dump(definition, fp, indent=4)
                return True
            except ValueError:
                self._logger.msg_error.emit(
                    "Saving Notebook Executor specification file failed. Path:{0}".format(self.definition_file_path)
                )
                return False

    @staticmethod
    def load(path, data, settings, logger):
        """Creates a PythonTool according to a Notebook Executor specification file.
        Args:
            path (str): Base path to Notebook Executor files
            data (dict): Dictionary of Notebook Executor definitions
            settings (QSettings): Toolbox settings
            logger (LoggerInterface): A logger instance

        Returns:
            Notebook Executor instance or None if there was a problem in the Notebook Executor definition file.
        """
        kwargs = NotebookExecutorSpecification.check_definition(data, logger)
        if kwargs is not None:
            # Return an executable model instance
            return NotebookExecutorSpecification(path=path, settings=settings, logger=logger, **kwargs)
        return None

    def create_instance(self, basedir, logger, owner):
        """Returns an instance of this Notebook Executor specification that is configured to run in the given directory.

        Args:
            basedir (str): the path to the directory where the instance will run
            logger (LoggerInterface)
            owner (ExecutableItemBase): The item that owns the instance
        """
        return NoteBookExecutorInstance(self, basedir, self._settings, logger, owner)

    def is_equivalent(self, other):
        """Checks if this spec is equivalent to the given definition dictionary.
        Used by the Notebook Executor spec widget when updating specs.

        Args:
            other (NotebookExecutorSpecification)

        Returns:
            bool: True if equivalent
        """
        for k, v in other.__dict__.items():
            if k in LIST_REQUIRED_KEYS:
                if set(self.__dict__[k]) != set(v):
                    return False
            else:
                if self.__dict__[k] != v:
                    return False
        return True
