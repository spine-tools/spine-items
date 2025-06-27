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
import unittest
from unittest import mock
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QStandardItem, QIcon
from spine_items.tool.widgets.options_widgets import JuliaOptionsWidget, PythonOptionsWidget, ExecutableOptionsWidget
from spinetoolbox.kernel_models import ExecutableCompoundModels


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

    def test_julia_options_widget(self):
        models = ExecutableCompoundModels(mock.MagicMock())
        # Test without using Julia in PATH
        with mock.patch("spinetoolbox.kernel_models.resolve_default_julia_executable") as mock_default_julia:
            mock_default_julia.return_value = ""
            models.load_julia_executables([])
            mock_default_julia.assert_called()
        models.load_julia_projects([])
        ow = JuliaOptionsWidget(models)
        tool = FakeTool(models)
        ow.set_tool(tool)
        ow._set_ui_at_work()
        ow._set_ui_at_rest()
        options = {
            "julia_sysimage": "/some/path",
            "kernel_spec_name": "",
            "env": "",
            "use_jupyter_console": False,
            "executable": "",
            "project": "",
        }
        tool._options = options
        ow.do_update_options(options)
        self.assertEqual("/some/path", ow.ui.lineEdit_sysimage.text())
        self.assertEqual("", ow.get_executable())
        self.assertEqual("", ow.get_project())
        self.assertTrue(ow.ui.radioButton_basic_console.isChecked())
        ow._block_signals(True)
        first_item = QStandardItem("Select Jupyter kernel...")
        models.julia_kernel_model.appendRow(first_item)
        deats = {"kernel_name": "julia-kernel"}
        models._add_julia_kernel("julia-kernel", "/kernel_dir", False, QIcon(), deats)
        ow._block_signals(False)
        with mock.patch("spine_items.tool.widgets.options_widgets.select_file_path") as mock_select_fpath:
            mock_select_fpath.return_value = "new/julia"
            ow._add_julia_executable()
            mock_select_fpath.assert_called()
        self.assertEqual("new/julia", ow.get_executable())
        with mock.patch("spine_items.tool.widgets.options_widgets.select_dir") as mock_select_dir:
            mock_select_dir.return_value = "julia/project"
            ow._add_julia_project()
            mock_select_dir.assert_called()
        self.assertEqual("julia/project", ow.get_project())
        options = {
            "julia_sysimage": "/some/path",
            "kernel_spec_name": "julia-kernel",
            "env": "",
            "use_jupyter_console": True,
            "executable": "",
            "project": "",
        }
        tool._options = options
        ow.do_update_options(options)
        self.assertTrue(ow.ui.radioButton_jupyter_console.isChecked())
        self.assertEqual("julia-kernel", ow.get_kernel_name())

    def test_python_options_widget(self):
        models = ExecutableCompoundModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        ow = PythonOptionsWidget(models)
        tool = FakeTool(models)
        ow.set_tool(tool)
        options = {"kernel_spec_name": "", "env": "", "use_jupyter_console": False, "executable": ""}
        tool._options = options
        ow.do_update_options(options)
        self.assertEqual("", ow.get_executable())
        self.assertTrue(ow.ui.radioButton_basic_console.isChecked())
        ow._block_signals(True)
        first_item = QStandardItem("Select Jupyter kernel...")
        models.python_kernel_model.appendRow(first_item)
        deats = {"kernel_name": "python-kernel"}
        models._add_python_kernel("python-kernel", "/kernel_dir", False, QIcon(), deats)
        ow._block_signals(False)
        with mock.patch("spine_items.tool.widgets.options_widgets.select_file_path") as mock_select_fpath:
            mock_select_fpath.return_value = "new/python"
            ow._add_python_interpreter()
            mock_select_fpath.assert_called()
        self.assertEqual("new/python", ow.get_executable())
        options = {"kernel_spec_name": "python-kernel", "env": "", "use_jupyter_console": True, "executable": ""}
        tool._options = options
        ow.do_update_options(options)
        self.assertTrue(ow.ui.radioButton_jupyter_console.isChecked())
        self.assertEqual("python-kernel", ow.get_kernel_name())

    def test_executable_options_widget(self):
        models = ExecutableCompoundModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        ow = ExecutableOptionsWidget(models)
        tool = FakeTool(models)
        ow.set_tool(tool)
        options = {"cmd": "", "shell": ""}
        tool._options = options
        ow.do_update_options(options)
        self.assertEqual("", ow.get_shell())
        self.assertEqual("", ow.ui.lineEdit_command.text())
        if sys.platform == "win32":
            options = {"cmd": "dir", "shell": "cmd.exe"}
            tool._options = options
            ow.do_update_options(options)
            self.assertEqual("cmd.exe", ow.get_shell())
            self.assertEqual("dir", ow.ui.lineEdit_command.text())
        else:
            options = {"cmd": "ls", "shell": "bash"}
            tool._options = options
            ow.do_update_options(options)
            self.assertEqual("bash", ow.get_shell())
            self.assertEqual("ls", ow.ui.lineEdit_command.text())


class FakeTool:
    def __init__(self, models):
        self.name = "testTool"
        self.group_id = None
        self._models = models
        self._options = {}
        self.project = mock.MagicMock()

    @property
    def models(self):
        return self._models

    def update_options(self, changed_option):
        self._options.update(changed_option)
