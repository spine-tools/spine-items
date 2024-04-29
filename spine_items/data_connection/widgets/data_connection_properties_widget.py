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

"""Data connection properties widget."""
import os
from PySide6.QtCore import QPoint, Qt, Slot, QUrl
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase
from .custom_menus import DcRefContextMenu, DcDataContextMenu


class DataConnectionPropertiesWidget(PropertiesWidgetBase):
    """Widget for the Data Connection Item Properties."""

    def __init__(self, toolbox):
        """

        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        from ..ui.data_connection_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(toolbox)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Class attributes
        self.connect_signals()

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.treeView_dc_references.customContextMenuRequested.connect(self.show_references_context_menu)
        self.ui.treeView_dc_data.customContextMenuRequested.connect(self.show_data_context_menu)

    @Slot(QPoint)
    def show_references_context_menu(self, pos):
        """Create and show a context-menu in data connection properties
        references view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.treeView_dc_references.indexAt(pos)
        dc = self._active_item
        global_pos = self.ui.treeView_dc_references.viewport().mapToGlobal(pos)
        dc_ref_context_menu = DcRefContextMenu(self, global_pos, index, dc)
        option = dc_ref_context_menu.get_action()
        dc_ref_context_menu.deleteLater()
        if option == "Open containing directory...":
            ref_path = self.ui.treeView_dc_references.model().itemFromIndex(index).data(Qt.ItemDataRole.DisplayRole)
            ref_dir = os.path.split(ref_path)[0]
            file_url = "file:///" + ref_dir
            self._toolbox.open_anchor(QUrl(file_url, QUrl.TolerantMode))
        elif option == "Open...":
            dc.open_reference(index)
        elif option == "Add file reference(s)...":
            dc.show_add_file_references_dialog()
        elif option == "Add database reference...":
            dc.show_add_db_reference_dialog()
        elif option == "Remove reference(s)":
            dc.remove_references()
        elif option == "Copy file reference(s) to project":
            dc.copy_to_project()
        elif option == "Refresh reference(s)":
            dc.refresh_references()
        elif option != "None":
            raise RuntimeError(f"Unknown menu option '{option}'")

    @Slot(QPoint)
    def show_data_context_menu(self, pos):
        """Create and show a context-menu in data connection properties
        data view.

        Args:
            pos (QPoint): Mouse position
        """
        index = self.ui.treeView_dc_data.indexAt(pos)
        dc = self._active_item
        global_pos = self.ui.treeView_dc_data.viewport().mapToGlobal(pos)
        dc_data_context_menu = DcDataContextMenu(self, global_pos, index, dc)
        option = dc_data_context_menu.get_action()
        dc_data_context_menu.deleteLater()
        if option == "New file...":
            dc.make_new_file()
        elif option == "Open...":
            dc.open_data_file(index)
        elif option == "Remove file(s)":
            dc.remove_files()
        elif option == "Open directory...":
            dc.open_directory()
        elif option != "None":
            raise RuntimeError(f"Unknown menu option '{option}'")
