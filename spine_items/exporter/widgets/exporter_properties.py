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

"""Exporter properties widget."""
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase
from ..item_info import ItemInfo


class ExporterProperties(PropertiesWidgetBase):
    """A main window widget to show GdxExport item's properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): a main window instance
        """
        from ..ui.exporter_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(toolbox)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        model = toolbox.filtered_spec_factory_models[ItemInfo.item_type()]
        self.ui.specification_combo_box.setModel(model)

    @property
    def ui(self):
        """The UI form of this widget."""
        return self._ui
