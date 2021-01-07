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
Unit tests for :class:`RenameTableModel`.

:author: A. Soininen (VTT)
:date:   7.1.2021
"""
import unittest
from PySide2.QtCore import Qt
from spine_items.data_transformer.mvcmodels.rename_table_model import RenameTableModel


class TestRenameTableModel(unittest.TestCase):
    def test_columnCount_always_two(self):
        model = RenameTableModel({})
        self.assertEqual(model.columnCount(), 2)

    def test_rowCount(self):
        model = RenameTableModel({})
        self.assertEqual(model.rowCount(), 0)
        model = RenameTableModel({"a": "A", "b": "B"})
        self.assertEqual(model.rowCount(), 2)

    def test_data(self):
        model = RenameTableModel({"a": "A", "b": "b"})
        self.assertEqual(model.index(0, 0).data(), "a")
        self.assertIsNone(model.index(0, 0).data(Qt.FontRole))
        self.assertEqual(model.index(0, 1).data(), "A")
        self.assertTrue(model.index(0, 1).data(Qt.FontRole).bold())
        self.assertEqual(model.index(1, 0).data(), "b")
        self.assertIsNone(model.index(1, 0).data(Qt.FontRole))
        self.assertEqual(model.index(1, 1).data(), "b")
        self.assertIsNone(model.index(1, 1).data(Qt.FontRole))

    def test_second_column_only_is_editable(self):
        model = RenameTableModel({"a": "A"})
        self.assertFalse(model.index(0, 0).flags() & Qt.ItemIsEditable)
        self.assertTrue(model.index(0, 1).flags() & Qt.ItemIsEditable)

    def test_headers(self):
        model = RenameTableModel({"a": "A"})
        self.assertIsNone(model.headerData(0, Qt.Vertical))
        self.assertEqual(model.headerData(0, Qt.Horizontal), "Original")
        self.assertEqual(model.headerData(1, Qt.Horizontal), "Renamed")

    def test_renaming_settings(self):
        model = RenameTableModel({"a": "A", "b": "b", "c": ""})
        self.assertEqual(model.renaming_settings(), {"a": "A", "b": "b"})

    def test_reset_originals(self):
        model = RenameTableModel({"a": "A", "b": "B", "c": "c", "d": "d"})
        model.reset_originals({"a", "c", "e"})
        self.assertEqual(model.renaming_settings(), {"a": "A", "c": "c", "e": "e"})

    def test_setData(self):
        model = RenameTableModel({"a": "A"})
        self.assertTrue(model.setData(model.index(0, 1), "B"))
        self.assertEqual(model.renaming_settings(), {"a": "B"})


if __name__ == '__main__':
    unittest.main()
