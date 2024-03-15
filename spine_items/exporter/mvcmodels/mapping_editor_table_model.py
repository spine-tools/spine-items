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

"""Contains model for export mapping setup table."""
from enum import IntEnum, unique
from operator import itemgetter
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont, QColor
from spinedb_api.mapping import is_pivoted, is_regular, Position, value_index
from spinedb_api.export_mapping.export_mapping import (
    AlternativeDescriptionMapping,
    AlternativeMapping,
    FixedValueMapping,
    ExpandedParameterValueMapping,
    ExpandedParameterDefaultValueMapping,
    EntityClassMapping,
    EntityGroupMapping,
    EntityGroupEntityMapping,
    EntityMapping,
    ParameterDefaultValueMapping,
    ParameterDefaultValueIndexMapping,
    ParameterDefinitionMapping,
    ParameterValueIndexMapping,
    ParameterValueListMapping,
    ParameterValueListValueMapping,
    ParameterValueMapping,
    ParameterValueTypeMapping,
    DimensionMapping,
    ElementMapping,
    ScenarioActiveFlagMapping,
    ScenarioAlternativeMapping,
    ScenarioBeforeAlternativeMapping,
    ScenarioDescriptionMapping,
    ScenarioMapping,
    IndexNameMapping,
    DefaultValueIndexNameMapping,
    ParameterDefaultValueTypeMapping,
)
from spinetoolbox.helpers import color_from_index, plain_to_rich
from ..commands import SetMappingNullable, SetMappingPositions, SetMappingProperty


POSITION_DISPLAY_TEXT = {Position.hidden: "hidden", Position.table_name: "table name", Position.header: "column header"}


@unique
class EditorColumn(IntEnum):
    ROW_LABEL = 0
    POSITION = 1
    PIVOTED = 2
    NULLABLE = 3
    HEADER = 4
    FILTER = 5


