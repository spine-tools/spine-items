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

"""Contains the :class:`ClassRenamesTableModel` class."""
from enum import IntEnum, unique
import pickle
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from ..commands import InsertRow, SetData
from ..widgets.drop_target_table import DROP_MIME_TYPE


@unique
class ClassTableColumn(IntEnum):
    CLASS = 0
    NEW_NAME = 1


@unique
class RenamesRoles(IntEnum):
    SILENT_EDIT = Qt.ItemDataRole.UserRole + 1


class ClassRenamesTableModel(QAbstractTableModel):
    """A table model for entity class renaming tables."""

    GET_DATA_ROLES = (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DisplayRole)
    SET_DATA_ROLES = (RenamesRoles.SILENT_EDIT, RenamesRoles.SILENT_EDIT)

    def __init__(self, undo_stack, renaming):
        """
        Args:
            undo_stack (QUndoStack)
            renaming (dict): renaming settings
        """
        super().__init__()
        self._undo_stack = undo_stack
        self._renames = [[original, renamed] for original, renamed in renaming.items()]

    def columnCount(self, parent=QModelIndex()):
        """
        Returns:
            int: number of columns
        """
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """Returns table data for given role."""
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._renames[index.row()][index.column()]
        return None

    def dropMimeData(self, data, action, row, column, parent):
        if row < 0:
            row = self.rowCount()
        classes = pickle.loads(data.data(DROP_MIME_TYPE))
        rows = [[klass, ""] for klass in classes]
        if len(rows) == 1:
            self._undo_stack.push(InsertRow("add class", self, row, rows[0]))
        else:
            self._undo_stack.beginMacro("add classes")
            for i, row_data in enumerate(rows):
                self._undo_stack.push(InsertRow("", self, row + i, row_data))
            self._undo_stack.endMacro()
        return True

    def mimeTypes(self):
        return [DROP_MIME_TYPE]

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsDropEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Returns header data."""
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ("Original", "Renamed")[section]
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        rows = count * [["", ""]]
        self.beginInsertRows(parent, row, row + count - 1)
        self._renames = self._renames[:row] + rows + self._renames[row:]
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._renames = self._renames[:row] + self._renames[row + count :]
        self.endRemoveRows()
        return True

    def renaming_settings(self):
        return {row[ClassTableColumn.CLASS]: row[ClassTableColumn.NEW_NAME] for row in self._renames}

    def rowCount(self, parent=QModelIndex()):
        """
        Returns:
            int: number of rows
        """
        return len(self._renames)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        column = index.column()
        if role == Qt.ItemDataRole.EditRole:
            old_value = self._renames[index.row()][column]
            if value == old_value:
                return False
            message = "change class name" if column == ClassTableColumn.CLASS else "change new class name"
            self._undo_stack.push(SetData(message, index, value, old_value, RenamesRoles.SILENT_EDIT))
            return True
        if role == RenamesRoles.SILENT_EDIT:
            self._renames[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False
