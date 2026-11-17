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

import os
import sys
import pytest
from unittest import mock
from PySide6.QtGui import QStandardItem, QIcon
from PySide6.QtCore import QPoint
from spine_items.tool.tool_factory import ToolFactory
from spine_items.tool.tool_specifications import ToolSpecification
from spine_items.tool.widgets.options_widgets import (
    JuliaOptionsWidget,
    PythonOptionsWidget,
    ExecutableOptionsWidget,
    ToolExecutionMethod,
)
from spinetoolbox.execution_models import ExecutionModels


class TestOptionsWidget:
    def test_julia_options_widget(self, application, spine_toolbox_with_project):
        models = ExecutionModels(mock.MagicMock())
        # Test without using Julia in PATH
        with mock.patch("spinetoolbox.execution_models.resolve_default_julia_executable") as mock_default_julia:
            mock_default_julia.return_value = ""
            models.load_julia_executables([])
            mock_default_julia.assert_called()
        models.load_julia_projects([])
        ow = JuliaOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "julia")
        ow.tool = tool
        ow._set_ui_at_work()
        ow._set_ui_at_rest()
        # Check stackedWidget default page
        tool._options = {}
        with mock.patch("spine_items.tool.widgets.options_widgets.default_julia_execution_settings") as mock_default_julia_settings:
            mock_default_julia_settings.return_value = {
                "kernel_spec_name": "",
                "env": "",
                "use_jupyter_console": False,
                "executable": "julia",
                "project": "julia-project",
            }
            ow.do_update_options_widget({})
            assert mock_default_julia_settings.call_count == 1
            assert ow.ui.label_execution_method.text() == "Julia executable & environment"
            assert ow.ui.label_executable_or_kernel.text() == "julia"
            assert ow.ui.label_environment.text() == "julia-project"
            mock_default_julia_settings.return_value = {
                "kernel_spec_name": "default-kernel",
                "env": "",
                "use_jupyter_console": True,
                "executable": "",
                "project": "",
            }
            ow.do_update_options_widget({})
            assert mock_default_julia_settings.call_count == 2
            assert ow.ui.label_execution_method.text() == "Jupyter kernel"
            assert ow.ui.label_executable_or_kernel.text() == "default-kernel"
            assert ow.ui.label_environment.text() == ""
        options = {
            "julia_sysimage": "/some/path",
            "kernel_spec_name": "",
            "env": "",
            "use_jupyter_console": False,
            "executable": "",
            "project": "",
        }
        tool._options = options
        ow.do_update_options_widget(options)
        assert ow.ui.lineEdit_sysimage.text() == "/some/path"
        assert ow.get_executable() == ""
        assert ow.get_project() == ""
        assert ow.ui.comboBox_julia_execution_method.currentData() == ToolExecutionMethod.DIRECT
        ow._block_signals(True)
        first_item = QStandardItem("Select Jupyter kernel...")
        models.julia_kernel_model.appendRow(first_item)
        deats = {"kernel_name": "julia-kernel"}
        models._add_julia_kernel("julia-kernel", "/kernel_dir", False, QIcon(), deats)
        ow._block_signals(False)
        with mock.patch("spinetoolbox.helpers.select_file_path") as mock_select_fpath:
            mock_select_fpath.return_value = "new/julia"
            ow._on_add_julia_executable_clicked()
            mock_select_fpath.assert_called()
        assert ow.get_executable() == "new/julia"
        with mock.patch("spinetoolbox.helpers.select_dir") as mock_select_dir:
            mock_select_dir.return_value = "julia/project"
            ow._on_add_julia_project_clicked()
            mock_select_dir.assert_called()
        assert ow.get_project() == "julia/project"
        options = {
            "julia_sysimage": "/some/path",
            "kernel_spec_name": "julia-kernel",
            "env": "",
            "use_jupyter_console": True,
            "executable": "",
            "project": "",
        }
        tool._options = options
        ow.do_update_options_widget(options)
        assert ow.ui.comboBox_julia_execution_method.currentData() == ToolExecutionMethod.JUPYTER
        assert ow.get_kernel_name() == "julia-kernel"
        options = {}
        tool._options = options
        with mock.patch(
            "spine_items.tool.widgets.options_widgets.default_julia_execution_settings"
        ) as mock_julia_defaults:
            mock_julia_defaults.return_value = {
                "kernel_spec_name": "",
                "env": "",
                "use_jupyter_console": False,
                "executable": "default/julia",
                "project": "/someProject",
            }
            ow.do_update_options_widget(options)
            mock_julia_defaults.assert_called()
        assert ow.ui.comboBox_julia_execution_method.currentData() == ToolExecutionMethod.DEFAULT
        exec_label_txt = ow.ui.label_executable_or_kernel.text().replace(os.sep, "/")
        assert exec_label_txt == "default/julia"
        env_label_txt = ow.ui.label_environment.text().replace(os.sep, "/")
        assert env_label_txt == "/someProject"

    def test_python_options_widget(self, application, spine_toolbox_with_project):
        models = ExecutionModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        ow = PythonOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "python")
        ow.tool = tool
        # Check stackedWidget default page
        tool._options = {}
        with mock.patch("spine_items.tool.widgets.options_widgets.default_python_execution_settings") as mock_default_python_settings:
            mock_default_python_settings.return_value = {
                "kernel_spec_name": "",
                "env": "",
                "use_jupyter_console": False,
                "executable": "python"
            }
            ow.do_update_options_widget({})
            assert mock_default_python_settings.call_count == 1
            assert ow.ui.label_execution_method.text() == "Python interpreter"
            assert ow.ui.label_interpreter_or_kernel.text() == "python"
            mock_default_python_settings.return_value = {
                "kernel_spec_name": "default-kernel",
                "env": "",
                "use_jupyter_console": True,
                "executable": ""
            }
            ow.do_update_options_widget({})
            assert mock_default_python_settings.call_count == 2
            assert ow.ui.label_execution_method.text() == "Jupyter kernel"
            assert ow.ui.label_interpreter_or_kernel.text() == "default-kernel"
        options = {"kernel_spec_name": "", "env": "", "use_jupyter_console": False, "executable": ""}
        tool._options = options
        ow.do_update_options_widget(options)
        assert ow.get_executable() == ""
        # Check current execution method combobox item by checking its data
        assert ow.ui.comboBox_python_execution_method.currentData() == ToolExecutionMethod.DIRECT
        ow._block_signals(True)
        first_item = QStandardItem("Select Jupyter kernel...")
        models.python_kernel_model.appendRow(first_item)
        deats = {"kernel_name": "python-kernel"}
        models._add_python_kernel("python-kernel", "/kernel_dir", False, QIcon(), deats)
        ow._block_signals(False)
        with mock.patch("spinetoolbox.helpers.select_file_path") as mock_select_fpath:
            mock_select_fpath.return_value = "new/python"
            ow._on_add_python_interpreter_clicked()
            mock_select_fpath.assert_called()
        assert ow.get_executable() == "new/python"
        options = {"kernel_spec_name": "python-kernel", "env": "", "use_jupyter_console": True, "executable": ""}
        tool._options = options
        ow.do_update_options_widget(options)
        assert ow.ui.comboBox_python_execution_method.currentData() == ToolExecutionMethod.JUPYTER
        assert ow.get_kernel_name() == "python-kernel"

    def test_python_options_widget_context_menus(self, application, spine_toolbox_with_project):
        models = ExecutionModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        models._add_python_kernel("python_kernel", "/kernel/resource/dir", False, QIcon(), {})
        ow = PythonOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "python")
        ow.tool = tool
        with mock.patch("spine_items.tool.widgets.options_widgets.PythonContextMenu") as mock_interp_menu:
            ow.ui.comboBox_executable.setCurrentIndex(0)
            ow._show_python_interpreters_context_menu(QPoint(0, 0))
            mock_interp_menu.assert_called_once()
            mock_interp_menu.assert_any_call(mock.ANY, mock.ANY, mock.ANY, "", mock.ANY, mock.ANY)
        with mock.patch("spine_items.tool.widgets.options_widgets.PythonContextMenu") as mock_kernel_menu:
            ow.ui.comboBox_kernel_specs.setCurrentIndex(0)
            ow._show_python_kernel_context_menu(QPoint(0, 0))
            mock_kernel_menu.assert_called_once()
            mock_kernel_menu.assert_any_call(
                mock.ANY, mock.ANY, mock.ANY, "/kernel/resource/dir", mock.ANY, mock.ANY
            )

    def test_julia_options_widget_context_menus(self, application, spine_toolbox_with_project):
        models = ExecutionModels(mock.MagicMock())
        # Add Julia to executables
        with mock.patch("spinetoolbox.execution_models.resolve_default_julia_executable") as mock_resolve_default_julia:
            # Mock resolve_default_julia_executable so the Julia from Path is not added to the model
            mock_resolve_default_julia.return_value = None
            models.load_julia_executables(["/some/julia"])
            mock_resolve_default_julia.assert_called_once()
        # Add Julia kernel
        models._add_julia_kernel("julia_kernel", "/kernel/resource/dir", False, QIcon(), {})
        models.load_julia_projects(["/julia/project"])
        ow = JuliaOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "julia")
        ow.tool = tool
        with mock.patch("spine_items.tool.widgets.options_widgets.JuliaContextMenu") as mock_exec_menu:
            ow.ui.comboBox_executable.setCurrentIndex(0)
            ow._show_julia_executables_context_menu(QPoint(0, 0))
            mock_exec_menu.assert_called_once()
            mock_exec_menu.assert_any_call(
                mock.ANY, mock.ANY, mock.ANY, "/some/julia", False, 0, ""
            )
        with mock.patch("spine_items.tool.widgets.options_widgets.JuliaContextMenu") as mock_kernel_menu:
            ow.ui.comboBox_kernel_specs.setCurrentIndex(0)
            ow._show_julia_kernel_context_menu(QPoint(0, 0))
            mock_kernel_menu.assert_called_once()
            mock_kernel_menu.assert_any_call(
                mock.ANY, mock.ANY, mock.ANY, "/kernel/resource/dir", False, 2, ""
            )
        with (mock.patch("spine_items.tool.widgets.options_widgets.JuliaContextMenu") as mock_projects_menu,
              mock.patch("os.path.exists") as mock_path_exists):
            mock_path_exists.return_value = True
            ow.ui.comboBox_executable.setCurrentIndex(0)
            ow.ui.comboBox_julia_project.setCurrentIndex(2)
            ow._show_julia_projects_context_menu(QPoint(0, 0))
            mock_projects_menu.assert_called_once()
            mock_path_exists.assert_called_once()
            mock_projects_menu.assert_any_call(
                mock.ANY, mock.ANY, mock.ANY, "/julia/project", False, 1, "/some"
            )

    def test_activate_execution_method(self, application, spine_toolbox_with_project):
        # Test PythonOptionsWidget
        models = ExecutionModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        ow = PythonOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "python")
        ow.tool = tool
        ow.ui.comboBox_python_execution_method.setCurrentIndex(0)
        ow.activate_execution_method(0)
        ow.ui.comboBox_python_execution_method.setCurrentIndex(1)
        ow.activate_execution_method(1)
        assert ow.tool._options["use_jupyter_console"] == False
        ow.ui.comboBox_python_execution_method.setCurrentIndex(2)
        ow.activate_execution_method(2)
        assert ow.tool._options["use_jupyter_console"] == True
        # Test JuliaOptionsWidget
        models = ExecutionModels(mock.MagicMock())
        # Test without using Julia in PATH
        with mock.patch("spinetoolbox.execution_models.resolve_default_julia_executable") as mock_default_julia:
            mock_default_julia.return_value = ""
            models.load_julia_executables([])
            mock_default_julia.assert_called()
        models.load_julia_projects([])
        ow = JuliaOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "julia")
        ow.tool = tool
        ow.ui.comboBox_julia_execution_method.setCurrentIndex(0)
        ow.activate_execution_method(0)
        ow.ui.comboBox_julia_execution_method.setCurrentIndex(1)
        ow.activate_execution_method(1)
        assert ow.tool._options["use_jupyter_console"] == False
        ow.ui.comboBox_julia_execution_method.setCurrentIndex(2)
        ow.activate_execution_method(2)
        assert ow.tool._options["use_jupyter_console"] == True

    def test_executable_options_widget(self, application, spine_toolbox_with_project):
        models = ExecutionModels(mock.MagicMock())
        models.load_python_system_interpreters([])
        ow = ExecutableOptionsWidget(models)
        tool = self._make_tool(spine_toolbox_with_project, "executable")
        ow.tool = tool
        options = {"cmd": "", "shell": ""}
        tool._options = options
        ow.do_update_options_widget(options)
        assert ow.get_shell() == ""
        assert ow.ui.lineEdit_command.text() == ""
        if sys.platform == "win32":
            options = {"cmd": "dir", "shell": "cmd.exe"}
            tool._options = options
            ow.do_update_options_widget(options)
            assert ow.get_shell() == "cmd.exe"
            assert ow.ui.lineEdit_command.text() == "dir"
        else:
            options = {"cmd": "ls", "shell": "bash"}
            tool._options = options
            ow.do_update_options_widget(options)
            assert ow.get_shell() == "bash"
            assert ow.ui.lineEdit_command.text() == "ls"
        ow.update_executable_tool_command("command string")
        ow._update_shell(0)
        ow.set_widget_disabled_state(True)
        ow.set_widget_disabled_state(False)

    def _make_tool(self, spine_toolbox_with_project, tool_type):
        item_dict = {"type": "Tool", "description": "", "x": 0, "y": 0}
        factory = ToolFactory()
        tool = factory.make_item("T", item_dict, spine_toolbox_with_project, spine_toolbox_with_project.project())
        tool.project.get_item = lambda name: tool
        tool_spec = ToolSpecification("spec", tool_type, "", list(), None, None)
        with (mock.patch("spine_items.tool.tool.Tool._check_notifications") as mock_check_notifications,
              mock.patch("spine_items.tool.tool.Tool.update_specification_icon") as mock_update_spec_icon):
            tool.set_specification(tool_spec)
            mock_check_notifications.assert_called_once()
            mock_update_spec_icon.assert_called_once()
        return tool
