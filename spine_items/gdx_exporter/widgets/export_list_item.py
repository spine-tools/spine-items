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
A small widget to set up a database in GdxExporter properties tab.

:author: A. Soininen (VTT)
:date:   10.9.2019
"""

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QWidget


_BASE_ALTERNATIVE_TEXT = "Export 'Base' alternative"


class ExportListItem(QWidget):
    """A widget with few controls to select the output file name and open a settings window."""

    file_name_changed = Signal(str, str)
    """Emitted when the file name field is changed."""
    scenario_changed = Signal(str, str)
    """Emitted when selected scenario has changed."""

    def __init__(self, url, file_name, parent=None):
        """
        Args:
            url (str): database URL
            file_name (str): relative path to the exported file name
            parent (QWidget): a parent widget
        """
        from ..ui.export_list_item import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent)
        self._ui = Ui_Form()
        self._url = url
        self._file_name = file_name
        self._ui.setupUi(self)
        self._ui.url_field.setText(url)
        self._ui.out_file_name_edit.setText(file_name)
        self._ui.out_file_name_edit.editingFinished.connect(self._emit_file_name_changed)
        self._ui.scenario_combo_box.currentTextChanged.connect(self._emit_scenario_changed)

    @property
    def out_file_name_edit(self):
        """export file name QLineEdit"""
        return self._ui.out_file_name_edit

    @property
    def url_field(self):
        """Text in the database URL field."""
        return self._ui.url_field

    def update_scenarios(self, scenarios, selected):
        """
        Updates the scenarios combo box.

        Args:
            scenarios (dict): a map from scenario name to boolean active flag
            selected (str, optional): currently selected scenario, None for the 'Base' alternative
        """
        active = [_BASE_ALTERNATIVE_TEXT] + [_activate(name) for name, active in scenarios.items() if active]
        inactive = [name for name, active in scenarios.items() if not active]
        self._ui.scenario_combo_box.clear()
        self._ui.scenario_combo_box.addItems(active)
        self._ui.scenario_combo_box.addItems(inactive)
        active = scenarios.get(selected)
        if active is not None:
            self._ui.scenario_combo_box.setCurrentText(_activate(selected) if active else selected)
        else:
            self._ui.scenario_combo_box.setCurrentIndex(0)

    def make_sure_this_scenario_is_shown_in_the_combo_box(self, scenario):
        """
        Makes sure the given scenario is selected in the combo box.

        Args:
            scenario (str, optional): scenario name
        """
        if scenario is None:
            scenario = _BASE_ALTERNATIVE_TEXT
        if scenario == self._ui.scenario_combo_box.currentText():
            return
        self._ui.scenario_combo_box.blockSignals(True)
        self._ui.scenario_combo_box.setCurrentText(scenario)
        self._ui.scenario_combo_box.blockSignals(False)

    @Slot()
    def _emit_file_name_changed(self):
        """Emits file_name_changed signal."""
        file_name = self._ui.out_file_name_edit.text()
        if self._file_name == file_name:
            return
        self._file_name = file_name
        self.file_name_changed.emit(file_name, self._url)

    @Slot(str)
    def _emit_scenario_changed(self, selected):
        """Emits scenario_changed signal."""
        if selected == _BASE_ALTERNATIVE_TEXT:
            self.scenario_changed.emit(None, self._url)
        else:
            scenario_name, _, active = selected.rpartition(" ")
            if active == "(active)":
                selected = scenario_name
            self.scenario_changed.emit(selected, self._url)


def _activate(scenario):
    """
    Expands active scenario's name so it is recognizable as combo box label.

    Args:
        scenario (str): scenario name

    Returns:
        str: expanded name
    """
    return scenario + " (active)"