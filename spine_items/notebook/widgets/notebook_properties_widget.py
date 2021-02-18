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
Tool properties widget.

:author: M. Marin (KTH)
:date:   12.9.2019
"""

from PySide2.QtWidgets import QWidget
from spinetoolbox.config import TREEVIEW_HEADER_SS


class NotebookPropertiesWidget(QWidget):
    """Widget for the Tool Item Properties.

    Args:
        toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
    """

    def __init__(self, toolbox):
        """Init class."""
        from ..ui.notebook_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__()
        self._toolbox = toolbox
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.treeView_cmdline_args.setStyleSheet(TREEVIEW_HEADER_SS)
        self.ui.treeView_input_files.setStyleSheet(TREEVIEW_HEADER_SS)
        toolbox.ui.tabWidget_item_properties.addTab(self, "Notebook")
        model = self._toolbox.filtered_spec_factory_models["Notebook"]
        self.ui.comboBox_notebook.setModel(model)
