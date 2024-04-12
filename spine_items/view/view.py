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

"""Module for view class."""
import os
from PySide6.QtCore import Qt, Slot, Signal, QObject, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel, QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextBrowser, QLineEdit, QLabel
from sqlalchemy.engine.url import URL, make_url
from spinetoolbox.project_item.project_item import ProjectItem
from spinetoolbox.plotting import plot_db_mngr_items, PlottingError
from spinetoolbox.helpers import busy_effect
from spinetoolbox.fetch_parent import FetchParent
from spinetoolbox.spine_db_editor.widgets.spine_db_editor import SpineDBEditor
from spinetoolbox.widgets.notification import Notification
from .item_info import ItemInfo
from .executable_item import ExecutableItem
from .commands import PinOrUnpinDBValuesCommand


class View(ProjectItem):
    """View's main class."""

    def __init__(self, name, description, x, y, toolbox, project, pinned_values=None):
        """
        Args:
            name (str): Object name
            description (str): Object description
            x (float): Initial X coordinate of item icon
            y (float): Initial Y coordinate of item icon
            project (SpineToolboxProject): the project this item belongs to
            pinned_values (dict): pinned values by name
        """
        super().__init__(name, description, x, y, project)
        self._toolbox = toolbox
        self._references = dict()
        self._pinned_values = pinned_values if pinned_values is not None else dict()
        self.pinned_value_model = QStandardItemModel()
        self.reference_model = QStandardItemModel()
        self._spine_ref_icon = QIcon(QPixmap(":/icons/Spine_db_ref_icon.png"))
        self._data_fetchers = []
        self._fetched_parameter_values = []
        self._pin_to_plot = None
        self.populate_pinned_values_list()

    @staticmethod
    def item_type():
        """See base class."""
        return ItemInfo.item_type()

    @property
    def executable_class(self):
        return ExecutableItem

    @property
    def pinned_values(self):
        return self._pinned_values

    def make_signal_handler_dict(self):
        """Returns a dictionary of all shared signals and their handlers.
        This is to enable simpler connecting and disconnecting."""
        s = super().make_signal_handler_dict()
        s[self._properties_ui.pushButton_pin_values.clicked] = self.pin_values
        s[self._properties_ui.pushButton_open_editor.clicked] = self.open_editor
        s[self._properties_ui.pushButton_plot_pinned.clicked] = self.plot_selected_pinned_values
        return s

    def restore_selections(self):
        """Restore selections into shared widgets when this project item is selected."""
        self._properties_ui.treeView_references.setModel(self.reference_model)
        self._properties_ui.treeView_pinned_values.setModel(self.pinned_value_model)
        self._update_buttons_enabled()

    def save_selections(self):
        """Save selections in shared widgets for this project item into instance variables."""
        self._properties_ui.treeView_references.setModel(None)
        self._properties_ui.treeView_pinned_values.setModel(None)

    @Slot(bool)
    def open_editor(self, checked=False):
        """Opens selected db in the Spine database editor."""
        indexes = self._selected_reference_indexes()
        db_url_codenames = self._db_url_codenames(indexes)
        if not db_url_codenames:
            return
        self._toolbox.db_mngr.open_db_editor(db_url_codenames, reuse_existing_editor=True)

    @Slot(bool)
    def pin_values(self, checked=False):
        """Opens selected db in the Spine database editor to pin values."""
        indexes = self._selected_reference_indexes()
        db_url_codenames = self._db_url_codenames(indexes)
        if not db_url_codenames:
            return
        db_editor = SpineDBEditor(self._toolbox.db_mngr, db_url_codenames)
        dialog = _PinValuesDialog(self, db_editor)
        db_editor.pinned_values_updated.connect(dialog.update_pinned_values)
        dialog.data_committed.connect(self._pin_db_values)
        db_editor.show()
        dialog.show()

    def selected_references(self):
        return self._properties_ui.treeView_references.selectedIndexes()

    def selected_pinned_values(self):
        return self._properties_ui.treeView_pinned_values.selectedIndexes()

    def reference_resource_label_from_url(self, url):
        for label, (ref_url, _) in self._references.items():
            if str(ref_url) == str(url):
                return label
        self._logger.msg_error.emit(f"<b>{self.name}</b>: Can't find any resource having url {url}.")

    @Slot(str, list)
    def _pin_db_values(self, name, values):
        self._toolbox.undo_stack.push(
            PinOrUnpinDBValuesCommand(self.name, {name: values}, {name: self._pinned_values.get(name)}, self._project)
        )
        self._logger.msg.emit(f"<b>{self.name}</b>: Successfully added pin '{name}'")

    def unpin_selected_pinned_values(self):
        names = [index.data() for index in self._properties_ui.treeView_pinned_values.selectedIndexes()]
        self._toolbox.undo_stack.push(
            PinOrUnpinDBValuesCommand(
                self.name,
                {name: None for name in names},
                {name: self._pinned_values.get(name) for name in names},
                self._project,
            )
        )

    def renamed_selected_pinned_value(self):
        index = self._properties_ui.treeView_pinned_values.selectedIndexes()[0]
        old_name = index.data()
        new_name, ok = _RenamePinDialog.get_new_name(self, old_name, self._toolbox)
        if not ok:
            return
        values = self._pinned_values.get(old_name)
        self._toolbox.undo_stack.push(
            PinOrUnpinDBValuesCommand(
                self.name, {old_name: None, new_name: values}, {old_name: values, new_name: None}, self._project
            )
        )

    def do_pin_db_values(self, values_by_name):
        for name, values in values_by_name.items():
            self._pinned_values[name] = values
            self.populate_pinned_values_list()

    @Slot(bool)
    def plot_selected_pinned_values(self, _checked=False):
        self._properties_ui.pushButton_plot_pinned.setEnabled(False)
        for index in self._selected_pinned_value_indexes():
            self._plot_pinned_value(index)

    @busy_effect
    def _make_plot_widget(self, index):
        self._pin_to_plot = index.data()
        pinned_values = self._pinned_values[index.data()]
        pks_by_resource_label = {}
        for value in pinned_values:
            resource_label, pk = value
            pks_by_resource_label.setdefault(resource_label, list()).append(pk)
        fetch_id_base = 0
        for resource_label, pks in pks_by_resource_label.items():
            url_provider_tuple = self._references.get(resource_label)
            if url_provider_tuple is None:
                self._logger.msg_error.emit(f"<b>{self.name}</b>: Can't find any resource with label {resource_label}")
                continue
            url = url_provider_tuple[0]
            db_map = self._toolbox.db_mngr.get_db_map(url, self._toolbox)
            self._data_fetchers += [
                _DatabaseFetch(fetch_id_base + i, self, self._toolbox.db_mngr, db_map, **pk) for i, pk in enumerate(pks)
            ]
            fetch_id_base += len(pks)
        for fetcher in self._data_fetchers:
            fetcher.start()

    def add_to_plot(self, fetch_id, db_map, parameter_record):
        """Adds parameter value to plot widget.

        Args:
            fetch_id (Any): id given to database fetcher
            db_map (DatabaseMapping): database map
            parameter_record (dict): parameter value's database data
        """
        if not self._data_fetchers:
            return
        if not self._fetched_parameter_values:
            self._fetched_parameter_values = len(self._data_fetchers) * [None]
        self._fetched_parameter_values[fetch_id] = (db_map, parameter_record)
        self._plot_if_all_fetched()

    def failed_to_plot(self, fetch_id, db_map, conditions):
        self._logger.msg_warning.emit(
            f"<b>{self.name}</b>: "
            f"Couldn't find any values having {_pk_to_ul(conditions)} in <b>{db_map.codename}</b>"
        )
        if not self._fetched_parameter_values:
            self._fetched_parameter_values = len(self._data_fetchers) * [None]
        self._fetched_parameter_values[fetch_id] = "skip"
        self._plot_if_all_fetched()

    def _plot_if_all_fetched(self):
        """Plots available data if all fetching has been finished."""
        if any(v is None for v in self._fetched_parameter_values):
            return
        existing_fetched_parameter_values = [v for v in self._fetched_parameter_values if v != "skip"]
        if any(v != "skip" for v in self._fetched_parameter_values):
            plot_db_maps, plot_items = zip(*existing_fetched_parameter_values)
            try:
                plot_widget = plot_db_mngr_items(plot_items, plot_db_maps)
            except PlottingError as error:
                self._logger.msg_error.emit(str(error))
                return
            plot_widget.use_as_window(self._toolbox, self.name + " / " + self._pin_to_plot)
            plot_widget.show()
        else:
            self._logger.msg_warning.emit("Nothing to plot.")
        self._finalize_fetching()

    def _finalize_fetching(self):
        self._fetched_parameter_values.clear()
        for fetcher in self._data_fetchers:
            fetcher.set_obsolete(True)
            fetcher.deleteLater()
        self._data_fetchers.clear()
        self._properties_ui.pushButton_plot_pinned.setEnabled(True)

    def copy_selected_pinned_value_plot_data(self):
        index = self._properties_ui.treeView_pinned_values.selectionModel().currentIndex()
        plot_widget = self._make_plot_widget(index)
        plot_widget.copy_plot_data()

    def _plot_pinned_value(self, index):
        self._make_plot_widget(index)

    def populate_pinned_values_list(self):
        """Populates pinned values list."""
        self.pinned_value_model.clear()
        self.pinned_value_model.setHorizontalHeaderItem(0, QStandardItem("Pinned values"))  # Add header
        for key, values in self._pinned_values.items():
            if not values:
                continue
            qitem = QStandardItem(key)
            qitem.setFlags(~Qt.ItemIsEditable)
            tool_tip = _format_pinned_values(values)
            qitem.setData(tool_tip, Qt.ItemDataRole.ToolTipRole)
            self.pinned_value_model.appendRow(qitem)

    def _update_buttons_enabled(self):
        self._properties_ui.pushButton_open_editor.setEnabled(bool(self._references))
        self._properties_ui.pushButton_pin_values.setEnabled(bool(self._references))
        self._properties_ui.pushButton_plot_pinned.setEnabled(bool(self._references))

    def populate_reference_list(self):
        """Populates reference list."""
        self._update_buttons_enabled()
        self.reference_model.clear()
        self.reference_model.setHorizontalHeaderItem(0, QStandardItem("Available resources"))  # Add header
        for db in sorted(self._references, reverse=True):
            qitem = QStandardItem(db)
            qitem.setFlags(~Qt.ItemIsEditable)
            qitem.setData(self._spine_ref_icon, Qt.ItemDataRole.DecorationRole)
            self.reference_model.appendRow(qitem)

    def upstream_resources_updated(self, resources):
        """See base class."""
        self._references.clear()
        for resource in resources:
            if resource.type_ == "database":
                url = make_url(resource.url)
                self._references[resource.label] = (url, resource.provider_name)
            elif resource.type_ == "file":
                filepath = resource.path
                if os.path.splitext(filepath)[1] == ".sqlite":
                    url = URL("sqlite", database=filepath)
                    self._references[resource.label] = (url, resource.provider_name)
        self.populate_reference_list()

    def replace_resources_from_upstream(self, old, new):
        """See base class."""
        for old_resource, new_resource in zip(old, new):
            if old_resource.type_ == "database" and new_resource.type_ == "database":
                old_label = old_resource.label
                new_label = new_resource.label
            elif old_resource.type_ == "file":
                if (
                    os.path.splitext(old_resource.path)[1] == ".sqlite"
                    and os.path.splitext(new_resource.path)[1] == ".sqlite"
                ):
                    old_label = old_resource.label
                    new_label = new_resource.label
                else:
                    continue
            else:
                continue
            self._references[new_label] = self._references.pop(old_label)
        self.populate_reference_list()

    def _selected_reference_indexes(self):
        """Returns selected references indexes."""
        selection_model = self._properties_ui.treeView_references.selectionModel()
        if not selection_model.hasSelection():
            self._properties_ui.treeView_references.selectAll()
        return self._properties_ui.treeView_references.selectionModel().selectedRows()

    def _selected_pinned_value_indexes(self):
        """Returns selected references indexes."""
        selection_model = self._properties_ui.treeView_pinned_values.selectionModel()
        if not selection_model.hasSelection():
            self._properties_ui.treeView_pinned_values.selectAll()
        return self._properties_ui.treeView_pinned_values.selectionModel().selectedRows()

    def _db_url_codenames(self, indexes):
        """Returns a dict mapping url to provider's name for given indexes in the reference model."""
        return dict(self._references[index.data(Qt.ItemDataRole.DisplayRole)] for index in indexes)

    def notify_destination(self, source_item):
        """See base class."""
        if source_item.item_type() == "Tool":
            self._logger.msg.emit(
                "Link established. You can visualize the output from Tool "
                f"<b>{source_item.name}</b> in View <b>{self.name}</b>."
            )
        elif source_item.item_type() == "Data Store":
            self._logger.msg.emit(
                "Link established. You can visualize Data Store "
                f"<b>{source_item.name}</b> in View <b>{self.name}</b>."
            )
        else:
            super().notify_destination(source_item)

    def item_dict(self):
        d = super().item_dict()
        d["pinned_values"] = {name: values for name, values in self._pinned_values.items() if values is not None}
        return d

    @staticmethod
    def from_dict(name, item_dict, toolbox, project):
        description, x, y = ProjectItem.parse_item_dict(item_dict)
        pinned_values = item_dict.get("pinned_values", dict())
        for values in pinned_values.values():
            for value in values:
                pks = value[1]
                for pk_key, pk in pks.items():
                    if isinstance(pk, list):
                        pks[pk_key] = tuple(pk)
        return View(name, description, x, y, toolbox, project, pinned_values=pinned_values)


