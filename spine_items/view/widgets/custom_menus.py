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


class ViewRefsContextMenu(CustomContextMenu):
    """Context menu class for the references tree view of the View project item properties."""

    def __init__(self, parent, position, view):
        """

        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            position (QPoint): Position on screen
            view (View): View item that requests the menu
        """
        super().__init__(parent, position)
        selected_references = view.selected_references()
        self.add_action("Pin values...", enabled=bool(selected_references))
        self.add_action("Open editor...", enabled=bool(selected_references))


class ViewSelectionsContextMenu(CustomContextMenu):
    """Context menu class for the pinned values tree view of the View project item properties."""

    def __init__(self, parent, position, view):
        """

        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            position (QPoint): Position on screen
            view (View): View item that requests the menu
        """
        super().__init__(parent, position)
        selected_pinned_values = view.selected_pinned_values()
        self.add_action("Plot", enabled=bool(selected_pinned_values))
        self.add_action("Copy plot data", enabled=len(selected_pinned_values) == 1)
        self.addSeparator()
        self.add_action("Unpin", enabled=bool(selected_pinned_values))
        self.add_action("Rename...", enabled=len(selected_pinned_values) == 1)
