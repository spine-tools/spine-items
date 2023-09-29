######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains unit tests for the tool_instance module."""

import sys
import unittest
from unittest import mock
from spine_items.tool.tool_specifications import PythonTool, JuliaTool
from tests.mock_helpers import MockQSettings


class TestToolInstance(unittest.TestCase):
    def test_python_prepare_with_cmd_line_arguments_in_jupyter_console(self):
        instance = self._make_python_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager"):
            instance.prepare(["arg1", "arg2"])
        self.assertEqual(instance.args, ['%cd -q path/', '%run "main.py" "arg1" "arg2"'])

    def test_python_prepare_without_cmd_line_arguments_in_jupyter_console(self):
        instance = self._make_python_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager"):
            instance.prepare([])
        self.assertEqual(instance.args, ['%cd -q path/', '%run "main.py"'])

    def test_python_prepare_with_cmd_line_arguments_in_basic_console(self):
        instance = self._make_python_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.PythonPersistentExecutionManager") as mock_manager:
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])
            mock_manager.assert_called()
            alias = mock_manager.call_args[0][3]
            self.assertEqual("python main.py arg1 arg2", alias)
            self.assertEqual(instance.program, [sys.executable])

    def test_python_prepare_without_cmd_line_arguments_in_basic_console(self):
        instance = self._make_python_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.PythonPersistentExecutionManager") as mock_manager:
            mock_manager.return_value = True
            instance.prepare([])
            mock_manager.assert_called()
            alias = mock_manager.call_args[0][3]
            self.assertEqual("python main.py", alias)
            self.assertEqual(instance.program, [sys.executable])

    def test_julia_prepare_with_cmd_line_arguments_in_jupyter_console(self):
        instance = self._make_julia_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_kem, mock.patch(
            "os.path.isfile"
        ) as mock_isfile:
            mock_isfile.return_value = False
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            self.assertEqual(
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg1", "arg2"]);', 'include("hello.jl")'], instance.args
            )

    def test_julia_prepare_without_cmd_line_arguments_in_jupyter_console(self):
        instance = self._make_julia_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager") as mock_kem, mock.patch(
            "os.path.isfile"
        ) as mock_isfile:
            mock_isfile.return_value = False
            instance.prepare([])
            mock_isfile.assert_called()
            self.assertEqual(['cd("path/");', 'include("hello.jl")'], instance.args)

    def test_julia_prepare_with_cmd_line_arguments_in_basic_console(self):
        instance = self._make_julia_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.JuliaPersistentExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile:
            mock_isfile.return_value = False
            mock_manager.return_value = True
            instance.prepare(["arg1", "arg2"])
            mock_isfile.assert_called()
            mock_manager.assert_called()
            alias = mock_manager.call_args[0][3]
            self.assertEqual("julia hello.jl arg1 arg2", alias)
            self.assertEqual([""], instance.program)  # Default setting for Julia exe
            self.assertEqual(
                ['cd("path/");', 'empty!(ARGS); append!(ARGS, ["arg1", "arg2"]);', 'include("hello.jl")'], instance.args
            )

    def test_julia_prepare_without_cmd_line_arguments_in_basic_console(self):
        instance = self._make_julia_tool_instance(False)
        with mock.patch("spine_items.tool.tool_instance.JuliaPersistentExecutionManager") as mock_manager, mock.patch(
            "os.path.isfile"
        ) as mock_isfile:
            mock_isfile.return_value = False
            mock_manager.return_value = True
            instance.prepare([])
            mock_isfile.assert_called()
            mock_manager.assert_called()
            alias = mock_manager.call_args[0][3]
            self.assertEqual("julia hello.jl", alias)
            self.assertEqual([""], instance.program)  # Default setting for Julia exe
            self.assertEqual(['cd("path/");', 'include("hello.jl")'], instance.args)

    @staticmethod
    def _make_python_tool_instance(use_jupyter_console):
        logger = mock.MagicMock()
        specification = PythonTool("specification name", "python", "", ["main.py"], MockQSettings(), mock.MagicMock())
        specification.set_execution_settings()
        if use_jupyter_console:
            specification.execution_settings["use_jupyter_console"] = True
        base_directory = "path/"
        return specification.create_tool_instance(base_directory, False, logger, mock.Mock())

    @staticmethod
    def _make_julia_tool_instance(use_jupyter_console):
        logger = mock.MagicMock()
        source_files = ["hello.jl"]
        specification = JuliaTool("specification name", "julia", "", source_files, MockQSettings(), mock.MagicMock())
        specification.set_execution_settings()
        if use_jupyter_console:
            specification.execution_settings["use_jupyter_console"] = True
        base_directory = "path/"
        return specification.create_tool_instance(base_directory, False, logger, mock.Mock())


if __name__ == '__main__':
    unittest.main()
