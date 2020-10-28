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
Contains the :class:`RenameTableModel` class.

:author: A. Soininen (VTT)
:date:   5.10.2020
"""
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QFont


class RenameTableModel(QAbstractTableModel):
    """A table model for database item renaming tables."""

    def __init__(self, renaming):
        """
        Args:
            renaming (dict): renaming settings
        """
        super().__init__()
        self._table = [[original, renamed] for original, renamed in renaming.items()]

    def columnCount(self, parent=QModelIndex()):
        """
        Returns:
            int: number of columns
        """
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """Returns table data for given role."""
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._table[index.row()][index.column()]
        if role == Qt.FontRole:
            if index.column() == 0:
                return None
            row = index.row()
            original = self._table[row][0]
            new = self._table[row][1]
            if new == original:
                return None
            font = QFont()
            font.setBold(True)
            return font
        return None

    def flags(self, index):
        if index.column() == 1:
            return super().flags(index) | Qt.ItemIsEditable
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns header data."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return "Original" if section == 0 else "Renamed"
        return None

    def renaming_settings(self):
        return {row[0]: row[1] for row in self._table if row[1]}

    def reset_originals(self, names):
        """
        Resets the original names keeping the renamed values where applicable.

        Args:
            names (set): new original names
        """
        self.beginResetModel()
        old_settings = self.renaming_settings()
        self._table = [[name, old_settings.get(name, name)] for name in names]
        self._table.sort(key=lambda row: row[0])
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        """
        Returns:
            int: number of rows
        """
        return len(self._table)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if role == Qt.EditRole and index.column() == 1:
            self._table[index.row()][1] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        return False
