######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains a model to handle source tables and import mapping."""
from __future__ import annotations

import pickle
import uuid
from dataclasses import dataclass, field
from enum import IntEnum, unique
import re

from PySide6.QtCore import QAbstractItemModel, QMimeData, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor, QFont
from spinetoolbox.helpers import plain_to_rich, list_to_rich_text, unique_name
from spinedb_api.parameter_value import join_value_and_type, split_value_and_type
from spinedb_api import from_database, ParameterValueFormatError
from spinedb_api.import_mapping.import_mapping import (
    default_import_mapping,
    EntityClassMapping,
    EntityMapping,
    EntityMetadataMapping,
    ScenarioBeforeAlternativeMapping,
)
from spinedb_api.import_mapping.import_mapping_compat import (
    parse_named_mapping_spec,
    import_mapping_from_dict,
    parameter_mapping_from_dict,
    parameter_default_value_mapping_from_dict,
    parameter_value_mapping_from_dict,
    unparse_named_mapping_spec,
)
from spinedb_api.import_mapping.type_conversion import FloatConvertSpec, StringConvertSpec, DateTimeConvertSpec
from spinedb_api.mapping import Position
from spinedb_api.mapping import to_dict as import_mapping_to_dict
from spinetoolbox.mvcmodels.shared import PARSED_ROLE
from ..commands import (
    MoveMappingInList,
    MoveTableInList,
    PasteMappings,
    RenameMapping,
    SetTableChecked,
    UpdateTableItem,
    SetMappingPositionType,
    SetMappingPosition,
    SetFilterRe,
)
from ..flattened_mappings import FlattenedMappings, VALUE_TYPES
from ..mapping_colors import ERROR_COLOR
from .mappings_model_roles import Role
from ..widgets.mime_types import MAPPING_LIST_MIME_TYPE, SOURCE_TABLE_LIST_MIME_TYPE

UNNAMED_TABLE_NAME = "<rename this to add table>"


@unique
class FlattenedColumn(IntEnum):
    NAME = 0
    POSITION_TYPE = 1
    POSITION = 2
    REGEXP = 3


@dataclass()
class SourceTableItem:
    """A list item for source tables."""

    name: str
    checked: bool
    checkable: bool = True
    editable: bool = False
    accepts_drags_and_drops: bool = True
    real: bool = True
    in_source: bool = False
    in_specification: bool = False
    empty: bool = False
    select_all: bool = False
    mapping_list: list[MappingListItem] = field(init=False, default_factory=list)
    id: uuid.UUID = field(init=False, default_factory=uuid.uuid4)

    def append_to_mapping_list(self, list_item):
        """Appends an item to mapping list.

        Args:
            list_item (MappingListItem): item
        """
        list_item.source_table_item = self
        self.mapping_list.append(list_item)

    def insert_to_mapping_list(self, row, list_item):
        """Inserts an item to mapping list.

        Args:
            row (int): insertion position
            list_item (MappingListItem): item
        """
        list_item.source_table_item = self
        self.mapping_list.insert(row, list_item)


@dataclass
class SourceTableMimeData:
    # We currently support only internal move, so we need just the id here.
    source_table_id: uuid.UUID


@dataclass
class MappingMimeData:
    name: str
    mapping_id: uuid.UUID
    mapping_dict: list[dict]


@dataclass
class MappingListMimeData:
    """Mime data for dragging and dropping."""

    source_table_name: str
    source_table_id: uuid.UUID
    mapping_list: list[MappingMimeData]


_dummy = object()


@dataclass()
class MappingListItem:
    """An item in mappings list."""

    name: str
    flattened_mappings: FlattenedMappings = field(init=False)
    source_table_item: SourceTableItem = field(init=False)
    id: uuid.UUID = field(init=False, default_factory=uuid.uuid4)

    def set_flattened_mappings(self, flattened_mappings):
        """Sets flattened mappings for this item.

        Args:
            flattened_mappings (FlattenedMappings): mappings
        """
        flattened_mappings.mapping_list_item = self
        self.flattened_mappings = flattened_mappings


