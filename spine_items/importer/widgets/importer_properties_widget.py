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

"""Importer properties widget."""
from PySide6.QtCore import QPoint, Slot
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase
from .custom_menus import FilesContextMenu
from ..item_info import ItemInfo


class ImporterPropertiesWidget(PropertiesWidgetBase):
    """Widget for the Importer Item Properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        super().__init__(toolbox)
        from ..ui.importer_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        # Class attributes
        self.files_context_menu = None
        model = self._toolbox.filtered_spec_factory_models[ItemInfo.item_type()]
        self.ui.comboBox_specification.setModel(model)
        self.connect_signals()

    def connect_signals(self):
        """Connect signals to slots."""
        self.ui.treeView_files.customContextMenuRequested.connect(self.show_files_context_menu)

    @Slot(QPoint)
    def show_files_context_menu(self, pos):
        """Create and show a context-menu in Importer properties source files view.

        Args:
            pos (QPoint): Mouse position
        """
        ind = self.ui.treeView_files.indexAt(pos)  # Index of selected item in references tree view.
        importer = self._active_item
        global_pos = self.ui.treeView_files.viewport().mapToGlobal(pos)
        self.files_context_menu = FilesContextMenu(self, global_pos, ind)
        option = self.files_context_menu.get_action()
        if option == "Open import editor":
            importer.open_import_editor(ind)
        elif option == "Select connector type":
            importer.select_connector_type(ind)
        elif option == "Open directory...":
            importer.open_directory()
