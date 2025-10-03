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
from collections.abc import Callable, Iterable, Sequence
import os
from typing import Any, Final
from PySide6.QtCore import Property, QMimeData, QSettings, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QDrag, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QStatusBar,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionComboBox,
    QTreeView,
    QWidget,
)
from spine_engine.logger_interface import LoggerInterface, NonImplementedSignal
from spinetoolbox.config import APPLICATION_PATH, STATUSBAR_SS
from spinetoolbox.helpers import get_open_file_name_in_last_dir
from .utils import UrlDict, convert_to_sqlalchemy_url


class ArgsTreeView(QTreeView):
    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        event.accept()


class ReferencesTreeView(QTreeView):
    """Custom QTreeView class for Data Connection and View properties."""

    files_dropped = Signal(list)
    del_key_pressed = Signal()

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
        event.setDropAction(Qt.DropAction.LinkAction)

    def dragMoveEvent(self, event):
        """Accepts event."""
        event.accept()

    def dropEvent(self, event):
        """Emits files_dropped signal with a list of files for each dropped url."""
        self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])

    def keyPressEvent(self, event):
        """Overridden method to make the view support deleting items with a delete key."""
        super().keyPressEvent(event)
        if event.key() == Qt.Key.Key_Delete:
            self.del_key_pressed.emit()


