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
from PySide2.QtCore import Qt, Signal, QUrl, QMimeData, Property
from PySide2.QtWidgets import QApplication, QTreeView, QStyledItemDelegate, QWidget
from PySide2.QtGui import QDrag


class ArgsTreeView(QTreeView):
    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        event.accept()


class ReferencesTreeView(QTreeView):
    """Custom QTreeView class for Data Connection and View properties.

    Attributes:
        parent (QWidget): The parent of this view
    """

    files_dropped = Signal(list)
    del_key_pressed = Signal()

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

    files_dropped = Signal(list)
    del_key_pressed = Signal()

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


class FilterEditDelegateBase(QStyledItemDelegate):
    """Base class for regexp filter edit delegates.

    Derived classes should reimplement at least ``createEditor()``.
    """

    def updateEditorGeometry(self, editor, option, index):
        top_left = option.rect.topLeft()
        popup_position = editor.parent().mapToGlobal(top_left)
        size_hint = editor.sizeHint()
        editor.setGeometry(
            popup_position.x(), popup_position.y(), max(option.rect.width(), size_hint.width()), size_hint.height()
        )


class FilterEdit(QWidget):
    """Filter regular expression editor."""

    def __init__(self, ui_form, parent):
        """
        Args:
            ui_form (Any): an interface from created from a .ui file
            parent (QWidget):
        """
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self._ui = ui_form
        self._ui.setupUi(self)
        self._focused = False

    def focusInEvent(self, e):
        self._ui.regexp_line_edit.setFocus()
        self._ui.regexp_line_edit.selectAll()
        super().focusInEvent(e)

    def keyPressEvent(self, event):
        # Relay key press events to the regexp line edit. Otherwise we may lose the first letter.
        return self._ui.regexp_line_edit.keyPressEvent(event)

    def regexp(self):
        """Returns the current regular expression.

        Returns:
            str: regular expression
        """
        return self._ui.regexp_line_edit.text()

    def set_regexp(self, regexp):
        """Sets a regular expression for editing.

        Args:
            regexp (str): new regular expression
        """
        self._ui.regexp_line_edit.setText(regexp)

    regexp = Property(str, regexp, set_regexp, user=True)
    """Property used to communicate with the editor delegate."""
