######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Undo/redo commands that can be used by multiple project items.

:authors: M. Marin (KTH), P. Savolainen (VTT)
:date:   5.5.2020
"""

from spinetoolbox.project_commands import SpineToolboxCommand


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, project_item, cancel_on_error):
        """Command to update Importer, GdxExporter, and Data Store cancel on error setting.

        Args:
            project_item (ProjectItem): Item
            cancel_on_error (bool): New setting
        """
        super().__init__()
        self._project_item = project_item
        self._redo_cancel_on_error = cancel_on_error
        self._undo_cancel_on_error = not cancel_on_error
        self.setText(f"change {project_item.name} cancel on error setting")

    def redo(self):
        self._project_item.set_cancel_on_error(self._redo_cancel_on_error)

    def undo(self):
        self._project_item.set_cancel_on_error(self._undo_cancel_on_error)


class ChangeItemSelectionCommand(SpineToolboxCommand):
    def __init__(self, project_item, selected, label):
        """Command to change file item's selection status.
        Used by Importers and Gimlets.

        Args:
            project_item (ProjectItem): Item
            selected (bool): True if the item is selected, False otherwise
            label (str): File label
        """
        super().__init__()
        self._item = project_item
        self._selected = selected
        self._label = label
        self.setText(f"change {project_item.name} file selection")

    def redo(self):
        self._item.set_file_selected(self._label, self._selected)

    def undo(self):
        self._item.set_file_selected(self._label, not self._selected)


class UpdateCmdLineArgsCommand(SpineToolboxCommand):
    def __init__(self, item, cmd_line_args):
        """Command to update Tool command line args.

        Args:
            item (ProjectItemBase): the item
            cmd_line_args (list): list of str args
        """
        super().__init__()
        self.item = item
        self.redo_cmd_line_args = cmd_line_args
        self.undo_cmd_line_args = self.item.cmd_line_args
        self.setText(f"change command line arguments of {item.name}")

    def redo(self):
        self.item.update_cmd_line_args(self.redo_cmd_line_args)

    def undo(self):
        self.item.update_cmd_line_args(self.undo_cmd_line_args)
