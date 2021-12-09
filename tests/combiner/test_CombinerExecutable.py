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
Unit tests for CombinerExecutable.

:author: A. Soininen
:date:   6.4.2020
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spinedb_api import create_new_spine_database, DatabaseMapping, DiffDatabaseMapping, import_functions
from spine_items.combiner.executable_item import ExecutableItem
from spine_engine.project_item.project_item_resource import database_resource


class TestCombinerExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Combiner")

    def test_from_dict(self):
        name = "Output Data Store"
        item_dict = {
            "type": "Data Store",
            "description": "",
            "x": 0,
            "y": 0,
            "cancel_on_error": True,
        }
        logger = mock.MagicMock()
        item = ExecutableItem.from_dict(item_dict, name, self._temp_dir.name, None, dict(), logger)
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Combiner", item.item_type())

    def test_stop_execution(self):
        executable = ExecutableItem("name", "", self._temp_dir.name, mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute(self):
        executable = ExecutableItem("name", "", self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], []))

    def test_execute_merge_two_dbs(self):
        """Creates two db's with some data and merges them to a third db."""
        db1_path = Path(self._temp_dir.name, "db1.sqlite")
        db1_url = "sqlite:///" + str(db1_path)
        create_new_spine_database(db1_url)
        # Add some data to db1
        db1_map = DiffDatabaseMapping(db1_url)
        import_functions.import_object_classes(db1_map, ["a"])
        import_functions.import_objects(db1_map, [("a", "a_1")])
        # Commit to db1
        db1_map.commit_session("Add an object class 'a' and an object for unit tests.")
        db2_path = Path(self._temp_dir.name, "db2.sqlite")
        db2_url = "sqlite:///" + str(db2_path)
        create_new_spine_database(db2_url)
        # Add some data to db2
        db2_map = DiffDatabaseMapping(db2_url)
        import_functions.import_object_classes(db2_map, ["b"])
        import_functions.import_objects(db2_map, [("b", "b_1")])
        # Commit to db2
        db2_map.commit_session("Add an object class 'b' and an object for unit tests.")
        # Close connections
        db1_map.connection.close()
        db2_map.connection.close()
        # Make an empty output db
        db3_path = Path(self._temp_dir.name, "db3.sqlite")
        db3_url = "sqlite:///" + str(db3_path)
        create_new_spine_database(db3_url)
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        executable = ExecutableItem("name", False, self._temp_dir.name, logger)
        input_db_resources = [database_resource("provider", db1_url), database_resource("provider", db2_url)]
        output_db_resources = [database_resource("receiver", db3_url)]
        self.assertTrue(executable.execute(input_db_resources, output_db_resources))
        # Check output db
        output_db_map = DatabaseMapping(db3_url)
        class_list = output_db_map.object_class_list().all()
        self.assertEqual(len(class_list), 2)
        self.assertEqual(class_list[0].name, "a")
        self.assertEqual(class_list[1].name, "b")
        object_list_a = output_db_map.object_list(class_id=class_list[0].id).all()
        self.assertEqual(len(object_list_a), 1)
        self.assertEqual(object_list_a[0].name, "a_1")
        object_list_b = output_db_map.object_list(class_id=class_list[1].id).all()
        self.assertEqual(len(object_list_b), 1)
        self.assertEqual(object_list_b[0].name, "b_1")
        output_db_map.connection.close()


if __name__ == "__main__":
    unittest.main()
