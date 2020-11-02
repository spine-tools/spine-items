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
Unit tests for DataConnectionExecutable.

:author: A. Soininen (VTT)
:date:   6.4.2020
"""
import os
import pathlib
import tempfile
import unittest
from unittest import mock
from spine_engine import ExecutionDirection
from spine_items.data_connection.executable_item import ExecutableItem


class TestDataConnectionExecutable(unittest.TestCase):
    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Data Connection")

    def test_from_dict(self):
        logger = mock.MagicMock()
        item_dict = {
            "type": "Data Connection",
            "description": "",
            "x": 0,
            "y": 0,
            "references": [{"type": "path", "relative": True, "path": "/temp/temp1.txt"}],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            dc_data_dir = pathlib.Path(temp_dir, ".spinetoolbox", "items", "dc")
            dc_data_dir.mkdir(parents=True)
            temp_file_path = pathlib.Path(dc_data_dir, "file.txt")
            with open(temp_file_path, "w") as file:
                file.write("abc.txt")
            item = ExecutableItem.from_dict(item_dict, "DC", temp_dir, None, dict(), logger)
            self.assertIsInstance(item, ExecutableItem)
            self.assertEqual("Data Connection", item.item_type())
            self.assertEqual(2, len(item._files))

    def test_stop_execution(self):
        executable = ExecutableItem("name", [], [], mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute_backward(self):
        executable = ExecutableItem("name", [], [], mock.MagicMock())
        self.assertTrue(executable.execute([], ExecutionDirection.BACKWARD))

    def test_execute_forward(self):
        executable = ExecutableItem("name", [], [], mock.MagicMock())
        self.assertTrue(executable.execute([], ExecutionDirection.FORWARD))

    def test_output_resources_backward(self):
        executable = ExecutableItem("name", ["file_reference"], ["data_file"], mock.MagicMock())
        self.assertEqual(executable.output_resources(ExecutionDirection.BACKWARD), [])

    def test_output_resources_forward(self):
        file_reference = os.path.join(tempfile.gettempdir(), "file_reference")
        data_file = os.path.join(tempfile.gettempdir(), "data_file")
        executable = ExecutableItem("name", [file_reference], [data_file], mock.MagicMock())
        output_resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertEqual(len(output_resources), 2)
        resource = output_resources[0]
        self.assertEqual(resource.type_, "file")
        self.assertEqual(resource.path, file_reference)
        self.assertEqual(resource.metadata, {})
        resource = output_resources[1]
        self.assertEqual(resource.type_, "file")
        self.assertEqual(resource.path, data_file)
        self.assertEqual(resource.metadata, {})


if __name__ == "__main__":
    unittest.main()
