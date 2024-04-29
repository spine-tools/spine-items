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

"""Unit tests for the custom_menus.py module."""
import unittest
from unittest import mock
import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QStandardItemModel, QStandardItem
from spine_items.tool.widgets.custom_menus import ToolSpecificationMenu
from spine_items.tool.tool_specifications import JuliaTool, ExecutableTool
from tests.mock_helpers import create_mock_toolbox_with_mock_qsettings, MockQSettings


class TestToolSpecificationMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.WARNING,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def setUp(self):
        """Overridden method. Runs before each test."""
        self.toolbox = create_mock_toolbox_with_mock_qsettings()
        self._temp_dir = TemporaryDirectory()

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self._temp_dir.cleanup()

    def test_open_main_program_file(self):
        spec = self.make_julia_tool_spec()
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        with mock.patch("spine_items.tool.widgets.custom_menus.open_url") as mock_open_url:
            menu._open_main_program_file()
            mock_open_url.assert_called()

    def test_open_main_program_file_fails_without_path(self):
        spec = self.make_julia_tool_spec()
        spec.path = None
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        with mock.patch("spine_items.tool.widgets.custom_menus.open_url") as mock_open_url:
            menu._open_main_program_file()
            mock_open_url.assert_not_called()

    def test_open_main_program_file_fails_without_path_and_includes(self):
        spec = self.make_julia_tool_spec()
        spec.path = None
        spec.includes = None
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        with mock.patch("spine_items.tool.widgets.custom_menus.open_url") as mock_open_url:
            menu._open_main_program_file()
            mock_open_url.assert_not_called()

    def test_open_main_program_file_fails_with_bat_file(self):
        spec = self.make_exec_tool_spec()
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        with mock.patch("spine_items.tool.widgets.custom_menus.open_url") as mock_open_url:
            menu._open_main_program_file()
            mock_open_url.assert_not_called()

    def test_open_main_program_dir(self):
        spec = self.make_julia_tool_spec()
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        menu._open_main_program_dir()

    def test_open_main_program_dir_fails_without_includes(self):
        spec = self.make_julia_tool_spec()
        spec.includes = None
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        menu._open_main_program_dir()

    def test_open_main_program_dir_fails_without_path(self):
        spec = self.make_julia_tool_spec()
        spec.path = None
        spec_model = CustomQStandardItemModel()
        spec_item = QStandardItem(spec.name)
        spec_item.setData(spec)
        spec_model.appendRow(spec_item)
        index = spec_model.index(0, 0)
        w = ParentWidget(spec_model)
        menu = ToolSpecificationMenu(w, index)
        menu._open_main_program_dir()

    def make_julia_tool_spec(self):
        script_dir = Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = "hello.jl"
        file_path = Path(script_dir, script_file_name)
        with open(file_path, "w") as script_file:
            script_file.writelines(["println('hello')\n"])
        mock_logger = mock.MagicMock()
        julia_tool_spec = JuliaTool(
            "test_julia_spec",
            "julia",
            str(script_dir),
            [script_file_name],
            MockQSettings(),
            mock_logger,
        )
        julia_tool_spec.init_execution_settings()  # Sets defaults
        return julia_tool_spec

    def make_exec_tool_spec(self):
        script_dir = Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = "batch.bat"
        file_path = Path(script_dir, script_file_name)
        with open(file_path, "w") as script_file:
            script_file.writelines(["dir\n"])
        mock_logger = mock.MagicMock()
        return ExecutableTool(
            "test_exec_spec",
            "executable",
            str(script_dir),
            [script_file_name],
            MockQSettings(),
            mock_logger,
        )


class CustomQStandardItemModel(QStandardItemModel):
    """Fake specification model."""

    def __init__(self):
        super().__init__()

    def specification(self, row):
        item = self.item(row, 0)
        return item.data()


class ParentWidget(QWidget):
    """Fake self._toolbox."""

    def __init__(self, spec_model):
        super().__init__()
        self.specification_model = spec_model
        self.msg_warning = MiniLogger()
        self.msg_error = MiniLogger()

    def open_anchor(self, url):
        """Fakes self._toolbox.open_anchor()"""
        return True


class MiniLogger:
    """Fakes calls to signal emits."""

    def emit(self, msg):
        return True
