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
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QWidget

from spinetoolbox.project_item.specification_editor_window import ChangeSpecPropertyCommand


class OptionalWidget(QWidget):
    """Base class for optional specification widgets."""

    def __init__(self, undo_stack):
        """
        Args:
            undo_stack (QUndoStack): undo stack
        """
        super().__init__()
        self._undo_stack = undo_stack
        self.setAttribute(Qt.WA_DeleteOnClose)

    def init_widget(self, specification):
        """Initializes the widget to given specification.

        Args:
            specification (ToolSpecification): specification
        """
        raise NotImplementedError

    def specification_dict_data(self):
        """Returns additional specification data held by the optional widget.

        Returns:
            dict: additional specification data
        """
        return {}

    def make_restore_data(self):
        """Returns data needed to restore the widget's contents.

        Returns:
            Any: data needed for restore operation
        """
        raise NotImplementedError()

    def restore(self, restore_data):
        """Restores widget's contents.

        Args:
            restore_data (Any): content data
        """
        raise NotImplementedError()


class ExecutableToolSpecOptionalWidget(OptionalWidget):
    """Executable tool specification's optional widget"""

    def __init__(self, undo_stack):
        """
        Args:
            undo_stack (QUndoStack): undo stack
        """
        from ..ui.executable_cmd_exec_options import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(undo_stack)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._ui.lineEdit_command.editingFinished.connect(self._push_change_executable_command)
        self._current_command = ""

    def init_widget(self, specification):
        """See base class."""
        command = specification.command if specification is not None else ""
        self._current_command = command
        self._ui.lineEdit_command.setText(command)

    def specification_dict_data(self):
        """See base class."""
        return {"command": self._current_command}

    @Slot()
    def _push_change_executable_command(self):
        """Pushes a command to undo stack that updates the command."""
        old_command = self._current_command
        new_command = self._ui.lineEdit_command.text().strip()
        if new_command == old_command:
            return
        self._undo_stack.push(ChangeSpecPropertyCommand(self._set_command, new_command, old_command, "change command"))

    def _set_command(self, command):
        """Sets new value to command.

        Args:
            command (str): new command
        """
        self._current_command = command
        self._ui.lineEdit_command.setText(command)

    def make_restore_data(self):
        """See base class."""
        return self._current_command

    def restore(self, restore_data):
        """See base class."""
        self._set_command(restore_data)
