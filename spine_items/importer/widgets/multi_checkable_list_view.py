######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains :class:`MultiCheckableListView`.

"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListView


class MultiCheckableListView(QListView):
    """A list view which allows all selected items to be checked/unchecked with space bar."""

    def keyPressEvent(self, event):
        """Handles key press events."""
        if event.key() != Qt.Key_Space or event.modifiers() != Qt.NoModifier:
            super().keyPressEvent(event)
            return
        selection_model = self.selectionModel()
        if not selection_model.hasSelection():
            super().keyPressEvent(event)
            return
        selected = selection_model.selectedIndexes()
        model = self.model()
        if len(selected) == 1:
            check_state = (
                Qt.CheckState.Checked
                if selected[0].data(Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked.value
                else Qt.CheckState.Unchecked
            )
            model.setData(selected[0], check_state, Qt.ItemDataRole.CheckStateRole)
        else:
            model.toggle_checked_tables(selected)
