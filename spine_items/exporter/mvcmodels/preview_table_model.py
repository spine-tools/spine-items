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

"""Contains model for a single export preview table."""
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


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

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._table[index.row()]
            column = index.column()
            if column < len(row):
                return row[column]
        if role == Qt.ItemDataRole.BackgroundRole:
            if self._index_in_pivot(index):
                return self._in_pivot_color
            color_row = self._row_to_map_color.get(index.row())
            if color_row is not None and index.column() > self._max_mapping_column:
                return color_row
            color_column = self._column_to_map_color.get(index.column())
            if color_column is not None and index.row() > self._max_mapping_row:
                return color_column
        return None

    def _index_in_pivot(self, index):
        return index.row() > self._max_mapping_row and index.column() > self._max_mapping_column

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return section + 1
        return None

    def mapping_name(self):
        """Returns current mapping's name.

        Returns:
            str: mapping name
        """
        return self._mapping_name

    def reset(self, mapping_name, table_name, table, mapping_colors):
        """
        Resets model's data.

        Args:
            mapping_name (str): current mapping's name
            table_name (str): current table's name
            table (list): table data
            mapping_colors (dict): mapping int position to QColor
        """
        self.beginResetModel()
        self._mapping_name = mapping_name
        self._table_name = table_name
        self._table = table
        self._reset_colors(mapping_colors)
        self.endResetModel()

    def _reset_colors(self, mapping_colors):
        """Updates attributes for coloring cells.

        Args:
            mapping_colors (dict): mapping int position to QColor
        """
        self._row_to_map_color = {}
        self._column_to_map_color = {}
        # Compute in-pivot color
        positions = list(mapping_colors)
        is_pivoted = any([p < 0 for p in positions[:-1]])
        if is_pivoted:
            p = positions.pop(-1)
            self._in_pivot_color = mapping_colors[p]
        # Compute row and column colors
        for position in positions:
            color = mapping_colors[position]
            if position < 0:
                row = -(position + 1)
                self._row_to_map_color[row] = color
            else:
                column = position
                self._column_to_map_color[column] = color
        # Compact the rows
        sorted_row_to_map_color = {row: self._row_to_map_color[row] for row in sorted(self._row_to_map_color)}
        self._row_to_map_color = dict(enumerate(sorted_row_to_map_color.values()))
        # Compute maxes
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
