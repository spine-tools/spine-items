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
from spinetoolbox.widgets.properties_widget import PropertiesWidgetBase
from spinedb_api import SUPPORTED_DIALECTS
from ...widgets import UrlSelectorMixin


class DataStorePropertiesWidget(UrlSelectorMixin, PropertiesWidgetBase):
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
        self.ui.url_selector_widget.setup(
            list(SUPPORTED_DIALECTS.keys()), self._select_sqlite_file, True, self._toolbox
        )

    def set_item(self, data_store):
        """Sets the active project item for the properties widget.

        Args:
            data_store (DataStore): data store
        """
        self._active_item = data_store

    def unset_item(self):
        """Unsets the active item."""
        self._active_item = None

    def _select_sqlite_file(self):
        """Lets active item select an SQLite file.

        Returns:
            str: file path or None if operation was cancelled
        """
        if self._active_item is None:
            return None
        return self._active_item.select_sqlite_file()
