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
Unit tests for Gimlet ExecutableItem.

:author: P. Savolainen (VTT)
:date:   25.5.2020
"""
import os
import sys
import unittest
from tempfile import TemporaryDirectory
from unittest import mock
from spine_engine import ExecutionDirection
from spine_engine.execution_managers import StandardExecutionManager
from spine_items.gimlet.executable_item import ExecutableItem
from spine_items.utils import CmdLineArg


class TestGimletExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Gimlet")

    def test_from_dict(self):
        selections = [[".spinetoolbox/items/input_files/a.txt", True], [".spinetoolbox/items/input_files/b.txt", False]]
        item_dict = {
            "type": "Gimlet",
            "x": 0,
            "y": 0,
            "description": "",
            "use_shell": True,
            "shell_index": 0,
            "cmd": "dir",
            "file_selection": selections,
            "cmd_line_args": [{"type": "literal", "arg": "--show-hidden"}],
            "work_dir_mode": True,
        }
        mock_settings = _MockSettings()
        item = ExecutableItem.from_dict(
            item_dict,
            name="G",
            project_dir=self._temp_dir.name,
            app_settings=mock_settings,
            specifications=dict(),
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Gimlet", item.item_type())
        self.assertEqual("cmd.exe", item.shell_name)
        self.assertTrue(os.path.join(self._temp_dir.name, "g", "work"), item._work_dir)
        self.assertIsInstance(item._selected_files, list)
        self.assertEqual(item.cmd_list, [CmdLineArg("dir"), CmdLineArg("--show-hidden")])
        # Modify item_dict
        item_dict["use_shell"] = False
        item_dict["work_dir_mode"] = False
        item = ExecutableItem.from_dict(
            item_dict,
            name="G",
            project_dir=self._temp_dir.name,
            app_settings=mock_settings,
            specifications=dict(),
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Gimlet", item.item_type())
        self.assertEqual("", item.shell_name)
        prefix, work_dir_name = os.path.split(item._work_dir)
        self.assertEqual("some_path", prefix)
        self.assertEqual("g__", work_dir_name[0:3])  # work dir name must start with 'g__'
        self.assertEqual("__toolbox", work_dir_name[-9:])  # work dir name must end with '__toolbox'
        self.assertEqual([".spinetoolbox/items/input_files/a.txt"], item._selected_files)
        # Modify item_dict
        item_dict["use_shell"] = True
        item_dict["shell_index"] = 99  # Unsupported shell
        item = ExecutableItem.from_dict(
            item_dict,
            name="G",
            project_dir=self._temp_dir.name,
            app_settings=mock_settings,
            specifications=dict(),
            logger=mock.MagicMock(),
        )
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual(item.shell_name, "")

    def test_execute(self):
        # Test executing command 'cd' in cmd.exe.
        executable = ExecutableItem("name", "cmd.exe", ["cd"], None, [], self._temp_dir.name, mock.MagicMock())
        expected_result = sys.platform == "win32"
        self.assertEqual(expected_result, executable.execute([], []))
        # Test that bash shell execution works on Linux.
        executable = ExecutableItem("name", "bash", ["ls"], None, [], self._temp_dir.name, mock.MagicMock())
        expected_result = sys.platform == "linux"
        self.assertEqual(expected_result, executable.execute([], []))

    def test_output_resources_backward(self):
        executable = ExecutableItem("name", "cmd.exe", ["cd"], None, [], self._temp_dir.name, mock.MagicMock())
        self.assertEqual(executable.output_resources(ExecutionDirection.BACKWARD), [])

    def test_output_resources_forward(self):
        with TemporaryDirectory() as temp_dir:
            executable = ExecutableItem("name", "cmd.exe", ["cd"], None, [], self._temp_dir.name, mock.MagicMock())
            self.assertEqual(executable.output_resources(ExecutionDirection.FORWARD), [])

    def test_stop_execution(self):
        logger = mock.MagicMock()
        prgm = "cmd.exe"
        cmd_list = ["dir"]
        executable = ExecutableItem("name", prgm, cmd_list, None, [], self._temp_dir.name, logger())
        executable._exec_mngr = StandardExecutionManager(logger, prgm, *cmd_list)
        executable.stop_execution()
        self.assertIsNone(executable._exec_mngr)


class FakeProvider:
    def __init__(self, name):
        self.name = name


class _MockSettings:
    @staticmethod
    def value(key, defaultValue=None):
        return {"appSettings/workDir": "some_path"}.get(key, defaultValue)


if __name__ == "__main__":
    unittest.main()
