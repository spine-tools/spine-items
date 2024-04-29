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

"""Contains shared functions that provide copy-paste functionality."""
import pickle
from PySide6.QtCore import QMimeData
from PySide6.QtWidgets import QApplication
from ..commands import InsertRow, SetData


def copy_table_data(table_view, mime_type):
    """Copies data to system clipboard.

    Args:
        table_view (QTableView): target table view
        mime_type (str): mime type for table's native data
    """
    indexes = table_view.selectionModel().selectedIndexes()
    if not indexes:
        return
    rows = [i.row() for i in indexes]
    min_row = min(rows)
    max_row = max(rows)
    columns = [i.column() for i in indexes]
    min_column = min(columns)
    max_column = max(columns)
    index_lookup = {(i.row(), i.column()): i for i in indexes}
    model = table_view.model().sourceModel()
    data = list()
    for row in range(min_row, max_row + 1):
        row_data = list()
        for column in range(min_column, max_column + 1):
            index = index_lookup.get((row, column))
            if index is None:
                row_data.append(None)
            else:
                row_data.append(index.data(model.GET_DATA_ROLES[column]))
        data.append(row_data)
    mime_data = QMimeData()
    mime_data.setData(mime_type, pickle.dumps(data))
    clipboard = QApplication.clipboard()
    clipboard.setMimeData(mime_data)


def paste_table_data(table_view, mime_type, undo_stack):
    """Pushes commands that Paste data from system clipboard to undo stack.

    Args:
        table_view (QTableView): target table view
        mime_type (str): mime type for table's native data
        undo_stack (QUndoStack): undo stack
    """
    if not table_view.selectionModel().hasSelection():
        return
    clipboard = QApplication.clipboard()
    mime_data = clipboard.mimeData()
    if mime_data is None:
        return
    if not mime_data.hasFormat(mime_type):
        return
    data = pickle.loads(mime_data.data(mime_type))
    indexes = table_view.selectionModel().selectedIndexes()
    model = table_view.model()
    source_model = model.sourceModel()
    model.setDynamicSortFilter(False)
    undo_stack.beginMacro("paste data")
    if len(indexes) == 1:
        _paste_all(indexes[0], data, model, source_model, undo_stack)
    else:
        _paste_fit_to_selection(indexes, data, model, source_model, undo_stack)
    model.setDynamicSortFilter(True)
    undo_stack.endMacro()


def _paste_all(top_left, data, model, source_model, undo_stack):
    """Pushes commands that paste all data on clipboard extending target model if needed to undo stack.

    Args:
        top_left (QModelIndex): top left corner of target area
        data (list of list): rows to paste
        model (QSortFilterModel): sorted model
        source_model (QAbstractTableModel): actual model
        undo_stack (QUndoStack): undo stack
    """
    for row, row_data in enumerate(data):
        table_row = row + top_left.row()
        if table_row >= model.rowCount():
            undo_stack.push(InsertRow("", source_model, table_row, None))
        for column, item in enumerate(row_data):
            table_column = column + top_left.column()
            if item is None or table_column >= model.columnCount():
                continue
            index = model.index(table_row, table_column)
            undo_stack.push(
                SetData(
                    "",
                    index,
                    item,
                    index.data(source_model.GET_DATA_ROLES[table_column]),
                    source_model.SET_DATA_ROLES[table_column],
                )
            )


def _paste_fit_to_selection(indexes, data, model, source_model, undo_stack):
    """Pushes commands that paste data on clipboard to undo stack.

    Args:
        indexes (QModelIndex): selected indexes
        data (list of list): rows to paste
        model (QSortFilterModel): sorted model
        source_model (QAbstractTableModel): actual model
        undo_stack (QUndoStack): undo stack
    """
    rows = [i.row() for i in indexes]
    min_row = min(rows)
    max_row = min(max(rows), min_row + len(data) - 1)
    columns = [i.column() for i in indexes]
    min_column = min(columns)
    max_column = min(max(columns), min_column + len(data[0]) - 1)
    for row in range(min_row, max_row + 1):
        row_data = data[row - min_row]
        for column in range(min_column, max_column + 1):
            if column >= model.columnCount():
                continue
            item = row_data[column - min_column]
            if item is None:
                continue
            index = model.index(row, column)
            undo_stack.push(
                SetData(
                    "",
                    index,
                    item,
                    index.data(source_model.GET_DATA_ROLES[column]),
                    source_model.SET_DATA_ROLES[column],
                )
            )
