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

"""Unit tests for Exporter's :func:`do_work` function."""
from csv import reader
import os.path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock
from spinedb_api import DatabaseMapping, import_object_classes, import_objects
from spinedb_api.export_mapping.export_mapping import FixedValueMapping
from spinedb_api.export_mapping.group_functions import NoGroup
from spinedb_api.export_mapping import entity_export
from spine_items.exporter.do_work import do_work
from spine_items.exporter.specification import OutputFormat, Specification, MappingSpecification, MappingType
from spinedb_api.mapping import Position


class TestWithCsvWriter(unittest.TestCase):
    _temp_dir = None
    _url = None

    @classmethod
    def setUpClass(cls):
        cls._temp_dir = TemporaryDirectory()
        db_file = os.path.join(cls._temp_dir.name, "test_db.sqlite")
        cls._url = "sqlite:///" + db_file
        with DatabaseMapping(cls._url, create=True) as db_map:
            import_object_classes(db_map, ("oc1", "oc2"))
            import_objects(db_map, (("oc1", "o11"), ("oc1", "o12"), ("oc2", "o21"), ("oc2", "o22"), ("oc2", "o23")))
            db_map.commit_session("Add test data.")

    def test_export_database(self):
        root_mapping = entity_export(entity_class_position=0, entity_position=1)
        mapping_specification = MappingSpecification(
            MappingType.entities, True, True, NoGroup.NAME, False, root_mapping
        )
        specification = Specification("name", "description", {"mapping": mapping_specification})
        databases = {self._url: "test_export_database.csv"}
        logger = MagicMock()
        self.assertTrue(
            do_work(None, specification.to_dict(), False, False, "", self._temp_dir.name, databases, {}, "", "", logger)
        )
        out_path = os.path.join(self._temp_dir.name, "test_export_database.csv")
        self.assertTrue(os.path.exists(out_path))
        with open(out_path) as input_:
            csv_reader = reader(input_)
            table = [row for row in csv_reader]
        expected = [["oc1", "o11"], ["oc1", "o12"], ["oc2", "o21"], ["oc2", "o22"], ["oc2", "o23"]]
        self.assertEqual(table, expected)

    def test_export_to_output_database(self):
        object_root = entity_export(entity_class_position=0, entity_position=1)
        object_root.header = "object_class"
        object_root.child.header = "object"
        root_mapping = FixedValueMapping(Position.table_name, "data_table")
        root_mapping.child = object_root
        mapping_specification = MappingSpecification(
            MappingType.entities, True, True, NoGroup.NAME, False, root_mapping
        )
        specification = Specification("name", "description", {"mapping": mapping_specification}, OutputFormat.SQL)
        databases = {self._url: "output label"}
        out_path = os.path.join(self._temp_dir.name, "out_database.sqlite")
        out_urls = {self._url: {"dialect": "sqlite", "database": out_path}}
        logger = MagicMock()
        self.assertTrue(
            do_work(
                None,
                specification.to_dict(),
                False,
                False,
                "",
                self._temp_dir.name,
                databases,
                out_urls,
                "",
                "",
                logger,
            )
        )
        self.assertTrue(os.path.exists(out_path))
        connection = sqlite3.connect(out_path)
        cursor = connection.cursor()
        expected = [("oc1", "o11"), ("oc1", "o12"), ("oc2", "o21"), ("oc2", "o22"), ("oc2", "o23")]
        self.assertEqual(cursor.execute("SELECT * FROM data_table").fetchall(), expected)
        connection.close()


if __name__ == "__main__":
    unittest.main()
