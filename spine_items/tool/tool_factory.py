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

"""The ToolFactory class."""
import os
import uuid
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFileDialog
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .tool import Tool
from .tool_icon import ToolIcon
from .widgets.tool_properties_widget import ToolPropertiesWidget
from .widgets.tool_specification_editor_window import ToolSpecificationEditorWindow
from .widgets.add_tool_widget import AddToolWidget
from .widgets.custom_menus import ToolSpecificationMenu


class ToolFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return Tool

    @staticmethod
    def icon():
        return ":/icons/item_icons/hammer.svg"

    @staticmethod
    def icon_color():
        return QColor("red")

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddToolWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return ToolIcon(toolbox, ToolFactory.icon(), ToolFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        return Tool.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        return ToolPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        return ToolSpecificationMenu(parent, index)

    @staticmethod
    def make_specification_editor(toolbox, specification=None, item=None, **kwargs):
        return ToolSpecificationEditorWindow(toolbox, specification, item, **kwargs)

    @staticmethod
    def repair_specification(toolbox, specification):
        """See base class."""
        ProjectItemFactory.repair_specification(toolbox, specification)
        # Skip for Executable Tool Specs because it is allowed to not have a main program
        if specification.tooltype == "executable":
            return
        # Check that main program file exists. If not, log a message with an anchor to find it
        filename = specification.includes[0]
        full_path = os.path.join(specification.path, filename)
        if not os.path.isfile(full_path):
            url = str(uuid.uuid4())
            toolbox.register_anchor_callback(
                url, lambda t=toolbox, f=filename, s=specification: _find_main_program_file(t, filename, specification)
            )
            toolbox.msg_error.emit(
                f"Tool spec <b>{specification.name}</b> won't work because "
                f"main program file <b>{full_path}</b> doesn't exist. "
                f"<a style='color:white;' href='{url}'><b>[find it]</b></a>"
            )


def _find_main_program_file(toolbox, filename, specification):
    """Shows a file dialog where the user can find the missing main program file of a tool spec.
    Updates the spec if good.

    Args:
        toolbox (ToolboxUI): The toolbox QMainWindow
        filename (str): The name of the main program file
        specification (ToolSpecification): The spec to update
    """
    answer = QFileDialog.getOpenFileName(toolbox, f"Select {filename}", toolbox.project().project_dir)
    if answer[0] == "":  # Cancel button clicked
        return
    specification = specification.clone()
    specification.path, specification.includes[0] = os.path.split(answer[0])
    toolbox.project().replace_specification(specification.name, specification)
