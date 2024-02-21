######################################################################################################################
# Copyright (C) 2017-2023 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Exporter's ``FullUrlListModel``."""
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt


class FullUrlListModel(QAbstractListModel):
    def __init__(self, parent=None):
        """
        Args:
            parent (QObject, optional): model's parent
        """
        super().__init__(parent)
        self._urls = list()

    def append(self, url):
        """
        Appends a URL to the model.

        Args:
            url (str): URL to append
        """
        n = len(self._urls)
        self.beginInsertRows(QModelIndex(), n, n)
        self._urls.append(url)
        self.endInsertRows()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._urls[index.row()]
        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._urls)

    def set_urls(self, urls):
        """
        Sets model's URLs.

        Args:
            urls (Iterable of str): URLs
        """
        self.beginResetModel()
        self._urls = list(urls)
        self.endResetModel()

    def update_url(self, old, new):
        """
        Updates a database URL.

        Args:
            old (str): old URL
            new (str): new URL
        """
        for row, url in enumerate(self._urls):
            if old == url:
                self._urls[row] = new
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return
