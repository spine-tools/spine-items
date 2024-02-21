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

"""Classes for custom context menus and pop-up menus."""
from spinetoolbox.widgets.custom_menus import CustomContextMenu


class DcRefContextMenu(CustomContextMenu):
    """Context menu class for references view in Data Connection properties."""

    def __init__(self, parent, position, index, dc):
        """
        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            position (QPoint): Position on screen
            index (QModelIndex): Index of item that requested the context-menu
            dc (DataConnection): Data connection item
        """
        super().__init__(parent, position)
        self.add_action("Open...", enabled=dc.current_is_file_ref)
        self.add_action("Open containing directory...", enabled=dc.current_is_file_ref)
        self.addSeparator()
        self.add_action("Add file reference(s)...")
        self.add_action("Add database reference...")
        self.add_action("Remove reference(s)", enabled=dc.any_refs_selected)
        self.add_action("Copy file reference(s) to project", enabled=dc.file_refs_selected)
        self.addSeparator()
        self.add_action("Refresh reference(s)", enabled=dc.any_refs_selected)


class DcDataContextMenu(CustomContextMenu):
    """Context menu class for data view in Data Connection properties."""

    def __init__(self, parent, position, index, dc):
        """
        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            position (QPoint): Position on screen
            index (QModelIndex): Index of item that requested the context-menu
            dc (DataConnection): Data connection item
        """
        super().__init__(parent, position)
        self.add_action("Open...", enabled=index.isValid())
        self.add_action("New file...")
        self.add_action("Remove file(s)", enabled=dc.any_data_selected)
        self.addSeparator()
        self.add_action("Open directory...")
