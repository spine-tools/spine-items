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
Provides an optional widget for Tool Specification Editor for each Tool Spec type (julia, python, executable, gams).

:author: P. Savolainen (VTT)
:date:   12.2.2021
"""

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from PySide2.QtGui import QStandardItemModel, QStandardItem
from spine_engine.utils.helpers import resolve_conda_executable, resolve_python_interpreter
from spine_engine.execution_managers.conda_kernel_spec_manager import CondaKernelSpecManager
from spinetoolbox.helpers import busy_effect, file_is_valid, select_python_interpreter
from spinetoolbox.widgets.notification import Notification
from spinetoolbox.widgets.kernel_editor import KernelEditor, find_python_kernels


class OptionalWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent

    @property
    def _toolbox(self):
        return self._parent._toolbox

    @property
    def _project(self):
        return self._toolbox._project

    @property
    def _settings(self):
        return self._project._settings

    @property
    def _logger(self):
        return self._toolbox._logger

    def init_widget(self, specification):
        raise NotImplementedError

    def add_execution_settings(self):
        raise NotImplementedError


class PythonToolSpecOptionalWidget(OptionalWidget):
    def __init__(self, parent):
        """Init class."""
        from ..ui.python_kernel_spec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.kernel_spec_model = QStandardItemModel(self)
        self.ui.comboBox_kernel_specs.setModel(self.kernel_spec_model)
        self._refresh_kernel_spec_model()
        self._kernel_spec_editor = None
        # Initialize UI elements with defaults
        use_jupyter_console = int(self._toolbox.qsettings().value("appSettings/usePythonKernel", defaultValue="0"))
        if use_jupyter_console == 2:
            self.ui.radioButton_jupyter_console.setChecked(True)
        else:
            self.ui.radioButton_python_console.setChecked(True)
        default_python_path = self._toolbox.qsettings().value("appSettings/pythonPath", defaultValue="")
        self.ui.lineEdit_python_path.setPlaceholderText(resolve_python_interpreter(""))
        self.ui.lineEdit_python_path.setText(default_python_path)
        default_kernel_spec = self._toolbox.qsettings().value("appSettings/pythonKernel", defaultValue="")
        row = self.find_index_by_data(default_kernel_spec)
        if row == -1:
            self.ui.comboBox_kernel_specs.setCurrentIndex(0)
        else:
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)
        self.set_ui_for_jupyter_console(not use_jupyter_console)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals."""
        self.ui.toolButton_refresh_kernel_specs.clicked.connect(self._refresh_kernel_spec_model)
        self.ui.comboBox_kernel_specs.activated.connect(self._parent._push_change_kernel_spec_command)
        self.ui.radioButton_jupyter_console.toggled.connect(self._parent._push_set_jupyter_console_mode)
        self.ui.toolButton_browse_python.clicked.connect(self.browse_python_button_clicked)
        self.ui.pushButton_open_kernel_spec_viewer.clicked.connect(self.show_python_kernel_spec_editor)
        self.ui.lineEdit_python_path.editingFinished.connect(self._parent._push_change_executable)
        self.ui.fail_on_stderror_check_box.stateChanged.connect(self._parent._push_set_fail_on_stderror)

    def init_widget(self, specification):
        """Initializes UI elements based on specification

        Args:
            specification (ToolSpecification): Specification to load
        """
        use_jupyter_console = specification.execution_settings["use_jupyter_console"]
        self.ui.radioButton_jupyter_console.blockSignals(True)
        self.ui.radioButton_python_console.blockSignals(True)
        self.ui.fail_on_stderror_check_box.blockSignals(True)
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
            self.ui.fail_on_stderror_check_box.setEnabled(False)
            self.ui.fail_on_stderror_check_box.setChecked(False)
        else:
            self.ui.radioButton_python_console.setChecked(True)
            self.ui.fail_on_stderror_check_box.setEnabled(True)
            self.ui.fail_on_stderror_check_box.setChecked(
                specification.execution_settings.get("fail_on_stderror", True)
            )
        self.ui.radioButton_jupyter_console.blockSignals(False)
        self.ui.radioButton_python_console.blockSignals(False)
        self.ui.fail_on_stderror_check_box.blockSignals(False)
        self.set_ui_for_jupyter_console(not use_jupyter_console)
        k_spec = specification.execution_settings["kernel_spec_name"]
        if k_spec == "":
            self.ui.comboBox_kernel_specs.setCurrentIndex(0)  # Set 'Select kernel spec...'
        else:
            row = self.find_index_by_data(k_spec)
            if row == -1:
                notification = Notification(
                    self._parent, f"This Tool spec has kernel spec '{k_spec}' saved " f"but it could not be found."
                )
                notification.show()
                # TODO: What to do when a kernel spec name that is saved to Tool spec is not found?
                row += 1  # Set 'Select kernel spec...'
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)
        self.set_executable(specification.execution_settings["executable"])

    def add_execution_settings(self):
        """Collects execution settings based on optional widget state into a dictionary, which is returned."""
        idx = self.ui.comboBox_kernel_specs.currentIndex()
        if idx < 1:
            d = dict()
            d["kernel_spec_name"] = ""
            d["env"] = ""
        else:
            item = self.ui.comboBox_kernel_specs.model().item(idx)
            k_spec_data = item.data()
            d = k_spec_data
        d["use_jupyter_console"] = self.ui.radioButton_jupyter_console.isChecked()
        self.validate_executable()  # Raises NameError if Python path is not valid
        d["executable"] = self.get_executable()
        d["fail_on_stderror"] = self.ui.fail_on_stderror_check_box.isChecked()
        return d

    @Slot(bool)
    def browse_python_button_clicked(self, _=False):
        """Calls static method that shows a file browser for selecting a Python interpreter."""
        select_python_interpreter(self, self.ui.lineEdit_python_path)
        self._parent._push_change_executable()

    def set_ui_for_jupyter_console(self, value):
        """Enables or disables some UI elements in the optional widget according to checkBox state."""
        self.ui.comboBox_kernel_specs.setDisabled(value)
        self.ui.toolButton_refresh_kernel_specs.setDisabled(value)
        self.ui.pushButton_open_kernel_spec_viewer.setDisabled(value)
        self.ui.lineEdit_python_path.setDisabled((not value))
        self.ui.toolButton_browse_python.setDisabled(not value)
        self.ui.fail_on_stderror_check_box.setEnabled(value)

    def validate_executable(self):
        """Check that Python path in the line edit is a file it exists and the file name starts with 'python'.

        Raises:
            NameError: If the python path in the line edit is not valid
        """
        p = self.ui.lineEdit_python_path.text().strip()
        if not file_is_valid(self._parent, p, "Invalid Python Interpreter", extra_check="python"):
            raise NameError

    def set_executable(self, p):
        self.ui.lineEdit_python_path.setText(p)

    def get_executable(self):
        return self.ui.lineEdit_python_path.text().strip()

    @Slot(bool)
    def show_python_kernel_spec_editor(self, _=False):
        """Opens kernel editor, where user can make kernel specs for the Jupyter Console."""
        p = self.ui.lineEdit_python_path.text()  # This may be an empty string
        j = ""
        item = self.kernel_spec_model.item(self.ui.comboBox_kernel_specs.currentIndex())
        selected_kernel_spec = item.data()["kernel_spec_name"]
        self._kernel_spec_editor = KernelEditor(self._parent, p, j, "python", selected_kernel_spec)
        self._kernel_spec_editor.finished.connect(self.python_kernel_editor_closed)
        self._kernel_spec_editor.open()

    @Slot(int)
    def python_kernel_editor_closed(self, ret_code):
        """Catches the selected Python kernel name when the editor is closed."""
        item = self.kernel_spec_model.item(self.ui.comboBox_kernel_specs.currentIndex())
        previous_kernel_spec = item.data()["kernel_spec_name"]
        self._refresh_kernel_spec_model()
        if ret_code != 1:  # Editor closed with Cancel
            # TODO: Is this needed?
            # Set previous kernel selected in Python kernel combobox if it still exists
            r = self.find_index_by_data(previous_kernel_spec)
            if r == -1:
                self.ui.comboBox_kernel_specs.setCurrentIndex(0)  # Previous not found
            else:
                self.ui.comboBox_kernel_specs.setCurrentIndex(r)
            return
        new_kernel_spec = self._kernel_spec_editor.selected_kernel
        row = self.find_index_by_data(new_kernel_spec)
        if row == -1:  # New kernel spec not found, should be quite uncommon
            notification = Notification(self, f"Python kernel spec {new_kernel_spec} not found")
            notification.show()
            self.ui.comboBox_kernel_specs.setCurrentIndex(0)
        else:
            self._parent._push_change_kernel_spec_command(row)

    def find_index_by_data(self, string):
        """Searches the kernel spec model for the first item whose data matches the given string.
        Returns the items row number or -1 if not found."""
        if string == "":
            return 0
        for row in range(1, self.kernel_spec_model.rowCount()):  # Start from index 1
            index = self.kernel_spec_model.index(row, 0)
            item = self.kernel_spec_model.itemFromIndex(index)
            d = item.data()
            if d["kernel_spec_name"] == string:
                return row
        return -1

    @busy_effect
    @Slot(bool)
    def _refresh_kernel_spec_model(self):
        item = self.kernel_spec_model.item(self.ui.comboBox_kernel_specs.currentIndex())
        if not item or not item.data():
            selected_kernel_spec = None
        else:
            selected_kernel_spec = item.data()["kernel_spec_name"]  # Remember the selected kernel spec
        self.kernel_spec_model.clear()
        first_item = QStandardItem("Select kernel spec...")
        self.kernel_spec_model.appendRow(first_item)
        # Add Python kernel specs
        kernel_specs = find_python_kernels()
        for n in kernel_specs.keys():
            item = QStandardItem(n + " [Jupyter]")
            spec_data = dict()
            spec_data["kernel_spec_name"] = n
            spec_data["env"] = ""
            item.setData(spec_data)
            self.kernel_spec_model.appendRow(item)
        # Add auto-generated conda kernel spec names
        conda_exe = self._toolbox.qsettings().value("appSettings/condaPath", defaultValue="")
        conda_exe = resolve_conda_executable(conda_exe)
        if conda_exe != "":
            ksm = CondaKernelSpecManager(conda_exe=conda_exe)
            conda_specs = ksm._all_specs()
            for i in conda_specs.keys():
                item = QStandardItem(i + " [Conda]")
                spec_data = dict()
                spec_data["kernel_spec_name"] = i
                spec_data["env"] = "conda"
                item.setData(spec_data)
                self.kernel_spec_model.appendRow(item)
        # Set the previously selected kernel spec as the current item after the model has been rebuilt
        if selected_kernel_spec is not None:
            row = self.find_index_by_data(selected_kernel_spec)
            if row == -1:
                # The kernel spec may have been removed
                self._parent._push_change_kernel_spec_command(0)
                return
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)


