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

"""Contains ConnectionManager class."""
from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from spinetoolbox.helpers import busy_effect


class ConnectionManager(QObject):
    """Class to manage data connections in another thread."""

    tables_requested = Signal()
    data_requested = Signal(str, dict, int, int)
    default_mapping_requested = Signal()

    connection_failed = Signal(str)
    """Signal with error message if connection fails  """

    connection_ready = Signal()
    """Signal that a connection to the datasource is ready  """

    connection_closed = Signal()
    """Signal that connection is being closed  """

    error = Signal(str)
    """error while reading data or connection to data source  """

    data_ready = Signal(list, list)
    """data from source is ready, should send list of data and headers  """

    tables_ready = Signal(dict)
    """tables from source is ready, should send a list of str of available tables  """

    default_mapping_ready = Signal(dict)
    """default mapping ready from data source  """

    current_table_changed = Signal()
    """Emitted when the current table has changed."""

    def __init__(self, connection, connection_settings, parent):
        """
        Args:
            connection (Type): A class derived from `SourceConnection`, e.g. `CSVConnector`
            connection_settings (dict): connection specific settings
            parent (QObject): parent object
        """
        super().__init__(parent)
        self._thread = None
        self._worker = None
        self._current_table = None
        self._table_options = {}
        self._table_types = {}
        self._default_table_column_type = {}
        self._table_row_types = {}
        self._connection = connection
        self._connection_settings = connection_settings
        self._is_connected = False

    @property
    def connection(self):
        return self._connection

    @property
    def current_table(self):
        return self._current_table

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def table_options(self):
        return self._table_options

    @property
    def table_types(self):
        return self._table_types

    @property
    def table_default_column_type(self):
        return self._default_table_column_type

    @property
    def table_row_types(self):
        return self._table_row_types

    @property
    def source_type(self):
        return self._connection.__name__

    def set_table(self, table):
        """Sets the current table of the data source.

        Args:
            table (str): table name
        """
        self._current_table = table
        self.current_table_changed.emit()

    def request_tables(self):
        """Gets tables tables from source, emits tables_requested."""
        if self.is_connected:
            self.tables_requested.emit()

    def request_data(self, table=None, max_rows=-1, start=0):
        """Requests data from a table. Starts a process that emits data_ready with the fetched data.

        Args:
            table (str): which table to get data from (default: {None})
            max_rows (int): how many rows to read (default: {-1})
        """
        if not self.is_connected:
            return
        if table is None:
            table = self._current_table
        options = self._table_options.get(self._current_table, {})
        self.data_requested.emit(table, options, max_rows, start)

    def request_default_mapping(self):
        """Request default mapping from worker."""
        if self.is_connected:
            self.default_mapping_requested.emit()

    def init_connection(self, source, **source_extras):
        """Creates a Worker and a new thread to read source data.
        If there is an existing thread close that one.

        Args:
            source (str): source file name or URL
            **source_extras: source specific additional connection settings
        """
        # close existing thread
        self.close_connection()
        # create new thread and worker
        self._thread = QThread()
        self._worker = ConnectionWorker(self._connection, self._connection_settings, source, source_extras)
        self._worker.moveToThread(self._thread)
        # connect worker signals
        self._worker.connectionReady.connect(self._handle_connection_ready)
        self._worker.tablesReady.connect(self._handle_tables_ready)
        self._worker.tablesReady[dict].connect(self._handle_tables_ready)
        self._worker.dataReady.connect(self.data_ready.emit)
        self._worker.defaultMappingReady.connect(self.default_mapping_ready.emit)
        self._worker.error.connect(self.error.emit)
        self._worker.connectionFailed.connect(self.connection_failed.emit)
        # connect start working signals
        self.tables_requested.connect(self._worker.tables)
        self.data_requested.connect(self._worker.data)
        self.default_mapping_requested.connect(self._worker.default_mapping)
        self.connection_closed.connect(self._worker.close_connection, type=Qt.ConnectionType.BlockingQueuedConnection)
        # when thread is started, connect worker to source
        self._thread.started.connect(self._worker.init_connection)
        self._thread.start()

    @Slot()
    def _handle_connection_ready(self):
        self._is_connected = True
        self.connection_ready.emit()

    @Slot(list)
    @Slot(dict)
    def _handle_tables_ready(self, table_options):
        if isinstance(table_options, list):
            table_options = {name: {} for name in table_options}

        # save table options if they don't already exist
        for key, table_settings in table_options.items():
            options = table_settings.get("options", {})
            if options is not None:
                self._table_options.setdefault(key, options)
            types = table_settings.get("types", {})
            if types is not None:
                self._table_types.setdefault(key, types)
            row_types = table_settings.get("row_types", {})
            if row_types is not None:
                self._table_row_types.setdefault(key, row_types)

        tables = {k: t.get("mapping", None) for k, t in table_options.items()}
        self.tables_ready.emit(tables)
        # update options if a sheet is selected
        if self._current_table in self._table_options:
            self.current_table_changed.emit()

    @Slot(dict)
    def update_options(self, options):
        if not self._current_table:
            return
        self._table_options.setdefault(self._current_table, {}).update(options)

    def get_current_options(self):
        if not self._current_table:
            return {}
        return self._table_options.get(self._current_table, {})

    def get_current_option_value(self, option_key):
        """Returns the value for option_key for the current table or the default value."""
        current_options = self._table_options.get(self._current_table, {})
        option_value = current_options.get(option_key)
        if option_value is None:
            option_specification = self._connection.OPTIONS.get(option_key)
            if option_specification is not None:
                return option_specification["default"]
            option_specification = self._connection.BASE_OPTIONS[option_key]
            return option_specification["default"]
        return option_value

    def set_table_options(self, options):
        """Sets connection manager options for current connector

        Args:
            options (dict): settings for the tables
        """
        self._table_options.update(options)
        if self._current_table in self._table_options:
            self.current_table_changed.emit()

    def set_table_types(self, types):
        """Sets connection manager types for current connector

        Args:
            types (dict): dict with types settings, column (int) as key, type as value
        """
        self._table_types.update(types)

    def update_table_default_column_type(self, column_type):
        """Updates default column type.

        Args:
            column_type (dict): mapping from table name to column type name
        """
        self._default_table_column_type.update(column_type)

    def clear_table_default_column_type(self, table_name):
        """Clears default column type.

        Args:
            table_name (str): table name
        """
        self._default_table_column_type.pop(table_name, None)

    def set_table_row_types(self, types):
        """Sets connection manager types for current connector

        Arguments:
            types {dict} -- Dict with types settings, row (int) as key, type as value
        """
        self._table_row_types.update(types)

    def close_connection(self):
        """Closes and deletes thread and worker"""
        self._is_connected = False
        self.connection_closed.emit()
        if self._worker:
            self.connection_closed.disconnect(self._worker.close_connection)
            self._worker.deleteLater()
            self._worker = None
        if self._thread:
            self._thread.quit()
            self._thread.wait()
            self._thread.deleteLater()


