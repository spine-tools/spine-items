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
Unit tests for Exporter's :func:`do_work` function.

:authors: A. Soininen (VTT)
:date:    14.12.2020
"""
from csv import reader
import os.path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock
from spinedb_api import DiffDatabaseMapping, import_object_classes, import_objects
from spinedb_api.export_mapping import object_export
from spine_items.exporter.do_work import do_work
from spine_items.exporter.specification import Specification, MappingSpecification, MappingType


class TestWithCsvWriter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temp_dir = TemporaryDirectory()
        db_file = os.path.join(cls._temp_dir.name, "test_db.sqlite")
        cls._url = "sqlite:///" + db_file
        db_map = DiffDatabaseMapping(cls._url, create=True)
        try:
            import_object_classes(db_map, ("oc1", "oc2"))
            import_objects(db_map, (("oc1", "o11"), ("oc1", "o12"), ("oc2", "o21"), ("oc2", "o22"), ("oc2", "o23")))
            db_map.commit_session("Add test data.")
        finally:
            db_map.connection.close()

    def test_export_database(self):
        root_mapping = object_export(class_position=0, object_position=1)
        mapping_specification = MappingSpecification(MappingType.objects, False, False, root_mapping)
        specification = Specification("name", "description", {"mapping": mapping_specification})
        databases = {self._url: "test_export_database.csv"}
        logger = MagicMock()
        self.assertTrue(
            do_work(specification, False, False, self._temp_dir.name, databases, {self._url: set()}, logger)
        )
        out_path = os.path.join(self._temp_dir.name, "test_export_database.csv")
        self.assertTrue(os.path.exists(out_path))
        with open(out_path) as input:
            csv_reader = reader(input)
            table = [row for row in csv_reader]
        expected = [["oc1", "o11"], ["oc1", "o12"], ["oc2", "o21"], ["oc2", "o22"], ["oc2", "o23"]]
        self.assertEqual(table, expected)


if __name__ == "__main__":
    unittest.main()
