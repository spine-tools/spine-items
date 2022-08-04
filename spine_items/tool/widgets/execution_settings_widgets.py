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
Execution settings widgets for Tool's properties tab.

:author: A. Soininen (VTT)
:date:   2.8.2022
"""
from PySide2.QtCore import Slot
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QWidget, QDialog

from spine_engine.execution_managers.conda_kernel_spec_manager import CondaKernelSpecManager
from spinetoolbox.helpers import busy_effect, select_python_interpreter
from spinetoolbox.widgets.kernel_editor import find_python_kernels, KernelEditor
from spine_engine.utils.helpers import resolve_python_interpreter, resolve_conda_executable
from ..commands import SetExecutionSetting
from ..utils import default_execution_settings


class ExecutionSettingsWidget(QWidget):
    """Base class for execution settings widgets."""

    def __init__(self, app_settings, undo_stack, logger):
        """
        Args:
            app_settings (QSettings): Toolbox settings
            undo_stack (QUndoStack): undo stack
            logger (LoggerInterface): a logger
        """
        super().__init__()
        self._app_settings = app_settings
        self._undo_stack = undo_stack
        self._execution_settings = None
        self._logger = logger

    def set_settings(self, execution_settings):
        """Updates the widget according to given execution settings.

        Args:
            execution_settings (dict): execution settings
        """
        self._execution_settings = execution_settings


class ExecutableExecutionSettingsWidget(ExecutionSettingsWidget):
    """Execution settings widget for Executable tools."""

    SHELLS = ("No shell", "cmd.exe", "powershell.exe", "bash")

    def __init__(self, app_settings, undo_stack, logger):
        """
        Args:
            app_settings (QSettings): Toolbox settings
            undo_stack (QUndoStack): undo stack
            logger (LoggerInterface): a logger
        """
        super().__init__(app_settings, undo_stack, logger)
        from ..ui.executable_execution_settings import Ui_Form

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._ui.shell_combo_box.addItems(self.SHELLS)
        self._ui.shell_combo_box.currentTextChanged.connect(self._update_shell)

    def set_settings(self, execution_settings):
        """See base class."""
        super().set_settings(execution_settings)
        self._ui.shell_combo_box.currentTextChanged.disconnect(self._update_shell)
        self._ui.shell_combo_box.setCurrentText(execution_settings["shell"])
        self._ui.shell_combo_box.currentTextChanged.connect(self._update_shell)

    def _set_shell(self, execution_settings, shell):
        """Sets shell for given execution settings.

        Args:
            execution_settings (dict): Executable tool's execution settings
            shell (str): new shell
        """
        execution_settings["shell"] = shell
        if execution_settings is self._execution_settings:
            self._ui.shell_combo_box.currentTextChanged.disconnect(self._update_shell)
            self._ui.shell_combo_box.setCurrentText(shell)
            self._ui.shell_combo_box.currentTextChanged.connect(self._update_shell)

    @Slot(str)
    def _update_shell(self, shell):
        """Updates shell in execution settings.

        Args:
            shell (str): new shell name
        """
        self._undo_stack.push(
            SetExecutionSetting(
                "shell change", self._execution_settings, shell, self._execution_settings["shell"], self._set_shell
            )
        )


class PythonExecutionSettingsWidget(ExecutionSettingsWidget):
    """Execution settings widget for Python tools."""

    def __init__(self, app_settings, undo_stack, logger):
        """
        Args:
            app_settings (QSettings): Toolbox settings
            undo_stack (QUndoStack): undo stack
            logger (LoggerInterface): a logger
        """
        super().__init__(app_settings, undo_stack, logger)
        from ..ui.python_execution_settings import Ui_Form

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._kernel_spec_model = QStandardItemModel(self)
        self._ui.comboBox_kernel_specs.setModel(self._kernel_spec_model)
        self._refresh_kernel_spec_model()
        self._kernel_spec_editor = None
        default_settings = default_execution_settings("python", app_settings)
        use_jupyter_console = default_settings["use_jupyter_console"]
        if use_jupyter_console:
            self._ui.radioButton_jupyter_console.setChecked(True)
        else:
            self._ui.radioButton_python_console.setChecked(True)
        self._ui.lineEdit_python_path.setPlaceholderText(resolve_python_interpreter(""))
        self._ui.lineEdit_python_path.setText(default_settings["executable"])
        row = self._find_index_by_data(default_settings["kernel_spec_name"])
        if row == -1:
            self._ui.comboBox_kernel_specs.setCurrentIndex(0)
        else:
            self._ui.comboBox_kernel_specs.setCurrentIndex(row)
        self._set_ui_for_jupyter_console_enabled(use_jupyter_console)
        self._ui.toolButton_refresh_kernel_specs.clicked.connect(self._refresh_kernel_spec_model)
        self._ui.comboBox_kernel_specs.currentIndexChanged.connect(self._change_kernel_spec)
        self._ui.radioButton_jupyter_console.toggled.connect(self._change_jupyter_console_enabled)
        self._ui.toolButton_browse_python.clicked.connect(self._browse_python_button_clicked)
        self._ui.pushButton_open_kernel_spec_viewer.clicked.connect(self._show_python_kernel_spec_editor)
        self._ui.lineEdit_python_path.editingFinished.connect(self._change_interpreter)

    def set_settings(self, execution_settings):
        """See base class."""
        super().set_settings(execution_settings)
        use_jupyter_console = execution_settings["use_jupyter_console"]
        self._ui.radioButton_jupyter_console.toggled.disconnect(self._change_jupyter_console_enabled)
        if use_jupyter_console:
            self._ui.radioButton_jupyter_console.setChecked(True)
        else:
            self._ui.radioButton_python_console.setChecked(True)
        self._ui.radioButton_jupyter_console.toggled.connect(self._change_jupyter_console_enabled)
        self._set_ui_for_jupyter_console_enabled(use_jupyter_console)
        k_spec = execution_settings["kernel_spec_name"]
        if not k_spec:
            self._silently_set_kernel_specs_combo_box_row(0)
        else:
            row = self._find_index_by_data(k_spec)
            if row == -1:
                self._logger.msg_error.emit(
                    f"This Tool spec has kernel spec '{k_spec}' saved " f"but it could not be found."
                )
                row = 0
            self._silently_set_kernel_specs_combo_box_row(row)
        self._ui.lineEdit_python_path.setText(execution_settings["executable"])

    def _set_ui_for_jupyter_console_enabled(self, enabled):
        """Enables or disables some UI elements in the optional widget.
        
        Args:
            enabled (bool): True if Jupyter console is enabled, False otherwise
        """
        self._ui.comboBox_kernel_specs.setEnabled(enabled)
        self._ui.toolButton_refresh_kernel_specs.setEnabled(enabled)
        self._ui.pushButton_open_kernel_spec_viewer.setEnabled(enabled)
        self._ui.lineEdit_python_path.setDisabled(enabled)
        self._ui.toolButton_browse_python.setDisabled(enabled)

    @busy_effect
    @Slot(bool)
    def _refresh_kernel_spec_model(self, _=False):
        """Searches for available Python kernels and populates the kernel model."""
        item = self._kernel_spec_model.item(self._ui.comboBox_kernel_specs.currentIndex())
        if not item or not item.data():
            selected_kernel_spec = None
        else:
            selected_kernel_spec = item.data()["kernel_spec_name"]
        self._kernel_spec_model.clear()
        first_item = QStandardItem("Select kernel spec...")
        self._kernel_spec_model.appendRow(first_item)
        # Add Python kernel specs
        kernel_specs = find_python_kernels()
        for n in kernel_specs.keys():
            item = QStandardItem(n + " [Jupyter]")
            spec_data = dict()
            spec_data["kernel_spec_name"] = n
            spec_data["env"] = ""
            item.setData(spec_data)
            self._kernel_spec_model.appendRow(item)
        # Add auto-generated conda kernel spec names
        conda_exe = self._app_settings.value("appSettings/condaPath", defaultValue="")
        conda_exe = resolve_conda_executable(conda_exe)
        if conda_exe:
            ksm = CondaKernelSpecManager(conda_exe=conda_exe)
            conda_specs = ksm.all_specs()
            for i in conda_specs.keys():
                item = QStandardItem(i + " [Conda]")
                spec_data = dict()
                spec_data["kernel_spec_name"] = i
                spec_data["env"] = "conda"
                item.setData(spec_data)
                self.kernel_spec_model.appendRow(item)
        # Set the previously selected kernel spec as the current item after the model has been rebuilt
        if selected_kernel_spec is not None:
            row = self._find_index_by_data(selected_kernel_spec)
            if row == -1:
                # The kernel spec may have been removed
                self._change_kernel_spec(0)
            else:
                self._silently_set_kernel_specs_combo_box_row(row)

    @Slot(int)
    def _change_kernel_spec(self, row):
        """Pushes a command to change kernel spec to undo stack.

        Args:
            row (int): kernel spec's row index in kernel spec model
        """
        item = self._kernel_spec_model.item(row)
        if not item.data():
            new_kernel_spec = ""
        else:
            new_kernel_spec = item.data()["kernel_spec_name"]
        previous_kernel_spec = self._execution_settings["kernel_spec_name"]
        self._undo_stack.push(
            SetExecutionSetting(
                "change kernel spec",
                self._execution_settings,
                new_kernel_spec,
                previous_kernel_spec,
                self._set_kernel_spec,
            )
        )

    def _set_kernel_spec(self, execution_settings, kernel_spec):
        """Sets kernel spec for given execution settings.

        Args:
            execution_settings (dict): execution settings
            kernel_spec (str): kernel spec name
        """
        execution_settings["kernel_spec_name"] = kernel_spec
        if execution_settings is self._execution_settings:
            row = self._find_index_by_data(kernel_spec)
            self._silently_set_kernel_specs_combo_box_row(row)

    @Slot(bool)
    def _change_jupyter_console_enabled(self, use_jupyter):
        """Pushes a command to change Jupyter console mode to undo stack.

        Args:
            use_jupyter (bool): True for Jupyter console, False for Basic console
        """
        old_value = self._execution_settings["use_jupyter_console"]
        if use_jupyter == old_value:
            return
        text = ("enable" if use_jupyter else "disable") + " use of Jupyter console"
        self._undo_stack.push(
            SetExecutionSetting(
                text, self._execution_settings, use_jupyter, old_value, self._set_jupyter_console_enabled
            )
        )

    def _set_jupyter_console_enabled(self, execution_settings, use_jupyter):
        """Enables Jupyter console or Basic console.

        Args:
            use_jupyter (bool): True for Jupyter console, False for Basic console
        """
        execution_settings["use_jupyter_console"] = use_jupyter
        if execution_settings is self._execution_settings:
            if use_jupyter:
                self._ui.radioButton_jupyter_console.setChecked(True)
            else:
                self._ui.radioButton_python_console.setChecked(True)
            self._set_ui_for_jupyter_console_enabled(use_jupyter)

    @Slot(bool)
    def _browse_python_button_clicked(self, _=False):
        """Shows a file browser for selecting a Python interpreter."""
        select_python_interpreter(self, self._ui.lineEdit_python_path)
        self._change_interpreter()

    @Slot()
    def _change_interpreter(self):
        """Pushes a command to change Python interpreter path to undo stack."""
        old_interpreter = self._execution_settings["executable"]
        new_interpreter = self._ui.lineEdit_python_path.text().strip()
        if new_interpreter == old_interpreter:
            return
        self._undo_stack.push(
            SetExecutionSetting(
                "change Python interpreter",
                self._execution_settings,
                new_interpreter,
                old_interpreter,
                self._set_interpreter,
            )
        )

    def _set_interpreter(self, execution_settings, interpreter_path):
        """Sets Python interpreter.

        Args:
            execution_settings (dict): execution settings
            interpreter_path (str): path to Python interpreter
        """
        execution_settings["executable"] = interpreter_path
        if execution_settings is self._execution_settings:
            self._ui.lineEdit_python_path.setText(interpreter_path)

    @Slot(bool)
    def _show_python_kernel_spec_editor(self, _=False):
        """Opens kernel editor, where user can make kernel specs for the Jupyter Console."""
        python_interpreter = self._ui.lineEdit_python_path.text()
        julia_interpreter = ""
        item = self._kernel_spec_model.item(self._ui.comboBox_kernel_specs.currentIndex())
        if not item.data():
            selected_kernel_spec = ""
        else:
            selected_kernel_spec = item.data()["kernel_spec_name"]
        self._kernel_spec_editor = KernelEditor(
            self, python_interpreter, julia_interpreter, "python", selected_kernel_spec, self._app_settings
        )
        self._kernel_spec_editor.finished.connect(self._python_kernel_editor_closed)
        self._kernel_spec_editor.open()

    @Slot(int)
    def _python_kernel_editor_closed(self, result_code):
        """Catches the selected Python kernel name when the editor is closed.

        Args:
            result_code (int): Dialog's result code
        """
        item = self._kernel_spec_model.item(self._ui.comboBox_kernel_specs.currentIndex())
        if not item.data():
            previous_kernel_spec = ""
        else:
            previous_kernel_spec = item.data()["kernel_spec_name"]
        self._refresh_kernel_spec_model()
        if result_code != QDialog.Accepted:
            # Set previous kernel selected in Python kernel combobox if it still exists
            row = self._find_index_by_data(previous_kernel_spec)
            self._ui.comboBox_kernel_specs.setCurrentIndex(row if row > -1 else 0)
            return
        new_kernel_spec = self._kernel_spec_editor.selected_kernel
        row = self._find_index_by_data(new_kernel_spec)
        if row == -1:  # New kernel spec not found, should be quite uncommon
            self._logger.msg_error.emit(f"Python kernel spec {new_kernel_spec} not found")
            self._silently_set_kernel_specs_combo_box_row(0)
        else:
            self._change_kernel_spec(row)
        self._kernel_spec_editor = None

    def _silently_set_kernel_specs_combo_box_row(self, row):
        """Changes the kernel specs combo box row without pushing commands to undo stack.

        Args:
            row (int): new combo box row
        """
        self._ui.comboBox_kernel_specs.currentIndexChanged.disconnect(self._change_kernel_spec)
        self._ui.comboBox_kernel_specs.setCurrentIndex(row)
        self._ui.comboBox_kernel_specs.currentIndexChanged.connect(self._change_kernel_spec)

    def _find_index_by_data(self, string):
        """Searches the kernel spec model for the first item whose data matches the given string.

        Args:
            string (str): string to match

        Returns:
            int: the item's row number or -1 if not found
        """
        if string == "":
            return 0
        for row in range(1, self._kernel_spec_model.rowCount()):
            index = self._kernel_spec_model.index(row, 0)
            item = self._kernel_spec_model.itemFromIndex(index)
            d = item.data()
            if d["kernel_spec_name"] == string:
                return row
        return -1