class MappingEditorTableModel(QAbstractTableModel):
    MAPPING_ITEM_ROLE = Qt.ItemDataRole.UserRole + 1

    def __init__(self, mapping_name, root_mapping, undo_stack, mapping_provider, parent=None):
        """
        Args:
            mapping_name (str): mapping's name
            root_mapping (ExportMapping, optional): root mapping
            undo_stack (QUndoStack): undo stack
            mapping_provider (SpecificationEditorWindow): window that can provide data for different mappings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._root_mapping = None
        self._mappings = []
        self._mapping_colors = {}
        self._reset_mapping(root_mapping)
        self._non_leaf_mapping_is_pivoted = self._is_non_leaf_pivoted()
        self._undo_stack = undo_stack
        self._mapping_name = mapping_name
        self._mapping_provider = mapping_provider

    def _reset_mapping(self, root_mapping):
        """Sets the root mapping attribute, then updates mappings and colors."""
        self._root_mapping = root_mapping
        if self._root_mapping is None:
            self._mappings = []
            self._mapping_colors = {}
            return
        self._mappings = self._root_mapping.flatten()
        if self._mappings and isinstance(self._mappings[0], FixedValueMapping):
            # Pop the first element if it's a FixedValueMapping. We don't want to have the fixed table name here.
            self._mappings.pop(0)
        self._reset_colors(emit_data_changed=False)

    def _reset_colors(self, emit_data_changed=True):
        """Recalculates position column background colors.

        Args:
            emit_data_changed (boo): if True emits relevant dataChanged signal
        """
        positions = [m.position for m in self._mappings if isinstance(m.position, int)]
        self._mapping_colors = {p: color_from_index(i, len(positions)).lighter() for i, p in enumerate(positions)}
        if emit_data_changed:
            top_left = self.index(0, EditorColumn.POSITION)
            bottom_right = self.index(len(self._mappings), EditorColumn.POSITION)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.BackgroundRole])

    def mapping_colors(self):
        return self._mapping_colors

    def columnCount(self, paren=QModelIndex()):
        return len(EditorColumn)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            row = index.row()
            if column == EditorColumn.ROW_LABEL:
                mapping = self._mappings[row]
                return _names[type(mapping)]
            if column == EditorColumn.POSITION:
                if row == value_index(self._mappings) and self._non_leaf_mapping_is_pivoted:
                    return "in pivot"
                position = self._mappings[row].position
                if is_regular(position):
                    return str(position + 1)
                if is_pivoted(position):
                    return str(-position)
                return POSITION_DISPLAY_TEXT.get(position, "unrecognized")
            if column == EditorColumn.HEADER:
                return self._mappings[row].header
            if column == EditorColumn.FILTER:
                return self._mappings[row].filter_re
        elif role == Qt.ItemDataRole.CheckStateRole:
            if column == EditorColumn.PIVOTED:
                if is_pivoted(self._mappings[index.row()].position):
                    return Qt.CheckState.Checked
                return Qt.CheckState.Unchecked
            if column == EditorColumn.NULLABLE:
                return Qt.CheckState.Checked if self._mappings[index.row()].is_ignorable() else Qt.CheckState.Unchecked
        elif role == Qt.ItemDataRole.FontRole and column == EditorColumn.ROW_LABEL:
            font = QFont()
            font.setBold(True)
            return font
        elif role == Qt.ItemDataRole.BackgroundRole and column == EditorColumn.ROW_LABEL:
            m = self._mappings[index.row()]
            return self._mapping_colors.get(m.position, QColor(Qt.GlobalColor.gray).lighter())
        elif role == Qt.ItemDataRole.ToolTipRole:
            if column == EditorColumn.FILTER:
                return plain_to_rich("Regular expression to filter database items.")
            elif column == EditorColumn.NULLABLE:
                return plain_to_rich("When checked, ignore this row if it yields nothing to export.")
        if role == self.MAPPING_ITEM_ROLE:
            return self._mappings[index.row()]
        return None

    def flags(self, index=QModelIndex()):
        row = index.row()
        column = index.column()
        value_row = value_index(self._mappings)
        if row >= value_row and column == EditorColumn.PIVOTED:
            return super().flags(index) & ~Qt.ItemIsEnabled
        if column == EditorColumn.ROW_LABEL:
            return super().flags(index) & ~Qt.ItemIsSelectable
        if column in (EditorColumn.POSITION, EditorColumn.FILTER):
            return super().flags(index) | Qt.ItemIsEditable
        if column == EditorColumn.PIVOTED:
            return super().flags(index) | Qt.ItemIsUserCheckable
        if column == EditorColumn.HEADER:
            if self._mappings[row].position == Position.header:
                return super().flags(index) & ~Qt.ItemIsEnabled
            return super().flags(index) | Qt.ItemIsEditable
        if column == EditorColumn.NULLABLE:
            return super().flags(index) | Qt.ItemIsUserCheckable
        return super().flags(index)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ("Mapping type", "Map to", "Pivoted", "Nullable", "Header", "Filter")[section]
        return None

    def root_mapping(self):
        """
        Returns:
            Mapping: root mapping
        """
        return self._root_mapping

    def rowCount(self, parent=QModelIndex()):
        return len(self._mappings)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        column = index.column()
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            mapping = self._mappings[row]
            if column == EditorColumn.POSITION:
                return self._push_set_positions_command(value, row, mapping)
            if column == EditorColumn.HEADER:
                if value == mapping.header:
                    return False
                previous_header = mapping.header
                command = SetMappingProperty(
                    "change mapping item's header", self.set_header, self._mapping_name, row, value, previous_header
                )
                self._undo_stack.push(command)
                return True
            if column == EditorColumn.FILTER:
                if value == mapping.filter_re:
                    return False
                previous_filter_re = mapping.filter_re
                command = SetMappingProperty(
                    "change mapping item's filter",
                    self.set_filter_re,
                    self._mapping_name,
                    row,
                    value,
                    previous_filter_re,
                )
                self._undo_stack.push(command)
                return True
        elif role == Qt.ItemDataRole.CheckStateRole:
            if column == EditorColumn.PIVOTED:
                row = index.row()
                new_positions = _propose_toggled_pivot(self._mappings, row)
                previous_positions = [m.position for m in self._mappings]
                command = SetMappingPositions(self, self._mapping_name, new_positions, previous_positions)
                self._undo_stack.push(command)
                return True
            if column == EditorColumn.NULLABLE:
                row = index.row()
                nullable = self._mappings[row].is_ignorable()
                self._undo_stack.push(SetMappingNullable(self, self._mapping_name, row, not nullable))
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
        self._reset_mapping(root_mapping)
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
                value = Position.table_name
            elif value.startswith("h"):
                value = Position.hidden
            elif value.startswith("c"):
                value = Position.header
            else:
                return False
        if value == mapping.position and (row != value_index(self._mappings) or not self._non_leaf_mapping_is_pivoted):
            return False
        positions = _propose_positions(self._mappings, row, value)
        previous_positions = [m.position for m in self._mappings]
        command = SetMappingPositions(self, self._mapping_name, positions, previous_positions)
        self._undo_stack.push(command)
        return True

    def positions(self):
        """Returns mapping positions.

        Returns:
            list: positions
        """
        return [m.position for m in self._mappings]

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
        for row, (mapping, position) in enumerate(zip(self._mappings, positions)):
            if position != mapping.position:
                top = row
                bottom = min(bottom, row)
                if is_pivoted(position) or is_pivoted(mapping.position):
                    pivot_top = row
                    pivot_bottom = min(pivot_bottom, row)
                mapping.position = position
        top_left = self.index(top, EditorColumn.POSITION)
        bottom_right = self.index(bottom, EditorColumn.POSITION)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
        if pivot_bottom <= pivot_top:
            top_left = self.index(pivot_top, EditorColumn.PIVOTED)
            bottom_right = self.index(pivot_bottom, EditorColumn.PIVOTED)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])
        non_leaf_pivoted = self._is_non_leaf_pivoted()
        if non_leaf_pivoted != self._non_leaf_mapping_is_pivoted:
            self._non_leaf_mapping_is_pivoted = non_leaf_pivoted
            index = self.index(value_index(self._mappings), EditorColumn.POSITION)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
        self._reset_colors()

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
        index = self.index(row, EditorColumn.HEADER)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

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
        index = self.index(row, EditorColumn.FILTER)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def set_nullable(self, nullable, row, mapping_name):
        """
        Sets mapping filter_re for given row.

        Args:
            nullable (bool): mapping filter_re
            row (int): row index
            mapping_name (str): mapping's name
        """
        if mapping_name != self._mapping_name:
            self._mapping_provider.show_on_table(mapping_name)
        self._mappings[row].set_ignorable(nullable)
        index = self.index(row, EditorColumn.NULLABLE)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

    def _is_non_leaf_pivoted(self):
        """Checks if a non-leaf mapping is pivoted.

        Returns:
            bool: True if one or more non-leaf mappings are pivoted, False otherwise
        """
        return any(is_pivoted(m.position) for m in self._mappings[: value_index(self._mappings)])

    def can_compact(self):
        """Checks if the mapping can be compacted.

        Returns:
            bool: True if the mapping can be compacted, False otherwise
        """
        regular_positions = sorted([m.position for m in self._mappings if is_regular(m.position)])
        for i, position in enumerate(regular_positions):
            if i != position:
                return True
        pivoted_positions = sorted([m.position for m in self._mappings if is_pivoted(m.position)])
        for i, position in enumerate(pivoted_positions):
            if i != position:
                return True
        return False

    def compact(self):
        """Compacts the mapping."""
        if self._is_non_leaf_pivoted():
            value_row = value_index(self._mappings)
            pivoted_mappings = [
                (m.position, m) for row, m in enumerate(self._mappings) if is_pivoted(m.position) and row != value_row
            ]
            pivoted_mappings.sort(reverse=True, key=itemgetter(0))
            for row, item in enumerate(pivoted_mappings):
                item[1].position = -(row + 1)
            regular_mappings = [
                (m.position, m) for row, m in enumerate(self._mappings) if is_regular(m.position) and row != value_row
            ]
            last_column = max(regular_mappings, key=itemgetter(0), default=-1)[0]
            regular_mappings.append((last_column + 1, self._mappings[value_row]))
        else:
            regular_mappings = [(m.position, m) for m in self._mappings if is_regular(m.position)]
        regular_mappings.sort(key=itemgetter(0))
        for column, item in enumerate(regular_mappings):
            item[1].position = column
        top_left = self.index(0, EditorColumn.POSITION)
        bottom_right = self.index(self.rowCount() - 1, EditorColumn.POSITION)
        self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])
        self._reset_colors()


_names = {
    AlternativeDescriptionMapping: "Alternatives description",
    AlternativeMapping: "Alternatives",
    DefaultValueIndexNameMapping: "Default value index names",
    ExpandedParameterDefaultValueMapping: "Default values",
    ExpandedParameterValueMapping: "Parameter values",
    IndexNameMapping: "Parameter index names",
    EntityClassMapping: "Entity classes",
    EntityGroupMapping: "Entity groups",
    EntityGroupEntityMapping: "Entities",
    EntityMapping: "Entities",
    ElementMapping: "Elements",
    ParameterDefaultValueMapping: "Default values",
    ParameterDefaultValueIndexMapping: "Default value indexes",
    ParameterDefaultValueTypeMapping: "Default value types",
    ParameterDefinitionMapping: "Parameter definitions",
    ParameterValueIndexMapping: "Parameter indexes",
    ParameterValueListMapping: "Value lists",
    ParameterValueListValueMapping: "Value list values",
    ParameterValueMapping: "Parameter values",
    ParameterValueTypeMapping: "Value types",
    DimensionMapping: "Dimensions",
    ScenarioActiveFlagMapping: "Active flags",
    ScenarioAlternativeMapping: "Alternatives",
    ScenarioBeforeAlternativeMapping: "Before alternatives",
    ScenarioDescriptionMapping: "Scenarios description",
    ScenarioMapping: "Scenarios",
}


def _propose_toggled_pivot(mappings, toggled_index):
    """Proposes new positions after toggling a mapping's pivoted status.

    Args:
        mappings (list of Mapping): flattened mappings
        toggled_index (int): toggled index in mappings

    Returns:
        list of Position: positions after toggling
    """
    positions = [m.position for m in mappings]
    previous_position = positions[toggled_index]
    if previous_position in (Position.hidden, Position.table_name, Position.header):
        previous_position = 0
    new_position = -previous_position - 1
    if new_position < 0:
        positions[toggled_index] = new_position
        _remove_column(positions, previous_position)
    else:
        _insert_into_position(positions, toggled_index, new_position)
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
    if target_index == value_index(mappings):
        _turn_off_pivots(positions)
    if isinstance(new_position, int):
        _insert_into_position(positions, target_index, new_position)
    else:
        if new_position == Position.table_name:
            try:
                other_table_name_index = positions.index(Position.table_name)
            except ValueError:
                pass
            else:
                positions[other_table_name_index] = positions[target_index]
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
