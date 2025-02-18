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

"""Contains unit tests for the ``import_sources`` module."""
import unittest
from unittest import mock
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QUndoStack
from PySide6.QtWidgets import QApplication, QListView, QListWidget, QWidget
from spine_items.importer.connection_manager import ConnectionManager
from spine_items.importer.mvcmodels.mappings_model import MappingsModel
from spine_items.importer.mvcmodels.mappings_model_roles import Role
from spine_items.importer.widgets.import_sources import ImportSources
from spine_items.importer.widgets.table_view_with_button_header import TableViewWithButtonHeader
from spinedb_api.spine_io.importers.reader import Reader, TableProperties
from spinetoolbox.helpers import signal_waiter
from tests.importer.helpers import append_source_table_with_mappings


class TestImportSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            QApplication()

    def setUp(self):
        self._parent_widget = _MockSpecificationEditor()
        self._undo_stack = QUndoStack(self._parent_widget)
        self._mappings_model = MappingsModel(self._undo_stack, self._parent_widget)

    def tearDown(self):
        self._parent_widget.deleteLater()

    def test_connector_fetches_empty_data(self):
        ui = mock.MagicMock()
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        source_list_selection_model = mock.MagicMock()
        ui.source_list.selectionModel.return_value = source_list_selection_model
        source_list_index = mock.MagicMock()
        source_list_index.row.return_value = 0
        source_list_selection_model.currentIndex.return_value = source_list_index
        ui.source_list.selectionModel.return_value = source_list_selection_model
        ui.mapping_list = QListWidget(self._parent_widget)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        data = []
        connection_settings = {"data": {"test data table": data}}
        connector = ConnectionManager(_FixedTableReader, connection_settings, self._parent_widget)
        mapping = {"table_options": {"test data table": {"has_header": False}}}
        import_sources.set_connector(connector, mapping)
        self._mappings_model.append_new_table_with_mapping("test data table", None)
        table_index = self._mappings_model.index(1, 0)
        import_sources._change_selected_table(table_index, QModelIndex())
        source_table_model = import_sources._source_data_model
        with signal_waiter(connector.connection_ready) as waiter:
            connector.init_connection("no file test source")
            waiter.wait()
        with signal_waiter(connector.data_ready) as waiter:
            source_table_model.fetchMore(QModelIndex())
            waiter.wait()
        header = []
        for column in range(source_table_model.columnCount()):
            header.append(source_table_model.headerData(column))
        self.assertEqual(header, [])
        data_rows = []
        for row in range(source_table_model.rowCount()):
            row_data = []
            for column in range(source_table_model.columnCount()):
                row_data.append(source_table_model.index(row, column).data())
            data_rows.append(row_data)
        self.assertEqual(data_rows, [])
        connector.close_connection()

    def test_connector_fetches_data_only(self):
        ui = mock.MagicMock()
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        source_list_selection_model = mock.MagicMock()
        ui.source_list.selectionModel.return_value = source_list_selection_model
        source_list_index = mock.MagicMock()
        source_list_index.row.return_value = 0
        source_list_selection_model.currentIndex.return_value = source_list_index
        ui.source_list.selectionModel.return_value = source_list_selection_model
        ui.mapping_list = QListWidget(self._parent_widget)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        data = [["data 1", "data 2"]]
        connection_settings = {"data": {"test data table": data}}
        connector = ConnectionManager(_FixedTableReader, connection_settings, self._parent_widget)
        mapping = {"table_options": {"test data table": {"has_header": False}}}
        import_sources.set_connector(connector, mapping)
        self._mappings_model.append_new_table_with_mapping("test data table", None)
        table_index = self._mappings_model.index(1, 0)
        import_sources._change_selected_table(table_index, QModelIndex())
        source_table_model = import_sources._source_data_model
        with signal_waiter(connector.connection_ready) as waiter:
            connector.init_connection("no file test source")
            waiter.wait()
        with signal_waiter(connector.data_ready) as waiter:
            source_table_model.fetchMore(QModelIndex())
            waiter.wait()
        header = []
        for column in range(source_table_model.columnCount()):
            header.append(source_table_model.headerData(column))
        self.assertEqual(header, [1, 2])
        data_rows = []
        for row in range(source_table_model.rowCount()):
            row_data = []
            for column in range(source_table_model.columnCount()):
                row_data.append(source_table_model.index(row, column).data())
            data_rows.append(row_data)
        self.assertEqual(data_rows, [["data 1", "data 2"]])
        connector.close_connection()

    def test_connector_fetches_header_only(self):
        ui = mock.MagicMock()
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        source_list_selection_model = mock.MagicMock()
        ui.source_list.selectionModel.return_value = source_list_selection_model
        source_list_index = mock.MagicMock()
        source_list_index.row.return_value = 0
        source_list_selection_model.currentIndex.return_value = source_list_index
        ui.source_list.selectionModel.return_value = source_list_selection_model
        ui.mapping_list = QListWidget(self._parent_widget)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        data = [["header 1", "header 2"]]
        connection_settings = {"data": {"test data table": data}}
        connector = ConnectionManager(_FixedTableReader, connection_settings, self._parent_widget)
        mapping = {"table_options": {"test data table": {"has_header": True}}}
        import_sources.set_connector(connector, mapping)
        self._mappings_model.append_new_table_with_mapping("test data table", None)
        table_index = self._mappings_model.index(1, 0)
        import_sources._change_selected_table(table_index, QModelIndex())
        source_table_model = import_sources._source_data_model
        with signal_waiter(connector.connection_ready) as waiter:
            connector.init_connection("no file test source")
            waiter.wait()
        with signal_waiter(connector.data_ready) as waiter:
            source_table_model.fetchMore(QModelIndex())
            waiter.wait()
        header = []
        for column in range(source_table_model.columnCount()):
            header.append(source_table_model.headerData(column))
        self.assertEqual(header, ["header 1", "header 2"])
        data_rows = []
        for row in range(source_table_model.rowCount()):
            row_data = []
            for column in range(source_table_model.columnCount()):
                row_data.append(source_table_model.index(row, column).data())
            data_rows.append(row_data)
        self.assertEqual(data_rows, [])
        connector.close_connection()

    def test_connector_fetches_data_and_header(self):
        ui = mock.MagicMock()
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        source_list_selection_model = mock.MagicMock()
        ui.source_list.selectionModel.return_value = source_list_selection_model
        source_list_index = mock.MagicMock()
        source_list_index.row.return_value = 0
        source_list_selection_model.currentIndex.return_value = source_list_index
        ui.source_list.selectionModel.return_value = source_list_selection_model
        ui.mapping_list = QListView(self._parent_widget)
        ui.mapping_list.setModel(self._mappings_model)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        data = [["header 1", "header 2"], ["data 1", "data 2"]]
        connection_settings = {"data": {"test data table": data}}
        connector = ConnectionManager(_FixedTableReader, connection_settings, self._parent_widget)
        mapping = {"table_options": {"test data table": {"has_header": True}}}
        import_sources.set_connector(connector, mapping)
        self._mappings_model.append_new_table_with_mapping("test data table", None)
        table_index = self._mappings_model.index(1, 0)
        import_sources._change_selected_table(table_index, QModelIndex())
        source_table_model = import_sources._source_data_model
        with signal_waiter(connector.connection_ready) as waiter:
            connector.init_connection("no file test source")
            waiter.wait()
        with signal_waiter(connector.data_ready) as waiter:
            source_table_model.fetchMore(QModelIndex())
            waiter.wait()
        header = []
        for column in range(source_table_model.columnCount()):
            header.append(source_table_model.headerData(column))
        self.assertEqual(header, ["header 1", "header 2"])
        data_rows = []
        for row in range(source_table_model.rowCount()):
            row_data = []
            for column in range(source_table_model.columnCount()):
                row_data.append(source_table_model.index(row, column).data())
            data_rows.append(row_data)
        self.assertEqual(data_rows, [["data 1", "data 2"]])
        connector.close_connection()

    def test_copying_and_pasting_mappings_and_options_from_one_table_to_another(self):
        ui = mock.MagicMock()
        ui.source_list = QListView(self._parent_widget)
        ui.source_list.setModel(self._mappings_model)
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        ui.mapping_list = QListView(self._parent_widget)
        ui.mapping_list.setModel(self._mappings_model)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        data = [["header 1", "header 2"], ["data 1", "data 2"]]
        connection_settings = {
            "data": {"source table": data, "destination table": data},
            "options": {"source table": {"has_header": True}, "destination table": {"has_header": False}},
        }
        connector = ConnectionManager(_FixedTableReader, connection_settings, self._parent_widget)
        mapping = {}
        import_sources.set_connector(connector, mapping)
        with signal_waiter(connector.connection_ready) as waiter:
            connector.init_connection("no file test source")
            waiter.wait()
        self.assertTrue(connector.is_connected)
        connector.request_tables()
        while self._mappings_model.rowCount() != 3:
            QApplication.processEvents()
        source_table_rows = {}
        for row in range(1, self._mappings_model.rowCount()):
            source_table_rows[self._mappings_model.index(row, 0).data(Role.ITEM).name] = row
        self.assertIn("source table", source_table_rows)
        source_table_index = self._mappings_model.index(source_table_rows["source table"], 0)
        ui.source_list.setCurrentIndex(source_table_index)
        with mock.patch("spine_items.importer.widgets.import_sources.QApplication") as mock_application:
            clipboard = _MockClipboard()
            mock_application.clipboard.return_value = clipboard
            import_sources._copy_mappings_and_options_to_clipboard(source_table_index)
            self.assertIn("destination table", source_table_rows)
            destination_table_index = self._mappings_model.index(source_table_rows["destination table"], 0)
            ui.source_list.setCurrentIndex(destination_table_index)
            self.assertEqual(
                connector.table_options,
                {"source table": {"has_header": True}, "destination table": {"has_header": False}},
            )
            import_sources._paste_mapping_list_from_clipboard()
            self.assertEqual(self._mappings_model.rowCount(source_table_index), 1)
            self.assertEqual(self._mappings_model.rowCount(destination_table_index), 1)
            self.assertEqual(self._mappings_model.index(0, 0, destination_table_index).data(), "Mapping 1")
            self.assertEqual(
                connector.table_options,
                {"source table": {"has_header": True}, "destination table": {"has_header": False}},
            )
            import_sources._paste_table_options_from_clipboard()
        self.assertEqual(
            connector.table_options, {"source table": {"has_header": True}, "destination table": {"has_header": True}}
        )
        connector.close_connection()

    def test_copying_and_pasting_mappings_from_one_table_to_another(self):
        ui = mock.MagicMock()
        ui.source_list = QListView(self._parent_widget)
        ui.source_list.setModel(self._mappings_model)
        ui.source_data_table = TableViewWithButtonHeader(self._parent_widget)
        ui.mapping_list = QListView(self._parent_widget)
        ui.mapping_list.setModel(self._mappings_model)
        import_sources = ImportSources(self._mappings_model, ui, self._undo_stack, self._parent_widget)
        source_table_index = append_source_table_with_mappings(
            self, self._mappings_model, "source table", "one mapping", []
        )
        destination_table_index = append_source_table_with_mappings(
            self, self._mappings_model, "destination table", "another mapping", []
        )
        with mock.patch("spine_items.importer.widgets.import_sources.QApplication") as mock_application:
            clipboard = _MockClipboard()
            mock_application.clipboard.return_value = clipboard
            import_sources._copy_mapping_list_to_clipboard(source_table_index)
            ui.source_list.setCurrentIndex(destination_table_index)
            import_sources._paste_mapping_list_from_clipboard()
        self.assertEqual(self._mappings_model.rowCount(source_table_index), 1)
        self.assertEqual(self._mappings_model.rowCount(destination_table_index), 1)
        self.assertEqual(self._mappings_model.index(0, 0, destination_table_index).data(), "one mapping")


class _MockSpecificationEditor(QWidget):
    def is_file_less(self):
        return False


class _FixedTableReader(Reader):
    DISPLAY_NAME = "test data source"
    OPTIONS = {"has_header": {"type": bool, "label": "Has header", "default": False}}
    FILE_EXTENSIONS = {"*.*"}

    def __init__(self, settings):
        super().__init__(None)
        self._data = settings["data"]
        self._options = settings.get("options")

    def connect_to_source(self, source, **extras):
        pass

    def disconnect(self):
        pass

    def get_tables_and_properties(self):
        return {table: TableProperties(self._options.get(table, {})) for table in self._data}

    def get_data_iterator(self, table, options, max_rows=-1):
        if options["has_header"]:
            header = self._data[table][0]
            begin = 1
            end = (begin + max_rows) if max_rows > -1 else None
        else:
            header = []
            begin = 0
            end = max_rows if max_rows > -1 else None
        return self._data[table][slice(begin, end)], header


class _MockClipboard:
    mime_data = None

    def setMimeData(self, data):
        self.mime_data = data

    def mimeData(self):
        return self.mime_data


if __name__ == "__main__":
    unittest.main()
