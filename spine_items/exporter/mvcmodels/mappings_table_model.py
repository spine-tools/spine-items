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

"""Contains the :class:`MappingListModel` model."""
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from spinedb_api.export_mapping.export_mapping import (
    ParameterDefaultValueIndexMapping,
    ParameterValueIndexMapping,
    DimensionMapping,
    EntityClassMapping,
)
from spinetoolbox.helpers import unique_name


class MappingsTableModel(QAbstractTableModel):
    """A table model that holds export mappings."""

    rename_requested = Signal(int, str)
    """Emitted when mapping's name should be changed."""
    mapping_enabled_state_change_requested = Signal(int)
    """Emitted when mapping's enabled state should be changed."""
    set_all_mappings_enabled_requested = Signal(bool)
    """Emitted when all mappings should be enabled/disabled."""
    write_order_about_to_change = Signal()
    """Emitted before changing the write order."""
    write_order_changed = Signal()
    """Emitted after the write order has changed."""

    MAPPING_SPECIFICATION_ROLE = Qt.ItemDataRole.UserRole + 1
    MAPPING_TYPE_ROLE = Qt.ItemDataRole.UserRole + 2
    MAPPING_ROOT_ROLE = Qt.ItemDataRole.UserRole + 3
    ALWAYS_EXPORT_HEADER_ROLE = Qt.ItemDataRole.UserRole + 4
    ENTITY_DIMENSIONS_ROLE = Qt.ItemDataRole.UserRole + 5
    USE_FIXED_TABLE_NAME_FLAG_ROLE = Qt.ItemDataRole.UserRole + 6
    FIXED_TABLE_NAME_ROLE = Qt.ItemDataRole.UserRole + 7
    PARAMETER_DIMENSIONS_ROLE = Qt.ItemDataRole.UserRole + 8
    GROUP_FN_ROLE = Qt.ItemDataRole.UserRole + 9
    HIGHLIGHT_POSITION_ROLE = Qt.ItemDataRole.UserRole + 10

    def __init__(self, mappings=None, parent=None):
        """
        Args:
            mappings (dict, optional): mapping from name to ``MappingSpecification``
            parent (QObject, optional): parent object
        """
        super().__init__(parent)
        if mappings is None:
            mappings = dict()
        self._names = list(mappings)
        self._mappings = mappings

    def columnCount(self, parent=QModelIndex()):
        return 2

    def extend(self, mapping_specification, name=""):
        """
        Appends a mapping to the table.

        Args:
            mapping_specification (MappingSpecification): specification to add
            name (str): mapping specification's name; if empty, the mapping is given a default name

        Returns:
            int: row index of the new mapping
        """
        position = len(self._names)
        self.beginInsertRows(QModelIndex(), position, position)
        if not name:
            name = unique_name("Mapping", self._names)
        elif name in self._names:
            name = unique_name(name, self._names)
        self._mappings[name] = mapping_specification
        self._names.append(name)
        self.endInsertRows()
        return position

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        if column == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                spec = self._mappings[self._names[index.row()]]
                return Qt.CheckState.Checked if spec.enabled else Qt.CheckState.Unchecked
            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
                return self._names[index.row()]
        if column == 1:
            if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
                order = str(index.row() + 1)
                if order.endswith(("11", "12", "13")):
                    return order + "th"
                if order.endswith("1"):
                    return order + "st"
                if order.endswith("2"):
                    return order + "nd"
                if order.endswith("3"):
                    return order + "rd"
                return order + "th"
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        if role >= Qt.ItemDataRole.UserRole:
            spec = self._mappings[self._names[index.row()]]
            if role == self.MAPPING_SPECIFICATION_ROLE:
                return spec
            if role == self.MAPPING_TYPE_ROLE:
                return spec.type.value
            if role == self.MAPPING_ROOT_ROLE:
                return spec.root
            if role == self.ALWAYS_EXPORT_HEADER_ROLE:
                return spec.always_export_header
            if role == self.ENTITY_DIMENSIONS_ROLE:
                return _instance_occurrences(spec.root, DimensionMapping)
            if role == self.USE_FIXED_TABLE_NAME_FLAG_ROLE:
                return spec.use_fixed_table_name_flag
            if role == self.FIXED_TABLE_NAME_ROLE:
                return spec.root.value
            if role == self.PARAMETER_DIMENSIONS_ROLE:
                dimensions = _instance_occurrences(spec.root, ParameterValueIndexMapping)
                if dimensions == 0:
                    return _instance_occurrences(spec.root, ParameterDefaultValueIndexMapping)
                return dimensions
            if role == self.GROUP_FN_ROLE:
                return spec.group_fn
            if role == self.HIGHLIGHT_POSITION_ROLE:
                highlighting_mapping = next((m for m in spec.root.flatten() if isinstance(m, EntityClassMapping)), None)
                if highlighting_mapping is None:
                    return None
                return highlighting_mapping.highlight_position
        return None

    def flags(self, index):
        if index.column() == 0:
            return super().flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ("Name", "Write order")[section]
        return None

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
        try:
            row = self._names.index(name)
        except ValueError:
            return QModelIndex()
        return self.index(row, 0)

    def reorder_writing(self, row, earlier):
        """Reorders writings.

        Args:
            row (int): row to reorder
            earlier (bool): True to write earlier, False to write later
        """
        moved = [self._names[row]]
        if earlier:
            before = self._names[: row - 1]
            after = [self._names[row - 1]] + self._names[row + 1 :]
        else:
            before = self._names[:row] + [self._names[row + 1]]
            after = self._names[row + 2 :]
        self.write_order_about_to_change.emit()
        self.beginRemoveRows(QModelIndex(), row, row)
        self._names = before + after
        self.endRemoveRows()
        insert_row = row - 1 if earlier else row + 1
        self.beginInsertRows(QModelIndex(), insert_row, insert_row)
        self._names = before + moved + after
        self.endInsertRows()
        reordered_mappings = {name: self._mappings[name] for name in self._names}
        self._mappings.clear()
        self._mappings.update(reordered_mappings)
        self.write_order_changed.emit()

    def rowCount(self, parent=QModelIndex()):
        return len(self._names)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        column = index.column()
        if column == 0:
            if role == Qt.ItemDataRole.CheckStateRole:
                row = index.row()
                self.mapping_enabled_state_change_requested.emit(row)
                return True
            if role == Qt.ItemDataRole.EditRole:
                if not value or value in self._names:
                    return False
                self.rename_requested.emit(index.row(), value)
                return True
        if role > Qt.ItemDataRole.UserRole:
            name = self._names[index.row()]
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
            elif role == self.USE_FIXED_TABLE_NAME_FLAG_ROLE:
                spec.use_fixed_table_name_flag = value
                self.dataChanged.emit(index, index, [self.USE_FIXED_TABLE_NAME_FLAG_ROLE])
            elif role == self.FIXED_TABLE_NAME_ROLE:
                spec.root.value = value
                self.dataChanged.emit(index, index, [self.FIXED_TABLE_NAME_ROLE])
            elif role == self.GROUP_FN_ROLE:
                spec.group_fn = value
                self.dataChanged.emit(index, index, [self.GROUP_FN_ROLE])
            elif role == self.HIGHLIGHT_POSITION_ROLE:
                highlighting_mapping = next((m for m in spec.root.flatten() if isinstance(m, EntityClassMapping)), None)
                if highlighting_mapping is None:
                    return False
                highlighting_mapping.highlight_position = value
                self.dataChanged.emit(index, index, [self.HIGHLIGHT_POSITION_ROLE])
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
        self._names.insert(row, name)
        self._mappings[name] = mapping_specification
        self.endInsertRows()

    def remove_mapping(self, name):
        """
        Deletes a mapping.

        Args:
            name (str): mapping's name
        """
        row = self._names.index(name)
        self.beginRemoveRows(QModelIndex(), row, row)
        name = self._names.pop(row)
        del self._mappings[name]
        self.endRemoveRows()

    def rename_mapping(self, row, new_name):
        """
        Renames an item.

        Args:
            row (int): row index
            new_name (str): item's new name
        """
        previous = self._names[row]
        self._names[row] = new_name
        self._mappings[new_name] = self._mappings.pop(previous)
        index = self.index(row, 1)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def set_mapping_enabled(self, row, enabled):
        """Enables or disables a mapping.

        Args:
            row (int): row index
            enabled (bool): True to enable mapping, False to disable
        """
        name = self._names[row]
        spec = self._mappings[name]
        spec.enabled = enabled
        index = self.index(row, 0)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

    def set_all_enabled(self, enabled):
        """Enables/disables all mappings.

        Args:
            enabled (bool): True to enable, False to disable
        """
        first = None
        last = 0
        for i in range(len(self._names)):
            mapping = self._mappings[self._names[i]]
            if mapping.enabled != enabled:
                mapping.enabled = enabled
                if first is None:
                    first = i
                last = i
        if first is not None:
            top_left = self.index(first, 0)
            bottom_right = self.index(last, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])

    def enable_mapping_rows(self, rows):
        """Enables mappings on given rows and disables the rest.

        Args:
            rows (set of int): row indexes to enable
        """
        first = None
        last = 0
        for row in range(len(self._names)):
            mapping = self._mappings[self._names[row]]
            enabled = row in rows
            if mapping.enabled != enabled:
                mapping.enabled = enabled
                if first is None:
                    first = row
                last = row
        if first is not None:
            top_left = self.index(first, 0)
            bottom_right = self.index(last, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])

    def enabled_mapping_rows(self):
        """Returns enabled mapping rows.

        Return:
            set of int: enabled mapping row indexes.
        """
        rows = set()
        for row in range(len(self._names)):
            if self._mappings[self._names[row]].enabled:
                rows.add(row)
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
