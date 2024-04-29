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

"""Contains unit tests for Import editor's :class:`MappingsModel`."""
import unittest
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QUndoStack
from spine_items.importer.mvcmodels.mappings_model_roles import Role
from spine_items.importer.mvcmodels.mappings_model import MappingsModel
from spinetoolbox.helpers import signal_waiter
from spinedb_api import import_mapping_from_dict


class TestMappingsModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._model_parent = QObject()
        self._undo_stack = QUndoStack(self._model_parent)

    def tearDown(self):
        self._model_parent.deleteLater()
        QApplication.processEvents()

    def test_empty_model_has_Select_All_item(self):
        model = MappingsModel(self._undo_stack, self._model_parent)
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.columnCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "Select all")

    def test_set_time_series_repeat_flag(self):
        model = MappingsModel(self._undo_stack, self._model_parent)
        model.add_empty_row()
        table_index = model.index(1, 0)
        with signal_waiter(model.dataChanged) as waiter:
            self.assertTrue(model.setData(table_index, "table"))
            waiter.wait()
        self.assertTrue(model.insertRow(0, table_index))
        list_index = model.index(0, 0, table_index)
        model.set_root_mapping(
            table_index.row(), list_index.row(), import_mapping_from_dict({"map_type": "ObjectClass"})
        )
        model.set_parameter_type(table_index.row(), list_index.row(), "Value")
        model.set_value_type(table_index.row(), list_index.row(), "Time series")
        flattened_mappings = model.data(list_index, Role.FLATTENED_MAPPINGS)
        self.assertNotIn("repeat", flattened_mappings.value_mapping().options)
        with signal_waiter(model.dataChanged) as waiter:
            model.set_time_series_repeat_flag(table_index.row(), list_index.row(), True)
            waiter.wait()
        self.assertTrue(flattened_mappings.value_mapping().options["repeat"])

    def test_change_mappings_type(self):
        model = MappingsModel(self._undo_stack, self._model_parent)
        model.restore(
            {
                "table_mappings": {
                    "Sheet1": [
                        {
                            "Mapping 1": {
                                "mapping": [
                                    {"map_type": "EntityClass", "position": "hidden", "value": "Object"},
                                    {"map_type": "Entity", "position": 0},
                                    {"map_type": "EntityMetadata", "position": "hidden"},
                                    {"map_type": "ParameterDefinition", "position": "hidden", "value": "size"},
                                    {"map_type": "Alternative", "position": "hidden", "value": "Base"},
                                    {"map_type": "ParameterValueMetadata", "position": "hidden"},
                                    {"map_type": "ParameterValue", "position": 1},
                                ]
                            }
                        }
                    ]
                },
                "selected_tables": ["Sheet1"],
                "table_options": {"Sheet1": {}},
                "table_types": {"Sheet1": {"0": "string", "1": "float"}},
                "table_default_column_type": {},
                "table_row_types": {},
                "source_type": "ExcelConnector",
            }
        )
        self.assertEqual(model.index(0, 0).data(), "Select all")
        table_index = model.index(1, 0)
        self.assertEqual(table_index.data(), "Sheet1")
        list_index = model.index(0, 0, table_index)
        self.assertEqual(list_index.data(), "Mapping 1")
        expected = [
            ["Entity class names", "Constant", "Object", ""],
            ["Entity names", "Column", 1, ""],
            ["Entity metadata", "None", None, ""],
            ["Parameter names", "Constant", "size", ""],
            ["Alternative names", "Constant", "Base", ""],
            ["Parameter value metadata", "None", None, ""],
            ["Parameter values", "Column", 2, ""],
        ]
        rows = model.rowCount(list_index)
        self.assertEqual(rows, len(expected))
        for row in range(model.rowCount(list_index)):
            expected_row = expected[row]
            columns = model.columnCount(list_index)
            self.assertEqual(columns, len(expected_row))
            for column in range(columns):
                with self.subTest(row=row, column=column):
                    index = model.index(row, column, list_index)
                    self.assertEqual(index.data(), expected_row[column])
        model.set_mappings_type(1, 0, "Entity group")
        expected = [
            ["Entity class names", "None", None, ""],
            ["Group names", "None", None, ""],
            ["Member names", "None", None, ""],
        ]
        rows = model.rowCount(list_index)
        self.assertEqual(rows, len(expected))
        for row in range(model.rowCount(list_index)):
            expected_row = expected[row]
            columns = model.columnCount(list_index)
            self.assertEqual(columns, len(expected_row))
            for column in range(columns):
                with self.subTest(row=row, column=column):
                    index = model.index(row, column, list_index)
                    self.assertEqual(index.data(), expected_row[column])


