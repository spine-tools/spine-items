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

"""View properties widget."""
from PySide6.QtCore import Slot, QPoint
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase
from .custom_menus import ViewRefsContextMenu, ViewSelectionsContextMenu


class ViewPropertiesWidget(PropertiesWidgetBase):
    """Widget for the View Item Properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        from ..ui.view_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(toolbox)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Class attributes
        self.view_prop_context_menu = None
        self.connect_signals()

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.treeView_references.customContextMenuRequested.connect(self.show_view_refs_context_menu)
        self.ui.treeView_pinned_values.customContextMenuRequested.connect(self.show_view_selections_context_menu)

    @Slot(QPoint)
    def show_view_refs_context_menu(self, pos):
        """Create and show a context-menu in View refs.

        Args:
            pos (QPoint): Mouse position
        """
        view = self._toolbox.active_project_item
        global_pos = self.ui.treeView_references.viewport().mapToGlobal(pos)
        self.view_prop_context_menu = ViewRefsContextMenu(self, global_pos, view)
        option = self.view_prop_context_menu.get_action()
        if option == "Pin values...":
            view.pin_values()
        elif option == "Open editor...":
            view.open_editor()
        self.view_prop_context_menu.deleteLater()
        self.view_prop_context_menu = None

    @Slot(QPoint)
    def show_view_selections_context_menu(self, pos):
        """Create and show a context-menu in View selections.

        Args:
            pos (QPoint): Mouse position
        """
        view = self._toolbox.active_project_item
        global_pos = self.ui.treeView_pinned_values.viewport().mapToGlobal(pos)
        self.view_prop_context_menu = ViewSelectionsContextMenu(self, global_pos, view)
        option = self.view_prop_context_menu.get_action()
        if option == "Plot":
            view.plot_selected_pinned_values()
        elif option == "Copy plot data":
            view.copy_selected_pinned_value_plot_data()
        elif option == "Unpin":
            view.unpin_selected_pinned_values()
        elif option == "Rename...":
            view.renamed_selected_pinned_value()
        self.view_prop_context_menu.deleteLater()
        self.view_prop_context_menu = None
