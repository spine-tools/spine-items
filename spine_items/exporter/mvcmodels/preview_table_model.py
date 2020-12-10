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
Contains model for a single export preview table.

:author: A. Soininen (VTT)
:date:   5.1.2021
"""
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt


class PreviewTableModel(QAbstractTableModel):

    MAX_COLUMNS = 50

    def __init__(self):
        super().__init__()
        self._table = list()
        self._mapping_name = None
        self._table_name = None

    def columnCount(self, parent=QModelIndex()):
        if not self._table:
            return 0
        return min(max(len(row) for row in self._table), self.MAX_COLUMNS)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = self._table[index.row()]
            column = index.column()
            if column < len(row):
                return row[column]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return section + 1
        return None

    def mapping_name(self):
        """Returns current mapping's name.

        Returns:
            str: mapping name
        """
        return self._mapping_name

    def reset(self, mapping_name, table_name, table):
        """
        Resets model's data.

        Args:
            mapping_name (str): current mapping's name
            table_name (str): current table's name
            table (list): table data
        """
        self.beginResetModel()
        self._mapping_name = mapping_name
        self._table_name = table_name
        self._table = table
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._table)

    def table_name(self):
        """Returns current table's name.

        Returns:
            str: table name
        """
        return self._table_name
