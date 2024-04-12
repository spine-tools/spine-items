######################################################################################################################
# Copyright (C) 2017-2022 Spine project consortium
# Copyright Spine Items contributors
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""Contains OptionsWidget class."""
import functools
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QWidget,
    QTableWidget,
    QToolButton,
    QHBoxLayout,
    QStyle,
)
from ..commands import SetConnectorOption


class OptionsWidget(QTableWidget):
    """A widget for handling simple options."""

    options_changed = Signal(dict)
    """Emitted whenever an option in the widget is changed."""
    about_to_undo = Signal(str)
    """Emitted before undo action."""
    load_default_mapping_requested = Signal()
    """Emitted whenever the uses presses the button to Load default mapping."""

    def __init__(self, undo_stack):
        """
        Args:
            undo_stack (QUndoStack): undo stack
        """
        super().__init__()
        self._options = {}
        self._connector = None
        self._undo_stack = undo_stack
        self._undo_enabled = True
        self._current_source_table = None
        self._ui_choices = {str: QLineEdit, list: QComboBox, int: QSpinBox, bool: QCheckBox}
        self._ui_elements = {}
        self._build_ui()
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

    def _clear_ui(self):
        """Clears UI."""
        self._ui_elements.clear()
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def _build_ui(self):
        """Builds ui from specification in dict"""
        self.insertRow(0)
        key_options = sorted(self._options.items(), key=lambda x: list(self._ui_choices).index(x[1]["type"]))
        for column, (key, options) in enumerate(key_options):
            ui_element = self._ui_choices[options["type"]]()
            maximum = options.get("Maximum", None)
            if maximum is not None:
                ui_element.setMaximum(maximum)
            minimum = options.get("Minimum", None)
            if minimum is not None:
                ui_element.setMinimum(minimum)
            special_value_text = options.get("SpecialValueText", None)
            if special_value_text is not None:
                ui_element.setSpecialValueText(special_value_text)
            max_length = options.get("MaxLength", None)
            if max_length is not None:
                ui_element.setMaxLength(max_length)
            bound_arguments = dict(option_key=key, options_widget=self)
            if isinstance(ui_element, QSpinBox):
                handler = functools.partial(_emit_spin_box_option_changed, **bound_arguments)
                ui_element.valueChanged.connect(handler)
            elif isinstance(ui_element, QLineEdit):
                handler = functools.partial(_emit_line_edit_option_changed, **bound_arguments)
                ui_element.textChanged.connect(handler)
                ui_element.setMaximumWidth(40)
            elif isinstance(ui_element, QCheckBox):
                handler = functools.partial(_emit_check_box_option_changed, **bound_arguments)
                ui_element.stateChanged.connect(handler)
            elif isinstance(ui_element, QComboBox):
                ui_element.addItems([str(x) for x in options["Items"]])
                handler = functools.partial(_emit_combo_box_option_changed, **bound_arguments)
                ui_element.currentTextChanged.connect(handler)
            self._ui_elements[key] = ui_element
            # Add to layout:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(3, 3, 3, 3)
            layout.setSpacing(3)
            layout.addWidget(QLabel(options["label"] + ":"))
            layout.addWidget(ui_element)
            self.insertColumn(self.columnCount())
            self.setCellWidget(0, column, widget)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self._adjust_height()

    def _adjust_height(self):
        height = self.verticalHeader().length() + 2
        if self.horizontalScrollBar().isVisible():
            height += self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent)
        self.setMaximumHeight(height)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._adjust_height()

    @property
    def connector(self):
        """The connection manager linked to this options widget."""
        return self._connector

    def set_connector(self, connector):
        """Sets connection manager.

        Args:
            connector (ConnectionManager): connector
        """
        self._connector = connector
        self._options = connector.connection.BASE_OPTIONS.copy()
        self._options.update(connector.connection.OPTIONS)
        connector.current_table_changed.connect(self._fetch_options_from_connector)
        self.options_changed.connect(connector.update_options)
        self._clear_ui()
        self._build_ui()
        self._set_options(self._connector.current_table)
        if hasattr(self._connector.connection, "create_default_mapping"):
            button = QToolButton()
            button.setText("Load default mapping")
            self.insertColumn(self.columnCount())
            self.setCellWidget(0, self.columnCount() - 1, button)
            button.clicked.connect(self.load_default_mapping_requested)

    @property
    def undo_stack(self):
        return self._undo_stack

    @property
    def undo_enabled(self):
        return self._undo_enabled

    @property
    def current_source_table(self):
        return self._current_source_table

    def _set_options(self, source_table, options=None):
        """Sets state of options

        Args:
            source_table (str): name of the source table
            options (dict, optional): Dict with option name as key and value as value (default: {None})
        """
        self._current_source_table = source_table
        if options is None:
            options = {}
        for key, ui_element in self._ui_elements.items():
            default = self._options[key]["default"]
            value = options.get(key, default)
            if value is None:
                continue
            ui_element.blockSignals(True)
            if isinstance(ui_element, QSpinBox):
                ui_element.setValue(value)
            elif isinstance(ui_element, QLineEdit):
                ui_element.setText(value)
            elif isinstance(ui_element, QCheckBox):
                ui_element.setChecked(value)
            elif isinstance(ui_element, QComboBox):
                ui_element.setCurrentText(value)
            ui_element.blockSignals(False)

    def set_option_without_undo(self, source_table, option_key, value):
        self.about_to_undo.emit(source_table)
        ui_element = self._ui_elements[option_key]
        if isinstance(ui_element, QSpinBox):
            current_value = ui_element.value()
            if value == current_value:
                return
            self._undo_enabled = False
            ui_element.setValue(value)
            self._undo_enabled = True
        elif isinstance(ui_element, QLineEdit):
            current_value = ui_element.text()
            if value == current_value:
                return
            self._undo_enabled = False
            ui_element.setText(value)
            self._undo_enabled = True
        elif isinstance(ui_element, QCheckBox):
            current_value = ui_element.isChecked()
            if value == current_value:
                return
            self._undo_enabled = False
            ui_element.setChecked(value)
            self._undo_enabled = True
        elif isinstance(ui_element, QComboBox):
            current_value = ui_element.currentText()
            if value == current_value:
                return
            self._undo_enabled = False
            ui_element.setCurrentText(value)
            self._undo_enabled = True

    @Slot()
    def _fetch_options_from_connector(self):
        """Read options from the connector."""
        table_name = self._connector.current_table
        self._set_options(table_name, self._connector.get_current_options())


def _emit_spin_box_option_changed(i, option_key, options_widget):
    """
    A 'slot' to transform changes in QSpinBox into changes in options.

    Args:
        i (int): spin box value
        option_key (str): option's key
        options_widget (OptionsWidget): options widget
    """
    if options_widget.undo_enabled:
        previous_value = options_widget.connector.get_current_option_value(option_key)
        options_widget.undo_stack.push(
            SetConnectorOption(options_widget.current_source_table, option_key, options_widget, i, previous_value)
        )
    options = {option_key: i}
    options_widget.options_changed.emit(options)


def _emit_line_edit_option_changed(text, option_key, options_widget):
    """
    A 'slot' to transform changes in QLineEdit into changes in options.

    Args:
        text (str): text for undo/redo
        option_key (str): option's key
        options_widget (OptionsWidget): options widget
    """
    if options_widget.undo_enabled:
        previous_value = options_widget.connector.get_current_option_value(option_key)
        options_widget.undo_stack.push(
            SetConnectorOption(options_widget.current_source_table, option_key, options_widget, text, previous_value)
        )
    options = {option_key: text}
    options_widget.options_changed.emit(options)


def _emit_check_box_option_changed(state, option_key, options_widget):
    """
    A 'slot' to transform changes in QCheckBox into changes in options.

    Args:
        state (int): check box value
        option_key (str): option's key
        options_widget (OptionsWidget): options widget
    """
    checked = state == Qt.CheckState.Checked.value
    if options_widget.undo_enabled:
        previous_value = options_widget.connector.get_current_option_value(option_key)
        options_widget.undo_stack.push(
            SetConnectorOption(options_widget.current_source_table, option_key, options_widget, checked, previous_value)
        )
    options = {option_key: checked}
    options_widget.options_changed.emit(options)


def _emit_combo_box_option_changed(text, option_key, options_widget):
    """
    A 'slot' to transform changes in QComboBox into changes in options.

    Args:
        text (str): text for undo/redo
        option_key (str): option's key
        options_widget (OptionsWidget): options widget
    """
    if options_widget.undo_enabled:
        previous_value = options_widget.connector.get_current_option_value(option_key)
        options_widget.undo_stack.push(
            SetConnectorOption(options_widget.current_source_table, option_key, options_widget, text, previous_value)
        )
    options = {option_key: text}
    options_widget.options_changed.emit(options)
