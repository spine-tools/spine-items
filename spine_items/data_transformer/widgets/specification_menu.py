######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains :class:`SpecificationMenu`.

:author: A. Soininen (VTT)
:date:   2.10.2020
"""
from spine_items.widgets.custom_menus import ItemSpecificationMenu


class SpecificationMenu(ItemSpecificationMenu):
    """Context menu class for Data transformer specifications."""

    def __init__(self, parent, index):
        """
        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            index (QModelIndex): the index from specification model
        """
        super().__init__(parent, index)
