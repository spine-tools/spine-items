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
Contains model for export mapping setup table.

:author: A. Soininen (VTT)
:date:   11.12.2020
"""
from itertools import takewhile
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide2.QtGui import QColor, QFont
from spinedb_api.export_mapping import is_pivoted, is_regular, Position
from spinedb_api.export_mapping.item_export_mapping import (
    AlternativeMapping,
    FixedValueMapping,
    ExpandedParameterValueMapping,
    ExpandedParameterDefaultValueMapping,
    FeatureEntityClassMapping,
    FeatureParameterDefinitionMapping,
    ObjectClassMapping,
    ObjectGroupMapping,
    ObjectMapping,
    ParameterDefaultValueMapping,
    ParameterDefaultValueIndexMapping,
    ParameterDefinitionMapping,
    ParameterValueIndexMapping,
    ParameterValueListMapping,
    ParameterValueListValueMapping,
    ParameterValueMapping,
    RelationshipClassMapping,
    RelationshipClassObjectClassMapping,
    RelationshipMapping,
    RelationshipObjectMapping,
    ScenarioActiveFlagMapping,
    ScenarioAlternativeMapping,
    ScenarioMapping,
    ToolFeatureEntityClassMapping,
    ToolFeatureMethodEntityClassMapping,
    ToolFeatureMethodMethodMapping,
    ToolFeatureMethodParameterDefinitionMapping,
    ToolFeatureParameterDefinitionMapping,
    ToolFeatureRequiredFlagMapping,
    ToolMapping,
)
from ..commands import SetFixedTitle, SetMappingPosition


class MappingTableModel(QAbstractTableModel):
    def __init__(self, mapping_name, root_mapping, undo_stack, mapping_provider):
        """
        Args:
            mapping_name (str): mapping's name
            root_mapping (Mapping, optional): root mapping
            undo_stack (QUndoStack): undo stack
            mapping_provider (SpecificationEditorWindow): window that can provide data for different mappings
        """
        super().__init__()
        self._mappings = [] if root_mapping is None else root_mapping.flatten()
        self._non_leaf_mapping_is_pivoted = self._is_non_leaf_pivoted()
        self._undo_stack = undo_stack
        self._mapping_name = mapping_name
        self._mapping_provider = mapping_provider

    def columnCount(self, paren=QModelIndex()):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        if role == Qt.DisplayRole:
            if column == 0:
                row = index.row()
                mapping = self._mappings[row]
                if row == 0 and isinstance(mapping, FixedValueMapping):
                    return mapping.value
                return _names[type(mapping)]
            if column == 1:
                row = index.row()
                if row == self._value_row() and self._non_leaf_mapping_is_pivoted:
                    return "in pivot"
                position = self._mappings[row].position
                if is_regular(position):
                    return str(position + 1)
                if is_pivoted(position):
                    return str(-position)
                return {
                    Position.hidden: "hidden",
                    Position.table_name: "table name",
                    Position.single_row: "single row",
                }.get(position, "unrecognized")
        elif role == Qt.CheckStateRole and index.column() == 2:
            if is_pivoted(self._mappings[index.row()].position):
                return Qt.Checked
            return Qt.Unchecked
        elif role == Qt.FontRole and column == 0:
            if index.row() != 0 or not isinstance(self._mappings[0], FixedValueMapping):
                font = QFont()
                font.setBold(True)
                return font
        elif role == Qt.BackgroundRole and column == 0:
            if index.row() != 0 or not isinstance(self._mappings[0], FixedValueMapping):
                return QColor(250, 250, 250)
        return None

    def flags(self, index=QModelIndex()):
        row = index.row()
        column = index.column()
        if row == 0 and isinstance(self._mappings[row], FixedValueMapping):
            if column == 0:
                return super().flags(index) | Qt.ItemIsEditable
            return super().flags(index) & ~Qt.ItemIsEnabled
        value_row = self._value_row()
        if row == value_row:
            if column == 1 and self._non_leaf_mapping_is_pivoted:
                return super().flags(index) & ~Qt.ItemIsEnabled
            if column == 2:
                return super().flags(index) & ~Qt.ItemIsEnabled
        if row > value_row and column == 2:
            return super().flags(index) & ~Qt.ItemIsEnabled
        if index.column() == 0:
            return super().flags(index) & ~Qt.ItemIsSelectable
        if index.column() == 1:
            return super().flags(index) | Qt.ItemIsEditable
        if index.column() == 2:
            return super().flags(index) | Qt.ItemIsUserCheckable
        return super().flags(index)

    def has_table_name(self):
        """Checks if current mappings have a table name.

        Returns:
            bool: True if mappings have a table name, False otherwise
        """
        return any(m.position == Position.table_name for m in self._mappings)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return {0: "Mapping type", 1: "Map to", 2: "Pivoted"}[section]
        return None

    def root_mapping(self):
        """
        Returns:
            Mapping: root mapping
        """
        return self._mappings[0]

    def rowCount(self, parent=QModelIndex()):
        return len(self._mappings)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            row = index.row()
            column = index.column()
            mapping = self._mappings[row]
            if column == 0 and isinstance(mapping, FixedValueMapping):
                self._undo_stack.push(SetFixedTitle(self, value, mapping.value))
                return True
            if column == 1:
                previous_value = mapping.position
                try:
                    value = max(int(value), 1)
                    if is_pivoted(mapping.position):
                        value = -value
                    else:
                        value = value - 1
                except ValueError:
                    value = value.strip().lower()
                    if value.startswith("t"):
                        if isinstance(self._mappings[0], FixedValueMapping):
                            return False
                        value = Position.table_name
                    elif value.startswith("h"):
                        value = Position.hidden
                    elif value.startswith("s"):
                        if row != len(self._mappings) - 1:
                            return False
                        value = Position.single_row
                    else:
                        return False
                if value == mapping.position:
                    return False
                command = SetMappingPosition(self, self._mapping_name, row, value, previous_value)
                self._undo_stack.push(command)
                return True
        elif role == Qt.CheckStateRole:
            row = index.row()
            mapping = self._mappings[row]
            position = mapping.position
            if position in (Position.hidden, Position.table_name, Position.single_row):
                position = 0
            new_position = -position - 1
            command = SetMappingPosition(self, self._mapping_name, row, new_position, mapping.position)
            self._undo_stack.push(command)
            return True
        return False

    def set_mapping(self, mapping_name, root_mapping):
        """
        Sets mapping for model.

        Args:
            mapping_name (str): mapping's name
            root_mapping (Mapping, optional): root mapping
        """
        self.beginResetModel()
        self._mapping_name = mapping_name
        self._mappings = [] if root_mapping is None else root_mapping.flatten()
        self._non_leaf_mapping_is_pivoted = self._is_non_leaf_pivoted()
        self.endResetModel()

    def set_position(self, position, row, mapping_name):
        """
        Sets mapping position for given row.

        Args:
            position (int or Position): mapping position
            row (int): row index
            mapping_name (str): mapping's name
        """
        if mapping_name != self._mapping_name:
            self._mapping_provider.show_on_table(mapping_name)
        self._mappings[row].position = position
        index = self.index(row, 1)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])
        pivot_index = self.index(row, 2)
        self.dataChanged.emit(pivot_index, pivot_index, [Qt.CheckStateRole])
        non_leaf_pivoted = self._is_non_leaf_pivoted()
        if non_leaf_pivoted != self._non_leaf_mapping_is_pivoted:
            self._non_leaf_mapping_is_pivoted = non_leaf_pivoted
            index = self.index(self._value_row(), 1)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_fixed_title(self, title):
        """
        Sets fixed table name.

        Args:
            title (str): fixed table name
        """
        self._mappings[0].value = title
        index = self.index(0, 0)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def _value_row(self):
        """
        Returns the last relevant row, i.e. the one that contains the leaf mapping.

        Returns:
            int: row index
        """
        return (
            len(self._mappings)
            - 1
            - len(list(takewhile(lambda m: m.position == Position.hidden, reversed(self._mappings))))
        )

    def _is_non_leaf_pivoted(self):
        """Checks if a non-leaf mapping is pivoted.

        Returns:
            bool: True if one or more non-leaf mappings are pivoted, False otherwise
        """
        return any(is_pivoted(m.position) for m in self._mappings[: self._value_row()])


_names = {
    AlternativeMapping: "Alternatives",
    ExpandedParameterDefaultValueMapping: "Default values",
    ExpandedParameterValueMapping: "Parameter values",
    FeatureEntityClassMapping: "Entity classes",
    FeatureParameterDefinitionMapping: "Parameter definitions",
    ObjectClassMapping: "Object classes",
    ObjectGroupMapping: "Object groups",
    ObjectMapping: "Objects",
    ParameterDefaultValueMapping: "Default values",
    ParameterDefaultValueIndexMapping: "Default value indexes",
    ParameterDefinitionMapping: "Parameter definitions",
    ParameterValueIndexMapping: "Parameter indexes",
    ParameterValueListMapping: "Value lists",
    ParameterValueListValueMapping: "Value list values",
    ParameterValueMapping: "Parameter values",
    RelationshipClassMapping: "Relationship classes",
    RelationshipClassObjectClassMapping: "Object classes",
    RelationshipMapping: "Relationships",
    RelationshipObjectMapping: "Objects",
    ScenarioActiveFlagMapping: "Active flags",
    ScenarioAlternativeMapping: "Alternatives",
    ScenarioMapping: "Scenarios",
    ToolFeatureEntityClassMapping: "Entity classes",
    ToolFeatureMethodEntityClassMapping: "Entity classes",
    ToolFeatureMethodMethodMapping: "Methods",
    ToolFeatureMethodParameterDefinitionMapping: "Parameter definitions",
    ToolFeatureParameterDefinitionMapping: "Parameter definitions",
    ToolFeatureRequiredFlagMapping: "Required flags",
    ToolMapping: "Tools",
}
