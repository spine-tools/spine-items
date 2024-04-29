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

"""Widget shown to user when a new Importer is created."""
from spinetoolbox.widgets.add_project_item_widget import AddProjectItemWidget
from ..importer import Importer
from ..item_info import ItemInfo


class AddImporterWidget(AddProjectItemWidget):
    """A widget to query user's preferences for a new item."""

    def __init__(self, toolbox, x, y, spec=""):
        """
        Args:
            toolbox (ToolboxUI): Parent widget
            x (float): X coordinate of new item
            y (float): Y coordinate of new item
            spec (str): item specification's name
        """
        super().__init__(toolbox, x, y, Importer, spec=spec)

    def call_add_item(self):
        """Creates new Item according to user's selections."""
        spec = self.ui.comboBox_specification.currentText()
        item = {
            self.name: {
                "type": ItemInfo.item_type(),
                "description": self.description,
                "specification": spec,
                "x": self._x,
                "y": self._y,
            }
        }
        self._toolbox.add_project_items(item)
