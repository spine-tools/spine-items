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
from collections.abc import Callable
from enum import IntEnum
from PySide6.QtCore import QModelIndex
from spine_engine.project_item.project_item_resource import CmdLineArg
from spinetoolbox.project import SpineToolboxProject
from spinetoolbox.project_commands import SpineToolboxCommand
from .models import CheckableFileListModel


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, item_name: str, cancel_on_error: bool, project: SpineToolboxProject):
        """Command to update Importer, Exporter, and Merger cancel on error setting.

        Args:
            item_name: Item's name
            cancel_on_error: New setting
            project: project
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
    def __init__(self, item_name: str, on_conflict: str, project: SpineToolboxProject):
        """Command to update Importer and Merger 'on conflict' setting.

        Args:
            item_name: Item's name
            on_conflict: New setting
            project: project
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
    def __init__(self, item_name: str, model: CheckableFileListModel, index: QModelIndex, selected: bool):
        """Command to change file item's selection status.

        Args:
            item_name: project item's name
            model: File model
            index : Index to file model
            selected: True if the item is selected, False otherwise
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
    def __init__(self, item_name: str, cmd_line_args: list[CmdLineArg], project: SpineToolboxProject):
        """Command to update Tool command line args.

        Args:
            item_name: item's name
            cmd_line_args: list of command line args
            project: project
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
    def __init__(self, item_name: str, group_id: str, project: SpineToolboxProject):
        """Command to update item group identifier.

        Args:
            item_name: item's name
            group_id: group identifier
            project: project
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


class UpdateRootDirCommand(SpineToolboxCommand):
    def __init__(self, item_name: str, root_dir: str, project: SpineToolboxProject):
        """Command to update Tool root directory.

        Args:
            item_name: Item's name
            root_dir: Root directory
            project: Project
        """
        super().__init__()
        self._item_name = item_name
        self._redo_root_dir = root_dir
        item = project.get_item(item_name)
        self._undo_root_dir = item.root_dir
        self._project = project
        self.setText(f"change root directory of {item_name}")

    def redo(self):
        item = self._project.get_item(self._item_name)
        item.do_set_root_directory(self._redo_root_dir)

    def undo(self):
        item = self._project.get_item(self._item_name)
        item.do_set_root_directory(self._undo_root_dir)


class UpdateText(SpineToolboxCommand):
    def __init__(
        self,
        item_name: str,
        new: str,
        old: str,
        command_text: str,
        command_id: int,
        update_callback_name: str,
        project: SpineToolboxProject,
    ):
        """Command to update a textual setting.

        Args:
            item_name: Item's name.
            new: Updated text.
            old: Previous text.
            command_text: Undo command's text.
            command_id: Command's id.
            update_callback_name: Name of the callback to call on the item to update the text.
            project: Project instance.
        """
        super().__init__()
        self._item_name = item_name
        self._is_sealed = False
        self._new = new
        self._old = old
        self._id = command_id
        self._update_callback_name = update_callback_name
        self._project = project
        self.setText(command_text)

    def id(self):
        return self._id

    def mergeWith(self, other):
        if not isinstance(other, UpdateText):
            self._is_sealed = True
            return False
        if self._is_sealed or self._id != other._id:
            return False
        if self._old == other._new:
            self.setObsolete(True)
        else:
            self._new = other._new
        return True

    def redo(self):
        item = self._project.get_item(self._item_name)
        set_text = getattr(item, self._update_callback_name)
        set_text(self._new)

    def undo(self):
        item = self._project.get_item(self._item_name)
        set_text = getattr(item, self._update_callback_name)
        set_text(self._old)
