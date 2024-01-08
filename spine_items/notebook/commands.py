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
from spine_items.commands import SpineToolboxCommand


class UpdateToolExecuteInWorkCommand(SpineToolboxCommand):
    def __init__(self, notebook, execute_in_work):
        """Command to update Tool execute_in_work setting.

        Args:
            notebook (Notebook): the Notebook
            execute_in_work (bool): True or False
        """
        super().__init__()
        self.notebook = notebook
        self.execute_in_work = execute_in_work
        self.setText(f"change execute in work setting of {notebook.name}")

    def redo(self):
        self.notebook.do_update_execution_mode(self.execute_in_work)

    def undo(self):
        self.notebook.do_update_execution_mode(not self.execute_in_work)
