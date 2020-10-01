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


class MoveIconCommand(SpineToolboxCommand):
    def __init__(self, graphics_item):
        """Command to move icons in the Design view.

        Args:
            graphics_item (ProjectItemIcon): the icon
        """
        super().__init__()
        self.graphics_item = graphics_item
        self.previous_pos = {x: x._previous_pos for x in graphics_item.icon_group}
        self.current_pos = {x: x._current_pos for x in graphics_item.icon_group}
        if len(graphics_item.icon_group) == 1:
            self.setText(f"move {list(graphics_item.icon_group)[0].name()}")
        else:
            self.setText("move multiple items")

    def redo(self):
        for item, current_post in self.current_pos.items():
            item.setPos(current_post)
        self.graphics_item.update_links_geometry()
        self.graphics_item.notify_item_move()

    def undo(self):
        for item, previous_pos in self.previous_pos.items():
            item.setPos(previous_pos)
        self.graphics_item.update_links_geometry()
        self.graphics_item.notify_item_move()


class UpdateCancelOnErrorCommand(SpineToolboxCommand):
    def __init__(self, project_item, cancel_on_error):
        """Command to update Importer, Exporter, and Combiner cancel on error setting.

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
