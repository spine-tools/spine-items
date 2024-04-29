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

"""Classes for context menus used alongside the Importer project item."""
from PySide6.QtCore import QPoint, Slot, Signal
from PySide6.QtWidgets import QMenu
from spinetoolbox.widgets.custom_menus import CustomContextMenu, ItemSpecificationMenu, FilterMenuBase
from spinetoolbox.mvcmodels.filter_checkbox_list_model import DataToValueFilterCheckboxListModel
from ..mvcmodels.mappings_model_roles import Role


class FilesContextMenu(CustomContextMenu):
    """Context menu class for source files view in Importer properties tab."""

    def __init__(self, parent, position, index):
        """
        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            position (QPoint): Position on screen
            index (QModelIndex): Index of item that requested the context-menu
        """
        super().__init__(parent, position)
        if not index.isValid():
            self.add_action("Open directory...")
        else:
            self.add_action("Open import editor")
            self.add_action("Select connector type")
            self.addSeparator()
            self.add_action("Open directory...")


class SpecificationMenu(ItemSpecificationMenu):
    """Context menu class for Data transformer specifications."""


class SourceListMenu(CustomContextMenu):
    """
    Menu for source list.
    """

    def __init__(self, parent, position, can_paste_option, can_paste_mapping):
        super().__init__(parent, position)
        self.add_action("Copy options")
        self.add_action("Copy mappings")
        self.add_action("Copy options and mappings")
        self.addSeparator()
        self.add_action("Paste options", enabled=can_paste_option)
        self.add_action("Paste mappings", enabled=can_paste_mapping)
        self.add_action("Paste options and mappings", enabled=can_paste_mapping & can_paste_option)


class MappingListMenu(CustomContextMenu):
    """
    Menu for source list.
    """

    def __init__(self, parent, position, can_copy, can_paste):
        super().__init__(parent, position)
        self.add_action("Copy mapping(s)", enabled=can_copy)
        self.add_action("Paste mapping(s)", enabled=can_paste)


class SourceDataTableMenu(QMenu):
    """
    A context menu for the source data table, to let users define a Mapping from a data table.
    """

    def __init__(self, model, ui):
        """
        Args:
            model (MappingsModel): model
            ui (Any): import editor's UI
        """
        super().__init__(ui.source_data_table)
        self._model = model
        self._ui = ui

    def _set_mapping(self, flattened_mappings, index, map_type=None, value=None):
        self._model.change_component_mapping(flattened_mappings, index, map_type, value)

    @Slot(QPoint)
    def request_menu(self, pos=None):
        indexes = self.parent().selectedIndexes()
        if not indexes:
            return
        self.clear()
        index = indexes[0]
        row = index.row() + 1
        col = index.column() + 1

        list_index = self._ui.mapping_list.selectionModel().currentIndex()
        if list_index.isValid():
            mapping_names = [
                self._model.index(row, 0, list_index).data() for row in range(self._model.rowCount(list_index))
            ]
            flattened_mappings = list_index.data(Role.FLATTENED_MAPPINGS)
        else:
            mapping_names = None
            flattened_mappings = None

        def create_callback(row, map_type, value):
            component_index = self._model.index(row, 0, list_index)
            return lambda: self._set_mapping(flattened_mappings, component_index, map_type, value)

        menus = [
            ("Map column to...", "Column", col),
            ("Map header to...", "Column Header", col),
            ("Map row to...", "Row", row),
            ("Map all headers to...", "Headers", 0),
        ]

        for title, map_type, value in menus:
            m = self.addMenu(title)
            if mapping_names is not None:
                for row, name in enumerate(mapping_names):
                    m.addAction(name).triggered.connect(create_callback(row, map_type, value))
            else:
                m.addAction("<no mapping selected>").setEnabled(False)

        global_pos = self.parent().mapToGlobal(QPoint(5, 20))
        menu_pos = global_pos + pos
        self.move(menu_pos)
        self.show()


class SimpleFilterMenu(FilterMenuBase):
    filterChanged = Signal(set)

    def __init__(self, parent, show_empty=True):
        """
        Args:
            parent (SpineDBEditor)
        """
        super().__init__(parent)
        self._set_up(DataToValueFilterCheckboxListModel, self, str, show_empty=show_empty)

    def emit_filter_changed(self, valid_values):
        self.filterChanged.emit(valid_values)
