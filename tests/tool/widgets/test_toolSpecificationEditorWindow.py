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

"""Unit tests for ToolSpecificationEditorWindow class and tool_spec_optional_widgets module."""
import unittest
import logging
import sys
import os
from unittest import mock
from tempfile import NamedTemporaryFile, TemporaryDirectory
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QItemSelectionModel
from PySide6.QtGui import QIcon
from spine_items.tool.tool_specifications import JuliaTool, ExecutableTool, PythonTool
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
            with mock.patch(
                "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase.tear_down"
            ) as mock_tear_down:
                mock_tear_down.return_value = True
                self.tool_specification_widget.close()
                mock_tear_down.assert_called()
            self.tool_specification_widget.deleteLater()
            self.tool_specification_widget = None

    def make_tool_spec_editor(self, spec=None):
        if not spec:
            with mock.patch("spinetoolbox.project_item.specification_editor_window.restore_ui") as mock_restore_ui:
                self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox)
                mock_restore_ui.assert_called()
        else:
            with mock.patch(
                "spinetoolbox.project_item.specification_editor_window.restore_ui"
            ) as mock_restore_ui, mock.patch(
                "spine_items.tool.tool_specifications.ToolSpecification._includes_main_path_relative"
            ) as mock_impr:
                mock_impr.return_value = ""
                self.tool_specification_widget = ToolSpecificationEditorWindow(self.toolbox, spec)
                mock_restore_ui.assert_called()
                mock_impr.assert_called()

    def test_change_tooltype(self):
        self.make_tool_spec_editor()
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(0)  # julia
        self.assertIsInstance(self.tool_specification_widget._get_optional_widget("julia"), JuliaToolSpecOptionalWidget)
        sd = self.tool_specification_widget.spec_dict
        exec_settings = sd.get("execution_settings")
        self.assertEqual(sd["tooltype"], "julia")
        self.assertEqual(len(exec_settings), 5)
        self.tool_specification_widget._ui.comboBox_tooltype.setCurrentIndex(1)  # python
        self.assertIsInstance(
            self.tool_specification_widget._get_optional_widget("python"), PythonToolSpecOptionalWidget
        )
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
        self.assertIsInstance(
            self.tool_specification_widget._get_optional_widget("executable"), ExecutableToolSpecOptionalWidget
        )
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
            self.tool_specification_widget._set_main_program_file(temp_file.name)
            spec = self.tool_specification_widget._make_new_specification("test_julia_tool")
            self.tool_specification_widget._init_optional_widget(spec)
            self.assertIsInstance(spec, JuliaTool)
            self.assertEqual(len(spec.execution_settings), 5)
        self._call_save()

    def _call_save(self):
        """Calls tool spec widgets _save() while Toolbox's tool spec widget base _save() is mocked."""
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._save"
        ) as mock_save:
            mock_save.return_value = True
            self.tool_specification_widget._save()
            mock_save.assert_called()

    def test_open_tool_specification_editor_with_julia_spec(self):
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
            "Description",
            inputfiles=["data.csv"],
            inputfiles_opt=["*.dat"],
            outputfiles=["results.txt"],
            cmdline_args=["-A", "-B"],
        )
        julia_tool_spec.init_execution_settings()  # Sets defaults
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
        exec_tool_spec = ExecutableTool(
            "a", "executable", self._temp_dir.name, ["fake_main_program.bat"], MockQSettings(), mock_logger
        )
        exec_tool_spec.init_execution_settings()  # Sets defaults
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
        index = self.tool_specification_widget.programfiles_model.index(
            0, 0, parent
        )  # Index of 'fake_main_program.bat'
        item = self.tool_specification_widget.programfiles_model.itemFromIndex(index)
        self.assertEqual("fake_main_program.bat", item.data(Qt.ItemDataRole.DisplayRole))

    def test_edit_and_save_program_file(self):
        mock_logger = mock.MagicMock()
        script_file_name = "hello.py"
        file_path = Path(self._temp_dir.name, script_file_name)
        with open(file_path, "w") as h:
            h.writelines(["# hello.py"])  # Make hello.py
        python_tool_spec = PythonTool(
            "a", "python", self._temp_dir.name, [script_file_name], MockQSettings(), mock_logger
        )
        python_tool_spec.init_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(python_tool_spec)
        parent = self.tool_specification_widget.programfiles_model.index(0, 0)
        index = self.tool_specification_widget.programfiles_model.index(0, 0, parent)  # Index of 'hello.py'
        self.tool_specification_widget._ui.textEdit_program.appendPlainText("print('hi')")
        self.tool_specification_widget._save_program_file(
            file_path, self.tool_specification_widget._ui.textEdit_program.document()
        )
        # Open file and check contents
        with open(file_path, "r") as edited_file:
            l = edited_file.readlines()
            self.assertEqual(2, len(l))
            self.assertTrue(l[0].startswith("# hello"))  # Don't match the whole str to avoid problems with newline
            self.assertTrue(l[1].startswith("print('hi')"))

    def test_change_python_spec_options(self):
        mock_logger = mock.MagicMock()
        script_file_name = "hello.py"
        file_path = Path(self._temp_dir.name, script_file_name)
        with open(file_path, "w") as h:
            h.writelines(["# hello.py"])  # Make hello.py
        python_tool_spec = PythonTool(
            "a", "python", self._temp_dir.name, [script_file_name], MockQSettings(), mock_logger
        )
        python_tool_spec.init_execution_settings()  # Sets defaults
        python_tool_spec.execution_settings["use_jupyter_console"] = True
        python_tool_spec.execution_settings["kernel_spec_name"] = "python310"
        with mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.KernelFetcher", new=FakeKernelFetcher):
            self.make_tool_spec_editor(python_tool_spec)
            opt_widget = self.tool_specification_widget.optional_widget
            self.assertTrue(opt_widget.ui.radioButton_jupyter_console.isChecked())
            self.assertEqual(3, opt_widget.kernel_spec_model.rowCount())
            self.assertEqual(1, opt_widget.ui.comboBox_kernel_specs.currentIndex())
            self.assertEqual("python310", opt_widget.ui.comboBox_kernel_specs.currentText())
            self.tool_specification_widget.push_change_kernel_spec_command(2)
            self.assertEqual(
                "python311", self.tool_specification_widget.spec_dict["execution_settings"]["kernel_spec_name"]
            )
            self.assertEqual(2, opt_widget.ui.comboBox_kernel_specs.currentIndex())
            self.assertEqual("python311", opt_widget.ui.comboBox_kernel_specs.currentText())
            self.assertTrue(self.tool_specification_widget.spec_dict["execution_settings"]["use_jupyter_console"])
            # Test SharedToolSpecOptionalWidget._restore_selected_kernel()
            # Restore selected kernel after the kernel spec model has been reloaded
            opt_widget.start_kernel_fetcher()
            self.assertEqual(3, opt_widget.kernel_spec_model.rowCount())
            self.assertEqual(2, opt_widget.ui.comboBox_kernel_specs.currentIndex())
            self.assertEqual("python311", opt_widget.ui.comboBox_kernel_specs.currentText())
            # Test push_set_jupyter_console_mode()
            self.tool_specification_widget.push_set_jupyter_console_mode(False)
            self.assertFalse(self.tool_specification_widget.spec_dict["execution_settings"]["use_jupyter_console"])
            opt_widget.set_executable("path/to/executable")
            self.tool_specification_widget.push_change_executable(opt_widget.get_executable())
            self.assertEqual(
                "path/to/executable", self.tool_specification_widget.spec_dict["execution_settings"]["executable"]
            )
            self.tool_specification_widget._push_change_args_command("-A -B")
            self.assertEqual(["-A", "-B"], self.tool_specification_widget.spec_dict["cmdline_args"])

    def test_change_executable_spec_options(self):
        mock_logger = mock.MagicMock()
        batch_file = "hello.bat"
        another_batch_file = "hello.sh"
        exec_tool_spec = ExecutableTool(
            "a", "executable", self._temp_dir.name, [batch_file, "data.file"], MockQSettings(), mock_logger
        )
        exec_tool_spec.init_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(exec_tool_spec)
        file_path = Path(self._temp_dir.name, another_batch_file)
        parent_main = self.tool_specification_widget.programfiles_model.index(0, 0)  # Main program file item
        parent_addit = self.tool_specification_widget.programfiles_model.index(1, 0)  # Additional program files item
        mp_index = self.tool_specification_widget.programfiles_model.index(0, 0, parent_main)
        # Try to open main program file
        with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.open_url") as mock_open_url:
            self.tool_specification_widget.open_program_file(mp_index)  # Fails because it's a .bat
            mock_open_url.assert_not_called()
        # Change main program file
        self.tool_specification_widget._push_change_main_program_file_command(file_path)
        mp_index = self.tool_specification_widget.programfiles_model.index(0, 0, parent_main)
        # Try to open main program file again
        with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.open_url") as mock_open_url:
            self.tool_specification_widget.open_program_file(mp_index)  # Calls open_url()
            mock_open_url.assert_called()
        # Try removing files without selecting anything
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._show_status_bar_msg"
        ) as m_notify:
            self.tool_specification_widget.remove_program_files()
            m_notify.assert_called()
        # Set 'data.file' selected
        self.assertEqual(1, self.tool_specification_widget.programfiles_model.rowCount(parent_main))
        self.assertEqual(1, self.tool_specification_widget.programfiles_model.rowCount(parent_addit))
        index = self.tool_specification_widget.programfiles_model.index(0, 0, parent_addit)  # Index of 'data.file'
        selection_model = self.tool_specification_widget._ui.treeView_programfiles.selectionModel()
        selection_model.setCurrentIndex(index, QItemSelectionModel.SelectionFlag.Select)
        # Remove additional program file 'data.file'
        self.tool_specification_widget.remove_program_files()
        self.assertEqual(0, self.tool_specification_widget.programfiles_model.rowCount(parent_addit))
        # Remove main program file
        self.tool_specification_widget.remove_all_program_files()
        self.assertEqual(0, self.tool_specification_widget.programfiles_model.rowCount(parent_main))
        # Do remove_all without selecting anything
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._show_status_bar_msg"
        ) as m_notify:
            self.tool_specification_widget.remove_all_program_files()
            m_notify.assert_called()
        # Add command for executable tool spec
        self.tool_specification_widget.optional_widget.ui.lineEdit_command.setText("ls -a")
        self.tool_specification_widget.push_change_executable_command(
            self.tool_specification_widget.optional_widget.ui.lineEdit_command.text()
        )
        # Check that no shell is selected
        self.assertEqual("", self.tool_specification_widget.optional_widget.get_current_shell())
        self.assertEqual("No shell", self.tool_specification_widget.optional_widget.ui.comboBox_shell.currentText())
        # Change shell to cmd.exe on win32, bash for others
        if sys.platform == "win32":
            index_of_cmd_exe = self.tool_specification_widget.optional_widget.shells.index("cmd.exe")
            self.tool_specification_widget.push_change_shell_command(index_of_cmd_exe)
            self.assertEqual("cmd.exe", self.tool_specification_widget.optional_widget.get_current_shell())
        else:
            index_of_bash = self.tool_specification_widget.optional_widget.shells.index("bash")
            self.tool_specification_widget.push_change_shell_command(index_of_bash)
            self.assertEqual("bash", self.tool_specification_widget.optional_widget.get_current_shell())

    def test_change_julia_project(self):
        mock_logger = mock.MagicMock()
        julia_tool_spec = JuliaTool("a", "julia", self._temp_dir.name, ["hello.jl"], MockQSettings(), mock_logger)
        julia_tool_spec.init_execution_settings()  # Sets defaults
        julia_tool_spec.execution_settings["use_jupyter_console"] = True
        with mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.KernelFetcher", new=FakeKernelFetcher):
            self.make_tool_spec_editor(julia_tool_spec)
            self.assertEqual("", self.tool_specification_widget.spec_dict["execution_settings"]["project"])
            self.tool_specification_widget.optional_widget.ui.lineEdit_julia_project.setText("path/to/julia_project")
            self.tool_specification_widget.push_change_project()
            self.assertEqual(
                "path/to/julia_project", self.tool_specification_widget.spec_dict["execution_settings"]["project"]
            )

    def test_restore_unknown_saved_kernel_into_optional_widget(self):
        mock_logger = mock.MagicMock()
        script_file_name = "hello.py"
        file_path = Path(self._temp_dir.name, script_file_name)
        with open(file_path, "w") as h:
            h.writelines(["# hello.py"])  # Make hello.py
        python_tool_spec = PythonTool(
            "a", "python", self._temp_dir.name, [script_file_name], MockQSettings(), mock_logger
        )
        python_tool_spec.init_execution_settings()  # Sets defaults
        python_tool_spec.execution_settings["use_jupyter_console"] = True
        python_tool_spec.execution_settings["kernel_spec_name"] = "unknown_kernel"
        with mock.patch(
            "spine_items.tool.widgets.tool_spec_optional_widgets.KernelFetcher", new=FakeKernelFetcher
        ), mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.Notification") as mock_notify:
            self.make_tool_spec_editor(python_tool_spec)
            opt_widget = self.tool_specification_widget.optional_widget
            self.assertTrue(opt_widget.ui.radioButton_jupyter_console.isChecked())
            self.assertEqual(3, opt_widget.kernel_spec_model.rowCount())
            self.assertEqual(0, opt_widget.ui.comboBox_kernel_specs.currentIndex())
            self.assertEqual("Select kernel spec...", opt_widget.ui.comboBox_kernel_specs.currentText())
            mock_notify.assert_called()

    def test_program_file_dialogs(self):
        mock_logger = mock.MagicMock()
        script_file_name = "hello.jl"
        script_file_name2 = "hello2.jl"
        data_file_name = "data.csv"
        file_path = Path(self._temp_dir.name, script_file_name)
        file_path2 = Path(self._temp_dir.name, script_file_name2)
        file_path3 = Path(self._temp_dir.name, data_file_name)
        # Make files so os.path.samefile() works
        with open(file_path, "w") as h:
            h.writelines(["println('Hello world')"])  # Make hello.jl
        with open(file_path2, "w") as h:
            h.writelines(["println('Hello world2')"])  # Make hello2.jl
        with open(file_path3, "w") as h:
            h.writelines(["1, 2, 3"])  # Make data.csv
        julia_tool_spec = JuliaTool(
            "a", "julia", self._temp_dir.name, [script_file_name, data_file_name], MockQSettings(), mock_logger
        )
        julia_tool_spec.init_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(julia_tool_spec)
        self.assertEqual("hello.jl", os.path.split(self.tool_specification_widget._current_main_program_file())[1])
        # Test browse_main_program_file()
        with mock.patch(
            "spine_items.tool.widgets.tool_specification_editor_window.QFileDialog.getOpenFileName"
        ) as mock_fd_gofn:
            mock_fd_gofn.return_value = [file_path2]
            # Change main program file hello.jl -> hello2.jl
            self.tool_specification_widget.browse_main_program_file()
            mock_fd_gofn.assert_called()
            self.assertEqual("hello2.jl", os.path.split(self.tool_specification_widget._current_main_program_file())[1])
            # Try to change additional program file as the main program, should pop up a QMessageBox
            mock_fd_gofn.return_value = [file_path3]
            with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.QMessageBox") as mock_mb:
                self.tool_specification_widget.browse_main_program_file()
                mock_mb.assert_called()
            self.assertEqual("hello2.jl", os.path.split(self.tool_specification_widget._current_main_program_file())[1])
        # Test new_main_program_file()
        with mock.patch(
            "spine_items.tool.widgets.tool_specification_editor_window.QFileDialog.getSaveFileName"
        ) as mock_fd_gsfn:
            mock_fd_gsfn.return_value = [file_path]
            # This should remove existing hello.jl, recreate it, and set it as main program
            self.tool_specification_widget.new_main_program_file()
            self.assertEqual(1, mock_fd_gsfn.call_count)
            self.assertEqual("hello.jl", os.path.split(self.tool_specification_widget._current_main_program_file())[1])
            # Test new_program_file()
            parent_addit = self.tool_specification_widget.programfiles_model.index(1, 0)
            self.assertEqual(1, self.tool_specification_widget.programfiles_model.rowCount(parent_addit))
            mock_fd_gsfn.return_value = [Path(self._temp_dir.name, "input.txt")]
            self.tool_specification_widget.new_program_file()
            self.assertEqual(2, mock_fd_gsfn.call_count)
            # Check that we now have 2 additional program files
            parent_addit = self.tool_specification_widget.programfiles_model.index(1, 0)
            self.assertEqual(2, self.tool_specification_widget.programfiles_model.rowCount(parent_addit))
            # Try to add file that's already been added
            mock_fd_gsfn.return_value = [file_path3]
            with mock.patch(
                "spine_items.tool.widgets.tool_specification_editor_window.QMessageBox.information"
            ) as mock_mb_info:
                self.tool_specification_widget.new_program_file()  # QMessageBox should appear
                mock_mb_info.assert_called()
            self.assertEqual(3, mock_fd_gsfn.call_count)
            self.assertEqual(2, self.tool_specification_widget.programfiles_model.rowCount(parent_addit))
        # Test show_add_program_files_dialog()
        with mock.patch(
            "spine_items.tool.widgets.tool_specification_editor_window.QFileDialog.getOpenFileNames"
        ) as mock_fd_gofns:
            with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.QMessageBox") as mock_mb:
                mock_fd_gofns.return_value = [[file_path]]
                self.tool_specification_widget.show_add_program_files_dialog()  # Shows 'Can't add main...' msg box
                self.assertEqual(1, mock_mb.call_count)
                self.assertEqual(1, mock_fd_gofns.call_count)
                mock_fd_gofns.return_value = [[file_path, file_path2, file_path3]]
                self.tool_specification_widget.show_add_program_files_dialog()  # Shows 'One file not add...' msg box
                self.assertEqual(2, mock_mb.call_count)
                self.assertEqual(2, mock_fd_gofns.call_count)
        # Test show_add_program_dirs_dialog()
        with mock.patch(
            "spine_items.tool.widgets.tool_specification_editor_window.QFileDialog.getExistingDirectory"
        ) as mock_fd_ged:
            mock_fd_ged.return_value = self._temp_dir.name
            self.tool_specification_widget.show_add_program_dirs_dialog()
            mock_fd_ged.assert_called()

    def test_add_rename_select_remove_input_and_output_files(self):
        mock_logger = mock.MagicMock()
        main_file = "hello.jl"
        main_path = Path(self._temp_dir.name, main_file)
        with open(main_path, "w") as h:
            h.writelines(["println('Hello world')"])  # Make hello.jl
        julia_tool_spec = JuliaTool("a", "julia", self._temp_dir.name, [main_file], MockQSettings(), mock_logger)
        julia_tool_spec.init_execution_settings()  # Sets defaults
        self.make_tool_spec_editor(julia_tool_spec)
        # INPUT FILES
        # Test add_input_files()
        with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.QInputDialog.getText") as mock_gt:
            mock_gt.return_value = ["data.csv"]
            self.tool_specification_widget.add_inputfiles()
            mock_gt.assert_called()
        iofm = self.tool_specification_widget.io_files_model
        selection_model = self.tool_specification_widget._ui.treeView_io_files.selectionModel()
        self.assertEqual(3, iofm.rowCount())  # row 0: Input files, row 1: Optional input files, row 2: Output files
        # There should be one item under 'Input files'
        input_files_root = iofm.index(0, 0)
        self.assertEqual(1, iofm.rowCount(input_files_root))
        input_file_item = iofm.itemFromIndex(iofm.index(0, 0, input_files_root))
        self.assertEqual("data.csv", input_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Test rename input file (tests _push_io_file_renamed_command())
        input_file_item.setData("renamed_file.csv", Qt.ItemDataRole.DisplayRole)
        input_file_item = iofm.itemFromIndex(iofm.index(0, 0, input_files_root))
        self.assertEqual("renamed_file.csv", input_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Try remove_inputfiles() without selections
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._show_status_bar_msg"
        ) as m_notify:
            self.tool_specification_widget.remove_inputfiles()
            m_notify.assert_called()
        # Select input file item
        selection_model.setCurrentIndex(iofm.index(0, 0, input_files_root), QItemSelectionModel.SelectionFlag.Select)
        # Test remove_inputfiles()
        self.tool_specification_widget.remove_inputfiles()
        self.assertEqual(0, iofm.rowCount(input_files_root))
        # OPTIONAL INPUT FILES
        # Test add_inputfiles_opt()
        with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.QInputDialog.getText") as mock_gt:
            mock_gt.return_value = ["*.dat"]
            self.tool_specification_widget.add_inputfiles_opt()
            mock_gt.assert_called()
        # There should be one item under 'Optional input files'
        opt_input_files_root = iofm.index(1, 0)
        self.assertEqual(1, iofm.rowCount(opt_input_files_root))
        opt_input_file_item = iofm.itemFromIndex(iofm.index(0, 0, opt_input_files_root))
        self.assertEqual("*.dat", opt_input_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Test rename optional input item (tests _push_io_file_renamed_command())
        opt_input_file_item.setData("???.dat", Qt.ItemDataRole.DisplayRole)
        opt_input_file_item = iofm.itemFromIndex(iofm.index(0, 0, opt_input_files_root))
        self.assertEqual("???.dat", opt_input_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Try remove_inputfiles_opt() without selections
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._show_status_bar_msg"
        ) as m_notify:
            self.tool_specification_widget.remove_inputfiles_opt()
            m_notify.assert_called()
        # Select optional input file item
        selection_model.setCurrentIndex(
            iofm.index(0, 0, opt_input_files_root), QItemSelectionModel.SelectionFlag.Select
        )
        # Test remove_inputfiles_opt()
        self.tool_specification_widget.remove_inputfiles_opt()
        self.assertEqual(0, iofm.rowCount(opt_input_files_root))
        # OUTPUT FILES
        # Test add_outputfiles()
        with mock.patch("spine_items.tool.widgets.tool_specification_editor_window.QInputDialog.getText") as mock_gt:
            mock_gt.return_value = ["results.txt"]
            self.tool_specification_widget.add_outputfiles()
            mock_gt.assert_called()
        # There should be one item under 'Output files'
        output_files_root = iofm.index(2, 0)
        self.assertEqual(1, iofm.rowCount(output_files_root))
        output_file_item = iofm.itemFromIndex(iofm.index(0, 0, output_files_root))
        self.assertEqual("results.txt", output_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Test rename output file
        output_file_item.setData("output.txt", Qt.ItemDataRole.DisplayRole)
        output_file_item = iofm.itemFromIndex(iofm.index(0, 0, output_files_root))
        self.assertEqual("output.txt", output_file_item.data(Qt.ItemDataRole.DisplayRole))
        # Try remove_outputfiles() without selections
        with mock.patch(
            "spinetoolbox.project_item.specification_editor_window.SpecificationEditorWindowBase._show_status_bar_msg"
        ) as m_notify:
            self.tool_specification_widget.remove_outputfiles()
            m_notify.assert_called()
        # Select output file item
        selection_model.setCurrentIndex(iofm.index(0, 0, output_files_root), QItemSelectionModel.SelectionFlag.Select)
        # Test remove_outputfiles()
        self.tool_specification_widget.remove_outputfiles()
        self.assertEqual(0, iofm.rowCount(output_files_root))


class FakeSignal:
    def __init__(self):
        self.call_list = list()  # List of slots

    def connect(self, method):
        """Stores all slots connected to this FakeSignal into a list."""
        self.call_list.append(method)


class FakeKernelFetcher:
    """Class for replacing KernelFetcher in tests."""

    kernel_found = FakeSignal()
    finished = FakeSignal()

    def __init__(self, conda_path="", fetch_mode=0):
        self.conda_path = conda_path
        self.fetch_mode = fetch_mode

    def isRunning(self):
        return False

    def start(self):
        for m in self.kernel_found.call_list:
            # Calls SharedToolSpecOptionalWidget.add_kernel()
            m("python310", "", False, QIcon(), dict())
            m("python311", "", False, QIcon(), dict())
        for meth in self.finished.call_list:
            # Calls two methods:
            # 1. Either SharedToolSpecOptionalWidget._restore_saved_kernel() or
            # SharedToolSpecOptionalWidget._restore_selected_kernel()
            # 2. mock.restore_overrider_cursor()
            # Note: The order of connect() calls matters.
            meth()
        # Clear signal slots, so this can be used again
        self.kernel_found.call_list.clear()
        self.finished.call_list.clear()


if __name__ == "__main__":
    unittest.main()
