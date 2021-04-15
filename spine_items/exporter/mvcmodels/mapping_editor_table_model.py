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
from spinedb_api.mapping import is_pivoted, is_regular, Position
from spinedb_api.export_mapping.export_mapping import (
    AlternativeDescriptionMapping,
    AlternativeMapping,
    FixedValueMapping,
    ExpandedParameterValueMapping,
    ExpandedParameterDefaultValueMapping,
    FeatureEntityClassMapping,
    FeatureParameterDefinitionMapping,
    ObjectClassMapping,
    ObjectGroupMapping,
    ObjectGroupObjectMapping,
    ObjectMapping,
    ParameterDefaultValueMapping,
    ParameterDefaultValueIndexMapping,
    ParameterDefinitionMapping,
    ParameterValueIndexMapping,
    ParameterValueListMapping,
    ParameterValueListValueMapping,
    ParameterValueMapping,
    ParameterValueTypeMapping,
    RelationshipClassMapping,
    RelationshipClassObjectClassMapping,
    RelationshipMapping,
    RelationshipObjectMapping,
    ScenarioActiveFlagMapping,
    ScenarioAlternativeMapping,
    ScenarioBeforeAlternativeMapping,
    ScenarioDescriptionMapping,
    ScenarioMapping,
    ToolFeatureEntityClassMapping,
    ToolFeatureMethodEntityClassMapping,
    ToolFeatureMethodMethodMapping,
    ToolFeatureMethodParameterDefinitionMapping,
    ToolFeatureParameterDefinitionMapping,
    ToolFeatureRequiredFlagMapping,
    ToolMapping,
)
from ..commands import SetFixedTitle, SetMappingPositions, SetMappingProperty


POSITION_DISPLAY_TEXT = {Position.hidden: "hidden", Position.table_name: "table name", Position.header: "column header"}