class ConnectionWorker(QObject):
    """A class for delegating SourceConnection operations to another QThread."""

    connectionFailed = Signal(str)
    """Signal with error message if connection fails"""
    error = Signal(str)
    """Signal with error message if something errors"""
    connectionReady = Signal()
    """Signal that connection is ready to be read"""
    tablesReady = Signal((list,), (dict,))
    """Signal when tables from source is ready, a list of table names or dict mapping table name to table options."""
    dataReady = Signal(list, list)
    """Signal when data from a specific table in source is ready, list of data and list of headers"""
    defaultMappingReady = Signal(dict)
    """Signal when default mapping is ready"""

    def __init__(self, connection, connection_settings, source, source_extras, parent=None):
        """
        Args:
            connection (class): A class derived from `SourceConnection` for connecting to the source file
            connection_settings (dict): settings passed to the connection constructor
            source (str): source file path or URL
            source_extras (dict): source specific additional connection settings
            parent (QObject, optional): parent object
        """
        super().__init__(parent)
        self._connection = connection(connection_settings)
        self._source = source
        self._source_extras = source_extras

    @Slot()
    def init_connection(self):
        """Connects to data source."""
        if self._source:
            try:
                self._connection.connect_to_source(self._source, **self._source_extras)
                self.connectionReady.emit()
            except Exception as error:
                self.connectionFailed.emit(f"Could not connect to source: {error}")
        else:
            self.connectionFailed.emit("Connection has no source")

    @Slot()
    def tables(self):
        try:
            tables = self._connection.get_tables()
            if isinstance(tables, list):
                self.tablesReady.emit(tables)
            else:
                self.tablesReady[dict].emit(tables)
        except Exception as error:
            self.error.emit(f"Could not get tables from source: {error}")

    @busy_effect
    @Slot(str, dict, int, int)
    def data(self, table, options, max_rows, start):
        if not table:
            # FIXME: The 'Select all' option in the Source tables list thinks it's a table too and requests data
            return
        try:
            data, header = self._connection.get_data(table, options, max_rows, start)
            self.dataReady.emit(data, header)
        except Exception as error:
            self.error.emit(f"Could not get data from source: {error}")

    @Slot()
    def close_connection(self):
        try:
            self._connection.disconnect()
        except Exception as error:
            self.error.emit(f"Could not disconnect from source: {error}")

    @Slot()
    def default_mapping(self):
        try:
            mapping = self._connection.create_default_mapping()
            self.defaultMappingReady.emit(mapping)
        except Exception as error:
            self.error.emit(f"Could not default mapping from source: {error}")
