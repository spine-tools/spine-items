######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Helper functions for Importer's unit tests."""


def append_mapping(test_case, mappings_model, name, table_index):
    row_count = mappings_model.rowCount(table_index)
    test_case.assertTrue(mappings_model.insertRow(row_count, table_index))
    test_case.assertEqual(mappings_model.rowCount(table_index), row_count + 1)
    mappings_model.rename_mapping(table_index.row(), row_count, name)
    test_case.assertEqual(mappings_model.index(row_count, 0, table_index).data(), name)


def append_source_table_with_mappings(
    test_case, mappings_model, table_name, first_mapping_name, additional_mapping_names
):
    original_row_count = mappings_model.rowCount()
    root_mapping = mappings_model.create_default_mapping()
    mappings_model.append_new_table_with_mapping(table_name, root_mapping)
    test_case.assertEqual(mappings_model.rowCount(), original_row_count + 1)
    table_row = original_row_count - (1 if mappings_model.has_empty_source_table_row() else 0)
    table_index = mappings_model.index(table_row, 0)
    test_case.assertEqual(table_index.data(), table_name)
    test_case.assertEqual(mappings_model.rowCount(table_index), 1)
    mappings_model.rename_mapping(table_row, 0, first_mapping_name)
    test_case.assertEqual(mappings_model.index(0, 0, table_index).data(), first_mapping_name)
    for name in additional_mapping_names:
        append_mapping(test_case, mappings_model, name, table_index)
    return table_index
