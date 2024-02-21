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

"""The ImporterFactory class."""
from PySide6.QtGui import QColor
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .widgets.import_editor_window import ImportEditorWindow
from .importer import Importer
from .importer_icon import ImporterIcon
from .widgets.importer_properties_widget import ImporterPropertiesWidget
from .widgets.add_importer_widget import AddImporterWidget
from .widgets.custom_menus import SpecificationMenu


class ImporterFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return Importer

    @staticmethod
    def icon():
        return ":/icons/item_icons/database-import.svg"

    @staticmethod
    def icon_color():
        return QColor("purple")

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddImporterWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return ImporterIcon(toolbox, ImporterFactory.icon(), ImporterFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        return Importer.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        return ImporterPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        return SpecificationMenu(parent, index)

    @staticmethod
    def make_specification_editor(toolbox, specification=None, item=None, **kwargs):
        """See base class."""
        source = kwargs.get("source")
        source_extras = kwargs.get("source_extras")
        return ImportEditorWindow(toolbox, specification, item, source, source_extras)
