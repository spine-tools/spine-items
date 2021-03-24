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
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate, QStyle, QStyleOptionComboBox


_positions = ["hidden", "table name"]


def position_section_width():
    # pylint: disable=undefined-variable
    fm = qApp.fontMetrics()
    style = qApp.style()
    option = QStyleOptionComboBox()
    rect = style.subControlRect(QStyle.CC_ComboBox, option, QStyle.SC_ComboBoxArrow)
    return max(fm.horizontalAdvance(pos) for pos in _positions) + rect.width()


class PositionEditDelegate(QStyledItemDelegate):
    """Custom delegate for editing positions."""

    def createEditor(self, parent, option, index):
        return _PositionEdit(parent)

    def setEditorData(self, editor, index):
        model = index.model()
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
        self.selectAll()
        super().focusInEvent(e)
