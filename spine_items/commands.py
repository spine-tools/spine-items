######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
QUndoCommand subclasses for modifying the project.

:authors: M. Marin (KTH)
:date:   12.2.2020
"""

from PySide2.QtWidgets import QUndoCommand


class SpineToolboxCommand(QUndoCommand):
    @staticmethod
    def is_critical():
        """Returns True if this command needs to be undone before
        closing the project without saving changes.
        """
        return False


class SetItemSpecificationCommand(SpineToolboxCommand):
    def __init__(self, item, specification):
        """Command to set the specification for a Tool.

        Args:
            item (ProjectItem): the Item
            specification (ProjectItemSpecification): the new spec
        """
        super().__init__()
        self.item = item
        self.redo_specification = specification
        self.setText(f"set specification of {item.name}")

    def redo(self):
        self.item.do_set_specification(self.redo_specification)

    def undo(self):
        self.item.undo_set_specification()
