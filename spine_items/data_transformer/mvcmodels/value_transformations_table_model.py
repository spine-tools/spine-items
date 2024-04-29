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

"""Contains :class:`ValueTransformTableModel`."""
from enum import IntEnum, unique
from PySide6.QtCore import QModelIndex, Qt
from .parameter_drop_target_table_model import ParameterDropTargetTableModel
from ..commands import SetData


@unique
class TransformationsTableColumn(IntEnum):
    CLASS = 0
    PARAMETER = 1
    INSTRUCTIONS = 2


@unique
class TransformationsTableRole(IntEnum):
    INSTRUCTIONS = Qt.ItemDataRole.UserRole + 1
    SILENT_EDIT = Qt.ItemDataRole.UserRole + 2


class ValueTransformationsTableModel(ParameterDropTargetTableModel):
    """A table model that contains parameter value transformations."""

    GET_DATA_ROLES = (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DisplayRole, TransformationsTableRole.INSTRUCTIONS)
    SET_DATA_ROLES = (
        TransformationsTableRole.SILENT_EDIT,
        TransformationsTableRole.SILENT_EDIT,
        TransformationsTableRole.INSTRUCTIONS,
    )

    def __init__(self, settings, undo_stack, parent):
        """
        Args:
            settings (ValueTransformSettings, optional): initial settings
            undo_stack (QUndoStack): undo stack
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._undo_stack = undo_stack
        if settings is not None:
            self._instructions = [
                [klass, param, instr]
                for klass, param_instr in settings.instructions.items()
                for param, instr in param_instr.items()
            ]
        else:
            self._instructions = []

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            column = index.column()
            if column != TransformationsTableColumn.INSTRUCTIONS:
                return self._instructions[index.row()][column]
            instructions = self._instructions[index.row()][column]
            return ", ".join(t["operation"] for t in instructions)
        if role == TransformationsTableRole.INSTRUCTIONS:
            return self._instructions[index.row()][TransformationsTableColumn.INSTRUCTIONS]
        return None

    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        if index.column() != TransformationsTableColumn.INSTRUCTIONS:
            flags |= Qt.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ("Class", "Parameter", "Instructions")[section]
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        rows = count * [["", "", []]]
        self.beginInsertRows(parent, row, row + count - 1)
        self._instructions = self._instructions[:row] + rows + self._instructions[row:]
        self.endInsertRows()
        return True

    @staticmethod
    def _make_drop_row(entity_class, parameter):
        return [entity_class, parameter, []]

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._instructions = self._instructions[:row] + self._instructions[row + count :]
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._instructions)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            if not value or not isinstance(value, str):
                return False
            column = index.column()
            message = "change class name" if column == TransformationsTableColumn.CLASS else "change parameter name"
            previous = self._instructions[index.row()][column]
            self._undo_stack.push(SetData(message, index, value, previous, TransformationsTableRole.SILENT_EDIT))
            return True
        if role == TransformationsTableRole.SILENT_EDIT:
            if not isinstance(value, str):
                return False
            self._instructions[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        if role == TransformationsTableRole.INSTRUCTIONS and index.column() == TransformationsTableColumn.INSTRUCTIONS:
            if not isinstance(value, list):
                return False
            row = index.row()
            self._instructions[row][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, TransformationsTableRole.INSTRUCTIONS])
            return True
        return False
