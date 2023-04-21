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

"""
Contains unit tests for the tool_instance module.

"""
import sys
import unittest
from unittest import mock

from spine_engine.execution_managers.persistent_execution_manager import kill_persistent_processes
from spine_items.tool.tool_specifications import PythonTool


class TestPythonToolInstance(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        kill_persistent_processes()

    def test_prepare_with_cmd_line_arguments_in_jupyter_kernel(self):
        instance = self._make_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager"):
            instance.prepare(["arg1", "arg2"])
        self.assertEqual(instance.args, ['%cd -q path/', '%run "main.py" "arg1" "arg2"'])

    def test_prepare_with_empty_cmd_line_arguments_in_jupyter_kernel(self):
        instance = self._make_tool_instance(True)
        with mock.patch("spine_items.tool.tool_instance.KernelExecutionManager"):
            instance.prepare([])
        self.assertEqual(instance.args, ['%cd -q path/', '%run "main.py"'])

    def test_prepare_with_cmd_line_arguments_in_persistent_process(self):
        instance = self._make_tool_instance(False)
        with mock.patch("spine_engine.execution_managers.persistent_execution_manager.PersistentManagerBase"):
            instance.prepare(["arg1", "arg2"])
        self.assertEqual(instance.program, [sys.executable])
        self.assertEqual(instance.exec_mngr.alias, "python main.py arg1 arg2")
        instance.terminate_instance()

    def test_prepare_without_cmd_line_arguments_in_persistent_process(self):
        instance = self._make_tool_instance(False)
        with mock.patch("spine_engine.execution_managers.persistent_execution_manager.PersistentManagerBase"):
            instance.prepare([])
        self.assertEqual(instance.program, [sys.executable])
        self.assertEqual(instance.exec_mngr.alias, "python main.py")
        instance.terminate_instance()

    @staticmethod
    def _make_tool_instance(execute_in_embedded_console):
        settings = mock.NonCallableMagicMock()
        if execute_in_embedded_console:
            settings.value = mock.MagicMock(return_value="2")
        else:

            def get_setting(name, defaultValue):
                return {"appSettings/pythonPath": sys.executable, "appSettings/useEmbeddedPython": "0"}.get(
                    name, defaultValue
                )

            settings.value = mock.MagicMock(side_effect=get_setting)
        logger = mock.Mock()
        path = ""
        source_files = ["main.py"]
        specification = PythonTool("specification name", "python", path, source_files, settings, logger)
        base_directory = "path/"
        return specification.create_tool_instance(base_directory, False, logger, mock.Mock())


if __name__ == '__main__':
    unittest.main()
