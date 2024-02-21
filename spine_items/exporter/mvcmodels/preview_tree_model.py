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

"""Contains model for export preview tables."""
from itertools import takewhile
from operator import methodcaller
from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt


class PreviewTreeModel(QAbstractItemModel):
    TABLE_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self):
        super().__init__()
        self._tables = dict()
        self._table_names = dict()
        self._mapping_names = list()

    def add_or_update_tables(self, mapping_name, tables):
        """
        Adds new tables to the model.

        Args:
            mapping_name (str): mapping's name
            tables (dict): mapping from table name to table data
        """
        if None in tables:
            tables["<anonymous table>"] = tables.pop(None)
        if mapping_name not in self._tables:
            new_names = list(self._mapping_names)
            new_names.append(mapping_name)
            new_names.sort(key=methodcaller("lower"))
            row = len(list(takewhile(lambda x: x[0] == x[1], zip(new_names, self._mapping_names))))
            self.beginInsertRows(QModelIndex(), row, row)
            self._tables[mapping_name] = dict()
            self._mapping_names = new_names
            self._table_names[mapping_name] = list()
            self.endInsertRows()
        parent_index = self.index(self._mapping_names.index(mapping_name), 0)
        for old_name in list(self._tables[mapping_name]):
            if old_name not in tables:
                names = self._table_names[mapping_name]
                row = names.index(old_name)
                self.beginRemoveRows(parent_index, row, row)
                del self._tables[mapping_name][old_name]
                self._table_names[mapping_name] = names[:row] + names[row + 1 :]
                self.endRemoveRows()
        for name, table in tables.items():
            if name in self._tables[mapping_name]:
                self._tables[mapping_name][name] = table
                row = self._table_names[mapping_name].index(name)
                index = self.index(row, 0, parent_index)
                self.dataChanged.emit(index, index, [self.TABLE_ROLE])
            else:
                self._tables[mapping_name][name] = table
                new_names = list(self._table_names[mapping_name])
                new_names.append(name)
                new_names.sort(key=methodcaller("lower"))
                row = len(list(takewhile(lambda x: x[0] == x[1], zip(new_names, self._table_names[mapping_name]))))
                self.beginInsertRows(parent_index, row, row)
                self._table_names[mapping_name] = new_names
                self.endInsertRows()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            mapping_name_row = index.internalId() - 1
            if mapping_name_row < 0:
                return self._mapping_names[index.row()]
            mapping_name = self._mapping_names[mapping_name_row]
            return self._table_names[mapping_name][index.row()]
        if role == self.TABLE_ROLE and index.internalId() > 0:
            mapping_name = self._mapping_names[index.internalId() - 1]
            return self._tables[mapping_name][self._table_names[mapping_name][index.row()]]
        return None

    def clear(self):
        """
        Clears the model.
        """
        self.beginResetModel()
        self._tables = {}
        self._table_names = {}
        self._mapping_names = list()
        self.endResetModel()

    def flags(self, parent=QModelIndex()):
        if parent.internalId() > 0:
            return super().flags(parent) | Qt.ItemNeverHasChildren
        return super().flags(parent)

    def has_name(self, name):
        """Returns True if the model has a mapping with given name.

        Args:
            name (str): mapping's name to look for

        Returns:
            bool: True if mapping was found, False otherwise
        """
        return name in self._mapping_names

    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, 0)
        if parent.internalId() > 0:
            return QModelIndex()
        return self.createIndex(row, column, parent.row() + 1)

    def parent(self, index):
        if index.internalId() == 0:
            return QModelIndex()
        row = index.internalId() - 1
        return self.createIndex(row, 0, 0)

    def rename_mappings(self, new_names):
        """
        Renames a mapping.

        Args:
            new_names (list of str): mapping names; only a single name is expected to be actually new

        Returns:
            tuple of str: old name, new name
        """
        new_names = sorted(new_names, key=methodcaller("lower"))
        olds = set(self._mapping_names)
        news = set(new_names)
        try:
            old_name = next(iter(olds - news))
        except StopIteration:
            # A disabled mapping was renamed.
            return "", ""
        new_name = next(iter(news - olds))
        old_row = self._mapping_names.index(old_name)
        self.beginRemoveRows(QModelIndex(), old_row, old_row)
        self._mapping_names = self._mapping_names[:old_row] + self._mapping_names[old_row + 1 :]
        tables = self._tables.pop(old_name)
        table_names = self._table_names.pop(old_name)
        self.endRemoveRows()
        new_row = new_names.index(new_name)
        self.beginInsertRows(QModelIndex(), new_row, new_row)
        self._mapping_names = new_names
        self._tables[new_name] = tables
        self._table_names[new_name] = table_names
        self.endInsertRows()
        return old_name, new_name

    def remove_mapping(self, name):
        """
        Deletes a mapping from the model.

        Args:
            name (str): mapping's name
        """
        try:
            mapping_name_row = self._mapping_names.index(name)
        except ValueError:
            # Ignoring. Mappings are being removed while the previews are still loading.
            return
        parent_index = self.index(mapping_name_row, 0)
        self.beginRemoveRows(parent_index, 0, len(self._tables[name]) - 1)
        self._tables[name].clear()
        self._table_names[name].clear()
        self.endRemoveRows()
        self.beginRemoveRows(QModelIndex(), mapping_name_row, mapping_name_row)
        del self._tables[name]
        del self._table_names[name]
        del self._mapping_names[mapping_name_row]
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self._mapping_names)
        mapping_name = self._mapping_names[parent.row()]
        return len(self._table_names[mapping_name])
