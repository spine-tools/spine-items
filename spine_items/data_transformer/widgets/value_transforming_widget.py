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
Contains a widget to set up a value transformer manipulator.

:author: A. Soininen (VTT)
:date:   24.5.2021
"""
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QWidget, QMessageBox, QTreeWidgetItem

from spinedb_api import DatabaseMapping, SpineDBAPIError
from ..commands import InsertRow, RemoveRow
from ..settings import ValueTransformSettings
from ..mvcmodels.value_transformations_table_model import (
    ValueTransformationsTableModel,
    TransformationsTableColumn,
    TransformationsTableRole,
)
from .instructions_editor import InstructionsEditor


class ValueTransformingWidget(QWidget):
    """A widget to edit parameter value transformer settings."""

    def __init__(self, undo_stack, settings=None):
        """
        Args:
            undo_stack (QUndoStack)
            settings (ValueTransformSettings, optional): filter settings
        """
        super().__init__()
        self._undo_stack = undo_stack
        from ..ui.value_transformer_editor import Ui_Form

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self._transformations_table_model = ValueTransformationsTableModel(settings, self._undo_stack, self)
        self._ui.transformations_table_view.setModel(self._transformations_table_model)
        self._instructions_editor = InstructionsEditor(
            self._ui, self._transformations_table_model, self._undo_stack, self
        )
        self._ui.add_parameter_button.clicked.connect(self._add_parameter)
        self._ui.remove_parameter_button.clicked.connect(self._ui.remove_parameter_action.trigger)
        self._ui.remove_parameter_action.triggered.connect(self._remove_parameters)
        self._ui.transformations_table_view.addAction(self._ui.remove_parameter_action)

    @Slot(bool)
    def _add_parameter(self, checked):
        """Adds a new parameter row.

        Args:
            checked (bool): unused
        """
        row = self._transformations_table_model.rowCount()
        self._undo_stack.push(
            InsertRow("add parameter", self._transformations_table_model, row, ("class", "parameter", []))
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
        rows = tuple(i.row() for i in indexes)
        if len(rows) == 1:
            self._undo_stack.push(RemoveRow("remove parameter", self._transformations_table_model, rows[0]))
        else:
            self._undo_stack.beginMacro("remove parameters")
            for row in reversed(sorted(rows)):
                self._undo_stack.push(RemoveRow("", self._transformations_table_model, row))
            self._undo_stack.endMacro()

    def load_data(self, url):
        """
        Loads parameter data from given URL.

        Args:
            url (str): database URL
        """
        self._ui.available_parameters_tree_view.load_data(url)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        settings = dict()
        for row in range(self._transformations_table_model.rowCount()):
            entity_class = self._transformations_table_model.index(row, TransformationsTableColumn.CLASS).data()
            parameter = self._transformations_table_model.index(row, TransformationsTableColumn.PARAMETER).data()
            instructions = self._transformations_table_model.index(row, TransformationsTableColumn.INSTRUCTIONS).data(
                TransformationsTableRole.INSTRUCTIONS
            )
            settings.setdefault(entity_class, {})[parameter] = instructions
        return ValueTransformSettings(settings)
