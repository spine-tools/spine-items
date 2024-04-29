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

"""Contains common & shared (Q)widgets."""
import os
from PySide6.QtCore import Qt, Signal, QUrl, QMimeData, Property, Slot
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QStyle,
    QStyleOptionComboBox,
    QTreeView,
    QStyledItemDelegate,
    QWidget,
    QDialog,
    QStatusBar,
    QDialogButtonBox,
)
from PySide6.QtGui import QDrag, QIntValidator
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from spinetoolbox.config import APPLICATION_PATH, STATUSBAR_SS
from .utils import convert_to_sqlalchemy_url


class ArgsTreeView(QTreeView):
    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        event.accept()


class ReferencesTreeView(QTreeView):
    """Custom QTreeView class for Data Connection and View properties."""

    files_dropped = Signal(list)
    del_key_pressed = Signal()

    def __init__(self, parent):
        """Initializes the view.

        Args:
            parent (QWidget): The parent of this view
        """
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
    """Custom QTreeView class for the 'Data' files in DataConnection properties."""

    files_dropped = Signal(list)
    del_key_pressed = Signal()

    def __init__(self, parent):
        """Initializes the view.

        Args:
            parent (QWidget): The parent of this view
        """
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
            self.drag_start_pos = event.position().toPoint()
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
        if (event.position().toPoint() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimeData = QMimeData()
        urls = list()
        for index in self.drag_indexes:
            file_path = index.data(Qt.ItemDataRole.UserRole)
            if not file_path:
                return
            urls.append(QUrl.fromLocalFile(file_path))
        mimeData.setUrls(urls)
        drag.setMimeData(mimeData)
        icon = self.drag_indexes[0].data(Qt.ItemDataRole.DecorationRole)
        if icon:
            pixmap = icon.pixmap(32, 32)
            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())
        drag.exec()

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
        self.setWindowFlags(Qt.WindowType.Popup)
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


class FileDropTargetLineEdit(QLineEdit):
    """A line edit that accepts file drops and displays the path."""

    def dragEnterEvent(self, event):
        """Accept a single file drop from the filesystem."""
        urls = event.mimeData().urls()
        if len(urls) > 1:
            event.ignore()
            return
        url = urls[0]
        if not url.isLocalFile():
            event.ignore()
            return
        if not os.path.isfile(url.toLocalFile()):
            event.ignore()
            return
        event.accept()
        event.setDropAction(Qt.LinkAction)

    def dragMoveEvent(self, event):
        """Accept event."""
        event.accept()

    def dropEvent(self, event):
        """Sets the text to the file path."""
        url = event.mimeData().urls()[0]
        self.setText(url.toLocalFile())


KNOWN_SQL_DIALECTS = ("mysql", "sqlite", "mssql", "postgresql")


class UrlSelectorMixin:
    def _setup(self, dialects):
        self.ui.comboBox_dialect.addItems(dialects)
        self.ui.comboBox_dialect.setCurrentIndex(-1)
        self.ui.lineEdit_port.setValidator(QIntValidator())

    def enable_dialect(self, dialect):
        """Enables the given dialect in the item controls."""
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
                msg = "Please create an SQL Server ODBC Data Source first."
                self._toolbox.msg_warning.emit(msg)
        else:
            self.enable_common()

    def enable_no_dialect(self):
        """Adjusts widget enabled status to default when no dialect is selected."""
        self.ui.comboBox_dialect.setEnabled(True)
        self.ui.comboBox_dsn.setEnabled(False)
        self.ui.toolButton_select_sqlite_file.setEnabled(False)
        self.ui.lineEdit_host.setEnabled(False)
        self.ui.lineEdit_port.setEnabled(False)
        self.ui.lineEdit_database.setEnabled(False)
        self.ui.lineEdit_username.setEnabled(False)
        self.ui.lineEdit_password.setEnabled(False)

    def enable_mssql(self):
        """Adjusts controls to mssql connection specification."""
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
        """Adjusts controls to sqlite connection specification."""
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
        """Adjusts controls to 'common' connection specification."""
        self.ui.comboBox_dsn.setEnabled(False)
        self.ui.comboBox_dsn.setCurrentIndex(-1)
        self.ui.toolButton_select_sqlite_file.setEnabled(False)
        self.ui.lineEdit_host.setEnabled(True)
        self.ui.lineEdit_port.setEnabled(True)
        self.ui.lineEdit_database.setEnabled(True)
        self.ui.lineEdit_username.setEnabled(True)
        self.ui.lineEdit_password.setEnabled(True)


def _set_line_edit_text(edit, text):
    """Sets QLineEdit's text only if it is changing.

    Avoids sudden jumps in cursors when e.g. the latest change goes through the
    undo stack

    Args:
        edit (QLineEdit): line edit
        text (str): new text to set for the edit
    """
    if text != edit.text():
        edit.setText(text)


