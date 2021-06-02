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
Contains classes to manage parameter renaming.

:author: A. Soininen (VTT)
:date:   31.5.2021
"""
from PySide2.QtCore import QObject, Slot

from ..commands import InsertRow, RemoveRow
from ..mvcmodels.parameter_renames_table_model import ParameterRenamesTableModel, RenamesTableColumn
from ..settings import ParameterRenamingSettings


class ParameterRename(QObject):
    def __init__(self, ui, undo_stack, settings, parent):
        """
        Args:
            ui (Ui_Form): specification editor's UI
            undo_stack (QUndoStack): undo stack
            settings (ParameterRenamingSettings, optional): initial settings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._ui = ui
        self._undo_stack = undo_stack
        self._rename_table_model = ParameterRenamesTableModel(settings, self._undo_stack, self)
        self._ui.parameter_rename_table_view.setModel(self._rename_table_model)
        self._ui.parameter_rename_table_view.addAction(self._ui.remove_parameter_rename_action)
        self._ui.add_parameter_button.clicked.connect(self._add_parameter)
        self._ui.remove_parameter_button.clicked.connect(self._ui.remove_parameter_rename_action.trigger)
        self._ui.remove_parameter_rename_action.triggered.connect(self._remove_parameters)

    @Slot(bool)
    def _add_parameter(self, checked):
        """Adds a new parameter row.

        Args:
            checked (bool): unused
        """
        row = self._rename_table_model.rowCount()
        self._undo_stack.push(InsertRow("add parameter", self._rename_table_model, row, ["class", "parameter", ""]))

    @Slot(bool)
    def _remove_parameters(self, checked):
        """Removes selected parameter row.

        Args:
            checked (bool): unused
        """
        indexes = self._ui.parameter_rename_table_view.selectionModel().selectedIndexes()
        if not indexes:
            return
        rows = set(i.row() for i in indexes)
        if len(rows) == 1:
            self._undo_stack.push(RemoveRow("remove parameter", self._rename_table_model, next(iter(rows))))
        else:
            self._undo_stack.beginMacro("remove parameters")
            for row in reversed(sorted(rows)):
                self._undo_stack.push(RemoveRow("", self._rename_table_model, row))
            self._undo_stack.endMacro()

    def load_data(self, url):
        """
        Loads entity class names from given URL.

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
        for row in range(self._rename_table_model.rowCount()):
            entity_class = self._rename_table_model.index(row, RenamesTableColumn.CLASS).data()
            parameter = self._rename_table_model.index(row, RenamesTableColumn.PARAMETER).data()
            new_name = self._rename_table_model.index(row, RenamesTableColumn.NEW_NAME).data()
            settings.setdefault(entity_class, {})[parameter] = new_name
        return ParameterRenamingSettings(settings)

    def show(self):
        """Shows docks."""
        self._ui.load_database_dock.show()
        self._ui.possible_parameters_dock.show()
        self._ui.parameter_rename_dock.show()

    def tear_down(self):
        """Hides docks and releases resources."""
        self._ui.load_database_dock.hide()
        self._ui.possible_parameters_dock.hide()
        self._ui.parameter_rename_dock.hide()
