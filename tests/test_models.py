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

"""Unit tests for the ``models`` module."""
from pathlib import Path
import unittest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from spine_engine.project_item.project_item_resource import file_resource, file_resource_in_pack
from spine_items.models import CheckableFileListModel


class TestCheckableFileListModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._model = CheckableFileListModel()

    def tearDown(self):
        self._model.deleteLater()

    def test_update(self):
        single_resource = file_resource("item name", str(Path.cwd() / "path" / "to" / "file"), "file label")
        pack_resource = file_resource_in_pack("item name", "pack label", str(Path.cwd() / "path" / "to" / "pack_file"))
        self._model.update([single_resource, pack_resource])
        self.assertEqual(self._model.rowCount(), 2)
        index = self._model.index(0, 0)
        self.assertEqual(index.data(), "file label")
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), str(Path.cwd() / "path" / "to" / "file"))
        self.assertEqual(self._model.rowCount(index), 0)
        index = self._model.index(1, 0)
        self.assertEqual(index.data(), "pack label")
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), None)
        self.assertEqual(self._model.rowCount(index), 1)
        index = self._model.index(0, 0, index)
        self.assertEqual(index.data(), str(Path.cwd() / "path" / "to" / "pack_file"))
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), str(Path.cwd() / "path" / "to" / "pack_file"))

    def test_replace_single_resource(self):
        single_resource = file_resource("item name", str(Path.cwd() / "path" / "to" / "file"), "file label")
        self._model.update([single_resource])
        new_resource = file_resource("other item", str(Path.cwd() / "path" / "to" / "another_file"), "new label")
        self._model.replace(single_resource, new_resource)
        self.assertEqual(self._model.rowCount(), 1)
        index = self._model.index(0, 0)
        self.assertEqual(index.data(), "new label")
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), str(Path.cwd() / "path" / "to" / "another_file"))
        self.assertEqual(self._model.rowCount(index), 0)

    def test_replace_pack_resource_file_path(self):
        pack_resource = file_resource_in_pack("item name", "pack label", str(Path.cwd() / "path" / "to" / "pack_file"))
        self._model.update([pack_resource])
        new_resource = file_resource_in_pack("item name", "pack label", str(Path.cwd() / "path" / "to" / "pack_file_2"))
        self._model.replace(pack_resource, new_resource)
        self.assertEqual(self._model.rowCount(), 1)
        index = self._model.index(0, 0)
        self.assertEqual(index.data(), "pack label")
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), None)
        self.assertEqual(self._model.rowCount(index), 1)
        index = self._model.index(0, 0, index)
        self.assertEqual(index.data(), str(Path.cwd() / "path" / "to" / "pack_file_2"))
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), str(Path.cwd() / "path" / "to" / "pack_file_2"))

    def test_replace_pack_resource_with_completely_new_one(self):
        pack_resource = file_resource_in_pack("item name", "pack label", str(Path.cwd() / "path" / "to" / "pack_file"))
        self._model.update([pack_resource])
        new_resource = file_resource_in_pack(
            "another item", "new pack label", str(Path.cwd() / "path" / "to" / "pack_file_2")
        )
        self._model.replace(pack_resource, new_resource)
        self.assertEqual(self._model.rowCount(), 1)
        index = self._model.index(0, 0)
        self.assertEqual(index.data(), "new pack label")
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), None)
        self.assertEqual(self._model.rowCount(index), 1)
        index = self._model.index(0, 0, index)
        self.assertEqual(index.data(), str(Path.cwd() / "path" / "to" / "pack_file_2"))
        self.assertEqual(index.data(Qt.ItemDataRole.ToolTipRole), str(Path.cwd() / "path" / "to" / "pack_file_2"))


if __name__ == "__main__":
    unittest.main()
