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
Parameter indexing settings window for .gdx export.

:author: A. Soininen (VTT)
:date:   25.11.2019
"""
from contextlib import contextmanager
from copy import deepcopy
from PySide2.QtCore import QItemSelectionModel, QModelIndex, Qt, Signal, Slot
from PySide2.QtGui import QStandardItem
from PySide2.QtWidgets import QMessageBox, QWidget
from spinedb_api.spine_io.exporters import gdx
from spinedb_api import DatabaseMapping
from .parameter_index_settings import IndexSettingsState, ParameterIndexSettings
from ..mvcmodels.indexing_domain_list_model import IndexingDomainListModel

_PARAMETER_ROLE = Qt.UserRole + 1
_PARAMETER_NAME_ROLE = Qt.UserRole + 2


class ParameterIndexSettingsWindow(QWidget):
    """A window which shows a list of ParameterIndexSettings widgets, one for each parameter with indexed values."""

    settings_approved = Signal()
    """Emitted when the settings have been approved."""
    settings_rejected = Signal()
    """Emitted when the settings have been rejected."""

    def __init__(self, indexing_settings, set_settings, database_path, none_fallback, parent):
        """
        Args:
            indexing_settings (dict): a map from parameter name to a dict of domain names and :class:`IndexingSetting`
            set_settings (SetSettings): export settings
            database_path (str): a database url
            none_fallback (NoneFallback): how to handle None values
            parent (QWidget): a parent widget
        """
        from ..ui.parameter_index_settings_window import Ui_Form  # pylint: disable=import-outside-toplevel

        super().__init__(parent, f=Qt.Window)
        self._set_settings = set_settings
        self._database_mapping = DatabaseMapping(database_path) if database_path else None
        self._enable_domain_updates = True
        self._parameters = gdx.indexed_parameters(self._database_mapping, none_fallback, logger=None)
        self._indexing_settings = self._fix_legacy_indexing_settings(indexing_settings)
        self._ui = Ui_Form()
        self._ui.setupUi(self)
        self.setWindowTitle(f"Gdx Parameter Indexing Settings")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self._ui.splitter.setSizes([400, 50])
        self._ui.button_box.accepted.connect(self._collect_and_hide)
        self._ui.button_box.rejected.connect(self._reject_and_close)
        self._additional_domains_model = IndexingDomainListModel(set_settings, self._parameters)
        self._additional_domains_model.domain_renamed.connect(self._update_after_domain_rename)
        self._additional_domains_model.domains_added.connect(self._add_available_domains)
        self._additional_domains_model.domains_removed.connect(self._remove_available_domains)
        self._ui.additional_domains_list_view.setModel(self._additional_domains_model)
        self._ui.additional_domains_list_view.selectionModel().currentChanged.connect(self._load_additional_domain)
        self._ui.add_domain_button.clicked.connect(self._add_domain)
        self._ui.remove_domain_button.clicked.connect(self._remove_selected_domains)
        self._ui.description_edit.textEdited.connect(self._set_domain_description)
        self._ui.use_expression_radio_button.clicked.connect(self._use_expression)
        self._ui.expression_edit.textChanged.connect(self._update_expression)
        self._ui.length_spin_box.valueChanged.connect(self._update_length)
        self._ui.extract_from_radio_button.clicked.connect(self._use_extraction)
        self._set_additional_domain_widgets_enabled(False)
        self._populate_extract_from_combo()
        self._ui.extract_from_combo_box.currentIndexChanged.connect(self._set_extraction_domain)
        self._settings_widgets = dict()
        self._available_domains = {name: set_settings.records(name) for name in set_settings.domain_names}
        for parameter_name, by_dimensions in self._indexing_settings.items():
            parameter_by_domains = self._parameters.get(parameter_name, {})
            for domain_names, indexing_setting in by_dimensions.items():
                parameter = parameter_by_domains.get(domain_names)
                if parameter is None:
                    parameter = gdx.Parameter(domain_names, [], [])
                settings_widget = ParameterIndexSettings(
                    parameter_name,
                    parameter,
                    indexing_setting,
                    self._available_domains,
                    self._ui.settings_area_contents,
                )
                self._ui.settings_area_layout.insertWidget(0, settings_widget)
                widgets = self._settings_widgets.setdefault(parameter_name, dict())
                widgets[domain_names] = settings_widget
        if not self._indexing_settings:
            self._ui.widget_stack.setCurrentIndex(1)
            return
        self._ui.widget_stack.setCurrentIndex(0)

    @property
    def indexing_settings(self):
        """indexing settings dictionary"""
        return self._indexing_settings

    def additional_indexing_domains(self):
        return self._additional_domains_model.gather_domains(self._parameters)

    def set_domain_updated_enabled(self, enabled):
        """
        Enables or disables updating the indexing settings widgets.

        Args:
            enabled (bool): if True, allow the widgets to update
        """
        self._enable_domain_updates = enabled

    def _switch_additional_domain_widgets_enabled_state(self, using_expression):
        """
        Enabled and disables additional domain widgets.

        Args:
            using_expression (bool): True if expression is used,
                False if record keys are extracted from existing parameter
        """
        self._ui.expression_edit.setEnabled(using_expression)
        self._ui.length_spin_box.setEnabled(using_expression)
        self._ui.extract_from_combo_box.setEnabled(not using_expression)

    def _set_additional_domain_widgets_enabled(self, enabled):
        self._ui.description_edit.setEnabled(enabled)
        self._ui.use_expression_radio_button.setEnabled(enabled)
        self._ui.expression_edit.setEnabled(enabled)
        self._ui.extract_from_radio_button.setEnabled(enabled)
        self._ui.extract_from_combo_box.setEnabled(enabled)

    @Slot(bool)
    def _add_domain(self, _):
        """Creates a new additional domain."""
        self._additional_domains_model.create_new_domain()
        new_current = self._additional_domains_model.index(self._additional_domains_model.rowCount() - 1, 0)
        self._ui.additional_domains_list_view.selectionModel().setCurrentIndex(
            new_current, QItemSelectionModel.ClearAndSelect
        )

    @Slot()
    def _collect_and_hide(self):
        """Collects settings from individual ParameterIndexSettings widgets and hides the window."""
        for parameter_name, widgets in self._settings_widgets.items():
            for domain_names, settings_widget in widgets.items():
                if settings_widget.state != IndexSettingsState.OK:
                    self._ui.settings_area.ensureWidgetVisible(settings_widget)
                    message = f"Parameter '{parameter_name}' indexing not well-defined."
                    QMessageBox.warning(self, "Bad Parameter Indexing", message)
                    return
        for parameter_name, widgets in self._settings_widgets.items():
            for domain_names, settings_widget in widgets.items():
                setting = self._indexing_settings[parameter_name][domain_names]
                setting.indexing_domain_name = settings_widget.indexing_domain_name()
                setting.picking = settings_widget.picking()
        self.settings_approved.emit()
        self.hide()

    @Slot(QModelIndex, QModelIndex)
    def _load_additional_domain(self, current, previous):
        if not previous.isValid():
            self._set_additional_domain_widgets_enabled(True)
        if not current.isValid():
            self._set_additional_domain_widgets_enabled(False)
            return
        with _disable_domain_updates(self):
            domain_proto = self._additional_domains_model.item_at(current.row())
            self._ui.description_edit.setText(domain_proto.description)
            if domain_proto.expression is not None:
                self._ui.use_expression_radio_button.setChecked(True)
                self._ui.expression_edit.setText(domain_proto.expression)
                self._ui.length_spin_box.setValue(domain_proto.length)
                self._ui.extract_from_combo_box.setCurrentIndex(-1)
                self._switch_additional_domain_widgets_enabled_state(True)
            else:
                self._ui.extract_from_radio_button.setChecked(True)
                self._ui.extract_from_combo_box.setCurrentIndex(-1)
                if domain_proto.extract_from_parameter_name is not None:
                    model = self._ui.extract_from_combo_box.model()
                    for row in range(model.rowCount()):
                        index = model.index(row, 0)
                        parameter_name = index.data(_PARAMETER_NAME_ROLE)
                        if domain_proto.extract_from_parameter_name != parameter_name:
                            continue
                        parameter = index.data(_PARAMETER_ROLE)
                        if domain_proto.extract_from_parameter_domain_names == parameter.domain_names:
                            self._ui.extract_from_combo_box.setCurrentIndex(row)
                            break
                self._ui.expression_edit.clear()
                self._switch_additional_domain_widgets_enabled_state(False)

    @Slot()
    def _reject_and_close(self):
        self.close()

    @Slot(bool)
    def _remove_selected_domains(self, _):
        selection_model = self._ui.additional_domains_list_view.selectionModel()
        if not selection_model.hasSelection():
            return
        rows = [index.row() for index in selection_model.selectedRows()]
        self._additional_domains_model.remove_rows(rows)
        current = selection_model.currentIndex()
        if current.isValid():
            selection_model.select(current, QItemSelectionModel.ClearAndSelect)

    @Slot(list)
    def _remove_available_domains(self, removed_domains):
        """
        Updates available domains.

        Args:
            removed_domains (list of str): domains that were removed
        """
        map(self._available_domains.pop, removed_domains)
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                for domain in removed_domains:
                    widget.remove_domain(domain)

    @Slot(list)
    def _add_available_domains(self, new_domains):
        """
        Updates available domains.

        Args:
            new_domains (list of str): a list of new domain names
        """

        self._available_domains.update(self._additional_domains_model.gather_domains(self._parameters)[0])
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                for domain in new_domains:
                    widget.add_domain(domain)

    @Slot(str, str)
    def _update_after_domain_rename(self, old_name, new_name):
        """
        Propagates changes in domain names to widgets.

        Args:
            old_name (str): domain's previous name
            new_name (str): domain's current name
        """
        self._available_domains[new_name] = self._available_domains.pop(old_name)
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                widget.update_domain_name(old_name, new_name)

    @Slot(str)
    def _update_expression(self, expression):
        """
        Updates the domain's record key expression.

        Args:
            expression (str): new expression
        """
        list_index = self._ui.additional_domains_list_view.currentIndex()
        if not list_index.isValid() or not self._enable_domain_updates:
            return
        item = self._additional_domains_model.item_at(list_index.row())
        item.expression = expression
        records = gdx.GeneratedRecords(item.expression, item.length)
        self._available_domains[item.name] = records
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                widget.update_records(item.name)

    @Slot(int)
    def _update_length(self, length):
        """
        Updates the number of additional domain's records.

        Args:
            length (int): new record count
        """
        list_index = self._ui.additional_domains_list_view.currentIndex()
        if not list_index.isValid() or not self._enable_domain_updates:
            return
        item = self._additional_domains_model.item_at(list_index.row())
        item.length = length
        records = gdx.GeneratedRecords(item.expression, item.length)
        self._available_domains[item.name] = records
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                widget.update_records(item.name)

    @Slot(bool)
    def _use_expression(self, _):
        self._switch_additional_domain_widgets_enabled_state(True)
        list_index = self._ui.additional_domains_list_view.currentIndex()
        if not list_index.isValid():
            return
        item = self._additional_domains_model.item_at(list_index.row())
        item.expression = self._ui.expression_edit.text()
        item.length = self._ui.length_spin_box.value()
        item.extract_from_parameter_name = None
        item.extract_from_parameter_domain_names = None
        records = gdx.GeneratedRecords(item.expression, item.length)
        self._available_domains[item.name] = records
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                widget.update_records(item.name)

    @Slot(bool)
    def _use_extraction(self, _):
        self._switch_additional_domain_widgets_enabled_state(False)
        index = self._ui.extract_from_combo_box.currentIndex()
        self._set_extraction_domain(index)

    @Slot(str)
    def _set_extraction_domain(self, index):
        """
        Sets the domain from which domain's records are extracted.

        Args:
            index (int): choice in the extract from combo box
        """
        if not self._enable_domain_updates or index < 0:
            return
        domain_list_index = self._ui.additional_domains_list_view.currentIndex()
        if not domain_list_index.isValid():
            return
        model = self._ui.extract_from_combo_box.model()
        model_index = model.index(index, 0)
        parameter = model_index.data(_PARAMETER_ROLE)
        parameter_name = model_index.data(_PARAMETER_NAME_ROLE)
        item = self._additional_domains_model.item_at(domain_list_index.row())
        item.expression = None
        item.extract_from_parameter_name = parameter_name
        item.extract_from_parameter_domain_names = parameter.domain_names
        first_value = next(iter(parameter.values))
        value_indexes = [(str(i),) for i in first_value.indexes]
        records = gdx.ExtractedRecords(parameter_name, parameter.domain_names, value_indexes)
        self._available_domains[item.name] = records
        for widgets in self._settings_widgets.values():
            for widget in widgets.values():
                widget.update_records(item.name)

    @Slot(str)
    def _set_domain_description(self, description):
        """
        Sets currently selected additional domain's description.

        Args:
            description (str): description text
        """
        domain_list_index = self._ui.additional_domains_list_view.currentIndex()
        item = self._additional_domains_model.item_at(domain_list_index.row())
        item.description = description

    def closeEvent(self, event):
        """Handles the close event."""
        super().closeEvent(event)
        if self._database_mapping is not None:
            self._database_mapping.connection.close()
        self.settings_rejected.emit()

    def _populate_extract_from_combo(self):
        """Populates the extract from combo box."""
        model = self._ui.extract_from_combo_box.model()
        items = list()
        for parameter_name, by_dimensions in self._parameters.items():
            if not by_dimensions:
                continue
            item = QStandardItem()
            item.setData(next(iter(by_dimensions.values())), _PARAMETER_ROLE)
            item.setData(parameter_name, _PARAMETER_NAME_ROLE)
            if len(by_dimensions) == 1:
                item.setText(parameter_name)
            else:
                for domain_names in by_dimensions:
                    if len(domain_names) == 1:
                        item.setText(f"{parameter_name} ({domain_names[0]})")
                    else:
                        item.setText(f"{parameter_name} {domain_names}")
            items.append(item)
        for item in sorted(items, key=lambda i: i.text()):
            model.appendRow(item)

    def _fix_legacy_indexing_settings(self, indexing_settings):
        """
        Fixes indexing settings that are loaded from 0.5 project file and are missing parameters' domain names.

        Args:
            indexing_settings (dict): indexing settings

        Returns:
            dict: fixed indexing settings
        """
        for parameter_name, by_dimensions in indexing_settings.items():
            if next(iter(by_dimensions))[0] is None:
                setting = next(iter(by_dimensions.values()))
                by_dimensions.clear()
                for domain_names in self._parameters[parameter_name]:
                    by_dimensions[domain_names] = deepcopy(setting)
        return indexing_settings


@contextmanager
def _disable_domain_updates(window):
    """
    A context manager which disables updates on the indexing settings widgets.

    Args:
        window (ParameterIndexSettingsWindow): settings window
    """
    window.set_domain_updated_enabled(False)
    try:
        yield None
    finally:
        window.set_domain_updated_enabled(True)
