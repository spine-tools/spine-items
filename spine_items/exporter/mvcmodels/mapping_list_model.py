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
Contains the :class:`MappingListModel` model.

:authors: A. Soininen (VTT)
:date:    30.12.2020
"""
from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt, Signal
from spinedb_api.export_mapping.export_mapping import (
    ParameterDefaultValueIndexMapping,
    ParameterValueIndexMapping,
    RelationshipClassObjectClassMapping,
)
from spinetoolbox.helpers import unique_name


class MappingListModel(QAbstractListModel):
    """A list model that holds export mappings."""

    rename_requested = Signal(int, str)
    """Emitted when mapping's name should be changed."""
    mapping_enabled_state_change_requested = Signal(int)
    """Emitted when mapping's enabled state should be changed."""
    set_all_mappings_enabled_requested = Signal(bool)
    """Emitted when all mappings should be enabled/disabled."""

    MAPPING_SPECIFICATION_ROLE = Qt.UserRole + 1
    MAPPING_TYPE_ROLE = Qt.UserRole + 2
    MAPPING_ROOT_ROLE = Qt.UserRole + 3
    ALWAYS_EXPORT_HEADER_ROLE = Qt.UserRole + 4
    EXPORT_OBJECTS_FLAG_ROLE = Qt.UserRole + 5
    RELATIONSHIP_DIMENSIONS_ROLE = Qt.UserRole + 6
    USE_FIXED_TABLE_NAME_FLAG_ROLE = Qt.UserRole + 7
    PARAMETER_DIMENSIONS_ROLE = Qt.UserRole + 8

    def __init__(self, mappings=None):
        """
        Args:
            mappings (dict, optional): mapping from name to ``MappingSpecification``
        """
        super().__init__()
        if mappings is None:
            mappings = dict()
        self._names = list(mappings)
        self._mappings = mappings

    def extend(self, mapping_specification):
        """
        Appends a new mapping to the list.

        Args:
            mapping_specification (MappingSpecification): specification to add

        Returns:
            int: row index of the new mapping
        """
        position = len(self._names)
        all_enabled = all(m.enabled for m in self._mappings.values())
        self.beginInsertRows(QModelIndex(), position, position)
        name = unique_name("Mapping", self._names)
        self._mappings[name] = mapping_specification
        self._names.append(name)
        if all_enabled:
            mapping_specification.enabled = True
        self.endInsertRows()
        return position

    def data(self, index, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole):
            row = index.row()
            if row == 0:
                return "Select All"
            return self._names[row - 1]
        if role == Qt.CheckStateRole:
            row = index.row()
            if row == 0:
                return Qt.Checked if all(m.enabled for m in self._mappings.values()) else Qt.Unchecked
            spec = self._mappings[self._names[row - 1]]
            return Qt.Checked if spec.enabled else Qt.Unchecked
        if role >= Qt.UserRole:
            spec = self._mappings[self._names[index.row() - 1]]
            if role == self.MAPPING_SPECIFICATION_ROLE:
                return spec
            if role == self.MAPPING_TYPE_ROLE:
                return spec.type
            if role == self.MAPPING_ROOT_ROLE:
                return spec.root
            if role == self.ALWAYS_EXPORT_HEADER_ROLE:
                return spec.always_export_header
            if role == self.EXPORT_OBJECTS_FLAG_ROLE:
                return spec.export_objects_flag
            if role == self.RELATIONSHIP_DIMENSIONS_ROLE:
                return _instance_occurrences(spec.root, RelationshipClassObjectClassMapping)
            if role == self.USE_FIXED_TABLE_NAME_FLAG_ROLE:
                return spec.use_fixed_table_name_flag
            if role == self.PARAMETER_DIMENSIONS_ROLE:
                dimensions = _instance_occurrences(spec.root, ParameterValueIndexMapping)
                if dimensions == 0:
                    return _instance_occurrences(spec.root, ParameterDefaultValueIndexMapping)
                return dimensions
        return None

    def flags(self, index):
        if index.row() == 0:
            return super().flags(index) | Qt.ItemIsUserCheckable
        return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsUserCheckable

    def mapping_specification(self, name):
        """
        Returns a mapping specification for given name.

        Args:
            name (str): mapping's name

        Returns:
            MappingSpecification: mapping specification
        """
        return self._mappings[name]

    def index_of(self, name):
        """
        Returns index for given mapping's name.

        Args:
            name (str): mapping's name

        Returns:
            QModelIndex: index
        """
        return self.index(self._names.index(name) + 1, 0)

    def rowCount(self, parent=QModelIndex()):
        return len(self._names) + 1

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            if value in self._names:
                return False
            self.rename_requested.emit(index.row(), value)
            return True
        if role == Qt.CheckStateRole:
            row = index.row()
            if row == 0:
                self.set_all_mappings_enabled_requested.emit(value == Qt.Checked)
                return True
            self.mapping_enabled_state_change_requested.emit(row)
            return True
        if role > Qt.UserRole:
            name = self._names[index.row() - 1]
            spec = self._mappings[name]
            if role == self.MAPPING_ROOT_ROLE:
                spec.root = value
                self.dataChanged.emit(index, index, [self.MAPPING_ROOT_ROLE])
            elif role == self.MAPPING_TYPE_ROLE:
                spec.type = value
                self.dataChanged.emit(index, index, [self.MAPPING_TYPE_ROLE])
            elif role == self.ALWAYS_EXPORT_HEADER_ROLE:
                spec.always_export_header = value
                self.dataChanged.emit(index, index, [self.ALWAYS_EXPORT_HEADER_ROLE])
            elif role == self.EXPORT_OBJECTS_FLAG_ROLE:
                spec.export_objects_flag = value
                self.dataChanged.emit(index, index, [self.EXPORT_OBJECTS_FLAG_ROLE])
            elif role == self.USE_FIXED_TABLE_NAME_FLAG_ROLE:
                spec.use_fixed_table_name_flag = value
                self.dataChanged.emit(index, index, [self.USE_FIXED_TABLE_NAME_FLAG_ROLE])
            return True
        return False

    def insert_mapping(self, row, name, mapping_specification):
        """
        Adds a new mapping.

        Args:
            row (int): row index
            name (str): mapping's name
            mapping_specification (MappingSpecification): mapping specification
        """
        self.beginInsertRows(QModelIndex(), row, row)
        self._names.insert(row - 1, name)
        self._mappings[name] = mapping_specification
        self.endInsertRows()

    def remove_mapping(self, row):
        """
        Deletes a mapping.

        Args:
            row (int): row index
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        name = self._names.pop(row - 1)
        del self._mappings[name]
        self.endRemoveRows()

    def rename_mapping(self, row, new_name):
        """
        Renames an item.

        Args:
            row (int): row index
            new_name (str): item's new name
        """
        previous = self._names[row - 1]
        self._names[row - 1] = new_name
        self._mappings[new_name] = self._mappings.pop(previous)
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_mapping_enabled(self, row, enabled):
        """Enables or disables a mapping.

        Args:
            row (int): row index
            enabled (bool): True to enable mapping, False to disable
        """
        name = self._names[row - 1]
        spec = self._mappings[name]
        spec.enabled = enabled
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [Qt.CheckStateRole])
        index = self.index(0, 0)
        self.dataChanged.emit(index, index, [Qt.CheckStateRole])

    def set_all_enabled(self, enabled):
        """Enables/disables all mappings.

        Args:
            enabled (bool): True to enable, False to disable
        """
        last = 0
        for i in range(len(self._names)):
            mapping = self._mappings[self._names[i]]
            if mapping.enabled != enabled:
                last = i + 1
                mapping.enabled = enabled
        top_left = self.index(0, 0)
        bottom_right = self.index(last, 0)
        self.dataChanged.emit(top_left, bottom_right, [Qt.CheckStateRole])

    def enable_mapping_rows(self, rows):
        """Enables mappings on given rows and disables the rest.

        Args:
            rows (set of int): row indexes to enable
        """
        last = 0
        for i in range(len(self._names)):
            mapping = self._mappings[self._names[i]]
            row = i + 1
            enabled = row in rows
            if mapping.enabled != enabled:
                mapping.enabled = enabled
                last = row
        top_left = self.index(0, 0)
        bottom_right = self.index(last, 0)
        self.dataChanged.emit(top_left, bottom_right, [Qt.CheckStateRole])

    def enabled_mapping_rows(self):
        """Returns enabled mapping rows.

        Return:
            set of int: enabled mapping row indexes.
        """
        rows = set()
        for i in range(len(self._names)):
            if self._mappings[self._names[i]].enabled:
                rows.add(i + 1)
        return rows

    def reset(self, mappings):
        self.beginResetModel()
        self._names = list(mappings)
        self._mappings = mappings
        self.endResetModel()


def _has_mapping_instance(mapping, cls):
    """
    Checks if mapping or any child mappings is an instance of ``cls``.

    Args:
        mapping (Mapping): a mapping
        cls (Type): subclass of ``Mapping`` to check against

    Returns:
        bool: True if mapping or any child mappings is an instance of ``cls``, False otherwise
    """
    if isinstance(mapping, cls):
        return True
    if mapping.child is not None:
        return _has_mapping_instance(mapping.child, cls)
    return False


def _instance_occurrences(mapping, cls):
    """
    Counts occurrences of ``cls`` in mapping hierarchy.

    Args:
        mapping (Mapping): a mapping
        cls (Type): type to count

    Returns:
        int: number of instances of ``cls``
    """
    count = 0
    if isinstance(mapping, cls):
        count += 1
    if mapping.child is not None:
        count += _instance_occurrences(mapping.child, cls)
    return count
