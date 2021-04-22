######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains SourceTableListModel and associated list item classes

:author: A. Soininen (VTT)
:date:   6.8.2019
"""

from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, Signal
from ..commands import SetTableChecked, UpdateTableItem


class SourceTableItem:
    """A list item for :class:`SourceTableListModel`"""

    def __init__(self, name, checked, checkable=True, editable=False, real=True):
        self.name = name
        self.checked = checked
        self.checkable = checkable
        self.editable = editable
        self.real = real

    def update_from_dict(self, d):
        self.name = d["name"]
        self.checked = d["checked"]
        self.checkable = d["checkable"]
        self.editable = d["editable"]
        self.real = d["real"]

    def to_dict(self):
        return dict(
            name=self.name, checked=self.checked, checkable=self.checkable, editable=self.editable, real=self.real
        )


class SourceTableListModel(QAbstractItemModel):
    """Model for source table lists which supports undo/redo functionality."""

    msg_error = Signal(str)
    table_created = Signal(int)

    def __init__(self, undo_stack):
        """
        Args:
            undo_stack (QUndoStack): undo stack
        """
        super().__init__()
        self._select_all_item = SourceTableItem("Select All", None, real=False)
        self._tables = []
        self._undo_stack = undo_stack

    def add_empty_row(self):
        self.beginInsertRows(QModelIndex(), self.rowCount() - 1, self.rowCount() - 1)
        empty_item = SourceTableItem("<unnamed table>", False, checkable=False, editable=True, real=False)
        self._tables.append(empty_item)
        self.endInsertRows()

    def _remove_empty_row(self):
        self.beginRemoveRows(QModelIndex(), self.rowCount() - 1, self.rowCount() - 1)
        self._tables.pop(self.rowCount() - 1)
        self.endRemoveRows()

    def columnCount(self, parent=QModelIndex()):
        return 1

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self._tables)
        return 0

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column, self._tables[row])

    def parent(self, _index):
        return QModelIndex()

    def checked_table_names(self):
        return [table.name for table in self._tables if table.checked]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            return index.internalPointer().name
        if role == Qt.CheckStateRole:
            if index.flags() & Qt.ItemIsUserCheckable:
                return Qt.Checked if index.internalPointer().checked else Qt.Unchecked
        return None

    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.internalPointer().checkable:
            flags |= Qt.ItemIsUserCheckable
        if index.internalPointer().editable:
            flags |= Qt.ItemIsEditable
        return flags

    def reset(self, items):
        self.beginResetModel()
        self._tables = [self._select_all_item] + items
        self.endResetModel()

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        item = self._tables[row]
        if role == Qt.CheckStateRole:
            checked = value == Qt.Checked
            if row == 0:
                self.set_multiple_checked_undoable(checked, *range(1, len(self._tables)))
            else:
                self._undo_stack.push(SetTableChecked(item.name, self, checked, row))
        if role == Qt.EditRole:
            if value == item.name:
                return True
            if value in self.table_names():
                self.msg_error.emit(f"There's already a table called {value}")
                return False
            item_dict = item.to_dict()
            new_item_dict = item_dict.copy()
            new_item_dict["name"] = value
            new_item_dict["real"] = True
            new_item_dict["checkable"] = True
            self._undo_stack.push(UpdateTableItem(self, row, item_dict, new_item_dict, row == self.rowCount() - 1))
            return True
        return True

    def update_item(self, row, item_dict, add_empty_row=False, remove_empty_row=False):
        """
        Updates item. This only happens in file-less mode, when the user is creating tables.

        Args:
            rows (int): item row
            item_dict (dict): new item dict
            add_empty_row (bool): whether or not to add an empty row
            remove_empty_row (bool): whether or not to remove the empty row
        """
        item = self._tables[row]
        item.update_from_dict(item_dict)
        index = self.index(row, 0)
        if add_empty_row:
            self.add_empty_row()
            self.table_created.emit(row)
        if remove_empty_row:
            self._remove_empty_row()
        self.dataChanged.emit(index, index)

    def set_checked(self, checked, *rows):
        """
        Sets the checked status of a list item.

        Args:
            checked (bool): True for checked, False for unchecked
            rows (int): item row
        """
        for row in rows:
            if self._tables[row].checked == checked:
                continue
            self._tables[row].checked = checked
            index = self.index(row, 0)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
        # Update select all state
        self._select_all_item.checked = all(self._tables[row].checked for row in range(1, len(self._tables)))
        index = self.index(0, 0)
        self.dataChanged.emit(index, index, [Qt.CheckStateRole])

    def set_multiple_checked_undoable(self, checked, *rows):
        """
        Sets the checked status of multiple list items.

        This action is undoable.

        Args:
            checked (bool): True for checked, False for unchecked
            rows (Iterable of int): item rows
        """
        rows = [row for row in rows if self._tables[row].checked != checked]
        self._undo_stack.push(SetTableChecked("All", self, checked, *rows))

    def table_at(self, index):
        return self._tables[index.row()]

    def table_index(self, table):
        rows = {table.name: i for i, table in enumerate(self._tables)}
        try:
            return self.index(rows[table], 0)
        except KeyError:
            return QModelIndex()

    def table_names(self):
        return [table.name for table in self._tables if table.real]
