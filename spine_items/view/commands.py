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

"""Undo/redo commands for the View project item."""
from copy import deepcopy
from spine_items.commands import SpineToolboxCommand


class PinOrUnpinDBValuesCommand(SpineToolboxCommand):
    """Command to pin or unpin DB values."""

    def __init__(self, view_name, new_values, old_values, project):
        """
        Args:
            view_name (str): View's name
            new_values (dict): mapping name to list of value identifiers
            old_values (dict): mapping name to list of value identifiers
            project (SpineToolboxProject): project
        """
        super().__init__()
        self._view_name = view_name
        self._new_values = deepcopy(new_values)
        self._old_values = deepcopy(old_values)
        self._project = project
        texts = ["pin" if values else "unpin" + " " + name for name, values in new_values.items()]
        self.setText(f"{', '.join(texts)} in {view_name}")

    def redo(self):
        view = self._project.get_item(self._view_name)
        view.do_pin_db_values(deepcopy(self._new_values))

    def undo(self):
        view = self._project.get_item(self._view_name)
        view.do_pin_db_values(deepcopy(self._old_values))
