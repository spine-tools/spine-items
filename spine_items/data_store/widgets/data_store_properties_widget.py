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

"""Data store properties widget."""
from spinedb_api import SUPPORTED_DIALECTS
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase


class DataStorePropertiesWidget(PropertiesWidgetBase):
    """Widget for the Data Store Item Properties."""

    def __init__(self, toolbox):
        """
        Args:
            toolbox (ToolboxUI): The toolbox instance where this widget should be embedded
        """
        from ..ui.data_store_properties import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(toolbox)
        self._active_item = None
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        dialects = ["sqlite"] + list(filter(lambda d: d != "sqlite", SUPPORTED_DIALECTS.keys()))
        self.ui.url_selector_widget.setup(dialects, self._select_sqlite_file, True, self._toolbox)

    def _select_sqlite_file(self):
        """Lets active item select an SQLite file.

        Returns:
            str: file path or None if operation was cancelled
        """
        if self._active_item is None:
            return None
        return self._active_item.select_sqlite_file()
