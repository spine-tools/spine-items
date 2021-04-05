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
Classes for context menus used alongside the Importer project item.

:author: P. Savolainen (VTT)
:date:   9.1.2018
"""

from PySide2.QtCore import Qt, QPoint, Slot
from PySide2.QtWidgets import QMenu
from spinetoolbox.widgets.custom_menus import CustomContextMenu, ItemSpecificationMenu


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

    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget): parent widget
        """
        super().__init__(parent)
        self._model = None

    def set_model(self, model):
        """
        Sets target mapping specification.

        Args:
            model (MappingSpecificationModel): mapping specification
        """
        self._model = model

    def set_mapping(self, name="", map_type=None, value=None):
        if self._model is None:
            return
        self._model.change_component_mapping(name, map_type, value)

    @Slot(QPoint)
    def request_menu(self, pos=None):
        if not self._model:
            return
        indexes = self.parent().selectedIndexes()
        if not indexes:
            return
        self.clear()
        index = indexes[0]
        row = index.row() + 1
        col = index.column() + 1

        def create_callback(name, map_type, value):
            return lambda: self.set_mapping(name, map_type, value)

        mapping_names = [
            self._model.data(self._model.createIndex(i, 0), Qt.DisplayRole) for i in range(self._model.rowCount())
        ]

        menus = [
            ("Map column to...", "Column", col),
            ("Map header to...", "Column Header", col),
            ("Map row to...", "Row", row),
            ("Map all headers to...", "Headers", 0),
        ]

        for title, map_type, value in menus:
            m = self.addMenu(title)
            for name in mapping_names:
                m.addAction(name).triggered.connect(create_callback(name, map_type, value))

        global_pos = self.parent().mapToGlobal(QPoint(5, 20))
        menu_pos = global_pos + pos
        self.move(menu_pos)
        self.show()
