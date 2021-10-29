######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains unit tests for Import editor's :class:`MappingsModel`.
"""
import unittest
from PySide2.QtCore import QObject, Qt
from PySide2.QtWidgets import QApplication, QUndoStack
from spinetoolbox.helpers import signal_waiter
from spine_items.importer.mvcmodels.mappings_model import MappingsModel
from spinedb_api import import_mapping_from_dict


class TestMappingsModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._undo_stack = QUndoStack()
        self._model_parent = QObject()

    def tearDown(self):
        self._undo_stack.deleteLater()
        self._model_parent.deleteLater()
        QApplication.processEvents()

    def test_empty_model_has_Select_All_item(self):
        model = MappingsModel(self._undo_stack, self._model_parent)
        self.assertEqual(model.rowCount(), 1)
        self.assertEqual(model.columnCount(), 1)
        index = model.index(0, 0)
        self.assertEqual(index.data(), "Select All")


class TestMappingComponentsTable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._undo_stack = QUndoStack()
        self._model_parent = QObject()
        self._model = MappingsModel(self._undo_stack, self._model_parent)
        self._model.add_empty_row()
        self._table_index = self._model.index(1, 0)
        with signal_waiter(self._model.dataChanged) as waiter:
            self.assertTrue(self._model.setData(self._table_index, "table"))
            waiter.wait()
        self.assertTrue(self._model.insertRow(0, self._table_index))
        self._list_index = self._model.index(0, 0, self._table_index)

    def tearDown(self):
        self._undo_stack.deleteLater()
        self._model_parent.deleteLater()
        QApplication.processEvents()

    def test_data_when_mapping_object_class_without_objects_or_parameters(self):
        root_mapping = import_mapping_from_dict({"map_type": "ObjectClass", "name": None, "object": None})
        self._model.set_root_mapping(self._table_index.row(), self._list_index.row(), root_mapping)
        self.assertEqual(self._model.rowCount(self._list_index), 3)
        self.assertEqual(self._model.columnCount(self._list_index), 4)
        index = self._model.index(0, 0, self._list_index)
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object metadata")
        index = self._model.index(0, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(1, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(2, 1, self._list_index)
        self.assertEqual(index.data(), "None")
        index = self._model.index(0, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        self.assertEqual(self._model.index(0, 3, self._list_index).data(), "")
        self.assertEqual(self._model.index(1, 3, self._list_index).data(), "")
        self.assertEqual(self._model.index(2, 3, self._list_index).data(), "")

    def test_data_when_mapping_invalid_object_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {'map_type': None},
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
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object metadata")
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
            self.assertEqual(index.data(Qt.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ToolTipRole))
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
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object metadata")
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
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), 1 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 2 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), "Pivoted values")
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        for row in range(8):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_valid_object_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {'map_type': 'column', 'reference': 99},
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
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object metadata")
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
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), "object_name")
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        for row in range(9):
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_valid_object_class_with_nested_map(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {'map_type': 'column', 'reference': 99},
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
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object metadata")
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
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), "object_name")
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(9, 2, self._list_index)
        self.assertEqual(index.data(), 6)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(10, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
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
        self.assertEqual(index.data(), "Relationship class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Relationship metadata")
        for row in range(4):
            index = self._model.index(row, 1, self._list_index)
            self.assertEqual(index.data(), "None")
            index = self._model.index(row, 2, self._list_index)
            self.assertEqual(index.data(), None)
            self.assertEqual(index.data(Qt.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ToolTipRole))
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_invalid_relationship_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {'map_type': None},
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
        self.assertEqual(index.data(), "Relationship class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object class names")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object names")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Relationship metadata")
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
            self.assertEqual(index.data(Qt.BackgroundRole), None)
            self.assertFalse(index.data(Qt.ToolTipRole))
            self.assertEqual(self._model.index(row, 3, self._list_index).data(), "")

    def test_data_when_mapping_multidimensional_relationship_class_with_parameters(self):
        indexed_parameter_mapping_dict = {
            "map_type": "parameter",
            "name": {'map_type': 'column', 'reference': 99},
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
        self.assertEqual(index.data(), "Relationship class names")
        index = self._model.index(1, 0, self._list_index)
        self.assertEqual(index.data(), "Object class names 1")
        index = self._model.index(2, 0, self._list_index)
        self.assertEqual(index.data(), "Object class names 2")
        index = self._model.index(3, 0, self._list_index)
        self.assertEqual(index.data(), "Object names 1")
        index = self._model.index(4, 0, self._list_index)
        self.assertEqual(index.data(), "Object names 2")
        index = self._model.index(5, 0, self._list_index)
        self.assertEqual(index.data(), "Relationship metadata")
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
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(1, 2, self._list_index)
        self.assertEqual(index.data(), 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(2, 2, self._list_index)
        self.assertEqual(index.data(), "second class")
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(3, 2, self._list_index)
        self.assertEqual(index.data(), 21 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(4, 2, self._list_index)
        self.assertEqual(index.data(), 22 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(5, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(6, 2, self._list_index)
        self.assertEqual(index.data(), 99 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(7, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(8, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(9, 2, self._list_index)
        self.assertEqual(index.data(), None)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(10, 2, self._list_index)
        self.assertEqual(index.data(), 5)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
        index = self._model.index(11, 2, self._list_index)
        self.assertEqual(index.data(), 23 + 1)
        self.assertEqual(index.data(Qt.BackgroundRole), None)
        self.assertFalse(index.data(Qt.ToolTipRole))
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


if __name__ == '__main__':
    unittest.main()
