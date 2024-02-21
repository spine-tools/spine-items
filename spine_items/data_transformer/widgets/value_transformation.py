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

"""Contains classes to manage parameter value transformation."""
from PySide6.QtCore import QObject, QSortFilterProxyModel, Qt, Slot
from ..commands import InsertRow, RemoveRow
from ..mvcmodels.value_transformations_table_model import (
    ValueTransformationsTableModel,
    TransformationsTableColumn,
    TransformationsTableRole,
)
from .copy_paste import copy_table_data, paste_table_data
from .instructions_editor import InstructionsEditor
from ..settings import ValueTransformSettings


class ValueTransformation(QObject):
    _MIME_TYPE = "application/spine-dtparameterrename"

    def __init__(self, ui, undo_stack, settings, parent):
        """
        Args:
            ui (Ui_Form): specification editor's UI
            undo_stack (QUndoStack): undo stack
            settings (ValueTransformSettings, optional): initial settings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._undo_stack = undo_stack
        self._ui = ui
        self._transformation_table_model = ValueTransformationsTableModel(settings, self._undo_stack, self)
        self._sorted_transformation_table_model = QSortFilterProxyModel(self)
        self._sorted_transformation_table_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._sorted_transformation_table_model.setSourceModel(self._transformation_table_model)
        self._ui.transformations_table_view.setModel(self._sorted_transformation_table_model)
        self._instructions_editor = InstructionsEditor(
            self._ui, self._transformation_table_model, self._undo_stack, self
        )
        self._ui.add_transformation_button.clicked.connect(self._add_parameter)
        self._ui.remove_transformation_button.clicked.connect(self._ui.remove_value_transformation_action.trigger)
        self._ui.remove_value_transformation_action.triggered.connect(self._remove_parameters)
        self._ui.transformations_table_view.addAction(self._ui.remove_value_transformation_action)
        self._ui.transformations_table_view.addAction(self._ui.copy_value_transformation_data_action)
        self._ui.copy_value_transformation_data_action.triggered.connect(self._copy_table_data)
        self._ui.transformations_table_view.addAction(self._ui.paste_value_transformation_data_action)
        self._ui.paste_value_transformation_data_action.triggered.connect(self._paste_table_data)

    @Slot(bool)
    def _add_parameter(self, checked):
        """Adds a new parameter row.

        Args:
            checked (bool): unused
        """
        row = self._transformation_table_model.rowCount()
        self._undo_stack.push(
            InsertRow("add parameter", self._transformation_table_model, row, ["class", "parameter", []])
        )

    @Slot(bool)
    def _remove_parameters(self, checked):
        """Removes selected parameter row.

        Args:
            checked (bool): unused
        """
        indexes = self._ui.transformations_table_view.selectionModel().selectedRows()
        if not indexes:
            return
        rows = tuple(self._sorted_transformation_table_model.mapToSource(i).row() for i in indexes)
        if len(rows) == 1:
            self._undo_stack.push(RemoveRow("remove parameter", self._transformation_table_model, rows[0]))
        else:
            self._undo_stack.beginMacro("remove parameters")
            for row in reversed(sorted(rows)):
                self._undo_stack.push(RemoveRow("", self._transformation_table_model, row))
            self._undo_stack.endMacro()

    def load_data(self, url):
        """
        Loads parameter data from given URL.

        Args:
            url (str): database URL
        """
        self._ui.available_parameters_tree_view.load_data(url)

    @Slot(bool)
    def _copy_table_data(self, checked):
        """Copies data to clipboard.

        Args:
            checked (bool): unused
        """
        copy_table_data(self._ui.transformations_table_view, self._MIME_TYPE)

    @Slot(bool)
    def _paste_table_data(self, checked):
        """Pastes data from clipboard.

        Args:
            checked (bool): unused
        """
        paste_table_data(self._ui.transformations_table_view, self._MIME_TYPE, self._undo_stack)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        settings = dict()
        for row in range(self._transformation_table_model.rowCount()):
            entity_class = self._transformation_table_model.index(row, TransformationsTableColumn.CLASS).data()
            parameter = self._transformation_table_model.index(row, TransformationsTableColumn.PARAMETER).data()
            instructions = self._transformation_table_model.index(row, TransformationsTableColumn.INSTRUCTIONS).data(
                TransformationsTableRole.INSTRUCTIONS
            )
            settings.setdefault(entity_class, {})[parameter] = instructions
        return ValueTransformSettings(settings)

    def show(self):
        """Shows docks."""
        self._ui.load_database_dock.show()
        self._ui.possible_parameters_dock.show()
        self._ui.value_transformation_dock.show()
        self._ui.value_instructions_dock.show()

    def tear_down(self):
        """Hides docks and releases resources."""
        self._ui.load_database_dock.hide()
        self._ui.possible_parameters_dock.hide()
        self._ui.value_transformation_dock.hide()
        self._ui.value_instructions_dock.hide()
