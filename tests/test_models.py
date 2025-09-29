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
from spine_engine.project_item.project_item_resource import CmdLineArg, file_resource, file_resource_in_pack
from spine_items.models import CheckableFileListModel, ToolCommandLineArgsModel
from spinetoolbox.mvcmodels.file_list_models import NewCommandLineArgItem
from tests.mock_helpers import q_object


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


_EMPTY_LINE_TEXT = "Type arg, or drag and drop from Available resources..."


class TestToolCommandLineArgsModel:
    def test_empty_model(self, application):
        with q_object(ToolCommandLineArgsModel()) as model:
            assert model.rowCount() == 2
            assert model.columnCount() == 1
            assert model.headerData(0, Qt.Orientation.Horizontal) == "Command line arguments"
            specification_args_root = model.item(0, 0)
            assert specification_args_root.rowCount() == 0
            assert model.data(specification_args_root.index()) == "Specification arguments"
            tool_args_root = model.item(1, 0)
            assert tool_args_root.rowCount() == 1
            assert model.data(tool_args_root.index()) == "Tool arguments"
            empty_item = tool_args_root.child(0, 0)
            assert (
                model.data(empty_item.index(), Qt.ItemDataRole.ForegroundRole)
                == NewCommandLineArgItem.text_color_hint()
            )
            assert model.data(empty_item.index(), Qt.ItemDataRole.FontRole) is None
            assert empty_item.flags() & Qt.ItemFlag.ItemIsDropEnabled == Qt.ItemFlag.NoItemFlags
            assert empty_item.flags() & Qt.ItemFlag.ItemIsEditable != Qt.ItemFlag.NoItemFlags
            assert empty_item.rowCount() == 0

    def test_reset_model_with_non_label_arg(self, application):
        with q_object(ToolCommandLineArgsModel()) as model:
            specification_args = [CmdLineArg("--version")]
            tool_args = [CmdLineArg("--dry-run")]
            model.reset_model(specification_args, tool_args)
            assert model.rowCount() == 2
            specification_arg_root = model.item(0, 0)
            assert specification_arg_root.rowCount() == 1
            specification_arg_item = specification_arg_root.child(0, 0)
            assert model.data(specification_arg_item.index()) == "--version"
            assert model.data(specification_arg_item.index(), Qt.ItemDataRole.ForegroundRole) is None
            assert (
                model.data(specification_arg_item.index(), Qt.ItemDataRole.FontRole)
                == ToolCommandLineArgsModel.non_label_arg_font()
            )
            assert specification_arg_item.flags() & Qt.ItemFlag.ItemIsDropEnabled == Qt.ItemFlag.NoItemFlags
            assert specification_arg_item.flags() & Qt.ItemFlag.ItemIsEditable != Qt.ItemFlag.NoItemFlags
            assert specification_arg_item.rowCount() == 0
            tool_arg_root = model.item(1, 0)
            assert tool_arg_root.rowCount() == 2
            tool_arg_item = tool_arg_root.child(0, 0)
            assert model.data(tool_arg_item.index()) == "--dry-run"
            assert model.data(tool_arg_item.index(), Qt.ItemDataRole.ForegroundRole) is None
            assert (
                model.data(tool_arg_item.index(), Qt.ItemDataRole.FontRole)
                == ToolCommandLineArgsModel.non_label_arg_font()
            )
            assert tool_arg_item.flags() & Qt.ItemFlag.ItemIsDropEnabled == Qt.ItemFlag.NoItemFlags
            assert tool_arg_item.flags() & Qt.ItemFlag.ItemIsEditable != Qt.ItemFlag.NoItemFlags
            assert tool_arg_item.rowCount() == 0
            empty_item = tool_arg_root.child(1, 0)
            assert model.data(empty_item.index()) == _EMPTY_LINE_TEXT
            assert empty_item.rowCount() == 0
