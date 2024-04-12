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

"""Contains ImportSources widget and SourceDataTableMenu."""
import pickle
from operator import itemgetter
from PySide6.QtCore import (
    QItemSelectionModel,
    QModelIndex,
    QObject,
    QPoint,
    Qt,
    Signal,
    Slot,
    QMimeData,
    QItemSelection,
)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from spinetoolbox.helpers import CharIconEngine
from spinedb_api.import_mapping.import_mapping_compat import unparse_named_mapping_spec
from spinedb_api.import_mapping.type_conversion import (
    value_to_convert_spec,
    IntegerSequenceDateTimeConvertSpec,
    StringConvertSpec,
)
from spinedb_api.exception import InvalidMappingComponent
from .custom_menus import SourceListMenu, SourceDataTableMenu
from .mime_types import MAPPING_LIST_MIME_TYPE, TABLE_OPTIONS_MIME_TYPE
from .options_widget import OptionsWidget
from .table_view_with_button_header import TYPE_TO_FONT_AWESOME_ICON
from ..commands import PasteMappings, PasteOptions, RestoreMappingsFromDict, DeleteMapping, SetColumnDefaultType
from ..mvcmodels.mappings_model import Role
from ..mvcmodels.source_data_table_model import SourceDataTableModel


_EMPTY_DEFAULT_COLUMN_TYPE = "undefined"


