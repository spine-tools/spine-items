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
Classes for custom context menus and pop-up menus.

:author: P. Savolainen (VTT)
:date:   9.1.2018
"""
import os
from PySide2.QtCore import QUrl, Slot
from spinetoolbox.helpers import open_url
from spinetoolbox.widgets.custom_menus import ItemSpecificationMenu, CustomPopupMenu


class NotebookSpecificationMenu(ItemSpecificationMenu):
    """Menu class for Tool specifications."""

    def __init__(self, parent, index):
        """
        Args:
            parent (QWidget): Parent for menu widget (ToolboxUI)
            index (QModelIndex): the index from specification model
        """
        super().__init__(parent, index)
        self.add_action("Open Jupyter notebook", self._open_jupyter_notebook_file)
        self.add_action("Open Jupyter notebook directory", self._open_jupyter_notebook_dir)

    @Slot()
    def _open_jupyter_notebook_file(self):
        spec = self.parent().specification_model.specification(self.index.row())
        file_path = spec.get_jupyter_notebook_path()
        if file_path is None:
            return
        main_program_url = "file:///" + file_path
        res = open_url(main_program_url)
        if not res:
            filename, file_extension = os.path.splitext(file_path)
            self.parent().msg_error.emit(
                "Unable to open Tool specification main program file {0}. "
                "Make sure that <b>{1}</b> "
                "files are associated with an editor. E.g. on Windows "
                "10, go to Control Panel -> Default Programs to do this.".format(filename, file_extension)
            )

    @Slot()
    def _open_jupyter_notebook_dir(self):
        notebook_specification_path = self.parent().specification_model.specification(self.index.row()).path
        if not notebook_specification_path:
            self.parent().msg_error.emit("Jupyter notebook directory does not exist. Fix this in Notebook spec editor.")
            return
        path_url = "file:///" + notebook_specification_path
        self.parent().open_anchor(QUrl(path_url, QUrl.TolerantMode))


class AddIncludesPopupMenu(CustomPopupMenu):
    """Popup menu class for add includes button in Tool specification editor widget."""

    def __init__(self, parent):
        """
        Args:
            parent (QWidget): Parent widget (ToolSpecificationWidget)
        """
        super().__init__(parent)
        self._parent = parent
        # Open a tool specification file
        self.add_action("New file", self._parent.new_source_file)
        self.addSeparator()
        self.add_action("Open files...", self._parent.show_add_source_files_dialog)
