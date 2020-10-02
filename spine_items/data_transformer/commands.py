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
Contains undo commands for Data Transformer.

:authors: A. Soininen (VTT)
:date:    5.10.2020
"""
from spinetoolbox.project_commands import SpineToolboxCommand


class SetSpecification(SpineToolboxCommand):
    """Sets Data transformer's specification."""

    def __init__(self, transformer, specification_name, previous_name):
        """
        Args:
            transformer (DataTransformer): target project item
            specification_name (str): new specification's name
            previous_name (str): previous specification's name
        """
        super().__init__(f"set specification of {transformer.name}")
        self._transformer = transformer
        self._specification_name = specification_name
        self._previous_name = previous_name

    def redo(self):
        """Sets the specification."""
        self._transformer.set_specification(self._specification_name)

    def undo(self):
        """Resets the specification."""
        self._transformer.set_specification(self._previous_name)
