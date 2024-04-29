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

"""Undo/redo commands for the Tool project item."""
import copy
from spine_items.commands import SpineToolboxCommand


class UpdateToolExecuteInWorkCommand(SpineToolboxCommand):
    """Command to update Tool execute_in_work setting."""

    def __init__(self, tool_name, execute_in_work, project):
        """
        Args:
            tool_name (str): Tool's name
            execute_in_work (bool): True or False
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._tool_name = tool_name
        self._execute_in_work = execute_in_work
        self._project = project
        self.setText(f"change execute in work setting of {tool_name}")

    def redo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_execution_mode(self._execute_in_work)

    def undo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_execution_mode(not self._execute_in_work)


class UpdateToolOptionsCommand(SpineToolboxCommand):
    """Command to update Tool options."""

    def __init__(self, tool_name, changed_options, current_options, project):
        """
        Args:
            tool_name (str): Tool's name
            changed_options (dict): The options that change
            current_options (dict): Current options
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._tool_name = tool_name
        self._old_options = copy.deepcopy(current_options)
        self._new_options = copy.deepcopy(current_options)
        self._new_options.update(changed_options)
        self._project = project
        self.setText(f"change options of {tool_name}")

    def redo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_set_options(copy.deepcopy(self._new_options))
        self.setObsolete(self._old_options == self._new_options)

    def undo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_set_options(copy.deepcopy(self._old_options))


class UpdateKillCompletedProcesses(SpineToolboxCommand):
    """Command to update Tool kill_completed_processes flag."""

    def __init__(self, tool_name, kill_completed_processes, project):
        """
        Args:
            tool_name (str): Tool's name
            kill_completed_processes (bool): new flag value
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._tool_name = tool_name
        self._kill_completed_processes = kill_completed_processes
        self._project = project
        self.setText(f"change kill consoles setting of {tool_name}")

    def redo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_kill_completed_processes(self._kill_completed_processes)

    def undo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_kill_completed_processes(not self._kill_completed_processes)


class UpdateLogProcessOutput(SpineToolboxCommand):
    """Command to update Tool log_process_output flag."""

    def __init__(self, tool_name, log_process_output, project):
        """
        Args:
            tool_name (str): Tool's name
            log_process_output (bool): new flag value
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._tool_name = tool_name
        self._log_process_output = log_process_output
        self._project = project
        self.setText(f"change log process output setting of {tool_name}")

    def redo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_log_process_output(self._log_process_output)

    def undo(self):
        tool = self._project.get_item(self._tool_name)
        tool.do_update_log_process_output(not self._log_process_output)
