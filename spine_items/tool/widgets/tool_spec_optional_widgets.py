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

"""Provides an optional widget for Tool Specification Editor when editing Julia, Python, or Executable Tool Specs."""
import sys
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import Qt, QStandardItemModel, QStandardItem, QIcon
from spine_engine.utils.helpers import resolve_default_julia_executable, resolve_python_interpreter
from spinetoolbox.helpers import file_is_valid, select_python_interpreter, select_julia_executable, select_julia_project
from spinetoolbox.widgets.notification import Notification
from spinetoolbox.kernel_fetcher import KernelFetcher


class OptionalWidget(QWidget):
    def __init__(self, specification_editor, toolbox):
        """
        Args:
            specification_editor (ToolSpecificationEditorWindow): Tool spec editor window
            toolbox (ToolboxUI): Toolbox main window
        """
        super().__init__()
        self._toolbox = toolbox
        self._specification_editor = specification_editor

    def init_widget(self, specification):
        raise NotImplementedError()

    def add_execution_settings(self, tool_spec_type):
        """Collects execution settings based on optional widget state into a dictionary, which is returned.

        Args:
            tool_spec_type (str): Tool spec type
        """
        raise NotImplementedError()

    def default_execution_settings(self):
        """Returns default execution settings dictionary."""
        raise NotImplementedError()

    def get_widgets_in_tab_order(self):
        """Returns widget in tab order.

        Returns:
            Sequence of QWidget: widgets
        """
        raise NotImplementedError()


class SharedToolSpecOptionalWidget(OptionalWidget):
    """Superclass for Python and Julia Tool Spec optional widgets."""

    def __init__(self, specification_editor, toolbox, Ui_Form, fetch_mode):
        """
        Args:
            specification_editor (ToolSpecificationEditorWindow): Tool spec editor window
            toolbox (ToolboxUI): Toolbox main window
            Ui_Form (Form): Optional widget UI form
            fetch_mode (int): Kernel fetch mode (see KernelFetcher class)
        """
        super().__init__(specification_editor, toolbox)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.fetch_mode = fetch_mode
        self.conda_path = self._toolbox.qsettings().value("appSettings/condaPath", defaultValue="")
        self.kernel_spec_model = QStandardItemModel(self)
        self.ui.comboBox_kernel_specs.setModel(self.kernel_spec_model)
        self._kernel_spec_editor = None
        self._kernel_spec_model_initialized = False
        self._saved_kernel = None
        self._selected_kernel = None
        self.kernel_fetcher = None

    def connect_signals(self):
        """Connects signals."""
        self.ui.toolButton_refresh_kernel_specs.clicked.connect(self.start_kernel_fetcher)
        self.ui.comboBox_kernel_specs.activated.connect(self._specification_editor.push_change_kernel_spec_command)
        self.ui.radioButton_jupyter_console.toggled.connect(self._specification_editor.push_set_jupyter_console_mode)
        self.ui.lineEdit_executable.textEdited.connect(self._specification_editor.push_change_executable)
        self.ui.lineEdit_executable.editingFinished.connect(self._specification_editor.finish_changing_executable)
        qApp.aboutToQuit.connect(self.stop_fetching_kernels)  # pylint: disable=undefined-variable

    def init_widget(self, specification):
        """Initializes UI elements based on specification

        Args:
            specification (ToolSpecification): Specification to load
        """
        use_jupyter_console = specification.execution_settings["use_jupyter_console"]
        self.ui.radioButton_jupyter_console.blockSignals(True)
        self.ui.radioButton_basic_console.blockSignals(True)
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
        else:
            self.ui.radioButton_basic_console.setChecked(True)
        self.ui.radioButton_jupyter_console.blockSignals(False)
        self.ui.radioButton_basic_console.blockSignals(False)
        self._saved_kernel = specification.execution_settings["kernel_spec_name"]
        self.set_executable(specification.execution_settings["executable"])
        self.set_ui_for_jupyter_console(use_jupyter_console)

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.lineEdit_executable.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.comboBox_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        self.ui.toolButton_refresh_kernel_specs.setEnabled(use_jupyter_console)  # Enable for jupyter console
        if use_jupyter_console and not self._kernel_spec_model_initialized:
            self.start_kernel_fetcher(restore_saved_kernel=True)

    def add_execution_settings(self, tool_spec_type):
        """See base class."""
        idx = self.ui.comboBox_kernel_specs.currentIndex()
        if idx < 1:
            d = {"kernel_spec_name": "", "env": ""}
        else:
            item = self.ui.comboBox_kernel_specs.model().item(idx)
            k_spec_data = item.data()
            d = k_spec_data
        d["use_jupyter_console"] = self.ui.radioButton_jupyter_console.isChecked()
        p = self.get_executable()
        self.validate_executable(p, tool_spec_type)  # Raises NameError if Python or Julia path is not valid
        d["executable"] = p
        return d

    def validate_executable(self, p, tool_spec_type):
        """Check that given Python or Julia path is a file, it exists, and the
        file name starts with either 'python' or 'julia'.

        Args:
            p (str): Abs. path to check
            tool_spec_type (str): 'python' or 'julia'

        Raises:
            NameError: If the python path in the line edit is not valid
        """
        if not file_is_valid(
            self._specification_editor,
            p,
            f"Invalid {tool_spec_type.capitalize()} Interpreter",
            extra_check=tool_spec_type,
        ):
            raise NameError

    def set_executable(self, p):
        """Sets given path p to either Python or Julia line edit."""
        if p == self.get_executable():
            return
        self.ui.lineEdit_executable.setText(p)

    def get_executable(self):
        """Returns either Python or Julia executable path."""
        return self.ui.lineEdit_executable.text().strip()

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
        """Initializes kernel spec model and starts KernelFetcher.

        Args:
            restore_saved_kernel (bool): True restores a saved kernel after the model has been refreshed,
            False restores the selected kernel after the model has been refreshed.
        """
        if self.kernel_fetcher is not None and self.kernel_fetcher.isRunning():
            return
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        self.initialize_kernel_spec_model()
        self.kernel_fetcher = KernelFetcher(self.conda_path, fetch_mode=self.fetch_mode)
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
                self._specification_editor.push_change_kernel_spec_command(0)
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
                    self._specification_editor,
                    f"This Tool spec has kernel spec '{self._saved_kernel}' " f"saved but it could not be found.",
                )
                notification.show()
                row += 1  # Set 'Select kernel spec...'
            self.ui.comboBox_kernel_specs.setCurrentIndex(row)


