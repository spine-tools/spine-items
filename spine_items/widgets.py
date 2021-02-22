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
Contains common & shared (Q)widgets.

:authors: M. Marin (KTH), P. Savolainen (VTT)
:date:   10.11.2020
"""

import os
from PySide2.QtCore import Qt, Signal, Slot, QUrl, QMimeData, QTimer
from PySide2.QtWidgets import QApplication, QWidget, QTreeView, QToolBar, QLabel, QHBoxLayout
from PySide2.QtGui import QDrag
from spinetoolbox.widgets.custom_qlineedits import PropertyQLineEdit
from .commands import SetSpecName, SetSpecDescription


class ArgsTreeView(QTreeView):
    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        event.accept()


class ReferencesTreeView(QTreeView):
    """Custom QTreeView class for Data Connection and View properties.

    Attributes:
        parent (QWidget): The parent of this view
    """

    files_dropped = Signal("QVariant", name="files_dropped")
    del_key_pressed = Signal(name="del_key_pressed")

    def __init__(self, parent):
        """Initializes the view."""
        super().__init__(parent=parent)

    def dragEnterEvent(self, event):
        """Accepts file drops from the filesystem."""
        urls = event.mimeData().urls()
        for url in urls:
            if not url.isLocalFile():
                event.ignore()
                return
            if not os.path.isfile(url.toLocalFile()):
                event.ignore()
                return
        event.accept()
        event.setDropAction(Qt.LinkAction)

    def dragMoveEvent(self, event):
        """Accepts event."""
        event.accept()

    def dropEvent(self, event):
        """Emits files_dropped signal with a list of files for each dropped url."""
        self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])

    def keyPressEvent(self, event):
        """Overridden method to make the view support deleting items with a delete key."""
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete:
            self.del_key_pressed.emit()


class DataTreeView(QTreeView):
    """Custom QTreeView class for the 'Data' files in DataConnection properties.

    Attributes:
        parent (QWidget): The parent of this view
    """

    files_dropped = Signal("QVariant", name="files_dropped")
    del_key_pressed = Signal(name="del_key_pressed")

    def __init__(self, parent):
        """Initializes the view."""
        super().__init__(parent=parent)
        self.drag_start_pos = None
        self.drag_indexes = list()

    def dragEnterEvent(self, event):
        """Accepts file drops from the filesystem."""
        urls = event.mimeData().urls()
        for url in urls:
            if not url.isLocalFile():
                event.ignore()
                return
            if not os.path.isfile(url.toLocalFile()):
                event.ignore()
                return
        event.accept()
        event.setDropAction(Qt.CopyAction)

    def dragMoveEvent(self, event):
        """Accepts event."""
        event.accept()

    def dropEvent(self, event):
        """Emits files_dropped signal with a list of files for each dropped url."""
        self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])

    def mousePressEvent(self, event):
        """Registers drag start position."""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.drag_indexes = self.selectedIndexes()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Starts dragging action if needed."""
        if not event.buttons() & Qt.LeftButton:
            return
        if not self.drag_start_pos:
            return
        if not self.drag_indexes:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimeData = QMimeData()
        urls = list()
        for index in self.drag_indexes:
            file_path = index.data(Qt.UserRole)
            urls.append(QUrl.fromLocalFile(file_path))
        mimeData.setUrls(urls)
        drag.setMimeData(mimeData)
        icon = self.drag_indexes[0].data(Qt.DecorationRole)
        if icon:
            pixmap = icon.pixmap(32, 32)
            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())
        drag.exec_()

    def mouseReleaseEvent(self, event):
        """Forgets drag start position"""
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)  # Fixes bug in extended selection

    def keyPressEvent(self, event):
        """Overridden method to make the view support deleting items with a delete key."""
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Delete:
            self.del_key_pressed.emit()


class SpecNameDescriptionToolbar(QToolBar):
    """A QToolBar to let users set name and description for an Spec."""

    def __init__(self, parent, spec, undo_stack):
        """

        Args:
            parent (QMainWindow): QMainWindow instance
        """
        super().__init__(parent=parent)
        self._undo_stack = undo_stack
        self._current_name = ""
        self._current_description = ""
        self._line_edit_name = PropertyQLineEdit()
        self._line_edit_description = PropertyQLineEdit()
        self._line_edit_name.setPlaceholderText("Enter specification name here...")
        self._line_edit_description.setPlaceholderText("Enter specification description here...")
        self._timer_set_name = QTimer(self)
        self._timer_set_description = QTimer(self)
        self._timer_set_name.setInterval(200)
        self._timer_set_description.setInterval(200)
        self.setAllowedAreas(Qt.TopToolBarArea)
        self.setFloatable(False)
        self.setMovable(False)
        self.addWidget(QLabel("Specification"))
        self.addSeparator()
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self._line_edit_name)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self._line_edit_description)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setStretchFactor(self._line_edit_name, 1)
        layout.setStretchFactor(self._line_edit_description, 3)
        self.addWidget(widget)
        self.setObjectName("SpecNameDescriptionToolbar")
        if spec:
            self.do_set_name(spec.name)
            self.do_set_description(spec.description)
        self._line_edit_name.textEdited.connect(self._timer_set_name.start)
        self._line_edit_description.textEdited.connect(self._timer_set_description.start)
        self._timer_set_name.timeout.connect(self._set_name)
        self._timer_set_description.timeout.connect(self._set_description)

    @Slot()
    def _set_name(self):
        self._timer_set_name.stop()
        self._undo_stack.push(SetSpecName(self, self.name(), self._current_name))

    @Slot()
    def _set_description(self):
        self._timer_set_description.stop()
        self._undo_stack.push(SetSpecDescription(self, self.description(), self._current_description))

    def do_set_name(self, name):
        self._current_name = name
        self._line_edit_name.setText(name)

    def do_set_description(self, description):
        self._current_description = description
        self._line_edit_description.setText(description)

    def name(self):
        return self._line_edit_name.text()

    def description(self):
        return self._line_edit_description.text()
