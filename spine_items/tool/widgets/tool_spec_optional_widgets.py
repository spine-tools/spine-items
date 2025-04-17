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
from PySide6.QtWidgets import QWidget


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

    def get_widgets_in_tab_order(self):
        """Returns widget in tab order.

        Returns:
            Sequence of QWidget: widgets
        """
        raise NotImplementedError()


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
