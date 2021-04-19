######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
The ToolFactory class.

:author: M. Marin (KTH)
:date:   15.4.2020
"""

import os
import uuid
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QFileDialog
from spinetoolbox.project_item.project_item_factory import ProjectItemFactory
from .notebook import Notebook
from .notebook_icon import NotebookIcon
from .widgets.notebook_properties_widget import NotebookPropertiesWidget
from .widgets.notebook_specification_editor_window import NotebookSpecificationEditorWindow
from .widgets.add_notebook_widget import AddNotebookWidget
from .widgets.custom_menus import NotebookSpecificationMenu


class NotebookFactory(ProjectItemFactory):
    @staticmethod
    def item_class():
        return Notebook

    @staticmethod
    def icon():
        return ":/icons/item_icons/hammer.svg"

    @staticmethod
    def icon_color():
        return QColor("green")

    @staticmethod
    def supports_specifications():
        return True

    @staticmethod
    def make_add_item_widget(toolbox, x, y, specification):
        return AddNotebookWidget(toolbox, x, y, specification)

    @staticmethod
    def make_icon(toolbox):
        return NotebookIcon(toolbox, NotebookFactory.icon(), NotebookFactory.icon_color())

    @staticmethod
    def make_item(name, item_dict, toolbox, project):
        return Notebook.from_dict(name, item_dict, toolbox, project)

    @staticmethod
    def make_properties_widget(toolbox):
        return NotebookPropertiesWidget(toolbox)

    @staticmethod
    def make_specification_menu(parent, index):
        return NotebookSpecificationMenu(parent, index)

    @staticmethod
    def show_specification_widget(toolbox, specification=None, item=None, **kwargs):
        """See base class."""
        NotebookSpecificationEditorWindow(toolbox, specification, item).show()

    @staticmethod
    def repair_specification(toolbox, specification):
        """See base class."""
        if not os.path.isabs(specification.path):
            specification.path = os.path.normpath(
                os.path.join(os.path.dirname(specification.definition_file_path), specification.path)
            )
        # Check that main program file exists. If not, log a message with an anchor to find it
        filename = specification.includes[0]
        full_path = os.path.join(specification.path, filename)
        if not os.path.isfile(full_path):
            url = str(uuid.uuid4())
            toolbox.register_anchor_callback(
                url, lambda t=toolbox, f=filename, s=specification: _find_main_program_file(t, filename, specification)
            )
            toolbox.msg_error.emit(
                f"Notebook spec <b>{specification.name}</b> won't work because "
                f".ipynb file <b>{full_path}</b> doesn't exist. "
                f"<a style='color:white;' href='{url}'><b>[find it]</b></a>"
            )


def _find_main_program_file(toolbox, filename, specification):
    """Shows a file dialog where the user can find the missing .ipynb file of a notebook spec.
    Updates the spec if good.

    Args:
        toolbox (ToolboxUI): The toolbox QMainWindow
        filename (str): The name of the .ipynb file
        specification (NotebookSpecification): The spec to update
    """
    answer = QFileDialog.getOpenFileName(toolbox, f"Select {filename}", toolbox._project.project_dir)
    if answer[0] == "":  # Cancel button clicked
        return
    specification.path, specification.includes[0] = os.path.split(answer[0])
    toolbox.update_specification(specification)
