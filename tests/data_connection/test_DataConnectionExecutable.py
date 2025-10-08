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

"""Unit tests for DataConnectionExecutable."""
from multiprocessing import Lock
import pathlib
import tempfile
import unittest
from unittest import mock
from spine_engine import ExecutionDirection
from spine_engine.project_item.project_item_resource import file_resource_in_pack
from spine_items.data_connection.executable_item import ExecutableItem
from spine_items.data_connection.utils import FilePattern
from spine_items.utils import UrlDict


class TestDataConnectionExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Data Connection")

    def test_from_dict(self):
        logger = mock.MagicMock()
        item_dict = {
            "type": "Data Connection",
            "description": "",
            "x": 0,
            "y": 0,
            "file_references": [{"type": "path", "relative": True, "path": "temp/temp1.txt"}],
            "directory_references": [{"type": "path", "relative": True, "path": "root/stem/"}],
            "db_references": [],
            "db_credentials": {},
        }
        dc_data_dir = pathlib.Path(self._temp_dir.name, ".spinetoolbox", "items", "dc")
        dc_data_dir.mkdir(parents=True)
        temp_file_path = pathlib.Path(dc_data_dir, "file.txt")
        temp_file_path.touch()
        item = ExecutableItem.from_dict(item_dict, "DC", self._temp_dir.name, None, {}, logger)
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Data Connection", item.item_type())
        self.assertEqual(2, len(item._file_paths))

    def test_stop_execution(self):
        executable = ExecutableItem("name", [], [], [], [], self._temp_dir.name, mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute(self):
        executable = ExecutableItem("name", [], [], [], [], self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_output_resources_backward(self):
        dc_data_dir = pathlib.Path(self._temp_dir.name, ".spinetoolbox", "items", "name")
        dc_data_dir.mkdir(parents=True)
        temp_file_path = pathlib.Path(dc_data_dir, "file.txt")
        temp_file_path.touch()
        executable = ExecutableItem("name", ["file_reference"], [], [], [], self._temp_dir.name, mock.MagicMock())
        self.assertEqual(executable.output_resources(ExecutionDirection.BACKWARD), [])

    def test_output_resources_forward_with_file_reference(self):
        file_reference = pathlib.Path(self._temp_dir.name, "file_reference")
        file_reference.touch()
        dc_data_dir = pathlib.Path(self._temp_dir.name, ".spinetoolbox", "items", "name")
        dc_data_dir.mkdir(parents=True)
        temp_file_path = pathlib.Path(dc_data_dir, "data_file")
        temp_file_path.touch()
        executable = ExecutableItem("name", [str(file_reference)], [], [], [], self._temp_dir.name, mock.MagicMock())
        output_resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertEqual(len(output_resources), 2)
        resource = output_resources[0]
        self.assertEqual(resource.type_, "file")
        self.assertTrue(pathlib.Path(resource.path).samefile(file_reference))
        self.assertEqual(resource.metadata, {})
        resource = output_resources[1]
        self.assertEqual(resource.type_, "file")
        self.assertTrue(pathlib.Path(resource.path).samefile(temp_file_path))
        self.assertEqual(resource.metadata, {})

    def test_output_resources_forward_with_file_pattern(self):
        data_dir = pathlib.Path(self._temp_dir.name, "data_dir")
        data_dir.mkdir()
        file1 = data_dir / "file1.dat"
        file1.touch()
        file2 = data_dir / "file2.dat"
        file2.touch()
        file_pattern = FilePattern(data_dir, "*.dat")
        executable = ExecutableItem("name", [], [file_pattern], [], [], self._temp_dir.name, mock.MagicMock())
        output_resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertCountEqual(
            output_resources,
            [
                file_resource_in_pack("name", str(file_pattern), str(file1)),
                file_resource_in_pack("name", str(file_pattern), str(file2)),
            ],
        )

    def test_output_resources_forward_with_directory_reference(self):
        data_dir = pathlib.Path(self._temp_dir.name, "data")
        data_dir.mkdir(parents=True)
        executable = ExecutableItem("name", [], [], [str(data_dir)], [], self._temp_dir.name, mock.MagicMock())
        output_resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertEqual(len(output_resources), 1)
        resource = output_resources[0]
        self.assertEqual(resource.type_, "directory")
        self.assertTrue(pathlib.Path(resource.path).samefile(data_dir))
        self.assertEqual(resource.metadata, {})

    def test_output_resources_forward_with_database_reference(self):
        url: UrlDict = {
            "dialect": "mysql",
            "host": "example.com",
            "port": 2323,
            "database": "my_db",
            "schema": "private",
            "username": "john",
            "password": "rocha",
        }
        executable = ExecutableItem("name", [], [], [], [url], self._temp_dir.name, mock.MagicMock())
        output_resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertEqual(len(output_resources), 1)
        resource = output_resources[0]
        self.assertEqual(resource.type_, "url")
        self.assertTrue(resource.url, "mysql://john:rocha@example.com/my_db")
        self.assertEqual(resource.metadata, {"schema": "private"})


if __name__ == "__main__":
    unittest.main()