def _pk_to_ul(pk):
    return "".join(["<ul>"] + [f"<li><b>{k}</b>: {v}</li>" for k, v in pk.items() if v] + ["</ul>"])


def _format_pinned_values(values):
    head = """
        <head>
        <style>
            table, th, td {
              border: 1px solid black;
              border-collapse: collapse;
              padding: 5px;
            }
        </style>
        </head>
    """
    tables = []
    for label, pk in values:
        header = [*pk, "source"]
        data = [*pk.values(), label]
        table = "<p><table>"
        table += "<tr>" + "".join([f"<th>{h}</th>" for h in header]) + "</tr>"
        table += "<tr>" + "".join([f"<td>{d}</td>" for d in data]) + "</tr>"
        table += "</table></p>"
        tables.append(table)
    table = "".join(tables)
    return f"<html>{head}<body>{table}</body></html>"


class _PinDialogMixin:
    @property
    def pin_name(self):
        return self._line_edit.text()

    def _check_name_valid(self):
        if self.pin_name in self._view.pinned_values:
            Notification(
                self,
                f"A pin called {self.pin_name} already exists, please select a different name.",
                corner=Qt.BottomRightCorner,
            ).show()
            return False
        return True


class _PinValuesDialog(_PinDialogMixin, QDialog):
    data_committed = Signal(str, list)

    def __init__(self, view, db_editor):
        super().__init__(parent=db_editor)
        self.setWindowTitle("Pin values")
        self._view = view
        self._db_editor = db_editor
        self._pinned_values = []
        outer_layout = QVBoxLayout(self)
        button_box = QDialogButtonBox(self)
        button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_button.setEnabled(False)
        self._line_edit = QLineEdit()
        self._line_edit.setPlaceholderText("Type a name for the pin here...")
        self._text_edit = QTextBrowser()
        self._text_edit.setPlaceholderText(
            "Select parameter values that you want to pin in the Spine DB Editor underneath "
            "(they will be shown here)..."
        )
        outer_layout.addWidget(self._line_edit)
        outer_layout.addWidget(self._text_edit)
        outer_layout.addWidget(button_box)
        button_box.rejected.connect(self.close)
        button_box.rejected.connect(db_editor.close)
        button_box.accepted.connect(self.accept)
        self._line_edit.textEdited.connect(self._update_ok_button_enabled)
        self.setAttribute(Qt.WA_DeleteOnClose)

    @Slot(str)
    def _update_ok_button_enabled(self, _text=None):
        self._ok_button.setEnabled(bool(self._pinned_values) and bool(self.pin_name))

    @Slot(list)
    def update_pinned_values(self, values):
        self._pinned_values = [(self._view.reference_resource_label_from_url(url), pk) for url, pk in values]
        html = _format_pinned_values(self._pinned_values)
        self._text_edit.setHtml(html)
        label = QLabel(html)
        width = label.sizeHint().width()
        doc_margin = self._text_edit.document().documentMargin()
        width += 2 * doc_margin
        self._text_edit.setMinimumWidth(width)
        self._update_ok_button_enabled()

    def accept(self):
        if not self._check_name_valid():
            return
        super().accept()
        self._db_editor.close()
        self.data_committed.emit(self.pin_name, self._pinned_values)


