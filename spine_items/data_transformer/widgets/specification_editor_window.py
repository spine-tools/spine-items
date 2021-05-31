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
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFileDialog, QVBoxLayout
from spinetoolbox.project_item.specification_editor_window import (
    SpecificationEditorWindowBase,
    ChangeSpecPropertyCommand,
)
from .entity_class_renaming_widget import EntityClassRenamingWidget
from .parameter_renaming_widget import ParameterRenamingWidget
from .value_transforming_widget import ValueTransformingWidget
from ..data_transformer_specification import DataTransformerSpecification
from ..settings import EntityClassRenamingSettings, ParameterRenamingSettings, ValueTransformSettings

_FILTER_NAMES = ("Rename entity classes", "Rename parameters", "Transform values")

_SETTINGS_CLASSES = dict(
    zip(_FILTER_NAMES, (EntityClassRenamingSettings, ParameterRenamingSettings, ValueTransformSettings))
)

_CLASSES_TO_DISPLAY_NAMES = {class_: name for name, class_ in _SETTINGS_CLASSES.items()}


class SpecificationEditorWindow(SpecificationEditorWindowBase):
    """Data transformer's specification editor."""

    def __init__(self, toolbox, specification=None, item=None, urls=None):
        """
        Args:
            toolbox (ToolboxUI): Toolbox main window
            specification (ProjectItemSpecification, optional): transformer specification
            item (ProjectItem, optional): invoking project item, if window was opened from its properties tab
            urls (dict, optional): a mapping from provider name to database URL
        """

        super().__init__(toolbox, specification, item)
        self._settings = {name: None for name in _FILTER_NAMES}
        self._urls = dict()
        self._filter_widgets = dict()
        self._current_filter_name = None
        self._ui.filter_combo_box.addItems(_FILTER_NAMES)
        if specification is not None and specification.settings is not None:
            settings = specification.settings
            filter_name = _CLASSES_TO_DISPLAY_NAMES[type(settings)]
            self._settings[filter_name] = settings
        else:
            filter_name = ""
        self._set_current_filter_name(filter_name)
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.load_data_button.clicked.connect(self._load_data)
        self._ui.database_url_combo_box.model().rowsInserted.connect(
            lambda *args: self._ui.load_data_button.setEnabled(True)
        )
        self._ui.database_url_combo_box.addItems(urls if urls is not None else [])
        self._ui.filter_combo_box.currentTextChanged.connect(self._change_filter_widget)

    @property
    def settings_group(self):
        return "dataTransformerSpecificationWindow"

    def _make_ui(self):
        from ..ui.specification_editor_widget import Ui_MainWindow  # pylint: disable=import-outside-toplevel

        return Ui_MainWindow()

    def _make_new_specification(self, spec_name):
        """See base class."""
        description = self._spec_toolbar.description()
        filter_name = self._ui.filter_combo_box.currentText()
        if not filter_name:
            filter_settings = None
        else:
            filter_widget = self._filter_widgets[filter_name]
            filter_settings = filter_widget.settings()
        return DataTransformerSpecification(spec_name, filter_settings, description)

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
            widget = dict(
                zip(_FILTER_NAMES, (EntityClassRenamingWidget, ParameterRenamingWidget, ValueTransformingWidget))
            )[filter_name](self._undo_stack, self._settings[filter_name])
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

    def tear_down(self):
        if not super().tear_down():
            return False
        for widget in self._filter_widgets.values():
            widget.deleteLater()
        return True
