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
        self._row_to_map_color = {}
        self._column_to_map_color = {}
        self._max_mapping_row = 0
        self._max_mapping_column = 0
        self._in_pivot_color = None

    def clear(self):
        """Empties the table."""
        if not self._table:
            return
        self.beginResetModel()
        self._table.clear()
        self.endResetModel()

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
        if role == Qt.BackgroundRole:
            if self._index_in_pivot(index):
                return self._in_pivot_color
            color_row = self._row_to_map_color.get(index.row())
            color_column = self._column_to_map_color.get(index.column())
            if color_row is not None and index.column() > self._max_mapping_column:
                return color_row
            if color_column is not None and index.row() > self._max_mapping_row:
                return color_column
        return None

    def _index_in_pivot(self, index):
        return index.row() > self._max_mapping_row and index.column() > self._max_mapping_column

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

    def reset(self, mapping_name, table_name, table, mappings, colors):
        """
        Resets model's data.

        Args:
            mapping_name (str): current mapping's name
            table_name (str): current table's name
            table (list): table data
            mappings (list of ExportMapping): mappings
            colors (list of QColor): colors
        """
        self.beginResetModel()
        self._mapping_name = mapping_name
        self._table_name = table_name
        self._table = table
        self._reset_colors(mappings, colors)
        self.endResetModel()

    def _reset_colors(self, mappings, colors):
        """Updates attributes that define colors for rows and columns in the tables.

        Args:
            mappings (list of ExportMapping): mappings
            colors (list of QColor): colors
        """
        row_to_map_color = {}
        self._column_to_map_color = {}
        # Compute positions
        positions = [m.position if isinstance(m.position, int) else None for m in mappings]
        is_pivoted = any([p < 0 for p in positions[:-1] if p is not None])
        if is_pivoted:
            positions.pop(-1)
            self._in_pivot_color = colors[-1]
        # Compute lookup dicts
        for position, color in zip(positions, colors):
            if position is None:
                continue
            if position < 0:
                row = -(position + 1)
                row_to_map_color[row] = color
            else:
                column = position
                self._column_to_map_color[column] = color
        sorted_row_to_map_color = {row: row_to_map_color[row] for row in sorted(row_to_map_color)}
        self._row_to_map_color = dict(enumerate(sorted_row_to_map_color.values()))
        self._max_mapping_row = max(self._row_to_map_color, default=-1)
        self._max_mapping_column = max(self._column_to_map_color, default=-1)

    def rowCount(self, parent=QModelIndex()):
        return len(self._table)

    def table_name(self):
        """Returns current table's name.

        Returns:
            str: table name
        """
        return self._table_name
