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

"""Contains :class:`SpecificationEditorWindow`."""
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QFileDialog, QHeaderView

from spinetoolbox.helpers import disconnect
from spinetoolbox.project_item.specification_editor_window import (
    SpecificationEditorWindowBase,
    ChangeSpecPropertyCommand,
)
from .class_rename import ClassRename
from .parameter_rename import ParameterRename
from .value_transformation import ValueTransformation
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
        self._changing_docks = [
            self._ui.load_database_dock,
            self._ui.possible_parameters_dock,
            self._ui.parameter_rename_dock,
            self._ui.value_transformation_dock,
            self._ui.value_instructions_dock,
            self._ui.possible_classes_dock,
            self._ui.class_rename_dock,
        ]
        for dock in self._changing_docks:
            dock.hide()
        self._urls = dict()
        self._filter_sub_interfaces = dict()
        self._current_filter_name = None
        self.takeCentralWidget().deleteLater()
        self._ui.filter_combo_box.addItems(_FILTER_NAMES)
        if specification is not None and specification.settings is not None:
            settings = specification.settings
            filter_name = _CLASSES_TO_DISPLAY_NAMES[type(settings)]
            self._settings[filter_name] = settings
        else:
            filter_name = _FILTER_NAMES[0]
        self._ui.load_url_from_fs_button.clicked.connect(self._load_url_from_filesystem)
        self._ui.load_data_button.clicked.connect(self._load_data)
        self._ui.database_url_combo_box.model().rowsInserted.connect(
            lambda *args: self._ui.load_data_button.setEnabled(True)
        )
        self._ui.database_url_combo_box.addItems(urls if urls is not None else [])
        self._ui.filter_combo_box.currentTextChanged.connect(self._change_filter_widget)
        self._set_current_filter_name(filter_name)
        for view in (
            self._ui.available_parameters_tree_view,
            self._ui.available_classes_tree_widget,
        ):
            view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        for view in (
            self._ui.parameter_rename_table_view,
            self._ui.transformations_table_view,
            self._ui.class_rename_table_view,
        ):
            view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

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
            interface = self._filter_sub_interfaces[filter_name]
            filter_settings = interface.settings()
        return DataTransformerSpecification(spec_name, filter_settings, description)

    @Slot(str)
    def _change_filter_widget(self, filter_name):
        """
        Pushes a command to change the current interface to undo stack.

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
        """Shows/hides current dock widgets depending on selected filter.

        Args:
            filter_name (str): filter's name
        """
        previous_interface = self._filter_sub_interfaces.get(self._current_filter_name)
        if previous_interface is not None:
            previous_interface.tear_down()
        self._current_filter_name = filter_name
        with disconnect(self._ui.filter_combo_box.currentTextChanged, self._change_filter_widget):
            self._ui.filter_combo_box.setCurrentText(filter_name)
        interface = self._filter_sub_interfaces.get(filter_name)
        if interface is None:
            interface = dict(zip(_FILTER_NAMES, (ClassRename, ParameterRename, ValueTransformation)))[filter_name](
                self._ui, self._undo_stack, self._settings[filter_name], self
            )
            self._filter_sub_interfaces[filter_name] = interface
        interface.show()

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
        interface = self._filter_sub_interfaces[filter_name]
        interface.load_data(self._ui.database_url_combo_box.currentText())

    def _restore_dock_widgets(self):
        docks = {
            Qt.LeftDockWidgetArea: (
                self._ui.type_dock,
                self._ui.possible_classes_dock,
                self._ui.possible_parameters_dock,
                self._ui.load_database_dock,
            ),
            Qt.RightDockWidgetArea: (
                self._ui.parameter_rename_dock,
                self._ui.class_rename_dock,
                self._ui.value_transformation_dock,
                self._ui.value_instructions_dock,
            ),
        }
        for area, area_docks in docks.items():
            for dock in area_docks:
                self.addDockWidget(area, dock)
