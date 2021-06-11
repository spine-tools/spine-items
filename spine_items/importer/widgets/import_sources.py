######################################################################################################################
# Copyright (C) 2017-2021 Spine project consortium
# This file is part of Spine Toolbox.
# Spine Toolbox is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General
# Public License for more details. You should have received a copy of the GNU Lesser General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
######################################################################################################################

"""
Contains ImportSources widget and SourceDataTableMenu.

:author: P. Vennström (VTT)
:date:   1.6.2019
"""

from copy import deepcopy
from PySide2.QtCore import QItemSelectionModel, QModelIndex, QObject, QPoint, Qt, Signal, Slot, QPersistentModelIndex
from spinedb_api.import_mapping.import_mapping_compat import import_mapping_from_dict
from spinedb_api.import_mapping.type_conversion import value_to_convert_spec
from .custom_menus import SourceListMenu, SourceDataTableMenu
from .options_widget import OptionsWidget
from ..commands import PasteMappings, PasteOptions, RestoreMappingsFromDict
from ..mvcmodels.mapping_list_model import MappingListModel
from ..mvcmodels.mapping_specification_model import MappingSpecificationModel
from ..mvcmodels.source_data_table_model import SourceDataTableModel
from ..mvcmodels.source_table_list_model import SourceTableItem, SourceTableListModel


