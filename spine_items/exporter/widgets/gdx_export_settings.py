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
Export item's settings window for .gdx export.

:author: A. Soininen (VTT)
:date:   9.9.2019
"""

from copy import deepcopy
import enum
from PySide2.QtCore import QItemSelection, Qt, Signal, Slot
from PySide2.QtWidgets import QDialogButtonBox, QMessageBox, QWidget
import spinetoolbox.spine_io.exporters.gdx as gdx
from ..list_utils import move_selected_elements_by
from ..mvcmodels.record_list_model import RecordListModel
from ..mvcmodels.set_list_model import SetListModel
from ..settings_state import SettingsState
from .parameter_index_settings_window import ParameterIndexSettingsWindow
from .parameter_merging_settings_window import ParameterMergingSettingsWindow


class State(enum.Enum):
    """Gdx Export Settings window state"""

    OK = enum.auto()
    """Settings are ok."""
    BAD_INDEXING = enum.auto()
    """Not all indexed parameters are set up correctly."""


class GdxExportSettings(QWidget):
    """A setting window for exporting .gdx files."""

    reset_requested = Signal(str)
    """Emitted when Reset Defaults button has been clicked."""
    settings_accepted = Signal()
    """Emitted when the OK button has been clicked."""
    settings_rejected = Signal()
    """Emitted when the Cancel button has been clicked."""

    def __init__(
        self,
        set_settings,
        indexing_settings,
        merging_settings,
        none_fallback,
        none_export,
        database_model,
        exporter_name,
        parent,
    ):
        """
        Args:
            set_settings (gdx.SetSettings): export settings for GAMS sets
            indexing_settings (dict): indexing domain information for indexed parameter values
            merging_settings (dict): parameter merging settings
            none_fallback (NoneFallback): fallback for None parameter values
            none_export (NoneExport): how to handle None values while exporting
            database_model (DatabaseListModel): a mapping from URL to :class:`Database`
            exporter_name (str, optional): name of the Exporter item that opened the window
            parent (QWidget): a parent widget
        """
        from ..ui.gdx_export_settings import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent=parent, f=Qt.Window)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setWindowTitle(f"Gdx Export settings    -- {exporter_name} --")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._database_model = database_model
        self._ui.database_combo_box.setModel(self._database_model)
        self._ui.update_button.clicked.connect(self._request_settings_update)
        self._ui.button_box.accepted.connect(self._accept)
        self._ui.button_box.rejected.connect(self._reject)
        self._ui.set_move_up_button.clicked.connect(self._move_sets_up)
        self._ui.set_move_down_button.clicked.connect(self._move_sets_down)
        self._set_settings = set_settings if set_settings is not None else gdx.SetSettings(set(), set(), dict())
        self._populate_global_parameters_combo_box(self._set_settings)
        self._ui.global_parameters_combo_box.currentIndexChanged[str].connect(self._update_global_parameters_domain)
        self._ui.record_sort_alphabetic.clicked.connect(self._sort_records_alphabetically)
        self._ui.record_move_up_button.clicked.connect(self._move_records_up)
        self._ui.record_move_down_button.clicked.connect(self._move_records_down)
        self._set_list_model = SetListModel(self._set_settings)
        self._ui.set_list_view.setModel(self._set_list_model)
        record_list_model = RecordListModel()
        self._ui.record_list_view.setModel(record_list_model)
        self._ui.set_list_view.selectionModel().selectionChanged.connect(self._populate_set_contents)
        self._ui.open_indexed_parameter_settings_button.clicked.connect(self._show_indexed_parameter_settings)
        self._ui.open_parameter_merging_settings_button.clicked.connect(self._show_parameter_merging_settings)
        self._indexing_settings = indexing_settings if indexing_settings is not None else {}
        self._indexed_parameter_settings_window = None
        self._merging_settings = merging_settings
        self._parameter_merging_settings_window = None
        self._none_fallback = none_fallback
        self._none_export = none_export
        self._init_none_fallback_combo_box(none_fallback)
        self._init_none_export_combo_box(none_export)
        self._ui.none_fallback_combo_box.currentTextChanged.connect(self._set_none_fallback)
        self._ui.none_export_combo_box.currentTextChanged.connect(self._set_none_export)
        self._state = State.OK
        self._check_state()

    @property
    def set_settings(self):
        """the settings object"""
        return self._set_settings

    @property
    def indexing_settings(self):
        """indexing settings dict"""
        return self._indexing_settings

    @property
    def merging_settings(self):
        """dictionary of merging settings"""
        return self._merging_settings

    @property
    def none_fallback(self):
        return self._none_fallback

    @property
    def none_export(self):
        return self._none_export

    def reset_settings(self, set_settings, indexing_settings, merging_settings):
        """Resets all settings."""
        if self._indexed_parameter_settings_window is not None:
            self._indexed_parameter_settings_window.close()
            self._indexed_parameter_settings_window = None
        if self._parameter_merging_settings_window is not None:
            self._parameter_merging_settings_window.close()
            self._parameter_merging_settings_window = None
        self._ui.global_parameters_combo_box.clear()
        self._populate_global_parameters_combo_box(set_settings)
        self._set_settings = set_settings
        self._set_list_model = SetListModel(set_settings)
        self._ui.set_list_view.setModel(self._set_list_model)
        self._ui.set_list_view.selectionModel().selectionChanged.connect(self._populate_set_contents)
        self._ui.record_list_view.setModel(RecordListModel())
        self._indexing_settings = indexing_settings
        self._merging_settings = merging_settings
        self._ui.controls_group.setEnabled(True)
        self._ui.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        self._check_state()

    def settings_reading_cancelled(self):
        self._ui.controls_group.setEnabled(True)
        self._ui.button_box.button(QDialogButtonBox.Ok).setEnabled(True)

    def _check_state(self):
        """Checks if there are parameters in need for indexing."""
        for by_dimensions in self._indexing_settings.values():
            for setting in by_dimensions.values():
                if setting.indexing_domain_name is None:
                    self._ui.indexing_status_label.setText(
                        "<span style='color:#ff3333;white-space: pre-wrap;'>Not all parameters correctly indexed.</span>"
                    )
                    self._state = State.BAD_INDEXING
                    return
        self._state = State.OK
        self._ui.indexing_status_label.setText("")

    @Slot(str)
    def _set_none_fallback(self, option):
        """
        Sets the None fallback option.

        Args:
            option (str): option as a label in the combo box
        """
        if option == "Use it":
            self._none_fallback = gdx.NoneFallback.USE_IT
        else:
            self._none_fallback = gdx.NoneFallback.USE_DEFAULT_VALUE

    def _init_none_fallback_combo_box(self, fallback):
        """
        Sets the current text in None fallback combo box.

        Args:
            fallback (NoneFallback): option
        """
        if fallback == gdx.NoneFallback.USE_IT:
            self._ui.none_fallback_combo_box.setCurrentText("Use it")
        else:
            self._ui.none_fallback_combo_box.setCurrentText("Replace by default value")

    @Slot(str)
    def _set_none_export(self, option):
        """
        Sets the None export option.

        Args:
            option (str): option as a label in the combo box
        """
        if option == "Do not export":
            self._none_export = gdx.NoneExport.DO_NOT_EXPORT
        else:
            self._none_export = gdx.NoneExport.EXPORT_AS_NAN

    def _init_none_export_combo_box(self, export):
        """
        Sets the current text in None export combo box

        Args:
            export (NoneExport): option
        """
        if export == gdx.NoneExport.DO_NOT_EXPORT:
            self._ui.none_export_combo_box.setCurrentText("Do not export")
        else:
            self._ui.none_export_combo_box.setCurrentText("Export as not-a-number")

    def _populate_global_parameters_combo_box(self, settings):
        """(Re)populates the global parameters combo box."""
        self._ui.global_parameters_combo_box.addItem("Nothing selected")
        usable_domains = [name for name in settings.domain_names if not settings.metadata(name).is_additional()]
        self._ui.global_parameters_combo_box.addItems(usable_domains)
        if settings.global_parameters_domain_name:
            self._ui.global_parameters_combo_box.setCurrentText(settings.global_parameters_domain_name)

    def _set_records_ordering_controls_enabled(self, enabled):
        """
        Sets or unsets the enabled state of buttons that control the record key order.

        Args:
            enabled: True if the buttons should be enabled, False otherwise
        """
        self._ui.record_sort_alphabetic.setEnabled(enabled)
        self._ui.record_move_down_button.setEnabled(enabled)
        self._ui.record_move_up_button.setEnabled(enabled)

    @Slot()
    def _accept(self):
        """Emits the settings_accepted signal."""
        if self._state != State.OK:
            QMessageBox.warning(
                self,
                "Bad Parameter Indexing",
                "Parameter indexing not set up correctly. Click 'Indexed parameters...' to open the settings window.",
            )
            return
        self.settings_accepted.emit()
        self.hide()

    @Slot(bool)
    def _move_sets_up(self, checked=False):
        """Moves selected domains and sets up one position."""
        move_selected_elements_by(self._ui.set_list_view, -1)

    @Slot(bool)
    def _move_sets_down(self, checked=False):
        """Moves selected domains and sets down one position."""
        move_selected_elements_by(self._ui.set_list_view, 1)

    @Slot(bool)
    def _move_records_up(self, checked=False):
        """Moves selected records up and position."""
        move_selected_elements_by(self._ui.record_list_view, -1)

    @Slot(bool)
    def _move_records_down(self, checked=False):
        """Moves selected records down on position."""
        move_selected_elements_by(self._ui.record_list_view, 1)

    @Slot()
    def _reject(self):
        """Closes the window."""
        self.close()

    def closeEvent(self, event):
        super().closeEvent(event)
        self.settings_rejected.emit()

    @Slot(bool)
    def _request_settings_update(self, _=True):
        """Requests for fresh settings to be read from the database."""
        url = self._ui.database_combo_box.currentText()
        if not url:
            return
        self._ui.controls_group.setEnabled(False)
        self._ui.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.reset_requested.emit(url)

    @Slot(str)
    def _update_global_parameters_domain(self, text):
        """Updates the global parameters domain name."""
        if text == "Nothing selected":
            text = ""
        self._set_list_model.update_global_parameters_domain(text)

    @Slot(QItemSelection, QItemSelection)
    def _populate_set_contents(self, selected, _):
        """Populates the record list by the selected domain's or set's records."""
        selected_indexes = selected.indexes()
        if not selected_indexes:
            return
        selected_set_name = self._set_list_model.data(selected_indexes[0])
        records = self._set_settings.records(selected_set_name)
        record_model = self._ui.record_list_view.model()
        record_model.reset(records, selected_set_name)
        self._set_records_ordering_controls_enabled(records.is_shufflable())

    @Slot(bool)
    def _sort_records_alphabetically(self, _):
        """Sorts the lists of set records alphabetically."""
        model = self._ui.record_list_view.model()
        model.sort_alphabetically()

    @Slot(bool)
    def _show_indexed_parameter_settings(self, _):
        """Shows the indexed parameter settings window."""
        if self._indexed_parameter_settings_window is None:
            url = self._ui.database_combo_box.currentText()
            scenario = self._database_model.item(url).scenario if url else None
            indexing_settings = deepcopy(self._indexing_settings)
            self._indexed_parameter_settings_window = ParameterIndexSettingsWindow(
                indexing_settings, self._set_settings, url, scenario, self._none_fallback, self
            )
            self._indexed_parameter_settings_window.settings_approved.connect(self._gather_parameter_indexing_settings)
            self._indexed_parameter_settings_window.settings_rejected.connect(
                self._dispose_parameter_indexing_settings_window
            )
        self._indexed_parameter_settings_window.show()

    @Slot(bool)
    def _show_parameter_merging_settings(self, _):
        """Shows the parameter merging settings window."""
        if self._parameter_merging_settings_window is None:
            url = self._ui.database_combo_box.currentText()
            self._parameter_merging_settings_window = ParameterMergingSettingsWindow(
                self._merging_settings, self._set_settings, url, self
            )
            self._parameter_merging_settings_window.settings_approved.connect(self._parameter_merging_approved)
            self._parameter_merging_settings_window.settings_rejected.connect(self._dispose_parameter_merging_window)
        self._parameter_merging_settings_window.show()

    @Slot()
    def _gather_parameter_indexing_settings(self):
        """Gathers settings from the indexed parameters settings window."""
        self._indexing_settings = self._indexed_parameter_settings_window.indexing_settings
        indexing_domains, descriptions = self._indexed_parameter_settings_window.additional_indexing_domains()
        self._set_list_model.update_indexing_domains(indexing_domains, descriptions)
        self._state = State.OK
        self._ui.indexing_status_label.setText("")

    @Slot()
    def _parameter_merging_approved(self):
        """Collects merging settings from the parameter merging window."""
        new_merging_settings = self._parameter_merging_settings_window.merging_settings
        old_domain_names = {s.new_domain_name for setting_list in self._merging_settings.values() for s in setting_list}
        new_domain_names = {s.new_domain_name for setting_list in new_merging_settings.values() for s in setting_list}
        new_records = dict()
        new_descriptions = dict()
        for setting_list in new_merging_settings.values():
            for setting in setting_list:
                merge_records = gdx.merging_records(setting)
                records = new_records.get(setting.new_domain_name)
                if records is None:
                    new_records[setting.new_domain_name] = merge_records
                else:
                    combined_records = gdx.LiteralRecords(records.records + merge_records.records)
                    new_records[setting.new_domain_name] = combined_records
                new_descriptions[setting.new_domain_name] = setting.new_domain_description
        for domain_to_drop in old_domain_names - new_domain_names:
            self._set_list_model.drop_domain(domain_to_drop)
        for domain_to_update in old_domain_names & new_domain_names:
            self._set_list_model.update_domain(
                domain_to_update, new_descriptions[domain_to_update], new_records[domain_to_update]
            )
        for domain_to_add in new_domain_names - old_domain_names:
            self._set_list_model.add_domain(
                domain_to_add, new_descriptions[domain_to_add], new_records[domain_to_add], gdx.Origin.MERGING
            )
        self._merging_settings = new_merging_settings

    @Slot()
    def _dispose_parameter_indexing_settings_window(self):
        """Removes references to the indexed parameter settings window."""
        self._indexed_parameter_settings_window = None

    @Slot()
    def _dispose_parameter_merging_window(self):
        """Removes references to the parameter merging settings window."""
        self._parameter_merging_settings_window = None