class _RenamePinDialog(_PinDialogMixin, QDialog):
    def __init__(self, view, old_name, parent):
        super().__init__(parent=parent)
        self._view = view
        self.new_name = ""
        self.setWindowTitle("Rename pin")
        outer_layout = QVBoxLayout(self)
        button_box = QDialogButtonBox(self)
        button_box.setStandardButtons(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._line_edit = QLineEdit()
        self._line_edit.setText(old_name)
        outer_layout.addWidget(QLabel("New name:"))
        outer_layout.addWidget(self._line_edit)
        outer_layout.addWidget(button_box)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.accept)
        self._line_edit.textEdited.connect(self._update_ok_button_enabled)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._line_edit.setFocus()

    @Slot(str)
    def _update_ok_button_enabled(self, _text=None):
        self._ok_button.setEnabled(bool(self.pin_name))

    def accept(self):
        if not self._check_name_valid():
            return
        super().accept()
        self.new_name = self.pin_name

    @classmethod
    def get_new_name(cls, view, old_name, parent):
        dialog = cls(view, old_name, parent)
        result = dialog.exec()
        return dialog.new_name, result == QDialog.DialogCode.Accepted


class _DatabaseFetch(FetchParent):
    """A data collector that fetches parameter values from database manager."""

    class _Signals(QObject):
        fetched = Signal()

        def __init__(self, database_fetch):
            super().__init__()
            self._database_fetch = database_fetch
            self.fetched.connect(self._finish_fetch)

        @Slot()
        def _finish_fetch(self):
            self._database_fetch.finished()

    def __init__(self, id_, view, db_mngr, db_map, **conditions):
        """
        Args:
            id_ (Any): fetch id
            view (View): View item
            db_mngr (SpineDBManager): database manager
            db_map (DiffDatabaseMapping): database map
            **conditions: filter conditions
        """
        super().__init__()
        self._id = id_
        self._view = view
        self._db_mngr = db_mngr
        self._db_map = db_map
        self._conditions = conditions
        self._value_fetched = False
        self._signals = None

    def start(self):
        """Starts fetching the parameter value."""
        cached_items = self._db_mngr.get_items(self._db_map, self.fetch_item_type)
        cached_match = self._find_one_or_none(cached_items)
        if cached_match is not None:
            self._value_fetched = True
            self._view.add_to_plot(self._id, self._db_map, cached_match)
        else:
            self._signals = _DatabaseFetch._Signals(self)
            self._try_fetching()

    def _try_fetching(self):
        """Repeatedly tries to fetch more data until there is nothing to fetch."""
        if self._db_mngr.can_fetch_more(self._db_map, self):
            self._db_mngr.fetch_more(self._db_map, self)
            QTimer.singleShot(50, self._try_fetching)

    @property
    def fetch_item_type(self):
        """See base class."""
        return "parameter_value"

    def accepts_item(self, item, db_map):
        """See base class."""
        return all(item[key] == value for key, value in self._conditions.items())

    def set_fetched(self, fetched):
        """See base class."""
        super().set_fetched(fetched)
        if fetched and self._signals is not None:
            self._signals.fetched.emit()

    def handle_items_added(self, db_map_data):
        """A callback that stores relevant parameter values.

        Args:
            db_map_data (dict): parameter value data
        """
        data = db_map_data.get(self._db_map)
        if data is None:
            return
        match = self._find_one_or_none(data)
        if match is not None:
            self._value_fetched = True
            self._view.add_to_plot(self._id, self._db_map, match)

    def _find_one_or_none(self, parameter_value_items):
        """Searches parameter value from given items and returns the match.

        Args:
            parameter_value_items (list of dict): parameter value items

        Returns:
            dict: match or None if not found
        """
        for parameter_value in parameter_value_items:
            match = True
            for key, filter_value in self._conditions.items():
                if parameter_value[key] != filter_value:
                    match = False
                    break
            if match:
                return parameter_value
        return None

    def finished(self):
        """Reports plotting failures to View."""
        if not self._value_fetched:
            self._view.failed_to_plot(self._id, self._db_map, self._conditions)
        self._signals.deleteLater()
        self._signals = None
