######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Unit tests for the ''specification'' module"""
import unittest
from spine_items.exporter.specification import MappingSpecification, MappingType, OutputFormat, Specification
from spinedb_api.export_mapping import entity_export
from spinedb_api.mapping import Position


class TestSpecification(unittest.TestCase):
    def test_is_exporting_multiple_files_is_false_when_exporting_single_file(self):
        mapping_root = entity_export(0, 1)
        mapping_specification = MappingSpecification(MappingType.entities, True, False, "", False, mapping_root)
        mapping_specifications = {"Only mapping": mapping_specification}
        specification = Specification(mapping_specifications=mapping_specifications, output_format=OutputFormat.CSV)
        self.assertFalse(specification.is_exporting_multiple_files())

    def test_is_exporting_multiple_files_is_false_when_exporting_csv_with_named_tables(self):
        mapping_root = entity_export(Position.table_name, 0)
        mapping_specification = MappingSpecification(MappingType.entities, True, False, "", False, mapping_root)
        mapping_specifications = {"Only mapping": mapping_specification}
        specification = Specification(mapping_specifications=mapping_specifications, output_format=OutputFormat.CSV)
        self.assertTrue(specification.is_exporting_multiple_files())


class TestOutputFormat(unittest.TestCase):
    def test_compatible_file_extensions(self):
        self.assertTrue(OutputFormat.CSV.is_compatible_file_extension("csv"))
        self.assertTrue(OutputFormat.CSV.is_compatible_file_extension("dat"))
        self.assertTrue(OutputFormat.CSV.is_compatible_file_extension("txt"))
        self.assertFalse(OutputFormat.CSV.is_compatible_file_extension("XXX"))
        self.assertTrue(OutputFormat.EXCEL.is_compatible_file_extension("xlsx"))
        self.assertFalse(OutputFormat.EXCEL.is_compatible_file_extension("XXX"))
        self.assertTrue(OutputFormat.GDX.is_compatible_file_extension("gdx"))
        self.assertFalse(OutputFormat.GDX.is_compatible_file_extension("XXX"))
        self.assertTrue(OutputFormat.SQL.is_compatible_file_extension("sqlite"))
        self.assertFalse(OutputFormat.SQL.is_compatible_file_extension("XXX"))

    def test_every_format_has_file_extensions(self):
        for output_format in OutputFormat:
            try:
                output_format.file_extension()
            except KeyError:
                self.fail(f"{output_format} is missing file extension")

    def test_output_format_from_extension(self):
        self.assertEqual(OutputFormat.output_format_from_extension("csv"), OutputFormat.CSV)
        self.assertEqual(OutputFormat.output_format_from_extension("dat"), OutputFormat.CSV)
        self.assertEqual(OutputFormat.output_format_from_extension("txt"), OutputFormat.CSV)
        self.assertEqual(OutputFormat.output_format_from_extension("gdx"), OutputFormat.GDX)
        self.assertEqual(OutputFormat.output_format_from_extension("sqlite"), OutputFormat.SQL)
        self.assertEqual(OutputFormat.output_format_from_extension("xlsx"), OutputFormat.EXCEL)
        self.assertIsNone(OutputFormat.output_format_from_extension("XXX"))

    def test_default_format(self):
        self.assertEqual(OutputFormat.default(), OutputFormat.CSV)


if __name__ == "__main__":
    unittest.main()
