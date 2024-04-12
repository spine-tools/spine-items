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

"""Contains :class:`ParameterRenamesTableModel`."""
from enum import IntEnum, unique
from PySide6.QtCore import QModelIndex, Qt
from .parameter_drop_target_table_model import ParameterDropTargetTableModel
from ..commands import SetData


@unique
class RenamesTableColumn(IntEnum):
    CLASS = 0
    PARAMETER = 1
    NEW_NAME = 2


@unique
class RenamesRoles(IntEnum):
    SILENT_EDIT = Qt.ItemDataRole.UserRole + 1


class ParameterRenamesTableModel(ParameterDropTargetTableModel):
    GET_DATA_ROLES = (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.DisplayRole)
    SET_DATA_ROLES = (RenamesRoles.SILENT_EDIT, RenamesRoles.SILENT_EDIT, RenamesRoles.SILENT_EDIT)

    def __init__(self, settings, undo_stack, parent):
        """
        Args:
            settings (ParameterRenamingSettings, optional): initial settings
            undo_stack (QUndoStack): undo stack
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._undo_stack = undo_stack
        if settings is not None:
            self._renames = [
                [klass, param, new_name]
                for klass, param_renames in settings.name_map.items()
                for param, new_name in param_renames.items()
            ]
        else:
            self._renames = []

    def columnCount(self, parent=QModelIndex()):
        return 3

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return self._renames[index.row()][index.column()]

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ("Class", "Parameter", "New name")[section]
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        rows = count * [["", "", ""]]
        self.beginInsertRows(parent, row, row + count - 1)
        self._renames = self._renames[:row] + rows + self._renames[row:]
        self.endInsertRows()
        return True

    @staticmethod
    def _make_drop_row(entity_class, parameter):
        return [entity_class, parameter, ""]

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        self._renames = self._renames[:row] + self._renames[row + count :]
        self.endRemoveRows()
        return True

    def rowCount(self, parent=QModelIndex()):
        return len(self._renames)

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if role == Qt.ItemDataRole.EditRole:
            column = index.column()
            if column == RenamesTableColumn.CLASS:
                message = "change class name"
            elif column == RenamesTableColumn.PARAMETER:
                message = "change parameter name"
            else:
                message = "change parameter's new name"
            previous = self._renames[index.row()][column]
            if value == previous:
                return False
            self._undo_stack.push(SetData(message, index, value, previous, RenamesRoles.SILENT_EDIT))
            return True
        if role == RenamesRoles.SILENT_EDIT:
            row = index.row()
            column = index.column()
            self._renames[row][column] = value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
            return True
        return False
