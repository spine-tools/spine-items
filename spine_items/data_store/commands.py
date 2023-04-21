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
Undo/redo commands for the DataStore project item.

"""
from enum import IntEnum, unique
from spine_items.commands import SpineToolboxCommand


@unique
class CommandId(IntEnum):
    UPDATE_URL = 1


class UpdateDSURLCommand(SpineToolboxCommand):
    def __init__(self, ds, was_url_valid, **kwargs):
        """Command to update DS url.

        Args:
            ds (DataStore): the DS
            was_url_valid (bool): True if previous URL was valid, False otherwise
            kwargs: url keys and their values
        """
        super().__init__()
        self.ds = ds
        self._undo_url_is_valid = was_url_valid
        self.redo_kwargs = kwargs
        self.undo_kwargs = {k: self.ds.url()[k] for k in kwargs}
        if len(kwargs) == 1:
            self.setText(f"change {list(kwargs.keys())[0]} of {ds.name}")
        else:
            self.setText(f"change url of {ds.name}")

    def id(self):
        return CommandId.UPDATE_URL.value

    def mergeWith(self, command):
        if not isinstance(command, UpdateDSURLCommand) or self.ds is not command.ds or command._undo_url_is_valid:
            return False
        diff_key = None
        for key, value in self.redo_kwargs.items():
            old_value = self.undo_kwargs[key]
            if value != old_value:
                if diff_key is not None:
                    return False
                diff_key = key
                break
        else:
            raise RuntimeError("Logic error: nothing changes between undo and redo URLs.")
        if diff_key == "dialect":
            return False
        changed_value = command.redo_kwargs[diff_key]
        if self.redo_kwargs[diff_key] == changed_value:
            return False
        self.redo_kwargs[diff_key] = changed_value
        if self.redo_kwargs[diff_key] == self.undo_kwargs[diff_key]:
            self.setObsolete(True)
        return True

    def redo(self):
        self.ds.do_update_url(**self.redo_kwargs)

    def undo(self):
        self.ds.do_update_url(**self.undo_kwargs)
