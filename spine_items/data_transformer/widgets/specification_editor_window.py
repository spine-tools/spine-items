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
from PySide2.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QWidget
from .entity_class_renaming_widget import EntityClassRenamingWidget
from .parameter_renaming_widget import ParameterRenamingWidget
from ..data_transformer_specification import DataTransformerSpecification
from ..settings import EntityClassRenamingSettings, ParameterRenamingSettings


_DISPLAY_NAMES = ("No filter", "Rename entity classes", "Rename parameters")

_SETTINGS_CLASSES = {_DISPLAY_NAMES[1]: EntityClassRenamingSettings, _DISPLAY_NAMES[2]: ParameterRenamingSettings}

_CLASSES_TO_DISPLAY_NAMES = {class_: name for name, class_ in _SETTINGS_CLASSES.items()}


class SpecificationEditorWindow(QWidget):
    """Data transformer's specification editor."""

    accepted = Signal(str)
    """Emitted when the specification has be accepted by the user."""

    def __init__(self, toolbox, specification=None, urls=None, item_name=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (ProjectItemSpecification, optional): transformer specification
            urls (dict, optional): a mapping from provider name to database URL
            item_name (str, optional): invoking project item's name, if window was opened from its properties tab
        """
        from ..ui.specification_editor_widget import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent=toolbox, f=Qt.Window)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._toolbox = toolbox
        self._original_spec_name = None if specification is None else specification.name
        if specification is None:
            specification = DataTransformerSpecification(name="")
        self._specification = specification
        self._urls = dict()
        self._filter_widgets = dict()
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        title = "Edit Data transformer specification"
        if item_name is not None:
            title = title + f"    -- {item_name} --"
        self.setWindowTitle(title)
        if self._specification.name:
            self._ui.specification_name_edit.setText(self._specification.name)
        if self._specification.description:
            self._ui.specification_description_edit.setText(self._specification.description)
        self._ui.filter_combo_box.addItem(_DISPLAY_NAMES[0])
        self._ui.filter_combo_box.addItems(list(_SETTINGS_CLASSES))
        self._ui.filter_combo_box.currentTextChanged.connect(self._change_filter_widget)
        if self._specification.settings is not None:
            widget_name = _CLASSES_TO_DISPLAY_NAMES[type(self._specification.settings)]
        else:
            widget_name = _DISPLAY_NAMES[0]
        self._ui.filter_combo_box.setCurrentText(widget_name)
        # For some reason, currentTextChanged doesn't seem to get emitted by the above.
        self._change_filter_widget(widget_name)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.load_data_button.clicked.connect(self._load_data)
        self._ui.database_url_combo_box.model().rowsInserted.connect(
            lambda *args: self._ui.load_data_button.setEnabled(True)
        )
        self._ui.database_url_combo_box.addItems(urls if urls is not None else [])
        self._ui.button_box.rejected.connect(self.close)
        self._ui.button_box.accepted.connect(self._accept_settings)

    @Slot()
    def _accept_settings(self):
        """Stores the specification to Toolbox' specification list, emits the accepted signal and closes the window."""
        specification_name = self._ui.specification_name_edit.text()
        if not specification_name:
            QMessageBox.information(self, "Specification name missing", "Please enter a name for the specification.")
            return
        existing = self._toolbox.specification_model.find_specification(specification_name)
        if existing is not None:
            # Specification names are case insensitive. Make sure we use the correct casing.
            specification_name = existing.name
            self._ui.specification_name_edit.setText(specification_name)
        description = self._ui.specification_description_edit.text()
        filter_name = self._ui.filter_combo_box.currentText()
        if filter_name == _DISPLAY_NAMES[0]:
            filter_settings = None
        else:
            filter_widget = self._filter_widgets[filter_name]
            filter_settings = filter_widget.settings()
        self._specification = DataTransformerSpecification(specification_name, filter_settings, description)
        if not self._store_specification():
            return
        self.accepted.emit(self._specification.name)
        self.close()

    def _store_specification(self):
        """
        Stores the specification.

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        update_existing = self._specification.name == self._original_spec_name
        return self._toolbox.add_specification(self._specification, update_existing, self)

    @Slot(str)
    def _change_filter_widget(self, display_name):
        """
        Changes the filter widget in ``filter_stack``.

        Args:
            display_name (str): widget's display name
        """
        if display_name == _DISPLAY_NAMES[0]:
            self._ui.filter_stack.setCurrentIndex(0)
            return
        widget = self._filter_widgets.get(display_name)
        if widget is None:
            widget = {_DISPLAY_NAMES[1]: EntityClassRenamingWidget, _DISPLAY_NAMES[2]: ParameterRenamingWidget}[
                display_name
            ](self._specification.settings)
            self._filter_widgets[display_name] = widget
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

    def close(self):
        """Cleans up before closing the window."""
        for widget in self._filter_widgets.values():
            widget.deleteLater()
        return super().close()

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
        selected = self._ui.filter_combo_box.currentText()
        widget = self._filter_widgets[selected]
        widget.load_data(self._ui.database_url_combo_box.currentText())
