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
Undo/redo commands for the Tool project item.

"""
import copy
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


class UpdateKillCompletedProcesses(SpineToolboxCommand):
    def __init__(self, tool, kill_completed_processes):
        """Command to update Tool kill_completed_processes flag.

        Args:
            tool (Tool): the Tool
            kill_completed_processes (bool): new flag value
        """
        super().__init__()
        self._tool = tool
        self._kill_completed_processes = kill_completed_processes
        self.setText(f"change kill consoles setting of {tool.name}")

    def redo(self):
        self._tool.do_update_kill_completed_processes(self._kill_completed_processes)

    def undo(self):
        self._tool.do_update_kill_completed_processes(not self._kill_completed_processes)


class UpdateLogProcessOutput(SpineToolboxCommand):
    def __init__(self, tool, log_process_output):
        """Command to update Tool log_process_output flag.

        Args:
            tool (Tool): the Tool
            log_process_output (bool): new flag value
        """
        super().__init__()
        self._tool = tool
        self._log_process_output = log_process_output
        self.setText(f"change log process output setting of {tool.name}")

    def redo(self):
        self._tool.do_update_log_process_output(self._log_process_output)

    def undo(self):
        self._tool.do_update_log_process_output(not self._log_process_output)
