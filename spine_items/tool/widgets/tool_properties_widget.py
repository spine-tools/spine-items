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

"""Tool properties widget."""
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase


class ToolPropertiesWidget(PropertiesWidgetBase):
    """Widget for the Tool Item Properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        from ..ui.tool_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(toolbox)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        model = self._toolbox.filtered_spec_factory_models["Tool"]
        self.ui.comboBox_tool.setModel(model)
        self.ui.options_widgets = {}
