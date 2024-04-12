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

"""Unit tests for :class:`ClassRenamesTableModel`."""
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoStack
from spine_items.data_transformer.mvcmodels.class_renames_table_model import ClassRenamesTableModel


class TestClassRenamesTableModel(unittest.TestCase):
    def setUp(self):
        self._undo_stack = QUndoStack()

    def tearDown(self):
        self._undo_stack.deleteLater()

    def test_columnCount_always_two(self):
        model = ClassRenamesTableModel(self._undo_stack, {})
        self.assertEqual(model.columnCount(), 2)

    def test_rowCount(self):
        model = ClassRenamesTableModel(self._undo_stack, {})
        self.assertEqual(model.rowCount(), 0)
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A", "b": "B"})
        self.assertEqual(model.rowCount(), 2)

    def test_data(self):
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A", "b": "b"})
        self.assertEqual(model.index(0, 0).data(), "a")
        self.assertEqual(model.index(0, 1).data(), "A")
        self.assertEqual(model.index(1, 0).data(), "b")
        self.assertEqual(model.index(1, 1).data(), "b")

    def test_both_columns_are_editable(self):
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A"})
        self.assertTrue(model.index(0, 0).flags() & Qt.ItemIsEditable)
        self.assertTrue(model.index(0, 1).flags() & Qt.ItemIsEditable)

    def test_headers(self):
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A"})
        self.assertIsNone(model.headerData(0, Qt.Orientation.Vertical))
        self.assertEqual(model.headerData(0, Qt.Orientation.Horizontal), "Original")
        self.assertEqual(model.headerData(1, Qt.Orientation.Horizontal), "Renamed")

    def test_renaming_settings(self):
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A", "b": "b", "c": ""})
        self.assertEqual(model.renaming_settings(), {"a": "A", "b": "b", "c": ""})

    def test_setData(self):
        model = ClassRenamesTableModel(self._undo_stack, {"a": "A"})
        self.assertTrue(model.setData(model.index(0, 1), "B"))
        self.assertEqual(model.renaming_settings(), {"a": "B"})


if __name__ == "__main__":
    unittest.main()
