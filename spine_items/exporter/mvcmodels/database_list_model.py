######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains a model for Exporter's output preview.

"""
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from spine_items.utils import Database


class DatabaseListModel(QAbstractListModel):
    """A model for exporter database lists."""

    def __init__(self, databases):
        """
        Args:
            databases (list of Database): databases to list
        """
        super().__init__()
        self._databases = databases

    def add(self, database):
        """
        Appends a database to the list.

        Args:
            database (Database): a database to add
        """
        row = len(self._databases)
        self.beginInsertRows(QModelIndex(), row, row)
        self._databases.append(database)
        self.endInsertRows()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._databases[index.row()].url
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        self._databases = self._databases[:row] + [Database() for _ in range(count)] + self._databases[row:]
        self.endInsertRows()

    def item(self, url):
        """
        Returns database item for given URL.

        Args:
            url (str): database URL

        Returns:
            Database: a database
        """
        for db in self._databases:
            if db.url == url:
                return db
        raise RuntimeError(f"Database '{url}' not found.")

    def items(self):
        """
        Returns a list of databases this model contains.

        Returns:
            list of Database: database
        """
        return self._databases

    def remove(self, url):
        """
        Removes database item with given URL.

        Args:
            url (str): database URL

        Returns:
            Database: removed database or None if not found
        """
        for row, db in enumerate(self._databases):
            if db.url == url:
                self.removeRows(row, 1)
                return db
        return None

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._databases = self._databases[:row] + self._databases[row + count :]
        self.endRemoveRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self._databases)

    def update_url(self, old, new):
        """
        Updates a database URL.

        Args:
            old (str): old URL
            new (str): new URL
        """
        for row, db in enumerate(self._databases):
            if old == db.url:
                db.url = new
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return

    def urls(self):
        """
        Returns database URLs.

        Returns:
            set of str: database URLs
        """
        return {db.url for db in self._databases}
