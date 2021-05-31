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
Contains a widget to set up a renamer filter.

:author: A. Soininen (VTT)
:date:   30.10.2020
"""
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget
from ..mvcmodels.class_renames_table_model import ClassRenamesTableModel
from ..settings import EntityClassRenamingSettings
from ..commands import InsertRow, RemoveRow


class EntityClassRenamingWidget(QWidget):
    """Widget for entity class renamer settings."""

    def __init__(self, undo_stack, settings=None):
        """
        Args:
            undo_stack (QUndoStack): undo stack
            settings (EntityClassRenamingSettings): filter settings
        """
        super().__init__()
        from ..ui.class_renamer_editor import Ui_Form  # pylint: disable=import-outside-toplevel

        self._undo_stack = undo_stack
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        name_map = settings.name_map if isinstance(settings, EntityClassRenamingSettings) else {}
        self._rename_table_model = ClassRenamesTableModel(undo_stack, name_map)
        self._ui.renaming_table_view.setModel(self._rename_table_model)
        self._ui.renaming_table_view.addAction(self._ui.remove_class_action)
        self._ui.add_class_button.clicked.connect(self._add_class)
        self._ui.remove_class_action.triggered.connect(self._remove_class)
        self._ui.remove_class_button.clicked.connect(self._ui.remove_class_action.trigger)

    @Slot(bool)
    def _add_class(self, checked):
        """Pushes an add class command to undo stack.

        Args:
            checked (bool): unused
        """
        row = self._rename_table_model.rowCount()
        self._undo_stack.push(InsertRow("add class", self._rename_table_model, row, ["class", ""]))

    @Slot(bool)
    def _remove_class(self, checked):
        """Pushes a remove class command to undo stack.

        Args:
            checked (bool) unused
        """
        indexes = self._ui.renaming_table_view.selectionModel().selectedIndexes()
        if not indexes:
            return
        rows = set(i.row() for i in indexes)
        if len(rows) == 1:
            self._undo_stack.push(RemoveRow("remove class", self._rename_table_model, next(iter(rows))))
        else:
            self._undo_stack.beginMacro("remove classes")
            for row in reversed(sorted(rows)):
                self._undo_stack.push(RemoveRow("", self._rename_table_model, row))
            self._undo_stack.endMacro()

    def load_data(self, url):
        """
        Loads entity class names from given URL.

        Args:
            url (str): database URL
        """
        self._ui.available_classes_tree_widget.load_data(url)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        return EntityClassRenamingSettings(self._rename_table_model.renaming_settings())
