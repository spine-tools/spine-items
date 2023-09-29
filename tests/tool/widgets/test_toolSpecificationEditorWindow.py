######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Unit tests for ToolSpecificationEditorWindow class."""

import unittest
import logging
import sys
from unittest import mock
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from spine_items.tool.tool_specifications import JuliaTool, ExecutableTool
from spine_items.tool.widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from spine_items.tool.widgets.tool_spec_optional_widgets import (
    JuliaToolSpecOptionalWidget,
    PythonToolSpecOptionalWidget,
    ExecutableToolSpecOptionalWidget,
)
from tests.mock_helpers import create_mock_toolbox_with_mock_qsettings, MockQSettings


class TestToolSpecificationEditorWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Overridden method. Runs once before all tests in this class."""
        try:
            cls.app = QApplication().processEvents()
        except RuntimeError:
            pass
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def setUp(self):
        """Overridden method. Runs before each test."""
        self._temp_dir = TemporaryDirectory()
        self.toolbox = create_mock_toolbox_with_mock_qsettings()
        self.tool_specification_widget = None

    def tearDown(self):
        """Overridden method. Runs after each test.
        Use this to free resources after a test if needed.
        """
        self._temp_dir.cleanup()
        if self.tool_specification_widget is not None:
            with mock.patch("spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase.tear_down") as mock_tear_down:
                mock_tear_down.return_value = True
                self.tool_specification_widget.close()
                mock_tear_down.assert_called()
            self.tool_specification_widget.deleteLater()
            self.tool_specification_widget = None

    def make_tool_spec_editor(self, spec=None):
        with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui, mock.patch(
                    "spine_items.tool.tool_specifications.ToolSpecification._includes_main_path_relative") as mock_mpr:
            mock_mpr.return_value = ""
            self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox, spec)
            mock_restore_ui.assert_called()
            mock_mpr.assert_called()

    def test_create_minimal_julia_tool_specification(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # 0: Julia
        self.assertIsInstance(self.tool_specification_widget.optional_widget, JuliaToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_julia_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_python_tool_specification(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(1)  # 1: Python
        self.assertIsInstance(self.tool_specification_widget.optional_widget, PythonToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_python_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_gams_tool_specification(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(2)  # 2: gams
        self.assertIsNone(self.tool_specification_widget.optional_widget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_gams_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def test_create_minimal_executable_tool_specification(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(3)  # 3: executable
        self.assertIsInstance(self.tool_specification_widget.optional_widget, ExecutableToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_executable_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            self._call_save()

    def _call_save(self):
        """Calls tool spec widgets _save() while Toolbox's tool spec widget base _save() is mocked."""
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._save"
        ) as mock_save:
            mock_save.return_value = True
            self.tool_specification_widget._save()
            mock_save.assert_called()

    def test_change_tooltype(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # julia
        self.assertIsInstance(self.tool_specification_widget._get_optional_widget("julia"), JuliaToolSpecOptionalWidget)
        sd = self.tool_specification_widget.spec_dict
        exec_settings = sd.get("execution_settings")
        self.assertEqual(sd["tooltype"], "julia")
        self.assertEqual(len(exec_settings), 5)
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(1)  # python
        self.assertIsInstance(self.tool_specification_widget._get_optional_widget("python"), PythonToolSpecOptionalWidget)
        sd = self.tool_specification_widget.spec_dict
        exec_settings = sd.get("execution_settings")
        self.assertEqual(sd["tooltype"], "python")
        self.assertEqual(len(exec_settings), 4)
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(2)  # gams
        self.assertIsNone(self.tool_specification_widget._get_optional_widget("gams"))
        sd = self.tool_specification_widget.spec_dict
        exec_settings = sd.get("execution_settings")
        self.assertEqual(sd["tooltype"], "gams")
        self.assertIsNone(exec_settings)
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(3)  # executable
        self.assertIsInstance(self.tool_specification_widget._get_optional_widget("executable"), ExecutableToolSpecOptionalWidget)
        sd = self.tool_specification_widget.spec_dict
        exec_settings = sd.get("execution_settings")
        self.assertEqual(sd["tooltype"], "executable")
        self.assertEqual(len(exec_settings), 2)

    def test_make_new_specification(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # julia
        self.assertIsInstance(self.tool_specification_widget.optional_widget, JuliaToolSpecOptionalWidget)
        self.tool_specification_widget._spec_toolbar._line_edit_name.setText("test_julia_tool")
        with NamedTemporaryFile(mode="r") as temp_file:
            self.tool_specification_widget._set_main_program_file(str(Path(temp_file.name)))
            spec = self.tool_specification_widget._make_new_specification("test_julia_tool")
            self.tool_specification_widget._init_optional_widget(spec)
            self.assertIsInstance(spec, JuliaTool)
            self.assertEqual(len(spec.execution_settings), 5)

    def test_open_tool_specification_editor_with_julia_spec(self):
        script_dir = Path(self._temp_dir.name, "scripts")
        script_dir.mkdir()
        script_file_name = "hello.jl"
        file_path = Path(script_dir, script_file_name)
        with open(file_path, "w") as script_file:
            script_file.writelines(["println('hello')\n"])
        mock_logger = mock.MagicMock()
        julia_tool_spec = JuliaTool("test_julia_spec", "julia", str(script_dir), [script_file_name], MockQSettings(), mock_logger, "Description", inputfiles=["data.csv"], inputfiles_opt=["*.dat"], outputfiles=["results.txt"], cmdline_args=["-A", "-B"])
        julia_tool_spec.set_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(julia_tool_spec)
        opt_widget = self.tool_specification_widget.optional_widget
        self.assertIsInstance(opt_widget, JuliaToolSpecOptionalWidget)
        self.assertTrue(self.tool_specification_widget._ui.comboBox_tooltype.currentText() == "Julia")
        self.assertTrue(self.tool_specification_widget._ui.lineEdit_args.text() == "-A -B")
        # Program files dock widget should have 2 rows :'Main program file' and 'Additional program files'
        self.assertEqual(2, self.tool_specification_widget.programfiles_model.rowCount())
        # Get index of 'Main program file' item
        parent = self.tool_specification_widget.programfiles_model.index(0, 0)
        # There should be one row under 'Main program file' -> the main program file
        self.assertEqual(1, self.tool_specification_widget.programfiles_model.rowCount(parent))
        index = self.tool_specification_widget.programfiles_model.index(0, 0, parent)  # Index of 'hello.jl'
        item = self.tool_specification_widget.programfiles_model.itemFromIndex(index)
        self.assertEqual(script_file_name, item.data(Qt.ItemDataRole.DisplayRole))
        # Check Input & output files dock widget
        self.assertEqual(3, self.tool_specification_widget.io_files_model.rowCount())
        if_index = self.tool_specification_widget.io_files_model.index(0, 0)  # 'Input files' item index
        oif_index = self.tool_specification_widget.io_files_model.index(1, 0)  # 'Optional input files' item index
        of_index = self.tool_specification_widget.io_files_model.index(2, 0)  # 'Output files' item index
        if_child_index = self.tool_specification_widget.io_files_model.index(0, 0, if_index)
        oif_child_index = self.tool_specification_widget.io_files_model.index(0, 0, oif_index)
        of_child_index = self.tool_specification_widget.io_files_model.index(0, 0, of_index)
        self.assertEqual(1, self.tool_specification_widget.io_files_model.rowCount(if_index))
        self.assertEqual(1, self.tool_specification_widget.io_files_model.rowCount(oif_index))
        self.assertEqual(1, self.tool_specification_widget.io_files_model.rowCount(of_index))
        if_item = self.tool_specification_widget.io_files_model.itemFromIndex(if_child_index)
        self.assertEqual("data.csv", if_item.data(Qt.ItemDataRole.DisplayRole))
        oif_item = self.tool_specification_widget.io_files_model.itemFromIndex(oif_child_index)
        self.assertEqual("*.dat", oif_item.data(Qt.ItemDataRole.DisplayRole))
        of_item = self.tool_specification_widget.io_files_model.itemFromIndex(of_child_index)
        self.assertEqual("results.txt", of_item.data(Qt.ItemDataRole.DisplayRole))

    def test_open_tool_specification_editor_with_executable_spec(self):
        mock_logger = mock.MagicMock()
        exec_tool_spec = ExecutableTool("a", "executable", "", ["fake_main_program.bat"], MockQSettings(), mock_logger)
        exec_tool_spec.set_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(exec_tool_spec)
        opt_widget = self.tool_specification_widget._get_optional_widget("executable")
        self.assertIsInstance(opt_widget, ExecutableToolSpecOptionalWidget)
        self.assertFalse(opt_widget.ui.lineEdit_command.isEnabled())  # Command is disabled when a program file is set
        # Program files dock widet should have 2 rows :'Main program file' and 'Additional program files'
        self.assertEqual(2, self.tool_specification_widget.programfiles_model.rowCount())
        # Get index of 'Main program file' item
        parent = self.tool_specification_widget.programfiles_model.index(0, 0)
        # There should be one row under 'Main program file' -> the main program file
        self.assertEqual(1, self.tool_specification_widget.programfiles_model.rowCount(parent))
        index = self.tool_specification_widget.programfiles_model.index(0, 0, parent)  # Index of 'fake_main_program.bat'
        item = self.tool_specification_widget.programfiles_model.itemFromIndex(index)
        self.assertEqual("fake_main_program.bat", item.data(Qt.ItemDataRole.DisplayRole))


if __name__ == "__main__":
    unittest.main()
