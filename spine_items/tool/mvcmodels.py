######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Models for the Tool item

:author: M. Marin (KTH)
:date:   9.11.2020
"""

import json
from PySide2.QtCore import Qt, QMimeData, Signal
from PySide2.QtGui import QStandardItemModel, QStandardItem, QPixmap, QPainter, QIcon
from ..models import FileListModel


def _make_icon(rank=None):
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.drawText(0, 0, 16, 16, Qt.AlignCenter, f"{rank}:")
    painter.end()
    return QIcon(pixmap)


class CommandLineArgItem(QStandardItem):
    def __init__(self, text, rank=None, selectable=False, editable=False, drag_enabled=False, drop_enabled=False):
        super().__init__(text)
        self.setEditable(editable)
        self.setDropEnabled(drop_enabled)
        self.setDragEnabled(drag_enabled)
        self.setSelectable(selectable)
        if rank is not None:
            icon = _make_icon(rank)
            self.setIcon(icon)


class NewCommandLineArgItem(CommandLineArgItem):
    def __init__(self):
        super().__init__("Type new arg here...", selectable=True, editable=True)
        gray_color = qApp.palette().text().color()
        gray_color.setAlpha(128)
        self.setForeground(gray_color)

    def setData(self, value, role=Qt.UserRole + 1):
        if role != Qt.EditRole:
            return super().setData(value, role=role)
        if value != self.data(role=role):
            self.model().append_tool_arg(value)
        return False


class CommandLineArgsModel(QStandardItemModel):
    args_updated = Signal(list)
    _tool_args = []

    def reset_model(self, spec_args, tool_args):
        self._tool_args = tool_args
        self.clear()
        self.setHorizontalHeaderItem(0, QStandardItem("Command line arguments"))
        spec_args_root = CommandLineArgItem("Specification arguments")
        tool_args_root = CommandLineArgItem("Tool arguments", drop_enabled=True)
        spec_args_root.setFlags(spec_args_root.flags() & ~Qt.ItemIsEditable)
        tool_args_root.setFlags(tool_args_root.flags() & ~Qt.ItemIsEditable)
        self.appendRow(spec_args_root)
        self.appendRow(tool_args_root)
        spec_args_children = [CommandLineArgItem(arg, rank=k + 1) for k, arg in enumerate(spec_args)]
        tool_args_children = [
            CommandLineArgItem(arg, rank=k + len(spec_args) + 1, editable=True, selectable=True, drag_enabled=True)
            for k, arg in enumerate(tool_args)
        ]
        tool_args_children.append(NewCommandLineArgItem())
        spec_args_root.appendRows(spec_args_children)
        tool_args_root.appendRows(tool_args_children)

    def append_tool_arg(self, arg):
        self.args_updated.emit(self._tool_args + [arg])

    def mimeData(self, indexes):
        data = QMimeData()
        text = json.dumps(("rows", ";;".join([str(index.row()) for index in indexes])))
        data.setText(text)
        return data

    def canDropMimeData(self, data, drop_action, row, column, parent):
        return parent.data() is not None and row >= 0

    def dropMimeData(self, data, drop_action, row, column, parent):
        head, contents = json.loads(data.text())
        if head == "rows":
            rows = [int(x) for x in contents.split(";;")]
            head = [arg for k, arg in enumerate(self._tool_args[:row]) if k not in rows]
            body = [self._tool_args[k] for k in rows]
            tail = [arg for k, arg in enumerate(self._tool_args[row:]) if k + row not in rows]
            new_args = head + body + tail
            self.args_updated.emit(new_args)
            return True
        if head == "paths":
            new_args = self._tool_args[:row] + contents.split(";;") + self._tool_args[row:]
            self.args_updated.emit(new_args)
            return True
        return False


class InputFileListModel(FileListModel):
    """A model for input files to be shown in a file list view."""

    _invalid_resource_types = ()
    _header_label = "Input files"

    def flags(self, index):
        return super().flags(index) & ~Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled

    def data(self, index, role=Qt.DisplayRole):
        """Returns data associated with given role at given index."""
        if role == Qt.CheckStateRole:
            return None
        return super().data(index, role=role)

    def mimeData(self, indexes):
        data = QMimeData()
        text = json.dumps(("paths", ";;".join([index.data() for index in indexes])))
        data.setText(text)
        return data
