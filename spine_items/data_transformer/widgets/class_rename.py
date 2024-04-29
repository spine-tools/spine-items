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

"""Contains classes to manage entity class renaming."""
from PySide6.QtCore import QObject, Qt, Slot, QSortFilterProxyModel
from ..commands import RemoveRow, InsertRow
from ..mvcmodels.class_renames_table_model import ClassRenamesTableModel
from ..settings import EntityClassRenamingSettings
from .copy_paste import copy_table_data, paste_table_data


class ClassRename(QObject):
    _MIME_TYPE = "application/spine-dtclassrename"

    def __init__(self, ui, undo_stack, settings, parent):
        """
        Args:
            ui (Ui_Form): specification editor's UI
            undo_stack (QUndoStack): undo stack
            settings (EntityClassRenamingSettings, optional): initial settings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._ui = ui
        self._undo_stack = undo_stack
        name_map = settings.name_map if isinstance(settings, EntityClassRenamingSettings) else {}
        self._rename_table_model = ClassRenamesTableModel(undo_stack, name_map)
        self._sorted_rename_table_model = QSortFilterProxyModel(self)
        self._sorted_rename_table_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self._sorted_rename_table_model.setSourceModel(self._rename_table_model)
        self._ui.class_rename_table_view.setModel(self._sorted_rename_table_model)
        self._ui.class_rename_table_view.addAction(self._ui.remove_class_rename_action)
        self._ui.add_class_button.clicked.connect(self._add_class)
        self._ui.remove_class_rename_action.triggered.connect(self._remove_class)
        self._ui.remove_class_button.clicked.connect(self._ui.remove_class_rename_action.trigger)
        self._ui.class_rename_table_view.addAction(self._ui.copy_class_rename_data_action)
        self._ui.copy_class_rename_data_action.triggered.connect(self._copy_table_data)
        self._ui.class_rename_table_view.addAction(self._ui.paste_class_rename_data_action)
        self._ui.paste_class_rename_data_action.triggered.connect(self._paste_table_data)

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
        indexes = self._ui.class_rename_table_view.selectionModel().selectedIndexes()
        if not indexes:
            return
        rows = set(self._sorted_rename_table_model.mapToSource(i).row() for i in indexes)
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

    @Slot(bool)
    def _copy_table_data(self, checked):
        """Copies data to clipboard.

        Args:
            checked (bool): unused
        """
        copy_table_data(self._ui.class_rename_table_view, self._MIME_TYPE)

    @Slot(bool)
    def _paste_table_data(self, checked):
        """Pastes data from clipboard.

        Args:
            checked (bool): unused
        """
        paste_table_data(self._ui.class_rename_table_view, self._MIME_TYPE, self._undo_stack)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        return EntityClassRenamingSettings(self._rename_table_model.renaming_settings())

    def show(self):
        """Shows docks."""
        self._ui.load_database_dock.show()
        self._ui.possible_classes_dock.show()
        self._ui.class_rename_dock.show()

    def tear_down(self):
        """Hides docks and releases resources."""
        self._ui.load_database_dock.hide()
        self._ui.possible_classes_dock.hide()
        self._ui.class_rename_dock.hide()