class UrlSelectorWidget(QWidget):
    """Widget for setting up database URLs."""

    url_changed = Signal()
    """Emitted whenever the URL changes."""

    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): parent widget
        """
        from .ui.url_selector_widget import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._url = None
        self._get_sqlite_file_path = None
        self._logger = None
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._ui.comboBox_dialect.setCurrentIndex(-1)
        self._ui.lineEdit_port.setValidator(QIntValidator())
        self._ui.comboBox_dialect.currentTextChanged.connect(self._enable_dialect)
        self._ui.toolButton_select_sqlite_file.clicked.connect(self._select_sqlite_file)
        self._ui.comboBox_dialect.currentTextChanged.connect(lambda: self.url_changed.emit())
        self._ui.lineEdit_host.textChanged.connect(lambda: self.url_changed.emit())
        self._ui.lineEdit_port.textChanged.connect(lambda: self.url_changed.emit())
        self._ui.lineEdit_database.textChanged.connect(lambda: self.url_changed.emit())
        self._ui.lineEdit_username.textChanged.connect(lambda: self.url_changed.emit())
        self._ui.lineEdit_password.textChanged.connect(lambda: self.url_changed.emit())

    def setup(self, dialects, select_sqlite_file_callback, hide_schema, logger):
        """Sets the widget up for usage.

        Args:
            dialects (Sequence of str): available SQL dialects
            select_sqlite_file_callback (Callable): function that returns a path to SQLite file or None
            hide_schema (bool): True to hide the Schema field
            logger (LoggerInterface): logger
        """
        self._get_sqlite_file_path = select_sqlite_file_callback
        self._logger = logger
        self._ui.comboBox_dialect.addItems(dialects)
        if hide_schema:
            self._ui.schema_line_edit.setVisible(False)
            self._ui.schema_label.setVisible(False)

    def set_url(self, url):
        """Sets the URL for the widget.

        Args:
            url (dict): URL as dict
        """
        dialect = url.get("dialect", "")
        host = url.get("host", "")
        port = url.get("port", "")
        database = url.get("database", "")
        schema = url.get("schema", "")
        username = url.get("username", "")
        password = url.get("password", "")
        self.blockSignals(True)
        if dialect == "":
            self._ui.comboBox_dialect.setCurrentIndex(-1)
        elif dialect != self._ui.comboBox_dialect.currentText():
            self._ui.comboBox_dialect.setCurrentText(dialect)
        _set_line_edit_text(self._ui.lineEdit_host, host)
        _set_line_edit_text(self._ui.lineEdit_port, port)
        _set_line_edit_text(self._ui.lineEdit_database, database)
        _set_line_edit_text(self._ui.schema_line_edit, schema)
        _set_line_edit_text(self._ui.lineEdit_username, username)
        _set_line_edit_text(self._ui.lineEdit_password, password)
        self.blockSignals(False)

    def url_dict(self):
        """Returns the URL as dictionary.

        Returns:
            dict: URL as dict
        """
        return {
            "dialect": self._ui.comboBox_dialect.currentText(),
            "host": self._ui.lineEdit_host.text(),
            "port": self._ui.lineEdit_port.text(),
            "database": self._ui.lineEdit_database.text(),
            "schema": self._ui.schema_line_edit.text(),
            "username": self._ui.lineEdit_username.text(),
            "password": self._ui.lineEdit_password.text(),
        }

    @Slot(bool)
    def _select_sqlite_file(self, _=False):
        """Select SQLite file."""
        file_path = self._get_sqlite_file_path()
        if file_path is not None:
            self._ui.lineEdit_database.setText(file_path)

    @Slot(str)
    def _enable_dialect(self, dialect):
        """Enables the given dialect in the item controls.

        Args:
            dialect (str): SQL dialect
        """
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
                self._ui.comboBox_dsn.clear()
                self._ui.comboBox_dsn.addItems(mssql_dsns)
                self._ui.comboBox_dsn.setCurrentIndex(-1)
                self.enable_mssql()
            else:
                msg = "Please create an SQL Server ODBC Data Source first."
                self._logger.msg_warning.emit(msg)
        else:
            self.enable_common()

    def enable_no_dialect(self):
        """Adjusts widget enabled status to default when no dialect is selected."""
        self._ui.comboBox_dialect.setEnabled(True)
        self._ui.comboBox_dsn.setEnabled(False)
        self._ui.toolButton_select_sqlite_file.setEnabled(False)
        self._ui.lineEdit_host.setEnabled(False)
        self._ui.lineEdit_port.setEnabled(False)
        self._ui.lineEdit_database.setEnabled(False)
        self._ui.lineEdit_username.setEnabled(False)
        self._ui.lineEdit_password.setEnabled(False)
        self._ui.schema_line_edit.setEnabled(False)

    def enable_mssql(self):
        """Adjusts controls to mssql connection specification."""
        self._ui.comboBox_dsn.setEnabled(True)
        self._ui.toolButton_select_sqlite_file.setEnabled(False)
        self._ui.lineEdit_host.setEnabled(False)
        self._ui.lineEdit_port.setEnabled(False)
        self._ui.lineEdit_database.setEnabled(False)
        self._ui.lineEdit_username.setEnabled(True)
        self._ui.lineEdit_password.setEnabled(True)
        self._ui.schema_line_edit.setEnabled(True)
        self._ui.lineEdit_host.clear()
        self._ui.lineEdit_port.clear()
        self._ui.lineEdit_database.clear()

    def enable_sqlite(self):
        """Adjusts controls to sqlite connection specification."""
        self._ui.comboBox_dsn.setEnabled(False)
        self._ui.comboBox_dsn.setCurrentIndex(-1)
        self._ui.toolButton_select_sqlite_file.setEnabled(True)
        self._ui.lineEdit_host.setEnabled(False)
        self._ui.lineEdit_port.setEnabled(False)
        self._ui.lineEdit_database.setEnabled(True)
        self._ui.lineEdit_username.setEnabled(False)
        self._ui.lineEdit_password.setEnabled(False)
        self._ui.schema_line_edit.setEnabled(False)
        self._ui.lineEdit_host.clear()
        self._ui.lineEdit_port.clear()
        self._ui.lineEdit_username.clear()
        self._ui.lineEdit_password.clear()

    def enable_common(self):
        """Adjusts controls to 'common' connection specification."""
        self._ui.comboBox_dsn.setEnabled(False)
        self._ui.comboBox_dsn.setCurrentIndex(-1)
        self._ui.toolButton_select_sqlite_file.setEnabled(False)
        self._ui.lineEdit_host.setEnabled(True)
        self._ui.lineEdit_port.setEnabled(True)
        self._ui.lineEdit_database.setEnabled(True)
        self._ui.lineEdit_username.setEnabled(True)
        self._ui.lineEdit_password.setEnabled(True)
        self._ui.schema_line_edit.setEnabled(True)


class UrlSelectorDialog(QDialog):
    msg_error = Signal(str)

    def __init__(self, app_settings, hide_schema, logger, parent=None):
        """
        Args:
            app_settings (QSettings): Toolbox settings
            hide_schema (bool): if True, hide the Schema field
            logger (LoggerInterface): logger
            parent (QWidget, optional): parent widget
        """
        from .ui.url_selector_dialog import Ui_Dialog  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._sa_url = None
        self._app_settings = app_settings
        self._logger = logger
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.url_selector_widget.setup(KNOWN_SQL_DIALECTS, self._browse_sqlite_file, hide_schema, self._logger)
        self.ui.url_selector_widget.url_changed.connect(self._refresh_url)
        # Add status bar to form
        self.statusbar = QStatusBar(self)
        self.statusbar.setFixedHeight(20)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setStyleSheet(STATUSBAR_SS)
        self.ui.horizontalLayout_statusbar_ph.addWidget(self.statusbar)
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.msg_error.connect(self.statusbar.showMessage)

    @property
    def url(self):
        if self._sa_url is None:
            return ""
        return str(self._sa_url)

    def url_dict(self):
        return self.ui.url_selector_widget.url_dict()

    def set_url_dict(self, url):
        """Sets the URL.

        Args:
            url (dict): URL as dict
        """
        self.ui.url_selector_widget.set_url(url)

    @property
    def dialect(self):
        return self.ui.url_selector_widget.url_dict().get("dialect")

    @Slot()
    def _refresh_url(self):
        """Updates the URL widget and status bar."""
        url = self.ui.url_selector_widget.url_dict()
        self._sa_url = convert_to_sqlalchemy_url(url, logger=self)
        if self._sa_url is not None:
            self.statusbar.clearMessage()
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self._sa_url is not None)

    def _browse_sqlite_file(self):
        """Opens a browser to select a SQLite file.

        Returns:
            str: path to the file or None if operation was cancelled
        """
        filter_ = "*.sqlite;;*.*"
        key = "selectImportSourceSQLiteFile"
        filepath, _ = get_open_file_name_in_last_dir(
            self._app_settings, key, self, "Select an SQLite file", APPLICATION_PATH, filter_=filter_
        )
        return filepath if filepath else None


def combo_box_width(font_metric_widget, items):
    """Returns section width.

    Args:
        font_metric_widget (QWidget): Widget whose font metrics are used
        items (Iterable of str): combo box items

    Returns:
        int: width of a combo box containing the given items
    """
    fm = font_metric_widget.fontMetrics()
    style = QApplication.instance().style()
    option = QStyleOptionComboBox()
    rect = style.subControlRect(QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxArrow)
    return max(fm.horizontalAdvance(item) for item in items) + rect.width()
