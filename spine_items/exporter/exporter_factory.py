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

"""Contains :class:`ExporterFactory`."""
from PySide6.QtGui import QColor
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .exporter import Exporter
from .exporter_icon import ExporterIcon
from .widgets.exporter_properties import ExporterProperties
from .widgets.specification_editor_window import SpecificationEditorWindow
from .widgets.add_exporter_widget import AddExporterWidget
from .widgets.specification_menu import SpecificationMenu


class ExporterFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        """See base class."""
        return Exporter

    @staticmethod
    def icon():
        """See base class."""
        return ":/icons/item_icons/database-export.svg"

    @staticmethod
    def icon_color():
        return QColor("maroon")

    @staticmethod
    def supports_specifications():
        """See base class."""
        return True

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        """See base class."""
        return AddExporterWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        """See base class."""
        return ExporterIcon(toolbox, ExporterFactory.icon(), ExporterFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        """See base class."""
        return Exporter.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        """See base class."""
        return ExporterProperties(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        """See base class."""
        return SpecificationMenu(parent, index)

    @staticmethod
    def make_specification_editor(toolbox, specification=None, item=None, **kwargs):
        """See base class."""
        url_model = item.full_url_model() if item is not None else None
        return SpecificationEditorWindow(toolbox, specification, item, url_model)
