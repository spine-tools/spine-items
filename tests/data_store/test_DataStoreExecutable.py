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

"""Unit tests for DataStoreExecutable."""
from multiprocessing import Lock
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spine_engine import ExecutionDirection
from spine_items.data_store.executable_item import ExecutableItem
from spine_items.utils import convert_to_sqlalchemy_url


class TestDataStoreExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Data Store")

    def test_from_dict(self):
        name = "Output Data Store"
        item_dict = {
            "type": "Data Store",
            "description": "",
            "x": 0,
            "y": 0,
            "url": {
                "dialect": "sqlite",
                "username": "",
                "password": "",
                "host": "",
                "port": "",
                "database": {
                    "type": "path",
                    "relative": True,
                    "path": ".spinetoolbox/items/output_data_store/Data Store 2.sqlite",
                },
            },
        }
        logger = mock.MagicMock()
        with mock.patch("spine_items.data_store.executable_item.convert_to_sqlalchemy_url") as mock_convert_url:
            mock_convert_url.return_value = "database.sqlite"
            item = ExecutableItem.from_dict(item_dict, name, self._temp_dir.name, None, dict(), logger)
            mock_convert_url.assert_called_once()
            self.assertIsInstance(item, ExecutableItem)
            self.assertEqual("Data Store", item.item_type())
            self.assertEqual("database.sqlite", item._url)

    def test_stop_execution(self):
        executable = ExecutableItem("name", "", self._temp_dir.name, mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute(self):
        executable = ExecutableItem("name", "", self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_output_resources_backward(self):
        db_file_path = Path(self._temp_dir.name, "database.sqlite")
        db_file_path.touch()
        url = convert_to_sqlalchemy_url({"dialect": "sqlite", "database": str(db_file_path)})
        executable = ExecutableItem("name", url, self._temp_dir.name, mock.MagicMock())
        with mock.patch("spine_items.data_store.executable_item.DatabaseMapping.create_engine"):
            resources = executable.output_resources(ExecutionDirection.BACKWARD)
        self.assertEqual(len(resources), 1)
        resource = resources[0]
        self.assertEqual(resource.type_, "database")
        self.assertEqual(resource.url, "sqlite:///" + str(db_file_path))
        self.assertEqual(resource.label, "db_url@name")

    def test_output_resources_forward(self):
        db_file_path = Path(self._temp_dir.name, "database.sqlite")
        db_file_path.touch()
        url = convert_to_sqlalchemy_url({"dialect": "sqlite", "database": str(db_file_path)})
        executable = ExecutableItem("name", url, self._temp_dir.name, mock.MagicMock())
        with mock.patch("spine_items.data_store.executable_item.DatabaseMapping.create_engine"):
            resources = executable.output_resources(ExecutionDirection.FORWARD)
        self.assertEqual(len(resources), 1)
        resource = resources[0]
        self.assertEqual(resource.type_, "database")
        self.assertEqual(resource.url, "sqlite:///" + str(db_file_path))
        self.assertEqual(resource.label, "db_url@name")


if __name__ == "__main__":
    unittest.main()
