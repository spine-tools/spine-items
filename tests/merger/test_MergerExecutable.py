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

"""Unit tests for MergerExecutable."""
from multiprocessing import Lock
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spinedb_api import create_new_spine_database, DatabaseMapping, import_functions
from spinedb_api.spine_db_server import db_server_manager
from spine_engine.project_item.project_item_resource import database_resource
from spine_engine.project_item.connection import Connection
from spine_engine.spine_engine import SpineEngine, SpineEngineState
from spine_items.merger.executable_item import ExecutableItem


class TestMergerExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Merger")

    def test_from_dict(self):
        name = "Output Data Store"
        item_dict = {"type": "Data Store", "description": "", "x": 0, "y": 0, "cancel_on_error": True}
        logger = mock.MagicMock()
        item = ExecutableItem.from_dict(item_dict, name, self._temp_dir.name, None, dict(), logger)
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Merger", item.item_type())

    def test_stop_execution(self):
        executable = ExecutableItem("name", True, self._temp_dir.name, mock.MagicMock())
        with mock.patch(
            "spine_engine.project_item.executable_item_base.ExecutableItemBase.stop_execution"
        ) as mock_stop_execution:
            executable.stop_execution()
            mock_stop_execution.assert_called_once()

    def test_execute(self):
        executable = ExecutableItem("name", True, self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))

    def test_execute_merge_two_dbs(self):
        """Creates two db's with some data and merges them to a third db."""
        db1_path = Path(self._temp_dir.name, "db1.sqlite")
        db1_url = "sqlite:///" + str(db1_path)
        # Add some data to db1
        with DatabaseMapping(db1_url, create=True) as db1_map:
            import_functions.import_entity_classes(db1_map, [("a",)])
            import_functions.import_entities(db1_map, [("a", "a_1")])
            db1_map.commit_session("Add an object class 'a' and an object for unit tests.")
        db2_path = Path(self._temp_dir.name, "db2.sqlite")
        db2_url = "sqlite:///" + str(db2_path)
        # Add some data to db2
        with DatabaseMapping(db2_url, create=True) as db2_map:
            import_functions.import_entity_classes(db2_map, [("b",)])
            import_functions.import_entities(db2_map, [("b", "b_1")])
            db2_map.commit_session("Add an object class 'b' and an object for unit tests.")
        # Make an empty output db
        db3_path = Path(self._temp_dir.name, "db3.sqlite")
        db3_url = "sqlite:///" + str(db3_path)
        create_new_spine_database(db3_url)
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        executable = ExecutableItem("name", True, self._temp_dir.name, logger)
        input_db_resources = [database_resource("provider", db1_url), database_resource("provider", db2_url)]
        output_db_resources = [database_resource("receiver", db3_url)]
        with db_server_manager() as mngr_queue:
            for r in input_db_resources + output_db_resources:
                r.metadata["db_server_manager_queue"] = mngr_queue
            self.assertTrue(executable.execute(input_db_resources, output_db_resources, Lock()))
        # Check output db
        with DatabaseMapping(db3_url) as output_db_map:
            class_list = output_db_map.query(output_db_map.entity_class_sq).all()
            self.assertEqual(len(class_list), 2)
            self.assertEqual(class_list[0].name, "a")
            self.assertEqual(class_list[1].name, "b")
            entity_list_a = output_db_map.query(output_db_map.entity_sq).filter_by(class_id=class_list[0].id).all()
            self.assertEqual(len(entity_list_a), 1)
            self.assertEqual(entity_list_a[0].name, "a_1")
            entity_list_b = output_db_map.query(output_db_map.entity_sq).filter_by(class_id=class_list[1].id).all()
            self.assertEqual(len(entity_list_b), 1)
            self.assertEqual(entity_list_b[0].name, "b_1")

    def test_write_order(self):
        db1_path = Path(self._temp_dir.name, "db1.sqlite")
        db1_url = "sqlite:///" + str(db1_path)
        # Add some data to db1
        with DatabaseMapping(db1_url, create=True) as db1_map:
            import_functions.import_data(db1_map, entity_classes=[("fish",)])
            db1_map.commit_session("Add test data.")
        db2_path = Path(self._temp_dir.name, "db2.sqlite")
        db2_url = "sqlite:///" + str(db2_path)
        # Add some data to db2
        with DatabaseMapping(db2_url, create=True) as db2_map:
            import_functions.import_data(db2_map, entity_classes=[("cat",)])
            db2_map.commit_session("Add test data.")
        # Make an empty output db
        db3_path = Path(self._temp_dir.name, "db3.sqlite")
        db3_url = "sqlite:///" + str(db3_path)
        # Make two mergers
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        merger1 = {"type": "Merger", "description": "", "cancel_on_error": True}
        merger2 = {"type": "Merger", "description": "", "cancel_on_error": True}
        # Make two input DS and one output DS
        input_ds_1 = {
            "type": "Data Store",
            "description": "",
            "url": {
                "dialect": "sqlite",
                "database": {
                    "type": "path",
                    "relative": False,
                    "path": str(db1_path),
                },
            },
        }
        input_ds_2 = {
            "type": "Data Store",
            "description": "",
            "url": {
                "dialect": "sqlite",
                "database": {
                    "type": "path",
                    "relative": False,
                    "path": str(db2_path),
                },
            },
        }
        output_ds = {
            "type": "Data Store",
            "description": "",
            "url": {
                "dialect": "sqlite",
                "database": {
                    "type": "path",
                    "relative": False,
                    "path": str(db3_path),
                },
            },
        }
        # Make connections
        conn1in = Connection("ds1", "right", "merger1", "left")
        conn2in = Connection("ds2", "right", "merger2", "left")
        conn1out = Connection("merger1", "left", "output_ds", "right", options={"write_index": 2})
        conn2out = Connection("merger2", "left", "output_ds", "right", options={"write_index": 1})
        # Make and run engine
        items = {"ds1": input_ds_1, "ds2": input_ds_2, "output_ds": output_ds, "merger1": merger1, "merger2": merger2}
        execution_permits = {name: True for name in items}
        # We can't easily enforce merger1 to execute before merger2 so the write index matters...
        # So for the moment, let's run 5 times and hope
        for _ in range(5):
            engine = SpineEngine(
                items=items,
                connections=[x.to_dict() for x in (conn1in, conn2in, conn1out, conn2out)],
                execution_permits=execution_permits,
                project_dir=self._temp_dir.name,
            )
            create_new_spine_database(db3_url)
            engine.run()
            self.assertEqual(engine.state(), SpineEngineState.COMPLETED)
            with DatabaseMapping(db3_url, create=True) as db3_map:
                commits = db3_map.query(db3_map.commit_sq).all()
            merger1_idx = next(iter(k for k, commit in enumerate(commits) if db1_url in commit.comment))
            merger2_idx = next(iter(k for k, commit in enumerate(commits) if db2_url in commit.comment))
            self.assertTrue(merger2_idx < merger1_idx)


if __name__ == "__main__":
    unittest.main()
