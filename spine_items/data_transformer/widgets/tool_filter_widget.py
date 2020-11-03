######################################################################################################################
# Copyright (C) 2017-2020 Spine project consortium
# This file is part of Spine Items.
# Spine Items is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################
"""
Contains a widget to set up a tool filter.

:author: A. Soininen (VTT)
:date:   2.11.2020
"""

from PySide2.QtWidgets import QMessageBox, QWidget
from spinedb_api import DatabaseMapping, SpineDBAPIError
from ..settings import ToolFilterSettings


class ToolFilterWidget(QWidget):
    """Widget for tool filter settings."""

    def __init__(self, settings=None):
        """
        Args:
            settings (ToolFilterSettings): filter settings
        """
        super().__init__()
        from ..ui.selector import Ui_Form

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        if isinstance(settings, ToolFilterSettings):
            self._ui.selection_combo_box.addItem(settings.tool)

    def load_data(self, url):
        """
        Loads tool names from given URL.

        Args:
            url (str): database URL
        """
        try:
            db_map = DatabaseMapping(url)
        except SpineDBAPIError as error:
            QMessageBox.information(self, "Error while opening database", f"Could not open database {url}:\n{error}")
            return
        tools = list()
        try:
            tools = [row.name for row in db_map.query(db_map.tool_sq).all()]
        except SpineDBAPIError as error:
            QMessageBox.information(
                self, "Error while reading database", f"Could not read from database {url}:\n{error}"
            )
        finally:
            db_map.connection.close()
        self._ui.selection_combo_box.clear()
        previous_tool = self._ui.selection_combo_box.currentText()
        for tool in tools:
            self._ui.selection_combo_box.addItem(tool)
        i = self._ui.selection_combo_box.findText(previous_tool)
        if i >= 0:
            self._ui.selection_combo_box.setCurrentIndex(i)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        return ToolFilterSettings(self._ui.selection_combo_box.currentText())
