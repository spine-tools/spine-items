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

"""Unit tests for export mapping setup table."""
import unittest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QUndoStack
from spinedb_api.mapping import Position
from spinedb_api.export_mapping import entity_export
from spine_items.exporter.mvcmodels.mapping_editor_table_model import MappingEditorTableModel


class TestMappingTableModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._undo_stack = QUndoStack()

    def test_columnCount(self):
        model = MappingEditorTableModel(
            "mapping", entity_export(Position.hidden, Position.hidden), self._undo_stack, MagicMock()
        )
        self.assertEqual(model.rowCount(), 2)

    def test_rowCount(self):
        mapping_root = entity_export(Position.hidden, Position.hidden)
        model = MappingEditorTableModel("mapping", mapping_root, self._undo_stack, MagicMock())
        self.assertEqual(model.rowCount(), mapping_root.count_mappings())

    def test_data(self):
        model = MappingEditorTableModel("mapping", entity_export(1, 2), self._undo_stack, MagicMock())
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.index(0, 0).data(), "Entity classes")
        self.assertEqual(model.index(0, 1).data(), "2")
        self.assertEqual(model.index(1, 0).data(), "Entities")
        self.assertEqual(model.index(1, 1).data(), "3")

    def test_setData_column_number(self):
        model = MappingEditorTableModel(
            "mapping", entity_export(Position.hidden, Position.hidden), self._undo_stack, MagicMock()
        )
        self.assertTrue(model.setData(model.index(0, 1), "23"))
        self.assertEqual(model.index(0, 1).data(), "23")

    def test_setData_prevents_duplicate_table_name_positions(self):
        model = MappingEditorTableModel("mapping", entity_export(Position.table_name, 0), self._undo_stack, MagicMock())
        self.assertEqual(model.rowCount(), 2)
        self.assertEqual(model.index(0, 0).data(), "Entity classes")
        self.assertEqual(model.index(0, 1).data(), "table name")
        self.assertEqual(model.index(1, 0).data(), "Entities")
        self.assertEqual(model.index(1, 1).data(), "1")
        model.setData(model.index(1, 1), "table name")
        self.assertEqual(model.index(0, 0).data(), "Entity classes")
        self.assertEqual(model.index(0, 1).data(), "1")
        self.assertEqual(model.index(1, 0).data(), "Entities")
        self.assertEqual(model.index(1, 1).data(), "table name")


if __name__ == "__main__":
    unittest.main()
