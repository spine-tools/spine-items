######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains mapping position editor.

:author: A. Soininen (VTT)
:date:   5.1.2021
"""
from PySide2.QtCore import QTimer, Slot
from PySide2.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate


_positions = ["hidden", "table name", "single row"]


class PositionEditDelegate(QStyledItemDelegate):
    """Custom delegate for editing positions."""

    def createEditor(self, parent, option, index):
        return _PositionEdit(parent)

    def setEditorData(self, editor, index):
        model = index.model()
        editor.set_table_name_item_disabled(model.has_table_name())
        editor.set_single_row_item_disabled(index.row() != model.rowCount() - 1)
        editor.set(index.data())


class _PositionEdit(QComboBox):
    def __init__(self, parent):
        """
        Args:
            parent (QWidget): parent widget
        """
        super().__init__(parent)
        self.addItems(_positions)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.currentTextChanged.connect(self._insert)
        self.setLineEdit(SelectingLineEdit())

    def set_table_name_item_disabled(self, disabled):
        """Disables or enables the 'table name' item.

        Args:
            disabled (bool): True to disable the item, False to enable it
        """
        model = self.model()
        model.item(len(_positions) - 2).setEnabled(not disabled)

    def set_single_row_item_disabled(self, disabled):
        """Disables or enables the 'table name' item.

        Args:
            disabled (bool): True to disable the item, False to enable it
        """
        model = self.model()
        model.item(len(_positions) - 1).setEnabled(not disabled)

    @Slot(str)
    def _insert(self, text):
        """
        Inserts new text item at the top of the box or replaces the current item.

        Args:
            text (str): text to insert
        """
        if text not in _positions:
            if self.count() == len(_positions):
                self.insertItem(0, text)
            else:
                self.setItemText(0, text)

    def set(self, position):
        """
        Sets the combo boxes value.

        Args:
            position (Position or str): position
        """
        if not position.isdigit():
            self.setCurrentText(position)
        else:
            self._insert(position)
            self.setCurrentIndex(0)


class SelectingLineEdit(QLineEdit):
    """Line editor that selects all text when focussed."""

    def focusInEvent(self, e):
        super().focusInEvent(e)
        QTimer.singleShot(0, self.selectAll)
