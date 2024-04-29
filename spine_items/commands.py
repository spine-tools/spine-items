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

"""Undo/redo commands that can be used by multiple project items."""
from spinetoolbox.project_commands import SpineToolboxCommand


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, item_name, cancel_on_error, project):
        """Command to update Importer, Exporter, and Merger cancel on error setting.

        Args:
            item_name (str): Item's name
            cancel_on_error (bool): New setting
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._item_name = item_name
        self._redo_cancel_on_error = cancel_on_error
        self._undo_cancel_on_error = not cancel_on_error
        self._project = project
        self.setText(f"change {item_name} cancel on error setting")

    def redo(self):
        item = self._project.get_item(self._item_name)
        item.set_cancel_on_error(self._redo_cancel_on_error)

    def undo(self):
        item = self._project.get_item(self._item_name)
        item.set_cancel_on_error(self._undo_cancel_on_error)


class UpdateOnConflictCommand(SpineToolboxCommand):
    def __init__(self, item_name, on_conflict, project):
        """Command to update Importer and Merger 'on conflict' setting.

        Args:
            item_name (str): Item's name
            on_conflict (str): New setting
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._item_name = item_name
        self._redo_on_conflict = on_conflict
        project_item = project.get_item(item_name)
        self._undo_on_conflict = project_item.on_conflict
        self._project = project
        self.setText(f"change {item_name} on conflict setting")

    def redo(self):
        item = self._project.get_item(self._item_name)
        item.set_on_conflict(self._redo_on_conflict)

    def undo(self):
        item = self._project.get_item(self._item_name)
        item.set_on_conflict(self._undo_on_conflict)


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
    def __init__(self, item_name, cmd_line_args, project):
        """Command to update Tool command line args.

        Args:
            item_name (str): item's name
            cmd_line_args (list): list of command line args
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._item_name = item_name
        self._redo_cmd_line_args = cmd_line_args
        item = project.get_item(item_name)
        self._undo_cmd_line_args = item.cmd_line_args
        self._project = project
        self.setText(f"change command line arguments of {item_name}")

    def redo(self):
        item = self._project.get_item(self._item_name)
        item.update_cmd_line_args(self._redo_cmd_line_args)

    def undo(self):
        item = self._project.get_item(self._item_name)
        item.update_cmd_line_args(self._undo_cmd_line_args)


class UpdateGroupIdCommand(SpineToolboxCommand):
    def __init__(self, item_name, group_id, project):
        """Command to update item group identifier.

        Args:
            item_name (str): item's name
            group_id (str): group identifier
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._item_name = item_name
        self._redo_group_id = group_id
        item = project.get_item(item_name)
        self._undo_group_id = item.group_id
        self._project = project
        self.setText(f"change group identifier of {item_name}")

    def redo(self):
        item = self._project.get_item(self._item_name)
        item.do_set_group_id(self._redo_group_id)

    def undo(self):
        item = self._project.get_item(self._item_name)
        item.do_set_group_id(self._undo_group_id)