class ExecutableToolSpecOptionalWidget(OptionalWidget):
    def __init__(self, parent):
        """Init class."""
        from ..ui.executable_cmd_exec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.shells = ["No shell", "cmd.exe", "powershell.exe", "bash"]
        self.ui.comboBox_shell.addItems(self.shells)
        self.connect_signals()

    def connect_signals(self):
        self.ui.lineEdit_command.editingFinished.connect(self._parent._push_change_executable_command)
        self.ui.comboBox_shell.activated.connect(self._parent._push_change_shell_command)

    def init_widget(self, specification):
        """Initializes UI elements based on specification."""
        self.ui.lineEdit_command.setText(specification.execution_settings["cmd"])
        shell = specification.execution_settings["shell"]
        ind = next(iter(k for k, t in enumerate(self.shells) if t.lower() == shell), 0)
        self.ui.comboBox_shell.setCurrentIndex(ind)

    def add_execution_settings(self):
        """Collects execution settings based on optional widget state into a dictionary, which is returned."""
        d = dict()
        d["cmd"] = self.ui.lineEdit_command.text()
        d["shell"] = self.get_current_shell()
        return d

    def get_current_shell(self):
        """Returns the selected shell in the shell combo box."""
        ind = self.ui.comboBox_shell.currentIndex()
        if ind < 1:
            return ""
        return self.ui.comboBox_shell.currentText()