class PythonToolSpecOptionalWidget(SharedToolSpecOptionalWidget):
    def __init__(self, specification_editor, toolbox):
        """
        Args:
            specification_editor (ToolSpecificationEditorWindow): Tool spec editor window
            toolbox (ToolboxUI): Toolbox main window
        """
        from ..ui.python_kernel_spec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(specification_editor, toolbox, Ui_Form, 2)
        # Initialize UI elements with defaults
        use_jupyter_console = bool(
            int(self._toolbox.qsettings().value("appSettings/usePythonKernel", defaultValue="0"))
        )
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
            # Get the default kernel spec from Settings->Tools for new Jupyter Console Tool Specs
            self._saved_kernel = self._toolbox.qsettings().value("appSettings/pythonKernel", defaultValue="")
        else:
            self.ui.radioButton_basic_console.setChecked(True)
        default_python_path = resolve_python_interpreter(self._toolbox.qsettings())
        self.ui.lineEdit_executable.setPlaceholderText(default_python_path)
        self.set_ui_for_jupyter_console(use_jupyter_console)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals to slots."""
        super().connect_signals()
        self.ui.toolButton_browse_python.clicked.connect(self.browse_python_button_clicked)

    def add_execution_settings(self, tool_spec_type):
        """See base class."""
        return super().add_execution_settings(tool_spec_type)

    def default_execution_settings(self):
        """See base class."""
        use_jupyter_cons = bool(int(self._toolbox.qsettings().value("appSettings/usePythonKernel", defaultValue="0")))
        k_name = self._toolbox.qsettings().value("appSettings/pythonKernel", defaultValue="")
        env = ""
        if use_jupyter_cons:
            # Check if the kernel is a Conda kernel by matching the name with the one that is in kernel_spec_model
            # Find k_name in kernel_spec_model and check it's data
            row = self.find_index_by_data(k_name)
            if row == -1:
                pass  # kernel not found
            else:
                index = self.kernel_spec_model.index(row, 0)
                item_data = self.kernel_spec_model.itemFromIndex(index).data()
                env = item_data["env"]
        d = dict()
        d["kernel_spec_name"] = k_name
        d["env"] = env
        d["use_jupyter_console"] = use_jupyter_cons
        d["executable"] = self._toolbox.qsettings().value("appSettings/pythonPath", defaultValue="")
        return d

    @Slot(bool)
    def browse_python_button_clicked(self, _=False):
        """Calls static method that shows a file browser for selecting a Python interpreter."""
        select_python_interpreter(self, self.ui.lineEdit_executable)
        self._specification_editor.push_change_executable(self.get_executable())
        self._specification_editor.finish_changing_executable()

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """
        self.ui.toolButton_browse_python.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        super().set_ui_for_jupyter_console(use_jupyter_console)

    def get_widgets_in_tab_order(self):
        """See base class."""
        return (
            self.ui.radioButton_basic_console,
            self.ui.radioButton_jupyter_console,
            self.ui.lineEdit_executable,
            self.ui.toolButton_browse_python,
            self.ui.comboBox_kernel_specs,
            self.ui.toolButton_refresh_kernel_specs,
        )