class MappingEditorTableModel(QAbstractTableModel):

    MAPPING_ITEM_ROLE = Qt.UserRole + 1

    def __init__(self, mapping_name, root_mapping, undo_stack, mapping_provider, parent=None):
        """
        Args:
            mapping_name (str): mapping's name
            root_mapping (Mapping, optional): root mapping
            undo_stack (QUndoStack): undo stack
            mapping_provider (SpecificationEditorWindow): window that can provide data for different mappings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._mappings = [] if root_mapping is None else root_mapping.flatten()
        self._non_leaf_mapping_is_pivoted = self._is_non_leaf_pivoted()
        self._undo_stack = undo_stack
        self._mapping_name = mapping_name
        self._mapping_provider = mapping_provider

    def columnCount(self, paren=QModelIndex()):
        return 5

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        if role in (Qt.DisplayRole, Qt.EditRole):
            row = index.row()
            if column == 0:
                mapping = self._mappings[row]
                if row == 0 and isinstance(mapping, FixedValueMapping):
                    return mapping.value
                return _names[type(mapping)]
            if column == 1:
                if row == _value_row(self._mappings) and self._non_leaf_mapping_is_pivoted:
                    return "in pivot"
                position = self._mappings[row].position
                if is_regular(position):
                    return str(position + 1)
                if is_pivoted(position):
                    return str(-position)
                return POSITION_DISPLAY_TEXT.get(position, "unrecognized")
            if column == 3:
                return self._mappings[row].header
            if column == 4:
                return self._mappings[row].filter_re
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
        elif role == Qt.ToolTipRole and column == 4:
            return "Regular expression"
        if role == self.MAPPING_ITEM_ROLE:
            return self._mappings[index.row()]
        return None

    def flags(self, index=QModelIndex()):
        row = index.row()
        column = index.column()
        if row == 0 and isinstance(self._mappings[row], FixedValueMapping):
            if column == 0:
                return super().flags(index) | Qt.ItemIsEditable
            return super().flags(index) & ~Qt.ItemIsEnabled
        value_row = _value_row(self._mappings)
        if row >= value_row and column == 2:
            return super().flags(index) & ~Qt.ItemIsEnabled
        if column == 0:
            return super().flags(index) & ~Qt.ItemIsSelectable
        if column in (1, 4):
            return super().flags(index) | Qt.ItemIsEditable
        if column == 2:
            return super().flags(index) | Qt.ItemIsUserCheckable
        if column == 3:
            if self._mappings[row].position == Position.header:
                return super().flags(index) & ~Qt.ItemIsEnabled
            return super().flags(index) | Qt.ItemIsEditable
        return super().flags(index)

    def has_table_name(self):
        """Checks if current mappings have a table name.

        Returns:
            bool: True if mappings have a table name, False otherwise
        """
        return any(m.position == Position.table_name for m in self._mappings)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ("Mapping type", "Map to", "Pivoted", "Header", "Filter")[section]
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
                return self._push_set_positions_command(value, row, mapping)
            if column == 3:
                if value == mapping.header:
                    return False
                previous_header = mapping.header
                command = SetMappingProperty(
                    "change mapping header", self.set_header, self._mapping_name, row, value, previous_header
                )
                self._undo_stack.push(command)
                return True
            if column == 4:
                if value == mapping.filter_re:
                    return False
                previous_filter_re = mapping.filter_re
                command = SetMappingProperty(
                    "change mapping filter", self.set_filter_re, self._mapping_name, row, value, previous_filter_re
                )
                self._undo_stack.push(command)
                return True
        elif role == Qt.CheckStateRole:
            row = index.row()
            new_positions = _propose_toggled_pivot(self._mappings, row)
            previous_positions = [m.position for m in self._mappings]
            command = SetMappingPositions(self, self._mapping_name, new_positions, previous_positions)
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

    def _push_set_positions_command(self, value, row, mapping):
        """Pushes SetMappingPosition command to undo stack

        Args:
            value (str): table cell's value
            row (int): row index
            mapping (Mapping): mapping to modify
        """
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
            elif value.startswith("c"):
                value = Position.header
            else:
                return False
        if value == mapping.position and (row != _value_row(self._mappings) or not self._non_leaf_mapping_is_pivoted):
            return False
        positions = _propose_positions(self._mappings, row, value)
        previous_positions = [m.position for m in self._mappings]
        command = SetMappingPositions(self, self._mapping_name, positions, previous_positions)
        self._undo_stack.push(command)
        return True

    def set_positions(self, positions, mapping_name):
        """
        Sets mapping position for given row.

        Args:
            positions (list of Position): mapping position
            mapping_name (str): mapping's name
        """
        if mapping_name != self._mapping_name:
            self._mapping_provider.show_on_table(mapping_name)
        top = -1
        pivot_top = top
        bottom = len(self._mappings)
        pivot_bottom = bottom
        for row in range(len(self._mappings)):
            mapping = self._mappings[row]
            position = positions[row]
            if position != mapping.position:
                top = row
                bottom = min(bottom, row)
                if is_pivoted(position) or is_pivoted(mapping.position):
                    pivot_top = row
                    pivot_bottom = min(pivot_bottom, row)
                mapping.position = position
        top_left = self.index(top, 1)
        bottom_right = self.index(bottom, 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.DisplayRole])
        if pivot_bottom <= pivot_top:
            top_left = self.index(pivot_top, 2)
            bottom_right = self.index(pivot_bottom, 2)
            self.dataChanged.emit(top_left, bottom_right, [Qt.CheckStateRole])
        non_leaf_pivoted = self._is_non_leaf_pivoted()
        if non_leaf_pivoted != self._non_leaf_mapping_is_pivoted:
            self._non_leaf_mapping_is_pivoted = non_leaf_pivoted
            index = self.index(_value_row(self._mappings), 1)
            self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_header(self, header, row, mapping_name):
        """
        Sets mapping header for given row.

        Args:
            header (str): mapping header
            row (int): row index
            mapping_name (str): mapping's name
        """
        if mapping_name != self._mapping_name:
            self._mapping_provider.show_on_table(mapping_name)
        self._mappings[row].header = header
        index = self.index(row, 3)
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def set_filter_re(self, filter_re, row, mapping_name):
        """
        Sets mapping filter_re for given row.

        Args:
            filter_re (str): mapping filter_re
            row (int): row index
            mapping_name (str): mapping's name
        """
        if mapping_name != self._mapping_name:
            self._mapping_provider.show_on_table(mapping_name)
        self._mappings[row].filter_re = filter_re
        index = self.index(row, 4)
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

    def _is_non_leaf_pivoted(self):
        """Checks if a non-leaf mapping is pivoted.

        Returns:
            bool: True if one or more non-leaf mappings are pivoted, False otherwise
        """
        return any(is_pivoted(m.position) for m in self._mappings[: _value_row(self._mappings)])


_names = {
    AlternativeDescriptionMapping: "Alternatives description",
    AlternativeMapping: "Alternatives",
    ExpandedParameterDefaultValueMapping: "Default values",
    ExpandedParameterValueMapping: "Parameter values",
    FeatureEntityClassMapping: "Entity classes",
    FeatureParameterDefinitionMapping: "Parameter definitions",
    ObjectClassMapping: "Object classes",
    ObjectGroupMapping: "Object groups",
    ObjectGroupObjectMapping: "Objects",
    ObjectMapping: "Objects",
    ParameterDefaultValueMapping: "Default values",
    ParameterDefaultValueIndexMapping: "Default value indexes",
    ParameterDefinitionMapping: "Parameter definitions",
    ParameterValueIndexMapping: "Parameter indexes",
    ParameterValueListMapping: "Value lists",
    ParameterValueListValueMapping: "Value list values",
    ParameterValueMapping: "Parameter values",
    ParameterValueTypeMapping: "Value types",
    RelationshipClassMapping: "Relationship classes",
    RelationshipClassObjectClassMapping: "Object classes",
    RelationshipMapping: "Relationships",
    RelationshipObjectMapping: "Objects",
    ScenarioActiveFlagMapping: "Active flags",
    ScenarioAlternativeMapping: "Alternatives",
    ScenarioBeforeAlternativeMapping: "Before alternatives",
    ScenarioDescriptionMapping: "Scenarios description",
    ScenarioMapping: "Scenarios",
    ToolFeatureEntityClassMapping: "Entity classes",
    ToolFeatureMethodEntityClassMapping: "Entity classes",
    ToolFeatureMethodMethodMapping: "Methods",
    ToolFeatureMethodParameterDefinitionMapping: "Parameter definitions",
    ToolFeatureParameterDefinitionMapping: "Parameter definitions",
    ToolFeatureRequiredFlagMapping: "Required flags",
    ToolMapping: "Tools",
}


def _value_row(mappings):
    """
    Returns the last relevant row, i.e. the one that contains the leaf mapping.

    Args:
        mappings (list of Mapping): flattened mappings

    Returns:
        int: row index
    """
    return len(mappings) - 1 - len(list(takewhile(lambda m: m.position == Position.hidden, reversed(mappings))))


def _propose_toggled_pivot(mappings, target_index):
    """Proposes new positions after toggling a mapping's pivoted status.

    Args:
        mappings (list of Mapping): flattened mappings
        target_index (int): target mapping's index

    Returns:
        list of Position: positions after toggling
    """
    previous_position = mappings[target_index].position
    if previous_position in (Position.hidden, Position.table_name, Position.header):
        previous_position = 0
    new_position = -previous_position - 1
    positions = [m.position for m in mappings]
    if new_position < 0:
        positions[target_index] = new_position
        _remove_column(positions, previous_position)
    else:
        _insert_into_position(positions, target_index, new_position)
    return positions


def _propose_positions(mappings, target_index, new_position):
    """Proposes new positions.

    Args:
        mappings (list of Mapping): flattened mappings
        target_index (int): index of mapping to modify
        new_position (Position or int): mapping's new position

    Returns:
        list of Position: positions after modification
    """
    positions = [m.position for m in mappings]
    if target_index == _value_row(mappings):
        _turn_off_pivots(positions)
    if isinstance(new_position, int):
        _insert_into_position(positions, target_index, new_position)
    else:
        positions[target_index] = new_position
    return positions


def _turn_off_pivots(positions):
    """Toggles pivoted positions.

    Args:
        positions (list of Position): proposed positions
    """
    for row, position in enumerate(positions):
        if is_pivoted(position):
            new_position = -position - 1
            _insert_into_position(positions, row, new_position)


def _insert_into_position(positions, target_index, new_position):
    """Inserts a position.

    Args:
        positions (list of Position): proposed positions
        target_index (int): index of position to modify
        new_position (Position or int): new position
    """
    for i in range(len(positions)):
        if i == target_index:
            continue
        if positions[i] == new_position:
            direction = 1 if new_position >= 0 else -1
            _insert_into_position(positions, i, new_position + direction)
            break
    positions[target_index] = new_position


def _remove_column(positions, column):
    """Removes a regular column position.

    Args:
        positions (list of Position): proposed positions

    """
    new_position = column + 1
    for i in range(len(positions)):
        if positions[i] == new_position:
            _insert_into_position(positions, i, new_position)
            break
