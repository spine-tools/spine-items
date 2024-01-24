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
Undo/redo commands for the View project item.

"""
from spine_items.commands import SpineToolboxCommand


class PinOrUnpinDBValuesCommand(SpineToolboxCommand):
    """Command to pin or unpin DB values."""

    def __init__(self, view, new_values, old_values):
        """
        Args:
            view (View): the View
            new_values (dict): mapping name to list of value identifiers
            old_values (dict): mapping name to list of value identifiers
        """
        super().__init__()
        self.view = view
        self.new_values = new_values
        self.old_values = old_values
        texts = ["pin" if values else "unpin" + " " + name for name, values in new_values.items()]
        self.setText(f"{', '.join(texts)} in {view.name}")

    def redo(self):
        self.view.do_pin_db_values(self.new_values)

    def undo(self):
        self.view.do_pin_db_values(self.old_values)