class JuliaToolSpecOptionalWidget(SharedToolSpecOptionalWidget):
    def __init__(self, specification_editor, toolbox):
        """
        Args:
            specification_editor (ToolSpecificationEditorWindow): Tool spec editor window
            toolbox (ToolboxUI): Toolbox main window
        """
        from ..ui.julia_kernel_spec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(specification_editor, toolbox, Ui_Form, 4)
        # Initialize UI elements with defaults
        use_jupyter_console = bool(int(self._toolbox.qsettings().value("appSettings/useJuliaKernel", defaultValue="0")))
        if use_jupyter_console:
            self.ui.radioButton_jupyter_console.setChecked(True)
            # Get the default kernel spec from Settings->Tools for new Jupyter Console Tool Specs
            self._saved_kernel = self._toolbox.qsettings().value("appSettings/juliaKernel", defaultValue="")
        else:
            self.ui.radioButton_basic_console.setChecked(True)
        default_julia_path = self._toolbox.qsettings().value("appSettings/juliaPath", defaultValue="")
        default_julia_project = self._toolbox.qsettings().value("appSettings/juliaProjectPath", defaultValue="")
        if not default_julia_path:
            default_julia_path = resolve_default_julia_executable()
        self.ui.lineEdit_executable.setPlaceholderText(default_julia_path)
        self.ui.lineEdit_julia_project.setText(default_julia_project)
        self.set_ui_for_jupyter_console(use_jupyter_console)
        self.connect_signals()

    def connect_signals(self):
        """Connects signals."""
        super().connect_signals()
        self.ui.toolButton_browse_julia.clicked.connect(self.browse_julia_button_clicked)
        self.ui.toolButton_browse_julia_project.clicked.connect(self.browse_julia_project_button_clicked)
        self.ui.lineEdit_julia_project.editingFinished.connect(self._specification_editor.push_change_project)

    def init_widget(self, specification):
        """Initializes UI elements based on specification

        Args:
            specification (ToolSpecification): Specification to load
        """
        project = specification.execution_settings["project"]
        self.ui.lineEdit_julia_project.setText(project)
        super().init_widget(specification)

    def add_execution_settings(self, tool_spec_type):
        """See base class."""
        d = super().add_execution_settings(tool_spec_type)
        d["project"] = self.get_julia_project()
        return d

    def default_execution_settings(self):
        """See base class."""
        d = dict()
        use_jupyter_console = bool(int(self._toolbox.qsettings().value("appSettings/useJuliaKernel", defaultValue="0")))
        d["kernel_spec_name"] = self._toolbox.qsettings().value("appSettings/juliaKernel", defaultValue="")
        d["env"] = ""
        d["use_jupyter_console"] = use_jupyter_console
        d["executable"] = self._toolbox.qsettings().value("appSettings/juliaPath", defaultValue="")
        d["project"] = self._toolbox.qsettings().value("appSettings/juliaProjectPath", defaultValue="")
        return d

    @Slot(bool)
    def browse_julia_button_clicked(self, _=False):
        """Calls static method that shows a file browser for selecting a Julia executable."""
        select_julia_executable(self, self.ui.lineEdit_executable)
        self._specification_editor.push_change_executable(self.get_executable())

    @Slot(bool)
    def browse_julia_project_button_clicked(self, _=False):
        """Calls static method that shows a file browser for selecting a Julia project."""
        select_julia_project(self, self.ui.lineEdit_julia_project)
        self._specification_editor.push_change_project()

    def set_ui_for_jupyter_console(self, use_jupyter_console):
        """Enables or disables some UI elements in the optional widget according to a checkBox state.

        Args:
            use_jupyter_console (bool): True when Jupyter Console checkBox is checked, false otherwise
        """

        self.ui.lineEdit_julia_project.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.toolButton_browse_julia.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        self.ui.toolButton_browse_julia_project.setEnabled(not use_jupyter_console)  # Disable for jupyter console
        super().set_ui_for_jupyter_console(use_jupyter_console)

    def set_julia_project(self, p):
        """Sets given Julia project to Julia project line edit."""
        self.ui.lineEdit_julia_project.setText(p)

    def get_julia_project(self):
        """Returns Julia project from line edit."""
        return self.ui.lineEdit_julia_project.text().strip()

    def get_widgets_in_tab_order(self):
        """See base class."""
        return (
            self.ui.radioButton_basic_console,
            self.ui.radioButton_jupyter_console,
            self.ui.lineEdit_executable,
            self.ui.toolButton_browse_julia,
            self.ui.lineEdit_julia_project,
            self.ui.toolButton_browse_julia_project,
            self.ui.comboBox_kernel_specs,
            self.ui.toolButton_refresh_kernel_specs,
        )


