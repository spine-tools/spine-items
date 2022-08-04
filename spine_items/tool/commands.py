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
Undo/redo commands for the Tool project item.

:authors: M. Marin (KTH)
:date:   5.5.2020
"""
import copy

from PySide2.QtWidgets import QUndoCommand

from spine_items.commands import SpineToolboxCommand


class UpdateToolExecuteInWorkCommand(SpineToolboxCommand):
    """Command to update Tool execute_in_work setting."""

    def __init__(self, tool, execute_in_work):
        """
        Args:
            tool (Tool): the Tool
            execute_in_work (bool): new value for the execute_in_work flag
        """
        super().__init__()
        self.tool = tool
        self.execute_in_work = execute_in_work
        self.setText(f"change execute in work setting of {tool.name}")

    def redo(self):
        self.tool.do_update_execution_mode(self.execute_in_work)

    def undo(self):
        self.tool.do_update_execution_mode(not self.execute_in_work)


class UpdateToolOptionsCommand(SpineToolboxCommand):
    """Command to update Tool options."""

    def __init__(self, tool, options):
        """
        Args:
            tool (Tool): the Tool
            options (dict): The options that change
        """
        super().__init__()
        self.tool = tool
        self.old_options = copy.deepcopy(self.tool._options)
        self.new_options = copy.deepcopy(self.tool._options)
        self.new_options.update(options)
        self.setText(f"change options of {tool.name}")

    def redo(self):
        self.tool.do_set_options(self.new_options)
        self.setObsolete(self.old_options == self.new_options)

    def undo(self):
        self.tool.do_set_options(self.old_options)


class SetExecutionSetting(SpineToolboxCommand):
    """Command to set execution settings for Tools."""

    def __init__(self, text, execution_settings, value, previous_value, callback):
        """
        Args:
            text (str): command's descriptive text
            execution_settings (dict): execution settings
            value (Any): new setting
            previous_value (Any): setting's previous value
            callback (Callable): function to call when undoing/redoing
        """
        super().__init__()
        self._execution_settings = execution_settings
        self._value = value
        self._previous_value = previous_value
        self._callback = callback
        self.setText(text)

    def redo(self):
        self._callback(self._execution_settings, self._value)

    def undo(self):
        self._callback(self._execution_settings, self._previous_value)


class StoreExecutionSettings(SpineToolboxCommand):
    """Restores execution settings upon undo.

    Not very useful in itself, but handy in undo macros.
    """

    def __init__(self, tool, execution_settings):
        """
        Args:
            tool (Tool): tool
            execution_settings (dict): execution settings
        """
        super().__init__()
        self.setText("store execution settings")
        self._tool = tool
        self._settings = execution_settings

    def redo(self):
        pass

    def undo(self):
        self._tool.set_execution_settings(self._settings)


class StoreOptionalWidgetContents(QUndoCommand):
    """Restores Tool specification editor window's optional widget's contents upon undo.

    Not very useful in itself, but handy in undo macros where one wants to restore
    optional widget contents e.g. after tool type change.
    """

    def __init__(self, optional_widget):
        """
        Args:
            optional_widget (OptionalWidget): optional widget
        """
        super().__init__("clear options")
        self._optional_widget = optional_widget
        self._undo_data = None

    def redo(self):
        self._undo_data = self._optional_widget.make_restore_data()

    def undo(self):
        self._optional_widget.restore(self._undo_data)
