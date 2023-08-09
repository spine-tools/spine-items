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

"""
Provides an optional widget for Tool Specification Editor for each Tool Spec type (julia, python, executable, gams).
"""

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import Qt, QStandardItemModel, QStandardItem, QIcon
from spine_engine.utils.helpers import resolve_python_interpreter
from spinetoolbox.helpers import file_is_valid, select_python_interpreter
from spinetoolbox.widgets.notification import Notification
from spinetoolbox.kernel_fetcher import KernelFetcher


class OptionalWidget(QWidget):
    def __init__(self, parent):
        """
        Args:
            parent (ToolSpecificationEditorWindow): Tool spec editor window
        """
        super().__init__()
        self._parent = parent

    @property
    def _toolbox(self):
        return self._parent._toolbox

    def init_widget(self, specification):
        raise NotImplementedError

    def add_execution_settings(self):
        raise NotImplementedError


class PythonToolSpecOptionalWidget(OptionalWidget):
    def __init__(self, parent):
        """
        Args:
            parent (ToolSpecificationEditorWindow): Tool spec editor window
        """
        from ..ui.python_kernel_spec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.kernel_spec_model = QStandardItemModel(self)
        self.ui.comboBox_kernel_specs.setModel(self.kernel_spec_model)
        self._kernel_spec_editor = None
        self._kernel_spec_model_initialized = False
        self._saved_kernel = None
        self._selected_kernel = None
        self.kernel_fetcher = None
        # Initialize UI elements with defaults
        use_jupyter_console = bool(
            int(self._toolbox.qsettings().value("appSettings/usePythonKernel", defaultValue="0"))
        )
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
            # Get the default kernel spec from Settings->Tools for new Jupyter Console Tool Specs
            self._saved_kernel = self._toolbox.qsettings().value("appSettings/pythonKernel", defaultValue="")
        else:
            self.ui.radioButton_python_console.setChecked(True)
        default_python_path = self._toolbox.qsettings().value("appSettings/pythonPath", defaultValue="")
        self.ui.lineEdit_python_path.setPlaceholderText(resolve_python_interpreter(""))
        self.ui.lineEdit_python_path.setText(default_python_path)
        self.set_ui_for_jupyter_console(use_jupyter_console)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals."""
        self.ui.toolButton_refresh_kernel_specs.clicked.connect(self.start_kernel_fetcher)
        self.ui.comboBox_kernel_specs.activated.connect(self._parent.push_change_kernel_spec_command)
        self.ui.radioButton_jupyter_console.toggled.connect(self._parent.push_set_jupyter_console_mode)
        self.ui.toolButton_browse_python.clicked.connect(self.browse_python_button_clicked)
        self.ui.lineEdit_python_path.editingFinished.connect(self._parent.push_change_executable)
        qApp.aboutToQuit.connect(self.stop_fetching_kernels)  # pylint: disable=undefined-variable

    def init_widget(self, specification):
        """Initializes UI elements based on specification

        Args:
            specification (ToolSpecification): Specification to load
        """
        use_jupyter_console = specification.execution_settings["use_jupyter_console"]
        self.ui.radioButton_jupyter_console.blockSignals(True)
        self.ui.radioButton_python_console.blockSignals(True)
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
        else:
            self.ui.radioButton_python_console.setChecked(True)
        self.ui.radioButton_jupyter_console.blockSignals(False)
        self.ui.radioButton_python_console.blockSignals(False)
        self.set_ui_for_jupyter_console(use_jupyter_console)
        # Must wait until model is built before setting the saved kernel spec as selected
        self._saved_kernel = specification.execution_settings["kernel_spec_name"]
        self.set_executable(specification.execution_settings["executable"])

    def add_execution_settings(self):
        """Collects execution settings based on optional widget state into a dictionary, which is returned."""
        idx = self.ui.comboBox_kernel_specs.currentIndex()
        if idx < 1:
            d = {"kernel_spec_name": "", "env": ""}
        else:
            item = self.ui.comboBox_kernel_specs.model().item(idx)
            k_spec_data = item.data()
            d = k_spec_data
        d["use_jupyter_console"] = self.ui.radioButton_jupyter_console.isChecked()
        self.validate_executable()  # Raises NameError if Python path is not valid
        d["executable"] = self.get_executable()
        return d

    @Slot(bool)
    def browse_python_button_clicked(self, _=False):
        """Calls static method that shows a file browser for selecting a Python interpreter."""
        select_python_interpreter(self, self.ui.lineEdit_python_path)
        self._parent.push_change_executable()

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.lineEdit_python_path.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.toolButton_browse_python.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.comboBox_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        self.ui.toolButton_refresh_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        if use_jupyter_console and not self._kernel_spec_model_initialized:
            self.start_kernel_fetcher(restore_saved_kernel=True)

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

    @Slot()
    def start_kernel_fetcher(self, restore_saved_kernel=False):
        """Starts KernelFetcher for Python kernels."""
        if self.kernel_fetcher is not None and self.kernel_fetcher.isRunning():
            return
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        self.initialize_kernel_spec_model()
        conda_path = self._toolbox.qsettings().value("appSettings/condaPath", defaultValue="")
        self.kernel_fetcher = KernelFetcher(conda_path, fetch_mode=2)
        self.kernel_fetcher.kernel_found.connect(self.add_kernel)
        if restore_saved_kernel:
            self.kernel_fetcher.finished.connect(self._restore_saved_kernel)
        else:
            self.kernel_fetcher.finished.connect(self._restore_selected_kernel)
        self.kernel_fetcher.finished.connect(self._toolbox.restore_override_cursor)
        self.kernel_fetcher.start()

    @Slot()
    def stop_fetching_kernels(self):
        """Terminates the kernel fetcher thread."""
        if self.kernel_fetcher is not None:
            self.kernel_fetcher.stop_fetcher.emit()

    @Slot(str, str, bool, QIcon, dict)
    def add_kernel(self, kernel_name, resource_dir, conda, icon, deats):
        """Adds a kernel entry as an item to kernel spec model."""
        if not conda:
            spec_data = {"kernel_spec_name": kernel_name, "env": ""}
            item = QStandardItem(kernel_name)
        else:
            spec_data = {"kernel_spec_name": kernel_name, "env": "conda"}
            item = QStandardItem(kernel_name + " [Conda]")
        item.setIcon(icon)
        item.setData(spec_data)
        self.kernel_spec_model.appendRow(item)

    def initialize_kernel_spec_model(self):
        """Initializes kernel spec model for fetching kernels. Memorizes currently
        selected kernel in order to select it again after the model has been
        refreshed."""
        item = self.kernel_spec_model.item(self.ui.comboBox_kernel_specs.currentIndex())
        if not item or not item.data():
            self._selected_kernel = None
        else:
            self._selected_kernel = item.data()["kernel_spec_name"]  # Remember the selected kernel spec
        self.kernel_spec_model.clear()
        first_item = QStandardItem("Select kernel spec...")
        self.kernel_spec_model.appendRow(first_item)

    @Slot()
    def _restore_selected_kernel(self):
        """Sets the previously selected kernel spec as the current item after the model has been refreshed."""
        self._kernel_spec_model_initialized = True
        if self._selected_kernel is not None:
            row = self.find_index_by_data(self._selected_kernel)
            if row == -1:
                # The kernel spec may have been removed
                self._parent.push_change_kernel_spec_command(0)
                return
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)

    @Slot()
    def _restore_saved_kernel(self):
        """Sets index of the kernel spec combobox to show the item that was saved with the Tool Specification.
        Make sure this is called after kernel spec model has been populated."""
        self._kernel_spec_model_initialized = True
        if not self._saved_kernel:
            self.ui.comboBox_kernel_specs.setCurrentIndex(0)  # Set 'Select kernel spec...'
        else:
            row = self.find_index_by_data(self._saved_kernel)
            if row == -1:
                notification = Notification(
                    self._parent,
                    f"This Tool spec has kernel spec '{self._saved_kernel}' " f"saved but it could not be found.",
                )
                notification.show()
                row += 1  # Set 'Select kernel spec...'
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)


class ExecutableToolSpecOptionalWidget(OptionalWidget):
    def __init__(self, parent):
        """
        Args:
            parent (QWidget): parent widget
        """
        from ..ui.executable_cmd_exec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.shells = ["No shell", "cmd.exe", "powershell.exe", "bash"]
        self.ui.comboBox_shell.addItems(self.shells)
        self.connect_signals()

    def connect_signals(self):
        self.ui.lineEdit_command.editingFinished.connect(self._parent.push_change_executable_command)
        self.ui.comboBox_shell.activated.connect(self._parent.push_change_shell_command)

    def init_widget(self, specification):
        """Initializes UI elements based on specification."""
        self.ui.lineEdit_command.setText(specification.execution_settings["cmd"])
        shell = specification.execution_settings["shell"]
        ind = next(iter(k for k, t in enumerate(self.shells) if t.lower() == shell), 0)
        self.ui.comboBox_shell.setCurrentIndex(ind)

    def add_execution_settings(self):
        """Collects execution settings based on optional widget state into a dictionary, which is returned."""
        return {"cmd": self.ui.lineEdit_command.text(), "shell": self.get_current_shell()}

    def get_current_shell(self):
        """Returns the selected shell in the shell combo box."""
        ind = self.ui.comboBox_shell.currentIndex()
        if ind < 1:
            return ""
        return self.ui.comboBox_shell.currentText()
