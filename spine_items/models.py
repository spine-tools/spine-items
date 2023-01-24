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
Common models.
Contains a generic File list model and an Item for that model.
Used by the Importer, Gimlet and Tool project items but this may be handy for other project items
as well.

:authors: P. Savolainen (VTT), P. Vennström (VTT), A. Soininen (VTT)
:date:    5.6.2020
"""
from collections import namedtuple
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal
from spinetoolbox.mvcmodels.file_list_models import (
    FileListModel,
    CommandLineArgsModel,
    NewCommandLineArgItem,
    CommandLineArgItem,
)
from spine_engine.project_item.project_item_resource import extract_packs
from .utils import Database


class CheckableFileListModel(FileListModel):
    """A model for checkable files to be shown in a file tree view."""

    FileItem = namedtuple("FileItem", ["resource", "checked"])
    PackItem = namedtuple("PackItem", ["label", "resources", "checked"])

    checked_state_changed = Signal(QModelIndex, bool)
    """Emitted when an item's checked state changes."""

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.CheckStateRole:
            if index.internalPointer() is None:
                row = index.row()
                if row < len(self._single_resources):
                    checked = self._single_resources[row].checked
                else:
                    checked = self._pack_resources[row - len(self._single_resources)].checked
                return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
            return None
        return super().data(index, role)

    def checked_data(self, index):
        """Returns checked status and label for given top-level index.

        Args:
            index (QModelIndex): top-level index

        Returns:
            tuple: item label and checked flag
        """
        row = index.row()
        if row < len(self._single_resources):
            return self._single_resources[row].resource.label, self._single_resources[row].checked
        pack = self._pack_resources[row - len(self._single_resources)]
        return pack.label, pack.checked

    def is_checked(self, index):
        """Returns True if the item at given index is checked.

        Args:
            index (QModelIndex): index

        Returns:
            bool: True if the item is checked, False otherwise
        """
        pack_label = index.internalPointer()
        if pack_label is None:
            row = index.row()
            if row < len(self._single_resources):
                return self._single_resources[row].checked
            return self._pack_resources[row - len(self._single_resources)].checked
        return self._pack_resources[self._pack_index(pack_label)].checked

    def flags(self, index):
        flags = super().flags(index)
        if index.internalPointer() is None:
            return flags | Qt.ItemIsUserCheckable
        return flags

    def update(self, resources):
        """Updates the model according to given list of resources.

        Args:
            resources (Iterable of ProjectItemResource): resources
        """
        self.beginResetModel()
        unchecked_singles = {item.resource.label for item in self._single_resources if not item.checked}
        unchecked_packs = {item.label for item in self._pack_resources if not item.checked}
        unchecked = unchecked_singles | unchecked_packs
        single_resources, pack_resources = extract_packs(resources)
        new_singles = [self.FileItem(r, r.label not in unchecked) for r in single_resources]
        new_packs = [
            self.PackItem(label, [r for r in r_list if r.hasfilepath], label not in unchecked)
            for label, r_list in pack_resources.items()
        ]
        self._single_resources = new_singles
        self._pack_resources = new_packs
        self.endResetModel()

    def replace(self, old_resource, new_resource):
        """Replaces existing data in the model.

        Note: we don't currently update file pack labels here.

        Args:
            old_resource (ProjectItemResource): resource to replace
            new_resource (ProjectItemResource): new resource
        """
        if old_resource.type_ == "database":
            return
        for row, item in enumerate(self._single_resources):
            if item.resource.provider_name == old_resource.provider_name and item.resource.label == old_resource.label:
                self._single_resources[row] = item._replace(resource=new_resource)
                index = self.index(row, 0)
                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole])
                return
        for pack_row, pack in enumerate(self._pack_resources):
            for row, resource in enumerate(pack.resources):
                if resource.provider_name == old_resource.provider_name and resource.label == old_resource.label:
                    if new_resource.label == resource.label:
                        pack.resources[row] = new_resource
                        pack_index = self.index(pack_row, 0)
                        index = self.index(row, 0, pack_index)
                        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole])
                        return
                    else:
                        single_resources = [item.resource for item in self._single_resources]
                        new_pack_resources = [
                            r
                            for existing_pack in self._pack_resources
                            for r in existing_pack.resources
                            if r is not resource
                        ]
                        new_pack_resources.append(new_resource)
                        self.update(single_resources + new_pack_resources)
                        return

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        """Sets data in the model."""
        if role != Qt.ItemDataRole.CheckStateRole or not index.isValid():
            return False
        checked = value == Qt.CheckState.Checked.value
        self.checked_state_changed.emit(index, checked)
        return True

    def set_initial_state(self, selected_items):
        """Fills model with incomplete data; needs a call to :func:`update` to make the model usable.

        Args:
            selected_items (dict): mapping from item label to checked flag
        """
        for label, selected in selected_items.items():
            self._pack_resources.append(self.PackItem(label, [], selected))

    def set_checked(self, index, checked):
        """Checks or unchecks given item.

        Args:
            index (QModelIndex): resource label
            checked (bool): checked flag
        """
        row = index.row()
        if row < len(self._single_resources):
            self._single_resources[row] = self._single_resources[row]._replace(checked=checked)
        else:
            row -= len(self._single_resources)
            self._pack_resources[row] = self._pack_resources[row]._replace(checked=checked)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

    def index_with_file_path(self):
        """Tries to find an item that has a valid file path.

        Returns:
            QModelIndex: index to a item with usable file path or an invalid index if none found
        """
        for row, item in enumerate(self._single_resources):
            if item.checked and item.resource.hasfilepath:
                return self.index(row, 0)
        for pack_row, item in enumerate(self._pack_resources):
            if item.checked:
                for row, resource in enumerate(item.resources):
                    if resource.hasfilepath:
                        return self.index(row, 0, self.index(pack_row, 0))
        return QModelIndex()


class GimletCommandLineArgsModel(CommandLineArgsModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.invisibleRootItem().appendRow(NewCommandLineArgItem())

    def reset_model(self, args):
        self._args = args
        self._reset_root(
            self.invisibleRootItem(), args, dict(editable=True, selectable=True, drag_enabled=True), has_empty_row=True
        )

    def canDropMimeData(self, data, drop_action, row, column, parent):
        return row >= 0


class ToolCommandLineArgsModel(CommandLineArgsModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._spec_args_root = CommandLineArgItem("Specification arguments")
        self._tool_args_root = CommandLineArgItem("Tool arguments", drop_enabled=True)
        self.appendRow(self._spec_args_root)
        self.appendRow(self._tool_args_root)
        self._tool_args_root.appendRow(NewCommandLineArgItem())

    def reset_model(self, spec_args, tool_args):
        self._args = tool_args
        self._reset_root(self._spec_args_root, spec_args, dict(), has_empty_row=False)
        self._reset_root(
            self._tool_args_root, tool_args, dict(editable=True, selectable=True, drag_enabled=True), has_empty_row=True
        )

    def canDropMimeData(self, data, drop_action, row, column, parent):
        return parent.data() is not None and row >= 0


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
