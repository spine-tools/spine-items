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

"""The ViewFactory class."""
from PySide6.QtGui import QColor
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .view import View
from .view_icon import ViewIcon
from .widgets.view_properties_widget import ViewPropertiesWidget
from .widgets.add_view_widget import AddViewWidget


class ViewFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return View

    @staticmethod
    def icon():
        return ":/icons/item_icons/binoculars.svg"

    @staticmethod
    def icon_color():
        return QColor("green")

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddViewWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return ViewIcon(toolbox, ViewFactory.icon(), ViewFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        return View.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        return ViewPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        raise NotImplementedError()

    @staticmethod
    def make_specification_editor(toolbox, specification=None, item=None, **kwargs):
        """See base class."""
        raise NotImplementedError()
