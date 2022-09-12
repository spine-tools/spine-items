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
from PySide2.QtWidgets import QApplication, QTreeView, QStyledItemDelegate, QWidget, QDialog, QStatusBar
from PySide2.QtGui import QDrag, QIntValidator
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from spinetoolbox.config import APPLICATION_PATH, STATUSBAR_SS
from spinetoolbox.widgets.select_database_items import SelectDatabaseItems
from .utils import convert_to_sqlalchemy_url


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


class UrlSelectorMixin:
    def _setup(self, dialects):
        self.ui.comboBox_dialect.addItems(dialects)
        self.ui.comboBox_dialect.setCurrentIndex(-1)
        self.ui.lineEdit_port.setValidator(QIntValidator())

    def enable_dialect(self, dialect):
        """Enable the given dialect in the item controls."""
        if dialect == "":
            self.enable_no_dialect()
        elif dialect == "sqlite":
            self.enable_sqlite()
        elif dialect == "mssql":
            import pyodbc  # pylint: disable=import-outside-toplevel

            dsns = pyodbc.dataSources()
            # Collect dsns which use the msodbcsql driver
            mssql_dsns = list()
            for key, value in dsns.items():
                if "msodbcsql" in value.lower():
                    mssql_dsns.append(key)
            if mssql_dsns:
                self.ui.comboBox_dsn.clear()
                self.ui.comboBox_dsn.addItems(mssql_dsns)
                self.ui.comboBox_dsn.setCurrentIndex(-1)
                self.enable_mssql()
            else:
                msg = "Please create a SQL Server ODBC Data Source first."
                self._logger.msg_warning.emit(msg)
        else:
            self.enable_common()

    def enable_no_dialect(self):
        """Adjust widget enabled status to default when no dialect is selected."""
        self.ui.comboBox_dialect.setEnabled(True)
        self.ui.comboBox_dsn.setEnabled(False)
        self.ui.toolButton_select_sqlite_file.setEnabled(False)
        self.ui.lineEdit_host.setEnabled(False)
        self.ui.lineEdit_port.setEnabled(False)
        self.ui.lineEdit_database.setEnabled(False)
        self.ui.lineEdit_username.setEnabled(False)
        self.ui.lineEdit_password.setEnabled(False)

    def enable_mssql(self):
        """Adjust controls to mssql connection specification."""
        self.ui.comboBox_dsn.setEnabled(True)
        self.ui.toolButton_select_sqlite_file.setEnabled(False)
        self.ui.lineEdit_host.setEnabled(False)
        self.ui.lineEdit_port.setEnabled(False)
        self.ui.lineEdit_database.setEnabled(False)
        self.ui.lineEdit_username.setEnabled(True)
        self.ui.lineEdit_password.setEnabled(True)
        self.ui.lineEdit_host.clear()
        self.ui.lineEdit_port.clear()
        self.ui.lineEdit_database.clear()

    def enable_sqlite(self):
        """Adjust controls to sqlite connection specification."""
        self.ui.comboBox_dsn.setEnabled(False)
        self.ui.comboBox_dsn.setCurrentIndex(-1)
        self.ui.toolButton_select_sqlite_file.setEnabled(True)
        self.ui.lineEdit_host.setEnabled(False)
        self.ui.lineEdit_port.setEnabled(False)
        self.ui.lineEdit_database.setEnabled(True)
        self.ui.lineEdit_username.setEnabled(False)
        self.ui.lineEdit_password.setEnabled(False)
        self.ui.lineEdit_host.clear()
        self.ui.lineEdit_port.clear()
        self.ui.lineEdit_username.clear()
        self.ui.lineEdit_password.clear()

    def enable_common(self):
        """Adjust controls to 'common' connection specification."""
        self.ui.comboBox_dsn.setEnabled(False)
        self.ui.comboBox_dsn.setCurrentIndex(-1)
        self.ui.toolButton_select_sqlite_file.setEnabled(False)
        self.ui.lineEdit_host.setEnabled(True)
        self.ui.lineEdit_port.setEnabled(True)
        self.ui.lineEdit_database.setEnabled(True)
        self.ui.lineEdit_username.setEnabled(True)
        self.ui.lineEdit_password.setEnabled(True)


class UrlSelector(UrlSelectorMixin, QDialog):
    msg_error = Signal(str)

    def __init__(self, toolbox, parent=None):
        from .ui.url_selector_widget import Ui_Dialog  # pylint: disable=import-outside-toplevel

        super().__init__(parent if parent is not None else toolbox)
        self._toolbox = toolbox
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_ph.addWidget(self.statusbar)
        self._sa_url = None
        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setEnabled(False)
        self._setup(("mysql", "sqlite", "mssql", "postgresql", "oracle"))  # Others?
        self.ui.comboBox_dialect.activated[str].connect(self.enable_dialect)
        self.ui.comboBox_dialect.activated.connect(self._refresh_url)
        self.ui.toolButton_select_sqlite_file.clicked.connect(self._browse_sqlite_file)
        self.ui.lineEdit_username.editingFinished.connect(self._refresh_url)
        self.ui.lineEdit_password.editingFinished.connect(self._refresh_url)
        self.ui.lineEdit_host.editingFinished.connect(self._refresh_url)
        self.ui.lineEdit_port.editingFinished.connect(self._refresh_url)
        self.ui.lineEdit_database.editingFinished.connect(self._refresh_url)
        self.msg_error.connect(self.statusbar.showMessage)

    @property
    def url(self):
        if self._sa_url is None:
            return ""
        return str(self._sa_url)

    def _refresh_url(self):
        url = {
            "dialect": self.ui.comboBox_dialect.currentText(),
            "host": self.ui.lineEdit_host.text(),
            "port": self.ui.lineEdit_port.text(),
            "database": self.ui.lineEdit_database.text(),
            "username": self.ui.lineEdit_username.text(),
            "password": self.ui.lineEdit_password.text(),
        }
        self._sa_url = convert_to_sqlalchemy_url(url, logger=self)
        self.ui.buttonBox.button(self.ui.buttonBox.Ok).setEnabled(self._sa_url is not None)

    def _browse_sqlite_file(self):
        filter_ = "*.sqlite;;*.*"
        key = "selectImportSourceSQLiteFile"
        filepath, _ = get_open_file_name_in_last_dir(
            self._toolbox.qsettings(), key, self, "Select a SQLite file", APPLICATION_PATH, filter_=filter_
        )
        if not filepath:
            return
        self.ui.lineEdit_database.setText(filepath)
        self._refresh_url()


class PurgeSettingsDialog(QDialog):
    """Importer's purge settings dialog."""

    def __init__(self, purge_settings, parent=None):
        """
        Args:
            purge_settings (dict): purge settings
            parent (QWidget, optional): parent widget
        """
        from .ui.purge_settings_dialog import Ui_Dialog  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)
        self._item_check_boxes_widget = SelectDatabaseItems(purge_settings, self)
        self._ui.root_layout.insertWidget(0, self._item_check_boxes_widget)

    def get_purge_settings(self):
        """Returns current purge settings.

        Returns:
            dict: mapping from purgeable database item name to purge flag
        """
        return self._item_check_boxes_widget.checked_states()
