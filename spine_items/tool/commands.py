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
    def __init__(self, tool, execute_in_work):
        """Command to update Tool execute_in_work setting.

        Args:
            tool (Tool): the Tool
            execute_in_work (bool): True or False
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
    def __init__(self, tool, options):
        """Command to update Tool options.

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


class ChangeToolSpecPropertyCommand(QUndoCommand):
    def __init__(self, callback, new_value, old_value, cmd_name):
        super().__init__()
        self._callback = callback
        self._new_value = new_value
        self._old_value = old_value
        self.setText(cmd_name)
        self.setObsolete(new_value == old_value)

    def redo(self):
        self._callback(self._new_value)

    def undo(self):
        self._callback(self._old_value)
