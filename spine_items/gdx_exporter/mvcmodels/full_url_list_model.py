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
Contains full URL list model.

:authors: A. Soininen (VTT)
:date:    3.12.2020
"""

from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt


class FullUrlListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self._urls = list()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
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
        self._urls = [url for url in urls]
        self.endResetModel()
