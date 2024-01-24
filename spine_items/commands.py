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
Undo/redo commands that can be used by multiple project items.

"""
from spinetoolbox.project_commands import SpineToolboxCommand


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, project_item, cancel_on_error):
        """Command to update Importer, Exporter, and Merger cancel on error setting.

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


class UpdateOnConflictCommand(SpineToolboxCommand):
    def __init__(self, project_item, on_conflict):
        """Command to update Importer and Merger 'on conflict' setting.

        Args:
            project_item (ProjectItem): Item
            on_conflict (str): New setting
        """
        super().__init__()
        self._project_item = project_item
        self._redo_on_conflict = on_conflict
        self._undo_on_conflict = self._project_item.on_conflict
        self.setText(f"change {project_item.name} on conflict setting")

    def redo(self):
        self._project_item.set_on_conflict(self._redo_on_conflict)

    def undo(self):
        self._project_item.set_on_conflict(self._undo_on_conflict)


class ChangeItemSelectionCommand(SpineToolboxCommand):
    def __init__(self, item_name, model, index, selected):
        """Command to change file item's selection status.

        Args:
            item_name (str): project item's name
            model (FileListModel): File model
            index (QModelIndex): Index to file model
            selected (bool): True if the item is selected, False otherwise
        """
        super().__init__()
        self._model = model
        self._index = index
        self._selected = selected
        self.setText(f"change {item_name} file selection")

    def redo(self):
        self._model.set_checked(self._index, self._selected)

    def undo(self):
        self._model.set_checked(self._index, not self._selected)


class UpdateCmdLineArgsCommand(SpineToolboxCommand):
    def __init__(self, item, cmd_line_args):
        """Command to update Tool command line args.

        Args:
            item (ProjectItemBase): the item
            cmd_line_args (list): list of command line args
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


class UpdateGroupIdCommand(SpineToolboxCommand):
    def __init__(self, item, group_id):
        """Command to update item group identifier.

        Args:
            item (ProjectItemBase): the item
            group_id (str): group identifier
        """
        super().__init__()
        self._item = item
        self._redo_group_id = group_id
        self._undo_group_id = self._item.group_id
        self.setText(f"change group identifier of {item.name}")

    def redo(self):
        self._item.do_set_group_id(self._redo_group_id)

    def undo(self):
        self._item.do_set_group_id(self._undo_group_id)
