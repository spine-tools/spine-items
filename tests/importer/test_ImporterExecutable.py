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

"""Unit tests for ImporterExecutable."""
from multiprocessing import Lock
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from spinedb_api import create_new_spine_database, DatabaseMapping
from spinedb_api.spine_db_server import db_server_manager
from spine_engine.project_item.project_item_resource import database_resource, file_resource
from spine_items.importer.executable_item import ExecutableItem
from spine_items.importer.importer_specification import ImporterSpecification


class TestImporterExecutable(unittest.TestCase):
    def setUp(self):
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        self._temp_dir.cleanup()

    def test_item_type(self):
        self.assertEqual(ExecutableItem.item_type(), "Importer")

    def test_from_dict(self):
        item_dict = {
            "type": "Importer",
            "description": "",
            "x": 0,
            "y": 0,
            "specification": "importer_spec",
            "cancel_on_error": True,
            "on_conflict": "merge",
            "mapping_selection": [
                [{"type": "path", "relative": True, "path": ".spinetoolbox/items/data/units.xlsx"}, True]
            ],
        }
        spec_dict = {
            "name": "importer_spec",
            "description": "Some importer spec",
            "mapping": {
                "table_mappings": {
                    "Sheet1": [
                        {
                            "map_type": "ObjectClass",
                            "name": {"map_type": "column", "reference": 0},
                            "parameters": {"map_type": "None"},
                            "skip_columns": [],
                            "read_start_row": 0,
                            "objects": {"map_type": "column", "reference": 1},
                        }
                    ]
                },
                "table_options": {},
                "table_types": {"Sheet1": {"0": "string", "1": "string"}},
                "table_row_types": {},
                "selected_tables": ["Sheet1"],
                "source_type": "ExcelConnector",
            },
        }
        logger = mock.MagicMock()
        specs = {"Importer": {"importer_spec": ImporterSpecification.from_dict(spec_dict, logger)}}
        item = ExecutableItem.from_dict(item_dict, "name", self._temp_dir.name, _MockSettings(), specs, logger)
        self.assertIsInstance(item, ExecutableItem)
        self.assertEqual("Importer", item.item_type())

    def test_stop_execution(self):
        executable = ExecutableItem("name", {}, [], "", True, "merge", self._temp_dir.name, mock.MagicMock())
        executable.stop_execution()
        self.assertIsNone(executable._process)

    def test_execute_simplest_case(self):
        executable = ExecutableItem("name", {}, [], "", True, "merge", self._temp_dir.name, mock.MagicMock())
        self.assertTrue(executable.execute([], [], Lock()))
        # Check that _process is None after execution
        self.assertIsNone(executable._process)

    def test_execute_import_small_file(self):
        data_file = Path(self._temp_dir.name, "data.dat")
        self._write_simple_data(data_file)
        mapping = self._simple_input_data_mapping()
        database_path = Path(self._temp_dir.name, "database.sqlite")
        database_url = "sqlite:///" + str(database_path)
        create_new_spine_database(database_url)
        gams_path = ""
        logger = mock.MagicMock()
        logger.__reduce__ = lambda _: (mock.MagicMock, ())
        executable = ExecutableItem(
            "name", mapping, [str(data_file)], gams_path, True, "merge", self._temp_dir.name, logger
        )
        database_resources = [database_resource("provider", database_url)]
        file_resources = [file_resource("provider", str(data_file))]
        with db_server_manager() as mngr_queue:
            for r in database_resources:
                r.metadata["db_server_manager_queue"] = mngr_queue
            self.assertTrue(executable.execute(file_resources, database_resources, Lock()))
        # Check that _process is None after execution
        self.assertIsNone(executable._process)
        with DatabaseMapping(database_url) as database_map:
            class_list = database_map.query(database_map.entity_class_sq).all()
            self.assertEqual(len(class_list), 1)
            self.assertEqual(class_list[0].name, "class")
            entity_list = database_map.query(database_map.entity_sq).filter_by(class_id=class_list[0].id).all()
            self.assertEqual(len(entity_list), 1)
            self.assertEqual(entity_list[0].name, "entity")

    def test_execute_skip_deselected_file(self):
        data_file = Path(self._temp_dir.name, "data.dat")
        self._write_simple_data(data_file)
        database_path = Path(self._temp_dir.name, "database.sqlite")
        database_url = "sqlite:///" + str(database_path)
        create_new_spine_database(database_url)
        gams_path = ""
        executable = ExecutableItem("name", {}, [], gams_path, True, "merge", self._temp_dir.name, mock.MagicMock())
        database_resources = [database_resource("provider", database_url)]
        file_resources = [file_resource("provider", str(data_file))]
        self.assertTrue(executable.execute(file_resources, database_resources, Lock()))
        # Check that _process is None after execution
        self.assertIsNone(executable._process)
        with DatabaseMapping(database_url) as database_map:
            class_list = database_map.query(database_map.entity_class_sq).all()
            self.assertEqual(len(class_list), 0)

    @staticmethod
    def _write_simple_data(file_name):
        with open(file_name, "w") as out_file:
            out_file.write("class,entity\n")

    @staticmethod
    def _simple_input_data_mapping():
        return {
            "table_mappings": {
                "csv": [
                    {
                        "map_type": "ObjectClass",
                        "name": {"map_type": "column", "reference": 0},
                        "parameters": {"map_type": "None"},
                        "skip_columns": [],
                        "read_start_row": 0,
                        "objects": {"map_type": "column", "reference": 1},
                    }
                ]
            },
            "table_options": {
                "csv": {
                    "encoding": "ascii",
                    "delimeter": ",",
                    "delimiter_custom": "",
                    "quotechar": '"',
                    "skip_header": False,
                    "skip": 0,
                }
            },
            "table_types": {"csv": {0: "string", 1: "string"}},
            "table_row_types": {},
            "selected_tables": ["csv"],
            "source_type": "CSVConnector",
        }


class _MockSettings:
    @staticmethod
    def value(key, defaultValue=None):
        return {"appSettings/gamsPath": ""}.get(key, defaultValue)


if __name__ == "__main__":
    unittest.main()