class ExecutableToolSpecOptionalWidget(OptionalWidget):
    def __init__(self, specification_editor, toolbox):
        """
        Args:
            specification_editor (ToolSpecificationEditorWindow): tool specification editor window
            toolbox (ToolboxUI): Toolbox main window
        """
        from ..ui.executable_cmd_exec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(specification_editor, toolbox)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.shells = ["No shell", "cmd.exe", "powershell.exe", "bash"]
        self.ui.comboBox_shell.addItems(self.shells)
        # Disable shell selections that are not compatible with the os running toolbox
        msg = f"<p>Selection not available for platform {sys.platform}</p>"
        if sys.platform == "win32":
            # No bash for windows
            self.ui.comboBox_shell.model().item(3).setEnabled(False)
            self.ui.comboBox_shell.model().item(3).setToolTip(msg)
        else:
            # For other systems no cmd or powershell
            self.ui.comboBox_shell.model().item(1).setEnabled(False)
            self.ui.comboBox_shell.model().item(1).setToolTip(msg)
            self.ui.comboBox_shell.model().item(2).setEnabled(False)
            self.ui.comboBox_shell.model().item(2).setToolTip(msg)
        self.connect_signals()

    def connect_signals(self):
        self.ui.lineEdit_command.textEdited.connect(self._specification_editor.push_change_executable_command)
        self.ui.lineEdit_command.editingFinished.connect(self._specification_editor.finish_changing_executable)
        self.ui.comboBox_shell.activated.connect(self._specification_editor.push_change_shell_command)

    def init_widget(self, specification):
        """Initializes UI elements based on specification."""
        self.ui.lineEdit_command.setText(specification.execution_settings["cmd"])
        shell = specification.execution_settings["shell"]
        ind = next(iter(k for k, t in enumerate(self.shells) if t.lower() == shell), 0)
        self.ui.comboBox_shell.setCurrentIndex(ind)

    def add_execution_settings(self, tool_spec_type):
        """See base class."""
        return {"cmd": self.ui.lineEdit_command.text(), "shell": self.get_current_shell()}

    def get_current_shell(self):
        """Returns the selected shell in the shell combo box."""
        ind = self.ui.comboBox_shell.currentIndex()
        if ind < 1:
            return ""
        return self.ui.comboBox_shell.currentText()

    def set_command_and_shell_edit_disabled_state(self, enabled):
        """Sets the enabled state for the Command -text editor and the Shell -combobox"""
        self.ui.comboBox_shell.setDisabled(enabled)
        self.ui.lineEdit_command.setDisabled(enabled)

    def get_widgets_in_tab_order(self):
        """See base class."""
        return (
            self.ui.lineEdit_command,
            self.ui.comboBox_shell,
        )