class ImportSources(QObject):
    """
    Loads and controls the 'Sources' and 'Source data' part of the window.
    Loads the 'Mappings' part of the window as the user changes the source table.
    """

    preview_data_updated = Signal(int)

    def __init__(self, mappings_model, ui, undo_stack, parent):
        """
        Args:
            mappings_model (MappingsModel): mappings model
            ui (Any): import editor window's UI
            undo_stack (QUndoStack): undo stack
            parent (ImportEditorWindow): import editor window
        """
        super().__init__(parent)
        self._mappings_model = mappings_model
        self._undo_stack = undo_stack
        self._ui = ui
        self._stored_source_list_row = 0

        # state
        self._connector = None
        self._source_data_model = SourceDataTableModel(self)
        # create ui
        self._ui.source_data_table.setModel(self._source_data_model)
        self._ui.source_data_table.set_undo_stack(self._undo_stack, self._select_table_for_undo)
        self._ui_source_data_table_menu = SourceDataTableMenu(self._mappings_model, self._ui)
        self._ui_options_widget = OptionsWidget(self._undo_stack)
        self._ui_options_widget.setEnabled(False)
        self._ui.verticalLayout_source_options.addWidget(self._ui_options_widget)
        self._ui.source_data_table.verticalHeader().display_all = False
        self._fill_default_column_type_combo_box_items()
        # connect signals
        self._mappings_model.modelAboutToBeReset.connect(self._store_source_list_current_index)
        self._mappings_model.modelReset.connect(self._restore_source_list_current_index)
        self._mappings_model.dataChanged.connect(self._handle_mapping_data_changed)
        self._mappings_model.row_or_column_type_recommended.connect(self._source_data_model.set_type)
        self._mappings_model.multi_column_type_recommended.connect(self._source_data_model.set_all_column_types)
        self._ui_options_widget.options_changed.connect(lambda _: self._clear_source_data_model())
        self._ui_options_widget.about_to_undo.connect(self._select_table_for_undo)
        self._ui_options_widget.load_default_mapping_requested.connect(self._load_default_mapping)
        self._ui.source_list.customContextMenuRequested.connect(self.show_source_list_context_menu)
        self._ui.source_list.selectionModel().currentChanged.connect(self._change_selected_table)
        self._ui.mapping_list.selectionModel().currentChanged.connect(self._change_selected_mapping)
        self._ui.source_data_table.customContextMenuRequested.connect(self._ui_source_data_table_menu.request_menu)
        self._ui.default_column_type_combo_box.currentTextChanged.connect(self._set_default_column_type)

        self._source_data_model.mapping_data_changed.connect(self._update_display_row_types)
        self._source_data_model.column_types_updated.connect(self._new_column_types)
        self._source_data_model.row_types_updated.connect(self._new_row_types)
        self._source_data_model.polish_mapping_requested.connect(self._polish_mappings_in_list)

    @Slot(QModelIndex, QModelIndex, list)
    def _handle_mapping_data_changed(self, top_left, bottom_right, roles):
        self._update_source_table_colors(top_left, bottom_right, roles)
        table_index = self._ui.source_list.selectionModel().currentIndex()
        if not table_index.isValid() or table_index.row() == 0:
            return
        header = self._source_data_model.header
        for list_row in range(self._mappings_model.rowCount(table_index)):
            list_index = self._mappings_model.index(list_row, 0, table_index)
            msg = self._mappings_model.check_validity_of_columns(list_index, header)
            if msg:
                self.parent().show_error(msg)
                return

    def set_connector(self, connector, mapping):
        """Sets connector.

        Args:
            connector (ConnectionManager): connector
            mapping (dict)
        """
        self._ui.source_list.selectionModel().clearCurrentIndex()
        self._connector = connector
        self._connector.connection_ready.connect(self.request_new_tables_from_connector)
        self._connector.data_ready.connect(self._update_source_data)
        self._connector.tables_ready.connect(self.update_tables)
        self._connector.default_mapping_ready.connect(self._set_default_mapping)
        self._ui_options_widget.set_connector(self._connector)
        self._source_data_model.more_data_needed.connect(self.fetch_more_data, Qt.UniqueConnection)
        self.restore_connectors(mapping)

    def _fill_default_column_type_combo_box_items(self):
        """Adds items to default column type combo box."""
        combo_box = self._ui.default_column_type_combo_box
        combo_box.addItem(_EMPTY_DEFAULT_COLUMN_TYPE)
        for data_type_label, icon_character in sorted(TYPE_TO_FONT_AWESOME_ICON.items(), key=itemgetter(0)):
            if data_type_label == IntegerSequenceDateTimeConvertSpec.DISPLAY_NAME:
                # Skipping the more complicated conversion for now.
                continue
            engine = CharIconEngine(icon_character, 0)
            icon = QIcon(engine.pixmap())
            self._ui.default_column_type_combo_box.addItem(icon, data_type_label)
        self._ui.default_column_type_combo_box.setCurrentText(_EMPTY_DEFAULT_COLUMN_TYPE)

    @Slot()
    def _polish_mappings_in_list(self):
        """Polishes mappings in mapping list."""
        table_index = self._ui.source_list.selectionModel().currentIndex()
        if not table_index.isValid() or table_index.row() == 0:
            return
        header = self._source_data_model.header
        for list_row in range(self._mappings_model.rowCount(table_index)):
            list_index = self._mappings_model.index(list_row, 0, table_index)
            try:
                self._mappings_model.polish_mapping(list_index, header)
            except InvalidMappingComponent as error:
                self.parent().show_error(str(error))

    @Slot(str)
    def _select_table_for_undo(self, table_name):
        """Selects source table to load correct values to different widgets.

        Args:
            table_name (str): table name
        """
        if table_name == self._connector.current_table:
            return
        for row in range(self._mappings_model.rowCount()):
            table_index = self._mappings_model.index(row, 0)
            if table_index.data() == table_name:
                self._ui.source_list.selectionModel().setCurrentIndex(table_index, QItemSelectionModel.ClearAndSelect)
                break

    @Slot()
    def _load_default_mapping(self):
        self._connector.request_default_mapping()

    @Slot(dict)
    def _set_default_mapping(self, mapping):
        self._undo_stack.push(RestoreMappingsFromDict(self, self._mappings_model, mapping))

    @Slot()
    def request_new_tables_from_connector(self):
        """
        Requests new tables data from connector
        """
        self._connector.request_tables()

    @Slot(QModelIndex, QModelIndex)
    def _change_selected_table(self, current, _previous):
        """
        Sets selected table and requests data from connector

        Args:
            current (QModelIndex): current index
            _previous (QModelIndex): previous index
        """
        if self._connector is None:
            self._ui_options_widget.setEnabled(False)
            return
        if not current.isValid():
            table_name = ""
            self._ui_options_widget.setEnabled(False)
            self._ui.default_column_type_combo_box.setEnabled(False)
        else:
            table_item = self._mappings_model.data(current, Role.ITEM)
            table_name = table_item.name if table_item.real else ""
            self._ui_options_widget.setEnabled(bool(table_name))
            self._ui.default_column_type_combo_box.setEnabled(bool(table_name))
            if table_name:
                self._reset_default_column_type(table_name)
        self._connector.set_table(table_name)
        self._clear_source_data_model()

    @Slot(QModelIndex, QModelIndex)
    def _change_selected_mapping(self, current, previous):
        """Updates source table according to newly selected mapping from mapping list.

        Args:
            current (QModelIndex): current mapping
            previous (QModelIndex): previous mapping
        """
        self._source_data_model.set_mapping_list_index(current)

    @Slot(str)
    def _set_default_column_type(self, selected_label):
        """Pushes a set default column type command to undo stack.

        Args:
            selected_label (str): new default column data type
        """
        table_name = self._connector.current_table
        current_type = self._connector.table_default_column_type.get(table_name, _EMPTY_DEFAULT_COLUMN_TYPE)
        self._undo_stack.push(SetColumnDefaultType(self, table_name, selected_label, current_type))

    def change_default_column_type(self, table_name, column_type):
        """Sets default column type.

        Args:
            table_name (str): table name
            column_type (str): new default column type
        """
        self._select_table_for_undo(table_name)
        if column_type != _EMPTY_DEFAULT_COLUMN_TYPE:
            self._connector.update_table_default_column_type({table_name: value_to_convert_spec(column_type)})
        else:
            self._connector.clear_table_default_column_type(table_name)
        if column_type != self._ui.default_column_type_combo_box.currentText():
            self._reset_default_column_type(table_name)

    def _reset_default_column_type(self, table_name):
        """Updates the default column type combo box.

        Args:
            table_name (str): current_table_name
        """
        converter = self._connector.table_default_column_type.get(table_name)
        column_type = converter.DISPLAY_NAME if converter is not None else _EMPTY_DEFAULT_COLUMN_TYPE
        self._ui.default_column_type_combo_box.currentTextChanged.disconnect(self._set_default_column_type)
        self._ui.default_column_type_combo_box.setCurrentText(column_type)
        self._ui.default_column_type_combo_box.currentTextChanged.connect(self._set_default_column_type)

    def _update_source_table_colors(self, top_left, bottom_right, roles):
        """Notifies source table model that colors have changed.

        Args:
            top_left (QModelIndex): changed data's top left index in mappings model
            bottom_right (QModelIndex): changed data's bottom right index in mappings model
        """
        mapping_list_index = self._ui.mapping_list.selectionModel().currentIndex()
        if not mapping_list_index.isValid() or (
            (
                QItemSelection(top_left, bottom_right).contains(mapping_list_index)
                and Role.FLATTENED_MAPPINGS not in roles
            )
            and top_left.parent() != mapping_list_index
        ):
            return
        self._source_data_model.handle_mapping_data_changed()

    @Slot(int, int)
    def fetch_more_data(self, max_rows, start):
        self._connector.request_data(max_rows=max_rows, start=start)

    def _select_table_row(self, row):
        selection_model = self._ui.source_list.selectionModel()
        index = self._mappings_model.index(row, 0)
        selection_model.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    @Slot(dict)
    def update_tables(self, tables):
        """Updates list of tables.

        Args:
            tables (dict): updated source tables
        """
        if self.parent().is_file_less():
            self._mappings_model.add_empty_row()
            return
        selection_model = self._ui.source_list.selectionModel()
        current_row = selection_model.currentIndex().row()
        self._mappings_model.cross_check_source_table_names(set(tables))
        self._mappings_model.remove_tables_not_in_source_and_specification()
        table_names = set(self._mappings_model.real_table_names())
        for t_name, t_mapping in tables.items():
            if t_name not in table_names:
                self._mappings_model.append_new_table_with_mapping(t_name, t_mapping)
        # reselect current table if existing otherwise select first table
        selection_model.setCurrentIndex(QModelIndex(), QItemSelectionModel.ClearAndSelect)
        if current_row >= 0:
            self._select_table_row(min(current_row, self._mappings_model.rowCount() - 1))
        else:
            self._select_table_row(1 if self._mappings_model.rowCount() > 1 else 0)

    @Slot(list, list)
    def _update_source_data(self, data, header):
        if not data and not header:
            return
        if data:
            try:
                data = _sanitize_data(data, header)
            except RuntimeError as error:
                self.parent().show_error(str(error))
                return
            self._source_data_model.append_rows(data)
            if not header:
                header = list(range(1, len(data[0]) + 1))
        # Set header data before resetting model because the header needs to be there for some slots...
        self._source_data_model.set_horizontal_header_labels(header)
        table_name = self._connector.current_table
        types = self._connector.table_types.get(table_name, {})
        row_types = self._connector.table_row_types.get(table_name, {})
        default_column_type = None
        for col in range(len(header)):
            col_type = types.get(col)
            if col_type is None:
                if default_column_type is None:
                    default_column_type = self._connector.table_default_column_type.get(table_name)
                    if default_column_type is None:
                        default_column_type = StringConvertSpec()
                col_type = default_column_type.DISPLAY_NAME
            self._source_data_model.set_type(
                col, value_to_convert_spec(col_type), orientation=Qt.Orientation.Horizontal
            )
        for row, row_type in row_types.items():
            self._source_data_model.set_type(row, value_to_convert_spec(row_type), orientation=Qt.Orientation.Vertical)
        self.preview_data_updated.emit(self._source_data_model.columnCount())

    def _clear_source_data_model(self):
        self._source_data_model.clear(infinite=self.parent().is_file_less())
        self.preview_data_updated.emit(0)

    def restore_connectors(self, mappings_dict):
        """Restores connectors.

        Args:
            mappings_dict (dict): serialized data
        """
        table_types = {
            tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
            for tn, cols in mappings_dict.get("table_types", {}).items()
        }
        table_default_column_type = {
            tn: value_to_convert_spec(spec) for tn, spec in mappings_dict.get("table_default_column_type", {}).items()
        }
        table_row_types = {
            tn: {int(row): value_to_convert_spec(spec) for row, spec in rows.items()}
            for tn, rows in mappings_dict.get("table_row_types", {}).items()
        }
        self._connector.set_table_options(mappings_dict.get("table_options", {}))
        self._connector.set_table_types(table_types)
        self._connector.update_table_default_column_type(table_default_column_type)
        self._connector.set_table_row_types(table_row_types)

    @Slot()
    def _store_source_list_current_index(self):
        """Stores source table list's current index."""
        self._stored_source_list_row = self._ui.source_list.selectionModel().currentIndex().row()

    @Slot()
    def _restore_source_list_current_index(self):
        """Restores source table list's current index."""
        row = min(self._stored_source_list_row, self._mappings_model.rowCount() - 1)
        current = self._mappings_model.index(row, 0)
        self._ui.source_list.selectionModel().setCurrentIndex(current, QItemSelectionModel.ClearAndSelect)

    def store_connectors(self):
        """Returns a dictionary with type of connector and connector options for tables.

        Returns:
            dict: stored connectors
        """
        table_names = set(self._mappings_model.real_table_names())
        table_types = {
            tn: {col: spec.to_json_value() for col, spec in cols.items()}
            for tn, cols in self._connector.table_types.items()
            if cols
            if tn in table_names
        }
        table_default_column_type = {
            tn: column_type.to_json_value()
            for tn, column_type in self._connector.table_default_column_type.items()
            if tn in table_names
        }
        table_row_types = {
            tn: {col: spec.to_json_value() for col, spec in cols.items()}
            for tn, cols in self._connector.table_row_types.items()
            if cols and tn in table_names
        }
        table_options = {t: o for t, o in self._connector.table_options.items() if t in table_names}
        return {
            "table_options": table_options,
            "table_types": table_types,
            "table_default_column_type": table_default_column_type,
            "table_row_types": table_row_types,
            "source_type": self._connector.source_type,
        }

    @Slot()
    def close_connection(self):
        """Close connector connection."""
        if self._connector is not None:
            self._connector.close_connection()

    @Slot()
    def _new_column_types(self):
        new_types = self._source_data_model.get_types(orientation=Qt.Orientation.Horizontal)
        self._connector.set_table_types({self._connector.current_table: new_types})

    @Slot()
    def _new_row_types(self):
        new_types = self._source_data_model.get_types(orientation=Qt.Orientation.Vertical)
        self._connector.set_table_row_types({self._connector.current_table: new_types})

    @Slot()
    def _update_display_row_types(self):
        """Updates displayed row types."""
        list_index = self._ui.mapping_list.selectionModel().currentIndex()
        if not list_index.isValid():
            return
        flattened_mapping = list_index.data(Role.FLATTENED_MAPPINGS)
        last_pivot_row = flattened_mapping.root_mapping.last_pivot_row()
        if last_pivot_row == -1:
            pivoted_rows = []
        else:
            pivoted_rows = list(range(last_pivot_row + 1))
        self._ui.source_data_table.verticalHeader().sections_with_buttons = pivoted_rows

    @Slot(QPoint)
    def show_source_list_context_menu(self, pos):
        """
        Shows context menu for source tables.

        Args:
            pos (QPoint): Mouse position
        """
        global_pos = self._ui.source_list.mapToGlobal(pos)
        index = self._ui.source_list.indexAt(pos)
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        source_list_menu = SourceListMenu(
            self._ui.source_list,
            global_pos,
            mime_data.hasFormat(TABLE_OPTIONS_MIME_TYPE),
            mime_data.hasFormat(MAPPING_LIST_MIME_TYPE),
        )
        option = source_list_menu.get_action()
        source_list_menu.deleteLater()
        if option == "Copy mappings":
            self._copy_mapping_list_to_clipboard(index)
            return
        if option == "Copy options":
            self._copy_table_options_to_clipboard(index)
            return
        if option == "Copy options and mappings":
            self._copy_mappings_and_options_to_clipboard(index)
            return
        if option == "Paste mappings":
            self._paste_mapping_list_from_clipboard()
            return
        if option == "Paste options":
            self._paste_table_options_from_clipboard()
            return
        if option == "Paste options and mappings":
            self._undo_stack.beginMacro("paste options and mappings")
            self._paste_mapping_list_from_clipboard()
            self._paste_table_options_from_clipboard()
            self._undo_stack.endMacro()

    def _copy_mapping_list_to_clipboard(self, table_index):
        """
        Copies the mappings of given source table to system clipboard.

        Args:
            table_index (QModelIndex): table index
        """
        mime_data = QMimeData()
        mime_data.setData(MAPPING_LIST_MIME_TYPE, self._pickle_mapping_list(table_index))
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data)

    def _pickle_mapping_list(self, table_index):
        """Pickles mapping list of given table.

        Args:
            table_index (QModelIndex): table index

        Returns:
            bytes: pickled list
        """
        mapping_dicts = list()
        for list_row in range(self._mappings_model.rowCount(table_index)):
            list_index = self._mappings_model.index(list_row, 0, table_index)
            name = list_index.data()
            flattened_mappings = list_index.data(Role.FLATTENED_MAPPINGS)
            mapping_dicts.append(unparse_named_mapping_spec(name, flattened_mappings.root_mapping))
        return pickle.dumps(mapping_dicts)

    def _paste_mapping_list_from_clipboard(self):
        """Pastes mapping list from system clipboard to selected source tables."""
        selection_model = self._ui.source_list.selectionModel()
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        mapping_dicts = pickle.loads(mime_data.data(MAPPING_LIST_MIME_TYPE))
        self._undo_stack.beginMacro("paste mappings")
        for table_index in selection_model.selectedIndexes():
            table_row = table_index.row()
            if table_row == 0:
                continue
            for list_row in reversed(range(self._mappings_model.rowCount(table_index))):
                self._undo_stack.push(DeleteMapping(table_row, self._mappings_model, list_row))
            target_row = self._mappings_model.rowCount(table_index)
            self._undo_stack.push(PasteMappings(table_row, target_row, self._mappings_model, mapping_dicts))
        self._undo_stack.endMacro()

    def _copy_table_options_to_clipboard(self, table_index):
        """
        Serializes mapping options to a dict.

        Args:
            table_index (QModelIndex): table index
        """
        mime_data = QMimeData()
        mime_data.setData(TABLE_OPTIONS_MIME_TYPE, self._pickle_table_options(table_index))
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data)

    def _pickle_table_options(self, table_index):
        """Pickles options from given table.

        Args:
            table_index (QModelIndex): table index

        Returns:
            bytes: pickles options
        """
        options = self._connector.table_options
        col_types = self._connector.table_types
        row_types = self._connector.table_row_types
        table_name = table_index.data()
        options_dict = dict()
        options_dict["options"] = options.get(table_name, {})
        options_dict["col_types"] = col_types.get(table_name, {})
        options_dict["row_types"] = row_types.get(table_name, {})
        return pickle.dumps(options_dict)

    def _paste_table_options_from_clipboard(self):
        selection_model = self._ui.source_list.selectionModel()
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        pickled_options = mime_data.data(TABLE_OPTIONS_MIME_TYPE)
        self._undo_stack.beginMacro("paste table options")
        for table_index in selection_model.selectedIndexes():
            table_row = table_index.row()
            if table_row == 0:
                continue
            pickled_previous_options = self._pickle_table_options(table_index)
            table_name = table_index.data()
            self._undo_stack.push(PasteOptions(self, table_name, pickled_options, pickled_previous_options))
        self._undo_stack.endMacro()

    def paste_options(self, table, options):
        """
        Pastes all mapping options to given table.

        Args:
            table (str): source table name
            options (dict): options
        """
        self._connector.set_table_options({table: options.get("options", {})})
        self._connector.set_table_types({table: options.get("col_types", {})})
        self._connector.set_table_row_types({table: options.get("row_types", {})})

    def _copy_mappings_and_options_to_clipboard(self, table_index):
        """Copies table's mapping list and options to system clipboard.

        Args:
            table_index (QModelIndex): table index
        """
        mime_data = QMimeData()
        mime_data.setData(MAPPING_LIST_MIME_TYPE, self._pickle_mapping_list(table_index))
        mime_data.setData(TABLE_OPTIONS_MIME_TYPE, self._pickle_table_options(table_index))
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(mime_data)


def _sanitize_data(data, header):
    """Fills empty data cells with None."""
    expected_columns = len(header) if header else max((len(x) for x in data))
    sanitized_data = list()
    for row in data:
        length_diff = expected_columns - len(row)
        if length_diff > 0:
            row = row + length_diff * [None]
        elif length_diff < 0:
            raise RuntimeError("Data row has more items than the header row.")
        sanitized_data.append(row)
    return sanitized_data
