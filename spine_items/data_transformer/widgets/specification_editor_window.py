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
Contains :class:`SpecificationEditorWindow`.

:author: A. Soininen (VTT)
:date:   2.10.2020
"""
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QMainWindow, QDialogButtonBox, QUndoStack
from spinetoolbox.config import STATUSBAR_SS
from .entity_class_renaming_widget import EntityClassRenamingWidget
from .parameter_renaming_widget import ParameterRenamingWidget
from ..data_transformer_specification import DataTransformerSpecification
from ..settings import EntityClassRenamingSettings, ParameterRenamingSettings
from ...widgets import SpecNameDescriptionToolbar, prompt_to_save_changes, save_ui, restore_ui
from ...commands import ChangeSpecPropertyCommand


_FILTER_NAMES = ("Rename entity classes", "Rename parameters")

_SETTINGS_CLASSES = dict(zip(_FILTER_NAMES, (EntityClassRenamingSettings, ParameterRenamingSettings)))

_CLASSES_TO_DISPLAY_NAMES = {class_: name for name, class_ in _SETTINGS_CLASSES.items()}


class SpecificationEditorWindow(QMainWindow):
    """Data transformer's specification editor."""

    def __init__(self, toolbox, specification=None, urls=None, item=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (ProjectItemSpecification, optional): transformer specification
            urls (dict, optional): a mapping from provider name to database URL
            item_name (str, optional): invoking project item's name, if window was opened from its properties tab
        """
        from ..ui.specification_editor_widget import Ui_MainWindow  # pylint: disable=import-outside-toplevel

        super().__init__(parent=toolbox)
        self._item = item
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._toolbox = toolbox
        self._original_spec_name = None if specification is None else specification.name
        if specification is None:
            specification = DataTransformerSpecification(name="")
        self._specification = specification
        self._app_settings = self._toolbox.qsettings()
        self.settings_group = "dataTransformerSpecificationWindow"
        self._urls = dict()
        self._filter_widgets = dict()
        self._current_filter_name = None
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._undo_stack = QUndoStack(self)
        self._spec_toolbar = SpecNameDescriptionToolbar(self, self._specification, self._undo_stack)
        self.addToolBar(Qt.TopToolBarArea, self._spec_toolbar)
        self._populate_main_menu()
        self._button_box = QDialogButtonBox(self)
        self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._ui.statusbar.addPermanentWidget(self._button_box)
        self._ui.statusbar.layout().setContentsMargins(6, 6, 6, 6)
        self._ui.statusbar.setStyleSheet(STATUSBAR_SS)
        title = "Data transformer specification editor[*]"
        if item is not None:
            title = title + f"    -- {item.name} --"
        self.setWindowTitle(title)
        self._ui.filter_combo_box.addItems(_FILTER_NAMES)
        if self._specification.settings is not None:
            filter_name = _CLASSES_TO_DISPLAY_NAMES[type(self._specification.settings)]
        else:
            filter_name = ""
        self._set_current_filter_name(filter_name)
        restore_ui(self, self._app_settings, self.settings_group)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.load_data_button.clicked.connect(self._load_data)
        self._ui.database_url_combo_box.model().rowsInserted.connect(
            lambda *args: self._ui.load_data_button.setEnabled(True)
        )
        self._ui.database_url_combo_box.addItems(urls if urls is not None else [])
        self._ui.filter_combo_box.currentTextChanged.connect(self._change_filter_widget)
        self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.save_and_close)
        self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.discard_and_close)
        self._undo_stack.cleanChanged.connect(self._update_window_modified)
        self._ui.actionSaveAndClose.triggered.connect(self.save_and_close)

    def _populate_main_menu(self):
        menu = self._spec_toolbar.menu
        undo_action = self._undo_stack.createUndoAction(self)
        redo_action = self._undo_stack.createRedoAction(self)
        undo_action.setShortcuts(QKeySequence.Undo)
        redo_action.setShortcuts(QKeySequence.Redo)
        menu.addActions([redo_action, undo_action])
        menu.addSeparator()
        menu.addAction(self._ui.actionSaveAndClose)
        self._ui.menubar.hide()
        self.addAction(self._spec_toolbar.menu_action)

    @Slot(bool)
    def _update_window_modified(self, clean):
        self.setWindowModified(not clean)

    @Slot(str)
    def _change_filter_widget(self, filter_name):
        """
        Changes the filter widget in ``filter_stack``.

        Args:
            filter_name (str): widget's filter name
        """
        if self._current_filter_name == filter_name:
            return
        self._undo_stack.push(
            ChangeSpecPropertyCommand(
                self._set_current_filter_name, filter_name, self._current_filter_name, "change filter"
            )
        )

    def _set_current_filter_name(self, filter_name):
        self._current_filter_name = filter_name
        if not self._current_filter_name:
            self._ui.filter_combo_box.setCurrentIndex(-1)
            self._ui.filter_stack.setCurrentIndex(0)
            return
        self._ui.filter_combo_box.setCurrentText(self._current_filter_name)
        widget = self._filter_widgets.get(filter_name)
        if widget is None:
            widget = dict(zip(_FILTER_NAMES, (EntityClassRenamingWidget, ParameterRenamingWidget)))[filter_name](
                self._undo_stack, self._specification.settings
            )
            self._filter_widgets[filter_name] = widget
        layout = self._ui.filter_widget.layout()
        if layout is None:
            layout = QVBoxLayout()
            self._ui.filter_widget.setLayout(layout)
        for _ in range(layout.count()):
            removed = layout.takeAt(0)
            removed.widget().hide()
        layout.addWidget(widget)
        widget.show()
        self._ui.filter_stack.setCurrentIndex(1)

    @Slot(bool)
    def discard_and_close(self, _=False):
        self._undo_stack.setClean()
        self.close()

    @Slot(bool)
    def save_and_close(self, _=False):
        """Stores the specification to Toolbox' specification list, sets the spec for the item, and closes the window."""
        if not self._save():
            return
        if self._item:
            self._item.set_specification(self._specification)
        self.close()

    def _save(self):
        specification_name = self._spec_toolbar.name()
        if not specification_name:
            QMessageBox.information(self, "Specification name missing", "Please enter a name for the specification.")
            return False
        description = self._spec_toolbar.description()
        filter_name = self._ui.filter_combo_box.currentText()
        if not filter_name:
            filter_settings = None
        else:
            filter_widget = self._filter_widgets[filter_name]
            filter_settings = filter_widget.settings()
        self._specification = DataTransformerSpecification(specification_name, filter_settings, description)
        if not self._call_add_specification():
            return False
        self._undo_stack.setClean()
        return True

    def _call_add_specification(self):
        """Adds the specification to the project.

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        update_existing = self._specification.name == self._original_spec_name
        return self._toolbox.add_specification(self._specification, update_existing, self)

    def closeEvent(self, event=None):
        """Handles close window.

        Args:
            event (QEvent): Closing event if 'X' is clicked.
        """
        if not self._undo_stack.isClean() and not prompt_to_save_changes(self, self._save):
            event.ignore()
            return
        for widget in self._filter_widgets.values():
            widget.deleteLater()
        self._undo_stack.cleanChanged.disconnect(self._update_window_modified)
        save_ui(self, self._app_settings, self.settings_group)
        if event:
            event.accept()

    @Slot(bool)
    def _load_url_from_filesystem(self, _):
        path = self._browse_database()
        if not path:
            return
        url = "sqlite:///" + path
        self._ui.database_url_combo_box.addItem(url)
        self._urls[url] = url

    def _browse_database(self):
        """
        Queries a database file from the user.

        Returns:
            str: path to database file
        """
        initial_path = self._toolbox.project().project_dir
        return QFileDialog.getOpenFileName(self, "Select database", initial_path, "sqlite (*.sqlite)")[0]

    @Slot(bool)
    def _load_data(self, _):
        """Sends selected database URL to current filter widget so it can load relevant data."""
        filter_name = self._ui.filter_combo_box.currentText()
        widget = self._filter_widgets[filter_name]
        widget.load_data(self._ui.database_url_combo_box.currentText())