class DataTreeView(QTreeView):
    """Custom QTreeView class for the 'Data' files in DataConnection properties."""

    files_dropped = Signal(list)
    del_key_pressed = Signal()

    def __init__(self, parent: QWidget | None):
        """
        Args:
            parent: The parent of this view
        """
        super().__init__(parent=parent)
        self.drag_start_pos = None
        self.drag_indexes = []

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
        event.setDropAction(Qt.DropAction.CopyAction)

    def dragMoveEvent(self, event):
        """Accepts event."""
        event.accept()

    def dropEvent(self, event):
        """Emits files_dropped signal with a list of files for each dropped url."""
        self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])

    def mousePressEvent(self, event):
        """Registers drag start position."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()
            self.drag_indexes = self.selectedIndexes()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Starts dragging action if needed."""
        if not event.buttons() & Qt.MouseButton.LeftButton:
            return
        if not self.drag_start_pos:
            return
        if not self.drag_indexes:
            return
        if (event.position().toPoint() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimeData = QMimeData()
        urls = []
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
        if event.key() == Qt.Key.Key_Delete:
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

    def __init__(self, ui_form: Any, parent: QWidget | None):
        """
        Args:
            ui_form: an interface form created from a .ui file
            parent: parent widget
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
        # Relay key press events to the regexp line edit. Otherwise, we may lose the first letter.
        return self._ui.regexp_line_edit.keyPressEvent(event)

    def regexp(self) -> str:
        """Returns the current regular expression.

        Returns:
            regular expression
        """
        return self._ui.regexp_line_edit.text()

    def set_regexp(self, regexp: str) -> None:
        """Sets a regular expression for editing.

        Args:
            regexp: new regular expression
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
        event.setDropAction(Qt.DropAction.LinkAction)

    def dragMoveEvent(self, event):
        """Accept event."""
        event.accept()

    def dropEvent(self, event):
        """Sets the text to the file path."""
        url = event.mimeData().urls()[0]
        self.setText(url.toLocalFile())


def _set_line_edit_text(edit: QLineEdit, text: str) -> None:
    """Sets QLineEdit's text only if it is changing.

    Avoids sudden jumps in cursors when e.g. the latest change goes through the
    undo stack

    Args:
        edit: line edit
        text: new text to set for the edit
    """
    if text != edit.text():
        edit.setText(text)


KNOWN_SQL_DIALECTS: Final[tuple[str, ...]] = ("mysql", "sqlite", "postgresql")


class UrlSelectorWidget(QWidget):
    """Widget for setting up database URLs."""

    url_changed = Signal()
    """Emitted whenever the URL changes."""

    def __init__(self, parent: QWidget | None = None):
        """
        Args:
            parent: parent widget
        """
        from .ui.url_selector_widget import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._url: UrlDict | None = None
        self._get_sqlite_file_path: Callable[[], str | None] | None = None
        self._logger: LoggerInterface | None = None
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

    def setup(
        self,
        dialects: Sequence[str],
        select_sqlite_file_callback: Callable[[], str | None],
        hide_schema: bool,
        logger: LoggerInterface,
    ) -> None:
        """Sets the widget up for usage.

        Args:
            dialects: available SQL dialects
            select_sqlite_file_callback: function that returns a path to SQLite file or None
            hide_schema: True to hide the Schema field
            logger: logger
        """
        self._get_sqlite_file_path = select_sqlite_file_callback
        self._logger = logger
        self._ui.comboBox_dialect.addItems(dialects)
        if hide_schema:
            self._ui.schema_line_edit.setVisible(False)
            self._ui.schema_label.setVisible(False)

    def set_url(self, url: UrlDict) -> None:
        """Sets the URL for the widget.

        Args:
            url: URL as dict
        """
        dialect = url.get("dialect", "")
        host = url.get("host", "")
        port = url.get("port")
        database = url.get("database", "")
        schema = url.get("schema", "")
        username = url.get("username", "")
        password = url.get("password", "")
        self.blockSignals(True)
        if not dialect:
            self._ui.comboBox_dialect.setCurrentIndex(-1 if self._ui.comboBox_dialect.count() == 0 else 0)
        elif dialect != self._ui.comboBox_dialect.currentText():
            self._ui.comboBox_dialect.setCurrentText(dialect)
        _set_line_edit_text(self._ui.lineEdit_host, host)
        _set_line_edit_text(self._ui.lineEdit_port, str(port) if port is not None else "")
        _set_line_edit_text(self._ui.lineEdit_database, database)
        _set_line_edit_text(self._ui.schema_line_edit, schema)
        _set_line_edit_text(self._ui.lineEdit_username, username)
        _set_line_edit_text(self._ui.lineEdit_password, password)
        self.blockSignals(False)

    def url_dict(self) -> UrlDict:
        """Returns the URL as dictionary.

        Returns:
            URL as dict
        """
        try:
            port = int(self._ui.lineEdit_port.text())
        except ValueError:
            port = None
        return {
            "dialect": self._ui.comboBox_dialect.currentText(),
            "host": self._ui.lineEdit_host.text(),
            "port": port,
            "database": self._ui.lineEdit_database.text(),
            "schema": self._ui.schema_line_edit.text(),
            "username": self._ui.lineEdit_username.text(),
            "password": self._ui.lineEdit_password.text(),
        }

    @Slot(bool)
    def _select_sqlite_file(self, _=False) -> None:
        """Select SQLite file."""
        if self._get_sqlite_file_path is None:
            raise RuntimeError("logic error: setup() has not been called")
        file_path = self._get_sqlite_file_path()
        if file_path is not None:
            self._ui.lineEdit_database.setText(file_path)

    @Slot(str)
    def _enable_dialect(self, dialect: str) -> None:
        """Enables the given dialect in the item controls.

        Args:
            dialect: SQL dialect
        """
        if dialect == "":
            self.enable_no_dialect()
        elif dialect == "sqlite":
            self.enable_sqlite()
        else:
            self.enable_common()

    def enable_no_dialect(self) -> None:
        """Adjusts widget enabled status to default when no dialect is selected."""
        self._ui.comboBox_dialect.setEnabled(True)
        self._ui.toolButton_select_sqlite_file.setEnabled(False)
        self._ui.lineEdit_host.setEnabled(False)
        self._ui.lineEdit_port.setEnabled(False)
        self._ui.lineEdit_database.setEnabled(False)
        self._ui.lineEdit_username.setEnabled(False)
        self._ui.lineEdit_password.setEnabled(False)
        self._ui.schema_line_edit.setEnabled(False)

    def enable_sqlite(self) -> None:
        """Adjusts controls to sqlite connection specification."""
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

    def enable_common(self) -> None:
        """Adjusts controls to 'common' connection specification."""
        self._ui.toolButton_select_sqlite_file.setEnabled(False)
        self._ui.lineEdit_host.setEnabled(True)
        self._ui.lineEdit_port.setEnabled(True)
        self._ui.lineEdit_database.setEnabled(True)
        self._ui.lineEdit_username.setEnabled(True)
        self._ui.lineEdit_password.setEnabled(True)
        self._ui.schema_line_edit.setEnabled(True)


class UrlSelectorDialog(QDialog):
    msg = NonImplementedSignal()
    msg_success = NonImplementedSignal()
    msg_warning = NonImplementedSignal()
    msg_error = Signal(str)
    msg_proc = NonImplementedSignal()
    msg_proc_error = NonImplementedSignal()
    information_box = NonImplementedSignal()
    error_box = NonImplementedSignal()

    def __init__(
        self, app_settings: QSettings, hide_schema: bool, logger: LoggerInterface, parent: QWidget | None = None
    ):
        """
        Args:
            app_settings: Toolbox settings
            hide_schema: if True, hide the Schema field
            logger: logger
            parent: parent widget
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
    def url(self) -> str:
        if self._sa_url is None:
            return ""
        return str(self._sa_url)

    def url_dict(self) -> UrlDict:
        return self.ui.url_selector_widget.url_dict()

    def set_url_dict(self, url: UrlDict) -> None:
        """Sets the URL.

        Args:
            url: URL as dict
        """
        self.ui.url_selector_widget.set_url(url)

    @property
    def dialect(self) -> str | None:
        return self.ui.url_selector_widget.url_dict().get("dialect")

    @Slot()
    def _refresh_url(self) -> None:
        """Updates the URL widget and status bar."""
        url = self.ui.url_selector_widget.url_dict()
        self._sa_url = convert_to_sqlalchemy_url(url, logger=self)
        if self._sa_url is not None:
            self.statusbar.clearMessage()
        self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(self._sa_url is not None)

    def _browse_sqlite_file(self) -> str | None:
        """Opens a browser to select a SQLite file.

        Returns:
            path to the file or None if operation was cancelled
        """
        filter_ = "*.sqlite;;*.*"
        key = "selectImportSourceSQLiteFile"
        filepath, _ = get_open_file_name_in_last_dir(
            self._app_settings, key, self, "Select an SQLite file", APPLICATION_PATH, filter_=filter_
        )
        return filepath if filepath else None


def combo_box_width(font_metric_widget: QWidget, items: Iterable[str]) -> int:
    """Returns section width.

    Args:
        font_metric_widget: Widget whose font metrics are used
        items: combo box items

    Returns:
        width of a combo box containing the given items
    """
    fm = font_metric_widget.fontMetrics()
    style = QApplication.instance().style()
    option = QStyleOptionComboBox()
    rect = style.subControlRect(QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxArrow)
    return max(fm.horizontalAdvance(item) for item in items) + rect.width()