class MappingsModel(QAbstractItemModel):
    """A tree model that manages source tables and their mappings."""

    msg_error = Signal(str)
    """Emitted when an error message should be displayed."""
    row_or_column_type_recommended = Signal(int, object, object)
    """Emitted when a change in mapping prompts for change in column or row type."""
    multi_column_type_recommended = Signal(object, object)
    """Emitted when all but given columns should be of given type."""

    _NOT_IN_SOURCE_COLOR = QColor(Qt.GlobalColor.gray)

    def __init__(self, undo_stack, parent):
        """
        Args:
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._undo_stack = undo_stack
        self._mappings = [self._make_select_all_tables_item()]
        self._add_table_row_font = QFont()
        self._add_table_row_font.setItalic(True)

    def __len__(self):
        return len(self._mappings)

    def has_empty_source_table_row(self):
        """Tests if source table list contains the empty row.

        Returns:
            bool: True if the last row is empty table, False otherwise
        """
        return self._mappings[-1].empty

    def real_table_names(self):
        """Returns real table names.

        Returns:
            list of str: real table names
        """
        return [i.name for i in self._mappings if i.real]

    def checked_table_names(self):
        """Returns checked table names.

        Returns:
            list of str: checked table names
        """
        return [i.name for i in self._mappings[1:] if i.checked]

    @staticmethod
    def _make_select_all_tables_item():
        """Creates the first source table list item.

        Returns:
            SourceTableItem: 'select all' item
        """
        return SourceTableItem("Select all", checked=True, accepts_drags_and_drops=False, real=False, select_all=True)

    def columnCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1
        parent_item = parent.internalPointer()
        if isinstance(parent_item, SourceTableItem):
            return 1
        if isinstance(parent_item, MappingListItem):
            return 4
        return 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        index_item = index.internalPointer()
        if isinstance(index_item, SourceTableItem):
            return self._table_list_data(index, role)
        if isinstance(index_item, MappingListItem):
            return self._mapping_list_data(index_item, role)
        if isinstance(index_item, FlattenedMappings):
            return self._mapping_data(index_item, index, role)
        return None

    def _table_list_data(self, index, role):
        """Returns source table data for given role.

        Args:
            index (QModelIndex): table index
            role (int): Qt's data role

        Returns:
            Any: data
        """
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            list_item = self._mappings[row]
            if row == 0 or list_item.in_specification or list_item.empty:
                return list_item.name
            return list_item.name + " (new)"
        if role == Qt.ItemDataRole.EditRole:
            return self._mappings[index.row()].name
        if role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if self._mappings[index.row()].checked else Qt.CheckState.Unchecked
        if role == Qt.ItemDataRole.ForegroundRole:
            row = index.row()
            item = self._mappings[row]
            return self._NOT_IN_SOURCE_COLOR if row > 0 and (not item.in_source and not item.empty) else None
        if role == Qt.ItemDataRole.ToolTipRole:
            row = index.row()
            if row == 0:
                return None
            list_item = self._mappings[row]
            if not list_item.empty:
                if not list_item.in_source:
                    return plain_to_rich("Table isn't in source data.")
                if not list_item.in_specification:
                    return plain_to_rich("Table's mappings haven't been saved with the specification yet.")
            return None
        if role == Qt.ItemDataRole.FontRole:
            return self._add_table_row_font if self._mappings[index.row()].empty else None
        if role == Role.ITEM:
            return self._mappings[index.row()]
        return None

    @staticmethod
    def _mapping_list_data(list_item, role):
        """Returns mapping list data for given role.

        Args:
            list_item (MappingListItem): list item
            role (int): Qt's data role

        Returns:
            Any: data
        """
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return list_item.name
        if role == Role.ITEM:
            return list_item
        if role == Role.FLATTENED_MAPPINGS:
            return list_item.flattened_mappings
        return None

    @staticmethod
    def _mapping_data(flattened_mappings, index, role):
        """Returns mapping component data for given role.

        Args:
            flattened_mappings (FlattenedMappings): flattened mappings
            index (QModelIndex): component index
            role (int): Qt's data role

        Returns:
            Any: data
        """
        if role == PARSED_ROLE:
            # Only used for the ParameterValueEditor.
            # At this point, the delegate has already checked that it's a constant parameter (default) value mapping
            m = flattened_mappings.component_at(index.row())
            try:
                return from_database(*split_value_and_type(m.value))
            except ParameterValueFormatError:
                return None
        column = index.column()
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if column == FlattenedColumn.NAME:
                return flattened_mappings.display_names[index.row()]
            if column == FlattenedColumn.POSITION_TYPE:
                return flattened_mappings.display_position_type(index.row())
            if column == FlattenedColumn.POSITION:
                display = flattened_mappings.display_position(index.row())
                if display == "<table name>":
                    return flattened_mappings.mapping_list_item.source_table_item.name
                return display
            if column == FlattenedColumn.REGEXP:
                return flattened_mappings.component_at(index.row()).filter_re
            raise RuntimeError("Column out of bounds.")
        if role == Qt.ItemDataRole.BackgroundRole:
            if column == FlattenedColumn.NAME:
                return flattened_mappings.display_colors[index.row()]
            if column == FlattenedColumn.POSITION:
                issues = flattened_mappings.display_row_issues(index.row())
                if issues:
                    return ERROR_COLOR
                return None
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == FlattenedColumn.POSITION:
                issues = flattened_mappings.display_row_issues(index.row())
                return list_to_rich_text(issues) if issues else None
            if column == FlattenedColumn.REGEXP:
                return plain_to_rich("Enter regular expression to filter importer data.")
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return ("Target", "Source type", "Source ref.", "Filter")[section]
        return None

    def flags(self, index):
        index_item = index.internalPointer()
        if index_item is None:
            return super().flags(index) | Qt.ItemFlag.ItemIsDropEnabled
        if isinstance(index_item, SourceTableItem):
            return self._table_list_flags(index)
        if isinstance(index_item, MappingListItem):
            return self._mapping_list_flags()
        if isinstance(index_item, FlattenedMappings):
            return self._mapping_flags(index_item, index)
        return super().flags(index)

    def _table_list_flags(self, index):
        """Returns flags for source table list.

        Args:
            index (QModelIndex): index

        Returns:
            int: flags
        """
        flags = Qt.ItemFlag.ItemIsEnabled
        table_item = self._mappings[index.row()]
        if table_item.checkable:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        if table_item.editable:
            flags |= Qt.ItemFlag.ItemIsEditable
        if table_item.accepts_drags_and_drops:
            flags |= Qt.ItemFlag.ItemIsDragEnabled
            flags |= Qt.ItemFlag.ItemIsDropEnabled
        if not table_item.select_all:
            flags |= Qt.ItemFlag.ItemIsSelectable
        return flags

    @staticmethod
    def _mapping_list_flags():
        """Returns flags for mapping list data.

        Returns:
            Qt.ItemFlag: flags
        """
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
        )

    @staticmethod
    def _mapping_flags(flattened_item, index):
        """Returns flags for mapping components.

        Args:
            flattened_item (FlattenedMappings): flattened mappings
            index (QModelIndex): index

        Returns:
            int: flags
        """
        non_editable = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        editable = non_editable | Qt.ItemIsEditable
        column = index.column()
        if column == FlattenedColumn.NAME:
            return non_editable
        if flattened_item.root_mapping.is_pivoted():
            # special case where we have pivoted data
            row = index.row()
            if row > 0 and row == len(flattened_item.display_names) - 1:
                return non_editable
        if column == FlattenedColumn.POSITION:
            component = flattened_item.component_at(index.row())
            if component.value is None and component.position == Position.header:
                return non_editable
        return editable

    def mimeTypes(self):
        return [SOURCE_TABLE_LIST_MIME_TYPE, MAPPING_LIST_MIME_TYPE]

    def mimeData(self, indexes):
        if not indexes:
            return QMimeData()
        items = [i.internalPointer() for i in indexes]
        if isinstance(items[0], SourceTableItem):
            mime_type = SOURCE_TABLE_LIST_MIME_TYPE
            if not all(isinstance(item, SourceTableItem) for item in items[1:]):
                raise RuntimeError("Logic error: not all indexes are SourceTableItems.")
            data = self._source_table_list_mime_data(items)
        elif isinstance(items[0], MappingListItem):
            mime_type = MAPPING_LIST_MIME_TYPE
            source_table_name = items[0].source_table_item.name
            source_table_id = items[0].source_table_item.id
            if not all(isinstance(item, MappingListItem) for item in items[1:]):
                raise RuntimeError("Logic error: not all indexes are MappingListItems.")
            if not all(item.source_table_item.id == source_table_id for item in items[1:]):
                raise RuntimeError("Logic error: not all MappingListItems come from same source table.")
            data = self._mapping_list_mime_data(source_table_name, source_table_id, items)
        else:
            raise RuntimeError("Logic error: drag and drop not supported for given indexes")
        mime_data = QMimeData()
        mime_data.setData(mime_type, pickle.dumps(data))
        return mime_data

    @staticmethod
    def _source_table_list_mime_data(items):
        """Creates MIME data for source table items.

        Args:
            items (Iterable of SourceTableItem): items

        Returns:
            MappingListMimeData: MIME data
        """

        data = []
        for item in items:
            data.append(SourceTableMimeData(item.id))
        return data

    @staticmethod
    def _mapping_list_mime_data(source_table_name, source_table_id, items):
        """Creates MIME data for mapping items that are all from a single source table.

        Args:
            source_table_name (str): name of the source table
            source_table_id (uuid.UUID): id of the source table
            items (Iterable of MappingListItem): items

        Returns:
            MappingListMimeData: MIME data
        """
        mapping_mime_data_list = []
        for item in items:
            mapping_mime_data_list.append(
                MappingMimeData(
                    item.name,
                    item.id,
                    import_mapping_to_dict(item.flattened_mappings.root_mapping),
                )
            )
        return MappingListMimeData(source_table_name, source_table_id, mapping_mime_data_list)

    def canDropMimeData(self, data, action, row, column, parent):
        if not any(data.hasFormat(mime_type) for mime_type in self.mimeTypes()):
            return False
        parent_item = parent.internalPointer()
        if data.hasFormat(SOURCE_TABLE_LIST_MIME_TYPE):
            if parent_item is not None:
                return False
            if row == 0:
                return False
            if self.has_empty_source_table_row() and (row == -1 or row == len(self._mappings)):
                return False
            return True
        if not isinstance(parent_item, SourceTableItem):
            return False
        mapping_list_data: MappingListMimeData = pickle.loads(data.data(MAPPING_LIST_MIME_TYPE))
        source_table: SourceTableItem = parent.internalPointer()
        is_internal_move = source_table.id == mapping_list_data.source_table_id
        if is_internal_move and row == -1:
            return False
        return True

    def dropMimeData(self, data, action, row, column, parent):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False
        if data.hasFormat(SOURCE_TABLE_LIST_MIME_TYPE):
            return self._drop_source_table_list(data, row)
        if data.hasFormat(MAPPING_LIST_MIME_TYPE):
            return self._drop_mappings_list(data, row, parent)
        raise RuntimeError(f"Logic error: unknown mime types {data.formats()}")

    def _drop_source_table_list(self, data, row):
        """Drops source table list.

        Args:
            data (QMimeData): MIME data
            row (int): target row index

        Returns:
            bool: True if operation was successful, False otherwise
        """
        source_table_list_data: list[SourceTableMimeData] = pickle.loads(data.data(SOURCE_TABLE_LIST_MIME_TYPE))
        moves = []
        # We support internal moves only currently.
        while source_table_list_data:
            source_table_data = source_table_list_data.pop(0)
            for i, source_table in enumerate(self._mappings[1:]):
                if source_table.id == source_table_data.source_table_id:
                    table_row = i + 1
                    # Ensure we're not dropping on the same spot.
                    if table_row != row and table_row != row - 1:
                        moved_from_above = len(
                            [source for source, destination in moves if source < table_row < destination]
                        )
                        moves.append((table_row - moved_from_above, row))
                        row = row if row > table_row else row + 1
                    break
        if not moves:
            return False
        self._undo_stack.beginMacro("change the order of tables")
        for source_row, target_row in moves:
            self._undo_stack.push(MoveTableInList(self, source_row, target_row))
        self._undo_stack.endMacro()
        return True

    def _drop_mappings_list(self, data, row, parent):
        """Drops mapping list.

        Args:
            data (QMimeData): MIME data
            row (int): target row index
            parent (QModelIndex): target index

        Returns:
            bool: True if operation was successful, False otherwise
        """
        source_table: SourceTableItem = parent.internalPointer()
        mapping_list_data: MappingListMimeData = pickle.loads(data.data(MAPPING_LIST_MIME_TYPE))
        is_internal_move = source_table.id == mapping_list_data.source_table_id
        if is_internal_move:
            moves = []
            while mapping_list_data.mapping_list:
                mapping_data = mapping_list_data.mapping_list.pop(0)
                for i, mapping in enumerate(source_table.mapping_list):
                    if mapping.id == mapping_data.mapping_id:
                        # Ensure we're not dropping on the same spot.
                        if i != row and i != row - 1:
                            moved_from_above = len(
                                [source for source, destination in moves if source < i < destination]
                            )
                            moves.append((i - moved_from_above, row))
                            row = row if row > i else row + 1
                        break
            if not moves:
                return False
            self._undo_stack.beginMacro("change the order of mappings")
            source_table_row = parent.row()
            for source_row, target_row in moves:
                self._undo_stack.push(MoveMappingInList(source_table_row, self, source_row, target_row))
            self._undo_stack.endMacro()
        else:
            if row == -1:
                row = len(source_table.mapping_list)
            self._undo_stack.push(PasteMappings(parent.row(), row, self, mapping_list_data, "drop mappings"))
        return True

    def insert_mapping_mime_data(self, table_row, list_row, mapping_list_data):
        """Inserts mapping mime data to mapping list

        Args:
            table_row (int): index to source table list
            list_row (int): index to mapping list
            mapping_list_data (list of MappingMimeData): mappings to insert
        """
        parent = self.index(table_row, 0)
        source_table: SourceTableItem = parent.internalPointer()
        self.beginInsertRows(parent, list_row, list_row + len(mapping_list_data) - 1)
        for i, mapping_data in enumerate(mapping_list_data):
            mapping_item = MappingListItem(mapping_data.name)
            flattened_mappings = FlattenedMappings(import_mapping_from_dict(mapping_data.mapping_dict))
            mapping_item.set_flattened_mappings(flattened_mappings)
            source_table.insert_to_mapping_list(list_row + i, mapping_item)
        self.endInsertRows()

    def index(self, row, column, parent=QModelIndex()):
        if row < 0 or column < 0:
            return QModelIndex()
        if not parent.isValid():
            return self.createIndex(row, 0, self._mappings[row])
        parent_item = parent.internalPointer()
        if isinstance(parent_item, SourceTableItem):
            return self.createIndex(row, 0, parent_item.mapping_list[row])
        if isinstance(parent_item, MappingListItem):
            return self.createIndex(row, column, parent_item.flattened_mappings)
        raise RuntimeError("Cannot create index.")

    @staticmethod
    def is_table_index(index):
        """Checks if given index is an index to source table list.

        Args:
            index (QModelIndex): index

        Returns:
            bool: True if index is table index, False otherwise
        """
        return isinstance(index.internalPointer(), SourceTableItem)

    @staticmethod
    def is_mapping_list_index(index):
        """Checks if given index is an index to mapping list.

        Args:
            index (QModelIndex): index

        Returns:
            bool: True if index is mapping list index, False otherwise
        """
        return isinstance(index.internalPointer(), MappingListItem)

    def dummy_parent(self):
        """Creates a dummy parent index that always returns an empty table.

        Returns:
            QModelIndex: dummy index
        """
        return self.createIndex(0, 0, _dummy)

    def parent(self, index):
        index_item = index.internalPointer()
        if isinstance(index_item, SourceTableItem):
            return QModelIndex()
        if isinstance(index_item, MappingListItem):
            for table_row, table_item in enumerate(self._mappings):
                if index_item.source_table_item is table_item:
                    return self.createIndex(table_row, 0, table_item)
        elif isinstance(index_item, FlattenedMappings):
            for list_row, list_item in enumerate(index_item.mapping_list_item.source_table_item.mapping_list):
                if index_item is list_item.flattened_mappings:
                    return self.createIndex(list_row, 0, list_item)
        elif index_item is _dummy:
            return QModelIndex()
        raise RuntimeError("Cannot create parent index.")

    def hasChildren(self, parent=QModelIndex()):
        if not QModelIndex().isValid():
            return True
        index_item = parent.internalPointer()
        if isinstance(index_item, SourceTableItem):
            return bool(index_item.mapping_list)
        if isinstance(index_item, MappingListItem):
            return True
        return False

    def store(self):
        """Stores source tables, mappings lists and mappings to a dict.

        Returns:
            dict: stored data
        """
        table_dicts = dict()
        for table_item in self._mappings[1:]:
            if not table_item.real:
                continue
            table_dicts[table_item.name] = [
                unparse_named_mapping_spec(list_item.name, list_item.flattened_mappings.root_mapping)
                for list_item in table_item.mapping_list
            ]
        selected_tables = self.checked_table_names()
        return {"table_mappings": table_dicts, "selected_tables": selected_tables}

    def restore(self, mappings_dict):
        """Restores source tables, mapping lists and mappings.

        Args:
            mappings_dict (dict): serialized data
        """
        checked_tables = mappings_dict.get("selected_tables")
        self.beginResetModel()
        self._mappings.clear()
        self._mappings.append(self._make_select_all_tables_item())
        try:
            for table_name, mapping_list_dicts in mappings_dict.get("table_mappings", {}).items():
                checked = table_name in checked_tables if checked_tables is not None else True
                table_item = SourceTableItem(table_name, checked, in_specification=True)
                for list_dict in mapping_list_dicts:
                    mapping_name, root_mapping = parse_named_mapping_spec(list_dict)
                    flattened_mappings = FlattenedMappings(root_mapping)
                    list_item = MappingListItem(mapping_name)
                    list_item.set_flattened_mappings(flattened_mappings)
                    table_item.append_to_mapping_list(list_item)
                self._mappings.append(table_item)
        except ValueError as error:
            # This will be raised by parse_named_mapping_spec() if mapping type is obsolete, like tool, feature, etc.
            self.msg_error.emit(f"{error}")
            return
        self.endResetModel()
        self._update_all_checked()

    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self._mappings)
        parent_item = parent.internalPointer()
        if isinstance(parent_item, SourceTableItem):
            return len(parent_item.mapping_list)
        if isinstance(parent_item, MappingListItem):
            if parent_item.flattened_mappings is None:
                return 0
            return len(parent_item.flattened_mappings.display_names)
        return 0

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        index_item = index.internalPointer()
        if isinstance(index_item, SourceTableItem):
            return self._set_table_list_data(index_item, index, value, role)
        if isinstance(index_item, MappingListItem):
            return self._set_mapping_list_data(index_item, index, value, role)
        if isinstance(index_item, FlattenedMappings):
            return self._set_mapping_data(index_item, index, value, role)
        raise RuntimeError("Unknown parent type.")

    def _set_table_list_data(self, table_item, index, value, role):
        """Sets data for source table list.

        Args:
            table_item (SourceTableItem): table item
            index (QModelIndex): index
            value (Any): value to set
            role (int): Qt's data role

        Returns:
            bool: True if data was set successfully, False otherwise
        """
        row = index.row()
        if role == Qt.ItemDataRole.CheckStateRole and table_item.checkable:
            checked = value == Qt.CheckState.Checked.value
            if row == 0:
                self._set_multiple_checked_undoable(checked, *range(len(self._mappings)))
            else:
                self._undo_stack.push(SetTableChecked(table_item.name, self, checked, row))
            return True
        if role == Qt.ItemDataRole.EditRole:
            if value == table_item.name:
                return False
            if value in {table.name for table in self._mappings if table.real}:
                self.msg_error.emit(f"There's already a table called {value}.")
                return False
            previous = {"name": table_item.name}
            updates = {"name": value}
            self._undo_stack.push(UpdateTableItem(self, row, previous, updates, table_item.empty))
            return True
        return False

    def _set_mapping_list_data(self, list_item, index, value, role):
        """Sets data for mapping list.

        Args:
            list_item (MappingListItem): list item
            index (QModelIndex): index
            value (Any): value to set
            role (int): Qt's data role

        Returns:
            bool: True if data was set successfully, False otherwise
        """
        if role == Qt.ItemDataRole.EditRole:
            if not value or value in {m.name for m in list_item.source_table_item.mapping_list}:
                return False
            previous = list_item.name
            parent_index = index.parent()
            self._undo_stack.push(RenameMapping(parent_index.row(), index.row(), self, value, previous))
            return True
        return False

    def update_table_item(self, row, data_dict, add_empty_row=False, remove_empty_row=False):
        """Updates table item.

         This only happens in file-less mode, when the user is creating tables.

        Args:
            row (int): item row
            data_dict (dict): table item data to update
            add_empty_row (bool): whether to add an empty row
            remove_empty_row (bool): whether to remove the empty row
        """
        table_item = self._mappings[row]
        for field_name, value in data_dict.items():
            setattr(table_item, field_name, value)
        index = self.index(row, 0)
        if add_empty_row:
            table_item.real = True
            table_item.checkable = True
            table_item.checked = self._mappings[0].checked
            table_item.accepts_drags_and_drops = True
            table_item.empty = False
            table_item.in_source = True
            default_flattened_mappings = FlattenedMappings(self.create_default_mapping())
            mapping_list_item = MappingListItem(self._unique_mapping_name(table_item))
            mapping_list_item.set_flattened_mappings(default_flattened_mappings)
            self.beginInsertRows(index, 0, 0)
            table_item.append_to_mapping_list(mapping_list_item)
            self.endInsertRows()
            self.add_empty_row()
        if remove_empty_row:
            table_item.real = False
            table_item.checkable = False
            table_item.checked = False
            table_item.accepts_drags_and_drops = False
            table_item.empty = True
            table_item.in_source = False
            self.beginRemoveRows(index, 0, len(table_item.mapping_list) - 1)
            table_item.mapping_list.clear()
            self.endRemoveRows()
            self._remove_last_source_table()
        self.dataChanged.emit(index, index)

    def toggle_checked_tables(self, table_indexes):
        """Toggles the checked status of source tables.

        Args:
            table_indexes (Iterable of QModelIndex): indexes
        """
        table_items = ((i.row(), self._mappings[i.row()]) for i in table_indexes)
        checkables = [i for i in table_items if i[1].checkable and i[1].real]
        all_checked = all(i[1].checked for i in checkables)
        self._set_multiple_checked_undoable(not all_checked, *(i[0] for i in checkables))

    def _set_multiple_checked_undoable(self, checked, *rows):
        """
        Sets the checked status of multiple list items.

        This action is undoable.

        Args:
            checked (bool): True for checked, False for unchecked
            *rows: item rows
        """
        rows = [row for row in rows if self._mappings[row].checked != checked]
        self._undo_stack.push(SetTableChecked(None, self, checked, *rows))

    def set_table_checked(self, checked, *rows):
        """
        Sets the checked status of a source table item.

        Args:
            checked (bool): True for checked, False for unchecked
            *rows: item rows
        """
        min_row = None
        max_row = None
        for row in rows:
            if not self._mappings[row].checkable or self._mappings[row].checked == checked:
                continue
            if min_row is None:
                min_row = row
                max_row = row
            else:
                min_row = min(row, min_row)
                max_row = max(row, max_row)
            self._mappings[row].checked = checked
        if min_row is not None:
            top_left = self.index(min_row, 0)
            bottom_right = self.index(max_row, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.CheckStateRole])
        self._update_all_checked()

    def _update_all_checked(self):
        """Updates the checked state of 'Select All' table item if needed."""
        checkables = tuple(m for m in self._mappings[1:] if m.checkable)
        if not checkables:
            return
        all_checked = all(m.checked for m in checkables)
        all_checked_item = self._mappings[0]
        if all_checked_item.checked != all_checked:
            self._mappings[0].checked = all_checked
            index = self.index(0, 0)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])

    def append_new_table_with_mapping(self, table_name, root_mapping):
        """Appends a new source table and adds given ``root_mapping`` as its first mapping.

        Args:
            table_name (str): table name
            root_mapping (ImportMapping, optional): initial mapping
        """
        has_root_mapping = root_mapping is not None
        if not has_root_mapping:
            root_mapping = self.create_default_mapping()
        flattened_mappings = FlattenedMappings(root_mapping)
        list_item = MappingListItem("Mapping 1")
        list_item.set_flattened_mappings(flattened_mappings)
        table_item = SourceTableItem(
            table_name, checked=self._mappings[0].checked, in_source=True, in_specification=has_root_mapping
        )
        table_item.append_to_mapping_list(list_item)
        insertion_point = len(self._mappings) - (1 if self.has_empty_source_table_row() else 0)
        self.beginInsertRows(QModelIndex(), insertion_point, insertion_point)
        self._mappings.insert(insertion_point, table_item)
        self.endInsertRows()

    def _remove_last_source_table(self):
        """Removes the last source table."""
        self.beginRemoveRows(QModelIndex(), self.rowCount() - 1, self.rowCount() - 1)
        del self._mappings[-1]
        self.endRemoveRows()

    def rename_mapping(self, table_row, list_row, name):
        """
        Renames a mapping.

        Args:
            table_row (int): source table row
            list_row (int): mapping list row
            name (str): new name
        """
        table_item = self._mappings[table_row]
        list_item = table_item.mapping_list[list_row]
        if name == list_item.name:
            return
        list_item.name = ""
        if self.has_mapping_name(table_row, name):
            match = re.search(r" [0-9]+$", name)
            prefix = name[: match.start()] if match is not None else name
            name = self._unique_mapping_name(table_item, prefix)
        list_item.name = name
        parent = self.index(table_row, 0)
        index = self.index(list_row, 0, parent)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    def set_root_mapping(self, table_row, list_row, root_mapping):
        """
        Sets new root mapping.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            root_mapping (ImportMapping): root mapping
        """
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        self.beginRemoveRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = None
        self.endRemoveRows()
        flattened_mappings.set_root_mapping(root_mapping)
        self.beginInsertRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = flattened_mappings
        self.endInsertRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_mappings_type(self, table_row, list_row, new_type):
        """
        Sets the type for mappings.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            new_type (str): name of the type
        """
        map_type = {
            "Entity class": "EntityClass",
            "Entity group": "EntityGroup",
            "Alternative": "Alternative",
            "Scenario": "Scenario",
            "Scenario alternative": "ScenarioAlternative",
            "Parameter value list": "ParameterValueList",
        }[new_type]
        root_mapping = default_import_mapping(map_type)
        self.set_root_mapping(table_row, list_row, root_mapping)

    def _set_mapping_data(self, flattened_mappings, index, value, role):
        """Sets data for mapping components.

        Args:
            flattened_mappings (FlattenedMappings): component's mapping list
            index (QModelIndex): index
            value (Any): value to set
            role (int): Qt's data role

        Returns:
            bool: True if data was set successfully, False otherwise
        """
        if role != Qt.ItemDataRole.EditRole:
            return False
        column = index.column()
        if column < FlattenedColumn.POSITION_TYPE:
            return False
        row = index.row()
        current_type = flattened_mappings.display_position_type(row)
        current_position = flattened_mappings.display_position(row)
        if column == FlattenedColumn.POSITION_TYPE:
            if value == current_type:
                return False
            parent_index = index.parent()
            mapping_list_row = parent_index.row()
            table_row = parent_index.parent().row()
            self._undo_stack.push(
                SetMappingPositionType(table_row, mapping_list_row, row, self, value, current_type, current_position)
            )
            return True
        if column == FlattenedColumn.POSITION:
            if current_type != "None":
                if value == current_position:
                    return False
                parent_index = index.parent()
                mapping_list_row = parent_index.row()
                table_row = parent_index.parent().row()
                self._undo_stack.push(
                    SetMappingPosition(
                        table_row, mapping_list_row, row, self, current_type, value, current_type, current_position
                    )
                )
                return True
            # If type is "None", set it to something reasonable to try and help users
            try:
                value = int(value)
            except ValueError:
                pass
            if isinstance(value, int):
                return self.change_component_mapping(flattened_mappings, index, "Column", value)
            elif isinstance(value, str):
                return self.change_component_mapping(flattened_mappings, index, "Constant", value)
        if column == FlattenedColumn.REGEXP:
            parent_index = index.parent()
            mapping_list_row = parent_index.row()
            table_row = parent_index.parent().row()
            current_re = flattened_mappings.component_at(row).filter_re
            self._undo_stack.push(SetFilterRe(table_row, mapping_list_row, row, self, value, current_re))
            return True
        return False

    def get_set_data_delayed(self, index):
        """Returns a function that ParameterValueEditor can call to set data for the given index at any later time,
        even if the model changes.

        Args:
            index (QModelIndex): model index

        Returns:
            Callable: callback for parameter value editor
        """
        return lambda value_type_tup, index=index: self.setData(index, join_value_and_type(*value_type_tup))

    @staticmethod
    def index_name(index):
        """Returns identifier for parameter value editor's title.

        Returns:
            str: 'index' name
        """
        return index.siblingAtColumn(0).data()

    def set_relationship_dimension_count(self, table_row, list_row, dimension_count):
        """Sets relationship dimension count.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            dimension_count (int): dimension count
        """
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        self.beginRemoveRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = None
        self.endRemoveRows()
        flattened_mappings.set_dimension_count(dimension_count)
        self.beginInsertRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = flattened_mappings
        self.endInsertRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_map_dimension_count(self, table_row, list_row, dimension_count):
        """
        Sets map dimension_count.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            dimension_count (int): new map dimension_count
        """
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        self.beginRemoveRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = None
        self.endRemoveRows()
        flattened_mappings.set_map_dimension_count(dimension_count)
        self.beginInsertRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = flattened_mappings
        self.endInsertRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_map_compress(self, table_row, list_row, compress):
        """
        Sets the compress flag for Map type parameters.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            compress (bool): flag value
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_map_compress(compress)
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_parameter_type(self, table_row, list_row, new_type):
        """Changes parameter type.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            new_type (str): parameter type
        """
        if new_type == "None":
            parameter_root = None
        elif new_type == "Value":
            parameter_root = parameter_mapping_from_dict({"map_type": "ParameterValue"})
        elif new_type == "Definition":
            parameter_root = parameter_mapping_from_dict({"map_type": "ParameterDefinition"})
        else:
            raise RuntimeError(f"Unknown parameter type '{new_type}'")
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        self.beginRemoveRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = None
        self.endRemoveRows()
        flattened_mappings.set_parameter_components(parameter_root)
        self.beginInsertRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = flattened_mappings
        self.endInsertRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_value_type(self, table_row, list_row, new_type):
        """Changes parameter value's type.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            new_type (str): value type
        """
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        if new_type == "None":
            value_mappings = None
        else:
            value_type = VALUE_TYPES[new_type]
            parameter_type = flattened_mappings.display_parameter_type()
            if parameter_type == "Definition":
                value_mappings = parameter_default_value_mapping_from_dict({"value_type": value_type})
            elif parameter_type == "Value":
                value_mappings = parameter_value_mapping_from_dict({"value_type": value_type})
            else:
                raise RuntimeError(f"Unknown value type '{value_type}'")
        self.beginRemoveRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = None
        self.endRemoveRows()
        flattened_mappings.set_value_components(value_mappings)
        self.beginInsertRows(list_index, 0, len(flattened_mappings.display_names) - 1)
        mapping_list.flattened_mappings = flattened_mappings
        self.endInsertRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def change_component_mapping(self, flattened_mappings, index, new_type, new_ref):
        """
        Pushes :class:`SetComponentMappingType` to the undo stack.

        Args:
            flattened_mappings (FlattenedMappings): flattened mappings
            index (QModelIndex): flattened mappings index
            new_type (str): name of the new type
            new_ref (str or int): component mapping reference

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        row = index.row()
        previous_type = flattened_mappings.display_position_type(row)
        previous_ref = flattened_mappings.display_position(row)
        parent_index = index.parent()
        mapping_list_row = parent_index.row()
        table_row = parent_index.parent().row()
        commands = list()
        if new_type != previous_type:
            commands.append(
                SetMappingPositionType(table_row, mapping_list_row, row, self, new_type, previous_type, previous_ref)
            )
        if new_ref != previous_ref:
            commands.append(
                SetMappingPosition(
                    table_row, mapping_list_row, row, self, new_type, new_ref, previous_type, previous_ref
                )
            )
        if not commands:
            return False
        self._undo_stack.beginMacro("mapping type and reference change")
        for command in commands:
            self._undo_stack.push(command)
        self._undo_stack.endMacro()
        return True

    def set_mapping_position_type(self, table_row, list_row, row, position_type):
        """Modifies mapping component's position type.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            position_type (str): new type
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_display_position_type(row, position_type)
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        top_left = self.index(row, 1, list_index)
        bottom_right = self.index(self.rowCount(list_index) - 1, 2, list_index)
        self.dataChanged.emit(
            top_left,
            bottom_right,
            [Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole],
        )

    def set_mapping_position(self, table_row, list_row, row, position_type, position):
        """Modifies mapping component's position

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            position_type (str): new type
            position (str or int): new position
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_display_position(row, position_type, position)
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        top_left = self.index(row, 1, list_index)
        bottom_right = self.index(self.rowCount(list_index) - 1, 2, list_index)
        self.dataChanged.emit(
            top_left,
            bottom_right,
            [Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole],
        )
        self._recommend_source_table_column_or_row_types(flattened_mappings, row)

    def set_import_entities(self, table_row, list_row, import_entities):
        """Sets the import entities flag.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            import_entities (bool): flag value
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_import_entities(import_entities)
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_use_before_alternative(self, table_row, list_row, use_before_alternative):
        """Sets the use before alternative flag.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            use_before_alternative (bool): flag value
        """
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        mapping_list = self._mappings[table_row].mapping_list[list_row]
        flattened_mappings = mapping_list.flattened_mappings
        if use_before_alternative:
            before_alternative_mapping = ScenarioBeforeAlternativeMapping(Position.hidden)
            self.beginInsertRows(list_index, 2, 2)
            flattened_mappings.append_tail_component(before_alternative_mapping)
            self.endInsertRows()
        else:
            self.beginRemoveRows(list_index, 2, 2)
            flattened_mappings.cut_tail_component()
            self.endRemoveRows()
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_read_start_row(self, table_row, list_row, start_row):
        """Sets mappings' read start row.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            start_row (int): read start row
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_read_start_row(start_row)
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_skip_columns(self, table_row, list_row, skip_columns):
        """Sets mappings' read start row.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            skip_columns (list): skipped column indexes or names
        """
        if skip_columns is None:
            skip_columns = []
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.set_skip_columns(sorted(list(set(skip_columns))))
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_time_series_repeat_flag(self, table_row, list_row, repeat):
        """Sets the repeat time series flag.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            repeat (bool): flag value
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        if not flattened_mappings.is_time_series_value():
            return
        flattened_mappings.value_mapping().options["repeat"] = repeat
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        self.dataChanged.emit(list_index, list_index, [Role.FLATTENED_MAPPINGS])

    def set_filter_re(self, table_row, list_row, row, filter_re):
        """Sets filter regular expression.

        Args:
            table_row (int): source table row index
            list_row (int): mapping list row index
            row (int): mapping component row index
            filter_re (str): filter regular expression
        """
        flattened_mappings = self._mappings[table_row].mapping_list[list_row].flattened_mappings
        flattened_mappings.component_at(row).filter_re = filter_re
        table_index = self.index(table_row, 0)
        list_index = self.index(list_row, 0, table_index)
        index = self.index(row, FlattenedColumn.REGEXP, list_index)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    @staticmethod
    def check_validity_of_columns(list_index, header):
        """Checks that the mapping doesn't have column refs
        that are larger than the source table column count

        Args:
            list_index (QModelIndex): index to mappings list
            header (Iterable): source table header
        Returns:
            bool: True if no source ref. is out of range, False otherwise
        """
        mapping_list_item = list_index.internalPointer()
        table_name = mapping_list_item.source_table_item.name
        return mapping_list_item.flattened_mappings.root_mapping.check_for_invalid_column_refs(header, table_name)

    @staticmethod
    def polish_mapping(list_index, header):
        """Polishes flattened mappings.

        Args:
            list_index (QModelIndex): index to mappings list
            header (Iterable): source table header
        """
        mapping_list_item = list_index.internalPointer()
        table_name = mapping_list_item.source_table_item.name
        mapping_list_item.flattened_mappings.root_mapping.polish(table_name, header, for_preview=True)
        # We don't emit dataChanged here as polishing is just beautification and
        # it would mess up the undo system which relies on real changes.

    def _recommend_source_table_column_or_row_types(self, flattened_mappings, row):
        """Checks if source table conversion specifications need an update.

        Args:
            flattened_mappings (FlattenedMappings): flattened mappings
            row (int): display row index
        """
        self._recommend_float_type_for_values(flattened_mappings)
        display_name = flattened_mappings.display_names[row]
        if display_name.endswith("indexes") and flattened_mappings.is_time_series_value():
            self._recommend_date_time_type(flattened_mappings.component_at(row))
        elif not display_name.endswith("values"):
            self._recommend_string_type(flattened_mappings.component_at(row))

    def _recommend_float_type_for_values(self, flattened_mappings):
        """

        Args:
            flattened_mappings (FlattenedMappings): flattened mappings
        """
        if not flattened_mappings.has_value_component():
            return
        visual_row = next(
            (k for k, name in enumerate(flattened_mappings.display_names) if name.endswith("values")), None
        )
        if visual_row is None:
            return
        component = flattened_mappings.component_at(visual_row)
        if not flattened_mappings.root_mapping.is_pivoted():
            self._recommend_float_type(component)
            return
        not_pivoted_columns = set(flattened_mappings.root_mapping.non_pivoted_columns())
        ignored_columns = set(flattened_mappings.skip_columns())
        excluded_columns = sorted(list(not_pivoted_columns | ignored_columns))
        self.multi_column_type_recommended.emit(excluded_columns, FloatConvertSpec())

    def _recommend_string_type(self, component):
        """Signals a need to change source table conversion specification to StringConvertSpec.

        Args:
            component (ImportMapping): mapping component
        """
        self._recommend_type(component, StringConvertSpec())

    def _recommend_float_type(self, component):
        """Signals a need to change source table conversion specification to FloatConvertSpec.

        Args:
            component (ImportMapping): mapping component
        """
        self._recommend_type(component, FloatConvertSpec())

    def _recommend_date_time_type(self, component):
        """Signals a need to change source table conversion specification to DateTimeConvertSpec.

        Args:
            component (ImportMapping): mapping component
        """
        self._recommend_type(component, DateTimeConvertSpec())

    def _recommend_type(self, component, convert_spec):
        """Signals a need to change source table conversion specifications.

        Args:
            component (ImportMapping): mapping component
            convert_spec (ConvertSpec): row/column conversion specification
        """
        if not isinstance(component.position, int):
            return
        if component.position >= 0:
            self.row_or_column_type_recommended.emit(component.position, convert_spec, Qt.Orientation.Horizontal)
        else:
            self.row_or_column_type_recommended.emit(-(component.position + 1), convert_spec, Qt.Orientation.Vertical)

    def set_tables_editable(self, editable):
        """Enables or disables table name editing.

        Args:
            editable (bool): True to enable table name editing, False to disable
        """
        for item in self._mappings[1:]:
            if item.empty:
                continue
            item.editable = editable

    def add_empty_row(self):
        """Adds the special 'unnamed table' row at the end of table list."""
        last_row = len(self._mappings) - 1
        empty_item = SourceTableItem(
            UNNAMED_TABLE_NAME,
            checked=False,
            checkable=False,
            editable=True,
            accepts_drags_and_drops=False,
            real=False,
            empty=True,
        )
        self.beginInsertRows(QModelIndex(), last_row, last_row)
        self._mappings.append(empty_item)
        self.endInsertRows()

    def insertRows(self, row, count, parent=QModelIndex()):
        parent_item = parent.internalPointer()
        if isinstance(parent_item, SourceTableItem) and parent_item.real:
            self.beginInsertRows(parent, row, row + count - 1)
            for _ in range(count):
                list_item = MappingListItem(self._unique_mapping_name(parent_item))
                list_item.set_flattened_mappings(FlattenedMappings(self.create_default_mapping()))
                parent_item.insert_to_mapping_list(row, list_item)
            self.endInsertRows()
            return True
        return False

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):

        source_parent_item = sourceParent.internalPointer()
        if source_parent_item is None:
            return self._move_source_table_list_rows(sourceRow, count, destinationChild)
        elif isinstance(source_parent_item, SourceTableItem):
            return self._move_mapping_list_rows(sourceParent, sourceRow, count, destinationParent, destinationChild)
        return False

    def _move_source_table_list_rows(self, source_row, count, destination_child):
        """Moves row in mapping list.

        Args:
            source_row (int): source row index
            count (int): mapping count
            destination_child (int): destination row index

        Returns:
            bool: True if operation was successful, False otherwise
        """
        items = self._mappings[source_row : source_row + count]
        is_legal_move = self.beginMoveRows(
            QModelIndex(), source_row, source_row + count - 1, QModelIndex(), destination_child
        )
        if not is_legal_move:
            return False
        self._mappings = self._mappings[:source_row] + self._mappings[source_row + count :]
        if source_row < destination_child:
            destination_child -= count
        for i, item in enumerate(items):
            self._mappings.insert(destination_child + i, item)
        self.endMoveRows()
        return True

    def _move_mapping_list_rows(self, source_parent, source_row, count, destination_parent, destination_child):
        """Moves row in mapping list.

        Args:
            source_parent (QModelIndex): source parent
            source_row (int): source row index
            count (int): mapping count
            destination_parent (QModelIndex): destination parent
            destination_child (int): destination row index

        Returns:
            bool: True if operation was successful, False otherwise
        """
        source_table_item = source_parent.internalPointer()
        destination_table_item = destination_parent.internalPointer()
        if not isinstance(destination_table_item, SourceTableItem):
            return False
        is_internal_move = source_table_item is destination_table_item
        source_list = source_table_item.mapping_list
        items = source_list[source_row : source_row + count]
        is_legal_move = self.beginMoveRows(
            source_parent, source_row, source_row + count - 1, destination_parent, destination_child
        )
        if not is_legal_move:
            return False
        source_table_item.mapping_list = source_list[:source_row] + source_list[source_row + count :]
        if is_internal_move and source_row < destination_child:
            destination_child -= count
        for i, item in enumerate(items):
            destination_table_item.insert_to_mapping_list(destination_child + i, item)
        self.endMoveRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        parent_item = parent.internalPointer()
        if parent_item is None:
            self.beginRemoveRows(parent, row, row + count - 1)
            self._mappings = self._mappings[:row] + self._mappings[row + count :]
            self.endRemoveRows()
            return True
        if isinstance(parent_item, SourceTableItem):
            self.beginRemoveRows(parent, row, row + count - 1)
            parent_item.mapping_list = parent_item.mapping_list[:row] + parent_item.mapping_list[row + count :]
            self.endRemoveRows()
            return True
        return False

    @staticmethod
    def create_default_mapping():
        """Creates a default object class mapping.

        Returns:
            ImportMapping: new mapping root
        """
        root_mapping = EntityClassMapping(0)
        object_mapping = root_mapping.child = EntityMapping(1)
        object_mapping.child = EntityMetadataMapping(Position.hidden)
        return root_mapping

    def has_mapping_name(self, table_row, name):
        """Checks if a name exists in mapping list.

        Args:
            table_row (int): source table row index
            name (str): name to check

        Returns:
            bool: True if name exists, False otherwise
        """
        return name in {i.name for i in self._mappings[table_row].mapping_list}

    def unique_mapping_name(self, table_row, prefix):
        """Generates a unique mapping name.

        Args:
            table_row (int): source table row index
            prefix (str): name prefix

        Returns:
            str: name
        """
        return self._unique_mapping_name(self._mappings[table_row], prefix)

    @staticmethod
    def _unique_mapping_name(table_item, prefix="Mapping"):
        """Generates a unique mapping name.

        Args:
            table_item (SourceTableItem): source table item
            prefix (str): name prefix

        Returns:
            str: name
        """
        return unique_name(prefix, [i.name for i in table_item.mapping_list])

    def set_source_table_items_into_specification(self):
        """Sets the in_specification flag for all appropriate source table items."""
        bottom = 0
        for mapping in self._mappings[1:]:
            mapping.in_specification = True
            bottom += 1
        if bottom > 0:
            top_left = self.index(1, 0)
            bottom_right = self.index(bottom, 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def remove_tables_not_in_source_and_specification(self):
        """Removes source table items that are not in source or saved in specification."""
        start = 1
        for row, table_item in reversed(list(enumerate(self._mappings[start:], start))):
            if not table_item.in_source and not table_item.in_specification:
                self.removeRow(row)

    def cross_check_source_table_names(self, table_names):
        """Sets the in_source flag for all appropriate source table items.

        Args:
            table_names (set of str): existing source table names
        """
        changed_rows = []
        start = 1
        for row, table_item in enumerate(self._mappings[start:], start):
            in_source = table_item.name in table_names
            changed = False
            if table_item.in_source != in_source:
                table_item.in_source = in_source
                changed = True
            if table_item.real != in_source:
                table_item.real = in_source
                changed = True
            if changed:
                changed_rows.append(row)
        if changed_rows:
            top_left = self.index(changed_rows[0], 0)
            bottom_right = self.index(changed_rows[-1], 0)
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.ForegroundRole])
