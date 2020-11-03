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
Contains a widget to set up a scenario filter.

:author: A. Soininen (VTT)
:date:   30.10.2020
"""
from PySide2.QtWidgets import QMessageBox, QWidget
from spinedb_api import DatabaseMapping, SpineDBAPIError
from ..settings import ScenarioFilterSettings


class ScenarioFilterWidget(QWidget):
    """Widget for scenario filter settings."""

    def __init__(self, settings=None):
        """
        Args:
            settings (ScenarioFilterSettings): filter settings
        """
        super().__init__()
        from ..ui.selector import Ui_Form

        self._ui = Ui_Form()
        self._ui.setupUi(self)
        if isinstance(settings, ScenarioFilterSettings):
            self._ui.selection_combo_box.addItem(settings.scenario, settings.scenario)

    def load_data(self, url):
        """
        Loads scenario names from given URL.

        Args:
            url (str): database URL
        """
        try:
            db_map = DatabaseMapping(url)
        except SpineDBAPIError as error:
            QMessageBox.information(self, "Error while opening database", f"Could not open database {url}:\n{error}")
            return
        scenarios = dict()
        try:
            scenario_rows = db_map.query(db_map.scenario_sq).all()
            scenarios = {row.name: row.active for row in scenario_rows}
        except SpineDBAPIError as error:
            QMessageBox.information(
                self, "Error while reading database", f"Could not read from database {url}:\n{error}"
            )
        finally:
            db_map.connection.close()
        self._ui.selection_combo_box.clear()
        previous_scenario = self._ui.selection_combo_box.currentData()
        active = sorted([scenario for scenario, active in scenarios.items() if active])
        inactive = sorted([scenario for scenario, active in scenarios.items() if not active])
        for scenario in active:
            self._ui.selection_combo_box.addItem(scenario + " (active)", scenario)
        for scenario in inactive:
            self._ui.selection_combo_box.addItem(scenario, scenario)
        i = self._ui.selection_combo_box.findData(previous_scenario)
        if i >= 0:
            self._ui.selection_combo_box.setCurrentIndex(i)

    def settings(self):
        """
        Returns filter's settings.

        Returns:
            FilterSettings: settings
        """
        return ScenarioFilterSettings(self._ui.selection_combo_box.currentData())
