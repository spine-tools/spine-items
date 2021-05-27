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
Contains :class:`ValueTransformTableModel`.

:author: A. Soininen (VTT)
:date:   25.5.2021
"""
from enum import IntEnum, unique
import pickle
from PySide2.QtCore import QAbstractTableModel, QModelIndex, Qt
from ..widgets.parameter_tree_widget import ParameterTreeWidget
from ..commands import InsertRow


@unique
class TransformationsTableColumn(IntEnum):
    CLASS = 0
    PARAMETER = 1
    INSTRUCTIONS = 2


@unique
class TransformationsTableRole(IntEnum):
    INSTRUCTIONS = Qt.UserRole + 1


class ValueTransformationsTableModel(QAbstractTableModel):
    """A table model that contains parameter value transformations."""

    GET_DATA_ROLES = (Qt.DisplayRole, Qt.DisplayRole, TransformationsTableRole.INSTRUCTIONS)
    SET_DATA_ROLES = (Qt.EditRole, Qt.EditRole, TransformationsTableRole.INSTRUCTIONS)

    def __init__(self, settings, undo_stack, parent):
        """
        Args:
            settings (ValueTransformSettings): initial settings
            undo_stack (QUndoStack): undo stack
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._undo_stack = undo_stack
        self._instructions = [
            (klass, param, instr)
            for klass, param_instr in settings.instructions.items()
            for param, instr in param_instr.items()
        ]

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            column = index.column()
            if column != TransformationsTableColumn.INSTRUCTIONS:
                return self._instructions[index.row()][column]
            instructions = self._instructions[index.row()][column]
            return ", ".join(t["operation"] for t in instructions)
        if role == TransformationsTableRole.INSTRUCTIONS:
            return self._instructions[index.row()][TransformationsTableColumn.INSTRUCTIONS]
        return None

    def dropMimeData(self, data, action, row, column, parent):
        if row < 0:
            row = len(self._instructions)
        rows = list()
        parameters = pickle.loads(data.data("application/spine-parameters"))
        for entity_class, parameter_list in parameters.items():
            for parameter in parameter_list:
                rows.append((entity_class, parameter, []))
        if len(rows) == 1:
            self._undo_stack.push(InsertRow("add parameter", self, row, rows[0]))
        else:
            self._undo_stack.beginMacro("add parameters")
            for i, row_data in enumerate(rows):
                self._undo_stack.push(InsertRow("", self, row + i, row_data))
            self._undo_stack.endMacro()
        return True

    def flags(self, index):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
        if index.row() != TransformationsTableColumn.INSTRUCTIONS:
            flags |= Qt.ItemIsEditable
        return flags

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ("Class", "Parameter", "Instructions")[section]
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        rows = count * [("", "", [])]
        self.beginInsertRows(parent, row, row + count - 1)
        self._instructions = self._instructions[:row] + rows + self._instructions[row:]
        self.endInsertRows()
        return True

    def mimeTypes(self):
        return [ParameterTreeWidget.MIME_TYPE]

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._instructions = self._instructions[:row] + self._instructions[row + count :]
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._instructions)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            column = index.column()
            if column == TransformationsTableColumn.INSTRUCTIONS:
                return False
            row = index.row()
            data = self._instructions[row]
            self._instructions[row] = data[:column] + (value,) + data[column + 1 :]
            self.dataChanged.emit(index, index, [Qt.DisplayRole])
            return True
        if role == TransformationsTableRole.INSTRUCTIONS and index.column() == TransformationsTableColumn.INSTRUCTIONS:
            row = index.row()
            data = self._instructions[row]
            self._instructions[row] = data[: TransformationsTableColumn.INSTRUCTIONS] + (value,)
            self.dataChanged.emit(index, index, [Qt.DisplayRole, TransformationsTableRole.INSTRUCTIONS])
        return False