class TestTableList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._model_parent = QObject()
        self._undo_stack = QUndoStack(self._model_parent)
        self._model = MappingsModel(self._undo_stack, self._model_parent)

    def tearDown(self):
        self._model_parent.deleteLater()
        QApplication.processEvents()

    def test_set_tables_editable(self):
        self._model.add_empty_row()
        table_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged) as waiter:
            self.assertTrue(self._model.setData(table_index, "table"))
            waiter.wait()
        self.assertEqual(self._model.rowCount(), 3)
        self.assertEqual(int((self._model.flags(self._model.index(0, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)
        self.assertNotEqual(int((self._model.flags(self._model.index(1, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)
        self.assertNotEqual(int((self._model.flags(self._model.index(2, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)
        self._model.set_tables_editable(False)
        self.assertEqual(int((self._model.flags(self._model.index(0, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)
        self.assertEqual(int((self._model.flags(self._model.index(1, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)
        self.assertNotEqual(int((self._model.flags(self._model.index(2, 0)) & Qt.ItemFlag.ItemIsEditable).value), 0)

    def test_set_source_table_items_into_specification(self):
        self._model.append_new_table_with_mapping("my source table", None)
        self.assertEqual(self._model.rowCount(), 2)
        for row in range(1, self._model.rowCount()):
            item = self._model.index(row, 0).data(Role.ITEM)
            self.assertFalse(item.in_specification)
        self._model.set_source_table_items_into_specification()
        for row in range(1, self._model.rowCount()):
            item = self._model.index(row, 0).data(Role.ITEM)
            self.assertTrue(item.in_specification)

    def test_remove_tables_not_in_source_and_specification(self):
        self._model.append_new_table_with_mapping("table that gets removed", None)
        self._model.append_new_table_with_mapping("table that is only in source", None)
        root_mapping = import_mapping_from_dict({"map_type": "ObjectClass", "name": None, "object": None})
        self._model.append_new_table_with_mapping("table that is in source and specification", root_mapping)
        self.assertEqual(self._model.rowCount(), 4)
        self._model.cross_check_source_table_names(
            {"table that is only in source", "table that is in source and specification"}
        )
        self._model.remove_tables_not_in_source_and_specification()
        self.assertEqual(self._model.rowCount(), 3)
        expected_names = ["Select all", "table that is only in source", "table that is in source and specification"]
        for row, expected_name in zip(range(self._model.rowCount()), expected_names):
            item = self._model.index(row, 0).data(Role.ITEM)
            self.assertEqual(item.name, expected_name)

    def test_cross_check_source_table_names(self):
        self._model.append_new_table_with_mapping("initially in source", None)
        self._model.append_new_table_with_mapping("initially not in source", None)
        not_in_source_item = self._model.index(self._model.rowCount() - 1, 0).data(Role.ITEM)
        self.assertEqual(not_in_source_item.name, "initially not in source")
        not_in_source_item.in_source = False
        self._model.cross_check_source_table_names({"initially not in source"})
        self.assertEqual(self._model.rowCount(), 3)
        expected_in_source = {"initially in source": False, "initially not in source": True}
        expected_real = {"initially in source": False, "initially not in source": True}
        for row in range(1, self._model.rowCount()):
            item = self._model.index(row, 0).data(Role.ITEM)
            self.assertEqual(item.in_source, expected_in_source[item.name])
            self.assertEqual(item.real, expected_real[item.name])

    def test_empty_model_has_select_all_source_table_item(self):
        self.assertEqual(self._model.rowCount(), 1)
        index = self._model.index(0, 0)
        self.assertEqual(index.data(), "Select all")
        self.assertIsNone(index.data(Qt.ItemDataRole.ForegroundRole))
        self.assertEqual(index.data(Qt.ItemDataRole.CheckStateRole), Qt.CheckState.Checked)
        self.assertIsNone(index.data(Qt.ItemDataRole.FontRole))
        self.assertIsNone(index.data(Qt.ItemDataRole.ToolTipRole))
        flags = self._model.flags(index)
        self.assertEqual(flags, Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)

    def test_empty_row(self):
        self._model.add_empty_row()
        self.assertEqual(self._model.rowCount(), 2)
        index = self._model.index(1, 0)
        self._assert_empty_row(index)

    def test_turn_empty_row_into_non_real_table(self):
        self._model.add_empty_row()
        empty_row_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged, timeout=1.0) as waiter:
            self._model.setData(empty_row_index, "my shiny table")
            waiter.wait()
            self.assertEqual(len(waiter.args), 3)
            self.assertTrue(self._model.is_table_index(waiter.args[0]))
            self.assertEqual(waiter.args[0].row(), 1)
            self.assertEqual(waiter.args[0].column(), 0)
            self.assertTrue(self._model.is_table_index(waiter.args[1]))
            self.assertEqual(waiter.args[1].row(), 1)
            self.assertEqual(waiter.args[1].column(), 0)
        self.assertEqual(self._model.rowCount(), 3)
        index = self._model.index(1, 0)
        self.assertEqual(index.data(), "my shiny table (new)")
        self.assertIsNone(index.data(Qt.ItemDataRole.ForegroundRole))
        self.assertEqual(index.data(Qt.ItemDataRole.CheckStateRole), Qt.CheckState.Checked)
        self.assertIsNone(index.data(Qt.ItemDataRole.FontRole))
        self.assertEqual(
            index.data(Qt.ItemDataRole.ToolTipRole),
            "<qt>Table's mappings haven't been saved with the specification yet.</qt>",
        )
        flags = self._model.flags(index)
        self.assertEqual(
            flags,
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsUserCheckable,
        )
        index = self._model.index(2, 0)
        self._assert_empty_row(index)

    def test_when_empty_row_turns_into_non_real_table_its_check_status_equals_select_all(self):
        self._model.add_empty_row()
        index = self._model.index(0, 0)
        self.assertTrue(self._model.setData(index, Qt.CheckState.Unchecked.value, Qt.ItemDataRole.CheckStateRole))
        empty_row_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged, timeout=1.0) as waiter:
            self._model.setData(empty_row_index, "my shiny table")
            waiter.wait()
        self.assertEqual(self._model.rowCount(), 3)
        index = self._model.index(1, 0)
        self.assertEqual(index.data(), "my shiny table (new)")
        self.assertEqual(index.data(Qt.ItemDataRole.CheckStateRole), Qt.CheckState.Unchecked)
        index = self._model.index(2, 0)
        self._assert_empty_row(index)

    def _assert_empty_row(self, index):
        self.assertEqual(index.data(), "<rename this to add table>")
        self.assertEqual(index.data(Qt.ItemDataRole.CheckStateRole), Qt.CheckState.Unchecked)
        self.assertIsNone(index.data(Qt.ItemDataRole.ForegroundRole))
        self.assertTrue(index.data(Qt.ItemDataRole.FontRole).italic())
        flags = self._model.flags(index)
        self.assertEqual(flags, Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)

    def test_undo_create_new_table_restores_empty_row(self):
        self._model.add_empty_row()
        empty_row_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged, timeout=1.0) as waiter:
            self._model.setData(empty_row_index, "my temporary table")
            waiter.wait()
        self.assertEqual(self._model.rowCount(), 3)
        with signal_waiter(self._model.dataChanged, timeout=1.0) as waiter:
            self._undo_stack.undo()
            waiter.wait()
        self.assertEqual(self._model.rowCount(), 2)
        index = self._model.index(1, 0)
        self._assert_empty_row(index)


class TestMappingComponentsTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._model_parent = QObject()
        self._undo_stack = QUndoStack(self._model_parent)
        self._model = MappingsModel(self._undo_stack, self._model_parent)
        self._model.add_empty_row()
        self._table_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged) as waiter:
            self.assertTrue(self._model.setData(self._table_index, "table"))
            waiter.wait()
        self.assertTrue(self._model.insertRow(0, self._table_index))
        self._list_index = self._model.index(0, 0, self._table_index)

    def tearDown(self):
        self._model_parent.deleteLater()
        QApplication.processEvents()

    def test_data_when_mapping_object_class_without_objects_or_parameters(self):
        root_mapping = import_mapping_from_dict({"map_type": "ObjectClass", "name": None, "object": None})
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), root_mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 3)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Entity names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        self.assertEqual(self._model.index(0, 3, self._list_index).data(), "")
        self.assertEqual(self._model.index(1, 3, self._list_index).data(), "")
        self.assertEqual(self._model.index(2, 3, self._list_index).data(), "")

    def test_data_when_mapping_invalid_object_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {"map_type": None},
            "parameter_type": "map",
            "value": {"map_type": None},
            "extra_dimensions": [{"map_type": None}],
        }
        mapping_dict = {
            "map_type": "ObjectClass",
            "name": None,
            "objects": None,
            "parameters": indexed_parameter_mapping_dict,
        }
        self._model.set_root_mapping(
            self._table_index.row(), self._list_index.row(), import_mapping_from_dict(mapping_dict)
        )
        self.assertEqual(self._model.rowCount(self._list_index), 9)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Entity names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes")
        index = self._model.index(8, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        for row in range(9):
            index = self._model.index(row, 1, self._list_index)
            self.assertEqual(index.data(), "None")
            index = self._model.index(row, 2, self._list_index)
            self.assertEqual(index.data(), None)
            self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_valid_object_class_with_pivoted_parameters(self):
        array_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": 2,
            "parameter_type": "array",
            "value": {"map_type": "row", "reference": 0},
        }
        mapping_dict = {"map_type": "ObjectClass", "name": 0, "objects": 1, "parameters": array_parameter_mapping_dict}
        self._model.set_root_mapping(
            self._table_index.row(), self._list_index.row(), import_mapping_from_dict(mapping_dict)
        )
        self.assertEqual(self._model.rowCount(self._list_index), 8)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Entity names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(3, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(4, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(5, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(6, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(7, 1, self._list_index)
        self.assertEqual(index.data(), "Pivoted")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), 0 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), 1 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 2 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), "Pivoted values")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        for row in range(8):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_valid_object_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {"map_type": "column", "reference": 99},
            "parameter_type": "map",
            "value": {"reference": 23, "map_type": "column"},
            "extra_dimensions": [{"reference": "fifth column", "map_type": "column"}],
        }
        mapping_dict = {
            "map_type": "ObjectClass",
            "parameters": indexed_parameter_mapping_dict,
            "name": {"reference": "class_name", "map_type": "constant"},
            "objects": {"reference": "object_name", "map_type": "constant"},
        }
        mapping = import_mapping_from_dict(mapping_dict)
        table_name = "source table"
        header = ["1", "2", "3", "4", "fifth column"]
        mapping.polish(table_name, header)
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 9)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Entity names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes")
        index = self._model.index(8, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(3, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(4, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(5, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(6, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(7, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(8, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), "class_name")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), "object_name")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        for row in range(9):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_valid_object_class_with_nested_map(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {"map_type": "column", "reference": 99},
            "parameter_type": "map",
            "value": {"reference": 23, "map_type": "column"},
            "extra_dimensions": [
                {"reference": "fifth column", "map_type": "column"},
                {"reference": "sixth column", "map_type": "column"},
            ],
        }
        mapping_dict = {
            "map_type": "ObjectClass",
            "parameters": indexed_parameter_mapping_dict,
            "name": {"reference": "class_name", "map_type": "constant"},
            "objects": {"reference": "object_name", "map_type": "constant"},
        }
        mapping = import_mapping_from_dict(mapping_dict)
        table_name = "source table"
        header = ["1", "2", "3", "4", "fifth column", "sixth column"]
        mapping.polish(table_name, header)
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 11)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Entity names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names 1")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes 1")
        index = self._model.index(8, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names 2")
        index = self._model.index(9, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes 2")
        index = self._model.index(10, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(3, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(4, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(5, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(6, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(7, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(8, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(9, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(10, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), "class_name")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), "object_name")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(9, 2, self._list_index)
        self.assertEqual(index.data(), 6)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(10, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        for row in range(11):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_relationship_class_without_objects_or_parameters(self):
        mapping = import_mapping_from_dict(
            {"map_type": "RelationshipClass", "name": None, "object_classes": None, "object": None}
        )
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 4)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Dimension names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Element names")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        for row in range(4):
            index = self._model.index(row, 1, self._list_index)
            self.assertEqual(index.data(), "None")
            index = self._model.index(row, 2, self._list_index)
            self.assertEqual(index.data(), None)
            self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_invalid_relationship_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {"map_type": None},
            "parameter_type": "map",
            "value": {"map_type": None},
            "extra_dimensions": [{"map_type": None}],
        }
        mapping_dict = {
            "map_type": "RelationshipClass",
            "name": None,
            "object_classes": None,
            "object": None,
            "parameters": indexed_parameter_mapping_dict,
        }
        self._model.set_root_mapping(
            self._table_index.row(), self._list_index.row(), import_mapping_from_dict(mapping_dict)
        )
        self.assertEqual(self._model.rowCount(self._list_index), 10)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Dimension names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Element names")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names")
        index = self._model.index(8, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes")
        index = self._model.index(9, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        for row in range(9):
            index = self._model.index(row, 1, self._list_index)
            self.assertEqual(index.data(), "None")
            index = self._model.index(row, 2, self._list_index)
            self.assertEqual(index.data(), None)
            self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_multidimensional_relationship_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {"map_type": "column", "reference": 99},
            "parameter_type": "map",
            "value": {"reference": 23, "map_type": "column"},
            "extra_dimensions": [{"reference": "fifth column", "map_type": "column"}],
        }
        mapping_dict = {
            "map_type": "RelationshipClass",
            "name": {"map_type": "constant", "reference": "relationship_class name"},
            "object_classes": [
                {"map_type": "column", "reference": "column header"},
                {"map_type": "constant", "reference": "second class"},
            ],
            "objects": [{"map_type": "column", "reference": 21}, {"map_type": "column", "reference": 22}],
            "parameters": indexed_parameter_mapping_dict,
        }
        mapping = import_mapping_from_dict(mapping_dict)
        table_name = "source table"
        header = ["column header", "2", "3", "4", "fifth column", "sixth column"]
        mapping.polish(table_name, header)
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 12)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Entity class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Dimension names 1")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Dimension names 2")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Element names 1")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Element names 2")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Entity metadata")
        index = self._model.index(6, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter names")
        index = self._model.index(7, 0, self._list_index)
        self.assertEqual(index.data(), "Alternative names")
        index = self._model.index(8, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter value metadata")
        index = self._model.index(9, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter index names")
        index = self._model.index(10, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter indexes")
        index = self._model.index(11, 0, self._list_index)
        self.assertEqual(index.data(), "Parameter values")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "Constant")
        index = self._model.index(3, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(4, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(5, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(6, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(7, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(8, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(9, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(10, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(11, 1, self._list_index)
        self.assertEqual(index.data(), "Column")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), "relationship_class name")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), "second class")
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 21 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), 22 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(9, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(10, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        index = self._model.index(11, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.ItemDataRole.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ItemDataRole.ToolTipRole))
        for row in range(12):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_object_class_with_regular_expression(self):
        root_mapping = import_mapping_from_dict({"map_type": "ObjectClass", "name": None, "object": None})
        root_mapping.filter_re = "starred"
        root_mapping.child.child.filter_re = "choose_me"
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), root_mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 3)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        self.assertEqual(self._model.index(0, 3, self._list_index).data(), "starred")
        self.assertEqual(self._model.index(1, 3, self._list_index).data(), "")
        self.assertEqual(self._model.index(2, 3, self._list_index).data(), "choose_me")


if __name__ == "__main__":
    unittest.main()
