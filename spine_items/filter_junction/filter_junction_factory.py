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

"""The FilterJunctionFactory class."""
from PySide6.QtGui import QColor
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .filter_junction import FilterJunction
from .filter_junction_icon import FilterJunctionIcon
from .widgets.add_filter_junction import AddFilterJunction
from .widgets.filter_junction_properties import FilterJunctionProperties


class FilterJunctionFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return FilterJunction

    @staticmethod
    def icon():
        return ":/icons/item_icons/filter-junction.svg"

    @staticmethod
    def icon_color():
        return QColor("darkorchid")

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddFilterJunction(toolbox, x, y)

    @staticmethod
    def make_icon(toolbox):
        return FilterJunctionIcon(toolbox, FilterJunctionFactory.icon(), FilterJunctionFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        return FilterJunction.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        return FilterJunctionProperties(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        raise NotImplementedError()

    @staticmethod
    def make_specification_editor(toolbox, specification=None, item=None, **kwargs):
        """See base class."""
        raise NotImplementedError()
