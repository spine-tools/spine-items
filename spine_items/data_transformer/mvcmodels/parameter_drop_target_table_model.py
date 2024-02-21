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

"""Contains a table model that can be used as drop target."""
import pickle
from PySide6.QtCore import QAbstractTableModel
from ..commands import InsertRow
from ..widgets.drop_target_table import DROP_MIME_TYPE


class ParameterDropTargetTableModel(QAbstractTableModel):
    def dropMimeData(self, data, action, row, column, parent):
        if row < 0:
            row = self.rowCount()
        rows = list()
        parameters = pickle.loads(data.data(DROP_MIME_TYPE))
        for entity_class, parameter_list in parameters.items():
            for parameter in parameter_list:
                rows.append(self._make_drop_row(entity_class, parameter))
        if len(rows) == 1:
            self._undo_stack.push(InsertRow("add parameter", self, row, rows[0]))
        else:
            self._undo_stack.beginMacro("add parameters")
            for i, row_data in enumerate(rows):
                self._undo_stack.push(InsertRow("", self, row + i, row_data))
            self._undo_stack.endMacro()
        return True

    def mimeTypes(self):
        return [DROP_MIME_TYPE]

    @staticmethod
    def _make_drop_row(entity_class, parameter):
        raise NotImplementedError()
