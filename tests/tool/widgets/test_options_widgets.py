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

"""Unit tests for the options_widgets.py module."""
import logging
import sys
from pathlib import Path
import unittest
from unittest import mock
from spine_items.tool.widgets.options_widgets import JuliaOptionsWidget, PythonOptionsWidget, ExecutableOptionsWidget
from spine_items.tool.tool_specifications import PythonTool
from tests.mock_helpers import MockQSettings
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QIcon


class TestJuliaOptionsWidget(unittest.TestCase):
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

    @unittest.skip("Under construction")
    def test_options_widget(self):
        ow = JuliaOptionsWidget()
        ow.set_tool(QWidget())  # Obviously not a real Tool
        ow._set_ui_at_work()
        ow._set_ui_at_rest()
        options = {"julia_sysimage": "/some/path"}
        ow.do_update_options(options)
        self.assertEqual("/some/path", ow.ui.lineEdit_sysimage.text())


#     def test_change_python_tool_options(self):
#         mock_logger = mock.MagicMock()
#         script_file_name = "hello.py"
#         file_path = Path(self._temp_dir.name, script_file_name)
#         with open(file_path, "w") as h:
#             h.writelines(["# hello.py"])  # Make hello.py
#         python_tool_spec = PythonTool(
#             "a", "python", self._temp_dir.name, [script_file_name], MockQSettings(), mock_logger
#         )
#         python_tool_spec.init_execution_settings()  # Sets defaults
#         python_tool_spec.execution_settings["use_jupyter_console"] = True
#         python_tool_spec.execution_settings["kernel_spec_name"] = "python310"
#         with mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.KernelFetcher", new=FakeKernelFetcher):
#             self.make_tool_spec_editor(python_tool_spec)
#             self.tool_specification_widget._push_change_args_command("-A -B")
#             self.assertEqual(["-A", "-B"], self.tool_specification_widget.spec_dict["cmdline_args"])
#
#     def test_restore_unknown_saved_kernel_into_optional_widget(self):
#         mock_logger = mock.MagicMock()
#         script_file_name = "hello.py"
#         file_path = Path(self._temp_dir.name, script_file_name)
#         with open(file_path, "w") as h:
#             h.writelines(["# hello.py"])  # Make hello.py
#         python_tool_spec = PythonTool(
#             "a", "python", self._temp_dir.name, [script_file_name], MockQSettings(), mock_logger
#         )
#         python_tool_spec.init_execution_settings()  # Sets defaults
#         python_tool_spec.execution_settings["use_jupyter_console"] = True
#         python_tool_spec.execution_settings["kernel_spec_name"] = "unknown_kernel"
#         with (
#             mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.KernelFetcher", new=FakeKernelFetcher),
#             mock.patch("spine_items.tool.widgets.tool_spec_optional_widgets.Notification") as mock_notify,
#         ):
#             self.make_tool_spec_editor(python_tool_spec)
#             opt_widget = self.tool_specification_widget.optional_widget
#             self.assertTrue(opt_widget.ui.radioButton_jupyter_console.isChecked())
#             self.assertEqual(3, opt_widget.kernel_spec_model.rowCount())
#             self.assertEqual(0, opt_widget.ui.comboBox_kernel_specs.currentIndex())
#             self.assertEqual("Select kernel spec...", opt_widget.ui.comboBox_kernel_specs.currentText())
#             mock_notify.assert_called()
#
#     def test_set_cmd_for_executable_tool_spec(self):
#         # Add command for executable tool spec
#         self.tool_specification_widget.optional_widget.ui.lineEdit_command.setText("ls -a")
#         self.tool_specification_widget.push_change_executable_command(
#             self.tool_specification_widget.optional_widget.ui.lineEdit_command.text()
#         )
#         # Check that no shell is selected
#         self.assertEqual("", self.tool_specification_widget.optional_widget.get_current_shell())
#         self.assertEqual("No shell", self.tool_specification_widget.optional_widget.ui.comboBox_shell.currentText())
#         # Change shell to cmd.exe on win32, bash for others
#         if sys.platform == "win32":
#             index_of_cmd_exe = self.tool_specification_widget.optional_widget.shells.index("cmd.exe")
#             self.tool_specification_widget.push_change_shell_command(index_of_cmd_exe)
#             self.assertEqual("cmd.exe", self.tool_specification_widget.optional_widget.get_current_shell())
#         else:
#             index_of_bash = self.tool_specification_widget.optional_widget.shells.index("bash")
#             self.tool_specification_widget.push_change_shell_command(index_of_bash)
#             self.assertEqual("bash", self.tool_specification_widget.optional_widget.get_current_shell())
#
#
# class FakeSignal:
#     def __init__(self):
#         self.call_list = []  # List of slots
#
#     def connect(self, method):
#         """Stores all slots connected to this FakeSignal into a list."""
#         self.call_list.append(method)
#
#
# class FakeKernelFetcher:
#     """Class for replacing KernelFetcher in tests."""
#
#     kernel_found = FakeSignal()
#     finished = FakeSignal()
#
#     def __init__(self, conda_path="", fetch_mode=0):
#         self.conda_path = conda_path
#         self.fetch_mode = fetch_mode
#
#     def isRunning(self):
#         return False
#
#     def start(self):
#         for m in self.kernel_found.call_list:
#             # Calls SharedToolSpecOptionalWidget.add_kernel()
#             m("python310", "", False, QIcon(), {})
#             m("python311", "", False, QIcon(), {})
#         for meth in self.finished.call_list:
#             # Calls two methods:
#             # 1. Either SharedToolSpecOptionalWidget._restore_saved_kernel() or
#             # SharedToolSpecOptionalWidget._restore_selected_kernel()
#             # 2. mock.restore_overrider_cursor()
#             # Note: The order of connect() calls matters.
#             meth()
#         # Clear signal slots, so this can be used again
#         self.kernel_found.call_list.clear()
#         self.finished.call_list.clear()