class ImportSources(QObject):
    """
    Loads and controls the 'Sources' and 'Source data' part of the window.
    Loads the 'Mappings' part of the window as the user changes the source table.
    """

    table_checked = Signal()
    mapped_data_ready = Signal(dict, list)
    source_table_selected = Signal(str, object)
    preview_data_updated = Signal(int)

    def __init__(self, parent, mapping):
        """
        Args:
            parent (ImportEditorWindow): importer window's UI
            mapping (dict): specification mapping
        """
        super().__init__()
        self._parent = parent
        self._ui = parent._ui
        self._ui_error = parent._ui_error

        # state
        self._connector = parent._connection_manager
        self._table_mappings = {}
        self._table_updating = False
        self._data_updating = False
        self._copied_mappings = parent._copied_mappings
        self._copied_options = {}
        self._undo_stack = parent._undo_stack
        self._source_data_model = SourceDataTableModel()
        self._source_table_model = SourceTableListModel(self._undo_stack)
        self._restore_mapping(mapping)
        self._ui.source_list.setModel(self._source_table_model)
        self._source_table_model.modelReset.connect(self._ui.source_list.expandAll)
        self._source_table_model.msg_error.connect(self._parent._show_error)
        self._source_table_model.table_created.connect(self._select_table_row)
        # create ui
        self._ui.source_data_table.setModel(self._source_data_model)
        self._ui_source_data_table_menu = SourceDataTableMenu(self._ui.source_data_table)
        self._ui_options_widget = OptionsWidget(self._connector, self._undo_stack)
        self._ui.dockWidget_source_options.setWidget(self._ui_options_widget)
        self._ui.source_data_table.verticalHeader().display_all = False

        # connect signals
        self._ui_options_widget.about_to_undo.connect(self.select_table)
        self._ui_options_widget.options_changed.connect(lambda _: self._clear_source_data_model())
        self._ui_options_widget.load_default_mapping_requested.connect(self._load_default_mapping)
        self._ui.source_list.customContextMenuRequested.connect(self.show_source_list_context_menu)
        self._ui.source_list.selectionModel().currentChanged.connect(self._change_selected_table)
        self._ui.source_data_table.customContextMenuRequested.connect(self._ui_source_data_table_menu.request_menu)

        # signals for connector
        self._connector.connection_ready.connect(self.request_new_tables_from_connector)
        self._connector.data_ready.connect(self._update_source_data)
        self._connector.tables_ready.connect(self.update_tables)
        self._connector.mapped_data_ready.connect(self.mapped_data_ready.emit)
        self._connector.default_mapping_ready.connect(self._set_default_mapping)

        # source data table
        self._source_data_model.more_data_needed.connect(self.fetch_more_data)
        self._source_data_model.mapping_data_changed.connect(self._update_display_row_types)
        self._source_data_model.column_types_updated.connect(self._new_column_types)
        self._source_data_model.row_types_updated.connect(self._new_row_types)

    @property
    def checked_tables(self):
        return self._source_table_model.checked_table_names()

    @Slot(object)
    def set_model(self, model):
        self._ui_source_data_table_menu.set_model(model)

    @Slot(object)
    def set_mapping(self, model):
        self._source_data_model.set_mapping(model)

    @Slot()
    def _load_default_mapping(self):
        self._connector.request_default_mapping()

    @Slot(dict)
    def _set_default_mapping(self, mapping):
        self._undo_stack.push(RestoreMappingsFromDict(self, mapping))

    @Slot()
    def request_new_tables_from_connector(self):
        """
        Requests new tables data from connector
        """
        self._connector.request_tables()

    @Slot(QModelIndex, QModelIndex)
    def _change_selected_table(self, selected, deselected):
        """
        Sets selected table and requests data from connector
        """
        item = self._source_table_model.table_at(selected)
        if not item.real:
            self.source_table_selected.emit("", None)
            return
        if item.name not in self._table_mappings:
            specification = MappingSpecificationModel(
                item.name, "", import_mapping_from_dict({"map_type": "ObjectClass"}), self._undo_stack
            )
            self._table_mappings[item.name] = MappingListModel([specification], item.name, self._undo_stack)
        self.source_table_selected.emit(item.name, self._table_mappings[item.name])
        self._connector.set_table(item.name)
        self._clear_source_data_model()

    @Slot(int, int)
    def fetch_more_data(self, max_rows, start):
        self._connector.request_data(max_rows=max_rows, start=start)

    def _select_table_row(self, row):
        selection_model = self._ui.source_list.selectionModel()
        index = self._source_table_model.index(row, 0)
        selection_model.clearSelection()
        selection_model.setCurrentIndex(index, QItemSelectionModel.Select)

    @Slot(str)
    def select_table(self, table):
        """
        Selects given table in the source table list.

        Args:
            table (str): source table name
        """
        index = self._source_table_model.table_index(table)
        selection_model = self._ui.source_list.selectionModel()
        if selection_model.hasSelection() and index == selection_model.selection().indexes()[0]:
            return
        selection_model.setCurrentIndex(index, QItemSelectionModel.ClearAndSelect)

    def request_mapped_data(self):
        tables_mappings = {t: self._table_mappings[t].get_mappings() for t in self.checked_tables}
        self._connector.request_mapped_data(tables_mappings, max_rows=-1)

    @Slot(dict)
    def update_tables(self, tables):
        """
        Updates list of tables
        """
        is_file_less = self._parent.is_file_less()
        if is_file_less:
            tables = self._table_mappings
        new_tables = list()
        for t_name, t_mapping in tables.items():
            if t_name not in self._table_mappings:
                if t_mapping is None:
                    t_mapping = import_mapping_from_dict({"map_type": "ObjectClass"})
                specification = MappingSpecificationModel(t_name, "", t_mapping, self._undo_stack)
                self._table_mappings[t_name] = MappingListModel([specification], t_name, self._undo_stack)
                new_tables.append(t_name)
        for k in list(self._table_mappings.keys()):
            if k not in tables:
                self._table_mappings.pop(k)
        if not tables:
            self._ui.source_list.clearSelection()

        # empty tables list and add new tables
        tables_to_select = set(self.checked_tables + new_tables)
        table_items = [SourceTableItem(name, name in tables_to_select, editable=is_file_less) for name in tables]
        self._source_table_model.reset(table_items)
        if is_file_less:
            self._source_table_model.add_empty_row()

        # current selected table
        current_index = self._ui.source_list.selectionModel().currentIndex()
        # reselect table if existing otherwise select first table
        if current_index.isValid():
            self._select_table_row(current_index.row())
        elif tables:
            self._select_table_row(0)
        self.table_checked.emit()

    @Slot(list, list)
    def _update_source_data(self, data, header):
        if not data:
            return
        try:
            data = _sanitize_data(data, header)
        except RuntimeError as error:
            self._ui_error.showMessage(str(error))
            return
        if not header:
            header = list(range(1, len(data[0]) + 1))
        # Set header data before reseting model because the header needs to be there for some slots...
        self._source_data_model.set_horizontal_header_labels(header)
        self._source_data_model.append_rows(data)
        types = self._connector.table_types.get(self._connector.current_table, {})
        row_types = self._connector.table_row_types.get(self._connector.current_table, {})
        for col in range(len(header)):
            col_type = types.get(col, "string")
            self._source_data_model.set_type(col, value_to_convert_spec(col_type), orientation=Qt.Horizontal)
        for row, row_type in row_types.items():
            self._source_data_model.set_type(row, value_to_convert_spec(row_type), orientation=Qt.Vertical)
        self.preview_data_updated.emit(self._source_data_model.columnCount())

    def _clear_source_data_model(self):
        self._source_data_model.set_horizontal_header_labels([])
        self._source_data_model.clear(infinite=self._parent.is_file_less())
        self.preview_data_updated.emit(0)

    def _restore_mapping(self, mapping):
        try:
            self._table_mappings = {
                table: MappingListModel(
                    [MappingSpecificationModel.from_dict(m, table, self._undo_stack) for m in mapping_specifications],
                    table,
                    self._undo_stack,
                )
                for table, mapping_specifications in mapping.get("table_mappings", {}).items()
            }
        except ValueError as error:
            self._ui_error.showMessage(f"{error}")
            return
        table_types = {
            tn: {int(col): value_to_convert_spec(spec) for col, spec in cols.items()}
            for tn, cols in mapping.get("table_types", {}).items()
        }
        table_row_types = {
            tn: {int(row): value_to_convert_spec(spec) for row, spec in rows.items()}
            for tn, rows in mapping.get("table_row_types", {}).items()
        }
        self._connector.set_table_options(mapping.get("table_options", {}))
        self._connector.set_table_types(table_types)
        self._connector.set_table_row_types(table_row_types)
        selected_tables = mapping.get("selected_tables")
        if selected_tables is None:
            selected_tables = set(self._table_mappings.keys())
        table_items = [SourceTableItem(name, name in selected_tables) for name in self._table_mappings]
        self._source_table_model.reset(table_items)

    def import_mappings(self, mapping):
        """
        Restores mappings from a dict.

        Args:
            mapping (dict): mapping
        """
        current = QPersistentModelIndex(self._ui.source_list.selectionModel().currentIndex())
        self._restore_mapping(mapping)
        self._ui.source_list.selectionModel().setCurrentIndex(current, QItemSelectionModel.ClearAndSelect)

    def get_mapping_dict(self):
        """Returns a dictionary with type of connector, connector options for tables,
        mappings for tables, selected tables.

        Returns:
            dict: dict with settings
        """
        tables = self._source_table_model.table_names()
        selected_tables = self._source_table_model.checked_table_names()

        table_mappings = {
            t: [m.to_dict() for m in mappings.mapping_specifications]
            for t, mappings in self._table_mappings.items()
            if t in tables
        }

        table_types = {
            tn: {col: spec.to_json_value() for col, spec in cols.items()}
            for tn, cols in self._connector.table_types.items()
            if cols
            if tn in tables
        }
        table_row_types = {
            tn: {col: spec.to_json_value() for col, spec in cols.items()}
            for tn, cols in self._connector.table_row_types.items()
            if cols and tn in tables
        }

        table_options = {t: o for t, o in self._connector.table_options.items() if t in tables}

        settings = {
            "table_mappings": table_mappings,
            "table_options": table_options,
            "table_types": table_types,
            "table_row_types": table_row_types,
            "selected_tables": selected_tables,
            "source_type": self._connector.source_type,
        }
        return settings

    @Slot()
    def close_connection(self):
        """Close connector connection."""
        self._connector.close_connection()

    @Slot()
    def _new_column_types(self):
        new_types = self._source_data_model.get_types(orientation=Qt.Horizontal)
        self._connector.set_table_types({self._connector.current_table: new_types})

    @Slot()
    def _new_row_types(self):
        new_types = self._source_data_model.get_types(orientation=Qt.Vertical)
        self._connector.set_table_row_types({self._connector.current_table: new_types})

    @Slot()
    def _update_display_row_types(self):
        mapping_specification = self._source_data_model.mapping_specification()
        if mapping_specification is None:
            return
        last_pivot_row = mapping_specification.last_pivot_row()
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
        source = index.data()
        source_list_menu = SourceListMenu(
            self._ui.source_list, global_pos, bool(self._copied_options), bool(self._copied_mappings)
        )
        option = source_list_menu.get_action()
        source_list_menu.deleteLater()
        if option == "Copy mappings":
            self._copied_mappings = self._copy_mappings(source)
            return
        if option == "Copy options":
            self._copied_options = self._options_to_dict(source)
            return
        if option == "Copy options and mappings":
            self._copied_options = self._options_to_dict(source)
            self._copied_mappings = self._copy_mappings(source)
            return
        if option == "Paste mappings":
            previous = self._copy_mappings(source)
            self._undo_stack.push(PasteMappings(self._parent, source, self._copied_mappings, previous))
            return
        if option == "Paste options":
            previous = self._options_to_dict(source)
            self._undo_stack.push(PasteOptions(self, source, self._copied_options, previous))
            return
        if option == "Paste options and mappings":
            previous_mappings = [deepcopy(m) for m in self._table_mappings[source].get_mappings()]
            previous_options = self._options_to_dict(source)
            self._undo_stack.beginMacro("paste options and mappings")
            self._undo_stack.push(PasteMappings(self._parent, source, self._copied_mappings, previous_mappings))
            self._undo_stack.push(PasteOptions(self, source, self._copied_options, previous_options))
            self._undo_stack.endMacro()

    def _copy_mappings(self, table):
        """
        Copies the mappings of the given source table.

        Args:
            table (str): source table name

        Returns:
            dict: copied mappings
        """
        mapping_list = self._table_mappings.get(table)
        if mapping_list is None:
            return {}
        return {
            specification.mapping_name: deepcopy(specification.mapping)
            for specification in mapping_list.mapping_specifications
        }

    def _options_to_dict(self, table):
        """
        Serializes mapping options to a dict.

        Args:
            table (str): source table name

        Returns:
            dict: serialized options
        """
        options = self._connector.table_options
        col_types = self._connector.table_types
        row_types = self._connector.table_row_types
        all_options = dict()
        all_options["options"] = deepcopy(options.get(table, {}))
        all_options["col_types"] = deepcopy(col_types.get(table, {}))
        all_options["row_types"] = deepcopy(row_types.get(table, {}))
        return all_options

    def paste_options(self, table, options):
        """
        Pastes all mapping options to given table.

        Args:
            table (str): source table name
            options (dict): options
        """
        self._connector.set_table_options({table: deepcopy(options.get("options", {}))})
        self._connector.set_table_types({table: deepcopy(options.get("col_types", {}))})
        self._connector.set_table_row_types({table: deepcopy(options.get("row_types", {}))})
        self.select_table(table)


def _sanitize_data(data, header):
    """Fills empty data cells with None."""
    expected_columns = len(header) if header else max((len(x) for x in data))
    sanitized_data = list()
    for row in data:
        length_diff = expected_columns - len(row)
        if length_diff > 0:
            row = row + length_diff * [None]
        elif length_diff < 0:
            raise RuntimeError("A row contains too many columns of data.")
        sanitized_data.append(row)
    return sanitized_data
